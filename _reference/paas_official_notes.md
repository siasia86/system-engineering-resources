---
name: paas-official-notes
description: Cloudflare Workers·Vercel·Netlify·Render·Railway·Heroku의 무료 플랜 한도, 첫 유료 플랜, 잠듦 동작, 사용량 요금을 공식 페이지 기준으로 정리.
tags:
  - paas
  - cloudflare
  - vercel
  - netlify
  - render
  - railway
  - heroku
last_checked: 2026-11-27
sources:
  - https://developers.cloudflare.com/workers/platform/pricing/
  - https://vercel.com/pricing
  - https://vercel.com/docs/limits
  - https://www.netlify.com/pricing/
  - https://render.com/pricing
  - https://render.com/docs/free
  - https://railway.com/pricing
  - https://docs.railway.com/reference/pricing/plans
  - https://www.heroku.com/pricing
  - https://devcenter.heroku.com/articles/eco-dyno-hours
---

# PaaS 공식 자료 참조 노트

## 1. Cloudflare Workers (페이지 갱신 2026-11-18)

- Free: 하루 요청 100,000, 호출당 CPU 10ms, 정적 자원 "free and unlimited". KV 하루 읽기 100,000·쓰기 1,000, D1 하루 읽기 5M 행·쓰기 100,000 행·5GB, R2 10GB-월.
- Paid: "minimum charge of $5 USD per month for an account", 요청 10M 포함 뒤 100만당 $0.30, CPU 30M ms 포함 뒤 100만 ms당 $0.02. egress 과금 없음. 컨테이너는 유료만.
- "Beginning December 1, 2026, Workers Logs will use Cloudflare Observability pricing." SQLite Durable Object 저장 과금 2026-01 시작.

## 2. Vercel

- Hobby $0: Fast Data Transfer 100GB/월, CDN 요청 1M, 함수 호출 1M, Active CPU 4시간, ISR 쓰기 200k. 무료 계정은 추가 사용량 구매 불가. Pro $20/월.
- Limits(2026-09-16): Hobby 빌드 45분, 함수 최대 300초, 런타임 로그 1시간, 하루 배포 100.
- Hobby 상업적 사용 조건은 읽은 페이지에서 찾지 못함.

## 3. Netlify

- Free 300 크레딧, Personal $9/월(1,000), Pro $20/월(3,000). 운영 배포 15 크레딧, 컴퓨트 GB-시간 10, 전송 GB 20, 웹 요청 1만 2.

## 4. Render

- "Render grants 750 Free instance hours to each workspace per calendar month." 15분 무트래픽이면 잠듦, 깨는 데 약 1분. 휘발성 파일 시스템. 무료 Postgres 1GB, 30일 뒤 만료(14일 유예), 백업 없음.
- Hobby: 전송 5GB 포함(이후 $0.15/GB), 빌드 500분. Pro $25/월 + 컴퓨트. 가장 작은 컴퓨트 $7/월(512MB).

## 5. Railway

- Free: 월 $1 크레딧, 카드 불필요, 서비스 1 vCPU·0.5GB, 프로젝트 1·서비스 3, 볼륨 0.5GB, "sleep after 5 to 10 minutes without outbound traffic". Trial $5 일회(30일).
- Hobby $5/월($5 크레딧 포함), Pro $20/월. 메모리 $0.00000386/GB·초, CPU $0.00000772/vCPU·초, egress $0.05/GB.

## 6. Heroku

- 무료 dyno 없음(읽은 페이지 기준, 2022 제거 사실은 확인하지 않음). Eco $5/월, 계정 공유 1000 dyno 시간, 30분 무트래픽이면 잠듦, 소진 시 그달 남은 기간 잠듦, 개인 계정 전용(2026-04-18 갱신).
- Basic: 요금 페이지 $7(0.5GB, 상시), Eco 문서는 "$0.01/hr"로 표기(서로 맞춰지지 않음). Heroku Postgres Essential-0 $5(1GB, 연결 20).
