---
name: bitbucket-official-notes
description: Bitbucket(Atlassian)의 Cloud 요금제와 자체 설치형(Data Center)의 공식 출처 기준 사실 정리. 계정 없이 확인할 수 있는 범위만 다룸.
tags:
  - git
  - bitbucket
  - saas
last_checked: 2026-11-23
sources:
  - https://www.atlassian.com/software/bitbucket/pricing
  - https://www.atlassian.com/software/bitbucket/enterprise
  - https://support.atlassian.com/bitbucket-cloud/
---

# Bitbucket 공식 참조 노트

## 1. 공식 소스

| 소스                      | URL                                                     | 용도         |
|---------------------------|---------------------------------------------------------|--------------|
| Bitbucket pricing         | https://www.atlassian.com/software/bitbucket/pricing    | Cloud 요금제 |
| Bitbucket Data Center     | https://www.atlassian.com/software/bitbucket/enterprise | 자체 설치형  |
| Bitbucket Cloud 지원 문서 | https://support.atlassian.com/bitbucket-cloud/          | 기능 문서    |

## 2. 검증된 사실 (2026-11-23)

| 항목           | 값                                                                   | 출처       |
|----------------|----------------------------------------------------------------------|------------|
| Cloud Free     | 사용자 5명까지 무료                                                  | pricing    |
| Cloud Standard | 사용자당 월 3.65달러                                                 | pricing    |
| Cloud Premium  | 사용자당 월 8달러                                                    | pricing    |
| 빌드 시간 계산 | Pipelines 빌드 시간은 러너 크기를 곱해 계산 (2× 러너에서 5분 = 10분) | pricing    |
| 자체 설치형    | Data Center: 자체 관리형, 영업 문의(유료)                            | enterprise |
| CI/CD          | Bitbucket Pipelines (Cloud에 포함)                                   | pricing    |

요금은 바뀔 수 있으므로 쓰기 전에 pricing 페이지에서 다시 확인합니다.

## 3. 검증 기록

- 1차: atlassian.com pricing·enterprise 페이지에서 확인했습니다.
- 2차: pricing 페이지의 요금제 표와 빌드 시간 설명 문단을 다시 대조했습니다. 상용 서비스라 계정이 필요한 기능은 실행하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
