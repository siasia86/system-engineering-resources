# 오픈소스 도구 및 컨테이너

Docker, 컨테이너 기술, 워크플로우 자동화 도구에 대한 가이드입니다.

## 목차

| 섹션 |
|------|
| [문서 목록](#문서-목록) / [빠른 시작](#빠른-시작) |


---

## 문서 목록

### 컨테이너
- **[Docker & Docker Compose 치트시트](../12_tech_stack/docker_docker_compose_cheatsheet.md)** - 자주 사용하는 Docker 명령어
- **[컨테이너 아키텍처](container_architecture.md)** - 컨테이너 내부 구조 및 원리

### 자동화 도구
- **[n8n Docker 치트시트](n8n_docker_cheatsheet.md)** - n8n 워크플로우 자동화 도구
- **[Ansible vs Jenkins](ansible_vs_jenkins.md)** - 자동화 도구 비교

### 데이터베이스 백업
- **[Percona XtraBackup 가이드](percona_xtrabackup_guide.md)** - MySQL/MariaDB 물리적 백업

[⬆ 목차로 돌아가기](#목차)

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

| 특징      | 컨테이너 | 가상 머신 |
|-----------|----------|-----------|
| 시작 시간 | 초 단위  | 분 단위   |
| 리소스    | 가벼움   | 무거움    |
| 격리 수준 | 프로세스 | 완전 격리(Full Isolation) |
| 이식성    | 높음     | 중간      |

---

[문서 전체 로드맵](../README.md)

---

## 참고 자료

- Docker Documentation: [docs.docker.com](https://docs.docker.com/) — ★★★☆☆
- Ansible Documentation: [docs.ansible.com](https://docs.ansible.com/) — ★★★☆☆

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

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.
