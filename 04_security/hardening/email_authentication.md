# 메일 인증 (SPF · DKIM · DMARC)
<!-- reference: _reference/email_authentication_official_notes.md -->

내 도메인을 사칭한 메일을 막고, 내가 보낸 메일이 받는 쪽에서 정상으로 판정되게 하는 세 가지 DNS 기반 인증(SPF, DKIM, DMARC)과 수신 서버의 화이트·그레이 리스트를 정리한 문서입니다. 이 문서만으로 원리 이해 → DNS 레코드 작성 → Postfix에 서명·검사 적용 → 정책 단계적 강화 → 검증까지 따라 할 수 있게 썼습니다.

- 기준: RFC 7208(SPF), 6376·8301·8463(DKIM), 9989·9990·9991(DMARC, 2026-05 발행으로 RFC 7489 대체), 6647(그레이 리스트). 2026-11-24 확인
- 예제 시험: 2026-11-24 Debian 13 컨테이너(Postfix 3.10.13, OpenDKIM 2.11.0, OpenDMARC 1.4.2, postfix-policyd-spf-python 3.1.0, postgrey 1.37)와 로컬 DNS(unbound)로 5·6·7절 실행. 공개 DNS·실제 메일 사업자 수신 판정은 미실행

## 목차

| 섹션                                                                                         |
|----------------------------------------------------------------------------------------------|
| [1. 세 가지가 확인하는 것](#1-세-가지가-확인하는-것) / [2. SPF](#2-spf) / [3. DKIM](#3-dkim) |
| [4. DMARC](#4-dmarc) / [5. 받는 서버에 적용 (Postfix)](#5-받는-서버에-적용-postfix)          |
| [6. 화이트 리스트와 그레이 리스트](#6-화이트-리스트와-그레이-리스트) / [7. 검증](#7-검증)    |
| [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)           |

---

## 1. 세 가지가 확인하는 것

메일에는 주소가 두 군데 있습니다. SMTP 봉투의 `MAIL FROM`(반송 주소)과 사용자에게 보이는 헤더 `From:`입니다. 위조는 주로 헤더 `From:`을 바꿉니다.

| 항목  | 확인하는 것                                                              | 기준 주소                      | 발신 도메인이 DNS에 올리는 것     |
|-------|--------------------------------------------------------------------------|--------------------------------|-----------------------------------|
| SPF   | 이 IP가 그 도메인의 메일을 보내도 되는가                                 | 봉투 `MAIL FROM` (없으면 HELO) | 허용 IP 목록 TXT                  |
| DKIM  | 메일이 서명 뒤 바뀌지 않았고, 서명한 도메인은 어디인가                   | 서명의 `d=` 도메인             | 공개 키 TXT (`선택자._domainkey`) |
| DMARC | SPF나 DKIM이 헤더 `From:` 도메인과 맞게 통과했는가, 실패하면 어떻게 할까 | 헤더 `From:`                   | 정책 TXT (`_dmarc`)               |

```text
수신 서버 판정 순서

  MAIL FROM, 접속 IP ──> SPF 검사 ──> pass/fail ──┐
                                                   ├─> DMARC: 통과한 쪽의 도메인이
  DKIM-Signature    ──> DKIM 검증 ──> pass/fail ──┘    헤더 From 도메인과 맞는가(정렬)
                                                        │
                                       맞는 것이 하나라도 있으면 pass
                                       없으면 _dmarc 정책(p=none/quarantine/reject) 적용
```

- SPF·DKIM만으로는 헤더 `From:` 위조를 막지 못합니다. 공격자가 자기 도메인으로 SPF·DKIM을 통과시키고 `From:`만 바꿀 수 있기 때문입니다. DMARC의 정렬(alignment) 검사가 이것을 막습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. SPF

도메인의 메일을 보낼 수 있는 서버를 TXT 레코드로 공개합니다.

```text
example.com.   IN TXT "v=spf1 mx ip4:192.0.2.10 include:_spf.mail-provider.example -all"
```

| 요소           | 뜻                                                    |
|----------------|-------------------------------------------------------|
| `v=spf1`       | SPF 레코드 표시 (도메인당 하나만, 둘이면 `permerror`) |
| `ip4:`, `ip6:` | 허용할 주소·대역                                      |
| `a`, `mx`      | 그 도메인의 A·MX 레코드가 가리키는 주소               |
| `include:`     | 다른 도메인의 SPF를 포함 (메일 대행 서비스 등)        |
| `-all`         | 위에 없으면 `fail` (권장 최종값)                      |
| `~all`         | 위에 없으면 `softfail` (도입·전환 기간)               |
| `?all`         | 판단 없음 (`neutral`)                                 |

- DNS 조회가 필요한 항목(`include`, `a`, `mx`, `ptr`, `exists`, `redirect`)은 합쳐서 10개까지입니다. 넘으면 `permerror`로 SPF가 통째로 실패합니다. 대행 서비스를 여러 개 `include`하면 쉽게 넘으니 개수를 세어 봅니다.
- 메일을 보내지 않는 도메인은 `v=spf1 -all`을 둬서 사칭을 막습니다.
- 전달(forwarding)된 메일은 전달 서버의 IP로 다시 보내지므로 SPF가 실패합니다. 이때는 DKIM이 DMARC를 통과시킵니다.

```bash
dig +short TXT example.com | grep spf1
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. DKIM

보내는 서버가 메일 헤더와 본문에 개인 키로 서명하고, 받는 서버는 DNS의 공개 키로 검증합니다.

### 3.1 키 만들기와 DNS 등록

```bash
sudo opendkim-genkey -b 2048 -d example.com -s s1 -D /etc/opendkim/keys
sudo chown opendkim:opendkim /etc/opendkim/keys/s1.private
sudo chmod 600 /etc/opendkim/keys/s1.private
sudo cat /etc/opendkim/keys/s1.txt     # DNS에 올릴 레코드
```

```text
s1._domainkey.example.com. IN TXT ( "v=DKIM1; h=sha256; k=rsa; "
                                    "p=MIIBIjANBgkqh...(공개 키)...IDAQAB" )
```

- 선택자(`s1`)는 키 이름입니다. 키를 바꿀 때는 새 선택자(`s2`)로 키를 만들어 DNS에 올리고, 서명을 새 키로 바꾼 뒤 며칠 지나 옛 레코드를 지웁니다.
- RSA 2048비트를 씁니다(RFC 8301: 1024비트 이상 필수, 2048 이상 권장, `rsa-sha1` 서명 금지). 2048비트 키는 TXT 한 문자열(255바이트)보다 길어 여러 문자열로 나눠 올립니다.
- `ed25519-sha256`(RFC 8463)도 정의되어 있지만 검증하지 못하는 수신 서버가 있어, 쓰려면 RSA 서명과 함께 둡니다.

### 3.2 서명 헤더 읽기

```text
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/simple; d=example.com; s=s1;
	t=1795490713; bh=dWexBXz5...; h=Date:To:From:Subject; b=IFWc6Ao1...
```

| 태그  | 뜻                                                       |
|-------|----------------------------------------------------------|
| `d=`  | 서명한 도메인 (DMARC 정렬 비교 대상)                     |
| `s=`  | 선택자 (`s=s1` → `s1._domainkey.d도메인` 조회)           |
| `a=`  | 알고리즘                                                 |
| `c=`  | 정규화 방식 (헤더/본문). `relaxed`는 공백 변화 등을 허용 |
| `h=`  | 서명에 포함한 헤더                                       |
| `bh=` | 본문 해시                                                |
| `b=`  | 서명 값                                                  |

### 3.3 OpenDKIM으로 서명 (Postfix 밀터)

```text
# /etc/opendkim.conf (필요한 값)
Mode                    sv
Domain                  example.com
Selector                s1
KeyFile                 /etc/opendkim/keys/s1.private
Canonicalization        relaxed/simple
InternalHosts           127.0.0.1
Socket                  inet:8891@127.0.0.1
```

- `Mode sv`: 서명(s)과 검증(v)을 함께 합니다. 인증한 사용자(587·465)와 `InternalHosts`의 메일에는 서명하고, 밖에서 들어온 메일은 검증합니다.
- 여러 도메인·여러 키는 `KeyTable`, `SigningTable`로 나눕니다.

```bash
sudo postconf -e "smtpd_milters = inet:127.0.0.1:8891" \
  "non_smtpd_milters = inet:127.0.0.1:8891" \
  "milter_default_action = accept"
sudo systemctl restart opendkim && sudo systemctl reload postfix
```

`milter_default_action = accept`는 밀터가 멈췄을 때 메일을 막지 않고 서명 없이 보냅니다. 서명 누락보다 메일 중단이 더 큰 문제인 경우의 선택이며, 반대라면 `tempfail`로 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. DMARC

SPF·DKIM 결과를 헤더 `From:` 도메인과 맞춰 보고(정렬), 실패한 메일의 처리 방침과 보고서 받을 주소를 공개합니다. 2026-05에 RFC 9989(본문), 9990(집계 보고), 9991(실패 보고)이 나와 이전 RFC 7489를 대체했습니다. 기존 `v=DMARC1` 레코드는 그대로 유효합니다.

### 4.1 레코드

```text
_dmarc.example.com. IN TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@example.com; adkim=r; aspf=r"
```

| 태그    | 뜻                                                             | 기본값        |
|---------|----------------------------------------------------------------|---------------|
| `v`     | `DMARC1`                                                       | 필수          |
| `p`     | 정책: `none`(관찰만), `quarantine`(스팸함 등), `reject`(거부)  | 없으면 `none` |
| `sp`    | 하위 도메인 정책                                               | `p`와 같음    |
| `np`    | 존재하지 않는 하위 도메인 정책 (RFC 9989에서 본문으로 들어옴)  | `sp`와 같음   |
| `adkim` | DKIM 정렬: `r`(같은 조직 도메인이면 됨), `s`(정확히 같아야 함) | `r`           |
| `aspf`  | SPF 정렬: `r`, `s`                                             | `r`           |
| `rua`   | 집계 보고서 받을 주소 (RFC 9990)                               | 없음          |
| `ruf`   | 실패 보고서 받을 주소 (RFC 9991, 보내지 않는 사업자가 많음)    | 없음          |
| `fo`    | 실패 보고 조건                                                 | `0`           |
| `t`     | `y`면 시험 중: 정책을 한 단계 낮춰 적용 요청                   | `n`           |
| `psd`   | 공개 접미사 도메인(PSD) 운영자용 표시                          | `u`           |

정렬 예: 헤더 `From: a@example.com`, DKIM `d=mail.example.com`이면 `adkim=r`에서는 같은 조직 도메인이라 정렬 통과, `adkim=s`에서는 실패입니다.

### 4.2 RFC 7489에서 바뀐 점

| 항목             | RFC 7489 (2015)             | RFC 9989 (2026)                      |
|------------------|-----------------------------|--------------------------------------|
| 문서 지위        | Informational               | Standards Track (Proposed Standard)  |
| `p` 태그         | 필수                        | 권장, 없으면 `p=none`                |
| 단계적 적용      | `pct=0~100` (비율 적용)     | `pct` 제거, `t=y`(한 단계 낮춰 적용) |
| `rf`, `ri`       | 보고 형식·주기              | 제거 (`historic`)                    |
| 조직 도메인 찾기 | 공개 접미사 목록(PSL)       | DNS Tree Walk (최대 8회 조회)        |
| `np`, `psd`      | 없음 (`np`는 RFC 9091 실험) | 본문에 정의                          |
| 보고             | 같은 문서                   | 9990(집계), 9991(실패)로 분리        |

- 제거된 태그는 무시되므로 레코드가 깨지지는 않습니다. 다만 `pct=25`처럼 비율로 단계적 적용을 하던 레코드는 더 이상 그 의미를 기대할 수 없어, `t=y`나 정책 단계(`none` → `quarantine` → `reject`)로 바꿉니다.
- 수신 구현이 RFC 9989를 따르는지는 구현마다 다릅니다. 시험한 OpenDMARC 1.4.2는 RFC 7489 기준입니다.

### 4.3 단계적 적용

| 단계 | 레코드                                   | 할 일                                                          |
|------|------------------------------------------|----------------------------------------------------------------|
| 1    | `p=none; rua=mailto:...`                 | 2~4주 집계 보고서로 내 도메인으로 메일을 보내는 곳을 모두 찾음 |
| 2    | 보낸 곳마다 SPF `include`·DKIM 서명 추가 | 보고서에서 정렬 실패가 정상 발송원에서 사라질 때까지           |
| 3    | `p=quarantine; t=y`                      | 실제로는 `none`으로 적용되며 영향 관찰                         |
| 4    | `p=quarantine`                           | 스팸함 처리 시작                                               |
| 5    | `p=reject`                               | 위조 메일 거부                                                 |

- 집계 보고서는 XML(보통 압축 첨부)로 하루 단위로 옵니다. 양이 많아 분석 도구나 서비스를 씁니다.
- `rua`를 다른 도메인 주소로 받으려면 그 도메인에 `example.com._report._dmarc.<받는 도메인>` TXT(`v=DMARC1`)가 있어야 합니다(RFC 9990). 없으면 보고서가 오지 않습니다.

```bash
dig +short TXT _dmarc.example.com
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 받는 서버에 적용 (Postfix)

받는 쪽에서 SPF는 정책 서비스, DKIM·DMARC는 밀터로 검사합니다.

```bash
sudo apt install postfix-policyd-spf-python opendkim opendmarc
```

```bash
# SPF 정책 서비스 (master.cf)
sudo postconf -M "policyd-spf/unix=policyd-spf unix - n n - 0 spawn user=nobody argv=/usr/bin/policyd-spf"
sudo postconf -e "policyd-spf_time_limit = 3600" \
  "smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination, check_policy_service unix:private/policyd-spf"
```

```text
# /etc/opendmarc.conf (필요한 값)
AuthservID                 mail.example.com
TrustedAuthservIDs         mail.example.com
IgnoreAuthenticatedClients true
RejectFailures             true
SPFSelfValidate            true
Socket                     inet:8893@127.0.0.1
```

```bash
sudo postconf -e "smtpd_milters = inet:127.0.0.1:8891, inet:127.0.0.1:8893"
sudo systemctl restart opendmarc && sudo systemctl reload postfix
```

- 밀터 순서는 OpenDKIM(검증 결과를 `Authentication-Results`에 기록) 다음에 OpenDMARC입니다. OpenDMARC는 `TrustedAuthservIDs`에 적은 서버의 결과만 믿습니다.
- `RejectFailures true`면 `p=reject` 도메인의 실패 메일을 SMTP 단계에서 `550 5.7.1`로 거부합니다. `false`면 판정 결과를 헤더에만 남깁니다.
- `IgnoreAuthenticatedClients true`: 내 사용자가 587로 제출한 메일은 검사하지 않습니다.
- `policyd-spf`의 기본 설정은 SPF `fail`을 거부하고 `softfail`은 헤더만 남깁니다(`/etc/postfix-policyd-spf-python/policyd-spf.conf`).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 화이트 리스트와 그레이 리스트

### 6.1 그레이 리스트

처음 보는 (접속 IP, 발신자, 수신자) 조합의 메일을 일단 임시 거부(`450`)합니다. 정상 메일 서버는 SMTP 규칙대로 잠시 뒤 다시 보내고, 한 번 보내고 끝나는 스팸 발송 도구는 다시 보내지 않는다는 점을 이용합니다(RFC 6647).

```bash
sudo apt install postgrey
```

```text
# /etc/default/postgrey (Debian 기본값은 --inet=10023, 지연 300초)
POSTGREY_OPTS="--inet=127.0.0.1:10023 --delay=300"
```

```bash
sudo postconf -e "smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination, check_policy_service unix:private/policyd-spf, check_policy_service inet:127.0.0.1:10023"
sudo systemctl restart postgrey && sudo systemctl reload postfix
```

| 장점                               | 주의할 점                                                                        |
|------------------------------------|----------------------------------------------------------------------------------|
| 설정이 간단하고 자원을 적게 씀     | 처음 오는 메일이 재시도 간격만큼 늦음 (보통 수 분~수십 분)                       |
| 재시도하지 않는 발송 도구를 걸러냄 | 여러 IP로 재시도하는 대형 사업자는 계속 처음 보는 조합이 됨 (화이트 리스트 필요) |
| 콘텐츠 검사 전에 걸러 부하 감소    | 인증번호 등 시간이 중요한 메일이 늦어짐                                          |

- postgrey는 같은 클라이언트가 몇 번 통과하면 자동으로 화이트 리스트에 넣습니다(`--auto-whitelist-clients`, 기본 5회).
- 판정 순서에서 SPF 검사를 그레이 리스트보다 앞에 두면, 위조 메일은 재시도 기회 없이 바로 `550`으로 끝납니다.

### 6.2 화이트 리스트

검사를 건너뛸 믿을 수 있는 발신원 목록입니다. 남용하면 그 경로가 우회로가 되므로 좁게 둡니다.

| 대상                   | 방법                                                                                         |
|------------------------|----------------------------------------------------------------------------------------------|
| 그레이 리스트 제외     | `/etc/postgrey/whitelist_clients.local`(호스트·도메인), `whitelist_recipients.local`(수신자) |
| Postfix 검사 전체 제외 | `check_client_access hash:/etc/postfix/client_allow`를 제한 목록 앞쪽에 두고 `OK`            |
| 인증 사용자            | `permit_sasl_authenticated` (이미 위 예에 포함)                                              |

```text
# /etc/postfix/client_allow  (postmap 으로 hash 생성)
192.0.2.25      OK
partner.example OK
```

```bash
sudo postmap /etc/postfix/client_allow
```

반대로 막을 발신원 목록(블랙리스트)은 `check_client_access`에 `REJECT`를 쓰거나, 공개 차단 목록(DNSBL)을 `reject_rbl_client`로 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 검증

발신 쪽(내 도메인 레코드와 서명)부터 확인합니다.

```bash
dig +short TXT example.com | grep spf1
dig +short TXT s1._domainkey.example.com
dig +short TXT _dmarc.example.com

# DKIM: 받은 메일 원본(.eml)으로 서명 검증 (python3-dkim)
dkimverify < message.eml

# SPF: 특정 IP·발신자 판정 (python3-spf)
python3 -c 'import spf; print(spf.check2(i="192.0.2.10", s="alice@example.com", h="mail.example.com"))'
```

받는 쪽 검사는 다른 서버(인증하지 않은 외부 주소)에서 swaks로 보냅니다.

```bash
# 봉투 발신자를 내 도메인으로 위조 → SPF fail
swaks -s mail.example.com -p 25 -f alice@example.com -t bob@example.com

# 헤더 From만 위조 → DMARC 거부
swaks -s mail.example.com -p 25 -f someone@example.net -t bob@example.com --h-From ceo@example.com
```

시험(로컬 DNS `example.test`, `p=reject`)에서 본 결과입니다.

| 확인                                       | 결과                                                                   |
|--------------------------------------------|------------------------------------------------------------------------|
| 587 제출 메일                              | `DKIM-Signature: ... d=example.test; s=s1`                             |
| `dkimverify` 원본 / 본문 한 글자 변경      | `signature ok` / `body hash mismatch`                                  |
| SPF 판정 (허용 IP / 다른 IP / 레코드 없음) | `pass` / `fail` / `none`                                               |
| 봉투 발신자 위조                           | `550 5.7.23 ... Message rejected due to: SPF fail - not authorized`    |
| 정상 외부 발신 첫 시도·즉시 재시도         | `450 4.2.0 ... Greylisted`                                             |
| 15초 지연 설정에서 17초 뒤 재시도          | `250 2.0.0`, `X-Greylist: delayed 18 seconds by postgrey-1.37`         |
| 헤더 From만 위조 (그레이 리스트 통과 뒤)   | `550 5.7.1 rejected by DMARC policy for example.test`                  |
| 받아들인 메일 헤더                         | `Received-SPF: None ...`, `Authentication-Results: ... dmarc=none ...` |

실제 수신 판정은 큰 메일 사업자 계정으로 메일을 보내 받은 메일의 원본 보기에서 `Authentication-Results`의 `spf=`, `dkim=`, `dmarc=` 값으로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                               | 원인                                           | 해결                                                             |
|------------------------------------|------------------------------------------------|------------------------------------------------------------------|
| SPF `permerror`                    | 레코드 두 개, 또는 DNS 조회 10개 초과          | 레코드 하나로 합치기, `include` 줄이기·IP로 바꾸기               |
| 전달된 메일만 SPF `fail`           | 전달 서버 IP가 SPF에 없음 (정상 동작)          | DKIM 서명으로 DMARC 통과, 전달 쪽은 SRS·ARC 사용                 |
| DKIM `body hash mismatch`          | 서명 뒤 본문이 바뀜 (서명 추가·바닥글 삽입 등) | 본문을 바꾸는 필터를 서명보다 앞에 둠                            |
| DKIM `key not found`, `no key`     | 선택자 레코드 이름·내용 오류, DNS 전파 전      | `dig TXT s1._domainkey.도메인`으로 확인, 나눈 문자열 따옴표 확인 |
| DMARC `fail`인데 SPF·DKIM은 `pass` | 정렬 실패 (대행 서비스 도메인으로 통과)        | 대행 서비스에 내 도메인 DKIM 서명(`d=내 도메인`)을 설정          |
| 집계 보고서가 오지 않음            | `rua`가 외부 도메인인데 확인 레코드 없음       | `<내 도메인>._report._dmarc.<받는 도메인>` TXT 추가              |
| `pct`로 단계적 적용이 안 됨        | RFC 9989에서 `pct` 제거                        | `t=y`나 정책 단계로 전환                                         |
| 정상 메일이 늦게 옴                | 그레이 리스트 지연                             | 상대 서버를 `whitelist_clients.local`에 추가, 지연 시간 조정     |
| 밀터 장애로 메일이 멈춤            | `milter_default_action = tempfail`             | 밀터 복구, 방침에 따라 `accept`로 둘지 결정                      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [메일 프로토콜 (SMTP · IMAP · POP3)](../../01_fundamentals/networking/mail_protocols.md) — 봉투와 헤더, Postfix·Dovecot 기본 서버
- [DNS 이름 해석과 장애 진단](../../01_fundamentals/networking/dns_resolution_troubleshooting.md) — TXT 레코드 조회
- [에러 코드](../../01_fundamentals/networking/error_codes.md) — SMTP 응답 코드

---

## 참고 자료

- IETF: [RFC 7208 Sender Policy Framework (SPF)](https://www.rfc-editor.org/rfc/rfc7208) — ★★★★☆
- IETF: [RFC 6376 DKIM Signatures](https://www.rfc-editor.org/rfc/rfc6376), [RFC 8301](https://www.rfc-editor.org/rfc/rfc8301) — ★★★★☆
- IETF: [RFC 9989 DMARC](https://www.rfc-editor.org/rfc/rfc9989), [RFC 9990 Aggregate Reporting](https://www.rfc-editor.org/rfc/rfc9990), [RFC 9991 Failure Reporting](https://www.rfc-editor.org/rfc/rfc9991) — ★★★★☆
- IETF: [RFC 6647 Email Greylisting](https://www.rfc-editor.org/rfc/rfc6647) — ★★★☆☆
- OpenDKIM: [opendkim.conf(5)](http://www.opendkim.org/opendkim.conf.5.html) — ★★★☆☆
- Postfix: [SMTPD Policy Delegation](https://www.postfix.org/SMTPD_POLICY_README.html), [Milter Support](https://www.postfix.org/MILTER_README.html) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-24

**마지막 업데이트**: 2026-11-24

© 2026 siasia86. Licensed under CC BY 4.0.
