---
name: varnish-official-notes
description: Varnish Cache의 판, VCL 기본 구조, 캐시 적중 확인 방법의 공식 출처 기준 사실 정리.
tags:
  - cache
  - varnish
last_checked: 2026-11-23
sources:
  - https://varnish-cache.org/docs/
  - https://github.com/varnishcache/varnish-cache
  - https://hub.docker.com/_/varnish
---

# Varnish 공식 참조 노트

| 항목          | 값                                                                                       | 출처                   |
|---------------|------------------------------------------------------------------------------------------|------------------------|
| 판            | 8.0 계열. 공식 이미지 `varnish:8`의 `varnishd -V`는 8.0.2 (저장소 태그는 8.0.0까지 보임) | 컨테이너, 저장소 태그  |
| 설정 언어     | VCL (`vcl 4.1;`), `backend` 정의, `vcl_recv`·`vcl_backend_response` 등 단계별 서브루틴   | Varnish docs           |
| TTL           | `vcl_backend_response`에서 `beresp.ttl` 지정                                             | Varnish docs, 컨테이너 |
| 캐시 우회     | `vcl_recv`에서 `return (pass);`                                                          | Varnish docs, 컨테이너 |
| 적중 확인     | 응답 헤더 `X-Varnish`에 ID가 두 개면 캐시 적중, `varnishstat -1 -f MAIN.cache_hit`       | 컨테이너               |
| 컨테이너 설정 | `/etc/varnish/default.vcl`                                                               | Docker Hub             |

검증: 1차 varnish-cache.org 문서와 저장소, 2차 `varnish:8` 컨테이너에서 nginx 앞단 캐시를 띄워 두 번째 요청 적중(cache_hit 1)을 확인했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
