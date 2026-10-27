# Graceful Reload 테스트 (Graceful Reload Testing)
<!-- reference: _reference/web_testing_official_notes.md -->

Graceful Reload 테스트는 웹 서버·프록시가 설정이나 인증서를 다시 읽는 동안 처리 중인 요청을 잃지 않고, 잘못된 설정은 적용하지 않으며, 이전 프로세스를 정해진 시간 안에 정리하는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                               |
|-----------|--------------------------------------------------------------------|
| 목적      | 설정 반영 과정에서 요청 유실·중복·장시간 지연이 없는지 확인        |
| 실행 시점 | 배포 자동화 도입·변경, 인증서 자동 갱신 도입, 웹 서버 버전 변경 후 |
| 핵심 질문 | 부하 중에 reload해도 클라이언트가 오류를 보지 않는가               |
| 판정 근거 | nginx 제어 신호 문서, HAProxy 관리 문서, 서비스 배포 기준          |

reload는 프로세스 재시작(restart)과 다릅니다. restart는 listen 소켓을 닫았다가 다시 열므로 그 사이의 연결이 거부될 수 있고, reload는 새 프로세스가 요청을 받는 동안 이전 프로세스가 기존 요청을 마칩니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
reload signal
     │
     v
[master] ── syntax check ──(fail)──> keep old config, old workers continue
     │
   (ok)
     ├──> start new workers  ──> accept new connections
     └──> old workers: close listen sockets
                        finish in-flight requests
                        exit (or forced after shutdown timeout)
```

| 제품    | 다시 읽기                               | 이전 프로세스 종료 상한                 |
|---------|-----------------------------------------|-----------------------------------------|
| nginx   | master에 HUP (`nginx -s reload`)        | `worker_shutdown_timeout` (기본값 없음) |
| HAProxy | master-worker 모드에서 master에 SIGUSR2 | `hard-stop-after`                       |

nginx는 새 설정을 적용하지 못하면 변경을 되돌리고 이전 설정으로 계속 동작합니다. 이 동작이 실제로 일어나는지 확인하는 것이 핵심 케이스 중 하나입니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 요청 보존

| 케이스             | 입력                                        | 기대 결과                                 | 실패 판정                          |
|--------------------|---------------------------------------------|-------------------------------------------|------------------------------------|
| 부하 중 reload     | 일정 부하를 거는 동안 reload 반복           | 오류율 변화 없음                          | reload 시점마다 연결 거부·5xx 발생 |
| 처리 중인 긴 요청  | 응답에 수십 초 걸리는 요청 중 reload        | 이전 worker가 응답을 끝까지 전송          | 응답 중간 절단                     |
| 큰 업로드·다운로드 | 전송 중 reload                              | 전송 완료                                 | 전송 중단, 크기 불일치             |
| keep-alive 연결    | 유휴 keep-alive 연결이 있는 상태에서 reload | 다음 요청이 정상 처리되거나 깔끔히 재연결 | 클라이언트가 재시도 없이 오류      |
| 비멱등 요청        | reload 시점의 POST                          | 한 번만 처리                              | 중복 처리, 처리 여부 불명          |

### 장기 연결과 종료 상한

| 케이스             | 입력                         | 기대 결과                                  | 실패 판정                               |
|--------------------|------------------------------|--------------------------------------------|-----------------------------------------|
| WebSocket 유지     | WebSocket 연결 중 reload     | 설계대로 유지 또는 정해진 시점에 정상 종료 | 예고 없이 끊김                          |
| 이전 프로세스 누적 | 짧은 간격으로 reload 여러 번 | 이전 프로세스 수가 상한 안에서 감소        | 이전 프로세스가 계속 쌓여 메모리 증가   |
| 종료 상한 적용     | 종료 상한보다 긴 연결 유지   | 상한 시점에 이전 프로세스 종료             | 상한이 없어 이전 프로세스가 무기한 유지 |

### 설정·인증서 반영

| 케이스         | 입력                             | 기대 결과                                | 실패 판정                 |
|----------------|----------------------------------|------------------------------------------|---------------------------|
| 문법 오류 설정 | 문법 오류가 있는 설정으로 reload | reload 거부, 이전 설정으로 계속 서비스   | 서비스 중단               |
| 적용 실패 설정 | 이미 사용 중인 포트 listen 추가  | 이전 설정 유지, 오류 로그 기록           | 일부만 적용된 상태로 동작 |
| 설정 변경 반영 | 응답 헤더 추가 후 reload         | 새 연결부터 변경 적용                    | 일부 worker만 새 설정     |
| 인증서 교체    | 새 인증서 파일 배치 후 reload    | 새 TLS 연결에 새 인증서 제공             | 이전 인증서 계속 제공     |
| 배포 전 검사   | 배포 자동화의 reload 단계        | reload 전에 문법 검사 실행, 실패 시 중단 | 검사 없이 reload          |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구                                  | 용도                              |
|---------------------------------------|-----------------------------------|
| `nginx -t`, `haproxy -c -f <파일>`    | reload 전 문법 검사               |
| `nginx -s reload`, `systemctl reload` | 설정 다시 읽기                    |
| `k6`·`h2load`                         | reload 중 일정 부하와 오류율 측정 |
| `ps`, `pgrep`                         | 이전·새 worker 프로세스 확인      |
| `openssl s_client`                    | 인증서 교체 반영 확인             |

### 명령 예시

```bash
# 문법 검사 후에만 reload
nginx -t && nginx -s reload
haproxy -c -f /etc/haproxy/haproxy.cfg && systemctl reload haproxy

