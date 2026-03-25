# 오픈소스 도구 및 컨테이너

Docker, 컨테이너 기술, 워크플로우 자동화 도구에 대한 가이드입니다.

## 문서 목록

### 컨테이너
- **[Docker & Docker Compose 치트시트](01_docker_docker_compose_cheatsheet.md)** - 자주 사용하는 Docker 명령어
- **[컨테이너 아키텍처](03_container_architecture.md)** - 컨테이너 내부 구조 및 원리

### 자동화 도구
- **[n8n Docker 치트시트](02_n8n_docker_cheatsheet.md)** - n8n 워크플로우 자동화 도구

---

## 빠른 시작

### Docker 기본 명령어

```bash
# 이미지 관리
docker pull nginx
docker images
docker rmi image_id

# 컨테이너 실행
docker run -d -p 80:80 nginx
docker ps
docker stop container_id

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
```

### 컨테이너 vs VM

| 특징 | 컨테이너 | 가상 머신 |
|------|---------|----------|
| 시작 시간 | 초 단위 | 분 단위 |
| 리소스 | 가벼움 | 무거움 |
| 격리 수준 | 프로세스 | 완전 격리 |
| 이식성 | 높음 | 중간 |

---

## 관련 문서

- [시스템 엔지니어링](../04_system_engineer/) - 로드맵
- [네트워크](../05_computer_science/) - 네트워크 기초

---

© 2026. Licensed under CC BY 4.0.
