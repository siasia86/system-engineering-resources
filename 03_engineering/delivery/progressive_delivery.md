# Progressive Delivery

새 버전을 한 번에 모든 사용자에게 내보내지 않고, 노출 범위를 단계적으로 넓히면서 지표로 진행 여부를 판정하는 배포 방식입니다. 이 문서는 Rolling Update, Blue-Green, Canary의 차이와 Kubernetes Deployment·Argo Rollouts에서의 설정, 롤백 판단 기준을 다룹니다.

## 목차

| 섹션                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 배포 전략 비교](#2-배포-전략-비교) / [3. Kubernetes Rolling Update](#3-kubernetes-rolling-update)   |
| [4. Blue-Green](#4-blue-green) / [5. Canary 설계](#5-canary-설계) / [6. Argo Rollouts 자동 분석](#6-argo-rollouts-자동-분석) |
| [7. 롤백 판단 기준](#7-롤백-판단-기준) / [8. 체크리스트](#8-체크리스트) / [9. 트러블슈팅](#9-트러블슈팅)                     |

## 1. 개요

| 항목      | 값                                                                                                                                                             |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 목적      | 결함이 있는 변경이 영향을 주는 사용자 수와 시간을 줄임                                                                                                         |
| 핵심 수단 | 노출 범위 제한(트래픽 비율·서버 일부) + 지표 기반 판정 + 빠른 되돌림                                                                                           |
| 출처      | Google SRE Workbook Ch.16 "Canarying Releases", Kubernetes 문서, Argo Rollouts 문서                                                                            |
| 연관 문서 | [Change Management](./change_management.md), [Zero-Downtime Migration](./zero_downtime_migration.md), [SLO & Error Budget](../reliability/slo_error_budget.md) |

SRE Workbook은 canarying을 "변경을 서비스 일부에 일정 시간만 배포하고 평가하는 것(a partial and time-limited deployment of a change in a service and its evaluation)"으로 정의합니다. 변경을 받은 쪽을 canary, 나머지를 control이라고 부르며, 평가 결과로 배포를 계속할지 정합니다.

Progressive Delivery는 이런 단계적 노출과 자동 판정을 배포 파이프라인 전체에 적용하는 접근을 가리키는 말입니다. 배포(deploy, 코드가 서버에 올라감)와 출시(release, 사용자가 기능을 보게 됨)를 나누어 생각하면 이해가 쉽습니다. 이 문서는 배포 단계를, [Feature Flag 관리](./feature_flag_management.md)는 출시 단계를 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 배포 전략 비교

| 전략               | 동작                                                  | 추가 자원           | 되돌림 속도          | 버전 공존   | 적합한 경우                                     |
|--------------------|-------------------------------------------------------|---------------------|----------------------|-------------|-------------------------------------------------|
| Recreate           | 기존 Pod를 모두 종료한 뒤 새 Pod 생성                 | 없음                | 느림 (재배포)        | 없음        | 두 버전이 동시에 돌면 안 되는 경우, 개발 환경   |
| Rolling Update     | 기존 Pod를 조금씩 새 Pod로 교체                       | 작음 (maxSurge만큼) | 중간 (다시 롤링)     | 있음        | 상태 없는 일반 서비스의 기본값                  |
| Blue-Green         | 새 환경 전체를 띄운 뒤 트래픽을 한 번에 전환          | 약 2배              | 빠름 (트래픽 재전환) | 전환 순간만 | 전환 전 검증이 중요하고 자원 여유가 있는 경우   |
| Canary             | 일부 트래픽만 새 버전으로 보내고 지표로 판정하며 확대 | 작음~중간           | 빠름 (가중치 0)      | 있음        | 사용자 영향 최소화, 실트래픽 검증이 필요한 경우 |
| Shadow (Mirroring) | 실트래픽을 복제해 새 버전에도 보내되 응답은 버림      | 큼                  | 해당 없음            | 있음        | 읽기 위주 API의 성능·정합성 사전 검증           |

### 선택 기준

| 질문                                                       | Yes일 때                                                              |
|------------------------------------------------------------|-----------------------------------------------------------------------|
| 두 버전이 같은 DB 스키마·메시지 형식을 동시에 써도 되는가? | Rolling·Canary 가능. 아니면 먼저 스키마를 하위 호환으로 바꿈          |
| 전환 직후 문제를 1분 안에 되돌려야 하는가?                 | Blue-Green 또는 트래픽 라우터 기반 Canary                             |
| 트래픽 비율을 1% 단위로 세밀하게 조절해야 하는가?          | Ingress·Service Mesh 등 트래픽 라우터 필요 (Pod 수 비율만으로는 부족) |
| 쓰기 요청이 외부에 부작용(결제·메일)을 내는가?             | Shadow는 쓰지 않거나 부작용을 차단한 뒤 사용                          |

🟡 Rolling·Canary·Blue-Green 모두 일정 시간 두 버전이 함께 동작합니다. DB 스키마 변경은 expand → migrate → contract 순서로 나누어 두 버전이 모두 동작하도록 만든 뒤 배포합니다([Zero-Downtime Migration](./zero_downtime_migration.md) 참고).

[⬆ 목차로 돌아가기](#목차)

## 3. Kubernetes Rolling Update

Kubernetes Deployment의 `.spec.strategy.type`은 `RollingUpdate`(기본값)와 `Recreate` 두 가지입니다.

### 주요 필드 (Kubernetes 문서 기준, 확인일 2026-11-16)

| 필드                                    | 기본값 | 의미                                                                 |
|-----------------------------------------|--------|----------------------------------------------------------------------|
| `strategy.rollingUpdate.maxUnavailable` | 25%    | 업데이트 중 사용할 수 없는 Pod 최대 수. 백분율은 내림 계산           |
| `strategy.rollingUpdate.maxSurge`       | 25%    | 원하는 Pod 수를 넘어 추가로 만들 수 있는 최대 수. 백분율은 올림 계산 |
| `minReadySeconds`                       | 0      | 새 Pod가 Ready 상태로 이 시간 동안 버텨야 available로 셈             |
| `progressDeadlineSeconds`               | 600    | 이 시간 안에 진행이 없으면 `ProgressDeadlineExceeded`로 실패 보고    |
| `revisionHistoryLimit`                  | 10     | 롤백용으로 남길 이전 ReplicaSet 수                                   |

`maxUnavailable`과 `maxSurge`는 둘 다 0일 수 없습니다. 용량 여유가 없는 서비스는 `maxUnavailable: 0`, `maxSurge: 1`처럼 설정해 처리 용량이 줄지 않게 교체합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 6
  minReadySeconds: 30
  progressDeadlineSeconds: 600
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: registry.example.com/web:1.4.2
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 5
```

`minReadySeconds`를 0으로 두면 readiness probe가 한 번 통과한 직후 다음 Pod 교체가 진행됩니다. 기동 직후에만 정상이고 몇십 초 뒤 실패하는 결함을 잡으려면 이 값을 늘립니다.

### rollout 명령

```bash
kubectl rollout status deployment/web                 # 완료 대기, 실패 시 종료 코드 1
kubectl rollout history deployment/web                # revision 목록
kubectl rollout history deployment/web --revision=3   # 특정 revision의 Pod template
kubectl rollout pause deployment/web                  # 진행 일시 중지
kubectl rollout resume deployment/web
kubectl rollout undo deployment/web                   # 직전 revision으로
kubectl rollout undo deployment/web --to-revision=3
```

`kubectl rollout status`는 rollout이 성공하면 종료 코드 0, 진행 기한 초과 등으로 실패하면 1을 돌려주므로 CI 파이프라인의 배포 완료 판정에 쓸 수 있습니다.

### Deployment만으로 Canary를 할 때

Kubernetes 문서는 버전마다 Deployment를 하나씩 만들고 같은 Service selector로 묶는 방식을 안내합니다. 예를 들어 stable 9개, canary 1개 replica를 두면 대략 10%가 canary로 갑니다. 비율이 replica 수에 묶이고 지표 판정·자동 롤백이 없으므로, 세밀한 비율과 자동 판정이 필요하면 6절의 도구나 Service Mesh를 씁니다.

[⬆ 목차로 돌아가기](#목차)

## 4. Blue-Green

현재 운영 환경(blue)과 같은 구성의 새 환경(green)을 띄우고, 검증이 끝나면 로드 밸런서나 Service selector를 green으로 바꿉니다. 문제가 생기면 selector를 blue로 되돌립니다.

```text
            +------------------+
 users ---> |  router / LB     |
            +--------+---------+
                     |  (switch)
          +----------+-----------+
          v                      v
   +-------------+        +-------------+
   | blue  v1    |        | green v2    |
   | (active)    |        | (preview)   |
   +-------------+        +-------------+
```

| 점검 항목      | 내용                                                                                            |
|----------------|-------------------------------------------------------------------------------------------------|
| 자원           | 전환 전후 두 환경이 모두 떠 있으므로 약 2배 용량이 필요                                         |
| 전환 지연      | Service selector 변경 후 각 노드의 iptables 등 규칙이 갱신될 때까지 일부 트래픽이 이전 Pod로 감 |
| 이전 환경 유지 | 전환 직후 바로 지우지 않고 일정 시간 유지해 빠른 되돌림에 대비                                  |
| 세션·캐시      | green의 캐시가 비어 있으면 전환 직후 지연이 커질 수 있음. 사전 warm-up 고려                     |
| 데이터         | 두 환경이 같은 DB를 쓰면 스키마 호환이 필수                                                     |

Argo Rollouts의 blueGreen 전략은 `activeService`(운영 트래픽)와 `previewService`(검증용)를 따로 두고, 승격 후 `scaleDownDelaySeconds`(기본 30초) 동안 이전 ReplicaSet을 유지합니다. 이 지연은 위의 규칙 전파 시간 동안 이전 Pod로 간 요청이 실패하지 않게 하기 위한 것입니다.

SRE Workbook은 blue/green이 시간 전후 비교(before/after) 방식에 가깝다고 설명하며, 새 환경으로 보내는 트래픽 비율을 점진적으로 늘리면 canary처럼 운영할 수 있다고 덧붙입니다.

[⬆ 목차로 돌아가기](#목차)

## 5. Canary 설계

### 크기와 기간

| 결정      | 기준 (SRE Workbook Ch.16 요약)                                                                  |
|-----------|-------------------------------------------------------------------------------------------------|
| 크기      | 문제를 드러낼 만큼 트래픽이 충분하되, 실패 시 error budget 소모가 감당 가능한 수준              |
| 기간      | 배포 주기에 맞춤. 하루 여러 번 배포하면 짧게, 비대화형 작업은 작업 단위 하나가 끝나는 시간 이상 |
| 시간대    | 성능 결함은 부하가 높을 때 드러나므로 한산한 시간대만으로 판정하지 않음                         |
| 동시 실행 | 한 번에 canary 하나만 실행. 여러 개가 겹치면 어느 변경이 원인인지 구분하기 어려움               |

Error budget 관점에서 canary의 위험은 노출된 트래픽 비율과 시간에 비례합니다. 예를 들어 월 SLO 99.9%(허용 실패 0.1%)인 서비스에서 5% canary가 1시간 동안 전부 실패하면, 한 달(약 720시간) 기준 예산 대비 소모는 다음과 같이 어림할 수 있습니다.

```text
consumed = 0.05 (traffic share) x 1 h / 720 h = 0.0000694 of all requests
budget   = 0.001 of all requests
ratio    = 0.0000694 / 0.001 = about 7% of monthly error budget
```

### 판정 지표

| 원칙                       | 설명                                                                                   |
|----------------------------|----------------------------------------------------------------------------------------|
| 문제를 나타낼 것           | 오류율·지연처럼 사용자가 느끼는 지표(대개 SLI)를 우선. CPU처럼 잡음이 큰 지표는 보조로 |
| 적게 고를 것               | 지표가 많으면 우연한 차이로 거짓 실패가 늘어남. Workbook은 십여 개 정도를 언급         |
| 원인이 변경에 있을 것      | canary와 control을 같은 시간에 비교해 요일·시간대 효과를 제거                          |
| 측정 창이 짧을 것          | 집계 창이 canary 기간보다 길면 차이가 희석됨 (30분 canary에 1시간 평균은 부적합)       |
| canary와 control을 나눌 것 | 전체 서비스 합계만 보면 canary의 심각한 실패가 묻힘. 버전 label로 지표를 분리          |

[⬆ 목차로 돌아가기](#목차)

## 6. Argo Rollouts 자동 분석

Argo Rollouts는 Deployment 대신 `Rollout` 리소스를 쓰는 Kubernetes 컨트롤러로, canary·blueGreen 전략과 지표 기반 분석을 제공합니다. 이 문서 작성 시점 최신 릴리스는 v1.10.2입니다(GitHub releases, 확인일 2026-11-16).

### 단계 정의

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web
spec:
  replicas: 10
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: registry.example.com/web:1.4.2
  strategy:
    canary:
      analysis:
        templates:
          - templateName: success-rate
        startingStep: 1
        args:
          - name: service-name
            value: web
      steps:
        - setWeight: 10
        - pause: {duration: 10m}
        - setWeight: 30
        - pause: {duration: 10m}
        - setWeight: 60
        - pause: {}            # 사람이 promote 할 때까지 대기
```

트래픽 라우터(Ingress·Service Mesh) 연동 없이 쓰면 `setWeight`는 Pod 수 비율로 근사됩니다. 예를 들어 replica 10개에 10%면 canary 1개, stable 9개입니다.

### 분석 템플릿

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 5m
      successCondition: result[0] >= 0.99
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.example.com:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",code!~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

AnalysisRun 결과는 Successful(계속), Failed(중단·롤백), Inconclusive(일시 중지) 세 가지입니다. `failureLimit`을 넘는 실패가 나오면 rollout이 중단되고 stable 버전으로 돌아갑니다.

### kubectl 플러그인 명령

```bash
kubectl argo rollouts get rollout web --watch            # 단계·가중치·분석 상태 확인
kubectl argo rollouts set image web web=registry.example.com/web:1.4.3
kubectl argo rollouts promote web                        # 다음 단계로
kubectl argo rollouts abort web                          # 중단, stable로 트래픽 복귀
kubectl argo rollouts retry rollout web                  # 중단된 rollout 재시도
kubectl argo rollouts undo web                           # 직전 revision으로
```

🟡 `abort`는 트래픽을 stable로 돌리지만 `spec.template`은 새 버전 그대로 남습니다. 중단 상태를 벗어나면 다시 새 버전으로 가려 하므로, 완전히 되돌리려면 manifest(또는 GitOps 저장소)의 이미지도 이전 버전으로 되돌립니다. `promote --full`은 남은 분석·대기·단계를 모두 건너뛰므로 긴급한 경우에만 씁니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 롤백 판단 기준

자동 분석이 없더라도 배포 전에 "어떤 값이면 되돌린다"를 숫자로 정해 두면, 배포 중 판단이 빨라집니다.

| 신호          | 예시 기준                                                 | 행동                           |
|---------------|-----------------------------------------------------------|--------------------------------|
| 오류율        | canary 5xx 비율이 control보다 0.5%p 이상 높음이 10분 지속 | 즉시 abort                     |
| 지연          | canary p99가 control 대비 1.5배 이상                      | 일시 중지 후 원인 확인         |
| 포화          | canary Pod의 재시작(CrashLoopBackOff, OOMKilled) 발생     | 즉시 abort                     |
| 비즈니스 지표 | 결제 성공률·로그인 성공률 하락                            | 즉시 abort, 인시던트 선언 검토 |
| 데이터        | canary가 만든 데이터 형식 오류                            | abort 후 데이터 정정 계획 수립 |

위 숫자는 설명용 예시입니다. 서비스의 SLO와 평소 변동 폭을 보고 정합니다. 되돌림이 늦어질수록 영향이 커지므로, "원인을 알 때까지 기다린다"보다 "먼저 되돌리고 원인을 찾는다"를 기본으로 둡니다. 되돌린 뒤의 절차는 [Incident Management](../reliability/incident_management.md)를 따릅니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 체크리스트

### 배포 전

- [ ] 새 버전이 이전 버전과 같은 DB 스키마·API·메시지 형식에서 함께 동작하는가
- [ ] readiness probe가 실제 처리 가능 여부를 반영하는가 (의존성 연결 확인 포함)
- [ ] canary와 control을 구분하는 label이 지표에 붙는가
- [ ] 판정 지표와 롤백 기준을 숫자로 적어 두었는가
- [ ] 롤백 명령과 담당자가 정해져 있는가
- [ ] 다른 canary가 진행 중이지 않은가

### 배포 중

- [ ] 각 단계에서 canary와 control 지표를 나란히 확인했는가
- [ ] 부하가 높은 시간대를 한 번 이상 거쳤는가
- [ ] 로그에 새 오류 유형이 나타나지 않았는가

### 배포 후

- [ ] 이전 ReplicaSet·환경을 정리할 시점을 정했는가
- [ ] 배포 기록(버전·시각·결과)을 변경 이력에 남겼는가

[⬆ 목차로 돌아가기](#목차)

## 9. 트러블슈팅

| 증상                                               | 가능한 원인                                                          | 확인·조치                                                                                         |
|----------------------------------------------------|----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `rollout status`가 끝나지 않고 600초 뒤 실패       | 새 Pod가 Ready가 되지 않음, 이미지 pull 실패, 자원 부족              | `kubectl describe deployment`의 Conditions, `kubectl get events` 확인                             |
| 롤링 중 처리 용량 부족으로 지연 증가               | `maxUnavailable` 때문에 동시에 여러 Pod가 빠짐                       | `maxUnavailable: 0`, `maxSurge: 1` 이상으로 조정                                                  |
| canary 지표가 control과 차이 없음인데 배포 후 장애 | canary 비율·기간이 작아 결함이 드러나지 않음, 지표 집계 창이 너무 김 | canary 기간에 피크 시간 포함, 버전별 지표 분리                                                    |
| canary 비율이 설정과 다름                          | 트래픽 라우터 없이 Pod 수로 근사, 세션 고정(sticky)                  | replica 수 조정 또는 트래픽 라우터 연동                                                           |
| Blue-Green 전환 직후 일부 요청 실패                | 이전 Pod를 너무 빨리 종료                                            | `scaleDownDelaySeconds` 유지, Pod의 graceful shutdown(preStop·terminationGracePeriodSeconds) 확인 |
| `undo` 했는데 원하는 버전이 없음                   | `revisionHistoryLimit`이 작거나 0                                    | 값을 늘리고, 이미지 태그를 GitOps 저장소에서 되돌림                                               |
| abort 후 잠시 뒤 다시 새 버전 배포 시도            | `spec.template`이 새 버전으로 남아 있음                              | manifest의 이미지를 이전 버전으로 되돌림                                                          |

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Google SRE Workbook Ch.16: [Canarying Releases](https://sre.google/workbook/canarying-releases/) — ★★★★☆ (확인일 2026-11-16)
- Kubernetes: [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) — ★★★☆☆ (확인일 2026-11-16)
- Kubernetes: [Deploy a Release Using a Canary Deployment](https://kubernetes.io/docs/tutorials/stateless-application/canary-deployment/) — ★★★☆☆ (확인일 2026-11-16)
- Argo Rollouts: [Documentation](https://argo-rollouts.readthedocs.io/en/stable/) (Canary, BlueGreen, Analysis, kubectl plugin) — ★★★☆☆ (확인일 2026-11-16)
- Argo Rollouts: [GitHub Releases](https://github.com/argoproj/argo-rollouts/releases) — ★★★☆☆ (확인일 2026-11-16)
- Martin Fowler: [BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html) — ★★☆☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
