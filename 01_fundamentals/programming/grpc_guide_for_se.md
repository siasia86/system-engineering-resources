# SE를 위한 gRPC 가이드
<!-- reference: _reference/grpc_official_notes.md, _reference/protobuf_official_notes.md -->

시스템 엔지니어 관점에서 gRPC를 학습하고 운영하는 가이드입니다. `.proto` 서비스 계약, RPC 호출 유형, deadline, status code, retry, TLS와 health checking에 초점을 맞춥니다.

## 목차

| 섹션                                                                                                                                                                                 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. gRPC 개요](#1-grpc-개요) / [2. SE 활용 판단](#2-se-활용-판단) / [3. 서비스 계약](#3-서비스-계약)                                                                                 |
| [4. RPC 호출 유형](#4-rpc-호출-유형) / [5. Deadline·상태·재시도](#5-deadline상태재시도) / [6. Metadata와 보안](#6-metadata와-보안)                                                   |
| [7. Health checking과 연결 운영](#7-health-checking과-연결-운영) / [8. 관측성과 장애 대응](#8-관측성과-장애-대응) / [9. 단계별 학습과 실무 프로젝트](#9-단계별-학습과-실무-프로젝트) |
| [10. CI·배포 검증](#10-ci배포-검증)                                                                                                                                                  |

---

## 1. gRPC 개요

gRPC는 다른 시스템의 service method를 로컬 호출처럼 사용할 수 있도록 하는 RPC framework입니다. 서비스와 메시지는 보통 Protocol Buffers로 정의하고, compiler가 생성한 client stub과 server interface를 사용합니다.

> RPC(Remote Procedure Call): 다른 프로세스나 시스템의 함수를 네트워크를 통해 호출하는 통신 모델입니다. 로컬 함수와 달리 지연·취소·부분 실패·직렬화·재시도를 설계해야 합니다.

### 핵심 구조

| 구성 요소             | 역할                                     |
|-----------------------|------------------------------------------|
| service definition    | 호출 가능한 method와 요청·응답 계약 정의 |
| client stub           | 원격 method 호출 API 제공                |
| server implementation | service interface 구현과 요청 처리       |
| Protocol Buffers      | 기본 메시지 정의·직렬화 형식             |
| HTTP/2 transport      | stream·metadata·status 전달              |
| channel               | 대상 endpoint와 연결 정책 관리           |

gRPC는 HTTP/2를 기반으로 하며 unary와 streaming RPC를 지원합니다. 다중 서비스가 같은 endpoint를 사용하면 연결 재사용과 장애 격리 정책을 함께 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. SE 활용 판단

### 적합한 영역

| 영역                   | gRPC 활용                       | 운영상 핵심                 |
|------------------------|---------------------------------|-----------------------------|
| 내부 control plane     | agent·scheduler·controller 통신 | deadline·mTLS·권한          |
| 고정 계약 서비스       | inventory·task·policy API       | `.proto` compatibility      |
| streaming collector    | 로그·metric·event 전달          | flow control·backpressure   |
| 다중 언어 플랫폼       | Go·Java·Python·Rust client      | 생성기·runtime 버전         |
| service mesh 내부 호출 | backend 간 RPC                  | load balancing·health check |

### REST API와 역할 분담

| 요구사항                            | 우선 검토                    |
|-------------------------------------|------------------------------|
| 브라우저·외부 개발자·단순 curl 접근 | REST API                     |
| 강한 타입의 내부 서비스 계약        | gRPC                         |
| 단방향 공개 이벤트 수신             | webhook 또는 event protocol  |
| 장시간 양방향 데이터 흐름           | gRPC bidirectional streaming |

gRPC를 선택해도 운영자가 문제를 확인할 수 있는 health endpoint, metrics, structured logs와 진단 절차를 별도로 제공합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 서비스 계약

### 최소 서비스 정의

```protobuf
syntax = "proto3";

package inventory.v1;

service Inventory {
  rpc GetHost(GetHostRequest) returns (Host);
  rpc WatchHosts(WatchHostsRequest) returns (stream Host);
}

message GetHostRequest {
  string host_id = 1;
}

message WatchHostsRequest {
  string tenant_id = 1;
}

message Host {
  string host_id = 1;
  string hostname = 2;
  repeated string addresses = 3;
}
```

### 계약 설계 기준

- package에 도메인과 version을 포함해 생성 코드 충돌을 줄입니다.
- request와 response를 별도 message로 정의해 향후 필드 확장 여지를 둡니다.
- 필드 번호는 사용 후 변경·재사용하지 않고 삭제한 번호와 이름은 `reserved`로 관리합니다.
- 서버가 처리할 수 없는 요청은 명확한 status code와 안전한 오류 세부 정보로 응답합니다.
- stream method는 종료 조건, 순서, 중복, client cancellation을 계약과 운영 문서에 기록합니다.

### 생성 코드 흐름

```text
.proto service and messages
          │
          v
protoc + language plugin
          │
          v
client stub + server interface
          │
          v
application implementation
          │
          v
integration test + compatibility gate
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. RPC 호출 유형

| 유형                    | 요청           | 응답           | 사용 예                        |
|-------------------------|----------------|----------------|--------------------------------|
| Unary                   | 단일 message   | 단일 message   | host 조회·작업 시작            |
| Server streaming        | 단일 message   | message stream | 상태 변경 watch                |
| Client streaming        | message stream | 단일 message   | batch 업로드                   |
| Bidirectional streaming | message stream | message stream | agent와 controller의 지속 연결 |

### 유형별 운영 기준

- Unary는 timeout과 retry 경계를 정하기 쉽고 일반적인 control API에 적합합니다.
- Server streaming은 client가 모든 message를 읽고 stream 종료를 처리해야 합니다.
- Client streaming은 마지막 message 이후 client half-close와 server response 시점을 정의합니다.
- Bidirectional streaming은 양쪽 stream이 독립적이므로 읽기·쓰기·취소·재연결 상태 머신을 설계합니다.
- gRPC는 하나의 RPC 호출 안에서 메시지 순서를 보장하지만, 여러 RPC 호출 사이의 전역 순서는 별도 보장하지 않습니다.

### Streaming 체크리스트

| 점검         | 질문                                                         |
|--------------|--------------------------------------------------------------|
| flow control | producer가 consumer보다 빠를 때 어떻게 제한하는가?           |
| lifecycle    | 정상 종료·server shutdown·network reset을 어떻게 구분하는가? |
| retry        | 중단된 stream을 처음부터 재생할 수 있는가?                   |
| idempotency  | 재연결 후 이미 처리한 message를 어떻게 식별하는가?           |
| memory       | 무제한 buffer와 대형 message를 어떻게 제한하는가?            |

[⬆ 목차로 돌아가기](#목차)

---

## 5. Deadline·상태·재시도

### Deadline

gRPC client는 기본 deadline을 설정하지 않을 수 있으므로 외부 호출마다 현실적인 deadline을 명시합니다. 서버가 deadline을 넘긴 작업을 계속 수행하면 thread·connection·DB slot이 누적될 수 있습니다.

```text
incoming request deadline
          │
          v
remaining budget 계산
          │
          v
outgoing RPC deadline 전파
          │
          v
deadline 초과 시 취소·정리
```

- client는 응답을 기다릴 최대 시간을 정의합니다.
- server는 취소 상태를 확인하고 시작한 장기 작업을 중단합니다.
- downstream 호출에는 전체 요청의 남은 시간 예산을 전달합니다.
- deadline 값은 정상 처리 latency, queue 대기, 재시도 횟수를 반영해 정합니다.

### Status code

| 상태                 | 일반적 의미         | 운영 판단                |
|----------------------|---------------------|--------------------------|
| `OK`                 | 정상 완료           | 응답 결과 처리           |
| `INVALID_ARGUMENT`   | 입력 오류           | client validation 수정   |
| `NOT_FOUND`          | 대상 없음           | 재시도보다 대상 확인     |
| `DEADLINE_EXCEEDED`  | 시간 예산 초과      | latency·downstream 점검  |
| `UNAVAILABLE`        | 일시적 서비스 불가  | 조건부 retry·backoff     |
| `CANCELLED`          | 호출 취소           | 원인과 작업 정리 확인    |
| `RESOURCE_EXHAUSTED` | quota·capacity 초과 | rate limit·capacity 점검 |
| `INTERNAL`           | 내부 오류           | server log와 trace 연결  |

### Retry

- retry는 실패한 호출을 새 호출로 대체하고 요청 이력을 재생하는 동작입니다.
- `UNAVAILABLE` 같은 transient failure와 애플리케이션 오류를 구분합니다.
- 최대 시도 횟수, exponential backoff, retryable status를 명시합니다.
- 비멱등 작업은 retry 전에 request ID와 중복 처리 방지를 구현합니다.
- 첫 response header가 수신된 뒤에는 추가 retry가 수행되지 않는 호출 lifecycle을 고려합니다.

> exponential backoff: 재시도 간격을 점진적으로 늘리는 방식입니다. 장애 시 client들이 동시에 재요청하는 retry storm을 줄입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Metadata와 보안

### Metadata

gRPC metadata는 호출과 함께 전달되는 key-value 데이터입니다. HTTP/2 header와 trailer를 사용하며 인증, tracing, request ID, 사용자 정의 제어 정보에 사용할 수 있습니다.

| 용도         | 예시                       | 주의사항                          |
|--------------|----------------------------|-----------------------------------|
| 인증         | bearer token·mTLS identity | 로그·오류 메시지에 원문 출력 금지 |
| 추적         | trace ID·span ID           | propagator 형식 통일              |
| 요청 식별    | request ID·tenant ID       | 신뢰 경계에서 재검증              |
| 응답 trailer | status detail·diagnostic   | 민감정보와 크기 제한              |

### TLS와 인증

- server authentication에는 TLS를 기본으로 적용합니다.
- 내부 service identity와 권한 검증은 TLS 인증서, token credentials, 또는 조직의 인증 체계로 분리합니다.
- channel credentials와 per-call credentials의 수명과 갱신 실패를 관측합니다.
- 인증 성공과 authorization 실패를 구분해 status와 audit event를 남깁니다.
- metadata는 암호화된 transport를 사용하더라도 애플리케이션·proxy·interceptor 로그에 노출될 수 있으므로 최소화합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Health checking과 연결 운영

### Health checking

gRPC는 `health/v1` 표준 service API를 제공합니다. 서버는 전체 server와 개별 service의 상태를 `SERVING`, `NOT_SERVING` 등으로 갱신하고, client나 load balancer가 이를 사용하도록 구성할 수 있습니다.

- readiness와 liveness를 같은 의미로 사용하지 않습니다.
- 의존 DB·queue·upstream이 준비되지 않으면 실제 요청 수용 상태를 `NOT_SERVING`으로 반영합니다.
- server shutdown 시 신규 호출 차단, 진행 중 호출 종료, health 상태 변경 순서를 정의합니다.

### Keepalive와 graceful shutdown

- keepalive는 HTTP/2 PING으로 연결 상태를 확인하는 기능이며 health checking을 대체하지 않습니다.
- keepalive interval을 proxy·load balancer 정책보다 무작정 짧게 설정하지 않습니다.
- 장기 streaming RPC는 shutdown signal을 받고 새 연결을 막은 뒤 진행 중 stream을 정리합니다.
- client는 연결 종료 후 backoff를 적용해 재연결하고, 이미 처리된 message의 중복을 방지합니다.

### 운영 상태 흐름

```text
NOT_SERVING
    │ readiness success
    v
SERVING ─────── shutdown ───────> NOT_SERVING
    │                                │
    └── dependency failure ──────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 관측성과 장애 대응

### 필수 관측 항목

| 범주       | 지표·로그                                   |
|------------|---------------------------------------------|
| latency    | method별 p50·p95·p99와 deadline 초과        |
| outcome    | status code·cancel·retry 횟수               |
| resource   | active RPC·stream·connection·queue depth    |
| payload    | message size·metadata size·compression 비용 |
| dependency | downstream latency·error·remaining deadline |
| health     | service별 SERVING·NOT_SERVING 전환          |

로그에는 method, service, request ID, trace ID, status, elapsed time을 구조화해 남기되 token·개인정보·payload 전체는 기록하지 않습니다.

### 장애 대응 순서

1. client status와 deadline 초과 여부를 확인합니다.
2. server의 active RPC, CPU, memory, file descriptor, queue 상태를 확인합니다.
3. 동일 method의 downstream latency와 retry 증가를 비교합니다.
4. health 상태와 load balancer의 backend 제외 여부를 확인합니다.
5. schema 또는 generated code 변경이 있었다면 client·server 버전 조합을 확인합니다.
6. 원인 제거 후 retry storm과 재연결 폭주가 가라앉는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 단계별 학습과 실무 프로젝트

| 단계  | 학습 주제                                   | 산출물                     |
|-------|---------------------------------------------|----------------------------|
| 1단계 | `.proto`, message, service, code generation | unary host 조회 API        |
| 2단계 | status, metadata, deadline, cancellation    | timeout이 있는 control API |
| 3단계 | server·client·bidirectional streaming       | agent watch channel        |
| 4단계 | TLS, health, retry, graceful shutdown       | 운영 가능한 내부 service   |
| 5단계 | load balancing, tracing, compatibility      | 다중 service platform API  |

### SE 실무 프로젝트

- 서버 inventory agent와 collector 사이의 unary·server streaming API 구축.
- 작업 실행 요청과 상태 event를 분리한 controller API 구축.
- health checking과 graceful shutdown을 포함한 maintenance daemon 작성.
- 장애 주입으로 deadline exceeded, connection reset, retry 중복을 검증.

[⬆ 목차로 돌아가기](#목차)

---

## 10. CI·배포 검증

```bash
protoc --version
# 프로젝트별 공식 build command로 generated code와 server/client 테스트 실행
```

CI에는 다음 검증을 포함합니다.

1. `.proto` lint와 generated code 재생성 결과를 확인합니다.
2. service contract 변경의 field number·reserved·package 영향을 확인합니다.
3. unit test에서 각 status code와 deadline 경계를 확인합니다.
4. integration test에서 TLS, metadata, health checking을 확인합니다.
5. streaming test에서 backpressure, cancellation, reconnect, graceful shutdown을 확인합니다.
6. retry test에서 멱등성과 최대 시도 횟수를 확인합니다.
7. 배포 전 client·server 버전 조합과 rollback 시 호환성을 확인합니다.

문서·schema·generated code·runtime 버전을 하나의 release artifact로 추적하면 서비스 간 계약 불일치를 조기에 발견할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [gRPC 공식 참조 노트](../../_reference/grpc_official_notes.md)
- [Protocol Buffers 공식 참조 노트](../../_reference/protobuf_official_notes.md)
- gRPC Documentation: [grpc.io/docs](https://grpc.io/docs/) — ★★★☆☆
- gRPC Introduction: [grpc.io/docs/what-is-grpc/introduction](https://grpc.io/docs/what-is-grpc/introduction/) — ★★★☆☆
- gRPC Core Concepts: [grpc.io/docs/what-is-grpc/core-concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) — ★★★☆☆
- gRPC Authentication: [grpc.io/docs/guides/auth](https://grpc.io/docs/guides/auth/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-11

**마지막 업데이트**: 2026-09-11

© 2026 siasia86. Licensed under CC BY 4.0.
