# Caddy
<!-- reference: _reference/caddy_official_notes.md -->

인증서 발급·갱신을 자동으로 하는 웹 서버이자 리버스 프록시입니다. 설정 파일(Caddyfile)이 짧아 작은 서비스나 내부 도구 앞단에 쓰기 좋습니다. 이 문서만으로 설치 → 정적 파일·리버스 프록시 설정 → 자동 HTTPS → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Caddy v2.11.9 (2026-11-23 확인)
- 예제 시험: 2026-11-23, `caddy:2`(v2.11.9) 컨테이너에서 3절 정적 파일·리버스 프록시 설정과 `validate`·`fmt`를 실행해 확인. 자동 HTTPS는 공개 도메인이 필요해 시험하지 않았음

## 목차

| 섹션                                                                               |
|------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. Caddyfile](#3-caddyfile)             |
| [4. 자동 HTTPS](#4-자동-https) / [5. 운영](#5-운영) / [6. 검증](#6-검증)           |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료) |

---

## 1. 개요

| 항목    | Caddy                               | Nginx                          |
|---------|-------------------------------------|--------------------------------|
| HTTPS   | 도메인을 쓰면 인증서 자동 발급·갱신 | certbot 등으로 따로 발급·갱신  |
| 설정    | Caddyfile 몇 줄                     | 블록·지시어가 많고 세밀함      |
| 맞는 곳 | 작은 서비스, 내부 도구, 빠른 HTTPS  | 대규모·세밀한 튜닝이 필요한 곳 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
# Ubuntu / Debian (공식 저장소)
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update && sudo apt-get install -y caddy

# 컨테이너
docker run -d --name caddy -p 80:80 -p 443:443 \
  -v $PWD/Caddyfile:/etc/caddy/Caddyfile:ro -v caddy_data:/data caddy:2

caddy version
```

패키지로 설치하면 `caddy` systemd 서비스와 `/etc/caddy/Caddyfile`이 만들어집니다. 컨테이너는 인증서가 저장되는 `/data`를 볼륨으로 유지해야 재시작 때 인증서를 다시 받지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Caddyfile

```text
# 정적 파일
:8080 {
	root * /srv
	file_server
}

# 리버스 프록시
:8081 {
	reverse_proxy 127.0.0.1:3000
}

# 도메인 + 자동 HTTPS + 압축 + 접근 로그
app.example.com {
	encode zstd gzip
	reverse_proxy 127.0.0.1:3000 127.0.0.1:3001 {
		lb_policy round_robin
		health_uri /healthz
	}
	log {
		output file /var/log/caddy/app.log
	}
}
```

| 지시어               | 하는 일                                |
|----------------------|----------------------------------------|
| `root`·`file_server` | 디렉터리의 정적 파일 제공              |
| `reverse_proxy`      | 뒤쪽 서버로 전달 (여러 대면 부하 분산) |
| `encode`             | 응답 압축                              |
| `log`                | 접근 로그                              |

Caddyfile은 들여쓰기에 탭을 씁니다. `caddy fmt --overwrite`로 형식을 맞춥니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 자동 HTTPS

사이트 주소에 도메인 이름(`app.example.com`)을 쓰면 Caddy가 인증서를 받고 갱신하며, HTTP 요청을 HTTPS로 넘깁니다. 조건은 다음과 같습니다.

- 그 도메인의 DNS가 이 서버를 가리켜야 합니다.
- 인증 과정에 쓰는 80·443 포트가 외부에서 이 서버에 닿아야 합니다.
- `:8080`처럼 포트만 쓰거나 `localhost`·사설 주소면 공개 인증서를 받지 않습니다(`localhost`는 Caddy 자체 인증서).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 운영

```bash
caddy validate --config /etc/caddy/Caddyfile      # 문법 검사
sudo systemctl reload caddy                       # 무중단 반영 (= caddy reload)
journalctl -u caddy -f                            # 로그
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용      | 명령                                           | 기대 결과                     |
|------|----------------|------------------------------------------------|-------------------------------|
| 1    | 판             | `caddy version`                                | `v2.x`                        |
| 2    | 설정 문법      | `caddy validate --config /etc/caddy/Caddyfile` | `Valid configuration`         |
| 3    | 정적 파일      | `curl http://127.0.0.1:8080/`                  | 파일 내용                     |
| 4    | 리버스 프록시  | `curl http://127.0.0.1:8081/`                  | 뒤쪽 서버 응답                |
| 5    | HTTPS (도메인) | `curl -sI https://app.example.com/`            | `HTTP/2 200`, 유효한 인증서   |
| 6    | HTTP 전환      | `curl -sI http://app.example.com/`             | `308` 또는 `301`로 HTTPS 안내 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                 | 원인                                | 해결 방법                                  |
|--------------------------------------|-------------------------------------|--------------------------------------------|
| 인증서 발급 실패                     | DNS가 다른 곳을 가리킴, 80·443 막힘 | DNS·방화벽 확인, `journalctl -u caddy`     |
| 컨테이너 재시작 때마다 인증서 재발급 | `/data` 볼륨 없음                   | `-v caddy_data:/data`                      |
| `Caddyfile input is not formatted`   | 형식이 표준과 다름 (경고)           | `caddy fmt --overwrite`                    |
| 502                                  | 뒤쪽 서버 중지, 주소 오타           | 뒤쪽 서버 상태와 `reverse_proxy` 주소 확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Nginx 설치](./nginx_install.md) — 세밀한 설정이 필요한 웹 서버
- [HAProxy 개념](./haproxy_concepts.md) — 부하 분산 전용
- [Docker Compose](../containers/docker_compose.md) — 컨테이너로 함께 운영
- [TLS 인증서 만료 감시](../../04_security/hardening/tls_certificate_expiry_monitoring.md) — 인증서 상태 감시

---

## 참고 자료

- Caddy: [Automatic HTTPS](https://caddyserver.com/docs/automatic-https) · [Caddyfile](https://caddyserver.com/docs/caddyfile) · [Command Line](https://caddyserver.com/docs/command-line) — ★★★☆☆
- Caddy: [Install](https://caddyserver.com/docs/install) — ★★★☆☆
- GitHub: [caddyserver/caddy releases](https://github.com/caddyserver/caddy/releases) — v2.11.9 확인 2026-11-23 — ★★★☆☆

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
