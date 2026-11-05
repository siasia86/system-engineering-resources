# TLS 인증서 만료 감시 가이드
<!-- reference: _reference/tls_cert_lifecycle_official_notes.md -->

## 목차

| 섹션                                                                                |
|-------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 감시 설계](#2-감시-설계)                                   |
| [3. openssl 수동 점검](#3-openssl-수동-점검) / [4. 점검 스크립트](#4-점검-스크립트) |
| [5. 모니터링 연동](#5-모니터링-연동) / [6. 갱신 자동화 점검](#6-갱신-자동화-점검)   |
| [7. 알림 기준](#7-알림-기준) / [8. 만료 장애 대응](#8-만료-장애-대응)               |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

인증서 만료는 원인이 단순하지만 서비스 전체를 멈추는 장애입니다. 갱신 자동화가 조용히 실패하거나, 디스크의 인증서는 바뀌었는데 서버가 다시 읽지 않았거나, 아무도 모르는 인증서가 남아 있을 때 생깁니다. 이 문서는 회사 운영 인프라에서 실제로 제공 중인 인증서를 관측하고, 갱신 자동화가 동작하는지 확인하는 방법을 다룹니다.

인증서 기본 구조와 발급은 [TLS/SSL 가이드](./tls_ssl_guide.md), 웹 서버의 TLS 설정 시험은 [TLS/HTTPS 테스트](../../01_fundamentals/cs/web_testing/tls_https_testing.md)에서 다룹니다.

### 왜 지금 감시를 다시 설계해야 하나

| 변화                                | 시점                  | 운영 영향                                     |
|-------------------------------------|-----------------------|-----------------------------------------------|
| 공개 TLS 인증서 최대 유효기간 200일 | 2026-03-15 발급분부터 | 1년짜리 수동 갱신 주기가 사라짐               |
| 최대 유효기간 100일                 | 2027-03-15 발급분부터 | 수동 갱신이 분기마다 필요                     |
| 최대 유효기간 47일                  | 2029-03-15 발급분부터 | 사실상 자동 갱신 필수                         |
| Let's Encrypt 만료 알림 메일 종료   | 2025-06-04            | CA가 알려 주지 않으므로 자체 감시 필요        |
| Let's Encrypt OCSP 종료(CRL만 제공) | 2025-08-06            | 폐기 확인 방식이 CRL로 바뀜                   |
| Let's Encrypt 기본 프로필 64일      | 2027-02-10            | 60일 고정 갱신 주기는 부족해짐                |
| Let's Encrypt 기본 프로필 45일      | 2028-02-16            | 갱신 실패를 알아챌 여유가 2주 안팎으로 줄어듦 |

공개 인증서의 유효기간 단축은 CA/Browser Forum TLS Baseline Requirements(Ballot SC-081v3, 2025-04-11 승인)에 정해져 있습니다. 같은 일정으로 도메인 검증 결과를 재사용할 수 있는 기간도 2029-03-15부터 10일로 줄어듭니다. 사내 CA로 발급한 인증서는 이 규칙을 따르지 않으므로 수명이 훨씬 긴 인증서가 섞여 있을 수 있습니다.

🟡 "만료 30일 전 알림" 하나로는 부족합니다. 수명이 짧아지면 정상인데도 경고가 계속 울리고, 수명이 긴 사내 인증서는 늦게 발견됩니다. 7절처럼 수명에 비례한 기준을 씁니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 감시 설계

### 두 층으로 감시

| 층          | 보는 것                                      | 놓치는 것                                  |
|-------------|----------------------------------------------|--------------------------------------------|
| 갱신 자동화 | ACME 클라이언트·cert-manager·ACM의 갱신 상태 | 갱신된 인증서를 서버가 다시 읽지 않은 경우 |
| 외부 관측   | 클라이언트가 실제로 받는 인증서              | 아직 서비스에 연결하지 않은 인증서         |

둘 중 하나만 두면 빈틈이 생깁니다. 갱신 자동화의 실패 알림과, 실제 접속으로 받은 인증서의 남은 기간을 함께 감시합니다.

### 감시 대상 목록

감시는 대상 목록이 있어야 시작할 수 있습니다. 다음을 모두 목록에 넣습니다.

| 대상                   | 예                                 | 주의                                     |
|------------------------|------------------------------------|------------------------------------------|
| 공개 웹·API            | `www`, `api`, 로그인 도메인        | 도메인마다 SNI가 다르면 각각 따로 점검   |
| 부하 분산기·CDN        | 클라우드 LB, CDN, WAF              | 원 서버와 다른 인증서를 쓰므로 각각 점검 |
| 내부 서비스            | 사내 관리 화면, DB·메시지 큐의 TLS | 사내 CA 묶음으로 검증                    |
| 메일·디렉터리 서비스   | SMTP·IMAP·LDAP의 STARTTLS          | 포트와 STARTTLS 프로토콜 지정            |
| mTLS 클라이언트 인증서 | 서비스 간 통신, 장비 인증서        | 서버 쪽 감시로는 보이지 않음             |
| 중간 CA·사내 루트 CA   | 사내 PKI                           | 만료되면 그 아래 인증서 전체가 실패      |
| Kubernetes·서비스 메시 | Ingress, webhook, 메시 내부 인증서 | 수명이 몇 시간~며칠인 경우가 많음        |

목록은 다음 자료를 대조해 만듭니다.

- 웹 서버·LB 설정 파일의 `server_name`·인증서 경로
- 클라우드 인증서 서비스 목록(예: AWS ACM `list-certificates`)
- 공개 인증서의 Certificate Transparency 로그(예: crt.sh에서 회사 도메인 검색). 공개 인증서는 모두 CT 로그에 남으므로 담당자가 모르는 인증서를 찾는 데 유용합니다.
- DNS 영역의 레코드

🟡 목록에는 담당 팀과 갱신 방식(자동·수동, 발급 CA)을 함께 적습니다. 알림이 와도 담당자를 모르면 대응이 늦어집니다.

[⬆ 목차로 돌아가기](#목차)

## 3. openssl 수동 점검

```bash
# 실제 제공 중인 인증서의 유효기간 (SNI 지정)
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# 호스트 이름 검증까지 포함한 결과 (Verify return code: 0 (ok)가 정상)
openssl s_client -connect app.example.com:443 -servername app.example.com \
  -verify_hostname app.example.com </dev/null 2>/dev/null \
  | grep "Verify return code"

# 체인 전체 확인 (중간 CA 만료 여부)
openssl s_client -connect app.example.com:443 -servername app.example.com -showcerts </dev/null 2>/dev/null \
  | awk '/BEGIN CERT/,/END CERT/' > chain.pem
openssl crl2pkcs7 -nocrl -certfile chain.pem | openssl pkcs7 -print_certs -noout

# STARTTLS (smtp, imap, pop3, ldap, postgres, mysql 등)
openssl s_client -connect mail.example.com:587 -starttls smtp </dev/null 2>/dev/null \
  | openssl x509 -noout -enddate

# 파일 인증서가 7일 안에 만료되는지 (만료 예정이면 종료 코드 1)
openssl x509 -in /etc/ssl/app/fullchain.pem -noout -checkend $((7 * 86400))
```

- `-servername`을 빼면 기본 인증서를 받아 엉뚱한 인증서를 점검할 수 있습니다. 한 IP에 여러 도메인이 있으면 반드시 지정합니다.
- `-verify_hostname`이 없으면 인증서가 다른 도메인용이어도 검증 결과가 정상으로 나올 수 있습니다.
- 사내 CA로 발급한 인증서는 `-CAfile <사내 CA 묶음>`을 추가해야 검증됩니다.
- 디스크의 파일과 실제 제공 인증서가 같은지는 지문으로 비교합니다(6절).

[⬆ 목차로 돌아가기](#목차)

## 4. 점검 스크립트

모니터링 시스템을 붙이기 전이나, 모니터링이 닿지 않는 망에서 쓸 수 있는 점검 스크립트입니다. 대상 파일을 읽어 실제 제공 인증서의 남은 일수와 검증 결과를 출력하고, 가장 나쁜 결과를 종료 코드로 돌려줍니다.

```bash
#!/usr/bin/env bash
# tls_expiry_check.sh - 대상 목록에서 실제 제공 중인 TLS 인증서의 남은 일수와 검증 결과 점검
# 사용: tls_expiry_check.sh <대상 파일> [경고 일수] [위험 일수]
# 대상 파일: 한 줄에 "host:port [SNI] [STARTTLS 프로토콜]", #으로 시작하면 주석
# 환경 변수: CA_FILE(사내 CA 묶음), TIMEOUT(초, 기본 10)
# 종료 코드: 0 정상, 1 경고, 2 위험·만료·검증 실패·연결 실패
set -u

TARGETS=${1:?"사용: $0 <대상 파일> [경고 일수] [위험 일수]"}
WARN_DAYS=${2:-30}
CRIT_DAYS=${3:-7}
TIMEOUT=${TIMEOUT:-10}
NOW=$(date +%s)
RC=0

raise() { (( $1 > RC )) && RC=$1; }

while read -r endpoint sni starttls _; do
    [[ -z "${endpoint:-}" || "${endpoint}" == \#* ]] && continue
    host=${endpoint%:*}
    sni=${sni:-$host}

    args=(-connect "${endpoint}" -servername "${sni}" -verify_hostname "${sni}" -showcerts)
    [[ -n "${starttls:-}" ]] && args+=(-starttls "${starttls}")
    [[ -n "${CA_FILE:-}" ]] && args+=(-CAfile "${CA_FILE}")

    out=$(timeout "${TIMEOUT}" openssl s_client "${args[@]}" </dev/null 2>/dev/null)
    leaf=$(printf '%s\n' "${out}" | sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/{p;/-----END CERTIFICATE-----/q}')
    if [[ -z "${leaf}" ]]; then
        printf 'CRIT\t%s\t%s\t-\t-\t연결 또는 handshake 실패\n' "${endpoint}" "${sni}"
        raise 2; continue
    fi

    not_after=$(printf '%s\n' "${leaf}" | openssl x509 -noout -enddate | cut -d= -f2)
    days=$(( ( $(date -d "${not_after}" +%s) - NOW ) / 86400 ))
    verify=$(printf '%s\n' "${out}" | sed -n 's/^ *Verify return code: //p' | tail -1)

    if [[ "${verify}" != 0* ]]; then
        status=CRIT; raise 2
    elif (( days < CRIT_DAYS )); then
        status=CRIT; raise 2
    elif (( days < WARN_DAYS )); then
        status=WARN; raise 1
    else
        status=OK
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${status}" "${endpoint}" "${sni}" "${days}" "${not_after}" "${verify}"
done < "${TARGETS}"

exit "${RC}"
```

```text
# targets.txt
app.example.com:443
203.0.113.10:443 api.example.com
mail.example.com:587 mail.example.com smtp
ldap.internal.example.com:389 ldap.internal.example.com ldap
```

```bash
CA_FILE=/etc/pki/internal-ca.pem ./tls_expiry_check.sh targets.txt 21 7
```

출력은 상태, 대상, SNI, 남은 일수, 만료 시각, 검증 결과 순서의 탭 구분 값입니다. 다음은 시험 환경 결과의 대상 이름만 예시 도메인으로 바꾼 것입니다.

```text
OK	app.example.com:443	app.example.com	24	Nov 30 02:11:50 2026 GMT	0 (ok)
WARN	203.0.113.10:443	api.example.com	19	Nov 25 02:11:51 2026 GMT	0 (ok)
CRIT	203.0.113.11:443	old.example.com	2	Nov  8 02:11:51 2026 GMT	0 (ok)
CRIT	203.0.113.10:443	www.example.com	24	Nov 30 02:11:50 2026 GMT	62 (hostname mismatch)
CRIT	203.0.113.12:443	down.example.com	-	-	연결 또는 handshake 실패
```

사내 CA를 `CA_FILE`로 지정하지 않으면 사내 인증서는 `21 (unable to verify the first certificate)`로 위험 판정됩니다.

- 남은 일수는 소수점을 버린 값입니다. 이 스크립트는 서버 인증서(leaf)만 판정하므로 중간 CA 만료는 3절의 체인 확인이나 5절의 blackbox_exporter로 봅니다.
- `date -d`는 GNU date 기준입니다. macOS·BSD에서는 `date -j -f` 형식으로 바꿔야 합니다.
- cron이나 systemd timer로 하루 한 번 이상 실행하고, 종료 코드가 0이 아니면 알림을 보냅니다. 실행 서버 자체가 멈추면 알림도 멈추므로 "점검이 실행되었다"는 신호도 함께 감시합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 모니터링 연동

### Prometheus blackbox_exporter

blackbox_exporter(v0.29.1 기준)는 HTTP·TCP 탐침으로 접속해 인증서 정보를 지표로 내보냅니다.

| 지표                                            | 의미                                                         |
|-------------------------------------------------|--------------------------------------------------------------|
| `probe_ssl_earliest_cert_expiry`                | 서버가 보낸 인증서 전체(중간 CA 포함) 중 가장 이른 만료 시각 |
| `probe_ssl_last_chain_expiry_timestamp_seconds` | 검증된 체인들 중 가장 늦게 끝나는 체인의 만료 시각           |
| `probe_ssl_last_chain_info`                     | 서버 인증서의 subject·issuer·SAN·지문 등 정보                |
| `probe_tls_version_info`                        | 협상된 TLS 버전                                              |
| `probe_success`                                 | 탐침 성공 여부(인증서 검증 실패도 실패)                      |

```yaml
# blackbox.yml
modules:
  https_cert:
    prober: http
    timeout: 10s
    http:
      method: GET
      fail_if_not_ssl: true
      preferred_ip_protocol: ip4
  tls_tcp:
    prober: tcp
    timeout: 10s
    tcp:
      tls: true
      tls_config:
        ca_file: /etc/blackbox/internal-ca.pem
  smtp_starttls:
    prober: tcp
    timeout: 10s
    tcp:
      query_response:
        - expect: "^220 "
        - send: "EHLO prober\r"
        - expect: "^250-STARTTLS"
        - send: "STARTTLS\r"
        - expect: "^220"
        - starttls: true
        - send: "QUIT\r"
```

```yaml
# Prometheus 알림 규칙
groups:
  - name: tls-certificates
    rules:
      - alert: TLSCertificateExpiringSoon
        expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 21
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }} 인증서 만료 {{ $value | humanize }}일 전"
      - alert: TLSCertificateExpiryCritical
        expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 7
        for: 10m
        labels:
          severity: critical
      - alert: TLSProbeFailed
        expr: probe_success{job=~"blackbox.*"} == 0
        for: 10m
        labels:
          severity: critical
```

- 기본 설정은 인증서 검증을 하므로, 검증 실패(다른 도메인·신뢰하지 않는 CA·만료)는 `probe_success == 0`으로 나타납니다. `insecure_skip_verify: true`를 쓰면 이 신호가 사라지므로 감시 모듈에는 쓰지 않습니다.
- `probe_ssl_earliest_cert_expiry`는 중간 CA까지 포함하므로 중간 CA 만료도 잡습니다. 도움말 문구는 "last SSL chain expiry"라고 되어 있지만 소스 기준 계산은 서버가 보낸 인증서 중 가장 이른 만료입니다.
- 탐침 대상 설정과 relabel은 [Prometheus·Grafana 문서](../../02_infrastructure/monitoring/prometheus_grafana.md)의 Blackbox Exporter 절을 따릅니다.
- `http`·`tcp` 탐침에서 `check_revoked: true`를 켜면 CRL로 폐기 여부를 `probe_ssl_crl_*` 지표로 내보냅니다(탐침 실패로 처리하지 않으므로 지표로 알림).

### Zabbix

Zabbix agent 2의 `web.certificate.get` 키와 공식 템플릿 "Website certificate by Zabbix agent 2"를 씁니다(Zabbix 7.0 이상).

| 매크로                     | 기본값 | 설명                               |
|----------------------------|--------|------------------------------------|
| `{$CERT.WEBSITE.HOSTNAME}` | 없음   | 점검할 DNS 이름(필수)              |
| `{$CERT.WEBSITE.PORT}`     | `443`  | TLS 포트                           |
| `{$CERT.WEBSITE.IP}`       | 없음   | 접속할 IP(DNS와 다른 경로를 볼 때) |
| `{$CERT.EXPIRY.WARN}`      | `7`    | 만료 경고 일수                     |

```bash
# agent 2에서 직접 확인
zabbix_get -s <agent 주소> -k 'web.certificate.get[app.example.com,443]'
```

- 템플릿 트리거: 인증서 무효(만료·다른 도메인, High), 만료 임박(`{$CERT.EXPIRY.WARN}`일 미만, Warning), 지문 변경(수동 종료).
- 기본 경고 7일은 짧습니다. 7절 기준에 맞춰 `{$CERT.EXPIRY.WARN}`을 올리고, 위험 단계가 필요하면 같은 항목으로 트리거를 하나 더 만듭니다.
- 7.4 템플릿은 매크로에 쉼표로 여러 호스트를 넣어 한 호스트에서 여러 사이트를 점검할 수 있습니다. 7.0 템플릿은 사이트 하나씩 연결합니다.
- 지문 변경 트리거는 정상 갱신 때마다 울리므로 짧은 수명 인증서에서는 끄거나, 갱신 기록과 대조하는 용도로만 씁니다.

### Kubernetes cert-manager

cert-manager(v1.21.3 기준)는 Certificate 리소스마다 다음 지표를 내보냅니다.

| 지표                                                   | 의미               |
|--------------------------------------------------------|--------------------|
| `certmanager_certificate_expiration_timestamp_seconds` | 인증서 만료 시각   |
| `certmanager_certificate_renewal_timestamp_seconds`    | 갱신을 시도할 시각 |
| `certmanager_certificate_ready_status`                 | Ready 조건 상태    |

```yaml
- alert: CertManagerRenewalOverdue
  # 갱신 예정 시각이 하루 넘게 지났는데 아직 갱신되지 않음
  expr: time() > certmanager_certificate_renewal_timestamp_seconds + 86400
  for: 1h
  labels:
    severity: warning
- alert: CertManagerCertificateNotReady
  expr: certmanager_certificate_ready_status{condition="False"} == 1
  for: 30m
  labels:
    severity: critical
```

- 기본 갱신 시점은 수명의 2/3입니다. `spec.renewBefore`(절대 시간)보다 `spec.renewBeforePercentage`(비율)를 권장합니다. 발급 CA가 수명을 줄여도 갱신 반복에 빠지지 않습니다.
- cert-manager 지표는 갱신 자동화 층입니다. Ingress가 실제로 새 인증서를 제공하는지는 blackbox_exporter로 따로 봅니다.

### AWS Certificate Manager

| 수단                                                  | 내용                                                                                                  |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| CloudWatch 지표 `DaysToExpiry`                        | 네임스페이스 `AWS/CertificateManager`, 차원 `CertificateArn`, 하루 두 번 발행                         |
| EventBridge `ACM Certificate Approaching Expiration`  | 공개 인증서는 30일 전, 사설·가져온 인증서는 45일 전부터 매일 발행(`PutAccountConfiguration`으로 변경) |
| EventBridge `ACM Certificate Renewal Action Required` | 자동 갱신이 막혔을 때(CAA 오류, 도메인 검증 대기 등). 가져온 인증서는 해당 없음                       |
| EventBridge `ACM Certificate Expired`                 | ACM이 발급한 인증서 만료. 가져온 인증서는 해당 없음                                                   |

- ACM이 발급한 인증서는 자동 갱신되지만, 가져온(imported) 인증서는 사람이 다시 가져와야 합니다. 가져온 인증서는 `DaysToExpiry` 경보를 반드시 둡니다.
- DNS 검증 인증서는 검증용 CNAME을 지우면 자동 갱신이 실패합니다. Renewal Action Required 이벤트를 알림으로 연결합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 갱신 자동화 점검

### ACME 클라이언트

- **고정 주기 대신 ARI 사용:** ACME Renewal Information(ARI, RFC 9773)은 CA가 인증서마다 권장 갱신 구간을 알려 주는 표준입니다. 대량 폐기 같은 사고 때 CA가 조기 갱신을 요청할 수 있습니다. certbot은 4.1.0부터 `certbot renew`에서 ARI를 자동으로 확인합니다. 다른 클라이언트는 지원 여부와 설정을 확인합니다.
- **ARI가 없으면 수명의 2/3:** Let's Encrypt는 ARI를 쓰지 않는 경우 수명의 약 2/3 시점에 갱신하라고 안내하며, 60일 고정 갱신은 45일 인증서에서 동작하지 않는다고 밝혔습니다.
- **실행 주기:** 갱신 판단은 클라이언트가 하므로 갱신 명령 자체는 하루 두 번처럼 자주 실행해도 됩니다.
- **실패 신호:** 갱신 명령의 종료 코드와 로그를 수집하고, 실패하면 바로 알립니다. 만료 알림을 기다리면 대응 시간이 줄어듭니다.

### 다시 읽기(reload) 확인

갱신 장애에서 가장 흔한 형태는 "파일은 새것인데 서버는 옛 인증서를 제공"하는 경우입니다.

```bash
# 디스크의 인증서와 실제 제공 인증서의 지문 비교
DISK=$(openssl x509 -in /etc/ssl/app/fullchain.pem -noout -fingerprint -sha256)
LIVE=$(openssl s_client -connect 127.0.0.1:443 -servername app.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -fingerprint -sha256)
[ "${DISK}" = "${LIVE}" ] && echo "일치" || echo "불일치: 서버 reload 필요"
```

- 갱신 후 hook(certbot의 `--deploy-hook` 등)에서 서버를 다시 읽게 하고, 위 비교로 결과를 확인합니다.
- 부하 분산기 뒤에 서버가 여러 대면 각 서버에 직접 접속해 비교합니다. 일부 서버만 옛 인증서를 내면 간헐 장애가 됩니다.
- 인증서를 다른 곳(LB, CDN, 다른 서버)에 복사해 쓰는 경우 복사 단계가 갱신 자동화에 포함되어 있는지 확인합니다.

### 수동 발급 인증서

유료 CA에서 수동으로 발급받는 인증서는 2026-03-15 이후 최대 200일, 2027-03-15 이후 100일이 됩니다. 갱신 횟수가 늘어나므로 ACME를 지원하는 CA로 옮기거나, 발급부터 배포까지의 절차를 문서화하고 담당자를 둘 이상 지정합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 알림 기준

경고는 "정상이면 이미 갱신되었어야 할 시점"에 울리도록 수명에 맞춰 정합니다. 자동 갱신이 수명의 2/3에 일어나면 남은 기간이 1/3 아래로 내려간 인증서는 갱신이 실패한 것입니다.

| 인증서 수명       | 자동 갱신 예정(남은 기간) | 경고(남은 기간) | 위험(남은 기간) |
|-------------------|---------------------------|-----------------|-----------------|
| 200일(수동 발급)  | 해당 없음                 | 30일            | 14일            |
| 90일              | 30일                      | 21일            | 7일             |
| 64일              | 약 21일                   | 14일            | 5일             |
| 45~47일           | 약 15일                   | 10일            | 3일             |
| 6일(단기 인증서)  | 2일                       | 1일             | 12시간          |
| 사내 CA(1년 이상) | 조직 기준                 | 60일            | 30일            |

- 수명이 다른 인증서가 섞여 있으면 하나의 일수 기준으로 묶지 말고 대상 그룹별로 기준을 나눕니다. 모니터링 시스템에서 대상에 수명 그룹 라벨을 붙이는 방식이 관리하기 쉽습니다.
- 경고는 담당 팀 채널로, 위험과 탐침 실패는 당직 호출로 보냅니다.
- 위의 경고·위험 값은 갱신 실패를 알아채고 고칠 시간을 기준으로 잡은 권장값입니다. 조직의 대응 시간과 변경 절차에 맞춰 조정합니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 만료 장애 대응

1. **범위 확인:** 만료된 인증서를 쓰는 도메인·서버·LB를 대상 목록과 `probe_ssl_last_chain_info`의 SAN으로 찾습니다.
2. **즉시 재발급:** ACME면 수동으로 갱신을 실행하고 오류를 확인합니다. 도메인 검증 실패면 DNS·HTTP 검증 경로를 먼저 고칩니다. 발급 한도에 걸릴 수 있으므로 같은 명령을 반복하기 전에 원인을 봅니다.
3. **배포와 다시 읽기:** 모든 서버·LB·CDN에 배포하고 6절의 지문 비교로 확인합니다.
4. **외부 확인:** 3절 명령이나 점검 스크립트로 실제 제공 인증서를 다시 봅니다. 브라우저·클라이언트 캐시 때문에 사용자 쪽 오류가 잠시 남을 수 있습니다.
5. **재발 방지:** 갱신 자동화가 왜 실패했는지, 왜 알림이 늦었는지 기록하고 감시 기준(7절)과 대상 목록(2절)을 고칩니다.

🟡 개인키가 노출된 경우는 만료 대응이 아니라 폐기·재발급 대응입니다. CA에 폐기를 요청하고 새 키로 발급합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- CA/Browser Forum TLS Baseline Requirements: [github.com/cabforum/servercert](https://github.com/cabforum/servercert/blob/main/docs/BR.md) — ★★★★★
- CA/Browser Forum Ballot SC-081v3: [cabforum.org](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/) — ★★★★★
- Let's Encrypt, Decreasing Certificate Lifetimes to 45 Days: [letsencrypt.org](https://letsencrypt.org/2025/12/02/from-90-to-45) — ★★★★☆
- Let's Encrypt, Ending Expiration Emails: [letsencrypt.org](https://letsencrypt.org/2025/01/22/ending-expiration-emails/) — ★★★★☆
- RFC 9773 ACME Renewal Information: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9773.html) — ★★★★★
- blackbox_exporter: [github.com/prometheus/blackbox_exporter](https://github.com/prometheus/blackbox_exporter) — ★★★★☆
- Zabbix 템플릿 Website certificate by Zabbix agent 2: [git.zabbix.com](https://git.zabbix.com/projects/ZBX/repos/zabbix/browse/templates/app/certificate_agent2) — ★★★★☆
- cert-manager Certificate: [cert-manager.io](https://cert-manager.io/docs/usage/certificate/) — ★★★★☆
- AWS ACM EventBridge 이벤트: [docs.aws.amazon.com](https://docs.aws.amazon.com/acm/latest/userguide/supported-events.html) — ★★★★☆
- 확인 기록: [TLS 인증서 수명 주기 참조 노트](../../_reference/tls_cert_lifecycle_official_notes.md)
- 관련 문서: [TLS/SSL 가이드](./tls_ssl_guide.md), [Trivy 가이드](./trivy_guide.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-05

**마지막 업데이트**: 2026-11-05

© 2026 siasia86. Licensed under CC BY 4.0.
