# 유사 GitHub 리포지토리

정보 수집 및 벤치마킹 목적으로 유사한 성격의 GitHub 리포지토리를 정리합니다.

## 목차

| 섹션                                                                                         |
|----------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 리포지토리 목록](#2-리포지토리-목록) / [3. 비교 분석](#3-비교-분석) |
| [4. 참고할 점](#4-참고할-점) / [5. 차별화 전략](#5-차별화-전략)                              |

---

## 1. 개요

이 문서는 SE/SRE/DevOps 분야의 지식 베이스·리소스 모음 리포지토리를 정리합니다. 유사 repo의 구조와 특징을 파악하여 우리 repo의 콘텐츠 방향과 품질 기준을 보완합니다.

### 분류 기준

| 유형               | 설명                      | 예시             |
|--------------------|---------------------------|------------------|
| Awesome List       | 도구/서비스 링크 큐레이션 | awesome-sysadmin |
| Knowledge Base     | 직접 작성한 개념·가이드   | 이 repo          |
| Exercise/Interview | Q&A, 면접 대비            | devops-exercises |
| Handbook           | 조직 운영 지침서          | gitlab-handbook  |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 리포지토리 목록

### 대규모 (10K+ ★, 2026-07-27 기준)

| 리포지토리                                                                                          | Stars   | 유형      | 문서 언어 | 설명                                          |
|-----------------------------------------------------------------------------------------------------|---------|-----------|-----------|-----------------------------------------------|
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)             | 359,318 | Knowledge | EN        | 대규모 시스템 설계 및 면접 학습 리소스        |
| [trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) | 235,347 | Awesome   | EN        | cheatsheet, 도구, one-liner, 보안 리소스 종합 |
| [jlevy/the-art-of-command-line](https://github.com/jlevy/the-art-of-command-line)                   | 161,931 | Guide     | EN        | 커맨드 라인 활용 노트와 팁                    |
| [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises)                   | 83,396  | Exercise  | EN        | Linux, AWS, K8s, Docker, Python Q&A·실습      |
| [kahun/awesome-sysadmin](https://github.com/kahun/awesome-sysadmin)                                 | 24,328  | Awesome   | EN        | 시스템 관리 오픈소스 도구 목록                |
| [dastergon/awesome-sre](https://github.com/dastergon/awesome-sre)                                   | 13,401  | Awesome   | EN        | SRE·Production Engineering 리소스 링크        |

### 중규모 (1K~10K ★, 2026-07-27 기준)

| 리포지토리                                                                                | Stars | 유형      | 문서 언어 | 설명                                    |
|-------------------------------------------------------------------------------------------|-------|-----------|-----------|-----------------------------------------|
| [mxssl/sre-interview-prep-guide](https://github.com/mxssl/sre-interview-prep-guide)       | 9,040 | Guide     | EN        | SRE 면접 준비 리소스                    |
| [linkedin/school-of-sre](https://github.com/linkedin/school-of-sre)                       | 8,131 | Course    | EN        | LinkedIn의 신입 SRE 온보딩 교육 과정    |
| [brave-people/brave-tech-interview](https://github.com/brave-people/brave-tech-interview) | 4,460 | Interview | KR        | 현직자가 해설하는 한국어 기술 면접 자료 |

### 핸드북/운영 가이드

| 리소스                                                            | 유형     | 문서 언어 | 설명                           |
|-------------------------------------------------------------------|----------|-----------|--------------------------------|
| [GitLab Handbook](https://handbook.gitlab.com/)                   | Handbook | EN        | GitLab 전사 운영 핸드북 (공개) |
| [Google SRE Book](https://sre.google/sre-book/table-of-contents/) | Handbook | EN        | Google SRE Book (무료 온라인)  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 비교 분석

### 형식 비교

| 항목             | Awesome List | devops-exercises    | 이 repo                          |
|------------------|--------------|---------------------|----------------------------------|
| 직접 작성 가이드 | ❌ (링크형)  | ✅ (Q&A·해설)       | ✅                               |
| 설치/설정 포함   | ❌           | ✅ (실습·스크립트)  | ✅                               |
| 코드 예시        | ❌           | ✅                  | ✅                               |
| 운영 시나리오    | ❌           | 🟡 (주제별 실습)    | ✅                               |
| 사실 검증 시스템 | ❌           | ❌                  | ✅ (`_reference` + `fact-check`) |
| 한국어           | ❌           | ❌ (기본 문서 기준) | ✅                               |

### 커버리지 비교

| 분야             | awesome-sysadmin      | devops-exercises      | 이 repo                    |
|------------------|-----------------------|-----------------------|----------------------------|
| Linux 기초/고급  | 🟡 (도구 목록)        | ✅ (Q&A·실습)         | ✅ (가이드 30개)           |
| DB 튜닝/운영     | 🟡 (RDBMS·NoSQL 도구) | ✅ (Databases 주제)   | ✅ (가이드 27개)           |
| 보안 (CVE/CWE)   | 🟡 (보안 도구)        | ✅ (Security 주제)    | ✅ (CVE 5건 + CWE 4건)     |
| IaC (Ansible/TF) | ✅                    | ✅                    | ✅ (가이드 11개)           |
| 클라우드 (AWS)   | 🟡 (클라우드 도구)    | ✅ (Cloud·AWS 주제)   | ✅ (AWS 가이드 6개)        |
| 파이프라인       | 🟡 (CI/CD·로그 도구)  | ✅ (CI/CD·Kafka 주제) | ✅ (데이터 파이프라인 4개) |
| AI/에이전트      | ❌                    | ❌                    | ✅ (AI 도구 가이드 8개)    |

### 품질 관리 비교

| 항목               | 확인된 구현                         | 위치                                                |
|--------------------|-------------------------------------|-----------------------------------------------------|
| 스타일 검사 (lint) | Markdown 스타일 및 표 정렬 검사     | `md-style-check.py`                                 |
| 사실 검증          | 공식 출처 대조 프롬프트와 팩트 노트 | `00_readme.md/prompts/fact-check.md`, `_reference/` |
| 보안 검사 설정     | 비밀정보 탐지 예외 설정             | `.gitleaks.toml`                                    |
| 링크 유효성        | 내부 링크·앵커·목차 검사            | `md-link-check.py`                                  |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 참고할 점

### trimstray/the-book-of-secret-knowledge (235,347 ★)

- **강점**: 방대한 커버리지, 카테고리 정리, 원라이너 cheatsheet
- **제약**: 주요 콘텐츠가 단일 `README.md`에 집중됨
- **참고**: 카테고리 분류 방식, README 구조

### bregman-arie/devops-exercises (83,396 ★)

- **강점**: Q&A와 실습, 기술별 분류
- **제약**: 공식 README에서 대부분의 질문과 실습이 실제 면접을 나타내지는 않는다고 명시함
- **참고**: 주제별 분류, 질문·답변 패턴

### google/sre-book

- **강점**: Google 운영 경험을 바탕으로 원칙과 사례를 함께 설명함
- **제약**: Google의 시스템과 조직 환경을 중심으로 구성됨
- **참고**: 모니터링, 알림, 장애 대응, 포스트모템 구성

### linkedin/school-of-sre (8,131 ★)

- **강점**: 교육 과정 형태, 단계별 학습, 실습 포함
- **구성**: 공개 과정이 Level 101과 Level 102로 구성됨
- **참고**: 개념 설명과 실습을 결합한 구조

[⬆ 목차로 돌아가기](#목차)

---

## 5. 차별화 전략

| 전략               | 설명                                           |
|--------------------|------------------------------------------------|
| 한국어 실무 가이드 | 영문 링크 모음이 아닌 **한국어로 직접 작성**   |
| 검증 기반          | `_reference` 팩트 노트 + `fact-check` 프로세스 |
| 설치→운영→튜닝     | 단편 지식이 아닌 **end-to-end 흐름**           |
| 보안 실습          | CVE 분석 + CWE 실습 환경 (VM + playbook)       |
| 품질 자동화        | `md-style-check.py`, `md-link-check.py`        |
| 시니어 콘텐츠      | 장애 관리, SLO, 용량 계획 등 (TODO 진행 중)    |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Book of Secret Knowledge: [github.com/trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) — ★★☆☆☆
- DevOps Exercises: [github.com/bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises) — ★★☆☆☆
- Awesome SRE: [github.com/dastergon/awesome-sre](https://github.com/dastergon/awesome-sre) — ★★☆☆☆
- School of SRE: [github.com/linkedin/school-of-sre](https://github.com/linkedin/school-of-sre) — ★★★☆☆
- Google SRE Book: [sre.google/sre-book](https://sre.google/sre-book/table-of-contents/) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-27

© 2026 siasia86. Licensed under CC BY 4.0.
