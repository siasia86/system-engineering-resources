# ASN 운영 및 IDC DDoS 대응 가이드

---

## 1. ASN (Autonomous System Number) 개요

ASN은 인터넷에서 독립적인 네트워크를 식별하는 번호.
BGP(Border Gateway Protocol)로 다른 네트워크와 라우팅 정보를 교환할 때 사용한다.

> ASN이 있어도 ISP 회선은 필수. 물리적 회선 없이 인터넷 연결 불가.
> ASN은 ISP에 종속되지 않고 여러 ISP를 자유롭게 선택/전환할 수 있게 해주는 것.

### 국내 AS번호 관리체계

```
┌────────┐     ┌────────┐     ┌───────────────────┐     ┌────────┐
│  IANA  │────▶│ APNIC  │────▶│ KISA (KRNIC)      │────▶│  ISP   │
│  총괄  │     │  아태  │     │ 한국인터넷진흥원  │     │ 관리   │
└────────┘     └────────┘     └───────────────────┘     │ 대행자 │
                                      │                 └────────┘
                                      │                     │
                                      ▼                     ▼
                              ┌───────────────┐       ┌────────────┐
                              │ 독립사용자    │       │ 일반사용자 │
                              │ (직접 할당)   │       │ (ISP 경유) │
                              └───────────────┘       └────────────┘
```

- 국내 AS번호는 KISA(한국인터넷진흥원) KRNIC에서 APNIC을 통해 할당
- 2004년 「인터넷주소자원에관한법률」 제정으로 법정 관리기관
- 2026년 3월 기준 국내 ~700개 이상 기관이 AS번호 보유
- 주요 보유 기관: ISP(KT, SKB, LGU+), 대학교, 금융기관, 공공기관, IT기업(카카오, 네이버, 삼성SDS 등)

---

## 2. ASN 등록 장단점

### 장점

- 독립적인 IP 운용 — PI(Provider Independent) IP로 ISP 변경해도 IP 유지
- 멀티호밍 — 2개 이상 ISP와 BGP 피어링, 장애 시 자동 failover
- 트래픽 제어 — BGP policy로 inbound/outbound 경로 직접 제어
- IX 참여 — KINX 등에서 다른 AS와 직접 피어링, 지연시간 감소 + 트랜짓 비용 절감
- DDoS 대응 옵션 확대 — BGP Blackhole, Scrubbing 서비스 연동 가능

### 단점

- ISP 2개 이상 회선 필수 (멀티호밍이 아니면 ASN 의미 감소)
- BGP 운영 가능한 네트워크 엔지니어 필요
- RPKI, IRR 등록/관리 부담
- 소규모 법인에는 비용 대비 효과 낮음

---

## 3. ASN 비용 (환율 1,500원 기준)

### 초기 비용 (1회성)

| 항목                  | USD               | KRW                      |
|-----------------------|-------------------|--------------------------|
| APNIC ASN 등록비      | 약 500            | 약 75만                  |
| IPv4 /24 구매 (256개) | 약 7,500 ~ 12,800 | 약 1,125만 ~ 1,920만     |
| BGP 라우터            | 약 3,000 ~ 10,000 | 약 450만 ~ 1,500만       |
| 초기 구축 인건비      | -                 | 약 300만 ~ 500만         |
| **합계**              |                   | **약 2,000만 ~ 4,000만** |

### 월 고정 비용

| 항목                     | 월 KRW                 |
|--------------------------|------------------------|
| APNIC 연회비 (÷12)       | 약 16만                |
| ISP 회선 A (BGP transit) | 약 75만 ~ 300만        |
| ISP 회선 B (이중화)      | 약 75만 ~ 300만        |
| IX 포트비 (KINX 등, 1G)  | 약 45만 ~ 75만         |
| IDC 코로케이션 (1/4랙)   | 약 30만 ~ 80만         |
| 장비 전력/유지보수       | 약 10만 ~ 20만         |
| 네트워크 엔지니어 (겸직) | 약 100만 ~ 200만       |
| **월 합계**              | **약 350만 ~ 1,000만** |

### 규모별 시나리오

