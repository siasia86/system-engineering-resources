# CPU 아키텍처: CISC vs RISC

CPU 명령어 집합 아키텍처(ISA)의 두 가지 설계 철학을 비교한다.

## 목차

| 단계   | 섹션                                                                                                |
|--------|-----------------------------------------------------------------------------------------------------|
| 기본   | [1. CISC](#1-cisc) / [2. RISC](#2-risc)                                                            |
| 비교   | [3. CISC vs RISC 비교](#3-cisc-vs-risc-비교) / [4. 파이프라인 차이](#4-파이프라인-차이)              |
| 현황   | [5. 대표 프로세서](#5-대표-프로세서) / [6. 현대 CPU의 융합](#6-현대-cpu의-융합)                      |
| 실무   | [7. 서버/클라우드 환경에서의 선택](#7-서버클라우드-환경에서의-선택) / [8. 실무 Tip](#8-실무-tip)      |

---

## 1. CISC

### 개요

CISC(Complex Instruction Set Computer)는 하나의 명령어로 복잡한 연산을 수행하는 설계 방식이다. 명령어 수가 많고, 명령어마다 길이와 실행 사이클이 다르다.

### 특징

| 항목              | 설명                                              |
|-------------------|---------------------------------------------------|
| 명령어 수         | 많음 (수백~수천 개)                                |
| 명령어 길이       | 가변 길이 (1~15 byte, x86 기준)                   |
| 실행 사이클       | 명령어마다 다름 (1~수십 사이클)                    |
| 메모리 접근       | 명령어 내에서 직접 메모리 연산 가능                |
| 레지스터 수       | 상대적으로 적음                                    |
| 디코딩            | 복잡 (마이크로코드 사용)                           |

### 동작 방식

```
CISC: one instruction does multiple operations

  ADD [mem_addr], reg
    |
    +-- 1. Fetch address from memory
    +-- 2. Load value from memory
    +-- 3. Add register value
    +-- 4. Store result back to memory
    +-- (1 instruction, multiple cycles)
```

- 하나의 명령어가 메모리 읽기 + 연산 + 메모리 쓰기를 모두 수행
- 컴파일러 부담이 적고, 코드 밀도가 높음
- 하드웨어 복잡도가 높음

### 대표 명령어 예시 — x86

```
; 메모리에서 직접 연산
ADD [EBX+ECX*4+8], EAX    ; mem[EBX+ECX*4+8] += EAX
REP MOVSB                  ; 문자열 복사 (반복 명령어)
ENTER 16, 0                ; 스택 프레임 생성 (복합 명령어)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. RISC

### 개요

RISC(Reduced Instruction Set Computer)는 단순하고 균일한 명령어로 빠른 실행을 추구하는 설계 방식이다. 명령어 수가 적고, 대부분 1사이클에 실행된다.

### 특징

| 항목              | 설명                                              |
|-------------------|---------------------------------------------------|
| 명령어 수         | 적음 (수십~수백 개)                                |
| 명령어 길이       | 고정 길이 (4 byte, ARM/RISC-V 기준)               |
| 실행 사이클       | 대부분 1사이클                                     |
| 메모리 접근       | Load/Store 명령어만 메모리 접근                    |
| 레지스터 수       | 많음 (32개 이상)                                   |
| 디코딩            | 단순 (하드와이어드)                                |

### 동작 방식

```
RISC: one instruction does one operation (Load/Store architecture)

  LDR  R1, [R2]       ; 1. Load value from memory to register
  ADD  R1, R1, R3     ; 2. Add registers
  STR  R1, [R2]       ; 3. Store result back to memory
  (3 instructions, each 1 cycle)
```

- 메모리 접근과 연산을 분리 (Load/Store 아키텍처)
- 파이프라인 효율이 높음
- 컴파일러가 최적화를 담당

### 대표 명령어 예시 — ARM

```
LDR  R0, [R1]         ; 메모리에서 레지스터로 로드
ADD  R0, R0, R2       ; 레지스터 간 덧셈
STR  R0, [R1]         ; 레지스터에서 메모리로 저장
CMP  R0, #0           ; 비교
BEQ  label            ; 조건 분기
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. CISC vs RISC 비교

| 항목              | CISC                           | RISC                           |
|-------------------|:------------------------------:|:------------------------------:|
| 명령어 수         | 많음                           | 적음                           |
| 명령어 길이       | 가변                           | 고정                           |
| 실행 사이클       | 명령어마다 다름                | 대부분 1사이클                 |
| 메모리 접근       | 명령어 내 직접 가능            | Load/Store만                   |
| 레지스터          | 적음                           | 많음                           |
| 파이프라인        | 복잡 (가변 길이로 인해)        | 단순 (고정 길이로 효율적)      |
| 코드 크기         | 작음 (명령어 밀도 높음)        | 큼 (명령어 수 많음)            |
| 전력 소모         | 높음                           | 낮음                           |
| 디코딩            | 마이크로코드                   | 하드와이어드                   |
| 컴파일러 부담     | 적음                           | 많음 (최적화 필요)             |
| 대표 ISA          | x86, x86-64                   | ARM, RISC-V, MIPS, SPARC      |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 파이프라인 차이

### RISC 파이프라인 (이상적)

```
Clock:    1     2     3     4     5     6     7
Inst 1:  [IF]  [ID]  [EX]  [MEM] [WB]
Inst 2:        [IF]  [ID]  [EX]  [MEM] [WB]
Inst 3:              [IF]  [ID]  [EX]  [MEM] [WB]

IF  = Instruction Fetch
ID  = Instruction Decode
EX  = Execute
MEM = Memory Access
WB  = Write Back
```

- 고정 길이 명령어 → 매 사이클 새 명령어 투입 가능
- 5단계 파이프라인이 가장 기본적인 형태

### CISC 파이프라인 (문제점)

```
Clock:    1     2     3     4     5     6     7     8
Inst 1:  [IF]  [IF]  [ID]  [ID]  [EX]  [MEM] [WB]
Inst 2:                    [IF]  [ID]  [EX]  [MEM] [WB]

--> variable length instructions cause pipeline stalls
--> decode stage takes multiple cycles
```

- 가변 길이 명령어 → Fetch/Decode 단계에서 지연 발생
- 현대 x86은 내부적으로 RISC 마이크로옵(micro-op)으로 변환하여 해결

### 파이프라인 해저드

| 해저드 유형       | 설명                                    | CISC 영향 | RISC 영향 |
|-------------------|-----------------------------------------|:---------:|:---------:|
| 구조적 해저드     | 하드웨어 자원 충돌                      | 🔴        | 🟡        |
| 데이터 해저드     | 이전 명령어 결과에 의존                 | 🟡        | 🟡        |
| 제어 해저드       | 분기 명령어로 인한 파이프라인 플러시    | 🟡        | 🟡        |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대표 프로세서

### CISC 계열

| 프로세서              | 제조사    | 용도                          |
|-----------------------|-----------|-------------------------------|
| x86 (i386~)           | Intel     | 데스크톱, 서버                |
| x86-64 (AMD64)        | AMD/Intel | 데스크톱, 서버, 클라우드      |
| Z/Architecture        | IBM       | 메인프레임                    |

### RISC 계열

| 프로세서              | 제조사        | 용도                          |
|-----------------------|---------------|-------------------------------|
| ARM Cortex-A          | ARM           | 모바일, 임베디드              |
| ARM Neoverse          | ARM           | 서버, 클라우드                |
| Apple M 시리즈        | Apple         | 데스크톱, 노트북              |
| AWS Graviton          | AWS (ARM)     | 클라우드 서버                 |
| RISC-V                | 오픈소스      | IoT, 임베디드, 연구           |
| MIPS                  | MIPS Tech     | 네트워크 장비, 임베디드       |
| SPARC                 | Oracle/Sun    | 레거시 서버 (단종 추세)       |
| POWER                 | IBM           | 서버, HPC                     |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 현대 CPU의 융합

### CISC 내부의 RISC화

현대 x86 CPU는 외부적으로 CISC 명령어를 받지만, 내부적으로 RISC 마이크로옵(micro-op)으로 변환하여 실행한다.

```
x86 instruction (CISC)
        |
        v
  ┌─────────────┐
  │  Decoder     │  --> CISC to micro-op translation
  └─────────────┘
        |
        v
  ┌─────────────┐
  │  micro-ops   │  --> RISC-like execution
  │  (internal)  │
  └─────────────┘
        |
        v
  ┌─────────────┐
  │  Out-of-Order│  --> superscalar pipeline
  │  Execution   │
  └─────────────┘
```

### RISC의 복잡화

ARM도 버전이 올라가면서 명령어가 추가되고, 마이크로아키텍처가 복잡해지고 있다.

| 세대              | 특징                                          |
|-------------------|-----------------------------------------------|
| ARMv7 (32bit)     | 단순 RISC, Thumb 명령어 (16bit 압축)          |
| ARMv8 (64bit)     | AArch64 추가, SIMD/암호화 명령어 확장         |
| ARMv9             | SVE2 (벡터 연산), CCA (보안), AI 가속         |

### 결론

현대 CPU에서 CISC/RISC의 경계는 흐려졌다. 핵심 차이는 ISA(명령어 집합) 수준의 설계 철학이며, 실제 실행 엔진은 양쪽 모두 유사한 기법을 사용한다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 서버/클라우드 환경에서의 선택

### AWS 인스턴스 비교

| 항목              | x86 (Intel/AMD)            | ARM (Graviton)               |
|-------------------|----------------------------|------------------------------|
| 인스턴스 타입     | m5, m6i, m6a, c5, r5 등   | m6g, m7g, c6g, r6g 등       |
| 가격              | 기준                       | x86 대비 약 20% 저렴        |
| 성능/와트         | 기준                       | 더 높음 (전력 효율 우수)     |
| 호환성            | 대부분의 소프트웨어 지원   | ARM 빌드 필요 (대부분 지원)  |
| 적합 워크로드     | 레거시, Windows, 특수 SW   | 웹서버, 컨테이너, 오픈소스   |

### 선택 기준

| 조건                                  | 권장              |
|---------------------------------------|:-----------------:|
| 기존 x86 바이너리 호환 필요           | x86               |
| Windows Server 필수                   | x86               |
| 비용 최적화 우선                      | ARM (Graviton)    |
| 컨테이너/마이크로서비스               | ARM (Graviton)    |
| 높은 단일 스레드 성능 필요            | x86 (고클럭)      |
| 전력 효율 / 지속 가능성               | ARM               |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 Tip

### Tip 1 — ARM 호환성 확인

ARM 서버로 전환 시 소프트웨어 호환성을 먼저 확인한다.

```bash
# Docker 이미지 멀티 아키텍처 확인
docker manifest inspect nginx:latest | grep architecture
```

### Tip 2 — 크로스 컴파일 활용

x86 환경에서 ARM 바이너리를 빌드할 수 있다.

```bash
# Go 크로스 컴파일
GOOS=linux GOARCH=arm64 go build -o app-arm64

# Docker 멀티 플랫폼 빌드
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .
```

### Tip 3 — CPU 아키텍처 확인 명령어

| OS        | 명령어                          | 출력 예시              |
|-----------|---------------------------------|------------------------|
| Linux     | `uname -m`                      | `x86_64` / `aarch64`  |
| Linux     | `lscpu`                         | Architecture 상세 정보 |
| Windows   | `echo %PROCESSOR_ARCHITECTURE%` | `AMD64` / `ARM64`     |
| macOS     | `uname -m`                      | `arm64` (M 시리즈)    |

### Tip 4 — RISC-V 동향 주시

RISC-V는 오픈소스 ISA로, 라이선스 비용이 없어 IoT/임베디드에서 채택이 증가하고 있다. 서버 시장 진입은 아직 초기 단계이나 장기적으로 주목할 아키텍처.

### Tip 5 — 성능 비교 시 주의사항

- 단순 클럭 속도 비교는 무의미 (IPC가 다름)
- 동일 워크로드 벤치마크로 비교해야 함
- 가격 대비 성능(price-performance)이 실무에서 가장 중요한 지표

[⬆ 목차로 돌아가기](#목차)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---
**작성일**: 2026-04-24

**마지막 업데이트**: 2026-04-24

© 2026 siasia86. Licensed under CC BY 4.0.
