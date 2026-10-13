# AI 시대 일하는 사람의 다섯 원형
<!-- reference: _reference/ai_work_archetypes_notes.md -->

Claude Code를 만든 Anthropic의 Boris Cherny(보리스 체르니)가 제시한 Prototyper·Builder·Sweeper·Grower·Maintainer를 정리합니다. 제안의 출처와 의미를 설명하고, 시스템 엔지니어링 업무에 적용하는 예시를 제공합니다.

## 목차

| 섹션                                                                                                |
|-----------------------------------------------------------------------------------------------------|
| [1. 제안자와 배경](#1-제안자와-배경) / [2. 다섯 원형](#2-다섯-원형)                                 |
| [3. 직무와 원형의 관계](#3-직무와-원형의-관계) / [4. 제품 단계별 팀 구성](#4-제품-단계별-팀-구성)   |
| [5. AI와 사람의 판단](#5-ai와-사람의-판단) / [6. 시스템 엔지니어링 적용](#6-시스템-엔지니어링-적용) |
| [7. 업무 점검과 한계](#7-업무-점검과-한계)                                                          |

---

## 1. 제안자와 배경

제안자는 Anthropic 공동창업자가 아니라 Claude Code를 만든 Boris Cherny입니다. Anthropic 공식 웨비나에서도 Claude Code 제작진으로 소개됩니다. [공식 웨비나](https://resources.anthropic.com/webinar/claude-code-live).

그는 엔지니어링·제품·디자인·데이터 사이의 역할 경계가 변하는 상황에서 자신의 팀을 다섯 원형으로 설명했습니다. Readside 전재의 게시일은 2026-06-28입니다. [원문 링크](https://x.com/bcherny/status/2071379474277613732), [전재 자료](https://www.readside.dev/read/9edf9c1c-b2ec-4d27-8db6-2e23e5bc501f).

이 조사는 X 원문의 직접 열람이 제한되어 전재 자료와 보도를 대조했습니다. 날짜 표기 차이와 자료별 접근 상태는 [참조 노트](../../_reference/ai_work_archetypes_notes.md)에 기록했습니다. 다섯 원형은 팀 구성에 관한 관찰과 제안이며, 확정된 미래 직업 목록으로 읽지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 다섯 원형

다음 정의는 Cherny의 게시물을 전재한 자료의 요약입니다. 한국어 명칭은 이해를 돕기 위한 번역입니다. [전재 자료](https://www.readside.dev/read/9edf9c1c-b2ec-4d27-8db6-2e23e5bc501f).

| 원형       | 한국어 설명          | 핵심 역할                                               |
|------------|----------------------|---------------------------------------------------------|
| Prototyper | 프로토타이퍼·탐색자  | 새로운 아이디어를 다수 탐색하며, 상당수는 출시하지 않음 |
| Builder    | 빌더·구현자          | 아이디어를 운영 가능한 제품·인프라로 빠르게 구현        |
| Sweeper    | 스위퍼·정리자        | UI·코드·시스템 단순화, 기능 제거, 성능 개선             |
| Grower     | 그로워·성장 담당     | 기존 제품을 반복 개선해 제품과 시장의 적합성을 높임     |
| Maintainer | 메인테이너·유지 담당 | 성숙한 시스템의 보안·신뢰성·속도·효율을 책임짐          |

아래 질문과 산출물은 정의를 실제 업무에 옮긴 **이 문서의 적용 예시**입니다.

| 원형       | 업무를 시작하는 질문                    | 산출물 예시                           |
|------------|-----------------------------------------|---------------------------------------|
| Prototyper | 어떤 가능성을 먼저 시험할까요?          | 가설, 작은 실험, 시제품, 중단 이유    |
| Builder    | 운영 환경에서 쓰려면 무엇이 필요할까요? | 구현, 배포 절차, 검증 결과, 운영 인계 |
| Sweeper    | 무엇을 줄이거나 없앨 수 있을까요?       | 중복 제거, 폐기 계획, 구조 단순화     |
| Grower     | 사용자가 더 잘 쓰도록 무엇을 바꿀까요?  | 피드백 분석, 개선 실험, 전후 비교     |
| Maintainer | 규모가 커져도 어떻게 품질을 지킬까요?   | 점검 기록, 복구 절차, 용량·보안 관리  |

예를 들어 동작하는 시제품을 만드는 일과 운영 품질을 갖추는 일은 완료 기준이 다릅니다. 실험 단계에서는 가설을 판단할 증거가 중요하고, 구현 단계에서는 실제 환경에서 검증된 동작과 인계 가능한 절차가 필요합니다.

스위퍼는 작은 버그 수정에만 국한되지 않습니다. 기능을 제거하는 `unship`도 정의에 포함되므로, 추가된 기능과 복잡성이 계속 필요한지 검토하는 업무까지 생각할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 직무와 원형의 관계

Cherny는 한 사람이 두 원형, 때로 세 원형에 걸칠 수 있으며 디자이너·엔지니어·PM·데이터 직무 모두에 이 구분을 적용할 수 있다고 설명합니다. [보도 자료](https://tech.yahoo.com/ai/claude/articles/5-job-archetypes-future-according-141801028.html).

직무는 전문 분야와 책임 범위를 설명하고, 원형은 현재 업무에서 어떤 방식으로 기여하는지 살펴보는 데 쓸 수 있습니다. 아래 대응은 고정된 분류가 아닌 적용 예시입니다.

| 직무·업무       | 가능한 원형 조합   | 기여 예시                         |
|-----------------|--------------------|-----------------------------------|
| 시스템 엔지니어 | Builder·Maintainer | 인프라 구축과 안정적 운영         |
| SRE             | Sweeper·Maintainer | 운영 복잡성 축소와 신뢰성 관리    |
| 제품 관리자     | Prototyper·Grower  | 문제 가설 탐색과 제품 개선        |
| 디자이너        | Prototyper·Sweeper | 경험 시제품과 화면 흐름 단순화    |
| 데이터 담당     | Grower·Builder     | 개선 효과 분석과 데이터 처리 구현 |

같은 엔지니어가 신규 서비스에서는 빌더, 기존 서비스 정리에서는 스위퍼로 기여할 수 있습니다. 개인에게 원형 하나를 영구적으로 붙이기보다 프로젝트와 기간을 함께 기록하면 역할 변화를 설명하기 쉽습니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 제품 단계별 팀 구성

Cherny가 제시한 단계별 조합은 다음과 같습니다. PMF(Product-Market Fit)는 제품과 시장의 적합성을 뜻합니다. [전재 자료](https://www.readside.dev/read/9edf9c1c-b2ec-4d27-8db6-2e23e5bc501f), [교차 확인 자료](https://thakicloud.com/tech-blog/en/culture/five-product-role-archetypes/).

| 제품 단계        | 중심 조합                  | 추가로 필요한 원형          |
|------------------|----------------------------|-----------------------------|
| 신규·PMF 확보 전 | Prototyper·Builder·Sweeper | 원문에서 별도 지정하지 않음 |
| PMF 확보 후 성장 | Builder·Sweeper·Grower     | 일부 Maintainer             |
| 강한 PMF 확보    | Sweeper·Grower·Maintainer  | 일부 Builder                |

스위퍼가 세 조합 모두에 등장합니다. 이 표에서 도출할 수 있는 해석은 실험·성장·성숙 어느 단계에서도 정리와 단순화가 필요하다는 것입니다. 조합은 인원 비율을 뜻하지 않으며, 초기 제품의 보안·운영 책임을 생략하라는 지시도 아닙니다.

실무에서는 먼저 현재 병목을 적고 해당 업무를 맡을 사람을 정할 수 있습니다. 아이디어는 많지만 출시가 지연되면 구현 업무를, 기능은 늘지만 사용 경험이 복잡해지면 정리 업무를 점검하는 방식입니다.

[⬆ 목차로 돌아가기](#목차)

## 5. AI와 사람의 판단

Anthropic의 내부 업무 연구는 AI 사용으로 직원의 업무 범위가 넓어지는 모습과 결과를 검증하는 필요성을 함께 보고합니다. 이는 원형이 직무를 가로지를 수 있다는 배경을 이해하는 자료입니다. 다섯 원형 자체의 타당성을 검증한 연구는 아닙니다. [공식 연구](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).

아래는 AI에 요청할 작업과 사람이 검토할 판단을 나눈 **적용 예시**입니다. 특정 모델의 성능 보장은 포함하지 않습니다.

| 원형       | AI에 요청할 작업 예시             | 사람이 검토할 판단             |
|------------|-----------------------------------|--------------------------------|
| Prototyper | 대안 정리, 작은 시제품 초안       | 실험할 문제와 성공·중단 기준   |
| Builder    | 구현 초안, 테스트 후보, 문서 초안 | 설계의 적합성과 운영 완료 기준 |
| Sweeper    | 중복·미사용 후보 조사, 정리안     | 제거 영향과 유지할 기능        |
| Grower     | 피드백 분류, 개선 가설 정리       | 지표의 의미와 사용자 가치      |
| Maintainer | 로그 요약, 점검 항목, 복구안      | 장애 영향과 변경·복구 결정     |

요청에는 목표, 대상 범위, 완료 기준과 검증 근거를 포함합니다. 예를 들어 미사용 기능을 찾도록 요청할 때는 호출 기록·사용자 영향·의존 관계를 확인할 근거도 지정합니다. 후보 목록만으로 제거를 확정하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 시스템 엔지니어링 적용

내부 배포 도구를 만드는 상황에 다섯 원형을 적용한 예시입니다. Cherny가 제시한 실제 사례는 아닙니다.

| 업무                                         | 담당 원형  | 확인할 결과                  |
|----------------------------------------------|------------|------------------------------|
| 반복되는 배포 문제를 조사하고 작은 도구 실험 | Prototyper | 해결할 문제와 실험 결과      |
| 인증·오류 처리·배포 흐름 구현                | Builder    | 검증된 동작과 운영 인계 자료 |
| 중복 옵션·스크립트·불필요한 경로 정리        | Sweeper    | 기능 영향과 복잡성 감소      |
| 사용 팀의 피드백을 받아 흐름 개선            | Grower     | 사용 완료율·소요 시간의 변화 |
| 업데이트·장애 대응·복구·용량 관리            | Maintainer | 운영 품질과 복구 가능성      |

실제 업무에서는 이 활동들이 겹치거나 앞 단계로 되돌아갈 수 있습니다. 한 사람이 여러 원형을 맡더라도 각 업무의 산출물과 완료 기준을 구분하면 빠뜨린 책임을 찾기 쉽습니다.

관련 자료: [인프라 직무 비교](../roadmap/infra_roles_comparison.md), [SRE 로드맵](../roadmap/sre_roadmap.md), [AI 개발 요청 템플릿](./ai_development_request_template.md).

[⬆ 목차로 돌아가기](#목차)

## 7. 업무 점검과 한계

다음은 업무 회고에 사용할 질문입니다. 성격 검사나 검증된 채용 평가표가 아닙니다.

- 최근 완료한 일에서 탐색·구현·정리·성장·유지 중 어떤 기여를 했나요?
- 현재 프로젝트의 병목을 풀기 위해 필요한 기여는 무엇인가요?
- 정리와 운영 업무에도 담당자·시간·완료 기준이 있나요?
- 원형을 맡길 때 필요한 전문 지식과 책임 범위를 함께 확인했나요?
- 다음 프로젝트에서 경험할 다른 원형은 무엇인가요?

이 분류만으로 개발자·디자이너·운영자의 전문성이 사라진다고 결론 내릴 수 없습니다. 다섯 유형이 모든 직업을 포괄한다는 근거도 확인되지 않았습니다. 한 팀의 관찰을 조직 전체에 적용하려면 실제 업무와 성과를 따로 확인해야 합니다.

적용 시에는 새 기능의 수뿐 아니라 불필요한 기능을 줄인 결과와 운영 품질을 지킨 결과도 기록할 수 있습니다. 사람을 고정된 유형으로 제한하지 않고, 지금 필요한 일을 함께 설명하는 용도로 활용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [Boris Cherny 원문 링크](https://x.com/bcherny/status/2071379474277613732) — 직접 열람 제한.
- [Readside 원문 전재](https://www.readside.dev/read/9edf9c1c-b2ec-4d27-8db6-2e23e5bc501f) — 정의와 단계별 조합.
- [Business Insider / Yahoo 보도](https://tech.yahoo.com/ai/claude/articles/5-job-archetypes-future-according-141801028.html) — 검색 본문으로 교차 확인.
- [Anthropic 공식 웨비나](https://resources.anthropic.com/webinar/claude-code-live) — 제작진 소개.
- [Anthropic 내부 업무 연구](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) — AI 활용 배경과 연구 한계.
- [출처와 사실 대조 기록](../../_reference/ai_work_archetypes_notes.md).

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-13

**마지막 업데이트**: 2026-10-13

© 2026 siasia86. Licensed under CC BY 4.0.
