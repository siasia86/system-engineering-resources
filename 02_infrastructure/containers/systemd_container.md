# systemd 포함 컨테이너

컨테이너 안에서 systemd를 PID 1로 실행해, 실제 서버처럼 `systemctl`로 서비스를 등록·시작할 수 있게 하는 방법입니다. Ansible playbook이나 서비스 설치 스크립트를 가상 머신 대신 가벼운 컨테이너에서 시험할 때 씁니다. 이 문서만으로 이미지 만들기 → 실행 → 서비스 확인 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 환경: Docker Engine 29.x, cgroup v2 호스트, Ubuntu 24.04 이미지(systemd 255)
- 예제 시험: 2026-11-23, Docker Engine 29.8.1(cgroup v2, cgroup driver systemd)에서 3절 이미지를 빌드하고 4절 구성 네 가지를 실행해 결과를 비교. 5절 Compose와 7절 Ansible 접속은 이 PC의 inotify 한도에 걸려(10절) 기동 확인을 끝내지 못했음

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 준비](#2-준비) / [3. 이미지 만들기](#3-이미지-만들기)                                     |
| [4. 실행 구성](#4-실행-구성) / [5. Compose로 여러 대](#5-compose로-여러-대) / [6. 서비스 다루기](#6-서비스-다루기) |
| [7. Ansible로 접속](#7-ansible로-접속) / [8. 보안 주의](#8-보안-주의) / [9. 검증](#9-검증)                         |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                               |

---

## 1. 개요

일반 컨테이너는 애플리케이션 프로세스 하나만 실행하므로 `systemctl`이 동작하지 않습니다(`System has not been booted with systemd`). systemd 포함 컨테이너는 이 제약을 풀어 서버처럼 쓰게 합니다.

| 방식                   | 장점                                   | 단점                                              |
|------------------------|----------------------------------------|---------------------------------------------------|
| systemd 포함 컨테이너  | 수 초 안에 기동, 여러 대를 가볍게      | 권한(`--privileged`)이 필요, 커널은 호스트와 공유 |
| 가상 머신 (Vagrant 등) | 커널까지 실제 서버와 같음, 격리 강함   | 기동이 느리고 자원을 많이 씀                      |
| Podman                 | systemd 실행을 기본 지원 (`--systemd`) | Docker와 명령·Compose 지원이 조금 다름            |

커널 모듈, 방화벽(nftables), 부팅 과정처럼 커널·하드웨어에 닿는 동작은 컨테이너에서 실제 서버와 다르게 보일 수 있으므로 가상 머신으로 시험합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 준비

| 확인 항목          | 명령                                                          | 기대 값                        |
|--------------------|---------------------------------------------------------------|--------------------------------|
| cgroup 판          | `stat -fc %T /sys/fs/cgroup`                                  | `cgroup2fs` (v2)               |
| Docker cgroup 정보 | `docker info --format '{{.CgroupVersion}} {{.CgroupDriver}}'` | `2 systemd`                    |
| inotify 한도       | `sysctl fs.inotify.max_user_instances`                        | 컨테이너 수에 맞게 여유 (10절) |

이 문서는 cgroup v2 호스트(Ubuntu 22.04 이후, RHEL 9 이후 기본)를 기준으로 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 이미지 만들기

`Dockerfile`

```dockerfile
FROM ubuntu:24.04
ENV container=docker
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus python3 sudo \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/*.wants/* /lib/systemd/system/multi-user.target.wants/getty* \
 && systemctl mask systemd-logind.service getty.target console-getty.service
STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
```

| 줄                         | 이유                                                  |
|----------------------------|-------------------------------------------------------|
| `ENV container=docker`     | systemd가 컨테이너 안임을 알고 불필요한 단위를 건너뜀 |
| `python3`                  | Ansible로 접속해 모듈을 실행하려면 대상에 Python 필요 |
| `rm ... *.wants/*`, `mask` | 콘솔 로그인 등 컨테이너에 필요 없는 단위를 끔         |
| `STOPSIGNAL SIGRTMIN+3`    | `docker stop` 때 systemd가 정상 종료 절차를 밟게 함   |
| `CMD ["/sbin/init"]`       | systemd를 PID 1로 실행                                |

```bash
docker build -t local/ubuntu-systemd:24.04 .
```

직접 만들지 않고 Ansible 시험용으로 널리 쓰는 공개 이미지(예: `geerlingguy/docker-ubuntu2404-ansible`)를 쓸 수도 있습니다. 공개 이미지는 태그·다이제스트를 고정하고 Dockerfile을 확인한 뒤 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 실행 구성

systemd는 자기 cgroup 아래에 서비스별 하위 cgroup을 만들어야 하므로 컨테이너 안에서 `/sys/fs/cgroup`에 쓸 수 있어야 합니다. Docker는 권한을 주지 않은 컨테이너에 cgroup을 읽기 전용으로 붙이므로 `--privileged`가 필요합니다.

### 4-1. 시험한 구성 비교

| 구성 | 옵션                                                               | 결과                                | 컨테이너에서 보이는 cgroup                   |
|------|--------------------------------------------------------------------|-------------------------------------|----------------------------------------------|
| A    | `--privileged --cgroupns=private`                                  | 기동, `running`                     | 자기 cgroup만 (`0::/init.scope`)             |
| B    | `--privileged --cgroupns=host -v /sys/fs/cgroup:/sys/fs/cgroup:rw` | 기동, `running`                     | 호스트 전체 트리 (호스트 서비스 이름이 보임) |
| C    | `--cgroupns=private --tmpfs /run --tmpfs /run/lock`                | 즉시 종료 (`Read-only file system`) | -                                            |
| D    | C + `--cap-add SYS_ADMIN`, AppArmor·seccomp 해제                   | 즉시 종료                           | -                                            |

- 권장은 A입니다. B는 공개 이미지 README에 자주 나오는 구성인데, 컨테이너가 호스트의 cgroup 트리 전체를 보므로 격리가 약합니다.
- A·B 모두 컨테이너마다 `system.slice/docker-<ID>.scope` 아래에 따로 자리를 잡으므로 여러 대를 동시에 띄워도 서로 충돌하지 않습니다.

### 4-2. 실행

```bash
docker run -d --name node1 --hostname node1 \
  --privileged --cgroupns=private \
  local/ubuntu-systemd:24.04

docker exec node1 systemctl is-system-running    # running (부팅 중이면 starting)
docker exec node1 ps -o comm= -p 1               # systemd
docker exec -it node1 bash                        # 셸 접속

docker stop node1                                 # STOPSIGNAL 덕분에 즉시 종료
```

`is-system-running`이 `degraded`이면 실패한 단위가 있다는 뜻입니다. `docker exec node1 systemctl --failed`로 확인하고, 컨테이너에 필요 없는 단위면 이미지에서 `mask`합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Compose로 여러 대

```yaml
# compose.yaml
services:
  node1:
    image: local/ubuntu-systemd:24.04
    hostname: node1
    privileged: true
    cgroup: private              # --cgroupns=private
  node2:
    image: local/ubuntu-systemd:24.04
    hostname: node2
    privileged: true
    cgroup: private
```

```bash
docker compose up -d
docker compose exec node1 systemctl is-system-running
docker compose down
```

Compose의 `cgroup` 키는 `host`·`private`를 받으며 `docker run --cgroupns`와 같습니다. 2026-11-23 시험에서 `docker compose config`로 두 컨테이너에 `privileged: true`, `cgroup: private`가 적용된 것까지 확인했고, 기동은 이 PC의 inotify 한도(10절)에 걸려 확인하지 못했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 서비스 다루기

컨테이너 안에서는 실제 서버와 같은 방법으로 unit 파일을 만들고 `systemctl`로 다룹니다.

```bash
docker exec node1 sh -c 'cat > /etc/systemd/system/demo.service <<EOF
[Unit]
Description=demo
[Service]
ExecStart=/bin/sleep infinity
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now demo'

docker exec node1 systemctl is-active demo     # active
docker exec node1 journalctl -u demo --no-pager | tail -5
```

시험에서 4-1의 구성 A·B 모두 `active`였습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Ansible로 접속

SSH 서버를 넣지 않고 `community.docker.docker` 연결 플러그인으로 `docker exec`를 통해 접속할 수 있습니다. 이 플러그인은 `ansible` 묶음 패키지에 들어 있고, `ansible-core`만 설치했다면 `ansible-galaxy collection install community.docker`로 더합니다.

```ini
# inventory.ini
[nodes]
node1
node2

[nodes:vars]
ansible_connection=community.docker.docker
ansible_python_interpreter=/usr/bin/python3
```

```bash
ansible -i inventory.ini nodes -m ansible.builtin.ping
ansible -i inventory.ini nodes -m ansible.builtin.systemd -a "name=dbus"
```

인벤토리의 호스트 이름은 컨테이너 이름입니다(Compose는 `<프로젝트>-<서비스>-1`). 2026-11-23 시험에서는 플러그인이 설치된 것까지 확인했고, 접속은 5절과 같은 이유로 확인하지 못했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 보안 주의

- `--privileged`는 장치 접근 제한, capability 제한, AppArmor·seccomp를 모두 풉니다. 컨테이너 안의 root가 호스트를 바꿀 수 있는 수준이므로 시험 전용 호스트나 가상 머신에서만 씁니다.
- 외부에서 받은 playbook·스크립트를 privileged 컨테이너에서 실행하는 것은 호스트에서 실행하는 것과 비슷하게 봅니다.
- 공개 이미지는 태그만으로는 내용이 바뀔 수 있으므로 다이제스트(`@sha256:...`)로 고정합니다.
- 운영 서비스는 systemd 포함 컨테이너로 돌리지 않고, 프로세스 하나짜리 일반 컨테이너나 실제 서버로 운영합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용        | 명령                                                     | 기대 결과                        |
|------|------------------|----------------------------------------------------------|----------------------------------|
| 1    | 호스트 조건      | `stat -fc %T /sys/fs/cgroup`                             | `cgroup2fs`                      |
| 2    | 컨테이너 유지    | `docker ps --filter name=node1`                          | `Up` (바로 종료되지 않음)        |
| 3    | PID 1            | `docker exec node1 ps -o comm= -p 1`                     | `systemd`                        |
| 4    | 부팅 상태        | `docker exec node1 systemctl is-system-running`          | `running`                        |
| 5    | 실패 단위        | `docker exec node1 systemctl --failed --no-legend`       | 출력 없음                        |
| 6    | cgroup 격리      | `docker exec node1 cat /proc/self/cgroup`                | `0::/init.scope` (구성 A)        |
| 7    | 서비스 등록·실행 | 6절 명령 후 `systemctl is-active demo`                   | `active`                         |
| 8    | 정상 종료        | `time docker stop node1`                                 | 몇 초 안에 종료 (10초 대기 없음) |
| 9    | Ansible 접속     | `ansible -i inventory.ini nodes -m ansible.builtin.ping` | `SUCCESS`                        |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                                                           | 원인                                        | 해결 방법                                                          |
|--------------------------------------------------------------------------------|---------------------------------------------|--------------------------------------------------------------------|
| 바로 종료, `Failed to create /init.scope control group: Read-only file system` | `--privileged` 없음 (cgroup 읽기 전용)      | 4-1 구성 A로 실행                                                  |
| 바로 종료, `Failed to allocate manager object: Too many open files`            | 호스트 inotify 인스턴스 한도 초과           | `fs.inotify.max_user_instances`를 올림 (아래)                      |
| `System has not been booted with systemd`                                      | PID 1이 systemd가 아님                      | `CMD ["/sbin/init"]` 확인, `docker run` 끝에 다른 명령을 주지 않음 |
| 컨테이너 안에서 호스트 서비스 이름이 보임                                      | 4-1 구성 B (`--cgroupns=host` + bind mount) | 구성 A로 바꿈                                                      |
| `docker stop`이 10초 기다린 뒤 끝남                                            | systemd가 SIGTERM을 종료 신호로 받지 않음   | `STOPSIGNAL SIGRTMIN+3`                                            |
| `is-system-running`이 `degraded`                                               | 컨테이너에 맞지 않는 단위 실패              | `systemctl --failed` 확인 후 이미지에서 `mask`                     |
| `docker logs`에 아무것도 없음                                                  | systemd가 터미널이 없으면 콘솔 출력을 줄임  | 원인 확인 때만 `docker run --rm -t ...`로 출력 보기                |

inotify 한도는 systemd 인스턴스마다 여러 개씩 쓰므로, systemd 컨테이너를 여러 대 띄우면 기본값(배포판에 따라 128)을 넘기 쉽습니다. 2026-11-23 시험 PC에서는 사용 중 인스턴스가 이미 한도를 넘어 새 컨테이너가 위 오류로 멈췄습니다. 호스트 설정이므로 영향 범위를 확인한 뒤 바꿉니다.

```bash
sysctl fs.inotify.max_user_instances fs.inotify.max_user_watches      # 현재 값
sudo sysctl -w fs.inotify.max_user_instances=512                      # 재부팅 전까지
echo 'fs.inotify.max_user_instances = 512' | sudo tee /etc/sysctl.d/99-inotify.conf   # 계속 적용
```

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Docker 가이드](./docker.md) — cgroup 판과 cgroup namespace 모드 개념
- [Docker Compose](./docker_compose.md) — compose.yaml 작성
- [Podman](./podman.md) — `--systemd` 옵션과 Quadlet
- [Linux namespace 개념](../../01_fundamentals/linux/namespace_concepts.md) — cgroup namespace
- [Ansible 기초 가이드](../iac/ansible_basic_guide.md) — 인벤토리와 playbook
- [Molecule](../iac/molecule.md) — 컨테이너를 대상으로 한 role 시험
- [Vagrant](../iac/vagrant.md) — 커널까지 필요한 시험은 가상 머신으로

---

## 참고 자료

- Docker Documentation: [docker container run — cgroupns, privileged](https://docs.docker.com/reference/cli/docker/container/run/) — ★★★☆☆
- Docker Documentation: [Compose file reference — cgroup](https://docs.docker.com/reference/compose-file/services/#cgroup) — ★★★☆☆
- systemd: [Container Interface](https://systemd.io/CONTAINER_INTERFACE/) — ★★★☆☆
- Ansible Documentation: [community.docker.docker connection](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_connection.html) — ★★★☆☆
- GitHub: [geerlingguy/docker-ubuntu2404-ansible](https://github.com/geerlingguy/docker-ubuntu2404-ansible) — 구성 B 실행 예 — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
