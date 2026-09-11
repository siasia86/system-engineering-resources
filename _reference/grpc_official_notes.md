---
name: grpc-official-notes
description: gRPC 공식 문서 기반 버전·RPC 호출 모델·신뢰성·보안·운영 참조 노트.
tags:
  - grpc
  - rpc
  - http2
  - protobuf
  - streaming
last_checked: 2026-09-11
sources:
  - https://grpc.io/docs/what-is-grpc/introduction/
  - https://grpc.io/docs/what-is-grpc/core-concepts/
  - https://grpc.io/docs/guides/deadlines/
  - https://grpc.io/docs/guides/status-codes/
  - https://grpc.io/docs/guides/metadata/
  - https://grpc.io/docs/guides/auth/
  - https://grpc.io/docs/guides/health-checking/
  - https://grpc.io/docs/guides/retry/
  - https://grpc.io/docs/guides/keepalive/
  - https://github.com/grpc/grpc/releases/tag/v1.84.0
---

# gRPC 공식 참조 노트

## 1. 버전 현황

- 최신 공식 GitHub 릴리스: `v1.84.0`.
- gRPC는 서비스 인터페이스와 원격 메서드를 정의하고, 클라이언트가 원격 서버의 메서드를 로컬 호출처럼 사용하도록 하는 RPC 프레임워크입니다.
- 기본 직렬화 형식으로 Protocol Buffers를 사용하지만 다른 데이터 형식도 사용할 수 있습니다.
- 구현 언어별 API·생성 코드·지원 범위는 언어별 공식 문서에서 별도로 확인합니다.

## 2. 기본 모델과 전송

- 서비스는 호출 가능한 메서드와 각 메서드의 요청·응답 메시지를 `.proto` 파일에 정의합니다.
- 서버는 서비스 인터페이스를 구현하고 gRPC server를 실행합니다.
- 클라이언트는 생성된 stub을 통해 서버 메서드를 호출합니다.
- gRPC는 HTTP/2를 기반으로 하며, Protocol Buffers 메시지와 함께 다중화·스트리밍·메타데이터·상태 전달을 제공합니다.

> RPC(Remote Procedure Call): 다른 프로세스나 시스템의 함수를 로컬 함수처럼 호출하는 통신 모델입니다. 네트워크 지연·부분 실패·직렬화·취소를 고려해야 하므로 일반 로컬 함수와 동일하게 취급하면 안 됩니다.

## 3. RPC 호출 유형

| 유형                    | 요청          | 응답          | 주요 용도                     |
|-------------------------|---------------|---------------|-------------------------------|
| Unary                   | 단일 메시지   | 단일 메시지   | 일반적인 요청·응답            |
| Server streaming        | 단일 메시지   | 메시지 스트림 | 서버의 연속 결과 전달         |
| Client streaming        | 메시지 스트림 | 단일 메시지   | 클라이언트 데이터 묶음 업로드 |
| Bidirectional streaming | 메시지 스트림 | 메시지 스트림 | 양방향 독립 스트림            |

- gRPC는 하나의 RPC 호출 안에서 메시지 순서를 보장합니다.
- 양방향 streaming에서는 클라이언트와 서버의 읽기·쓰기 흐름이 독립적이며 애플리케이션이 처리 순서를 결정합니다.
- streaming을 선택할 때는 연결 수명, flow control, 취소, 부분 전송 실패, graceful shutdown을 함께 설계합니다.

## 4. 호출 수명과 상태

호출 흐름은 일반적으로 다음 순서입니다.

1. 클라이언트가 stub 메서드를 호출하고 metadata·메서드명·deadline을 전달합니다.
2. 서버가 초기 metadata를 보내거나 요청 메시지를 기다립니다.
3. 서버가 요청을 처리하고 응답 메시지, status code, 선택적 trailing metadata를 반환합니다.
4. 클라이언트가 최종 상태를 확인하고 호출을 완료합니다.

