---
name: tls-cert-lifecycle-official-notes
description: 공개 TLS 인증서 유효기간 단축, Let's Encrypt 수명·알림·OCSP 변경, ACME ARI, blackbox_exporter·Zabbix·cert-manager·AWS ACM 만료 감시 수단의 공식 근거 노트.
tags:
  - tls
  - certificate
  - monitoring
  - acme
last_checked: 2026-11-09
sources:
  - https://github.com/cabforum/servercert/blob/main/docs/BR.md
  - https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/
  - https://letsencrypt.org/2025/12/02/from-90-to-45
  - https://letsencrypt.org/2025/01/22/ending-expiration-emails/
  - https://letsencrypt.org/2025/06/26/expiration-notification-service-has-ended
  - https://letsencrypt.org/docs/profiles/
  - https://letsencrypt.org/2024/12/05/ending-ocsp
  - https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life
  - https://www.rfc-editor.org/rfc/rfc9773.html
  - https://github.com/certbot/certbot/blob/main/certbot/CHANGELOG.md
  - https://github.com/prometheus/blackbox_exporter/tree/v0.29.1
  - https://git.zabbix.com/projects/ZBX/repos/zabbix/browse/templates/app/certificate_agent2
  - https://cert-manager.io/docs/usage/certificate/
  - https://github.com/cert-manager/cert-manager/blob/v1.21.3/internal/collectors/certificate_collector.go
  - https://docs.aws.amazon.com/acm/latest/userguide/supported-events.html
  - https://docs.aws.amazon.com/acm/latest/userguide/cloudwatch-metrics.html
---

# TLS Certificate Lifecycle Official Notes

## 1. 공개 인증서 유효기간 (CA/Browser Forum)

TLS Baseline Requirements v2.3.1(2026-10-04) 원문 6.3.2·4.2.1 표를 직접 확인했습니다. Ballot SC-081v3는 2025-04-11 승인되었습니다.

| 발급일                  | 최대 유효기간 | 도메인·IP 검증 재사용 |
|-------------------------|---------------|-----------------------|
| 2026-03-15 이전         | 398일         | 398일                 |
| 2026-03-15 ~ 2027-03-15 | 200일         | 200일                 |
| 2027-03-15 ~ 2029-03-15 | 100일         | 100일                 |
| 2029-03-15 이후         | 47일          | 10일                  |

도메인 외 검증 정보(조직 정보 등)의 재사용 기간은 2026-03-15부터 825일에서 398일로 줄었습니다.

## 2. Let's Encrypt

- 수명 단축(2025-12-02 공지): 현재 90일·인증 재사용 30일. 2026-05-13 `tlsserver` 프로필(선택) 45일, 2027-02-10 기본 `classic` 프로필 64일·인증 재사용 10일, 2028-02-16 `classic` 45일·인증 재사용 7시간. staging은 약 한 달 먼저 바뀝니다. 6일짜리 `shortlived` 프로필이 따로 있습니다(공지 표현, 프로필 문서의 유효기간은 160시간).
- 갱신 권장: ARI 사용. ARI가 없으면 수명의 약 2/3 시점에 갱신하며, 60일 고정 갱신은 충분하지 않다고 명시했습니다. 수동 갱신은 권장하지 않고 갱신 실패 알림을 두라고 안내합니다. DNS TXT 레코드를 매번 바꾸지 않는 DNS-PERSIST-01은 2026년 도입 예정으로 소개되었습니다.
- 만료 알림 메일: 2025-01-22 종료를 공지했고 2025-06-04 서비스를 끝냈습니다. ACME API로 받은 메일 주소는 삭제했습니다.
- OCSP: 2024-12-05 공지대로 2025-05-07 인증서에서 OCSP URL을 빼고 2025-08-06 OCSP 응답 서버를 껐으며, 폐기 정보는 CRL로만 제공합니다(2026-11-09 공지 원문 두 건 확인).

## 3. ACME Renewal Information (RFC 9773)

