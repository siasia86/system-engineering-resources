# 설치 가이드 (Install)

소프트웨어 설치 및 초기 설정 관련 문서 모음.

## 목차

| 분류             | 문서                                                            | 설명                                   |
|------------------|-----------------------------------------------------------------|----------------------------------------|
| **자동화**       | [Ansible](ansible_install_and_team_operation.md)                | Ubuntu/Rocky 설치, 팀 운영, 권한 제어  |
| **데이터베이스** | [MySQL 설치](mysql_install.md)                                  | Ubuntu/Rocky, 초기 설정, 보안          |
| **데이터베이스** | [PostgreSQL 설치](postgresql_install.md)                        | Ubuntu/Rocky, pg_hba.conf, 보안        |
| **데이터베이스** | [MongoDB](mongodb_install.md)                                   | 설치, 보안 설정, CRUD, 백업            |
| **컨테이너**     | [Docker + Compose](docker_install_and_compose.md)               | 설치, Compose 운영, 실무 팁            |
| **컨테이너**     | [Kubernetes](kubernetes_install.md)                             | k3s, kubeadm, kubectl 기본 사용법      |
| **웹 서버**      | [Nginx](nginx_install.md)                                       | 설치, 가상 호스트, 리버스 프록시, SSL  |
| **웹 서버**      | [Apache](apache_install.md)                                     | 설치, MPM(prefork/worker/event), SSL   |
| **웹 서버**      | [Nginx GeoIP2 모듈](01_script_markdown/nginx_geoip2_install.md) | GeoIP2 모듈 소스 빌드, 국가 차단       |
| **캐시**         | [Redis](redis_install.md)                                       | 설치, 보안 설정, 자료형, 실무 팁       |
| **모니터링**     | [Prometheus + Grafana](prometheus_grafana_install.md)           | 설치, Node Exporter, 알림, Compose     |
| **검색/로그**    | [Elasticsearch](elasticsearch_install.md)                       | 설치, ELK 스택, ILM, Compose           |
| **로드 밸런서**  | [HAProxy](haproxy_install.md)                                   | L4/L7 LB, SSL 터미네이션, 통계         |
| **시크릿 관리**  | [Vault](vault_install.md)                                       | 설치, KV/DB 엔진, AppRole, Auto Unseal |
| **CI/CD**        | [Jenkins](jenkins_install.md)                                   | 설치, Pipeline, Docker Compose         |
| **원격 접속**    | [Windows OpenSSH](windows_openssh_install.md)                   | Windows Server OpenSSH 설치, 설정      |

---

## 참고 자료

- [09_database/](../09_database/README.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-23

© 2026 siasia86. Licensed under CC BY 4.0.
