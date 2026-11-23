---
name: caddy-official-notes
description: Caddy 웹 서버의 판, Caddyfile 기본 지시어, 자동 HTTPS, 검증 명령의 공식 출처 기준 사실 정리.
tags:
  - caddy
  - web-server
  - tls
last_checked: 2026-11-23
sources:
  - https://github.com/caddyserver/caddy/releases
  - https://caddyserver.com/docs/automatic-https
  - https://caddyserver.com/docs/caddyfile
  - https://caddyserver.com/docs/command-line
  - https://hub.docker.com/_/caddy
---

# Caddy 공식 참조 노트

## 1. 공식 소스

| 소스               | URL                                           | 용도                  |
|--------------------|-----------------------------------------------|-----------------------|
| Caddy releases     | https://github.com/caddyserver/caddy/releases | 판                    |
| Automatic HTTPS    | https://caddyserver.com/docs/automatic-https  | 인증서 자동 발급·갱신 |
| Caddyfile          | https://caddyserver.com/docs/caddyfile        | 설정 문법             |
| Command line       | https://caddyserver.com/docs/command-line     | validate, fmt, reload |
| Docker 공식 이미지 | https://hub.docker.com/_/caddy                | 컨테이너 이미지       |

## 2. 검증된 사실 (2026-11-23)

| 항목               | 값                                                                                   | 출처                   |
|--------------------|--------------------------------------------------------------------------------------|------------------------|
| 최신 판            | v2.11.9 (2026-11-05)                                                                 | releases               |
| 자동 HTTPS         | 사이트 주소에 도메인 이름을 쓰면 인증서를 자동으로 받고 갱신하며 HTTP를 HTTPS로 넘김 | automatic-https        |
| 기본 지시어        | `root`·`file_server`(정적 파일), `reverse_proxy`(프록시), `encode`, `log`            | Caddyfile              |
| 검증·정리          | `caddy validate --config <파일>`, `caddy fmt`                                        | command-line, 컨테이너 |
| 설정 반영          | `caddy reload --config <파일>` (무중단)                                              | command-line           |
| 컨테이너 설정 위치 | `/etc/caddy/Caddyfile`, 정적 파일 예시 `/srv`                                        | Docker Hub, 컨테이너   |

## 3. 검증 기록

- 1차: GitHub release와 caddyserver.com 문서에서 확인했습니다.
- 2차: `caddy:2`(v2.11.9) 컨테이너에서 `file_server`·`reverse_proxy` 설정을 띄워 응답을 확인하고 `caddy validate`·`caddy fmt`를 실행했습니다. 자동 HTTPS는 공개 도메인이 필요해 시험하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
