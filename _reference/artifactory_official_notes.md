---
name: artifactory-official-notes
description: JFrog Artifactory 판·에디션·저장소 유형·요금 공식 자료 정리 (상용, 실행 시험 없음).
tags:
  - artifactory
  - jfrog
  - artifact-repository
  - pricing
last_checked: 2026-11-24
sources:
  - https://docs.jfrog.com/releases/docs/artifactory-self-managed-releases
  - https://jfrog.com/pricing/
  - https://jfrog.com/artifactory/
  - https://jfrog.com/container-registry/
  - https://jfrog.com/community/open-source/
  - https://docs.jfrog.com/installation/docs/install-artifactory-linux-archive
  - https://docs.jfrog.com/artifactory/docs/repository-management-overview
  - https://docs.jfrog.com/artifactory/docs/federated-repositories
---

# JFrog Artifactory 공식 자료 참조 노트

## 1. 판 (2026-11-24)

| 항목           | 내용                                                              | 근거                      |
|----------------|-------------------------------------------------------------------|---------------------------|
| 자체 관리 최신 | 7.173.21과 7.161.42 (2026-11-17), 이전 7.173.18 (11-03)           | Self-Managed Releases     |
| 릴리스 노트    | 공개 페이지는 요약만, 전체는 MyJFrog 로그인 필요                  | 같은 페이지               |
| 7.161.24       | 원격 플러그인 배포 기본 꺼짐                                      | 같은 페이지               |
| OSS 배포       | 설치 문서에 OSS 7.161.15와 C/C++ Community Edition 압축 파일 경로 | Linux 압축 파일 설치 문서 |

## 2. 에디션과 요금 (jfrog.com/pricing, 2026-11-03 수정, 2026-11-24 확인)

| 배포      | 등급         | 가격                                  | 비고               |
|-----------|--------------|---------------------------------------|--------------------|
| SaaS      | Pro          | 월 $50 (정가 월 $150, 기간 한정 할인) | 기본 사용량 25GB   |
| SaaS      | Enterprise X | 월 $950부터                           | 기본 사용량 125GB  |
| SaaS      | Enterprise+  | 별도 문의                             | -                  |
| 자체 관리 | Pro X        | 연 $27,000부터                        | 서버 1대, 24/7 SLA |
| 자체 관리 | Enterprise X | 연 $51,000부터                        | 서버 3대, 24/7 SLA |
| 자체 관리 | Enterprise+  | 별도 문의                             | 멀티사이트         |

- 무료 클라우드 등급은 요금 페이지에서 확인하지 못했습니다(페이지 일부만 읽음).
- JFrog Container Registry: 온프레미스 전용 무료 판, 컨테이너 레지스트리 기능만 있습니다.
- Artifactory OSS: 현재도 배포되며 기능 범위는 오픈소스 안내 페이지에 있습니다.

## 3. 기능

- 지원 형식: 제품 페이지 표기 "60+ artifact types" (패키지·파일·AI 자산).
- 저장소 유형:

| 유형      | 역할                                      |
|-----------|-------------------------------------------|
| local     | 직접 올린 결과물 보관                     |
| remote    | 외부 저장소 캐시 프록시                   |
| virtual   | 같은 패키지 유형 저장소를 URL 하나로 묶음 |
| federated | 여러 사이트 간 양방향 동기화              |

- federated 조건(federated 문서, 2026-07-29 갱신): "Enterprise X or Enterprise+ subscription with Artifactory 7.18.3 or later".
- SaaS는 3개 클라우드의 30개 리전에서 제공합니다(요금 페이지).

## 4. 시험

상용 제품이라 계정·사용권 없이 실행하지 않았습니다. Nexus 용어와의 대응은 local=hosted, remote=proxy, virtual=group입니다.
