# HAProxy ACME 인증서 자동 갱신 가이드
<!-- reference: _reference/web_server_official_notes.md, _reference/tls_cert_lifecycle_official_notes.md -->

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 동작 방식](#2-동작-방식) / [3. 방식 선택](#3-방식-선택)                           |
| [4. 준비](#4-준비) / [5. http-01 설정](#5-http-01-설정) / [6. 발급과 상태 확인](#6-발급과-상태-확인)       |
| [7. 디스크 저장](#7-디스크-저장) / [8. DNS 방식](#8-dns-방식) / [9. 갱신 시점과 감시](#9-갱신-시점과-감시) |
| [10. 이중화 구성 주의](#10-이중화-구성-주의) / [11. 장애 사례](#11-장애-사례)                              |

---

## 1. 개요

HAProxy는 3.2부터 ACME 클라이언트를 내장합니다. certbot·acme.sh 없이 HAProxy가 직접 CA(Let's Encrypt 등)에 인증서를 요청하고, 만료가 가까워지면 갱신해 메모리의 인증서를 바꿉니다.

| 버전 | 추가된 것                                                                                      |
|------|------------------------------------------------------------------------------------------------|
| 3.2  | ACME 초기 지원(http-01). 시작할 때 디스크에 인증서 파일이 있어야 함                            |
| 3.3  | `crt-store`로 선언하면 인증서 파일 없이 시작 가능(임시 키 쌍 사용), Data Plane API 경유 dns-01 |
| 3.4  | dns-persist-01, External Account Binding(EAB), 발급 프로필(`profile`), DNS 방식 기능 확장      |

🟡 **실험 기능입니다.** 3.4 설정 문서는 ACME를 실험 기능으로 분류하며 `global`에 `expose-experimental-directives`가 있어야 씁니다. 운영 적용은 [3절](#3-방식-선택)의 비교를 보고 정합니다.

🟡 이 문서는 HAProxy 3.4 설정·관리 문서, haproxy-3.4 소스의 `admin/cli/haproxy-dump-certs`, HAProxy 공식 wiki의 ACME 안내, Let's Encrypt directory 응답을 읽고 정리했으며 작성 시 HAProxy를 실행하거나 인증서를 발급하지 않았습니다. 확인 범위는 [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy)에 기록했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 동작 방식

```
 HAProxy start
      |
      v
 ACME scheduler  -- every 12h -->  check each cert linked to "acme"
      |
      |  notAfter - now < (notAfter - notBefore) / 12 ?
      v
 renewal task:  newOrder --> challenge --> finalize --> download
      |                         |
      |            http-01: CA requests
      |            /.well-known/acme-challenge/<token>
      |            HAProxy answers from map (virt@acme)
      v
 certificate replaced in MEMORY only
      |
      v
 "dump ssl cert" / haproxy-dump-certs --> file on disk
```

| 항목           | 공식 문서 내용                                                                      |
|----------------|-------------------------------------------------------------------------------------|
| 갱신 시점      | 남은 기간이 전체 유효 기간의 1/12보다 짧아지면 시작. notBefore가 없으면 만료 7일 전 |
| 확인 주기      | 시작 시 한 번, 이후 12시간마다                                                      |
| 수동 갱신      | CLI `acme renew <인증서>`                                                           |
| 저장 위치      | 메모리. 디스크 쓰기는 이벤트 루프를 막을 수 있어 HAProxy가 하지 않음                |
| 계정 키        | `account-key`가 없으면 `<section 이름>.account.key`를 읽고, 없으면 새로 만듦        |
| 기본 키 종류   | ECDSA P-384. RSA를 고르면 기본 2048비트                                             |
| 기본 challenge | http-01                                                                             |

🟡 **reload하면 다시 발급합니다.** 공식 wiki는 HAProxy가 디스크에 아무것도 저장하지 않으므로, 저장하지 않은 채 reload하면 인증서를 다시 요청하고 CA의 발급 횟수 제한에 걸릴 수 있다고 설명합니다. [7절](#7-디스크-저장)의 저장 절차가 필수입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 방식 선택

| 기준              | HAProxy 내장 ACME                                | 외부 클라이언트(certbot·acme.sh) + reload |
|-------------------|--------------------------------------------------|-------------------------------------------|
| 성숙도            | 실험 기능                                        | 오래 쓰인 방식                            |
| 추가 프로그램     | 없음(저장용 스크립트·socat 필요)                 | ACME 클라이언트, 갱신 후 reload 훅        |
| 인증서 파일       | 메모리에서 꺼내 저장해야 함                      | 클라이언트가 파일로 저장                  |
| 갱신 시점         | 유효 기간의 마지막 1/12 (조정 설정 없음)         | 클라이언트 설정·ARI에 따름                |
| http-01 응답      | HAProxy가 직접 응답                              | 웹 루트나 별도 포트로 넘기는 규칙 필요    |
| 여러 노드(이중화) | 노드마다 따로 발급([10절](#10-이중화-구성-주의)) | 한 곳에서 발급해 배포 가능                |

- **권장:** 운영 서버는 외부 클라이언트 + reload를 기본으로 두고, 내장 ACME는 단일 노드·시험 환경에서 먼저 씁니다. 실험 기능이고 갱신 시점을 조정할 수 없기 때문입니다.
- 외부 클라이언트로 갱신할 때 HAProxy용 PEM 만들기는 [운영 가이드 8절](./haproxy_operations_guide.md#8-tls-종료)을 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 준비

| 항목           | 확인                                                                                         |
|----------------|----------------------------------------------------------------------------------------------|
| HAProxy 버전   | 3.3 이상 권장(파일 없이 시작). dns-persist-01은 3.4. `haproxy -v`                            |
| TLS 라이브러리 | `haproxy -vv`의 OpenSSL 등 빌드 정보                                                         |
| 80번 포트      | http-01은 CA가 `http://<도메인>/.well-known/acme-challenge/`로 접속. 외부에서 열려 있어야 함 |
| DNS            | 인증서에 넣을 도메인이 이 HAProxy(또는 VIP)를 가리켜야 함                                    |
| master socket  | 공식 unit은 `-S /run/haproxy-master.sock`. 저장 스크립트가 사용                              |
| 도구           | `socat`, `openssl`                                                                           |

설치 소스는 [운영 가이드 2절](./haproxy_operations_guide.md#2-버전-선택과-설치-소스)을 봅니다. Ubuntu 24.04 기본 저장소의 2.8에는 이 기능이 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. http-01 설정

처음에는 반드시 Let's Encrypt **staging** directory로 시험합니다. staging 인증서는 브라우저가 신뢰하지 않지만 발급 횟수 제한 걱정 없이 절차를 확인할 수 있습니다.

```
global
    expose-experimental-directives
    stats socket /run/haproxy/admin.sock mode 660 level admin
    crt-base /etc/haproxy/certs

acme LE
    directory https://acme-staging-v02.api.letsencrypt.org/directory
    contact admin@example.com
    challenge http-01
    keytype ECDSA
    map virt@acme

crt-store
    load crt "example.com.pem" acme LE domains "example.com,www.example.com"

frontend fe_web
    bind :80
    bind :443 ssl
    # http-01 challenge answer (token.thumbprint)
    http-request return status 200 content-type text/plain lf-string "%[path,field(-1,/)].%[path,field(-1,/),map(virt@acme)]\n" if { path_beg '/.well-known/acme-challenge/' }
    http-request redirect scheme https code 301 unless { ssl_fc }
    ssl-f-use crt "example.com.pem"
    default_backend be_app
```

| 설정                           | 뜻                                                                    |
|--------------------------------|-----------------------------------------------------------------------|
| `acme LE`                      | ACME section. 인증서와 이름으로 연결                                  |
| `directory`                    | CA의 directory 주소. 기본값이 없어 필수                               |
| `map virt@acme`                | challenge token과 thumbprint를 담을 가상 map. 발급 중에만 항목이 있음 |
| `load crt ... acme LE domains` | 인증서와 ACME section 연결. 첫 도메인이 CN                            |
| `http-request return ...`      | CA의 http-01 요청에 HAProxy가 직접 응답                               |
| `ssl-f-use crt`                | 443 bind들이 쓸 인증서                                                |

- `global`에 `crt-base`가 있으면 HAProxy 안의 인증서 이름은 `/etc/haproxy/certs/example.com.pem`처럼 `crt-base`를 붙인 경로가 됩니다(3.4 소스 `src/ssl_ckch.c`의 `crtstore_parse_load`). 아래 CLI 명령에는 `acme status`·`show ssl cert`에 나오는 이름을 그대로 씁니다.
- challenge 응답 줄은 HTTPS 리다이렉트 **앞**에 둡니다. 뒤에 두면 CA 요청이 443으로 넘어가 실패할 수 있습니다.
- 시험이 끝나면 `directory`를 운영 주소 `https://acme-v02.api.letsencrypt.org/directory`로 바꿉니다. staging과 운영의 계정은 CA마다 따로 만들어지므로 `account-key`로 키 파일 이름을 나누어 두면 구분하기 쉽습니다.
- `contact`의 주소는 CA 계정에 연결됩니다. 개인 주소 대신 팀 공용 주소를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 발급과 상태 확인

```bash
# 설정 검사 후 reload
sudo haproxy -c -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d
sudo systemctl reload haproxy

# 즉시 발급(스케줄을 기다리지 않음). @1 = 현재 worker
echo "@1 acme renew /etc/haproxy/certs/example.com.pem" | sudo socat /run/haproxy-master.sock -

# 상태
echo "@1 acme status" | sudo socat /run/haproxy-master.sock - | column -t -s $'\t'
```

`acme status` 출력 열:

| 열                    | 뜻                                 |
|-----------------------|------------------------------------|
| certificate           | HAProxy 안의 인증서 이름           |
| section               | 연결된 acme section                |
| state                 | `Running`, `Scheduled`, `Stopped`  |
| expiration date (UTC) | 만료 시각(ISO8601)                 |
| expires in            | 만료까지 남은 시간(만료면 0d)      |
| scheduled date (UTC)  | 다음 갱신 예정 시각                |
| scheduled in          | 갱신까지 남은 시간(진행 중이면 0d) |

```bash
# 메모리의 인증서 내용 확인
echo "@1 dump ssl cert /etc/haproxy/certs/example.com.pem" | sudo socat /run/haproxy-master.sock - \
  | openssl storeutl -noout -text /dev/stdin | grep -E 'Issuer|Not After|DNS:'
```

발급 진행·오류는 HAProxy 로그(`journalctl -u haproxy`)에서 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 디스크 저장

HAProxy 소스에는 메모리의 인증서를 파일로 저장하는 `admin/cli/haproxy-dump-certs` 스크립트가 있습니다(스크립트 스스로 실험 단계라고 밝힘).

| 동작        | 내용                                                                     |
|-------------|--------------------------------------------------------------------------|
| 대상        | `show ssl cert`에 나오는 인증서 전체, 또는 지정한 인증서                 |
| 같은 인증서 | 지문이 같으면 건너뜀                                                     |
| 키 검사     | 새 인증서의 공개키와 개인키가 맞지 않으면 저장하지 않음                  |
| 이전 파일   | `<파일>.old.<유닉스시각>`으로 옮긴 뒤 새 파일로 교체                     |
| 주요 옵션   | `-S` master socket, `-s` stats socket, `-p` 상대 경로 기준, `-n` dry-run |

```bash
# 먼저 dry-run
sudo haproxy-dump-certs -n -v -p /etc/haproxy/certs -S /run/haproxy-master.sock

# 저장
sudo haproxy-dump-certs -v -p /etc/haproxy/certs -S /run/haproxy-master.sock /etc/haproxy/certs/example.com.pem
```

공식 wiki는 정지·reload 때마다 저장하도록 systemd unit에 넣는 방법을 안내합니다. 패키지 unit을 직접 고치지 않고 drop-in으로 더합니다.

```ini
# sudo systemctl edit haproxy
[Service]
ExecStop=/usr/local/sbin/haproxy-dump-certs -p /etc/haproxy/certs -S /run/haproxy-master.sock
ExecReload=
ExecReload=/usr/local/sbin/haproxy-dump-certs -p /etc/haproxy/certs -S /run/haproxy-master.sock
ExecReload=/usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d -c -S /run/haproxy-master.sock
ExecReload=/bin/kill -USR2 $MAINPID
```

- 🟡 스크립트 설치 경로는 배포판 패키지마다 다를 수 있습니다(공식 wiki 예시는 `/usr/sbin`). 패키지에 없으면 사용 중인 HAProxy 버전 태그의 소스에서 받아 `/usr/local/sbin`에 두고, 내용을 읽은 뒤 씁니다.
- `ExecReload=` 빈 줄은 기존 reload 명령을 지우고 다시 정의한다는 뜻입니다. 나머지 두 줄은 HAProxy 3.4 공식 unit의 reload 명령과 같으며, 실제 unit의 값을 `systemctl cat haproxy`로 확인해 맞춥니다.
- 이 방식은 갱신 직후가 아니라 reload·정지 때만 저장합니다. 그 사이 서버가 갑자기 꺼지면 새 인증서를 잃고 시작 시 다시 발급합니다. 주기적으로(예: 하루 한 번) 저장 스크립트를 실행하는 timer를 함께 둡니다.
- 저장한 PEM에는 개인키가 들어 있습니다. 디렉터리 권한 700, 파일 600을 유지하고 백업 대상에 넣을 때 암호화합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. DNS 방식

와일드카드 인증서나 80번 포트를 열 수 없는 경우 DNS 방식을 씁니다. 아래 설정 항목은 HAProxy 3.4 문서 기준입니다.

| challenge        | TXT 레코드                     | 갱신마다 DNS 변경  | HAProxy 밖에서 필요한 것                        |
|------------------|--------------------------------|--------------------|-------------------------------------------------|
| `dns-01`         | `_acme-challenge.<도메인>`     | 필요               | DNS 제공자 API를 다루는 도구(Data Plane API 등) |
| `dns-persist-01` | `_validation-persist.<도메인>` | 불필요(한 번 설정) | 처음 한 번 TXT 등록(수동 가능)                  |

`challenge-ready`는 CA에 "검증 준비 완료"를 알리기 전 조건입니다.

| 값      | 뜻                                                                                     |
|---------|----------------------------------------------------------------------------------------|
| `cli`   | 운영자·도구가 CLI `acme challenge_ready <인증서> domain <도메인>`으로 알릴 때까지 대기 |
| `dns`   | `default` resolvers로 TXT 레코드를 조회해 맞을 때까지 대기                             |
| `delay` | `dns-delay`(기본 30초)만큼 대기                                                        |
| `none`  | 바로 진행                                                                              |

- 기본값은 dns-01이 `cli`, dns-persist-01이 `dns,delay`입니다. `dns` 조회는 권한 DNS가 아니라 설정된 resolver를 거치므로 캐시 영향을 받습니다. 조회 상한은 `dns-timeout`(기본 600초)입니다.
- dns-persist-01은 갱신 때 TXT 레코드가 이미 있으면 준비 단계를 건너뛰고 바로 요청합니다. DNS API 권한을 HAProxy 서버에 두지 않아도 되는 것이 장점입니다.
- 🟡 dns-persist-01은 IETF draft(`draft-ietf-acme-dns-persist`) 구현입니다. CA가 지원하는지 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 갱신 시점과 감시

HAProxy는 유효 기간의 **마지막 1/12**이 남았을 때 갱신을 시작합니다. Let's Encrypt는 ARI를 쓰거나, ARI가 없으면 수명의 약 2/3 시점(남은 기간 1/3)에 갱신하라고 권장합니다([인증서 수명 노트](../../_reference/tls_cert_lifecycle_official_notes.md)).

| 인증서 수명           | HAProxy 갱신 시작(만료 전) | 수명 2/3 시점 갱신(만료 전) |
|-----------------------|----------------------------|-----------------------------|
| 90일                  | 약 7.5일                   | 30일                        |
| 64일                  | 약 5.3일                   | 약 21일                     |
| 45일                  | 약 3.75일                  | 15일                        |
| 160시간(`shortlived`) | 약 13시간                  | 약 2.2일                    |

- 🟡 HAProxy 3.4 설정·관리 문서에는 ARI(renewalInfo) 지원이나 갱신 시점 조정 설정이 없습니다. 수명이 짧아질수록 갱신 실패를 고칠 여유가 줄어듭니다. Let's Encrypt 수명 단축 일정은 인증서 수명 노트에 정리되어 있습니다.
- 그래서 HAProxy 내장 ACME를 쓰면 **만료 감시를 따로** 둡니다. 경보 기준은 "HAProxy 갱신 시작 시점이 지났는데 만료일이 그대로"입니다.

```bash
# expires in 이 갱신 시작 시점(수명의 1/12)보다 작은데 만료일이 그대로면 갱신 실패
echo "@1 acme status" | sudo socat /run/haproxy-master.sock - | column -t -s $'\t'
```

외부 감시(blackbox_exporter, Zabbix)와 알림 기준은 [TLS 인증서 만료 감시](../../04_security/hardening/tls_certificate_expiry_monitoring.md)를 따릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 이중화 구성 주의

[Keepalived 이중화](./haproxy_keepalived_ha.md)처럼 HAProxy가 여러 대면 다음을 고려합니다. 공식 문서가 이 구성을 직접 다루지 않으므로, 아래는 위 동작 방식에서 추론한 주의점입니다.

| 문제                       | 원인                                                                          | 대안                                                            |
|----------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------|
| BACKUP 노드의 http-01 실패 | CA의 검증 요청은 VIP를 가진 MASTER로만 감. BACKUP의 token은 MASTER map에 없음 | BACKUP에서 발급하지 않음, 또는 DNS 방식                         |
| 노드마다 따로 발급         | 각 HAProxy가 자기 메모리의 인증서만 갱신                                      | 한 노드에서 발급·저장 후 다른 노드로 배포, 또는 외부 클라이언트 |
| 발급 횟수 제한             | 노드 수만큼 주문이 늘어남                                                     | 발급 노드를 하나로 제한                                         |

- 두 노드에서 모두 내장 ACME를 켜는 구성은 권장하지 않습니다. 이중화 구성에서는 [3절](#3-방식-선택)의 외부 클라이언트 방식이 단순합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 장애 사례

| 증상                             | 먼저 볼 것                                   | 흔한 원인                                                    |
|----------------------------------|----------------------------------------------|--------------------------------------------------------------|
| 설정 검사에서 `acme` 키워드 오류 | `global`                                     | `expose-experimental-directives` 없음, 3.2 미만 버전         |
| 시작 실패: 인증서 파일 없음      | 인증서 선언 위치                             | 3.2이거나 `crt-store` 대신 `ssl-f-use`·crt-list에만 선언     |
| http-01 검증 실패                | 외부에서 `/.well-known/acme-challenge/` 접근 | 80번 차단, 리다이렉트가 challenge 규칙보다 앞, DNS가 다른 곳 |
| reload 뒤 다시 발급, 횟수 제한   | `acme status`, 디스크 파일 날짜              | 저장 스크립트 미설정                                         |
| 브라우저 인증서 경고             | 발급자                                       | staging directory 그대로 사용                                |
| dns-01이 `Running`에서 멈춤      | `challenge-ready` 값                         | 기본 `cli`인데 준비 완료 알림을 보내는 도구가 없음           |
| 만료 임박인데 `Scheduled`        | 로그의 갱신 오류                             | CA 오류·네트워크 차단. 1/12 시점 이후라 여유가 적음          |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HAProxy 3.4 Configuration Manual 12.7 Certificate Storage, 12.8 ACME: [docs.haproxy.org/3.4/configuration.html](https://docs.haproxy.org/3.4/configuration.html) — ★★★☆☆
- HAProxy 3.4 Management Guide(`acme renew`, `acme status`, `dump ssl cert`): [docs.haproxy.org/3.4/management.html](https://docs.haproxy.org/3.4/management.html) — ★★★☆☆
- HAProxy wiki ACME 안내: [github.com/haproxy/wiki/wiki/ACME:--native-haproxy](https://github.com/haproxy/wiki/wiki/ACME:--native-haproxy) — ★★★☆☆
- haproxy-dump-certs 스크립트: [git.haproxy.org](https://git.haproxy.org/?p=haproxy-3.4.git;a=blob;f=admin/cli/haproxy-dump-certs) — ★★★☆☆
- 인증서 이름과 `crt-base`(`crtstore_parse_load`): [git.haproxy.org src/ssl_ckch.c](https://git.haproxy.org/?p=haproxy-3.4.git;a=blob;f=src/ssl_ckch.c) — ★★★☆☆
- Let's Encrypt 프로필(`shortlived` 160시간): [letsencrypt.org/docs/profiles](https://letsencrypt.org/docs/profiles/) — ★★★☆☆
- 확인 기록: [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy), [인증서 수명 노트](../../_reference/tls_cert_lifecycle_official_notes.md)
- 관련 문서: [HAProxy 운영 가이드](./haproxy_operations_guide.md), [HAProxy + Keepalived 이중화](./haproxy_keepalived_ha.md), [TLS 인증서 만료 감시](../../04_security/hardening/tls_certificate_expiry_monitoring.md)

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

**마지막 업데이트**: 2026-11-09

© 2026 siasia86. Licensed under CC BY 4.0.