| 규모      | 월 비용             | 설명                                          |
|-----------|---------------------|-----------------------------------------------|
| 최소 구성 | 약 350만 ~ 500만    | ISP 2개 소규모 회선, IX 미가입, 엔지니어 겸직 |
| 일반 구성 | 약 500만 ~ 800만    | ISP 2개 + IX 1개, 겸직 운영                   |
| 여유 구성 | 약 800만 ~ 1,000만+ | ISP 2개 + IX, 전담 인력, 이중화 장비          |

---

## 4. IDC에서의 DDoS 대응 — Cloudflare 서비스 비교

### 4-1. DNS/Proxy (일반 Cloudflare)

가장 기본적인 방식. ASN 불필요.

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Client  │────▶│  Cloudflare  │────▶│ IDC 서버 │
└──────────┘     │  (Proxy)     │     └──────────┘
                 └──────────────┘
                 HTTP/HTTPS만 처리
```

| 항목      | 내용                                                |
|-----------|-----------------------------------------------------|
| ASN 필요  | ❌                                                  |
| 보호 범위 | HTTP/HTTPS                                          |
| 원본 IP   | Cloudflare 뒤에 숨김                                |
| 비용      | Free / Pro($20/월) / Business($200/월) / Enterprise |
| 설정      | DNS를 Cloudflare로 변경                             |
| 적합 대상 | 웹사이트, API 서버                                  |

### 4-2. Spectrum

non-HTTP 프로토콜(TCP/UDP)을 Cloudflare Proxy로 보호. ASN 불필요.

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Client  │────▶│  Cloudflare  │────▶│ IDC 서버 │
└──────────┘     │  (Spectrum)  │     └──────────┘
                 └──────────────┘
                 특정 TCP/UDP 포트 처리
```

| 항목      | 내용                                  |
|-----------|---------------------------------------|
| ASN 필요  | ❌                                    |
| 보호 범위 | 설정한 TCP/UDP 포트                   |
| 원본 IP   | Cloudflare IP 사용, 원본 숨김         |
| 비용      | Pro 이상 ($5/포트~, 대역폭별 과금)    |
| 설정      | Cloudflare 대시보드에서 포트별 설정   |
| 적합 대상 | 게임서버, SSH, RDP, 메일서버          |
| 한계      | 포트 단위 설정, 포트 많으면 비용 증가 |

### 4-3. Magic Transit

L3/L4 전체 트래픽 보호. ASN + PI IP 필수.

```
┌──────────┐     ┌────────────────┐     GRE/IPsec     ┌──────────┐
│  Client  │────▶│  Cloudflare    │═══════════════════│ IDC 서버 │
└──────────┘     │  (BGP 광고)    │     터널          └──────────┘
                 └────────────────┘
                 자체 IP prefix 전체 보호
```

| 항목      | 내용                                    |
|-----------|-----------------------------------------|
| ASN 필요  | ✅                                      |
| 보호 범위 | 전체 IP 대역 (모든 프로토콜)            |
| IP 사용   | 자체 PI IP (Cloudflare에 BGP 광고 위임) |
| 비용      | 수천$/월~ (트래픽 규모별)               |
| 설정      | BGP 피어링 + GRE/IPsec 터널             |
| 적합 대상 | 대규모 IDC, 전체 네트워크 보호          |

---

## 5. 서비스 선택 가이드

| 상황                    | 추천                      | ASN    |
|-------------------------|---------------------------|--------|
| 웹서비스만 운영         | DNS/Proxy                 | 불필요 |
| 게임서버 몇 대 보호     | Spectrum                  | 불필요 |
| non-HTTP 포트 다수      | Spectrum (비용 검토)      | 불필요 |
| 전체 네트워크 DDoS 방어 | Magic Transit             | 필요   |
| ISP 이중화 + DDoS 방어  | Magic Transit + 멀티호밍  | 필요   |
| 소규모, 비용 최소화     | DNS/Proxy + Spectrum 조합 | 불필요 |

---

## 6. ASN 보유 시 DDoS 대응 추가 옵션

ASN이 있으면 Cloudflare 외에도 직접 제어 가능한 방법이 생긴다.

| 방법                 | 설명                                                                            |
|----------------------|---------------------------------------------------------------------------------|
| BGP Blackhole (RTBH) | 공격받는 IP를 upstream에서 null route. 빠르지만 해당 IP 서비스 중단             |
| BGP 경로 전환        | 공격 트래픽이 오는 ISP 경로를 빼고 다른 ISP로 우회                              |
| BGP Flowspec         | upstream 라우터에서 특정 패턴 트래픽 필터링                                     |
| Scrubbing 서비스     | Cloudflare Magic Transit, Akamai Prolexic, AWS Shield Advanced 등에 prefix 위임 |

