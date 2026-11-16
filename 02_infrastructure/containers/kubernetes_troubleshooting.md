# Kubernetes 장애 진단
<!-- reference: _reference/kubernetes_official_notes.md -->

Kubernetes에서 Pod가 뜨지 않거나, 계속 재시작하거나, Service로 접속되지 않을 때 원인을 좁혀 가는 순서를 정리합니다.
오브젝트와 kubectl 기본 사용법은 [Kubernetes 기본](./kubernetes_basic.md), 설치 단계의 문제는 [Kubernetes 설치](./kubernetes_install.md)의 트러블슈팅 절을 참고합니다.

## 목차

| 섹션                                                                                                                     |
|--------------------------------------------------------------------------------------------------------------------------|
| [1. 진단 순서](#1-진단-순서) / [2. Pod 상태 읽기](#2-pod-상태-읽기) / [3. Pending](#3-pending)                           |
| [4. 이미지와 컨테이너 생성 오류](#4-이미지와-컨테이너-생성-오류) / [5. CrashLoopBackOff](#5-crashloopbackoff)            |
| [6. OOMKilled와 Eviction](#6-oomkilled와-eviction) / [7. Probe 실패](#7-probe-실패) / [8. Service 연결](#8-service-연결) |
| [9. kubectl debug](#9-kubectl-debug) / [10. 노드 문제](#10-노드-문제) / [11. 점검표](#11-점검표)                         |

---

## 1. 진단 순서

장애를 볼 때는 넓은 범위에서 좁은 범위로 내려갑니다. 먼저 사실을 모으고, 원인을 추정한 뒤 하나씩 바꿔 확인합니다.

```text
 1. scope      kubectl get pods -A -o wide | grep -v Running
                    |
 2. object     kubectl describe pod <pod>   (Events at the bottom)
                    |
 3. container  kubectl logs <pod> [-c <ctr>] [--previous]
                    |
 4. network    Service -> EndpointSlice -> Pod IP -> DNS
                    |
 5. node       kubectl describe node <node> / journalctl -u kubelet
```

```bash
# 정상이 아닌 Pod만 보기 (STATUS가 Running·Completed가 아닌 것)
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

# 네임스페이스 이벤트를 시간순으로
kubectl get events -n <ns> --sort-by=.lastTimestamp

# Warning 이벤트만
kubectl get events -A --field-selector type=Warning

# 최근 변경 확인 (롤아웃 이력)
kubectl rollout history deployment/<name> -n <ns>
```

🟡 이벤트는 기본적으로 1시간 정도만 보관되므로(kube-apiserver `--event-ttl` 기본값) 장애 직후 먼저 저장해 둡니다: `kubectl get events -n <ns> -o yaml > events.yaml`.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Pod 상태 읽기

`kubectl get pods`의 STATUS 열은 Pod의 `phase` 필드와 컨테이너 상태의 `reason`을 섞어 보여 줍니다. `CrashLoopBackOff`, `Terminating`은 phase가 아니라 표시용 값입니다.

| Pod phase   | 의미                                                                    |
|-------------|-------------------------------------------------------------------------|
| `Pending`   | 승인되었지만 컨테이너가 아직 준비되지 않음(스케줄 대기, 이미지 받는 중) |
| `Running`   | 노드에 배치되고 컨테이너가 만들어짐. 하나 이상 실행·시작·재시작 중      |
| `Succeeded` | 모든 컨테이너가 성공 종료했고 재시작하지 않음                           |
| `Failed`    | 모든 컨테이너가 종료했고 하나 이상 실패로 끝남                          |
| `Unknown`   | 노드와 통신 문제로 상태를 알 수 없음                                    |

| 컨테이너 상태 | 설명                                                                |
|---------------|---------------------------------------------------------------------|
| `Waiting`     | 이미지 받기·Secret 적용 등으로 아직 실행 전. `reason`에 이유가 나옴 |
| `Running`     | 실행 중. `postStart` 훅은 끝난 상태                                 |
| `Terminated`  | 종료. `reason`, `exitCode`, 시작·종료 시각이 기록됨                 |

STATUS 값별로 먼저 볼 곳은 다음과 같습니다.

| STATUS                            | 먼저 볼 곳                                   | 절 |
|-----------------------------------|----------------------------------------------|----|
| `Pending`                         | `describe pod`의 Events(FailedScheduling)    | 3  |
| `ErrImagePull`/`ImagePullBackOff` | Events의 pull 오류 메시지                    | 4  |
| `CreateContainerConfigError`      | 참조한 ConfigMap·Secret·키 존재 여부         | 4  |
| `CrashLoopBackOff`                | `logs --previous`, `lastState.terminated`    | 5  |
| `OOMKilled`                       | 메모리 limit, 사용량                         | 6  |
| `Evicted`                         | 노드 압박 상태(MemoryPressure, DiskPressure) | 6  |
| `Running`인데 READY `0/1`         | readiness probe 실패 이벤트                  | 7  |
| `Terminating`에서 멈춤            | finalizer, admission webhook                 | 10 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Pending

Pending은 대부분 스케줄러가 Pod를 놓을 노드를 찾지 못한 경우입니다. `kubectl describe pod`의 Events에 `FailedScheduling`과 이유가 나옵니다.

```bash
kubectl describe pod <pod> -n <ns> | sed -n '/Events:/,$p'
# 예: 0/3 nodes are available: 3 Insufficient memory.
```

| 메시지 예                                           | 원인                                | 조치                                                   |
|-----------------------------------------------------|-------------------------------------|--------------------------------------------------------|
| `Insufficient cpu` / `Insufficient memory`          | requests 합이 노드 할당 가능량 초과 | requests 조정, 노드 추가, 불필요 Pod 정리              |
| `node(s) had untolerated taint`                     | 노드 taint를 Pod가 허용하지 않음    | taint 의도 확인 후 toleration 추가 또는 다른 노드 사용 |
| `node(s) didn't match Pod's node affinity/selector` | nodeSelector·affinity 조건 불일치   | 노드 label과 Pod 조건 비교                             |
| `pod has unbound immediate PersistentVolumeClaims`  | PVC가 바인딩되지 않음               | `kubectl get pvc`, StorageClass·프로비저너 상태 확인   |
| `didn't have free ports`                            | `hostPort` 충돌                     | hostPort 대신 Service 사용                             |

```bash
# 노드별 할당 가능량과 이미 요청된 양
kubectl describe node <node> | sed -n '/Allocated resources:/,/Events:/p'

# 노드 taint와 label
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
kubectl get nodes --show-labels

# PVC 상태
kubectl get pvc -n <ns>
kubectl describe pvc <pvc> -n <ns>
```

스케줄은 실제 사용량이 아니라 `requests` 합으로 판단합니다. `kubectl top node`의 사용률이 낮아도 requests가 가득 차면 Pending이 됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 이미지와 컨테이너 생성 오류

### ErrImagePull / ImagePullBackOff

노드에 배치되었지만 이미지를 받지 못한 상태입니다. `ErrImagePull`이 반복되면 kubelet이 재시도 간격을 늘리며 `ImagePullBackOff`로 표시합니다.

| Events 메시지 예                | 원인                             | 확인                                         |
|---------------------------------|----------------------------------|----------------------------------------------|
| `not found`, `manifest unknown` | 이미지 이름·tag 오타, push 안 됨 | 레지스트리에서 tag 존재 확인                 |
| `unauthorized`, `denied`        | 비공개 레지스트리 인증 실패      | `imagePullSecrets`, Secret 네임스페이스·내용 |
| `i/o timeout`, `no such host`   | 노드에서 레지스트리 접근 불가    | 노드 DNS·프록시·방화벽                       |
| `toomanyrequests`               | 레지스트리 pull 횟수 제한        | 인증 pull, 미러 레지스트리                   |
| `no matching manifest`          | 노드 CPU 아키텍처용 이미지 없음  | 멀티 플랫폼 이미지 여부                      |

```bash
# Pod가 쓰는 이미지와 pull secret
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].image}{"\n"}{.spec.imagePullSecrets}{"\n"}'

# 해당 노드에서 직접 pull 시험 (containerd/CRI-O 노드)
sudo crictl pull <image>
```

### CreateContainerConfigError

이미지는 받았지만 컨테이너 설정을 만들지 못한 상태입니다. 대부분 `env`·`envFrom`·`volume`이 참조한 ConfigMap·Secret이나 그 안의 키가 없는 경우입니다.

```bash
kubectl describe pod <pod> -n <ns> | grep -A3 -i 'Warning'
kubectl get configmap,secret -n <ns>
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. CrashLoopBackOff

컨테이너가 시작 후 종료되고, kubelet이 재시작을 반복하면서 간격을 늘리는 상태입니다. 기본 재시작 지연은 10초에서 시작해 두 배씩(10s, 20s, 40s, ...) 늘어나 최대 300초(5분)에서 멈추고, 컨테이너가 10분 동안 문제없이 실행되면 초기화됩니다.

🟡 Kubernetes v1.35부터 베타(기본 활성)인 `KubeletCrashLoopBackOffMax` 기능으로 kubelet 설정 `crashLoopBackOff.maxContainerRestartPeriod`(1s~300s)를 지정하면 최대 지연이 달라질 수 있습니다. 노드별 kubelet 설정을 확인합니다(2026-11-16 확인).

```bash
# 직전에 죽은 컨테이너의 로그 (현재 로그는 비어 있는 경우가 많음)
kubectl logs <pod> -n <ns> -c <container> --previous

# 종료 코드와 이유
kubectl get pod <pod> -n <ns> \
  -o jsonpath='{range .status.containerStatuses[*]}{.name}{" "}{.lastState.terminated.reason}{" exit="}{.lastState.terminated.exitCode}{"\n"}{end}'
```

| 종료 코드 | 흔한 의미                                                     |
|-----------|---------------------------------------------------------------|
| `0`       | 정상 종료. 서버가 아니라 한 번 실행하고 끝나는 명령일 수 있음 |
| `1`, `2`  | 앱 오류·잘못된 인자. 로그 확인                                |
| `126`     | 실행 권한 없음                                                |
| `127`     | 명령·실행 파일을 찾지 못함(`command` 경로, 이미지 내용 확인)  |
| `137`     | SIGKILL(128+9). OOMKilled 또는 liveness 실패 후 강제 종료     |
| `143`     | SIGTERM(128+15). 정상 종료 요청을 받고 끝남                   |

종료 코드 128 이상은 셸 관례상 `128 + 신호 번호`입니다. 같은 137이라도 `reason`이 `OOMKilled`인지, Events에 `Liveness probe failed`가 있는지로 구분합니다.

### 종료 메시지 남기기

로그가 짧게 지나가 원인을 놓친다면 `terminationMessagePolicy: FallbackToLogsOnError`를 설정합니다. 종료 메시지 파일(기본 `/dev/termination-log`)이 비어 있고 오류로 끝났을 때 로그 마지막 부분(최대 2048바이트 또는 80줄 중 작은 쪽)을 `lastState.terminated.message`에 남깁니다.

```yaml
containers:
  - name: app
    image: registry.example.com/team/app:1.0
    terminationMessagePolicy: FallbackToLogsOnError
```

### 원인을 찾을 때까지 컨테이너 살려 두기

```bash
# Pod 복사본을 만들고 명령만 셸로 바꿔 내부를 확인 (원본은 그대로)
kubectl debug <pod> -n <ns> -it --copy-to=<pod>-debug --container=<container> -- sh
```

확인이 끝나면 복사본을 지웁니다: `kubectl delete pod <pod>-debug -n <ns>`.

[⬆ 목차로 돌아가기](#목차)

---

## 6. OOMKilled와 Eviction

둘 다 메모리 부족으로 Pod가 멈추지만 주체가 다릅니다.

| 구분 | OOMKilled                                      | Eviction                                                |
|------|------------------------------------------------|---------------------------------------------------------|
| 주체 | 리눅스 커널 OOM killer                         | kubelet                                                 |
| 계기 | 컨테이너가 memory limit 초과, 노드 메모리 고갈 | 노드 자원이 eviction 임계값 아래로 내려감               |
| 결과 | 컨테이너 재시작(`reason: OOMKilled`)           | Pod `Failed`, `reason: Evicted`. 컨트롤러가 새 Pod 생성 |
| 확인 | `lastState.terminated.reason`                  | `kubectl describe node`의 Conditions                    |

```bash
# OOMKilled 여부
kubectl get pod <pod> -n <ns> -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}'

# 현재 사용량 (metrics-server 필요)
kubectl top pod <pod> -n <ns> --containers

# 노드 압박 조건 (MemoryPressure, DiskPressure, PIDPressure)
kubectl describe node <node> | sed -n '/Conditions:/,/Addresses:/p'

# 남아 있는 Evicted Pod 목록
kubectl get pods -A --field-selector=status.phase=Failed
```

리눅스 노드의 기본 hard eviction 임계값은 `memory.available<100Mi`, `nodefs.available<10%`, `nodefs.inodesFree<5%`, `imagefs.available<15%`입니다. kubelet 설정(`evictionHard`)으로 바꿀 수 있으므로 실제 값은 노드 설정에서 확인합니다.

조치 기준:

- limit이 실제 최대 사용량보다 작으면 limit을 올리고, 사용량이 계속 늘면 메모리 누수를 의심합니다.
- JVM·Node.js처럼 힙 크기를 따로 정하는 런타임은 컨테이너 limit에 맞춰 힙 상한을 설정합니다.
- 중요한 Pod는 requests와 limits를 같게 두어 QoS를 `Guaranteed`로 만들면 노드 압박 때 나중에 축출됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Probe 실패

| Probe            | 실패 시 동작                                                            | 흔한 실수                                             |
|------------------|-------------------------------------------------------------------------|-------------------------------------------------------|
| `startupProbe`   | 성공 전까지 다른 probe 정지. 실패하면 컨테이너 종료 후 재시작 정책 적용 | 시작 시간보다 짧은 `failureThreshold × periodSeconds` |
| `livenessProbe`  | 허용 횟수를 넘기면 kubelet이 컨테이너 재시작                            | DB 같은 외부 의존성까지 검사해 연쇄 재시작            |
| `readinessProbe` | Pod IP를 Service의 EndpointSlice에서 빼서 트래픽 차단                   | 경로·포트 오타로 READY `0/1` 유지                     |

```bash
# probe 실패 이벤트
kubectl get events -n <ns> --field-selector involvedObject.name=<pod> | grep -i probe

# Pod 안에서 probe와 같은 요청을 직접 시험
kubectl exec -n <ns> <pod> -- wget -qO- http://127.0.0.1:8080/healthz
```

🟡 liveness probe가 외부 DB 상태를 검사하면 DB 장애 때 모든 Pod가 함께 재시작되어 장애가 커집니다. liveness는 프로세스 자체가 멈췄는지만 보고, 의존성 확인은 readiness에 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Service 연결

Service로 접속되지 않으면 바깥에서 안쪽 순서로 확인합니다.

```text
 client -> DNS name -> Service (ClusterIP:port)
                          |
                          v
                   EndpointSlice (Pod IP:targetPort)
                          |
                          v
                   Pod (containerPort, process listening)
```

```bash
# 1) Service와 EndpointSlice: 엔드포인트 수가 Ready Pod 수와 같아야 함
kubectl get svc <svc> -n <ns> -o wide
kubectl get endpointslices -n <ns> -l kubernetes.io/service-name=<svc>

# 2) 엔드포인트가 없으면 selector와 Pod label 비교
kubectl get svc <svc> -n <ns> -o jsonpath='{.spec.selector}{"\n"}'
kubectl get pods -n <ns> --show-labels

# 3) 임시 Pod에서 DNS와 연결 시험 (종료 시 자동 삭제)
kubectl run -it --rm --restart=Never dnstest -n <ns> --image=registry.k8s.io/busybox:1.27.2 -- sh
#   nslookup <svc>
#   nslookup <svc>.<ns>.svc.cluster.local
#   nslookup kubernetes.default
#   cat /etc/resolv.conf
#   wget -qO- http://<svc>:<port>/
#   wget -qO- http://<pod-ip>:<targetPort>/

# 4) kube-proxy 동작 모드와 규칙 (노드에서)
curl -s localhost:10249/proxyMode
sudo iptables-save | grep <svc>
```

| 증상                                | 원인 후보                                              |
|-------------------------------------|--------------------------------------------------------|
| EndpointSlice가 비어 있음           | selector와 label 불일치, Pod가 Ready가 아님            |
| Pod IP로는 되는데 Service로는 안 됨 | `targetPort`와 `containerPort` 불일치, kube-proxy 문제 |
| IP로는 되는데 이름으로 안 됨        | CoreDNS 상태, `resolv.conf`의 nameserver·search        |
| 특정 Pod에서만 안 됨                | NetworkPolicy가 Ingress·Egress를 막고 있음             |
| 앱은 듣는데 연결 거부               | 앱이 `127.0.0.1`에만 바인딩(`0.0.0.0`으로 바꿔야 함)   |

```bash
# CoreDNS 상태와 로그
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50

# 대상 Pod에 적용되는 NetworkPolicy
kubectl get networkpolicy -n <ns>
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. kubectl debug

운영 이미지에는 셸·진단 도구가 없는 경우가 많습니다. `kubectl debug`는 원본 컨테이너를 바꾸지 않고 진단 컨테이너를 붙입니다.

| 형태                     | 명령                                                                             | 용도                                    |
|--------------------------|----------------------------------------------------------------------------------|-----------------------------------------|
| 임시(ephemeral) 컨테이너 | `kubectl debug -it <pod> --image=busybox:1.28 --target=<container>`              | 실행 중 Pod에 도구 컨테이너 추가        |
| Pod 복사본               | `kubectl debug <pod> -it --image=ubuntu --share-processes --copy-to=<pod>-debug` | 원본을 건드리지 않고 실험               |
| 이미지 바꾼 복사본       | `kubectl debug <pod> --copy-to=<pod>-debug --set-image=*=ubuntu`                 | 도구가 든 이미지로 교체해 재현          |
| 노드 디버그              | `kubectl debug node/<node> -it --image=ubuntu`                                   | 노드 루트 파일시스템을 `/host`에 마운트 |

- `--target`은 지정한 컨테이너의 프로세스 네임스페이스에 붙어 그 프로세스를 볼 수 있게 합니다. 런타임이 지원하지 않으면 프로세스가 보이지 않을 수 있습니다.
- 임시 컨테이너를 추가하려면 `pods/ephemeralcontainers` 하위 리소스에 대한 `update`/`patch` 권한이 필요하고, 추가한 임시 컨테이너는 Pod를 지울 때까지 남습니다.
- `--profile`로 보안 설정을 고릅니다: `legacy`(지정하지 않을 때 기본, 지원 중단 예정), `general`, `baseline`, `restricted`, `netadmin`, `sysadmin`.
- 노드 디버그 Pod는 호스트 IPC·Network·PID 네임스페이스를 쓰지만 privileged가 아닙니다. 루트 권한이 필요하면 `--profile=sysadmin`을 씁니다.

🟡 `sysadmin` 프로필과 노드 디버그는 노드 전체 권한에 가깝습니다. 운영 클러스터에서는 사용 기록을 남기고, 끝나면 `kubectl delete pod <node-debugger-pod>`로 바로 지웁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 노드 문제

```bash
# 노드 상태와 조건
kubectl get nodes -o wide
kubectl describe node <node>

# 노드에서 kubelet·런타임 확인
sudo systemctl status kubelet
sudo journalctl -u kubelet --since "30 min ago" --no-pager | tail -100
sudo crictl ps -a
sudo crictl logs <container-id>

# 디스크와 inode
df -h /var/lib/kubelet /var/lib/containerd
df -i /var/lib/kubelet
```

| 증상                         | 확인할 것                                                     |
|------------------------------|---------------------------------------------------------------|
| `NotReady`                   | kubelet 실행 여부, CNI 설치, 런타임 소켓, 인증서 만료         |
| `DiskPressure`               | 이미지·로그 누적. `crictl rmi --prune`으로 미사용 이미지 정리 |
| `PIDPressure`                | 프로세스 폭증 Pod. `ps -eLf \| wc -l`                         |
| Pod가 `Terminating`에서 멈춤 | `metadata.finalizers`, UPDATE를 막는 admission webhook        |

Terminating 문제는 먼저 finalizer를 확인합니다.

```bash
kubectl get pod <pod> -n <ns> -o jsonpath='{.metadata.finalizers}{"\n"}'
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
```

🟡 `kubectl delete pod --grace-period=0 --force`는 API에서 객체만 지우고 노드의 컨테이너가 실제로 멈췄는지 기다리지 않습니다. StatefulSet Pod에 쓰면 같은 이름의 Pod가 둘 실행되어 데이터가 손상될 수 있으므로, 노드가 확실히 내려갔는지 확인한 뒤에만 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 점검표

장애 보고를 쓰기 전에 아래 사실을 모았는지 확인합니다.

- [ ] 영향 범위: 어떤 네임스페이스·Deployment·노드에서, 몇 개 Pod가 영향받는가
- [ ] 시작 시각과 직전 변경(배포, 설정, 노드 작업, 인증서 갱신)
- [ ] `kubectl describe`의 Events와 `kubectl get events` 저장본
- [ ] 직전 컨테이너 로그(`--previous`)와 종료 코드·이유
- [ ] requests·limits와 실제 사용량(`kubectl top`)
- [ ] 노드 Conditions와 kubelet 로그
- [ ] Service의 EndpointSlice 수와 DNS 조회 결과
- [ ] 취한 조치와 결과(롤백, 재시작, 자원 조정), 재발 방지 항목

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Debug Pods: [kubernetes.io/docs/tasks/debug/debug-application/debug-pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) — ★★★☆☆ (확인일 2026-11-16)
- Debug Running Pods: [kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/) — ★★★☆☆ (확인일 2026-11-16)
- Debug Services: [kubernetes.io/docs/tasks/debug/debug-application/debug-service](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) — ★★★☆☆ (확인일 2026-11-16)
- Determine the Reason for Pod Failure: [kubernetes.io/docs/tasks/debug/debug-application/determine-reason-pod-failure](https://kubernetes.io/docs/tasks/debug/debug-application/determine-reason-pod-failure/) — ★★★☆☆ (확인일 2026-11-16)
- Pod Lifecycle: [kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) — ★★★☆☆ (확인일 2026-11-16)
- Node-pressure Eviction: [kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/) — ★★★☆☆ (확인일 2026-11-16)
- Kubernetes Releases: [kubernetes.io/releases](https://kubernetes.io/releases/) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
