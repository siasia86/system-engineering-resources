---
name: protobuf-official-notes
description: Protocol Buffers 공식 문서 기반 버전·스키마·직렬화·호환성 참조 노트.
tags:
  - protobuf
  - protocol-buffers
  - serialization
  - schema
  - wire-format
last_checked: 2026-09-11
sources:
  - https://protobuf.dev/overview/
  - https://protobuf.dev/programming-guides/proto3/
  - https://protobuf.dev/programming-guides/encoding/
  - https://protobuf.dev/programming-guides/serialization-not-canonical/
  - https://protobuf.dev/editions/overview/
  - https://github.com/protocolbuffers/protobuf/releases/tag/v36.1
---

# Protocol Buffers 공식 참조 노트

## 1. 버전 현황

- 최신 공식 GitHub 릴리스: `v36.1`.
- Protocol Buffers 문서는 `proto2`, `proto3`, Protobuf Editions를 함께 설명합니다.
- Editions는 기존 `proto2`·`proto3` 표기를 대체하고 `edition = "2024"` 같은 edition 번호로 기본 동작을 지정하는 모델입니다.
- Editions는 기능(feature)의 기본 동작을 점진적으로 변경할 수 있도록 설계되며, 기존 바이너리와 메시지의 binary·text·JSON 직렬화 형식을 깨지 않는 것을 목표로 합니다.

## 2. 구성 요소와 사용 범위

Protocol Buffers는 다음 요소의 조합입니다.

| 구성 요소          | 역할                                        |
|--------------------|---------------------------------------------|
| `.proto` 정의 언어 | 메시지·필드·서비스·옵션의 스키마 표현       |
| `protoc` 컴파일러  | `.proto`를 언어별 소스 코드로 변환          |
| 생성 코드          | 메시지 접근자와 직렬화·역직렬화 API 제공    |
| 언어별 runtime     | 생성 코드가 사용하는 파싱·직렬화 라이브러리 |
| wire format        | 네트워크·파일에 기록되는 바이너리 표현      |
| serialized data    | 실제 전송·저장되는 메시지 바이트            |

Protocol Buffers는 언어·플랫폼 중립적인 구조화 데이터 직렬화 형식입니다. gRPC 서비스 정의와 함께 통신 프로토콜을 선언하거나 데이터 저장 형식으로 사용할 수 있습니다.

> wire format: `.proto`의 필드 번호와 wire type을 사용해 메시지를 바이트로 표현하는 규칙입니다. 수신자는 같은 스키마 또는 생성 코드로 필드 번호와 값을 해석합니다.

## 3. 스키마 정의와 호환성

### 필드 번호

- 필드 번호는 메시지 wire format에서 필드를 식별하므로 사용 후 변경하거나 재사용하지 않습니다.
- 새 필드는 기존 필드를 이해하지 못하는 구형 파서가 건너뛸 수 있도록 추가해야 합니다.
- 삭제한 필드의 번호는 `reserved`로 지정해 향후 재사용을 막습니다.
- 삭제한 필드 이름도 JSON·TextFormat 파싱 위험을 줄이기 위해 `reserved`로 지정하는 것이 권장됩니다.
- 구현 예약 범위인 `19000`~`19999`는 사용하지 않습니다.

### 변경 분류

| 변경 유형       | 공식 문서상 의미                                  |
|-----------------|---------------------------------------------------|
| wire-safe       | 기존 바이너리 해석을 깨지 않는 변경               |
| wire-compatible | 조건을 만족할 때 바이너리 호환이 가능한 변경      |
| wire-unsafe     | 기존 메시지 해석 또는 전송과 호환되지 않는 변경   |
| field addition  | 구형 코드가 알 수 없는 필드를 건너뛸 수 있는 확장 |
| field deletion  | 번호·이름 예약 없이 삭제하면 재사용 위험 발생     |

알 수 없는 필드(unknown fields)를 보존하는 동작은 새 필드를 모르는 구형 코드와 새 코드를 함께 운영할 때의 호환성에 사용됩니다. 스키마 변경 전에는 생성 코드뿐 아니라 저장된 메시지와 다중 버전 서비스의 파싱 동작도 확인합니다.

## 4. 직렬화와 wire format

- 메시지는 필드 번호, wire type, payload로 구성된 key-value 레코드의 연속으로 인코딩됩니다.
- wire type은 파서가 뒤따르는 payload의 길이와 해석 방식을 결정합니다.
- 작은 필드 번호는 wire format에서 더 적은 바이트를 사용할 수 있으므로 자주 설정되는 필드에는 `1`~`15` 범위를 우선 고려합니다.
- 기본 직렬화 결과는 canonical하지 않으며 필드 순서와 바이트 출력의 안정성을 일반적으로 보장하지 않습니다.
- deterministic serialization을 사용하더라도 모든 스키마·애플리케이션·runtime 버전에 걸친 canonical serialization을 의미하지 않습니다.
- 메시지는 자동 압축되지 않습니다. 필요한 경우 전송 계층 또는 별도 압축 형식을 사용합니다.

> canonical serialization: 같은 논리적 메시지에 대해 언제나 하나의 동일한 바이트 표현을 만드는 직렬화 방식입니다. Protocol Buffers 공식 문서는 일반적인 메시지 직렬화가 canonical하지 않다고 설명합니다.

## 5. Proto3와 Editions

| 구분     | 정의 방식              | 적용 관점                                   |
|----------|------------------------|---------------------------------------------|
| proto2   | `syntax = "proto2";`   | 기존 proto2 문법과 동작 유지                |
| proto3   | `syntax = "proto3";`   | proto3 문법·field presence 규칙 적용        |
| Editions | `edition = "2024";` 등 | 기능별 기본 동작을 edition과 feature로 관리 |

- 파일의 첫 번째 비공백·비주석 선언은 syntax 또는 edition 선언이어야 합니다.
- proto3의 `optional` 필드는 명시적 presence를 사용합니다.
- Editions는 파일·메시지·필드 등 범위에서 feature 옵션을 재정의할 수 있습니다.
- Editions 도입·마이그레이션 시 `protoc`, 생성기, runtime의 지원 범위를 함께 확인합니다.

## 6. 운영 권고

- `.proto` 파일을 API 계약의 원본으로 버전 관리하고 생성 코드는 재현 가능한 빌드 단계에서 생성합니다.
- 필드 번호·이름을 삭제할 때 `reserved` 정책을 코드 리뷰 항목으로 둡니다.
- 저장·전송 메시지의 크기는 제한합니다. 공식 개요는 수 메가바이트를 넘는 데이터에서 메모리 복사와 사용량 급증을 주의하도록 설명합니다.
- serialized bytes를 해시 키·동등성 비교·무결성 fingerprint로 사용할 때는 canonical하지 않다는 점과 unknown fields를 고려합니다.
- 스키마 변경은 이전·이후 생성 코드, 다중 언어 runtime, 장기 보관 데이터로 검증합니다.

## 7. 공식 확인 항목

| 확인 항목             | 확인 기준                                   |
|-----------------------|---------------------------------------------|
| compiler/runtime 버전 | `protoc`와 언어별 runtime의 지원 범위       |
| 문법 체계             | proto2·proto3·Edition 선언과 feature 기본값 |
| 스키마 변경           | field number·name 예약 및 wire 호환성       |
| 직렬화 비교           | canonical 여부와 deterministic 옵션의 범위  |
| 메시지 크기           | 전체 메시지 메모리 로드와 복사 비용         |
| 언어 간 생성 코드     | 공식 compiler·plugin·runtime 조합           |