- 모든 RPC는 상태를 반환합니다.
- 애플리케이션은 공식적으로 정의된 gRPC status code만 사용합니다.
- `INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `FAILED_PRECONDITION`, `ABORTED`, `OUT_OF_RANGE`, `DATA_LOSS`는 library가 생성하지 않고 사용자 코드가 반환하는 상태로 분류됩니다.
- `DEADLINE_EXCEEDED`, `UNAVAILABLE`, `CANCELLED` 등은 호출 실패 원인과 재시도 정책을 함께 검토해야 합니다.

## 5. Deadline·취소·재시도

### Deadline

- gRPC client는 기본 deadline을 설정하지 않으므로 명시적인 현실적 deadline을 지정합니다.
- deadline을 넘기면 클라이언트는 `DEADLINE_EXCEEDED`로 실패할 수 있습니다.
- 서버는 deadline이 지난 호출을 취소할 수 있으며, 애플리케이션이 시작한 장기 작업도 취소 상태를 확인하고 중단해야 합니다.
- 서버가 다른 gRPC 서버를 호출하는 경우 남은 시간을 downstream 호출에 전파해 전체 요청 예산을 지킵니다.

### Retry

- retry는 실패한 호출을 새 호출로 대체하고 호출 이력을 재생하는 동작입니다.
- 공식 문서는 재시도 가능한 작업, exponential backoff, 최대 시도 횟수, retry metrics를 명시하도록 권고합니다.
- 첫 response header가 수신되면 RPC가 committed되어 추가 retry를 수행하지 않습니다.
- retry 정책을 적용할 때는 비멱등 작업의 중복 실행, 서버 부하, retry storm을 검토합니다.

> exponential backoff: 재시도 사이의 대기 시간을 점진적으로 늘리는 방식입니다. 동시 장애 상황에서 재시도 요청이 한꺼번에 몰리는 것을 줄이는 데 사용합니다.

## 6. Metadata와 보안

- gRPC metadata는 호출과 함께 전달되는 key-value 데이터이며 HTTP/2 header와 trailer를 사용합니다.
- metadata는 인증 정보, tracing 정보, 사용자 정의 header 등에 사용할 수 있습니다.
- gRPC 공식 인증 문서는 server authentication에 SSL/TLS 사용을 권장하고, token-based authentication과 channel·call credentials를 설명합니다.
- 토큰·개인정보·비밀값을 일반 로그에 기록하지 않고, metadata 크기·수명·전달 범위를 제한합니다.
- 인증 실패와 권한 부족을 적절한 status code로 구분하고 인증서·토큰 만료 및 rotation을 운영 절차에 포함합니다.

## 7. Health checking과 연결 운영

- gRPC는 `health/v1` 표준 서비스 API를 제공합니다.
- 서버는 서비스별 `SERVING`, `NOT_SERVING` 상태를 갱신해야 합니다.
- client health checking은 비정상 backend로 요청을 보내지 않도록 사용할 수 있습니다.
- keepalive는 HTTP/2 PING으로 연결 상태를 확인하는 기능이며 health checking과 목적이 다릅니다.
- keepalive interval을 과도하게 짧게 설정하면 연결과 서버에 부하를 주거나 `too_many_pings`로 연결이 종료될 수 있으므로 서비스 소유자와 합의합니다.

## 8. 공식 운영 확인 항목

| 확인 항목 | 확인 기준                                           |
|-----------|-----------------------------------------------------|
| API 계약  | `.proto` 서비스·메시지·생성 코드 일치               |
| 호출 유형 | unary·streaming 선택과 flow control                 |
| 시간 예산 | 모든 외부 호출의 deadline과 downstream 전파         |
| 장애 처리 | status code·취소·retryable 조건·backoff             |
| 보안      | TLS·token credentials·metadata 노출                 |
| 가용성    | health checking·graceful shutdown·connection policy |
| 연결 유지 | keepalive interval과 proxy/load balancer 정책       |
| 관측성    | latency·status·retry·stream·metadata 관련 지표      |
