# PaaS 비교 (Cloudflare · Vercel · Netlify · Render · Railway · Heroku)
<!-- reference: _reference/paas_official_notes.md -->

코드나 컨테이너를 올리면 빌드·배포·확장·인증서를 대신 처리해 주는 PaaS·엣지 플랫폼 여섯 가지를 무료 플랜 조건, 첫 유료 플랜, 실행할 수 있는 것(정적 사이트, 함수, 오래 도는 서비스, DB)으로 비교합니다. 작은 서비스·시제품·개인 프로젝트를 빠르게 올릴 때 고르는 기준을 정리했습니다.

- 확인일: 2026-11-27, 각 사업자의 공식 요금·문서 페이지 기준. 가격은 미국 달러, 세금 별도이며 자주 바뀝니다
- 예제 시험: 계정이 필요해 실행하지 않음. 무료 플랜의 상업적 사용 조건은 읽은 페이지에서 찾지 못해 미확인

## 목차

| 섹션                                                                                                |
|-----------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 한눈에 비교](#2-한눈에-비교) / [3. 사업자별 메모](#3-사업자별-메모)        |
| [4. 고르는 기준](#4-고르는-기준) / [5. 옮기기 전 확인](#5-옮기기-전-확인) / [함께 보기](#함께-보기) |

---

## 1. 개요

| 종류             | 사업자                  | 실행 단위                                            |
|------------------|-------------------------|------------------------------------------------------|
| 엣지 함수·정적   | Cloudflare Workers      | 짧은 함수(요청당 CPU 시간 제한), 정적 자원, KV·D1·R2 |
| 프런트엔드 배포  | Vercel, Netlify         | 정적 사이트 + 서버리스 함수                          |
| 앱·컨테이너 PaaS | Render, Railway, Heroku | 오래 도는 웹 서비스·워커·크론, 관리형 DB             |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 항목             | Cloudflare Workers                                      | Vercel                                | Netlify          | Render                                              | Railway                                           | Heroku                               |
|------------------|---------------------------------------------------------|---------------------------------------|------------------|-----------------------------------------------------|---------------------------------------------------|--------------------------------------|
| 무료 플랜        | 있음: 하루 요청 10만, 요청당 CPU 10ms, 정적 자원 무제한 | Hobby: 월 전송 100GB, 함수 호출 100만 | Free: 300 크레딧 | Hobby: 월 750 인스턴스 시간, 15분 무트래픽이면 잠듦 | Free: 월 $1 사용 크레딧, 5~10분 무트래픽이면 잠듦 | 없음(찾지 못함)                      |
| 첫 유료          | Workers Paid 월 최소 $5                                 | Pro 월 $20                            | Personal 월 $9   | Pro 월 $25 + 컴퓨트(가장 작은 컴퓨트 월 $7)         | Hobby 월 $5(사용 크레딧 $5 포함)                  | Eco 월 $5(계정 공유 1,000 dyno 시간) |
| 오래 도는 서비스 | 컨테이너는 유료만                                       | 없음(함수 최대 시간 제한)             | 없음             | 있음(웹·워커·크론·Docker)                           | 있음(컨테이너, 유료는 상시)                       | 있음(dyno)                           |
| 관리형 DB        | D1(SQLite), KV, R2(객체)                                | 목록에 관리형 SQL 없음                | Netlify Database | Postgres(무료는 1GB, 30일 뒤 만료), Key Value       | Postgres·Redis·MySQL·MongoDB(Hobby부터)           | Heroku Postgres Essential-0 월 $5    |
| 나가는 트래픽    | Workers는 egress 과금 없음                              | 플랜 포함량                           | GB당 20 크레딧   | Hobby 월 5GB 포함, 이후 GB당 $0.15                  | GB당 $0.05                                        | 미확인                               |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 사업자별 메모

### 3.1 Cloudflare Workers

- 무료: 하루 요청 10만, 호출당 CPU 10ms, 정적 자원 요청 무료·무제한. KV(하루 읽기 10만·쓰기 1,000), D1(하루 읽기 500만 행, 5GB), R2(월 10GB)도 무료 한도가 있습니다.
- Workers Paid는 계정당 월 최소 $5이고, 요청 1,000만·CPU 3,000만 ms가 포함되며 초과분은 요청 100만당 $0.30, CPU 100만 ms당 $0.02입니다. egress는 과금하지 않습니다.
- 2026-12-01부터 Workers Logs가 Cloudflare Observability 요금을 따릅니다.

### 3.2 Vercel

- Hobby(무료): 월 Fast Data Transfer 100GB, CDN 요청 100만, 함수 호출 100만, Active CPU 4시간, 빌드 45분, 함수 최대 300초, 하루 배포 100회. 무료 계정은 한도를 넘는 사용량을 살 수 없습니다.
- Pro 월 $20.

### 3.3 Netlify

- 크레딧 방식입니다. Free 300 크레딧, Personal 월 $9(1,000 크레딧), Pro 월 $20(3,000 크레딧). 운영 배포 1회 15 크레딧, 컴퓨트 GB-시간당 10, 전송 GB당 20, 웹 요청 1만 건당 2 크레딧.

### 3.4 Render

- 무료 웹 서비스는 15분 동안 들어오는 트래픽이 없으면 잠들고 깨는 데 약 1분 걸립니다. 파일 시스템은 휘발성이고 영구 디스크가 없습니다. 무료 Postgres는 1GB, 만든 지 30일 뒤 만료(14일 유예), 백업 없음.
- 정적 사이트는 무료이며 Hobby는 월 전송 5GB(이후 GB당 $0.15), 빌드 500분을 포함합니다. 가장 작은 유료 컴퓨트는 월 $7(512MB).

### 3.5 Railway

- Free: 월 $1 사용 크레딧, 신용카드 불필요, 서비스당 1 vCPU·0.5GB, 프로젝트 1개·서비스 3개, 5~10분 동안 나가는 트래픽이 없으면 잠듦. Free Trial은 30일 $5 일회 크레딧.
- 사용량 요금: 메모리 GB·초당 $0.00000386(약 GB·월 $10), CPU vCPU·초당 $0.00000772(약 vCPU·월 $20), 서비스 egress GB당 $0.05. Hobby 이상은 상시 실행.

### 3.6 Heroku

- 읽은 요금 페이지에 무료 dyno가 없습니다. Eco는 월 $5로 계정 전체 Eco dyno가 1,000 dyno 시간을 나눠 쓰고, 30분 동안 웹 트래픽이 없으면 잠들며(잠든 동안은 시간 소모 없음), 시간을 다 쓰면 그달 남은 기간 모든 Eco dyno가 잠듭니다. 개인 계정 전용입니다.
- Basic은 요금 페이지에 월 $7(0.5GB, 상시)로 나와 있습니다. Heroku Postgres Essential-0은 월 $5(디스크 1GB, 연결 20).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 고르는 기준

| 상황                                              | 먼저 볼 것                 | 이유                                       |
|---------------------------------------------------|----------------------------|--------------------------------------------|
| 정적 사이트·짧은 API, 전 세계 사용자, 트래픽 많음 | Cloudflare Workers         | egress 과금 없음, 엣지 실행                |
| Next.js 등 프런트엔드 프레임워크 배포             | Vercel, Netlify            | 빌드·미리 보기 배포 흐름                   |
| 오래 도는 API·워커와 Postgres를 함께              | Render, Railway, Heroku    | 서비스·DB를 한 곳에서                      |
| 무료로 상시 켜 두어야 함                          | 어느 무료 플랜도 맞지 않음 | Render·Railway·Heroku Eco 모두 잠듦        |
| 비용 예측이 중요                                  | 고정 월 요금 플랜          | 사용량 요금(Railway·Netlify 크레딧)은 변동 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 옮기기 전 확인

이번에 공식 문서와 대조하지 않은 일반 점검 목록입니다.

- 잠듦(sleep) 동작: 무료 플랜은 첫 요청이 느립니다. 상태 확인·크론으로 깨우는 것은 약관을 먼저 확인합니다.
- 데이터: 무료 DB의 만료·백업 여부(Render 무료 Postgres는 30일 만료), 내보내기 방법.
- 상업적 사용: 무료 플랜의 상업적 사용 허용 여부를 약관에서 확인합니다(이번에 찾지 못함).
- 종속성: 플랫폼 전용 기능(KV, Edge Config, 크레딧 계산)을 많이 쓸수록 옮기기 어렵습니다. 컨테이너 이미지로 배포하면 옮기기 쉽습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [서버리스 함수 비교](./serverless_functions_comparison.md) — Lambda, Azure Functions, Cloud Run functions
- [클라우드 사업자 비교](./cloud_provider_comparison.md) — IaaS 비교
- [Docker Compose](../containers/docker_compose.md) — 직접 서버에 올릴 때

---

## 참고 자료

- Cloudflare: [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/) — ★★★☆☆
- Vercel: [Pricing](https://vercel.com/pricing) · [Limits](https://vercel.com/docs/limits) — ★★★☆☆
- Netlify: [Pricing](https://www.netlify.com/pricing/) — ★★★☆☆
- Render: [Pricing](https://render.com/pricing) · [Free instances](https://render.com/docs/free) — ★★★☆☆
- Railway: [Pricing](https://railway.com/pricing) · [Plans](https://docs.railway.com/reference/pricing/plans) — ★★★☆☆
- Heroku: [Pricing](https://www.heroku.com/pricing) · [Eco dyno hours](https://devcenter.heroku.com/articles/eco-dyno-hours) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
