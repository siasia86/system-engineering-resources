---
name: email-authentication-official-notes
description: SPF·DKIM·DMARC(RFC 9989 개정)·그레이 리스트 기준 RFC, 구현 판과 Postfix 컨테이너 확인 결과 정리.
tags:
  - email
  - spf
  - dkim
  - dmarc
  - greylisting
  - rfc
last_checked: 2026-11-24
sources:
  - https://www.rfc-editor.org/rfc/rfc7208
  - https://www.rfc-editor.org/rfc/rfc6376
  - https://www.rfc-editor.org/rfc/rfc8301
  - https://www.rfc-editor.org/rfc/rfc8463
  - https://www.rfc-editor.org/rfc/rfc9989
  - https://www.rfc-editor.org/rfc/rfc9990
  - https://www.rfc-editor.org/rfc/rfc9991
  - https://www.rfc-editor.org/rfc/rfc7489
  - https://www.rfc-editor.org/rfc/rfc6647
  - https://www.rfc-editor.org/rfc-index.txt
---

# 메일 인증 공식 자료 참조 노트

## 1. 기준 RFC (rfc-index.txt, 2026-11-24)

| RFC  | 발행    | 제목                                                                    | 관계·상태                                              |
|------|---------|-------------------------------------------------------------------------|--------------------------------------------------------|
| 7208 | 2014-04 | Sender Policy Framework (SPF) ... Version 1                             | RFC 4408 대체, Proposed Standard                       |
| 6376 | 2011-09 | DomainKeys Identified Mail (DKIM) Signatures                            | STD 76, 8301·8463 등이 갱신                            |
| 8301 | 2018-01 | Cryptographic Algorithm and Key Usage Update to DKIM                    | `rsa-sha1` 서명 금지, RSA 1024비트 이상 필수·2048 권장 |
| 8463 | 2018-09 | A New Cryptographic Signature Method for DKIM                           | `ed25519-sha256` 추가                                  |
| 9989 | 2026-05 | Domain-Based Message Authentication, Reporting, and Conformance (DMARC) | RFC 7489·9091 대체, Proposed Standard                  |
| 9990 | 2026-05 | DMARC Aggregate Reporting                                               | RFC 7489 대체 (집계 보고 `rua`)                        |
| 9991 | 2026-05 | DMARC Failure Reporting                                                 | RFC 7489 대체, RFC 6591 갱신 (실패 보고 `ruf`)         |
| 7489 | 2015-03 | DMARC (이전 판)                                                         | Informational, 9989~9991로 대체됨                      |
| 6647 | 2012-06 | Email Greylisting: An Applicability Statement for SMTP                  | Proposed Standard                                      |

## 2. 원문에서 확인한 규칙

- SPF (RFC 7208 4.6.4): DNS 조회가 필요한 메커니즘·수정자(`include`, `a`, `mx`, `ptr`, `exists`, `redirect`)는 합쳐서 10개까지이고, 넘으면 `permerror`입니다. 응답이 없는 조회(void lookup)는 2회로 제한할 것을 권고합니다.
- DKIM (RFC 8301): `rsa-sha1`은 서명에 쓰면 안 되고, 서명자는 RSA 1024비트 이상을 써야 하며 2048비트 이상을 권장합니다.
- DMARC (RFC 9989):
  - `p`는 권장(RECOMMENDED) 태그가 되었고, 없으면 `p=none`으로 취급합니다(RFC 7489에서는 필수).
  - `adkim`, `aspf` 기본값은 `r`(relaxed).
  - 정의된 태그: `v`, `p`, `sp`, `np`, `psd`, `t`, `adkim`, `aspf`, `rua`, `ruf`, `fo`.
  - `pct`, `rf`, `ri`는 IANA 등록부에서 `historic`(부록 C.5.2 Tags Removed). `t=y`가 `pct`의 일부 기능을 대신하며, 정책을 한 단계 낮춰 적용하라는 요청입니다(`reject` → `quarantine`, `quarantine` → `none`).
  - 조직 도메인과 정책 레코드는 공개 접미사 목록(PSL) 대신 DNS Tree Walk(4.10절)로 찾고, 조회는 최대 8회입니다.
