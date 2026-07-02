# 네트워크·서버 공격 유형 용어 정리

서버/네트워크 보안에서 자주 등장하는 공격 유형을 분류별로 정리합니다. 각 항목은 정의, 동작 원리, 대응 방법을 포함합니다.

## 목차

| 섹션                                                                                                                                  |
|---------------------------------------------------------------------------------------------------------------------------------------|
| [1. 스니핑](#1-스니핑sniffing) / [2. 스푸핑](#2-스푸핑spoofing) / [3. 중간자 공격](#3-중간자-공격mitm)                                |
| [4. 서비스 거부](#4-서비스-거부dosddos) / [5. 세션 공격](#5-세션-공격) / [6. 인증 공격](#6-인증-공격)                                 |
| [7. 주입 공격](#7-주입-공격injection) / [8. 권한 상승](#8-권한-상승privilege-escalation) / [9. 정보 수집](#9-정보-수집reconnaissance) |

---

## 1. 스니핑(Sniffing)

네트워크 트래픽을 도청(엿보기)하여 민감 데이터를 수집하는 공격입니다.

| 유형                          | 정의                                                               | 대상                          | 대응                                     |
|-------------------------------|--------------------------------------------------------------------|-------------------------------|------------------------------------------|
| 패킷 스니핑 (Packet Sniffing) | NIC를 promiscuous 모드로 전환하여 같은 세그먼트의 모든 패킷을 수집 | 평문 통신 (HTTP, FTP, Telnet) | 암호화 (TLS/SSH), 스위치 환경 사용       |
| ARP 스니핑 (ARP Snooping)     | ARP 테이블 감시를 통해 트래픽 모니터링                             | LAN 내 통신                   | Dynamic ARP Inspection (DAI)             |
| DHCP 스니핑 (DHCP Snooping)   | 비인가 DHCP 서버의 응답을 탐지·차단하는 방어 기법                  | DHCP 환경                     | 스위치 DHCP Snooping 활성화              |
| DNS 스니핑                    | DNS 쿼리/응답을 도청하여 접속 사이트 파악                          | DNS 트래픽 (UDP 53)           | DNS over HTTPS (DoH), DNS over TLS (DoT) |
| 포트 미러링 악용              | 스위치 SPAN/미러링 포트에서 복제된 트래픽 수집                     | 관리형 스위치                 | 미러링 포트 접근 제한, 물리 보안         |

### 스니핑 vs 스누핑

| 용어     | 의미                        | 차이                                         |
|----------|-----------------------------|----------------------------------------------|
| Sniffing | 네트워크 패킷 도청 (수동적) | 트래픽을 가로채서 읽기만 함                  |
| Snooping | 데이터/시스템 엿보기 (광의) | 파일, 이메일, 메모리 등 포함하는 포괄적 용어 |

🟡 실무에서는 거의 같은 의미로 혼용됩니다. 엄밀히는 Sniffing ⊂ Snooping 입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 스푸핑(Spoofing)

출발지 정보를 위조하여 신뢰 관계를 악용하는 공격입니다.

| 유형                           | 정의                                           | 동작 원리                                | 대응                                 |
|--------------------------------|------------------------------------------------|------------------------------------------|--------------------------------------|
| ARP Spoofing                   | ARP 응답을 위조하여 피해자의 ARP 테이블을 오염 | 공격자 MAC을 게이트웨이 MAC으로 등록시킴 | Static ARP, DAI, ARP 감시            |
| IP Spoofing                    | 출발지 IP를 위조하여 패킷 전송                 | 반사 공격(Amplification)에 활용          | BCP38 (Ingress Filtering), rp_filter |
| DNS Spoofing (Cache Poisoning) | DNS 응답을 위조하여 잘못된 IP로 유도           | 재귀 DNS에 위조 응답 삽입                | DNSSEC, DNS over TLS                 |
| MAC Spoofing                   | 출발지 MAC 주소를 위조                         | MAC 기반 접근 제어 우회                  | 802.1X (포트 기반 인증)              |
| Email Spoofing                 | 발신자 주소를 위조한 이메일 발송               | SMTP From 헤더 위조                      | SPF, DKIM, DMARC                     |
| BGP Hijacking                  | BGP 경로 공지를 위조하여 트래픽을 가로챔       | 더 구체적인 prefix 공지                  | RPKI, BGP Route Validation           |
| Caller ID Spoofing             | 발신 번호를 위조 (보이스 피싱)                 | VoIP에서 발신 번호 변조                  | STIR/SHAKEN 프로토콜                 |

### ARP Spoofing 동작

```
정상:
  PC-A ──ARP Request──> "Gateway MAC은?" ──> Gateway 응답 (정상 MAC)

공격:
  Attacker ──위조 ARP Reply──> PC-A: "Gateway MAC = Attacker MAC"
  PC-A ──트래픽──> Attacker ──전달──> Gateway (MITM 성립)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 중간자 공격(MITM)

통신 경로에 공격자가 끼어들어 도청·변조하는 공격입니다. 스니핑 + 스푸핑의 결합입니다.

| 유형            | 전제 조건                        | 동작                               | 대응                 |
|-----------------|----------------------------------|------------------------------------|----------------------|
| ARP MITM        | 같은 LAN 세그먼트                | ARP Spoofing → 양쪽 트래픽 중계    | DAI, Static ARP, VPN |
| SSL Strip       | HTTP → HTTPS 리다이렉트 가로채기 | HTTPS를 HTTP로 다운그레이드        | HSTS, HSTS Preload   |
| DNS MITM        | DNS 응답 위조 가능               | 가짜 IP로 유도 → 피싱 사이트       | DNSSEC, DoH/DoT      |
| Wi-Fi Evil Twin | 공개 Wi-Fi 환경                  | 동일 SSID 가짜 AP 설치 → 접속 유도 | VPN, 802.1X 인증     |
| BGP MITM        | BGP 라우팅 제어 가능             | 경로 가로채기 → 트래픽 중계·도청   | RPKI                 |

### MITM 공격 흐름

```
Client ──────────> Attacker ──────────> Server
         (암호화 해제)        (재암호화)
   Client는 정상 통신으로 인식
   Attacker는 평문 데이터 열람 가능
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 서비스 거부(DoS/DDoS)

대량 트래픽 또는 리소스 고갈로 서비스를 마비시키는 공격입니다.

| 계층 | 유형                    | 동작                               | 대응                          |
|------|-------------------------|------------------------------------|-------------------------------|
| L3   | ICMP Flood (Ping Flood) | 대량 ICMP Echo Request             | ICMP Rate Limit, 차단         |
| L3   | IP Fragmentation        | 조작된 fragment로 재조합 장애      | Fragment 검사, 최소 크기 제한 |
| L4   | SYN Flood               | 대량 SYN → 반개방 연결로 자원 고갈 | SYN Cookie, Backlog 증가      |
| L4   | UDP Flood               | 대량 UDP 패킷으로 대역폭 포화      | Rate Limiting, BCP38          |
| L4   | ACK Flood               | 대량 ACK → 상태 추적 테이블 고갈   | Stateful Firewall             |
| L7   | HTTP Flood              | 정상 HTTP 요청 대량 전송           | WAF, Rate Limiting, CAPTCHA   |
| L7   | Slowloris               | HTTP 연결을 극도로 느리게 유지     | 연결 타임아웃, mod_reqtimeout |
| L7   | DNS Amplification       | 작은 쿼리 → 큰 응답 (증폭)         | BCP38, DNS 응답 크기 제한     |
| L7   | NTP Amplification       | monlist 명령 악용 (증폭)           | NTP monlist 비활성화          |

### SYN Flood 동작

```
Attacker ──SYN (위조 IP)──> Server
Server ──SYN+ACK──> 위조 IP (응답 없음)
Server: half-open 연결 대기 (자원 점유)
... 수만 회 반복 → backlog 가득 → 정상 연결 불가
```

### 대응: SYN Cookie

```bash
# Linux sysctl
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 65535
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 세션 공격

인증된 세션을 탈취하거나 조작하는 공격입니다.

| 유형              | 정의                                               | 동작                                     | 대응                                     |
|-------------------|----------------------------------------------------|------------------------------------------|------------------------------------------|
| Session Hijacking | 유효한 세션 토큰을 탈취하여 인증 우회              | 스니핑/XSS로 세션 ID 획득                | HTTPS 필수, HttpOnly Cookie, 세션 재생성 |
| Session Fixation  | 공격자가 미리 설정한 세션 ID를 피해자에게 사용시킴 | 로그인 전 세션 ID 고정 → 로그인 후 탈취  | 로그인 시 세션 ID 재생성                 |
| Cookie Theft      | 쿠키를 탈취하여 세션 정보 획득                     | XSS, 스니핑, 브라우저 취약점             | Secure/HttpOnly/SameSite 속성            |
| Replay Attack     | 캡처한 인증 데이터를 재전송                        | 네트워크 도청 → 동일 요청 재전송         | Nonce, Timestamp, TLS                    |
| Token Theft       | JWT/API Token 탈취                                 | 로그, 에러 메시지, Referer 헤더에서 노출 | 짧은 만료, Token Rotation                |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 인증 공격

인증 메커니즘을 뚫어 비인가 접근을 시도하는 공격입니다.

| 유형                | 정의                                           | 동작                                             | 대응                                    |
|---------------------|------------------------------------------------|--------------------------------------------------|-----------------------------------------|
| Brute Force         | 모든 조합을 시도하여 비밀번호 탐색             | 자동화 도구로 무차별 대입                        | 계정 잠금, Rate Limit, MFA              |
| Dictionary Attack   | 사전 파일 기반 비밀번호 시도                   | 흔한 비밀번호 목록(rockyou.txt 등) 사용          | 복잡도 요구, MFA                        |
| Credential Stuffing | 유출된 계정/비밀번호 조합을 다른 서비스에 시도 | 데이터 유출 DB 활용                              | MFA, 비밀번호 재사용 금지, 유출 DB 대조 |
| Password Spraying   | 소수 비밀번호를 대량 계정에 시도               | 잠금 임계값 이하로 분산 시도                     | 잠금 정책 + 로그 모니터링               |
| Rainbow Table       | 해시 역산 테이블로 비밀번호 크래킹             | 사전 계산된 해시 매핑                            | Salt 적용 (bcrypt, argon2)              |
| Pass the Hash       | NTLM 해시를 그대로 인증에 사용                 | 해시 탈취 → 해시만으로 인증                      | Kerberos 강제, Credential Guard         |
| Kerberoasting       | AD 서비스 계정의 TGS 티켓을 오프라인 크래킹    | SPN 등록 계정의 티켓 요청 → 오프라인 해시 크래킹 | 강한 서비스 계정 비밀번호, AES 암호화   |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 주입 공격(Injection)

입력값에 악성 코드/명령을 삽입하여 실행시키는 공격입니다.

| 유형                       | 대상        | 동작                                              | 대응                            |
|----------------------------|-------------|---------------------------------------------------|---------------------------------|
| SQL Injection              | DB 쿼리     | 입력값에 SQL 구문 삽입 → DB 조작                  | Prepared Statement, ORM         |
| OS Command Injection       | 시스템 셸   | 입력값에 셸 명령 삽입 → 서버 명령 실행            | disable_functions, 입력 검증    |
| XSS (Cross-Site Scripting) | 브라우저    | 악성 스크립트 삽입 → 피해자 브라우저에서 실행     | 출력 인코딩, CSP                |
| LDAP Injection             | LDAP 쿼리   | 입력값에 LDAP 필터 삽입 → 디렉토리 정보 유출      | 입력 이스케이프, 파라미터화     |
| XML Injection (XXE)        | XML 파서    | 외부 엔터티 선언 → 서버 파일 읽기                 | DTD 비활성화, XML 파서 설정     |
| Template Injection (SSTI)  | 템플릿 엔진 | 템플릿 구문 삽입 → 서버측 코드 실행               | 사용자 입력 샌드박스, 로직 분리 |
| Log Injection              | 로그 시스템 | 로그에 조작된 데이터 삽입 → 로그 위변조/SIEM 혼란 | 로그 입력값 이스케이프          |

### SQL Injection 예시

```
정상: SELECT * FROM users WHERE id = '1'
공격: SELECT * FROM users WHERE id = '1' OR '1'='1'
결과: 전체 사용자 데이터 반환
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 권한 상승(Privilege Escalation)

낮은 권한에서 높은 권한(root/admin)을 획득하는 공격입니다.

| 유형                          | 경로      | 동작                                   | 대응                                 |
|-------------------------------|-----------|----------------------------------------|--------------------------------------|
| SUID 바이너리 악용            | 로컬      | SUID 설정된 바이너리로 root 명령 실행  | 불필요한 SUID 제거, 감사             |
| Kernel Exploit                | 로컬      | 커널 취약점으로 root 획득              | 커널 업데이트, seccomp               |
| sudo 설정 오류                | 로컬      | NOPASSWD 또는 와일드카드 설정 악용     | sudo 최소 권한, 정기 감사            |
| 컨테이너 탈출                 | 로컬      | 컨테이너에서 호스트로 탈출             | rootless 컨테이너, seccomp, AppArmor |
| 서비스 계정 악용              | 로컬/원격 | 서비스 계정 자격 증명 탈취 → 상위 접근 | 최소 권한, 자격 증명 관리            |
| DLL Hijacking (Windows)       | 로컬      | 악성 DLL을 검색 경로에 배치            | 안전한 DLL 검색 순서, 코드 서명      |
| Token Impersonation (Windows) | 로컬      | 다른 사용자의 토큰을 복제 → 권한 획득  | SeImpersonatePrivilege 제한          |

### Linux 권한 상승 체크

```bash
# SUID 파일 검색
find / -perm -4000 -type f 2>/dev/null

# sudo 설정 확인
sudo -l

# 커널 버전 확인 → CVE 검색
uname -r
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 정보 수집(Reconnaissance)

공격 전 대상 시스템 정보를 수집하는 단계입니다. 직접적 피해는 없지만 후속 공격의 기초입니다.

| 유형                  | 방법                     | 수집 정보                      | 대응                         |
|-----------------------|--------------------------|--------------------------------|------------------------------|
| Port Scan             | nmap, masscan            | 열린 포트, 서비스 버전         | 방화벽, IDS 탐지             |
| Banner Grabbing       | telnet, curl -I          | 서버 소프트웨어·버전           | ServerTokens Prod, 헤더 제거 |
| DNS Enumeration       | dig, fierce, dnsenum     | 서브도메인, MX, NS 레코드      | DNS Zone Transfer 제한       |
| WHOIS                 | whois                    | 도메인 소유자, 등록 정보       | WHOIS Privacy                |
| Directory Brute Force | dirb, gobuster           | 숨겨진 경로, 관리자 페이지     | 비표준 경로, 접근 제어       |
| OS Fingerprinting     | nmap -O                  | OS 종류·버전                   | 방화벽 규칙, TCP 옵션 조정   |
| Social Engineering    | 피싱, 전화, 사칭         | 내부 정보, 자격 증명           | 보안 교육, 인증 절차 강화    |
| Google Dorking        | site:, filetype:, inurl: | 노출된 파일, 설정, 관리 페이지 | robots.txt, 민감 파일 제거   |
| Shodan/Censys         | 검색 엔진                | 공개된 서비스, IoT 장비        | 불필요 포트 차단, 인증 강화  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OWASP Top 10: [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/) — ★★★☆☆
- MITRE ATT&CK: [attack.mitre.org](https://attack.mitre.org/) — ★★★★☆
- CWE List: [cwe.mitre.org](https://cwe.mitre.org/) — ★★★☆☆
- [02_web_cwe (웹 취약점 실습)](./02_web_cwe/README.md)
- [01_cve (CVE 분석)](./01_cve/README.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-02

**마지막 업데이트**: 2026-07-02

© 2026 siasia86. Licensed under CC BY 4.0.
