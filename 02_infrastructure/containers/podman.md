# Podman

Podman은 데몬 없이 OCI 컨테이너를 실행하는 도구로, 일반 사용자 권한으로 컨테이너를 돌리는 rootless 실행과 systemd 연동(Quadlet)이 특징입니다.
RHEL 계열 배포판의 기본 컨테이너 도구이므로, Docker를 아는 시스템 엔지니어가 차이점과 운영 방법을 함께 익혀 두면 좋습니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Docker와 비교](#2-docker와-비교) / [3. 설치와 기본 명령](#3-설치와-기본-명령)   |
| [4. rootless 동작 원리](#4-rootless-동작-원리) / [5. rootless 설정](#5-rootless-설정) / [6. Pod](#6-pod) |
| [7. Quadlet으로 서비스 운영](#7-quadlet으로-서비스-운영) / [8. 자동 업데이트](#8-자동-업데이트)          |
| [9. Docker 호환](#9-docker-호환) / [10. 문제 해결](#10-문제-해결)                                        |

---

## 1. 개요

Podman은 Red Hat 주도로 개발되는 오픈소스 컨테이너 엔진입니다. `podman` 명령이 직접 런타임(crun 또는 runc)을 호출해 컨테이너를 만들고, 항상 떠 있는 중앙 데몬이 없습니다. 2026-11-16 확인 기준 최신 판은 v6.2.0입니다.

```text
 Docker                               Podman
 ------                               ------
 docker CLI                           podman CLI
     |  (REST over socket)                |  (fork/exec, no daemon)
     v                                    v
 dockerd (root daemon)                conmon (per container monitor)
     |                                    |
     v                                    v
 containerd -> runc                   crun / runc
     |                                    |
     v                                    v
 container                            container
```

| 구성 요소     | 역할                                                       |
|---------------|------------------------------------------------------------|
| `podman`      | CLI. 이미지·컨테이너·Pod·볼륨 관리                         |
| `conmon`      | 컨테이너마다 붙는 작은 감시 프로세스. 로그·종료 코드 수집  |
| `crun`/`runc` | OCI 런타임. 실제로 namespace·cgroup을 설정해 프로세스 실행 |
| `pasta`       | rootless 컨테이너의 기본 사용자 공간 네트워크              |
| `buildah`     | 이미지 빌드 라이브러리. `podman build`가 내부적으로 사용   |
| `skopeo`      | 레지스트리 간 이미지 복사·검사 도구(별도 패키지)           |

컨테이너가 namespace와 cgroup으로 격리되는 원리는 [컨테이너 아키텍처](./container_architecture.md)와 [namespace 개념](../../01_fundamentals/linux/namespace_concepts.md)을 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Docker와 비교

| 항목            | Docker                               | Podman                                             |
|-----------------|--------------------------------------|----------------------------------------------------|
| 데몬            | `dockerd` 상시 실행                  | 없음. 명령마다 프로세스 실행                       |
| 기본 실행 권한  | root 데몬(rootless 모드는 별도 설정) | 일반 사용자 rootless 실행이 기본 사용 방식         |
| 서비스 등록     | `--restart` 정책을 데몬이 관리       | systemd 유닛(Quadlet)으로 관리                     |
| Pod             | 없음(Compose로 묶음)                 | Kubernetes Pod와 같은 개념 지원                    |
| Kubernetes YAML | 없음                                 | `podman kube play`/`podman kube generate`          |
| 빌드 파일       | `Dockerfile`                         | `Containerfile` 또는 `Dockerfile`                  |
| 명령 호환       | -                                    | 대부분 같은 하위 명령·옵션                         |
| API 소켓        | `/var/run/docker.sock`               | 필요할 때 `podman.socket`으로 Docker 호환 API 제공 |

🟡 데몬이 없으므로 `--restart=always`만으로는 재부팅 뒤 컨테이너가 다시 뜨지 않습니다. 재부팅 후에도 실행해야 하는 컨테이너는 7절의 Quadlet으로 systemd에 등록합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설치와 기본 명령

```bash
# RHEL / Rocky / Alma / Fedora
sudo dnf install -y podman

# Debian / Ubuntu
sudo apt install -y podman

podman --version
podman info --format '{{.Host.Security.Rootless}} {{.Store.GraphRoot}}'
```

Docker 명령을 알면 대부분 그대로 쓸 수 있습니다.

```bash
podman pull docker.io/library/nginx:1.27
podman run -d --name web -p 8080:80 docker.io/library/nginx:1.27
podman ps
podman logs -f web
podman exec -it web sh
podman stop web && podman rm web

podman images
podman build -t localhost/app:1.0 .
podman system df
```

### 이미지 이름은 전체 경로로

Podman은 `/etc/containers/registries.conf`의 `unqualified-search-registries` 목록에서 짧은 이름(`nginx`)을 찾습니다. 여러 레지스트리가 등록되어 있으면 선택 창이 뜨거나 의도하지 않은 레지스트리에서 받을 수 있으므로, 스크립트와 유닛 파일에는 `docker.io/library/nginx:1.27`처럼 레지스트리를 포함한 전체 이름을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. rootless 동작 원리

rootless 컨테이너는 user namespace를 써서 컨테이너 안의 root(UID 0)를 호스트의 일반 사용자 UID로 대응시킵니다. 컨테이너 안의 다른 UID는 `/etc/subuid`에 등록된 보조 UID 범위로 대응됩니다.

```text
 host /etc/subuid:  alice:100000:65536      (alice UID = 1000)

 container UID      host UID
 -------------      --------
 0 (root)     --->  1000      (alice herself)
 1            --->  100000
 2            --->  100001
 ...                ...
 65536        --->  165535
```

```bash
# 현재 사용자의 UID 대응 확인 (user namespace 안에서 실행)
podman unshare cat /proc/self/uid_map
#          0       1000          1
#          1     100000      65536
```

| 항목           | rootful(sudo podman)          | rootless(일반 사용자)               |
|----------------|-------------------------------|-------------------------------------|
| 저장소         | `/var/lib/containers/storage` | `~/.local/share/containers/storage` |
| 실행 상태      | `/run/containers`             | `$XDG_RUNTIME_DIR/containers`       |
| 1024 미만 포트 | 가능                          | 기본 불가(5절 참조)                 |
| 네트워크       | netavark 브리지               | 기본 pasta(사용자 공간 네트워크)    |
| 탈출 시 권한   | 호스트 root                   | 해당 일반 사용자 권한               |

rootless 이미지 저장소는 사용자마다 따로 있습니다. `sudo podman images`와 `podman images` 결과가 다른 것은 정상입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. rootless 설정

### 보조 UID/GID 범위

최근 배포판은 사용자를 만들 때 범위를 자동으로 넣지만, 기존 사용자나 LDAP 사용자는 직접 등록해야 할 수 있습니다. 파일을 직접 편집하기보다 `usermod`를 씁니다. 사용자끼리 범위가 겹치면 서로의 namespace에 접근할 수 있으므로 겹치지 않게 지정합니다.

```bash
grep alice /etc/subuid /etc/subgid

sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 alice

# 범위를 바꾼 뒤 해당 사용자로 실행 (실행 중 컨테이너 정지·pause 프로세스 재시작)
podman system migrate
```

`newuidmap`, `newgidmap` 명령이 필요하며 shadow-utils(Debian 계열은 uidmap) 패키지에 들어 있습니다.

### 낮은 번호 포트

일반 사용자는 기본적으로 1024 미만 포트에 바인딩할 수 없습니다. 방법은 두 가지입니다.

```bash
# 방법 1: 높은 포트로 열고 앞단(로드밸런서·방화벽 포트 전달)에서 80/443으로 연결
podman run -d -p 8080:80 docker.io/library/nginx:1.27

# 방법 2: 비특권 포트 시작 번호를 낮춤 (호스트 전체에 적용되므로 영향 검토 후)
echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee /etc/sysctl.d/90-unprivileged-port.conf
sudo sysctl --system
```

🟡 방법 2는 모든 일반 사용자 프로세스가 80번 이상 포트를 열 수 있게 합니다. 다중 사용자 서버에서는 방법 1을 먼저 검토합니다.

### 로그아웃 뒤에도 실행 유지

rootless 컨테이너는 사용자 세션이 끝나면 함께 종료됩니다. 서비스용 계정은 linger를 켜서 로그인 없이도 사용자 systemd가 실행되게 합니다.

```bash
sudo loginctl enable-linger alice
loginctl show-user alice --property=Linger
```

### 볼륨 권한

```bash
# SELinux 사용 시: :Z는 이 컨테이너 전용 라벨, :z는 여러 컨테이너 공유 라벨
podman run -d -v ./data:/data:Z docker.io/library/redis:7

# 컨테이너 안 non-root 사용자와 호스트 사용자를 같은 UID로 맞춤
podman run --rm --userns=keep-id -v ./src:/src:Z localhost/app:1.0 ls -ln /src

# 보조 UID 소유로 만들어진 파일을 호스트에서 정리
podman unshare chown -R 0:0 ./data
podman unshare rm -rf ./data/tmp
```

🟡 `/home`, `/usr` 같은 시스템 디렉터리에 `:Z`·`:z`를 쓰면 SELinux 라벨이 바뀌어 호스트 서비스가 동작하지 않을 수 있습니다. 컨테이너 전용 디렉터리에만 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Pod

Podman Pod는 Kubernetes Pod처럼 여러 컨테이너가 네트워크 namespace를 공유하는 묶음입니다. 같은 Pod 안의 컨테이너는 `localhost`로 서로 통신하고, 포트 공개는 Pod 단위로 합니다.

```bash
# Pod 생성 (포트는 Pod에 지정)
podman pod create --name wp -p 8080:80

# 같은 Pod에 DB와 앱 컨테이너 추가
podman run -d --pod wp --name wp-db \
  -e MARIADB_ROOT_PASSWORD='<PASSWORD>' -e MARIADB_DATABASE=wp \
  docker.io/library/mariadb:11
podman run -d --pod wp --name wp-app \
  -e WORDPRESS_DB_HOST=127.0.0.1 -e WORDPRESS_DB_PASSWORD='<PASSWORD>' \
  docker.io/library/wordpress:6

podman pod ps
podman pod stop wp && podman pod rm wp
```

### Kubernetes YAML과 오가기

```bash
# 실행 중 Pod를 Kubernetes YAML로 내보내기
podman kube generate wp > wp.yaml

# YAML로 Pod 실행 / 정리
podman kube play wp.yaml
podman kube down wp.yaml
```

내보낸 YAML은 Kubernetes 매니페스트의 출발점으로 쓸 수 있지만, 비밀번호가 환경변수 값으로 그대로 들어가므로 저장소에 올리기 전에 Secret 참조로 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Quadlet으로 서비스 운영

Quadlet은 `.container` 같은 선언 파일을 읽어 systemd 서비스로 바꿔 주는 systemd generator입니다. 예전 `podman generate systemd` 명령은 지원 중단(deprecated) 상태이며 긴급 버그 수정만 받으므로, 새 구성은 Quadlet으로 만듭니다.

| 파일 종류    | 만드는 것                         |
|--------------|-----------------------------------|
| `.container` | 컨테이너 하나                     |
| `.volume`    | 이름 있는 볼륨                    |
| `.network`   | Podman 네트워크                   |
| `.pod`       | Pod                               |
| `.kube`      | Kubernetes YAML로 정의한 컨테이너 |
| `.image`     | 이미지 받기·보관                  |
| `.build`     | Containerfile로 이미지 빌드       |

| 실행 방식 | 파일 위치(주요)                 | 재적용 명령                      |
|-----------|---------------------------------|----------------------------------|
| rootful   | `/etc/containers/systemd/`      | `sudo systemctl daemon-reload`   |
| rootless  | `~/.config/containers/systemd/` | `systemctl --user daemon-reload` |

### 예시: rootless 웹 서비스

```ini
# ~/.config/containers/systemd/web-data.volume
[Volume]
```

```ini
# ~/.config/containers/systemd/web.container
[Unit]
Description=Nginx web container
After=network-online.target

[Container]
Image=docker.io/library/nginx:1.27
PublishPort=8080:80
Volume=web-data.volume:/usr/share/nginx/html:Z
AutoUpdate=registry

[Service]
Restart=always
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user start web.service
systemctl --user status web.service
journalctl --user -u web.service -f

# 생성될 유닛 미리 보기 (문법 오류 확인)
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun
```

- `web.container`는 `web.service`가 되고 컨테이너 이름은 기본으로 `systemd-web`입니다.
- Quadlet이 만든 서비스는 생성된 유닛이라 `systemctl enable`이 동작하지 않습니다. 부팅 시 시작은 `[Install]`의 `WantedBy=`로 정합니다. rootless는 5절의 linger도 켜야 부팅 뒤 실행됩니다.
- `[Service]`의 `Restart=`, `TimeoutStartSec=` 같은 키는 systemd에 그대로 전달됩니다. 첫 실행 때 이미지 받기가 길어질 수 있어 `TimeoutStartSec`을 넉넉히 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 자동 업데이트

`podman auto-update`는 자동 업데이트 정책이 있는 컨테이너의 이미지를 확인하고, 바뀌었으면 해당 systemd 유닛을 재시작합니다. 컨테이너가 systemd 유닛 안에서 실행 중이어야 합니다.

| 정책       | 동작                                                                      |
|------------|---------------------------------------------------------------------------|
| `registry` | 원격 레지스트리의 digest와 비교해 새 이미지를 받음. 전체 이미지 이름 필요 |
| `local`    | 로컬 저장소의 이미지 digest와 비교(직접 빌드·pull한 이미지 반영)          |

```bash
# 받지 않고 확인만 (UPDATED 열이 pending이면 갱신 대상)
podman auto-update --dry-run

# 즉시 실행
podman auto-update

# 정기 실행 타이머 (기본: 매일 자정)
systemctl --user enable --now podman-auto-update.timer
systemctl --user list-timers podman-auto-update.timer
```

`--rollback`은 기본으로 켜져 있어 재시작한 유닛이 실패하면 이전 이미지로 되돌립니다. 다만 컨테이너가 준비 완료를 알리지 않으면 시작 직후 죽는 경우를 놓칠 수 있으므로, 앱이 sd_notify를 지원하면 `--sdnotify=container`(Quadlet은 `Notify=true`)를 함께 검토합니다.

🟡 `latest` 같은 움직이는 tag에 `registry` 정책을 쓰면 상위 이미지 변경이 검증 없이 운영에 들어갑니다. 운영 서비스는 고정 tag를 쓰고 갱신은 검토 후 반영하는 편이 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. Docker 호환

| 필요                      | 방법                                                                |
|---------------------------|---------------------------------------------------------------------|
| `docker` 명령 그대로 사용 | `podman-docker` 패키지(배포판 제공 시) 또는 `alias docker=podman`   |
| Docker API를 쓰는 도구    | `systemctl --user enable --now podman.socket` 후 `DOCKER_HOST` 지정 |
| Compose 파일 실행         | `podman compose`(설치된 docker-compose 또는 podman-compose를 호출)  |

```bash
systemctl --user enable --now podman.socket
export DOCKER_HOST="unix://$XDG_RUNTIME_DIR/podman/podman.sock"
docker-compose version    # 또는 Docker API를 쓰는 다른 도구
```

호환되지 않거나 다르게 동작하는 부분:

- Docker Swarm 기능은 없습니다.
- rootless에서는 컨테이너 IP로 호스트가 직접 접근하는 구성이 rootful Docker와 다르게 동작할 수 있습니다.
- Compose의 일부 고급 옵션은 구현(docker-compose, podman-compose)에 따라 지원 범위가 다르므로 실행 전 `config`로 해석 결과를 확인합니다.

Compose 문법 자체는 [Docker Compose 치트시트](./docker_compose_cheatsheet.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 문제 해결

| 증상                                                       | 원인과 조치                                                                  |
|------------------------------------------------------------|------------------------------------------------------------------------------|
| `there might not be enough IDs available in the namespace` | 보조 UID 범위 없음. `/etc/subuid` 확인 후 `podman system migrate`            |
| `newuidmap: not found`                                     | shadow-utils(uidmap) 패키지 설치                                             |
| 80번 포트에서 `permission denied`                          | 비특권 포트 제한. 5절 방법 1 또는 2                                          |
| 로그아웃하면 컨테이너 종료                                 | `loginctl enable-linger <user>`                                              |
| 볼륨에서 `Permission denied`                               | SELinux 라벨(`:Z`) 또는 UID 대응(`--userns=keep-id`, `podman unshare chown`) |
| 호스트에서 볼륨 파일 소유자가 숫자(100xxx)로 보임          | 보조 UID 소유 파일. `podman unshare`로 소유자 변경·삭제                      |
| 짧은 이름 이미지가 다른 레지스트리에서 받아짐              | 전체 이미지 이름 사용, `registries.conf` 확인                                |
| Quadlet 서비스가 생성되지 않음                             | 파일 위치·확장자 확인, generator `--dryrun` 출력의 오류 메시지 확인          |

```bash
podman info                         # 저장소·네트워크·cgroup·rootless 상태
podman system df                    # 이미지·컨테이너·볼륨 용량
podman events --since 30m           # 최근 이벤트
podman inspect <container> --format '{{.State.Status}} {{.State.ExitCode}}'
```

🟡 `podman system reset`은 해당 사용자의 모든 컨테이너·이미지·볼륨·네트워크를 지웁니다. 실행 전에 보존할 볼륨을 백업(`podman volume export`)합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Podman 공식 문서: [docs.podman.io](https://docs.podman.io/en/latest/) — ★★★☆☆ (확인일 2026-11-16)
- Quadlet(podman-systemd.unit): [docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) — ★★★☆☆ (확인일 2026-11-16)
- podman generate systemd (deprecated): [docs.podman.io/en/latest/markdown/podman-generate-systemd.1.html](https://docs.podman.io/en/latest/markdown/podman-generate-systemd.1.html) — ★★★☆☆ (확인일 2026-11-16)
- podman auto-update: [docs.podman.io/en/latest/markdown/podman-auto-update.1.html](https://docs.podman.io/en/latest/markdown/podman-auto-update.1.html) — ★★★☆☆ (확인일 2026-11-16)
- podman run: [docs.podman.io/en/latest/markdown/podman-run.1.html](https://docs.podman.io/en/latest/markdown/podman-run.1.html) — ★★★☆☆ (확인일 2026-11-16)
- Rootless tutorial: [github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md) — ★★★☆☆ (확인일 2026-11-16)
- Podman troubleshooting: [github.com/containers/podman/blob/main/troubleshooting.md](https://github.com/containers/podman/blob/main/troubleshooting.md) — ★★★☆☆ (확인일 2026-11-16)
- Podman releases: [github.com/containers/podman/releases](https://github.com/containers/podman/releases) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
