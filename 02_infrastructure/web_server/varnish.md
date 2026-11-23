# Varnish (HTTP 캐시 서버)
<!-- reference: _reference/varnish_official_notes.md -->

웹 서버 앞에서 응답을 메모리에 저장해 같은 요청에 바로 답하는 HTTP 캐시 서버입니다. 뒤쪽 서버의 부하를 줄이고 응답 시간을 낮출 때 씁니다. 이 문서만으로 설치 → VCL 설정 → 캐시 적중 확인 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Varnish 8.0 (공식 이미지의 `varnishd -V` 8.0.2, 2026-11-23 확인)
- 예제 시험: 2026-11-23, `varnish:8` 컨테이너를 nginx 앞에 두고 3절 VCL과 5절 1~4번을 실행해 확인

## 목차

| 섹션                                                                     |
|--------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. VCL 기본](#3-vcl-기본)     |
| [4. 운영](#4-운영) / [5. 검증](#5-검증) / [6. 트러블슈팅](#6-트러블슈팅) |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                        |

---

## 1. 개요

```text
client ──> Varnish (:80, cache) ──> backend web server (:8080)
```

| 항목      | 내용                                                                                |
|-----------|-------------------------------------------------------------------------------------|
| 저장 위치 | 메모리 (재시작하면 캐시가 비워짐)                                                   |
| 설정      | VCL(Varnish Configuration Language)로 요청·응답 단계마다 규칙 작성                  |
| TLS       | Varnish 자체는 HTTPS를 처리하지 않으므로 앞에 TLS 종료(Nginx·HAProxy·Hitch 등)를 둠 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
sudo apt-get install -y varnish       # Ubuntu / Debian (배포판 판)
sudo dnf install -y varnish           # RHEL 계열
varnishd -V

# 컨테이너
docker run -d --name varnish -p 80:80 -v $PWD/default.vcl:/etc/varnish/default.vcl:ro varnish:8
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. VCL 기본

`/etc/varnish/default.vcl`

```text
vcl 4.1;

backend default {
  .host = "127.0.0.1";
  .port = "8080";
}

sub vcl_recv {
  if (req.url ~ "^/admin") { return (pass); }   # 관리 화면은 캐시하지 않음
}

sub vcl_backend_response {
  set beresp.ttl = 60s;                         # 60초 동안 캐시
}
```

| 서브루틴               | 시점                                  |
|------------------------|---------------------------------------|
| `vcl_recv`             | 요청을 받았을 때 (캐시 우회·정규화)   |
| `vcl_backend_response` | 뒤쪽 서버 응답을 받았을 때 (TTL 지정) |
| `vcl_deliver`          | 클라이언트에 보내기 전 (헤더 정리)    |

쿠키나 `Authorization` 헤더가 있는 요청은 기본 규칙상 캐시하지 않습니다. 로그인 사용자별 화면이 다른 사람에게 보이지 않도록, 캐시 대상은 공용 콘텐츠로 좁힙니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 운영

```bash
varnishstat -1 -f MAIN.cache_hit -f MAIN.cache_miss   # 적중·실패 횟수
varnishlog -g request -q 'ReqURL ~ "^/api"'           # 요청 단위 로그
varnishadm ban 'req.url ~ ^/news'                     # 해당 URL 캐시 무효화
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 검증

| 순서 | 확인 내용    | 명령                                                   | 기대 결과            |
|------|--------------|--------------------------------------------------------|----------------------|
| 1    | 판           | `varnishd -V`                                          | `varnish-8.0.x`      |
| 2    | 첫 요청      | `curl -sI http://127.0.0.1/ \| grep -i x-varnish`      | ID 하나 (캐시 실패)  |
| 3    | 두 번째 요청 | 같은 명령 한 번 더                                     | ID 두 개 (캐시 적중) |
| 4    | 통계         | `varnishstat -1 -f MAIN.cache_hit`                     | 1 이상               |
| 5    | 우회 경로    | `curl -sI http://127.0.0.1/admin \| grep -i x-varnish` | 계속 ID 하나         |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 트러블슈팅

| 증상                     | 원인                             | 해결 방법                                  |
|--------------------------|----------------------------------|--------------------------------------------|
| 적중이 전혀 없음         | 응답에 `Set-Cookie`, 요청에 쿠키 | 공용 경로의 쿠키 제거 규칙, 뒤쪽 헤더 확인 |
| 503 Backend fetch failed | 뒤쪽 서버 주소·포트 오류, 중지   | `backend` 설정과 뒤쪽 서버 상태 확인       |
| 바뀐 내용이 안 보임      | TTL 동안 캐시된 응답             | `varnishadm ban`으로 무효화, TTL 조정      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Nginx 설치](./nginx_install.md) — 뒤쪽 웹 서버와 TLS 종료
- [HAProxy 개념](./haproxy_concepts.md) — 앞단 부하 분산
- [캐시·CDN 시험](../../01_fundamentals/cs/web_testing/cache_cdn_testing.md) — 캐시 동작 시험 방법

---

## 참고 자료

- Varnish: [Varnish Cache documentation](https://varnish-cache.org/docs/) — ★★★☆☆
- Docker Hub: [varnish official image](https://hub.docker.com/_/varnish) — ★★★☆☆

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
