---
name: papertrail-official-notes
description: SolarWinds Papertrail 요금 구조, 전송량 계산, 보관(archive), 수집 방식 정리 (공식 페이지 범위).
tags:
  - papertrail
  - logging
  - saas
  - syslog
last_checked: 2026-11-23
sources:
  - https://www.papertrail.com/plans/
  - https://www.papertrail.com/help/
---

# Papertrail 공식 자료 참조 노트

SolarWinds가 운영하는 로그 SaaS입니다. 계정 없이 확인할 수 있는 요금·도움말 페이지 범위만 기록하고, 전송은 시험하지 않았습니다.

## 1. 요금 (Plans 페이지, 2026-11-23)

| 항목           | 내용                                                                                                  |
|----------------|-------------------------------------------------------------------------------------------------------|
| 시작 가격      | GB당 월 $5.00부터                                                                                     |
| 포함 기능      | 웹 로그 뷰어, 팀 공유 그룹·검색, 시스템·사용자 수 무제한, 암호화 전송, 장기 보관, REST API, 검색 알림 |
| 한도 초과      | 수집을 멈추거나, 사용량 기반으로 계속(최대 200% 추가, GB당 30% 높은 단가) 중 선택                     |
| 전송량 계산    | 메시지 길이 + 메타데이터 50바이트. 1 GB는 100자 메시지 약 660만 건. 월 단위로 측정                    |
| 검색 기간 근거 | 자체 검색의 약 97%가 3~7일 범위였다는 설명. 그 밖은 보관(archive)으로                                 |
| 보관           | 내려받을 수 있는 텍스트 파일이며 Amazon S3에 복사됨. Redshift·Athena·EMR로 분석하는 문서 제공         |

## 2. 수집 방식 (Help 페이지 목차)

- syslog(Unix·BSD 시스템 로그, 네트워크 장비), 텍스트 파일(`remote_syslog2`), systemd, Docker, Kubernetes, 언어별 라이브러리(Python·Go·Node.js·Java 등), Fluentd 연동.
- TLS 암호화 전송과 로그 대상(Log destinations) 설정 문서가 있습니다.

## 3. 확인하지 못한 것

- 요금제별 검색 가능 기간·보관 기간의 정확한 값(요금 페이지가 표를 스크립트로 그림)
- 실제 전송과 알림 동작
