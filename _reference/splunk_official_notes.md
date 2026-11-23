---
name: splunk-official-notes
description: Splunk Enterprise·Splunk Cloud Platform 판, 체험판·무료 색인 한도, 요금 방식 정리 (공식 페이지 범위).
tags:
  - splunk
  - logging
  - siem
  - commercial
last_checked: 2026-11-23
sources:
  - https://www.splunk.com/en_us/download/splunk-enterprise.html
  - https://www.splunk.com/en_us/products/pricing.html
  - https://hub.docker.com/r/splunk/splunk/tags
---

# Splunk 공식 자료 참조 노트

상용 제품이라 계정·비용 없이 확인할 수 있는 공식 페이지 범위만 기록합니다. 설치·실행은 시험하지 않았습니다.

## 1. 판과 체험 (2026-11-23)

| 항목              | 내용                                                | 근거            |
|-------------------|-----------------------------------------------------|-----------------|
| Splunk Enterprise | 10.6.2.5 (다운로드 페이지), 이전 계열 10.4.2도 게시 | 다운로드 페이지 |
| 컨테이너 이미지   | `splunk/splunk:10.6.2`, `10.6.2.5`, `-rhel9` 변형   | Docker Hub      |
| 체험판            | Splunk Enterprise 60일 무료 체험, 신용카드 불필요   | 다운로드 페이지 |
| 무료 색인 한도    | 다운로드 페이지에 `Index 500 MB/Day` 표기           | 다운로드 페이지 |

## 2. 제품과 요금 방식 (Pricing 페이지)

| 제품                  | 배포                                 | 요금 방식                                                   |
|-----------------------|--------------------------------------|-------------------------------------------------------------|
| Splunk Enterprise     | 사설 클라우드·온프레미스·폐쇄망 가능 | 수집량(data-ingest) 또는 작업량(workload), 사용자 수 무제한 |
| Splunk Cloud Platform | Splunk가 운영하는 SaaS               | 활동량(activity-based)·수집량·작업량 중 선택                |

- 단가는 공개되어 있지 않고 견적(Get a quote) 방식입니다.
- Cisco 텔레메트리는 0.5배 가중 수집률로 계산한다는 안내가 있습니다(Cloud Platform).

## 3. 확인하지 못한 것

- 실제 단가, Splunk Free 라이선스의 기능 제한 상세(관련 문서 페이지 조회 실패)
- Universal Forwarder 설정과 검색 언어(SPL) 동작
