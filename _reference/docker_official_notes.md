---
name: docker-official-notes
description: Docker 공식 문서 기반 권장사항, deprecated, breaking changes 정리. 문서 작성/검토 시 참조.
tags:
  - docker
  - reference
last_checked: 2026-05-22
sources:
  - https://docs.docker.com/engine/install/
  - https://docs.docker.com/reference/cli/dockerd/
  - https://docs.docker.com/build/building/best-practices/
  - https://docs.docker.com/engine/network/drivers/macvlan/
  - https://docs.docker.com/reference/compose-file/
---

# Docker 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-22)

| 컴포넌트       | 최신 버전 | 비고           |
|----------------|-----------|----------------|
| Docker Engine  | 29.5.2    | moby/moby      |
| Docker Compose | v5.1.4    | docker/compose |

## 2. 설치

### Ubuntu — 저장소 추가 (공식 권장: DEB822 형식)

```bash
# 구형 방식 (sources.list) — 비권장
echo "deb [...] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list

# 신형 방식 (DEB822) — 공식 권장 (Ubuntu 22.04+)
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF2
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF2
```

### RHEL 계열

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
# Rocky Linux도 동일 URL 사용 가능
```

## 3. daemon.json 권장 설정

```json
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "live-restore": true,
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Hard": 65536, "Soft": 65536 }
  }
}
```

| 옵션             | 기본값      | 권장값  | 이유                                                                                             |
|------------------|-------------|---------|--------------------------------------------------------------------------------------------------|
| `log-driver`     | `json-file` | `local` | 자동 로테이션, 효율적 포맷. json-file은 로테이션 없음                                            |
| `live-restore`   | `false`     | `true`  | 데몬 재시작 시 컨테이너 유지                                                                     |
| `userland-proxy` | `true`      | `false` | 루프백 트래픽을 커널 직접 처리. 일부 환경에서 미지원 주의 (공식 daemon.json 예시에서 false 사용) |

🟡 `json-file`은 기본값이지만 로테이션이 없어 디스크 고갈 위험. 공식 문서에서 `local` 권장.

## 4. Compose 파일

### 파일명 우선순위

1. `compose.yaml` — **공식 권장**
2. `compose.yml`
3. `docker-compose.yaml` (하위 호환)
4. `docker-compose.yml` (하위 호환)

### override 파일 자동 병합

```yaml
compose.yaml          # 기본 설정
compose.override.yaml # 자동 병합 (개발 환경 오버라이드)
```

### depends_on condition 값

| 값                               | 의미                   |
|----------------------------------|------------------------|
| `service_started`                | 컨테이너 시작됨 (기본) |
| `service_healthy`                | healthcheck 통과       |
| `service_completed_successfully` | 종료 코드 0으로 완료   |

### deploy.resources

Compose standalone에서도 동작 (Swarm 전용 아님).

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 128M
```

## 5. 네트워크

### macvlan 제약사항 (공식 문서)

- Linux 호스트 전용 (macOS/Windows 미지원)
- 대부분의 클라우드 프로바이더에서 차단 (물리 접근 필요)
- rootless 모드 미지원
- 네트워크 장비에서 **promiscuous mode** 허용 필요
- **호스트 → 컨테이너 직접 통신 불가** (macvlan 특성)
  - 우회: 호스트에 macvlan 인터페이스 추가 또는 bridge 네트워크 병행

### macvlan 옵션

| 옵션           | 기본값   | 설명                                       |
|----------------|----------|--------------------------------------------|
| `macvlan_mode` | `bridge` | `bridge` / `vepa` / `passthru` / `private` |
| `parent`       | 없음     | 부모 인터페이스 (필수)                     |

### cgroup (compose)

| 값        | 설명                                          |
|-----------|-----------------------------------------------|
| `host`    | 컨테이너 런타임 cgroup 네임스페이스 사용      |
| `private` | 컨테이너 전용 독립 cgroup 네임스페이스 (보안) |

## 6. Dockerfile 권장사항

- `FROM` — 특정 버전 고정 (`alpine:3.21`, `latest` 금지)
- `RUN` — `apt-get update && apt-get install -y --no-install-recommends` 체이닝
- `COPY` vs `ADD` — 단순 복사는 `COPY` 사용 (`ADD`는 URL/tar 압축 해제 시만)
- Multi-stage build — 최종 이미지 크기 최소화
- `USER` — root 실행 금지, non-root 사용자 지정
- `HEALTHCHECK` — 컨테이너 상태 모니터링

## 7. 보안

- 내부 서비스 포트 바인딩: `127.0.0.1:PORT:PORT` (외부 노출 방지)
- SELinux (RHEL): 볼륨 마운트 시 `:z` (공유) 또는 `:Z` (전용) 레이블
- Docker 그룹 멤버십 = root 권한과 동일 — 신중하게 부여
- `docker.sock` 마운트 = 호스트 전체 접근 권한

## 8. 알려진 주의사항

- `ufw` / `firewalld` 규칙을 Docker iptables가 우회할 수 있음
- `docker compose down -v` — 볼륨까지 삭제 (데이터 손실 주의)
- `image: latest` — 예기치 않은 업데이트로 장애 유발 가능, 버전 고정 권장
- `nft` (nftables) 방화벽 규칙은 Docker와 호환되지 않음 (iptables 사용)
