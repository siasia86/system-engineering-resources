# Docker & Docker Compose Cheat Sheet
<!-- reference: _reference/docker_official_notes.md -->

## 목차

| 섹션                                                                                                            |
|-----------------------------------------------------------------------------------------------------------------|
| [1. Docker 기본 명령어](#1-docker-기본-명령어) / [2. Docker Compose 기본 명령어](#2-docker-compose-기본-명령어) |
| [3. Compose 네트워크](#3-compose-네트워크) / [4. Compose 고급 설정](#4-compose-고급-설정)                       |

---

## 1. Docker 기본 명령어

### 컨테이너 실행

```bash
docker run -d -p 8080:80 --name web nginx        # 백그라운드 실행
docker run -it ubuntu:22.04 bash                 # 인터랙티브 실행
docker run --rm alpine echo hello                # 실행 후 자동 삭제
docker run -e ENV_VAR=value nginx                # 환경변수 전달
docker run -v /host/path:/container/path nginx   # 볼륨 마운트
docker run --network mynet nginx                 # 네트워크 지정
```

### 컨테이너 관리

```bash
docker ps                                        # 실행 중 컨테이너 목록
docker ps -a                                     # 모든 컨테이너 목록 (중단 포함)
docker stop <컨테이너>                           # 컨테이너 중지
docker start <컨테이너>                          # 컨테이너 시작
docker restart <컨테이너>                        # 컨테이너 재시작
docker rm <컨테이너>                             # 컨테이너 삭제
docker rm -f <컨테이너>                          # 강제 삭제 (실행 중도 가능)
docker logs <컨테이너>                           # 로그 확인
docker logs -f <컨테이너>                        # 실시간 로그
docker exec -it <컨테이너> bash                  # 컨테이너 내부 접속
docker cp <컨테이너>:/path /host/path            # 컨테이너 → 호스트 파일 복사
docker cp /host/path <컨테이너>:/path            # 호스트 → 컨테이너 파일 복사
docker inspect <컨테이너>                        # 상세 정보 (JSON)
docker stats                                     # 실시간 리소스 사용량
docker diff <컨테이너>                           # 파일 변경 내역
```

### 이미지 관리

```bash
docker images                                    # 로컬 이미지 목록
docker pull <이미지>:<태그>                      # 이미지 다운로드
docker build -t myapp:1.0 .                      # Dockerfile 빌드
docker push myrepo/myapp:1.0                     # 레지스트리 푸시
docker rmi <이미지>                              # 이미지 삭제
docker image prune                               # 미사용(dangling) 이미지 삭제
docker tag myapp:1.0 myrepo/myapp:1.0            # 이미지 태그 추가
docker save myapp:1.0 | gzip > myapp.tar.gz      # 이미지 파일로 저장
docker load < myapp.tar.gz                       # 이미지 파일에서 로드
```

### 볼륨/네트워크 관리

```bash
docker volume ls                                 # 볼륨 목록
docker volume create myvol                       # 볼륨 생성
docker volume rm <볼륨>                          # 볼륨 삭제
docker volume inspect <볼륨>                     # 볼륨 상세 정보
docker network ls                                # 네트워크 목록
docker network create mynet                      # 네트워크 생성
docker network inspect <네트워크>                # 네트워크 상세 정보
docker network connect mynet <컨테이너>          # 컨테이너를 네트워크에 연결
```

### 시스템 정리

```bash
docker stop $(docker ps -aq)                     # 모든 컨테이너 중지
docker rm $(docker ps -aq)                       # 모든 컨테이너 삭제
docker volume rm $(docker volume ls -q)          # 모든 볼륨 삭제
docker system prune -a -f                        # 미사용 이미지/컨테이너/네트워크 전체 정리
docker system df                                 # 디스크 사용량 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Docker Compose 기본 명령어

Compose 명령은 [Docker Compose](./docker_compose.md) 5절로 옮겼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Compose 네트워크

네트워크 드라이버 비교, compose.yml 네트워크 설정, 네트워크 명령, macvlan 주의사항은 [Docker 네트워크](./docker_network.md) 문서로 옮겼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Compose 고급 설정

### cgroup 설정

```yaml
services:
  ubuntu22:
    privileged: true
    cgroup: host          # with host /sys/fs/cgroup bind mount (image README)
    # cgroup: private     # dockerd default on cgroup v2, no host cgroup mount
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
```

| cgroup 모드 | dockerd 기본값   | 용도                                                   |
|-------------|------------------|--------------------------------------------------------|
| `host`      | cgroup v1 호스트 | systemd 이미지 + 호스트 `/sys/fs/cgroup` rw bind mount |
| `private`   | cgroup v2 호스트 | 일반 컨테이너 (컨테이너 자신의 cgroup만 보임)          |

🔵 geerlingguy systemd 이미지 README는 `--privileged --volume=/sys/fs/cgroup:/sys/fs/cgroup:rw --cgroupns=host` 조합을 안내합니다. 모드별 상세는 [docker.md 11절](./docker.md#11-cgroup-namespace)을 참고합니다.

리소스 제한, 의존성과 헬스체크, 환경 변수, 프로파일은 [Docker Compose](./docker_compose.md) 6~8절로 옮겼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Docker Documentation: [docs.docker.com](https://docs.docker.com/) — ★★★☆☆
- Docker Compose Reference: [docs.docker.com/compose](https://docs.docker.com/compose/) — ★★★☆☆
- docker volume prune: [docs.docker.com/reference/cli/docker/volume/prune](https://docs.docker.com/reference/cli/docker/volume/prune/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-25

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