---

## 7. Cloudflare 외 DDoS 방어 서비스 비교

```
┌───────────────────────────────────────────┐
│          ASN 없이 가능한 영역             │
│  ┌─────────────┐  ┌───────────────────┐   │
│  │ DNS/Proxy   │  │ Spectrum          │   │
│  │ (웹서비스)  │  │ (게임/TCP/UDP)    │   │
│  └─────────────┘  └───────────────────┘   │
└───────────────────────────────────────────┘
                    │
          규모 확대, 전체 네트워크 보호 필요
                    │
                    ▼
┌───────────────────────────────────────────┐
│          ASN 필요한 영역                  │
│  ┌──────────────────────────────────────┐ │
│  │ Magic Transit + BGP 멀티호밍         │ │
│  │ (전체 IP 대역 DDoS 방어)             │ │
│  └──────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

- 대부분의 IDC 서비스는 ASN 없이 Cloudflare DNS/Proxy + Spectrum으로 충분
- ASN + Magic Transit은 자체 IDC에서 대규모 서비스 운영 + 전체 네트워크 보호가 필요할 때
- DDoS 방어만이 목적이면 ASN 등록보다 Cloudflare 서비스가 비용 대비 효과적

---

## 8. 결론

| 서비스                        | L3/L4 방어 | L7 방어 | ASN 필요 | 최소 비용 (월)           | 특징                                  |
|-------------------------------|------------|---------|----------|--------------------------|---------------------------------------|
| Cloudflare (Proxy)            | ✅         | ✅      | ❌       | Free~                    | 가장 접근성 좋음, 무료 플랜           |
| Cloudflare Spectrum           | ✅         | ❌      | ❌       | ~$5/포트                 | non-HTTP 보호                         |
| Cloudflare Magic Transit      | ✅         | ✅      | ✅       | ~수천$                   | 전체 IP 대역 보호                     |
| AWS Shield Standard           | ✅         | ❌      | ❌       | 무료 (AWS 사용 시)       | AWS 인프라 자동 적용                  |
| AWS Shield Advanced           | ✅         | ✅      | ❌       | $3,000                   | DRT 전담팀 지원, 비용 보호            |
| Akamai Prolexic               | ✅         | ✅      | ✅       | Enterprise 협의          | 대규모 Scrubbing, 금융권 다수 사용    |
| Akamai App & API Protector    | ❌         | ✅      | ❌       | Enterprise 협의          | WAF + Bot 관리 통합                   |
| Azure DDoS Protection         | ✅         | ❌      | ❌       | ~$2,944 (기본 플랜 기준) | Azure 리소스 자동 보호                |
| 국내 ISP 클린존 (KT/SKB/LGU+) | ✅         | △       | ❌       | 약 50만 ~ 200만          | IDC 회선 부가서비스, 별도 장비 불필요 |

### 선택 기준

| 상황                   | 추천                                          |
|------------------------|-----------------------------------------------|
| AWS 기반 서비스        | AWS Shield (Standard 무료, 대규모면 Advanced) |
| Azure 기반 서비스      | Azure DDoS Protection                         |
| IDC + 웹서비스 위주    | Cloudflare DNS/Proxy (비용 대비 최고)         |
| IDC + 게임서버         | Cloudflare Spectrum 또는 ISP 클린존           |
| 금융/대기업 + 자체 IDC | Akamai Prolexic 또는 Cloudflare Magic Transit |
| 국내 IDC + 간단한 방어 | ISP 클린존 (KT DDoS 방어, SKB 클린존 등)      |

---

## 9. ISP/ASN 업체의 BFD 지원 현황

BFD(Bidirectional Forwarding Detection)는 두 네트워크 장비 간 링크 장애를 빠르게 감지하는 프로토콜입니다.
BGP만 사용할 경우 장애 감지에 30\~90초가 걸리지만, BFD를 적용하면 50ms\~1초 이내에 감지할 수 있습니다.

```
BGP만 사용 시:
Router A ----X---- Router B
         장애 발생 → 감지까지 30~90초 → Failover