- DMARC 보고 (RFC 9990): `rua` 주소의 도메인이 정책 도메인과 다르면, 받는 쪽이 `<정책 도메인>._report._dmarc.<받는 도메인>`에 `v=DMARC1` TXT를 둬야 보고서를 보냅니다.

## 3. 구현 판 (Debian 13 패키지, 2026-11-24)

| 구현                       | 판           | 비고                                       |
|----------------------------|--------------|--------------------------------------------|
| OpenDKIM                   | 2.11.0~beta2 | 서명·검증 밀터, `opendkim-genkey`          |
| OpenDMARC                  | 1.4.2        | RFC 9989 이전 구현(RFC 7489 기준)          |
| postfix-policyd-spf-python | 3.1.0        | Postfix SPF 정책 서비스, pyspf 2.0.14 사용 |
| postgrey                   | 1.37         | 그레이 리스트 정책 서비스                  |
| dkimpy (`dkimverify`)      | 1.1.8        | 검증 확인용                                |

## 4. 컨테이너 시험 (2026-11-24)

구성: Debian 13 컨테이너 3개. `dns`(unbound 로컬 영역 `example.test`: MX, `v=spf1 mx -all`, DKIM 선택자 `s1` RSA 2048, `_dmarc` `p=reject; adkim=s; aspf=s`), `mx`(Postfix 3.10.13 + OpenDKIM + OpenDMARC + policyd-spf + postgrey `--delay=15`), `client`(swaks).

| 확인                                             | 결과                                                                                      |
|--------------------------------------------------|-------------------------------------------------------------------------------------------|
| pyspf: mx 주소, `alice@example.test`             | `pass`                                                                                    |
| pyspf: client 주소, `alice@example.test`         | `fail`                                                                                    |
| pyspf: client 주소, SPF 없는 도메인              | `none`                                                                                    |
| 587 인증 발송 메일 헤더                          | `DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/simple; d=example.test; s=s1`               |
| `dkimverify` 원본                                | `signature ok`                                                                            |
| `dkimverify` 본문 한 글자 변경                   | `body hash mismatch`                                                                      |
| 25번, 봉투 발신자 위조 (`alice@example.test`)    | `550 5.7.23 ... SPF fail - not authorized`                                                |
| 25번, 정상 외부 발신 첫 시도·즉시 재시도         | `450 4.2.0 ... Greylisted`                                                                |
| 같은 발신 17초 뒤                                | `250 2.0.0`, 헤더 `X-Greylist: delayed 18 seconds by postgrey-1.37`                       |
| 받아들인 메일 헤더                               | `Received-SPF: None`, `Authentication-Results: ... dmarc=none ... header.from=other.test` |
| 25번, 봉투는 외부·헤더 From만 `ceo@example.test` | 그레이 리스트 통과 뒤 `550 5.7.1 rejected by DMARC policy for example.test`               |
| `opendkim-testkey` (시험 DNS)                    | `record not found` (원인 미확인, 같은 레코드를 `dig`·`dkimverify`는 찾음)                 |

- Debian의 opendkim은 libunbound를 링크하며, 이 시험 구성에서는 `Nameservers` 설정으로도 `opendkim-testkey`가 로컬 영역을 찾지 못했습니다. 실제 공개 DNS에서는 확인하지 않았습니다.
- postgrey 기동 때 Perl 경고(`IO::Multiplex` import)가 한 줄 나왔으나 동작에는 영향이 없었습니다.
- OpenDMARC 1.4.2는 RFC 7489 기준이라 `t` 태그와 DNS Tree Walk는 시험하지 않았습니다.
