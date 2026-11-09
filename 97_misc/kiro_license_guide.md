# Kiro 라이선스 및 비용 가이드

## 목차

| 섹션                                                                                                                                                         |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 제품 개요](#1-제품-개요) / [2. 개인 플랜](#2-개인-플랜) / [3. 팀·Enterprise 플랜](#3-팀enterprise-플랜)                                                  |
| [4. 모델별 크레딧 소비](#4-모델별-크레딧-소비) / [5. Q Developer Pro와의 관계](#5-q-developer-pro와의-관계) / [6. 사내 도입 시나리오](#6-사내-도입-시나리오) |

---

## 1. 제품 개요

Kiro는 AWS가 제공하는 AI 코딩 어시스턴트로, Amazon Q Developer와는 **별개의 독립 제품**입니다.

| 항목        | Amazon Q Developer Pro      | Kiro                                  |
|-------------|-----------------------------|---------------------------------------|
| 제품 유형   | AWS 콘솔 통합 AI 어시스턴트 | 독립 AI 코딩 에이전트                 |
| 가입 경로   | 신규 가입 종료 (2026-05-15) | kiro.dev(개인), Kiro 콘솔(팀)         |
| 인증 방식   | AWS IAM / SSO               | GitHub·Google, AWS Builder ID, IAM IC |
| 서비스 리전 | 프로필 US East, Frankfurt   | 프로필 US East, Frankfurt, GovCloud   |
| 청구 방식   | AWS 청구서                  | 개인 kiro.dev, 팀 AWS 청구서          |
| 상호 호환   | 🟡 Kiro CLI에서 사용 가능   | 🟡 Q 구독을 Kiro 구독으로 전환 가능   |

🟡 Q Developer Pro 구독으로 Kiro CLI를 쓸 수 있지만 Kiro 요금제의 추가 크레딧·overage는 적용되지 않습니다. 관리자는 Q 구독을 사용자·그룹 단위로 Kiro 구독으로 전환할 수 있습니다. Amazon Q Developer는 2026-05-15부터 신규 가입을 받지 않으며 IDE plugin과 유료 구독은 2027-04-30에 지원이 끝납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 개인 플랜

kiro.dev에서 개인 신용카드로 직접 가입합니다.

| 플랜    | 가격 (월) | 크레딧/월 | 주요 특징                     |
|---------|-----------|-----------|-------------------------------|
| Free    | $0        | 50        | Sonnet 4.5, 오픈웨이트 모델만 |
| Pro     | $20       | 1,000     | 프리미엄 모델 전체 접근       |
| Pro+    | $40       | 2,000     | 동일 + 크레딧 2배             |
| Pro Max | $100      | 5,000     | 동일 + 크레딧 5배             |
| Power   | $200      | 10,000    | 동일 + 크레딧 10배            |

- 추가 크레딧: $0.04 / credit (한도 초과 시 $5~$100 add-on 팩 구매, 구매일부터 12개월 사용)
- Free에서 Pro로 처음 업그레이드하면 그달 남은 기간 무료 + 12개월 안에 쓸 trial 크레딧 500 지급 (2026-11-01 이전 업그레이드는 기존 $20 할인 유지)
- 세금 별도 (일본 청구 주소 시 소비세 적용)

[⬆ 목차로 돌아가기](#목차)

---

## 3. 팀·Enterprise 플랜

별도 "Enterprise 전용 플랜"은 없습니다. 팀 플랜이 Enterprise 기능을 포함합니다.

신규 팀·Enterprise 고객은 credit pooling 좌석을 구매합니다. 좌석은 $20/월이고 좌석마다 월 500 크레딧이 pool에 추가되며, 2개 이상 좌석을 한 pool에 배정해 크레딧을 함께 씁니다. pool 추가 크레딧은 $0.04 / credit(12개월 사용)입니다. 아래 사용자별 Pro~Power 구독은 기존 Enterprise 고객이 유지할 수 있는 방식입니다.

| 플랜    | 가격 (유저/월) | 크레딧/월 | 추가 크레딧    |
|---------|----------------|-----------|----------------|
| Pro     | $20            | 1,000     | $0.04 / credit |
| Pro+    | $40            | 2,000     | $0.04 / credit |
| Pro Max | $100           | 5,000     | $0.04 / credit |
| Power   | $200           | 10,000    | $0.04 / credit |

### 팀 플랜 공통 포함 기능

팀·Enterprise 구독(credit pooling 포함)에 아래 기능이 포함됩니다.

| 기능                            | 설명                           |
|---------------------------------|--------------------------------|
| SAML/SCIM SSO                   | IAM Identity Center·외부 IdP   |
| Consolidated billing            | 팀 전체 중앙 청구              |
| Usage analytics                 | 사용량 분석 및 리포팅          |
| 조직 관리 대시보드              | 구독 관리, 사용자 추가/제거    |
| Enterprise 보안/프라이버시 통제 | 데이터 보호, 컴플라이언스 통제 |

### 볼륨 할인 / 커스텀 계약

공식 가격 페이지에 게시된 단가 이외의 볼륨 할인 및 커스텀 계약은 kiro.dev 영업팀 문의가 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 모델별 크레딧 소비

크레딧 소비는 Auto(1.0x)를 기준으로 배율이 적용됩니다.

| 모델              | 배율  | 컨텍스트 | 리전   | Pro (1,000cr) 소진 기준 |
|-------------------|-------|----------|--------|-------------------------|
| GPT-5.6 Sol       | 4.4x  | 1M       | US, EU | ~227 작업               |
| GPT-5.6 Terra     | 2.2x  | 1M       | US, EU | ~454 작업               |
| GPT-5.6 Luna      | 0.6x  | 1M       | US, EU | ~1,667 작업             |
| Claude Opus 5     | 2.2x  | 1M       | US, EU | ~454 작업               |
| Claude Opus 4.8   | 2.2x  | 1M       | US, EU | ~454 작업               |
| Claude Sonnet 5   | 1.3x  | 1M       | US, EU | ~769 작업               |
| Claude Sonnet 4.6 | 1.3x  | 1M       | US, EU | ~769 작업               |
| Auto              | 1.0x  | —        | US, EU | ~1,000 작업             |
| Claude Haiku 4.5  | 0.4x  | 200K     | US, EU | ~2,500 작업             |
| DeepSeek 3.2      | 0.25x | 128K     | US     | ~4,000 작업             |

GPT-5.6은 272K 토큰까지 표의 배율이 적용되고, 272K 토큰을 넘는 요청은 2배 배율로 청구됩니다.

🟡 "작업 1회"는 단순 질문 기준입니다. 파일 수정, tool 호출이 많은 agentic 작업은 수십 크레딧을 소모하므로 Opus 5 기준 Pro 플랜($20)은 크레딧이 빠르게 소진됩니다. 팀 용도라면 **Pro Max 이상**이 현실적입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Q Developer Pro와의 관계

### 리전 차이

| 항목                  | Amazon Q Developer Pro               | Kiro (개인/팀)                                   |
|-----------------------|--------------------------------------|--------------------------------------------------|
| 서비스 리전           | 프로필 US East, Frankfurt            | 프로필 US East, Frankfurt, GovCloud(US)          |
| 개인 구독자 inference | US East (Builder ID)                 | US endpoint 사용                                 |
| Enterprise 구독자     | 프로필 리전 (US East 또는 Frankfurt) | 프로필 리전 (GPT-5.6 등 일부 모델은 Global 추론) |

### 라이선스 독립성

- Q Developer Pro 구독으로 Kiro CLI 사용 가능 (add-on 크레딧·overage는 미지원)
- Kiro 팀 플랜은 AWS IAM Identity Center 연동이 가능하나, 이는 **Kiro 자체 구독을 전제**로 합니다
- Kiro 요금제의 크레딧·추가 크레딧을 쓰려면 **Kiro 구독**이 필요하며, 관리자는 Q 구독을 사용자·그룹 단위로 Kiro 구독으로 전환할 수 있습니다

[⬆ 목차로 돌아가기](#목차)

---

## 6. 사내 도입 시나리오

### 시나리오 비교

| 시나리오                  | 방법                   | 비용                   | 특이사항                             |
|---------------------------|------------------------|------------------------|--------------------------------------|
| 개인 즉시 사용            | kiro.dev 개인 Pro 가입 | $20/월 (개인 신용카드) | 즉시 사용, 최신 모델 접근            |
| 팀 도입 (SSO 포함)        | credit pooling 좌석    | $20 / 좌석 / 월        | 좌석당 월 500 크레딧 공유            |
| 사내 Q Developer Pro 활용 | Kiro CLI 사용          | 기존 Q 구독            | overage 미지원, 2027-04-30 지원 종료 |
| 볼륨 할인 / 커스텀 계약   | kiro.dev 영업팀 문의   | 협의                   | 대규모 팀 도입 시 검토               |

### 팀 도입 절차 (Teams 플랜 기준)

```
1. kiro.dev 접속 → Teams 플랜 선택
2. Kiro 프로필 생성 (us-east-1 또는 eu-central-1) 후 IAM Identity Center 인스턴스 연동
3. 팀원 계정 구독 등록 (SAML/SCIM)
4. 조직 관리 대시보드에서 사용량 모니터링
```

🟡 IAM Identity Center 인스턴스는 **서울(ap-northeast-2)을 포함한 지원 리전**에 있으면 됩니다. Kiro 프로필(데이터 저장·추론 위치)은 US East(N. Virginia)·Europe(Frankfurt)·AWS GovCloud(US)에만 만들 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Kiro Pricing: [kiro.dev/pricing](https://kiro.dev/pricing/) — ★★★☆☆
- Kiro Models: [kiro.dev/docs/models](https://kiro.dev/docs/models/) — ★★★☆☆
- Kiro Data Protection: [kiro.dev/docs/privacy-and-security/data-protection](https://kiro.dev/docs/privacy-and-security/data-protection/) — ★★★☆☆
- Kiro Enterprise Supported Regions: [kiro.dev/docs/enterprise/supported-regions](https://kiro.dev/docs/enterprise/supported-regions/) — ★★★☆☆
- Kiro Enterprise Billing: [kiro.dev/docs/enterprise/billing](https://kiro.dev/docs/enterprise/billing/) — ★★★☆☆
- Kiro Upgrading from Q CLI (Q Developer Pro FAQ): [kiro.dev/docs/upgrade-guides/migrating-from-q](https://kiro.dev/docs/upgrade-guides/migrating-from-q/) — ★★★☆☆
- Amazon Q Developer end of support: [aws.amazon.com/blogs/devops](https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement/) — ★★★☆☆
- Amazon Q Developer Pro Region support: [docs.aws.amazon.com/amazonq](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-admin-setup-subscribe-regions.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-05

**마지막 업데이트**: 2026-11-09

© 2026 siasia86. Licensed under CC BY 4.0.
