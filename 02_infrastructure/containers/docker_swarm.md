# Docker Swarm
<!-- reference: _reference/docker_swarm_official_notes.md -->

Docker Engine에 들어 있는 컨테이너 오케스트레이션 기능(Swarm 모드)입니다. 여러 Docker 호스트를 하나의 클러스터로 묶고, 서비스 단위로 복제·롤링 업데이트·장애 시 재배치를 합니다. 별도 설치 없이 `docker swarm init`으로 시작하고 Compose 파일 형식으로 배포할 수 있어, Kubernetes보다 작은 규모에 맞습니다. 이 문서만으로 클러스터 만들기 → 서비스 배포 → 업데이트·롤백 → secret·config → stack 배포 → 장애 확인 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Docker Engine v29.10.1 (2026-11-24) (2026-11-27 확인)
- 예제 시험: 2026-11-27 2~8절을 `docker:29-dind` 컨테이너 3개(관리 노드 1·작업 노드 2, 관리 노드 3개 구성도 따로)로 실행해 init·join, routing mesh, scale, 롤링 업데이트와 실패 시 자동 롤백, drain, secret·config, stack 배포와 overlay DNS, 관리 노드 장애와 quorum 상실, autolock을 확인. 실제 서버 여러 대, 방화벽 설정, TLS 인증서 교체, 백업·복구는 미실행

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 클러스터 만들기](#2-클러스터-만들기) / [3. 서비스](#3-서비스)                             |
| [4. 업데이트와 롤백](#4-업데이트와-롤백) / [5. 노드 관리](#5-노드-관리) / [6. secret과 config](#6-secret과-config) |
| [7. stack 배포](#7-stack-배포) / [8. 장애와 quorum](#8-장애와-quorum) / [9. 검증](#9-검증)                         |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기)                                                         |

---

## 1. 개요

```text
docker CLI (on a manager)
    │
    v
managers (Raft):  m1 Leader / m2 Reachable / m3 Reachable   -> cluster state, scheduling
    │
    │ tasks
    v
workers:          w1 / w2 / w3                              -> run containers
                  (overlay network + routing mesh)
```

| 용어    | 뜻                                                        |
|---------|-----------------------------------------------------------|
| node    | Swarm에 들어온 Docker 호스트. manager와 worker            |
| service | 원하는 상태 선언(이미지, replica 수, 포트, 업데이트 방식) |
| task    | service가 노드에 배치한 컨테이너 하나                     |
| stack   | Compose 파일로 묶어 배포한 여러 service                   |

| 포트         | 쓰임                                         |
|--------------|----------------------------------------------|
| TCP 2377     | manager와의 통신, manager 사이 통신          |
| TCP·UDP 7946 | overlay 네트워크 노드 발견                   |
| UDP 4789     | overlay 네트워크 데이터(VXLAN, 바꿀 수 있음) |

- 시험에서 manager는 TCP 2377·7946을 열고 있었습니다(UDP 포트는 확인하지 않음).
- Kubernetes와 비교: 설정이 적고 Compose 파일을 거의 그대로 쓰지만, 자동 확장(HPA)·CRD·생태계 도구는 없습니다. 노드 수십 대 이하, 운영 인력이 적은 곳에서 고려합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 클러스터 만들기

```bash
# manager에서
docker swarm init --advertise-addr <MANAGER_IP>

# worker 참가 명령 출력 (토큰 포함)
docker swarm join-token worker

# 각 worker에서
docker swarm join --token <WORKER_TOKEN> <MANAGER_IP>:2377

# manager에서 확인
docker node ls
```

```text
HOSTNAME   STATUS   AVAILABILITY   MANAGER STATUS
m1         Ready    Active         Leader
w1         Ready    Active
w2         Ready    Active
```

- manager로 참가시키려면 `docker swarm join-token manager`의 토큰을 쓰거나, 참가 뒤 `docker node promote <노드>`를 씁니다.
- 토큰이 새었으면 `docker swarm join-token --rotate worker`로 바꿉니다(이미 참가한 노드는 영향 없음).
- worker에서는 클러스터 명령을 쓸 수 없습니다. `docker service ls`는 `This node is not a swarm manager`로 거부됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 서비스

```bash
docker service create --name web --replicas 3 \
  --publish published=8080,target=80 nginx:1.29-alpine

docker service ls
docker service ps web          # task가 어느 노드에 있는지
docker service scale web=5
docker service logs web
```

- routing mesh: 공개한 포트(8080)는 모든 노드에서 열립니다. 시험에서 task가 있든 없든 worker IP의 8080으로 접속하면 nginx 응답이 왔습니다. 앞단 로드밸런서는 아무 노드로 보내도 됩니다.
- `--mode global`은 노드마다 하나씩 띄웁니다(로그 수집기·모니터링 agent 등).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 업데이트와 롤백

```bash
# 2개씩, 2초 간격으로 교체
docker service update --image nginx:1.29.3-alpine \
  --update-parallelism 2 --update-delay 2s web

# 실패하면 자동으로 이전 설정으로 되돌리기
docker service update --image nginx:1.29.4-alpine \
  --update-failure-action rollback --update-monitor 30s web

# 직전 설정으로 수동 롤백
docker service rollback web
```

| 옵션                         | 뜻                                                    |
|------------------------------|-------------------------------------------------------|
| `--update-parallelism`       | 한 번에 바꿀 task 수                                  |
| `--update-delay`             | 묶음 사이 대기                                        |
| `--update-order start-first` | 새 task를 먼저 띄우고 옛 task를 내림(기본 stop-first) |
| `--update-failure-action`    | 실패 시 `pause`(기본), `continue`, `rollback`         |
| `--update-monitor`           | 새 task를 실패로 볼지 지켜보는 시간                   |

- 시험에서 없는 이미지(`nginx:does-not-exist`)로 업데이트하면 `UpdateStatus`가 `rollback_completed`가 되고 이미지가 직전 값으로 돌아갔습니다.
- 자동 롤백이 끝난 직후 `docker service rollback`을 하면 `service ... does not have a previous spec`로 실패했습니다. 롤백은 직전 설정 한 단계만 기억합니다.
- 이미지는 태그만 쓰면 manager가 다이제스트(`@sha256:...`)로 고정해 모든 노드가 같은 이미지를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 노드 관리

```bash
# 점검 전: 이 노드의 task를 다른 노드로 옮김
docker node update --availability drain w1

# 점검 뒤
docker node update --availability active w1

# 다시 고르게 나누기 (task 재생성)
docker service update --force web

# 노드 역할·라벨
docker node promote w1
docker node update --label-add zone=a w1
```

- 시험에서 `drain` 뒤 w1의 task가 m1·w2로 옮겨졌고, `active`로 되돌려도 task는 돌아오지 않았습니다(m1 1, w2 2). `docker service update --force web` 뒤에 m1·w1·w2에 하나씩 나뉘었습니다.
- manager도 기본으로 task를 받습니다. manager를 관리 전용으로 두려면 manager에 `drain`을 겁니다.
- 배치 조건은 `--constraint node.role==worker`, `--constraint node.labels.zone==a`처럼 줍니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. secret과 config

```bash
printf '%s' '<DB_PASSWORD>' | docker secret create db_pw -
printf 'hello=1\n' | docker config create app_conf -

docker service create --name app \
  --secret db_pw \
  --config source=app_conf,target=/etc/app.conf \
  alpine:3.22 sh -c 'cat /run/secrets/db_pw; sleep 3600'
```

- secret은 컨테이너 안 `/run/secrets/<이름>`에 읽기 전용 tmpfs로 붙습니다(시험: `tmpfs on /run/secrets/db_pw type tmpfs (ro,...)`). config는 지정한 경로에 파일로 붙습니다.
- `docker secret inspect`에는 값이 나오지 않습니다(`{"Name":"db_pw","Labels":{}}`).
- 사용 중인 secret은 지울 수 없습니다(`secret 'db_pw' is in use by the following service: sc`). 값을 바꿀 때는 새 이름(`db_pw_v2`)으로 만들고 `docker service update --secret-rm db_pw --secret-add source=db_pw_v2,target=db_pw`로 바꿉니다.
- secret은 manager의 Raft 로그에 암호화돼 저장됩니다. manager 디스크까지 보호하려면 autolock(8절)을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. stack 배포

Compose 파일의 `deploy:` 항목으로 replica·업데이트·배치 조건을 정합니다.

```yaml
services:
  api:
    image: traefik/whoami:v1.11
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        order: start-first
      resources:
        limits:
          memory: 64M
    networks: [backnet]
  front:
    image: nginx:1.29-alpine
    ports:
      - "8081:80"
    deploy:
      placement:
        constraints: [node.role == worker]
    networks: [backnet]
networks:
  backnet:
    driver: overlay
```

```bash
docker stack deploy -c stack.yml demo
docker stack services demo
docker stack ps demo
docker stack rm demo
```

- 서비스 이름은 `<stack>_<service>`(`demo_api`)가 되고, 같은 overlay 네트워크 안에서는 서비스 이름(`api`)으로 접속합니다. 시험에서 `front` 컨테이너에서 `http://api/`로 whoami 응답을 받았습니다.
- `build:`는 쓸 수 없습니다. 이미지를 레지스트리에 올리고 `image:`로 지정합니다(시험: `invalid image reference for service b: no image specified`).
- 비공개 레지스트리 이미지는 `docker stack deploy --with-registry-auth`로 인증 정보를 노드에 넘깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 장애와 quorum

manager는 Raft 합의로 상태를 맞추므로, 과반이 살아 있어야 클러스터를 바꿀 수 있습니다.

| manager 수 | 견딜 수 있는 manager 장애 |
|------------|---------------------------|
| 1          | 0                         |
| 3          | 1                         |
| 5          | 2                         |

- manager 1개 구성에서 manager를 멈추자 worker의 컨테이너는 계속 돌았고, worker의 `docker info`는 `control=false`였습니다. manager를 다시 켜고 약 20초 뒤 모든 노드가 Ready로 돌아왔습니다.
- manager 3개 구성에서 리더를 멈추자 다른 manager가 Leader가 됐고 서비스는 3/3을 유지했습니다.
- 3개 중 2개를 멈추면 쓰기와 조회 모두 `The swarm does not have a leader. It's possible that too few managers are online. Make sure more than half of the managers are online.`로 실패했습니다(멈춘 뒤 약 45초 시점, 15초 시점에는 아직 조회가 됨). 이미 떠 있던 컨테이너는 계속 돌았습니다.
- manager는 홀수(3 또는 5)로 두고, 서로 다른 장애 영역(랙·가용 영역)에 나눕니다.

autolock을 켜면 Docker 재시작 때 잠금 키를 넣어야 manager가 상태를 엽니다.

```bash
docker swarm update --autolock=true     # SWMKEY-1-... 키 출력, 따로 보관
docker swarm unlock                      # 재시작 뒤 키 입력
docker swarm unlock-key                  # 현재 키 보기 (manager에서)
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용    | 방법                                                            | 기대 결과                             |
|------|--------------|-----------------------------------------------------------------|---------------------------------------|
| 1    | 노드         | `docker node ls`                                                | 모든 노드 Ready·Active, Leader 하나   |
| 2    | 서비스       | `docker service ls`                                             | REPLICAS가 `3/3`처럼 맞음             |
| 3    | 배치         | `docker service ps web`                                         | task가 여러 노드에 Running            |
| 4    | routing mesh | 아무 노드 IP의 공개 포트로 접속                                 | 응답                                  |
| 5    | 업데이트     | `docker service inspect --format '{{.UpdateStatus.State}}' web` | `completed` 또는 `rollback_completed` |
| 6    | secret       | 컨테이너 안 `/run/secrets/`                                     | 파일 있음, 읽기 전용                  |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                              | 원인                                     | 조치                                                                               |
|---------------------------------------------------|------------------------------------------|------------------------------------------------------------------------------------|
| `This node is not a swarm manager`                | worker에서 클러스터 명령                 | manager에서 실행 또는 `docker node promote`                                        |
| `The swarm does not have a leader ...`            | manager 과반 장애                        | manager 복구. 복구 불가면 남은 manager에서 `docker swarm init --force-new-cluster` |
| `secret '...' is in use by the following service` | 사용 중인 secret 삭제                    | 새 secret으로 교체 뒤 삭제                                                         |
| `does not have a previous spec`                   | 되돌릴 직전 설정 없음(자동 롤백 직후 등) | 원하는 이미지로 `service update`                                                   |
| `no image specified` (stack)                      | `build:`만 있는 서비스                   | 이미지를 레지스트리에 올리고 `image:` 지정                                         |
| 점검 뒤 노드에 task가 없음                        | `active`로 되돌려도 재분배 안 함         | `docker service update --force <service>`                                          |
| overlay 네트워크로 통신 안 됨                     | UDP 4789·7946 방화벽 차단                | 노드 사이 포트 허용                                                                |

- `--force-new-cluster`는 남은 manager 하나로 클러스터를 새로 세우는 복구 명령입니다(미시험). 다른 manager는 다시 참가시켜야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Docker Compose](./docker_compose.md) — stack 파일의 바탕
- [Docker 네트워크](./docker_network.md) — overlay 네트워크
- [Kubernetes 기초](./kubernetes_basic.md) — 더 큰 규모의 오케스트레이션

---

## 참고 자료

- Docker Docs: [Swarm mode overview](https://docs.docker.com/engine/swarm/) · [Deploy services](https://docs.docker.com/engine/swarm/services/) · [Raft consensus](https://docs.docker.com/engine/swarm/raft/) · [Admin guide](https://docs.docker.com/engine/swarm/admin_guide/) — ★★★☆☆
- GitHub: [moby/moby releases](https://github.com/moby/moby/releases) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
