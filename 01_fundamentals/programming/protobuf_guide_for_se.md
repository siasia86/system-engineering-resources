# SE를 위한 Protocol Buffers 가이드
<!-- reference: _reference/protobuf_official_notes.md -->

시스템 엔지니어 관점에서 Protocol Buffers를 학습하고 운영하는 가이드입니다. `.proto` 스키마 설계, 다중 버전 호환성, 생성 코드, 직렬화 비용과 CI 검증에 초점을 맞춥니다.

## 목차

| 섹션                                                                                                                                   |
|----------------------------------------------------------------------------------------------------------------------------------------|
| [1. Protocol Buffers 개요](#1-protocol-buffers-개요) / [2. SE 활용 판단](#2-se-활용-판단) / [3. 스키마 설계](#3-스키마-설계)           |
| [4. 호환성과 직렬화](#4-호환성과-직렬화) / [5. 도구와 프로젝트](#5-도구와-프로젝트) / [6. 데이터 수명주기](#6-데이터-수명주기)         |
| [7. 운영·보안·관측성](#7-운영보안관측성) / [8. 단계별 학습과 실무 프로젝트](#8-단계별-학습과-실무-프로젝트) / [9. CI 검증](#9-ci-검증) |

---

## 1. Protocol Buffers 개요

Protocol Buffers는 언어와 플랫폼에 중립적인 구조화 데이터 직렬화 형식입니다. `.proto` 파일에 메시지와 필드를 정의하면 `protoc`가 언어별 생성 코드를 만들고, runtime이 메시지의 파싱과 직렬화를 처리합니다.

> 직렬화(Serialization): 메모리의 구조화된 값을 파일이나 네트워크로 전달할 수 있는 바이트·텍스트 표현으로 변환하는 과정입니다. 역직렬화는 반대 방향의 변환입니다.

### 구성 요소

| 구성 요소   | 역할                                           |
|-------------|------------------------------------------------|
| `.proto`    | 메시지·필드·서비스·옵션의 계약 정의            |
| `protoc`    | `.proto`를 생성 코드로 변환하는 compiler       |
| 생성 코드   | 언어별 메시지 접근자와 파싱·직렬화 API 제공    |
| runtime     | 생성 코드가 사용하는 언어별 라이브러리         |
| wire format | 필드 번호와 wire type을 사용하는 바이너리 표현 |

### JSON과의 역할 차이

- Protocol Buffers는 명시적 스키마와 생성 코드를 사용합니다.
- wire format은 필드 이름 대신 field number를 사용하므로 메시지 크기를 줄일 수 있습니다.
- JSON처럼 사람이 직접 읽는 교환 형식이 아니므로 운영 로그에는 별도 진단 표현을 사용합니다.
- 메시지를 장기 저장할 때는 schema version, migration, unknown fields 보존 정책을 함께 관리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. SE 활용 판단

### 적합한 영역

| 영역             | 활용 예시                             | 판단 포인트                 |
|------------------|---------------------------------------|-----------------------------|
| 내부 서비스 계약 | 자산·인벤토리·작업 상태 메시지        | 다중 언어 client 필요 여부  |
| 에이전트 통신    | node agent와 중앙 collector 간 메시지 | 연결 장애·재전송·버전 공존  |
| 이벤트 저장      | 변경 이벤트와 audit payload           | 장기 보관 schema migration  |
| 고정 형식 데이터 | 설정 배포·정책 평가 입력              | field number 관리와 검증    |
| gRPC 서비스      | service와 RPC request·response        | 서비스 lifecycle과 deadline |

### 도입을 늦출 상황

- 외부 사용자가 직접 읽고 수정해야 하는 공개 payload가 주된 경우.
- 스키마 관리 주체와 compatibility 검증 절차가 없는 경우.
- 수 메가바이트를 넘는 대형 메시지를 한 번에 메모리에 올리는 구조인 경우.
- 단순한 설정 파일처럼 사람이 직접 편집하는 것이 운영상 중요한 경우.

Protocol Buffers는 형식 자체가 시스템의 호환성을 자동으로 보장하지 않습니다. field number를 잘못 재사용하거나 생성 코드와 runtime 버전을 혼합하면 계약 변경이 장애로 이어질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 스키마 설계

### 최소 메시지 정의

```protobuf
syntax = "proto3";

package inventory.v1;

message Host {
  string host_id = 1;
  optional string hostname = 2;
  repeated string addresses = 3;

  reserved 4;
  reserved "legacy_name";
}
```

- 첫 선언은 `syntax` 또는 지원하는 Editions 선언으로 고정합니다.
- 필드 번호는 메시지가 외부로 사용된 뒤 변경하거나 재사용하지 않습니다.
- 삭제한 필드의 번호와 이름은 `reserved`로 남겨 재사용을 막습니다.
- 자주 설정되는 필드는 작은 field number를 사용해 wire format 비용을 줄일 수 있습니다.
- `repeated`, `optional`, `map`, `oneof`는 데이터 존재 여부와 호환성 요구사항을 먼저 정한 뒤 선택합니다.

### 이름과 package

| 항목    | 권장 기준                                     |
|---------|-----------------------------------------------|
| package | 조직·도메인·버전을 포함해 충돌 방지           |
| message | 단일 책임의 명사형 이름 사용                  |
| field   | 의미가 바뀌지 않는 안정적인 이름 사용         |
| enum    | 알 수 없는 값과 기본값 처리 고려              |
| version | 호환되지 않는 계약 변경은 명시적 version 분리 |

### 서비스 계약과 분리

메시지 정의와 transport service 정의를 한 파일에 둘 수도 있지만, 재사용되는 공통 message와 서비스별 request·response를 구분하면 변경 범위를 추적하기 쉽습니다. 공개 계약에는 내부 DB column명이나 운영용 비밀값을 그대로 노출하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 호환성과 직렬화

### 호환성 규칙

| 변경            | 운영 판단                                      |
|-----------------|------------------------------------------------|
| 새 field 추가   | 구형 parser가 unknown field를 건너뛰는지 확인  |
| field 삭제      | 번호와 이름을 `reserved`로 유지                |
| field 번호 변경 | 삭제 후 신규 field 생성과 같으므로 금지        |
| field type 변경 | wire-compatible 조건과 실제 parser를 별도 검증 |
| enum 값 추가    | 구형 client의 unknown enum 처리 확인           |
| package 변경    | 생성 코드 namespace와 wire 계약 영향 검토      |

Protocol Buffers의 호환성은 schema 규칙뿐 아니라 저장된 메시지, 배포 중인 구버전 client, 언어별 runtime의 동작까지 포함합니다. 변경 전후 메시지를 실제 fixture로 파싱하는 검증을 둡니다.

### 직렬화 특성

- wire format은 field number와 wire type으로 값을 식별합니다.
- 알 수 없는 필드를 건너뛸 수 있어 새 field 추가에 유리합니다.
- 기본 serialized bytes는 canonical하지 않으므로 바이트 배열을 곧바로 논리적 동등성이나 장기 fingerprint로 사용하지 않습니다.
- deterministic serialization도 모든 schema·애플리케이션·runtime 버전에서 동일한 canonical 결과를 보장하지 않습니다.
- 메시지는 자동 압축되지 않으므로 압축이 필요하면 transport 또는 별도 저장 계층에서 명시합니다.

> canonical serialization: 동일한 논리 메시지를 항상 하나의 동일한 바이트 표현으로 만드는 직렬화 방식입니다. Protocol Buffers의 일반 직렬화는 이 보장을 제공하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 도구와 프로젝트

### 도구 흐름

```text
.proto schema
    │
    v
protoc + language plugin
    │
    v
Generated source + runtime
    │
    v
Application build and tests
    │
    v
Compatibility and release validation
```

| 도구·산출물                | SE 운영 관점                                      |
|----------------------------|---------------------------------------------------|
| `protoc`                   | CI에서 버전을 고정하고 로컬·빌드 서버 차이를 제거 |
| language plugin            | 생성기 버전을 runtime과 호환되게 관리             |
| generated code             | 수동 수정하지 않고 schema에서 재생성              |
| runtime                    | 애플리케이션 의존성과 보안 업데이트 추적          |
| descriptor·reflection 자료 | 디버깅·검사에 사용하되 운영 노출 범위 제한        |

### 저장소 구조 예시

```text
proto/
├── inventory/v1/host.proto
├── inventory/v1/task.proto
└── common/v1/resource.proto

generated/
├── go/
├── java/
└── python/
```

스키마와 생성 코드의 변경을 한 commit에서 추적하거나, 생성 단계가 재현되도록 build metadata를 남깁니다. 생성 코드의 diff가 예상보다 크면 compiler·plugin·runtime 버전 변경을 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 데이터 수명주기

### 저장·전송 경계

| 경계                | 확인할 항목                                                 |
|---------------------|-------------------------------------------------------------|
| client → server     | schema version, size limit, deadline 또는 transport timeout |
| server → queue      | retry 시 중복 event와 ordering 정책                         |
| queue → consumer    | unknown fields, consumer lag, poison message 처리           |
| storage → migration | 장기 보관 메시지의 parser와 schema archive                  |
| 운영자 → diagnostic | 사람이 읽을 표현과 민감정보 마스킹                          |

### 장애 처리

- 파싱 실패를 정상적인 빈 메시지로 처리하지 말고 원인과 payload 식별자를 기록합니다.
- 최대 메시지 크기와 nested depth를 제한해 메모리 고갈을 줄입니다.
- 재시도 시 동일 메시지가 여러 번 처리될 수 있으므로 event ID와 idempotency 정책을 둡니다.
- schema 변경을 먼저 배포할지 consumer를 먼저 배포할지의 순서를 계약별로 정합니다.
- 장기 저장 데이터는 현재 parser가 읽을 수 있는지 정기적으로 샘플 검증합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 운영·보안·관측성

### 보안 기준

- 메시지 payload에 password, token, private key를 포함하지 않습니다.
- 진단 로그에는 원본 serialized bytes를 무제한으로 남기지 않고 필드별 마스킹을 적용합니다.
- 신뢰할 수 없는 입력은 parser에서 크기와 구조를 검증한 뒤 처리합니다.
- schema 자체에 접근 제어가 필요한 경우 저장소 권한과 생성 artifact 배포 권한을 분리합니다.
- Protocol Buffers는 암호화나 인증을 제공하지 않으므로 transport 보안과 별도 설계합니다.

### 관측 지표

| 지표                      | 목적                          |
|---------------------------|-------------------------------|
| parse failure count       | 계약 불일치·손상 payload 탐지 |
| message size distribution | 메모리·네트워크 비용 추적     |
| schema version usage      | 구버전 client 잔존 확인       |
| unknown field count       | 점진 배포와 호환성 상태 확인  |
| serialization latency     | CPU 비용과 병목 확인          |
| rejected message count    | 크기·검증 정책 초과 확인      |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 단계별 학습과 실무 프로젝트

| 단계  | 학습 주제                            | 산출물                       |
|-------|--------------------------------------|------------------------------|
| 1단계 | message·field·enum·repeated·optional | 간단한 host inventory schema |
| 2단계 | wire format·unknown fields·reserved  | 호환성 변경 fixture          |
| 3단계 | `protoc`·plugin·generated code       | 두 언어 client/server 모델   |
| 4단계 | schema registry·version·migration    | 다중 버전 배포 계획          |
| 5단계 | 크기 제한·관측·CI compatibility      | 운영 가능한 계약 pipeline    |

### SE 실무 프로젝트

- 서버 inventory를 수집하는 agent와 중앙 collector의 message 계약 작성.
- 작업 실행 상태를 `queued`, `running`, `succeeded`, `failed`로 표현하는 event schema 작성.
- 기존 schema에 field를 추가하고 구버전·신버전 parser를 함께 검증.
- fixture 메시지의 parse·round-trip·size limit을 CI에서 검사.

[⬆ 목차로 돌아가기](#목차)

---

## 9. CI 검증

```bash
protoc --version
protoc --descriptor_set_out=/tmp/inventory.pb proto/inventory/v1/host.proto
```

CI에는 다음 검증을 포함합니다.

1. `protoc`와 plugin 버전 확인.
2. 생성 코드 재생성과 working tree 변경 여부 확인.
3. 이전 schema로 생성한 fixture를 현재 parser가 읽는지 확인.
4. 현재 schema로 생성한 fixture를 지원 대상 구버전 parser가 읽는지 확인.
5. 삭제 field의 number·name이 `reserved`인지 확인.
6. 메시지 크기·중첩 구조·잘못된 입력의 실패 동작 확인.
7. 생성 코드와 runtime의 dependency lock 상태 확인.

문서화·코드 생성·compatibility 검증을 하나의 release gate로 묶으면 schema 변경이 서비스 배포 뒤에 발견되는 위험을 줄일 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [Protocol Buffers 공식 참조 노트](../../_reference/protobuf_official_notes.md)
- Protocol Buffers Documentation: [protobuf.dev](https://protobuf.dev/) — ★★★☆☆
- Protocol Buffers Overview: [protobuf.dev/overview](https://protobuf.dev/overview/) — ★★★☆☆
- Protocol Buffers Language Guide: [protobuf.dev/programming-guides/proto3](https://protobuf.dev/programming-guides/proto3/) — ★★★☆☆
- Protocol Buffers Editions: [protobuf.dev/editions](https://protobuf.dev/editions/) — ★★★☆☆

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
