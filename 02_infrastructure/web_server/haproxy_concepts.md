# HAProxy 핵심 개념
<!-- reference: _reference/web_server_official_notes.md -->

## 목차

| 섹션                                                                              |
|-----------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 동작 구조](#2-동작-구조) / [3. 설정 구조](#3-설정-구조)  |
| [4. 요청 처리와 규칙](#4-요청-처리와-규칙) / [5. 분산 알고리즘](#5-분산-알고리즘) |
| [6. 세션 유지](#6-세션-유지) / [7. 헬스체크와 서버 상태](#7-헬스체크와-서버-상태) |
| [8. 연결과 timeout](#8-연결과-timeout) / [9. 무중단 reload](#9-무중단-reload)     |
| [10. 버전 정책](#10-버전-정책)                                                    |

---

## 1. 개요

HAProxy는 TCP·HTTP 트래픽을 받아 여러 서버로 나누어 보내는 프록시입니다. 클라이언트 연결을 HAProxy가 직접 끝내고 서버로 새 연결을 맺기 때문에, 두 연결 사이에서 요청을 검사·수정·차단·분기할 수 있습니다.

이 문서는 HAProxy 3.4 공식 문서를 기준으로 설정을 읽고 고칠 때 필요한 개념을 정리합니다. 설치는 [HAProxy 설치 가이드](./haproxy_install.md), 운영 절차는 [HAProxy 운영 가이드](./haproxy_operations_guide.md)에서 다룹니다.

### 하는 일과 하지 않는 일

| 구분         | 내용                                                                                    |
|--------------|-----------------------------------------------------------------------------------------|
| 하는 일      | TCP 프록시, HTTP reverse proxy, TLS 종료·재암호화, 헤더 수정, 내용 기반 분기, 부하 분산 |
| 하는 일      | 요청 속도 제한, 남용 차단, 응답 압축, 메모리 캐시, FastCGI 연결                         |
| 하지 않는 일 | 브라우저용 forward proxy(Squid 영역), 요청·응답 본문 변경, 정적 파일 제공               |
| 하지 않는 일 | 패킷 단위 분산(NAT·DSR 없음, UDP 데이터그램 분산 없음, LVS/IPVS 영역)                   |

🔵 HAProxy는 시작한 뒤 chroot 안에서 권한을 낮추고 파일 시스템에 접근하지 않습니다. 그래서 정적 파일은 Nginx·Apache 같은 웹 서버가 맡고 HAProxy는 그 앞에 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 동작 구조

### 이벤트 기반 엔진

HAProxy는 하나의 프로세스 안에서 event-driven, non-blocking 방식으로 동작합니다. 연결마다 프로세스나 스레드를 만들지 않고, 준비된 I/O 이벤트만 골라 처리합니다. 스레드는 CPU 코어마다 하나씩 두며, 기본 스레드 수는 사용 가능한 CPU 수입니다(`haproxy -vv`에 표시).

공식 문서가 밝히는 운영상 특징은 다음과 같습니다.

- 처리 시간의 대부분은 커널에서 쓰입니다. TCP·HTTP close 모드에서 HAProxy 15% 대 커널 85%, keep-alive 모드에서 30% 대 70% 정도입니다.
- 99% 이상의 사용자에게 CPU 1코어면 충분합니다. 여러 스레드는 TLS 처리나 40Gbps 이상 전송에서 쓸모가 있습니다.
- 서버가 swap을 쓰거나 CPU를 나누어 할당받으면 지연이 크게 늘어납니다. 성능 문제의 첫 조치가 CPU 수를 줄이는 것인 경우도 많습니다.

### 시작과 실패

HAProxy는 시작할 때 설정을 모두 읽고 모든 listen socket을 bind합니다. 하나라도 실패하면 시작하지 않습니다. 시작에 성공한 뒤에는 연결 처리, 서버 헬스체크, 다른 HAProxy 노드와의 정보 교환(peers) 세 가지만 합니다.

### master와 worker

systemd에서 `-Ws` 옵션으로 실행하면 master-worker 모드가 됩니다. master는 설정을 읽고 worker를 띄워 관리하며, 실제 트래픽은 worker가 처리합니다. 설정을 다시 읽을 때는 master가 새 worker를 띄우고 이전 worker는 처리 중인 연결이 끝나면 종료합니다([9절](#9-무중단-reload)).

```
            systemd (Type=notify)
                   |
                   v
             +-----------+   SIGUSR2 / master CLI "reload"
             |  master   | <-------------------------------
             +-----------+
               |       |
         fork  |       |  keeps until old jobs finish
               v       v
         +---------+ +---------+
         | worker  | | worker  |
         |  (new)  | |  (old)  |
         +---------+ +---------+
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설정 구조

설정 파일은 section으로 나뉘며, 각 section은 다음 section 키워드가 나올 때까지 이어집니다.

| section    | 역할                                                                      |
|------------|---------------------------------------------------------------------------|
| `global`   | 프로세스 전체 설정: 사용자, chroot, 로그 대상, 스레드, Runtime API socket |
| `defaults` | 뒤따르는 proxy section에 적용할 기본값: mode, timeout, log 형식           |
| `frontend` | 클라이언트 연결을 받는 쪽: bind 주소, 요청 규칙, backend 선택             |
| `backend`  | 서버 묶음: 서버 목록, 분산 알고리즘, 헬스체크                             |
| `listen`   | frontend와 backend를 합친 형태: TCP 프록시나 통계 화면처럼 단순한 경우    |

공식 문서는 frontend와 backend를 각각 한쪽만 보는 "half-proxy"로 설명합니다. frontend는 클라이언트만, backend는 서버만 봅니다. HTTP는 여러 frontend가 여러 backend를 고를 수 있도록 나누어 쓰고, TCP만 다루면 `listen` 하나가 더 읽기 쉽습니다.

### mode

| mode   | 분산 단위 | 볼 수 있는 정보                     | 대표 용도                        |
|--------|-----------|-------------------------------------|----------------------------------|
| `tcp`  | 연결      | 주소, 포트, TLS SNI(검사 시)        | DB, Redis, TLS 통과(passthrough) |
| `http` | 요청      | 메서드, 경로, 헤더, 쿠키, 상태 코드 | 웹, API, TLS 종료                |

`http` 모드에서는 한 연결 안의 요청마다 다른 서버를 고를 수 있고, 잘못된 HTTP 요청은 서버에 전달하지 않습니다.

```
global
    ...

defaults
    mode http
    timeout connect 5s
    timeout client  30s
    timeout server  30s

frontend fe_web
    bind :80
    default_backend be_app

backend be_app
    server app1 192.0.2.11:8080 check
    server app2 192.0.2.12:8080 check
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 요청 처리와 규칙

### 처리 순서

공식 소개 문서는 연결 처리를 9단계로 설명합니다.

```
client
  |
  v
[1] frontend accepts connection (bind)
[2] frontend request rules  (http-request / tcp-request)
[3] pick backend            (use_backend / default_backend)
[4] backend request rules
[5] pick server             (persistence, then balance algorithm)
       |
       v
     server
       |
[6] backend response rules  (http-response)
[7] frontend response rules
[8] emit log
[9] HTTP: wait for next request on same connection, else close
```

### ACL, fetch, converter

규칙의 조건은 세 요소로 만듭니다.

| 요소      | 뜻                              | 예                                |
|-----------|---------------------------------|-----------------------------------|
| fetch     | 요청·연결·서버에서 값을 꺼냄    | `src`, `path`, `req.hdr(host)`    |
| converter | 꺼낸 값을 바꿈                  | `lower`, `ipmask(24)`, `map(...)` |
| ACL       | 값과 기준을 비교해 참·거짓을 냄 | `acl is_api path_beg /api/`       |

이름 붙인 ACL 대신 `{ ... }` 안에 바로 조건을 써도 됩니다(익명 ACL).

```
frontend fe_web
    bind :80
    acl is_api path_beg /api/
    http-request deny if { path_beg /admin } !{ src 10.0.0.0/8 }
    use_backend be_api if is_api
    default_backend be_app
```

- 규칙은 같은 종류끼리 적힌 순서대로 평가합니다. `deny`처럼 처리를 끝내는 규칙이 참이 되면 뒤 규칙은 실행하지 않습니다.
- `use_backend`는 처음으로 참이 된 줄을 쓰고, 모두 거짓이면 `default_backend`로 갑니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 분산 알고리즘

backend의 `balance`가 서버를 고릅니다. 세션 유지 정보([6절](#6-세션-유지))가 있으면 그 서버가 먼저이고, 알고리즘은 유지 정보가 없거나 다른 서버로 다시 보낼 때만 씁니다.

| 알고리즘     | 방식                                       | 가중치 실시간 변경 | 맞는 경우                           |
|--------------|--------------------------------------------|--------------------|-------------------------------------|
| `random`     | 무작위로 N개(기본 2)를 뽑아 부하가 적은 쪽 | 가능               | 3.3 이상 기본값, 대부분의 HTTP      |
| `roundrobin` | 가중치에 따라 차례로                       | 가능               | 처리 시간이 고른 요청               |
| `static-rr`  | roundrobin과 같으나 가중치 고정            | 불가               | 서버가 아주 많은 단순 분산          |
| `leastconn`  | 현재 연결 수가 가장 적은 서버              | 가능               | 연결이 오래가는 DB, WebSocket       |
| `first`      | 앞 서버의 maxconn이 찰 때까지 몰아줌       | 무시               | 사용하지 않는 서버를 끄는 절전 구성 |
| `source`     | 클라이언트 IP hash                         | 기본 불가          | 쿠키를 쓸 수 없는 TCP 세션 유지     |
| `uri`·`hash` | URI나 지정한 값의 hash                     | 기본 불가          | 같은 객체를 같은 캐시 서버로        |

- 🟡 **기본값이 바뀌었습니다.** HAProxy 3.3부터 `balance`를 쓰지 않은 backend는 `random`(2개 중 선택)을 씁니다. 이전 버전 설정을 옮길 때 `roundrobin`에 기대고 있었다면 명시적으로 적습니다.
- `random(2)`는 "Power of Two Random Choices" 방식입니다. 두 서버만 비교해도 가장 바쁜 서버를 피하므로 분포가 고르고 비용이 적습니다. 공식 문서는 서버당 초당 요청이 아주 적은 큰 서버 묶음에서 3이나 4로 올릴 것을 제안합니다.
- hash 계열은 기본이 정적 map 방식이라 서버가 하나 빠지면 대부분의 키가 다른 서버로 옮겨 갑니다. `hash-type consistent`를 쓰면 빠진 서버 몫만 옮겨 갑니다.
- `roundrobin`은 backend당 활성 서버를 4095개까지 다룹니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 세션 유지

로그인 세션을 서버 메모리에 두는 애플리케이션은 같은 사용자를 같은 서버로 보내야 합니다. HAProxy는 두 가지 방법을 씁니다.

| 방법        | 원리                                                      | 장점                              | 주의                                       |
|-------------|-----------------------------------------------------------|-----------------------------------|--------------------------------------------|
| 쿠키        | HAProxy가 응답에 서버 이름 쿠키를 넣고 다음 요청에서 읽음 | 서버 상태를 저장하지 않음         | HTTP 모드 전용, 쿠키를 거부하는 클라이언트 |
| stick-table | IP·헤더 등 키와 서버를 메모리 표에 기록                   | TCP 모드에서도 가능, peers로 공유 | 표 크기·만료 시간 설계, 재시작 시 사라짐   |

```
backend be_app
    balance random
    cookie SRV insert indirect nocache
    server app1 192.0.2.11:8080 check cookie a1
    server app2 192.0.2.12:8080 check cookie a2
```

stick-table은 세션 유지 외에 요청 수·오류 수 같은 카운터를 키별로 세는 데에도 씁니다. 속도 제한 예는 [운영 가이드](./haproxy_operations_guide.md#9-요청-속도-제한)에 있습니다.

🔵 세션을 Redis 같은 외부 저장소에 두는 애플리케이션이라면 세션 유지가 필요 없고, 분산이 더 고르게 됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 헬스체크와 서버 상태

### 헬스체크

`server` 줄에 `check`를 붙이면 헬스체크를 시작합니다. `option httpchk`가 없으면 TCP 연결 성공 여부만 봅니다.

| 매개변수 | 뜻                       | 기본값  |
|----------|--------------------------|---------|
| `inter`  | 검사 간격                | 2000 ms |
| `rise`   | 연속 몇 번 성공하면 UP   | 2       |
| `fall`   | 연속 몇 번 실패하면 DOWN | 3       |

기본값이면 서버가 죽은 뒤 약 6초(2초 × 3회) 동안은 요청이 그 서버로 갈 수 있습니다. 이 사이 실패한 연결은 `retries`·`option redispatch`로 다른 서버에 다시 보냅니다.

HTTP 검사는 `option httpchk`에 `http-check send`·`http-check expect`를 더해 씁니다. `option httpchk`만 쓰면 `OPTIONS / HTTP/1.0`을 보냅니다.

### 운영 상태와 관리 상태

서버 상태는 두 축으로 봅니다.

| 축        | 값        | 정하는 주체         | 뜻                                           |
|-----------|-----------|---------------------|----------------------------------------------|
| 운영 상태 | UP / DOWN | 헬스체크            | 서버가 실제로 응답하는가                     |
| 관리 상태 | `ready`   | 운영자(Runtime API) | 정상 분산 대상                               |
| 관리 상태 | `drain`   | 운영자              | 분산에서 빼되 헬스체크·세션 유지 연결은 받음 |
| 관리 상태 | `maint`   | 운영자              | 트래픽과 헬스체크를 모두 멈춤                |

배포할 때는 `drain`으로 새 요청을 끊고 기존 연결이 줄어든 뒤 `maint`로 바꾸어 작업합니다. 절차는 [운영 가이드 6절](./haproxy_operations_guide.md#6-배포-중-서버-빼기)에 있습니다.

### 그 밖의 서버 옵션

| 옵션        | 뜻                                                             |
|-------------|----------------------------------------------------------------|
| `backup`    | 다른 서버가 모두 DOWN일 때만 사용                              |
| `weight`    | 상대 가중치(기본 1)                                            |
| `maxconn`   | 이 서버로 동시에 보낼 최대 연결 수. 넘으면 HAProxy 큐에서 대기 |
| `slowstart` | 복구된 서버의 가중치를 지정 시간 동안 천천히 올림              |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 연결과 timeout

### HTTP 연결 모드

HAProxy는 기본으로 클라이언트 쪽과 서버 쪽 모두 keep-alive로 동작하며, 서버 쪽 유휴 연결을 다른 요청에 다시 씁니다. `option http-server-close`는 서버 쪽 연결만 요청마다 닫는 옵션으로, keep-alive를 지원하지 않는 서버가 있을 때만 씁니다.

### 연결 한도와 큐

```
client --> [frontend maxconn] --> [backend] --> [server maxconn] --> server
                                       |
                                       +-- queue (timeout queue)
```

- global `maxconn`을 쓰지 않으면 파일 디스크립터 한도(`ulimit -n`)에서 자동으로 계산합니다.
- 서버 `maxconn`에 도달한 요청은 HAProxy 큐에서 기다립니다. 서버가 과부하로 느려지는 것보다 HAProxy에서 기다리는 편이 전체 응답 시간이 짧은 경우가 많습니다.

### timeout

| timeout           | 재는 구간                              | 설정하지 않으면        |
|-------------------|----------------------------------------|------------------------|
| `connect`         | 서버와 TCP 연결을 맺기까지             | 무제한(시작 시 경고)   |
| `client`          | 클라이언트가 아무것도 보내지 않는 시간 | 무제한(시작 시 경고)   |
| `server`          | 서버가 아무것도 보내지 않는 시간       | 무제한(시작 시 경고)   |
| `http-request`    | 요청 헤더 전체를 받기까지(초과 시 408) | `timeout client` 적용  |
| `http-keep-alive` | 응답 뒤 다음 요청이 시작되기까지       | `timeout http-request` |
| `queue`           | 큐에서 서버 자리를 기다리는 시간       | `timeout connect`      |
| `tunnel`          | WebSocket·CONNECT 전환 뒤 유휴 시간    | `client`·`server` 적용 |
| `check`           | 헬스체크 응답 대기                     | `inter`                |

🟡 `timeout http-request`를 두지 않으면 헤더를 아주 천천히 보내는 공격(slowloris)에 `timeout client` 전체가 쓰입니다. 공식 문서는 몇 초면 충분하다고 설명합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 무중단 reload

설정을 바꾸면 프로세스를 재시작하지 않고 reload합니다.

1. master가 `SIGUSR2`(systemd `reload`)나 master CLI `reload` 명령을 받습니다.
2. master가 설정을 다시 읽고 새 worker를 띄웁니다. listen socket은 master가 새 worker에 넘겨주므로 포트를 다시 bind하는 틈이 없습니다.
3. 이전 worker는 새 연결을 받지 않고 처리 중인 연결이 끝나면 종료합니다.

| 방법                       | 결과 확인                                    |
|----------------------------|----------------------------------------------|
| `systemctl reload haproxy` | unit의 `ExecReload`가 `-c` 검사 뒤 신호 전송 |
| master CLI `reload`        | `Success=1` 같은 결과를 바로 돌려줌          |

- 설정 문법이 틀리면 새 worker를 띄우지 않고 이전 worker가 계속 동작합니다. reload 실패가 곧 중단은 아니지만, 바뀐 설정이 적용되지 않은 상태가 남습니다.
- 연결이 오래 유지되는 서비스(WebSocket, DB 프록시)는 이전 worker가 오래 남습니다. 메모리 사용이 reload 횟수만큼 늘 수 있으므로 `hard-stop-after`로 상한을 둡니다.
- 3.3부터 통계 카운터를 reload 뒤에도 이어서 유지할 수 있습니다(stats-file).

[⬆ 목차로 돌아가기](#목차)

---

## 10. 버전 정책

짝수 분기(3.0, 3.2, 3.4)는 LTS로 5년 지원하고, 홀수 분기(3.1, 3.3)는 stable로 다음 분기 뒤 짧게 지원합니다. 2026-11-06 확인 기준입니다.

| 분기 | 최신   | 상태                | 지원 종료 |
|------|--------|---------------------|-----------|
| 3.4  | 3.4.7  | LTS                 | 2031-Q2   |
| 3.3  | 3.3.17 | stable              | 2027-Q1   |
| 3.2  | 3.2.26 | LTS                 | 2030-Q2   |
| 3.0  | 3.0.30 | LTS                 | 2029-Q2   |
| 2.8  | 2.8.31 | critical fixes only | 2028-Q2   |
| 2.6  | 2.6.35 | critical fixes only | 2027-Q2   |

- 운영에는 LTS 분기를 쓰고, 같은 분기 안의 최신 수정판으로 올립니다.
- 3.1·2.9·2.4 이하는 지원이 끝났습니다.
- Ubuntu 24.04 기본 저장소는 2.8 분기를 제공합니다. 새 기능(3.3 기본 알고리즘, 3.4 동적 backend 등)이 필요하면 [운영 가이드 2절](./haproxy_operations_guide.md#2-버전-선택과-설치-소스)의 설치 소스를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HAProxy 공식 사이트(버전 표): [haproxy.org](https://www.haproxy.org/) — ★★★★☆
- HAProxy 3.4 Starter Guide: [docs.haproxy.org/3.4/intro.html](https://docs.haproxy.org/3.4/intro.html) — ★★★★☆
- HAProxy 3.4 Configuration Manual: [docs.haproxy.org/3.4/configuration.html](https://docs.haproxy.org/3.4/configuration.html) — ★★★★★
- HAProxy 3.4 Management Guide: [docs.haproxy.org/3.4/management.html](https://docs.haproxy.org/3.4/management.html) — ★★★★☆
- 확인 기록: [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy)
- 관련 문서: [HAProxy 설치 가이드](./haproxy_install.md), [HAProxy 운영 가이드](./haproxy_operations_guide.md), [로드 밸런서 테스트](../../01_fundamentals/cs/web_testing/load_balancer_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-06

**마지막 업데이트**: 2026-11-06

© 2026 siasia86. Licensed under CC BY 4.0.
