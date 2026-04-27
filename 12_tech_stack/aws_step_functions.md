# AWS Step Functions

## 목차

| 단계  | 섹션                                                                                                      |
|-------|-----------------------------------------------------------------------------------------------------------|
| 기본  | [1. 개요](#1-개요) / [2. 핵심 개념](#2-핵심-개념) / [3. 상태 유형](#3-상태-유형)                         |
| 실전  | [4. ASL 작성](#4-asl-작성) / [5. 실행 모드](#5-실행-모드) / [6. 에러 처리](#6-에러-처리)                 |
| 운영  | [7. 모니터링](#7-모니터링) / [8. 비용](#8-비용) / [9. Tips](#9-tips)                                     |

---

## 1. 개요

AWS Step Functions는 AWS 서비스와 Lambda 등을 **시각적 워크플로우**로 연결하는 서버리스 오케스트레이터.
코드 없이 분산 애플리케이션의 실행 순서, 분기, 병렬 처리, 재시도를 정의합니다.

```
┌──────────────────────────────────────────────────────┐
│                  State Machine                       │
│                                                      │
│  [Start] -> [Task] -> [Choice] -> [Task] -> [End]    │
│                           │                          │
│                           v                          │
│                        [Fail]                        │
└──────────────────────────────────────────────────────┘
```

- 상태 머신(State Machine): 워크플로우 전체 정의
- 상태(State): 워크플로우의 각 단계
- 실행(Execution): 상태 머신의 1회 실행 인스턴스

---

## 2. 핵심 개념

### Amazon States Language (ASL)

워크플로우를 JSON으로 정의하는 언어.

```json
{
  "Comment": "간단한 예시",
  "StartAt": "HelloWorld",
  "States": {
    "HelloWorld": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:123456789:function:hello",
      "End": true
    }
  }
}
```

### 실행 유형 비교

| 구분             | Standard                  | Express                        |
|-----------------|---------------------------|--------------------------------|
| 최대 실행 시간   | 1년                       | 5분                            |
| 실행 이력        | 90일 보관                 | CloudWatch Logs만              |
| 과금 기준        | 상태 전환 횟수             | 실행 횟수 + 실행 시간           |
| 적합 용도        | 장기 비즈니스 프로세스     | 고빈도 단기 이벤트 처리         |
| 정확히 1회 실행  | 보장                      | 최소 1회 (중복 가능)            |

---

## 3. 상태 유형

| 상태 유형  | 설명                                      | 주요 필드                        |
|-----------|------------------------------------------|----------------------------------|
| `Task`    | Lambda, ECS, SNS 등 작업 실행            | `Resource`, `TimeoutSeconds`     |
| `Choice`  | 조건 분기                                | `Choices`, `Default`             |
| `Parallel`| 여러 브랜치 병렬 실행                    | `Branches`                       |
| `Map`     | 배열 항목별 반복 실행                    | `Iterator`, `MaxConcurrency`     |
| `Wait`    | 지정 시간 또는 타임스탬프까지 대기       | `Seconds`, `Timestamp`           |
| `Pass`    | 입력을 출력으로 그대로 전달 (디버깅용)   | `Result`, `ResultPath`           |
| `Succeed` | 성공 종료                                | -                                |
| `Fail`    | 실패 종료                                | `Error`, `Cause`                 |

---

## 4. ASL 작성

### 데이터 흐름 제어

```json
{
  "Type": "Task",
  "Resource": "arn:aws:lambda:...",
  "InputPath": "$.order",
  "ResultPath": "$.processResult",
  "OutputPath": "$.processResult"
}
```

| 필드          | 역할                                      |
|--------------|------------------------------------------|
| `InputPath`  | 전체 입력 중 Task에 전달할 부분 선택      |
| `ResultPath` | Task 결과를 저장할 입력 내 경로           |
| `OutputPath` | 다음 상태로 전달할 출력 선택              |
| `Parameters` | 입력 재구성 (정적 값 + 동적 값 혼합)      |

### Choice 상태 예시

```json
{
  "Type": "Choice",
  "Choices": [
    {
      "Variable": "$.status",
      "StringEquals": "approved",
      "Next": "ApproveOrder"
    },
    {
      "Variable": "$.amount",
      "NumericGreaterThan": 1000,
      "Next": "HighValueProcess"
    }
  ],
  "Default": "RejectOrder"
}
```

### Map 상태 예시 (배열 병렬 처리)

```json
{
  "Type": "Map",
  "ItemsPath": "$.items",
  "MaxConcurrency": 5,
  "Iterator": {
    "StartAt": "ProcessItem",
    "States": {
      "ProcessItem": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:...",
        "End": true
      }
    }
  }
}
```

---

## 5. 실행 모드

### SDK Integration (권장)

Lambda 호출 없이 AWS 서비스를 직접 호출.

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::dynamodb:putItem",
  "Parameters": {
    "TableName": "orders",
    "Item": {
      "orderId": { "S.$": "$.orderId" }
    }
  }
}
```

### 통합 패턴

| 패턴                        | 동작                                      | 사용 시점                    |
|----------------------------|------------------------------------------|------------------------------|
| Request-Response (기본)     | 호출 후 즉시 다음 상태로                  | 비동기 작업                  |
| `.sync`                    | 작업 완료까지 대기                        | ECS Task, Glue Job 등        |
| `.waitForTaskToken`        | 외부 시스템 콜백 대기                     | 사람 승인, 외부 API 연동      |

---

## 6. 에러 처리

### Retry

```json
{
  "Type": "Task",
  "Resource": "arn:aws:lambda:...",
  "Retry": [
    {
      "ErrorEquals": ["Lambda.ServiceException", "Lambda.TooManyRequestsException"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2
    }
  ]
}
```

### Catch

```json
{
  "Catch": [
    {
      "ErrorEquals": ["States.TaskFailed"],
      "Next": "HandleError",
      "ResultPath": "$.error"
    },
    {
      "ErrorEquals": ["States.ALL"],
      "Next": "FallbackHandler"
    }
  ]
}
```

### 주요 내장 에러 코드

| 에러 코드                  | 발생 조건                          |
|---------------------------|-----------------------------------|
| `States.ALL`              | 모든 에러 (catch-all)              |
| `States.TaskFailed`       | Task 실행 실패                     |
| `States.Timeout`          | TimeoutSeconds 초과                |
| `States.HeartbeatTimeout` | HeartbeatSeconds 내 응답 없음      |
| `States.NoChoiceMatched`  | Choice에서 매칭 없고 Default 없음  |

---

## 7. 모니터링

- 실행 이력: 콘솔에서 각 상태별 입출력 시각적 확인 가능
- CloudWatch Metrics: `ExecutionsStarted`, `ExecutionsFailed`, `ExecutionTime`
- X-Ray 연동: Lambda 포함 전체 실행 추적

```bash
# 실행 목록 조회
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:ap-northeast-1:123456789:stateMachine:MyMachine \
  --status-filter FAILED

# 실행 상세 조회
aws stepfunctions describe-execution \
  --execution-arn arn:aws:states:ap-northeast-1:123456789:execution:MyMachine:exec-id
```

---

## 8. 비용

| 항목              | Standard                        | Express                              |
|------------------|---------------------------------|--------------------------------------|
| 무료 티어         | 월 4,000회 상태 전환             | 월 1,000회 실행, 100초               |
| 과금 단위         | 상태 전환 1만 회당 $0.025        | 실행 100만 회당 $1 + GB-초당 $0.00001 |

> 💡 Express는 고빈도 단기 워크플로우에서 Standard 대비 90% 이상 비용 절감 가능.

---

## 9. Tips

### 설계

- Lambda 체이닝 대신 Step Functions 사용: Lambda에서 다른 Lambda를 직접 호출하면 에러 처리와 재시도가 복잡해짐. Step Functions로 오케스트레이션 분리.
- Map의 `MaxConcurrency` 설정 필수: 기본값 0(무제한)은 하위 서비스 throttling 유발.
- `ResultPath`로 원본 입력 보존: `"ResultPath": "$.taskResult"` 로 원본 입력과 결과를 함께 유지.

### 운영

- 실행 이름 지정: `--name` 옵션으로 의미 있는 이름 부여 → 콘솔 검색 용이.
- 타임아웃 반드시 설정: `TimeoutSeconds` 미설정 시 1년까지 실행 유지 → 비용 발생.
- Express + SQS 조합: 고빈도 이벤트는 SQS로 버퍼링 후 Express로 처리.

### 디버깅

Pass 상태로 중간 데이터 확인:

```json
{
  "Type": "Pass",
  "Result": "debug checkpoint",
  "ResultPath": "$.debug",
  "Next": "NextState"
}
```

`$.Execution.Name`, `$.Execution.StartTime` 등 컨텍스트 객체 활용 가능.

---

[⬆ 목차로 돌아가기](#목차)