BGP + BFD 사용 시:
Router A ----X---- Router B
         장애 발생 → 감지까지 ~150ms → Failover
         (BFD: 50ms 간격 × 3회 미응답 = 150ms)
```

| 항목             | BGP만 사용                  | BGP + BFD                        |
|------------------|-----------------------------|----------------------------------|
| 장애 감지 시간   | 30~90초                     | 50ms ~ 1초                       |
| 동작 방식        | Keepalive 메시지 타임아웃   | 전용 경량 패킷으로 상시 헬스체크 |
| 오버헤드         | 낮음                        | 매우 낮음 (패킷이 작음)          |
| 게임 서비스 영향 | 장애 시 30초 이상 접속 불가 | 1초 이내 백업 회선 전환          |

### 9-1. ISP 구간별 BFD 지원 여부

| 구간                    | BFD 지원 여부     | 비고                                             |
|-------------------------|-------------------|--------------------------------------------------|
| IDC 내부 (자체 장비 간) | ✅ 직접 설정 가능 | 자체 라우터/스위치에서 자유롭게 설정합니다       |
| IDC ↔ ISP (전용회선)    | ⚠️ 협의 필요      | ISP와 별도 협의 및 계약이 필요합니다             |
| ISP 백본 내부           | ❌ 관여 불가      | ISP 내부 정책에 따르며 고객이 제어할 수 없습니다 |

### 9-2. 국내 주요 ISP 상황

- KT, LG U+, SK브로드밴드 등 대형 ISP는 장비 자체는 BFD를 지원합니다
- 다만 고객과의 BGP 피어링에서 BFD를 켜줄지는 **별도 요청 및 협의** 사항입니다
- 일반 인터넷 회선에서는 보통 적용하지 않으며, **전용회선(Dedicated Line)이나 프리미엄 서비스** 계약 시 가능한 경우가 많습니다

### 9-3. BFD 미지원 시 대안

| 방법               | 설명                                                              |
|--------------------|-------------------------------------------------------------------|
| BGP Timer 조정     | Keepalive 3초 / Hold 9초로 공격적으로 줄여 감지 시간을 단축합니다 |
| 서버 레벨 헬스체크 | 자체 헬스체크로 회선 장애를 감지하고 DNS/라우팅을 전환합니다      |

> IDC 계약 시 ISP에 "BGP 피어링에 BFD 적용 가능한지" 사전에 확인하는 것을 권장합니다.

---

## 10. References

### ASN / BGP

- KRNIC AS번호란: <https://nic.or.kr/jsp/resources/asInfo.jsp>
- KRNIC AS번호 전세계 관리체계: <https://nic.or.kr/jsp/resources/asSys.jsp>
- KRNIC AS번호 신청: <https://nic.or.kr/jsp/business/management/asReg.jsp>
- KRNIC AS번호 사용자 현황: <https://nic.or.kr/jsp/business/management/asList.jsp>
- KRNIC IP주소/AS번호 통계: <https://nic.or.kr/jsp/statboard/IPAS/inter/pos/currentV4Addr.jsp>
- BGP 기본 개념 (Cloudflare): <https://www.cloudflare.com/learning/security/glossary/what-is-bgp/> ★★★
- KINX (한국 IX): <https://www.kinx.net/>

### Cloudflare DDoS 서비스

- Cloudflare DDoS Protection: <https://www.cloudflare.com/ddos/>
- Cloudflare Spectrum: <https://www.cloudflare.com/products/cloudflare-spectrum/>
- Cloudflare Magic Transit: <https://www.cloudflare.com/magic-transit/>
- Cloudflare 요금제 비교: <https://www.cloudflare.com/plans/>

### DDoS 방어 서비스

- AWS Shield: <https://aws.amazon.com/shield/>
- Azure DDoS Protection: <https://azure.microsoft.com/en-us/products/ddos-protection>
- Akamai Prolexic: <https://www.akamai.com/products/prolexic>

### DDoS 대응 일반

- Cloudflare BGP Blackhole 설명: <https://www.cloudflare.com/learning/ddos/glossary/ddos-blackhole-routing/>
- RTBH (RFC 5635): <https://datatracker.ietf.org/doc/html/rfc5635>
- BGP Flowspec (RFC 5575): <https://datatracker.ietf.org/doc/html/rfc5575>


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-11

© 2026 siasia86. Licensed under CC BY 4.0.
