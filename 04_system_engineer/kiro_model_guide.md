# Kiro CLI 모델 가이드

## 모델 목록

| 모델                | 크레딧 배율 | 컨텍스트 | 특징                        |
|---------------------|-------------|----------|-----------------------------|
| `auto` (기본)       | 1.00x       | -        | 작업별 최적 모델 자동 선택  |
| `claude-opus-4.6`   | 2.20x       | 1M       | 최고 추론 능력, 최신 Opus   |
| `claude-sonnet-4.6` | 1.30x       | 1M       | 성능/비용 균형, 최신 Sonnet |
| `claude-sonnet-4`   | 1.30x       | -        | 일반 코딩/추론              |
| `claude-haiku-4.5`  | 0.40x       | -        | 경량, 빠른 응답             |
| `deepseek-3.2`      | 0.25x       | -        | 실험적 프리뷰               |
| `minimax-m2.5`      | 0.25x       | -        | 실험적 프리뷰               |
| `qwen3-coder-next`  | 0.05x       | -        | 최저 비용, 코딩 특화        |

> ⚠️ 모델 목록은 리전과 시점에 따라 달라질 수 있습니다.

## 용도별 추천

| 용도                         | 추천 모델           | 이유                                |
|------------------------------|---------------------|-------------------------------------|
| 일반 작업 (기본)             | `auto`              | 작업별 최적 모델 자동 선택          |
| 복잡한 아키텍처 설계         | `claude-opus-4.6`   | 최고 추론 능력, 긴 컨텍스트 필요 시 |
| 장애 분석 / 근본 원인 추적   | `claude-opus-4.6`   | 복잡한 인과관계 추론                |
| 일상 코딩 / 스크립트 작성    | `claude-sonnet-4.6` | 성능/비용 균형                      |
| 문서 작성 / README / 가이드  | `claude-sonnet-4.6` | 충분한 품질, 합리적 비용            |
| 간단한 질문 / 명령어 확인    | `claude-haiku-4.5`  | 빠른 응답, 저렴                     |
| 반복 작업 / CI/CD 자동화     | `claude-haiku-4.5`  | 비용 절감, 속도 우선                |
| 대량 코드 생성 / 비용 최소화 | `qwen3-coder-next`  | 0.05x 최저 비용, 코딩 특화          |
| 마이그레이션 계획 수립       | `claude-opus-4.6`   | 단계별 추론, 리스크 분석            |
| Ansible / Terraform 작성     | `claude-sonnet-4.6` | 코드 품질과 비용 균형               |

## 인프라 엔지니어 시나리오별 추천

```
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│ 고비용 / 고품질            | 중간                       | 저비용 / 빠름              |
│ claude-opus-4.6 (2.20x)   │ claude-sonnet-4.6 (1.30x) │ claude-haiku-4.5 (0.40x)  │
├───────────────────────────┴───────────────────────────┴───────────────────────────┘
│ - 아키텍처 설계            | - 코드 작성/리뷰           | - 명령어 확인              |
│ - 장애 원인 분석           | - 문서 작성                | - 간단한 질문              |
│ - 마이그레이션 계획        | - Ansible/Terraform        | - 반복 자동화              |
│ - 보안 취약점 분석         | - 로그 분석                | - CI/CD 파이프라인         |
└───────────────────────────┬───────────────────────────┬───────────────────────────┐
```

## 모델 변경 방법

```bash
# 채팅 중 대화형 선택
/model

# 직접 지정
/model claude-sonnet-4.6

# 현재 모델을 기본값으로 저장
/model set-current-as-default

# CLI 시작 시 지정
kiro-cli chat --model claude-opus-4.6

# 영구 기본 모델 설정
kiro-cli settings chat.defaultModel claude-sonnet-4.6

# 사용 가능한 모델 목록
kiro-cli chat --list-models
```

## 에이전트별 모델 고정

특정 에이전트에 모델을 고정하면 매번 변경할 필요 없습니다:

```json
// ~/.kiro/agents/infra.json
{
  "name": "infra",
  "model": "claude-opus-4.6",
  "description": "아키텍처 설계 / 장애 분석 전용"
}
```

```json
// ~/.kiro/agents/daily.json
{
  "name": "daily",
  "model": "claude-sonnet-4.6",
  "description": "일상 코딩 / 문서 작업"
}
```

## 크레딧 확인

```bash
/usage
```

## 선택 우선순위

```
에이전트 model 필드 > --model 옵션 > chat.defaultModel 설정 > auto
```

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-14

© 2026 siasia86. Licensed under CC BY 4.0.