- 2025-06 Standards Track. 서버가 directory에 `renewalInfo` URL을 두고, 클라이언트는 인증서의 Authority Key Identifier와 일련번호로 만든 경로를 인증 없이 GET합니다.
- 응답의 `suggestedWindow`(`start`, `end`)에서 무작위 시점을 골라 갱신하고 `Retry-After` 간격으로 다시 확인합니다. 일시 오류는 지수 백오프, 지속 오류는 약 6시간 뒤 재시도를 권장합니다.
- certbot 4.1.0(2025-06-10)부터 `certbot renew`가 ARI를 자동 확인합니다. 최신 릴리스는 v5.9.0(2026-10-29)입니다.

## 4. 감시 도구

- blackbox_exporter v0.29.1(2026-10-21): `prober/tls.go`에서 `probe_ssl_earliest_cert_expiry`는 `PeerCertificates` 전체 중 가장 이른 `NotAfter`, `probe_ssl_last_chain_expiry_timestamp_seconds`는 `VerifiedChains`별 가장 이른 만료 중 가장 늦은 값입니다. 두 지표의 도움말 문구는 "Returns last SSL chain expiry ..."로 계산 방식과 다릅니다. 그 밖에 `probe_ssl_last_chain_info`, `probe_tls_version_info`, `probe_tls_cipher_info`가 있습니다. `check_revoked`(기본 false)는 CRL을 확인해 `probe_ssl_crl_revoked`·`probe_ssl_crl_stale`·`probe_ssl_crl_available`·`probe_ssl_crl_next_update_timestamp_seconds`·`probe_ssl_crl_fetch_time_seconds`를 내보내며 탐침 실패로 처리하지 않습니다. 공식 `example.yml`에 `smtp_starttls` 모듈 예시가 있습니다.
- Zabbix: 템플릿 "Website certificate by Zabbix agent 2", agent 2의 `web.certificate.get` 키. 7.0 README는 Zabbix 7.0 이상(사이트 하나), 7.4 README는 7.4 이상이며 매크로에 쉼표로 여러 사이트를 넣습니다. `{$CERT.EXPIRY.WARN}` 기본 7, `{$CERT.WEBSITE.PORT}` 기본 443. 트리거는 무효(High), 만료 임박(Warning), 지문 변경(수동 종료).
- cert-manager v1.21.3(2026-10-23): `certmanager_certificate_expiration_timestamp_seconds`, `certmanager_certificate_renewal_timestamp_seconds`, `certmanager_certificate_not_after_timestamp_seconds`, `certmanager_certificate_not_before_timestamp_seconds`, `certmanager_certificate_ready_status`. 기본 갱신 시점은 수명의 2/3이고 `spec.renewBeforePercentage`를 권장합니다. 기본 `spec.duration`은 90일이며 `spec.renewal`로 갱신 허용 시간대를 정할 수 있습니다.
- AWS ACM: CloudWatch `AWS/CertificateManager`의 `DaysToExpiry`(차원 `CertificateArn`, 하루 두 번 발행, 만료 후 중단). EventBridge `ACM Certificate Approaching Expiration`은 공개 인증서 30일 전, 사설·가져온 인증서 45일 전부터 매일 발행하며 `PutAccountConfiguration`으로 바꿉니다. `ACM Certificate Expired`와 `ACM Certificate Renewal Action Required`는 가져온 인증서에 발행되지 않습니다. 갱신 막힘 이벤트는 공개 30일·사설 45일 전 실패 시 발행되고 이후 재시도마다 발행됩니다.

## 5. 로컬 확인 (2026-11-05, OpenSSL 3.0.13)

- 가이드 4절 스크립트를 스크래치 폴더의 임시 CA·인증서(25·20·3일)와 localhost `openssl s_server`로 시험했습니다. 정상·경고·위험, 호스트 이름 불일치(`62 (hostname mismatch)`), 사내 CA 미지정(`21 (unable to verify the first certificate)`), 연결 실패가 의도대로 판정되었고 종료 코드는 최악 결과(2)와 정상(0)이 맞았습니다.
- `openssl x509 -checkend`는 기간 안 만료면 1, 아니면 0을 반환했습니다. 지문 비교와 체인 출력 명령도 같은 환경에서 동작했습니다.
- STARTTLS 대상, blackbox_exporter·Zabbix·cert-manager·ACM 설정과 알림 규칙은 실행하지 않았습니다.