# reload 전후 worker 프로세스 (이전 worker는 "shutting down" 표시)
ps -o pid,ppid,etime,cmd -C nginx

# 부하를 거는 동안 다른 터미널에서 10초마다 reload
for i in $(seq 1 6); do nginx -s reload; sleep 10; done

# 새 인증서의 만료일과 일련번호 확인
openssl s_client -connect 192.0.2.10:443 -servername www.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -serial -enddate
```

부하 측정은 [웹 성능·Timeout 테스트](web_performance_timeout_testing.md)의 k6 threshold를 그대로 쓰고, reload 시각을 기록해 오류·지연 그래프와 맞춰 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                          | 우선 확인 대상                                             |
|-------------------------------|------------------------------------------------------------|
| reload 순간 연결 거부         | 실제로 restart가 실행되는지, 서비스 관리자의 reload 정의   |
| reload 순간 502               | upstream keepalive 연결 정리, 프록시 앞단의 연결 재사용    |
| 이전 프로세스가 사라지지 않음 | 장기 연결, 종료 상한 미설정                                |
| 인증서가 바뀌지 않음          | 파일 경로·심볼릭 링크, reload 누락, 여러 서버 중 일부 누락 |
| 문법 오류인데 서비스 중단     | 배포 도구가 restart 사용, 문법 검사 생략                   |

### 분석 원칙

- reload 시각을 로그와 지표에 표시해 오류와의 시간 관계를 확인합니다.
- 서비스 관리자(systemd 등)의 `reload` 동작이 실제로 어떤 명령을 실행하는지 단위 파일에서 확인합니다.
- 오류가 클라이언트 재시도로 가려지지 않도록 부하 도구의 재시도를 끄고 측정합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 부하 중 반복 reload에서 오류율 변화가 없음을 확인했습니다.
- [ ] 처리 중인 긴 요청과 큰 전송이 끝까지 완료됨을 확인했습니다.
- [ ] 장기 연결의 유지·종료 방식이 설계와 같음을 확인했습니다.
- [ ] 이전 프로세스 종료 상한을 설정하고 적용을 확인했습니다.
- [ ] 문법 오류·적용 실패 설정에서 이전 설정이 유지됨을 확인했습니다.
- [ ] 인증서 교체가 모든 서버에 반영됨을 확인했습니다.
- [ ] 배포 자동화가 reload 전에 문법 검사를 실행합니다.

## 참고 자료

- nginx Controlling nginx: [nginx.org](https://nginx.org/en/docs/control.html) — ★★★☆☆
- nginx core module `worker_shutdown_timeout`: [nginx.org](https://nginx.org/en/docs/ngx_core_module.html) — ★★★☆☆
- HAProxy Management Guide 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/management.html) — ★★★☆☆
- [Nginx 설치 가이드](../../../02_infrastructure/web_server/nginx_install.md)
- [HAProxy 설치 가이드](../../../02_infrastructure/web_server/haproxy_install.md)
- [TLS/HTTPS 테스트](tls_https_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-27

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.
