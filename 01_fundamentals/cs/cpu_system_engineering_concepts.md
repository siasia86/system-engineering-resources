# CPU 시스템 운영 개념
<!-- reference: _reference/cpu_system_engineering_official_notes.md -->

CPU의 내부 회로 설계보다 시스템 엔지니어(SE)가 운영·성능·가상화·호환성 판단에 필요한 개념을 정리합니다. CISC/RISC와 ISA 설계 철학은 [CPU 아키텍처: CISC vs RISC](cpu_cisc_risc_concepts.md)에서 별도로 다룹니다.

## 목차

| 섹션                                                                                                                  |
|-----------------------------------------------------------------------------------------------------------------------|
| [1. SE에게 필요한 CPU 이해 범위](#1-se에게-필요한-cpu-이해-범위) / [2. CPU 구성과 성능 표현](#2-cpu-구성과-성능-표현) |
| [3. 운영체제 스케줄링과 관측](#3-운영체제-스케줄링과-관측) / [4. NUMA와 메모리 배치](#4-numa와-메모리-배치)           |
| [5. 가상화 환경의 CPU](#5-가상화-환경의-cpu) / [6. 명령어 세트와 호환성](#6-명령어-세트와-호환성)                     |
| [7. CPU 성능 장애 진단](#7-cpu-성능-장애-진단) / [8. 용량 계획과 하드웨어 선정](#8-용량-계획과-하드웨어-선정)         |
| [9. 보안과 유지보수](#9-보안과-유지보수) / [10. 운영 체크리스트](#10-운영-체크리스트)                                 |

---

## 1. SE에게 필요한 CPU 이해 범위

SE는 CPU 내부의 트랜지스터나 마이크로아키텍처 전체를 구현할 필요는 없습니다. 대신 장애 원인을 CPU·메모리·I/O·가상화 경합 중 어디로 분류할 수 있고, CPU 증설이 실제 해결책인지 판단할 수 있어야 합니다.

| 수준   | 이해할 내용                                  | 실무 판단                          |
|--------|----------------------------------------------|------------------------------------|
| 필수   | Socket, core, thread, 주파수, 캐시           | 서버 토폴로지와 기본 성능 파악     |
| 운영   | 스케줄링, run queue, context switch, NUMA    | CPU 병목과 메모리 병목 구분        |
| 가상화 | vCPU, overcommit, CPU ready·steal, affinity  | VM 지연과 호스트 경합 분석         |
| 호환성 | ISA feature, microcode, BIOS, Hypervisor     | 실행 가능 여부와 마이그레이션 판단 |
| 고급   | cache miss, branch prediction, false sharing | 애플리케이션 성능 분석 지원        |

🟡 CPU 사용률 하나만으로 병목을 판단하지 않습니다. 전체 사용률이 낮아도 단일 스레드, 메모리 지연, VM 스케줄링 대기로 서비스가 느릴 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. CPU 구성과 성능 표현

### Socket, Core, Thread

| 용어              | 의미                          | 주의사항                                                |
|-------------------|-------------------------------|---------------------------------------------------------|
| Socket            | 물리 CPU 패키지 또는 CPU 소켓 | 소켓마다 NUMA node가 나뉠 수 있습니다.                  |
| Physical core     | 실제 연산 코어                | 코어 수가 동시 처리 능력의 기본 단위입니다.             |
| Logical processor | OS가 인식하는 실행 단위       | SMT 논리 프로세서는 물리 코어와 동일한 성능이 아닙니다. |
| Thread            | 실행 가능한 작업 단위         | 하나의 프로세스에 여러 스레드가 있을 수 있습니다.       |

일반적으로 다음 관계가 성립하지만, 서버와 플랫폼에 따라 예외가 있으므로 실제 값을 확인합니다.

```text
Logical processors = sockets × cores per socket × threads per core
```

### 주파수, IPC, 캐시

- **주파수(Clock)**: 초당 사이클 수입니다. 주파수가 높아도 작업의 명령어 수와 메모리 대기시간에 따라 처리량이 달라집니다.
- **IPC(Instructions Per Cycle)**: 한 사이클에 완료할 수 있는 명령어 수를 나타내는 성능 개념입니다. 서로 다른 CPU의 GHz만 직접 비교하면 안 됩니다.
- **Turbo**: 부하·전력·온도 조건이 허용하는 동안 일시적으로 높아지는 주파수입니다. 지속적인 전체 코어 성능은 All-core 동작과 냉각 조건을 함께 확인합니다.
- **Cache**: CPU와 메모리 사이의 빠른 저장 공간입니다. L1·L2·L3 캐시 적중률이 낮으면 메모리 지연의 영향이 커질 수 있습니다.

### CPU 기능 확인

AES-NI, SSE4.2, AVX, AVX2, AVX-512와 같은 ISA 확장은 특정 암호화·벡터 연산·과학 계산 코드의 실행 경로에 영향을 줍니다. 애플리케이션이 특정 확장을 요구하는지와 운영 환경의 CPU가 해당 기능을 노출하는지 확인해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 운영체제 스케줄링과 관측

운영체제 스케줄러는 실행 가능한 스레드를 CPU에 배치하고, 우선순위·affinity·대기 상태를 조정합니다. CPU 장애 분석에서는 사용률을 다음처럼 분해해 확인합니다.

| 지표      | 의미                                  | 해석 예시                              |
|-----------|---------------------------------------|----------------------------------------|
| User      | 사용자 애플리케이션이 사용한 CPU 시간 | 계산 작업 또는 busy loop               |
| System    | 커널이 사용한 CPU 시간                | 시스템 콜, 네트워크, 파일 시스템 처리  |
| I/O wait  | I/O 완료를 기다리는 시간              | CPU보다 디스크·스토리지 병목 가능      |
| Idle      | 유휴 시간                             | CPU 여유가 있다는 의미입니다.          |
| Steal     | 가상화 호스트가 다른 VM에 할당한 시간 | VM이 물리 CPU를 받지 못한 상태         |
| Run queue | 실행 대기 중인 작업 수                | CPU 공급보다 runnable 작업이 많은 상태 |

다음 상황을 구분해야 합니다.

```text
전체 CPU 30% + 단일 스레드 100%   → 단일 실행 경로 포화
전체 CPU 90% + 응답 정상           → 계획된 처리량일 수 있음
전체 CPU 30% + I/O wait 증가       → CPU가 아닌 I/O 병목 가능
VM CPU 30% + steal/ready 증가      → Hypervisor CPU 경합 가능
```

Context switch가 지나치게 많으면 짧은 작업 전환 비용, lock contention, 과도한 스레드 수를 의심합니다. 반대로 CPU 사용률이 낮다고 해서 항상 정상인 것은 아니며, run queue와 애플리케이션 latency를 함께 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. NUMA와 메모리 배치

NUMA(Non-Uniform Memory Access)는 모든 CPU가 같은 비용으로 메모리에 접근하지 않는 구조입니다. 각 CPU 소켓에 가까운 메모리를 **local memory**, 다른 소켓에 연결된 메모리를 **remote memory**라고 합니다.

```text
NUMA node 0                         NUMA node 1
┌───────────────┐                    ┌───────────────┐
│ CPU + Memory │ <── interconnect ─>  │ CPU + Memory │
└───────────────┘                    └───────────────┘
```

원격 메모리 접근이 항상 장애를 의미하는 것은 아니지만, 대규모 데이터 처리나 지연시간에 민감한 서비스에서는 local memory 비율과 CPU·메모리 배치를 확인해야 합니다.

### 운영 시 확인할 항목

- 소켓별 코어 수와 메모리 용량이 균형을 이루는지 확인합니다.
- VM의 vCPU와 메모리가 특정 NUMA node에 과도하게 집중되지 않는지 확인합니다.
- CPU affinity를 임의로 고정하면 오히려 다른 NUMA node의 메모리를 사용하게 될 수 있습니다.
- 데이터베이스·캐시·HPC처럼 메모리 대역폭과 지연시간이 중요한 워크로드는 NUMA-aware 설정을 검토합니다.

NUMA 문제를 CPU 문제로 오인하지 않으려면 CPU 사용률 외에 메모리 대역폭, remote access, latency를 함께 측정해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 가상화 환경의 CPU

가상화에서는 VM에 할당한 vCPU가 곧 물리 코어가 아닙니다. Hypervisor가 여러 VM의 vCPU를 물리 CPU에 스케줄링합니다.

```text
Physical CPU
    │
    ├── Hypervisor scheduler
    │       ├── VM-A: vCPU 4개
    │       ├── VM-B: vCPU 8개
    │       └── VM-C: vCPU 2개
    │
    └── Host services
```

### 핵심 개념

| 개념               | 설명                                      | 운영상 주의사항                                             |
|--------------------|-------------------------------------------|-------------------------------------------------------------|
| vCPU               | VM에 노출되는 가상 실행 단위              | 많이 할당한다고 항상 빨라지지 않습니다.                     |
| Overcommit         | 물리 CPU보다 많은 vCPU를 할당하는 상태    | 경합과 스케줄링 지연이 증가할 수 있습니다.                  |
| CPU ready          | VM이 CPU를 요청했지만 실행을 기다린 시간  | VMware에서 호스트 경합을 판단하는 지표입니다.               |
| Steal time         | 다른 VM 때문에 게스트가 CPU를 빼앗긴 시간 | Linux 게스트에서 확인할 수 있습니다.                        |
| Affinity/pinning   | 특정 논리 CPU에 실행을 고정               | NUMA와 함께 설계하지 않으면 역효과가 날 수 있습니다.        |
| Compatibility mode | VM에 공통 CPU 기능만 노출                 | 라이브 마이그레이션에 유리하지만 기능이 제한될 수 있습니다. |

Hyper-V의 Processor Compatibility와 VMware EVC는 주로 VM 이동성을 높이기 위한 기능입니다. 실제 CPU의 성능·발열·BIOS·메모리 토폴로지까지 검증하지는 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 명령어 세트와 호환성

### 호환성의 세 가지 층위

| 층위          | 확인 대상                      | 대표적인 테스트 방법         |
|---------------|--------------------------------|------------------------------|
| 바이너리 실행 | OS와 CPU가 명령어를 실행하는지 | 실제 CPU, VM CPU model, QEMU |
| 플랫폼 지원   | BIOS, 소켓, 칩셋, microcode    | 실제 서버와 제조사 지원 목록 |
| 운영 성능     | 성능, 전력, 발열, NUMA         | 실제 CPU·메모리·냉각 환경    |

VM과 QEMU는 명령어 feature와 애플리케이션 fallback 경로를 테스트하는 데 유용합니다. 하지만 BIOS 인식, POST, 실제 발열, 전력, sustained all-core 성능은 실제 플랫폼에서 확인해야 합니다.

### 빌드와 런타임 분기

특정 최신 CPU에만 존재하는 명령어로 바이너리를 빌드하면 구형 CPU에서 `Illegal instruction` 오류가 발생할 수 있습니다. 운영 환경에서는 공통 baseline을 정하고, 실행 시 CPU 기능을 확인하여 최적화 경로를 선택합니다.

```text
기본 경로: 공통 x86-64 또는 x86-64-v2
최적화 경로: AVX2
고급 경로: AVX-512
실행 시: CPUID 확인 후 지원 경로 선택
```

### 테스트 장비 선정

모든 CPU 세대를 구매하기보다 다음 feature group과 플랫폼 경계를 대표하는 장비를 선정합니다.

```text
최저 지원 CPU 1대
일반 Intel 서버 CPU 1대
일반 AMD 서버 CPU 1대
AVX2 또는 특수 명령어가 필요한 경우 해당 CPU 1대
운영과 동일한 서버 플랫폼 1대
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. CPU 성능 장애 진단

### 증상별 1차 판단

| 증상                        | 우선 확인할 항목                             | 흔한 오해                                 |
|-----------------------------|----------------------------------------------|-------------------------------------------|
| CPU 사용률 100%             | 단일 코어, process, thread, run queue        | 전체 평균만 보고 증설                     |
| CPU 사용률 낮음 + 지연 증가 | I/O wait, memory latency, lock, network      | CPU가 여유라서 애플리케이션 정상으로 판단 |
| VM만 느림                   | CPU ready, steal, overcommit, noisy neighbor | 게스트의 CPU 사용률만 확인                |
| 부하 후 성능 하락           | 온도, Turbo 지속성, power limit, throttling  | 정격 주파수만 비교                        |
| 특정 서버에서만 실행 실패   | ISA feature, microcode, BIOS, VM CPU masking | 애플리케이션 버그로만 판단                |
| 코어 수 증가 후 성능 저하   | NUMA, lock contention, 스케줄링 비용         | vCPU를 늘리면 항상 빨라진다고 판단        |

### 진단 순서

```text
1. 장애 범위와 발생 시각 확인
2. 전체 CPU와 코어별 사용률 비교
3. User/System/I/O wait/Steal 분해
4. Run queue, latency, context switch 확인
5. 메모리·NUMA·네트워크·스토리지 지표 비교
6. 프로세스와 스레드별 hotspot 확인
7. 변경 이력, throttling, microcode, Hypervisor 경합 확인
8. 증설 전 부하 테스트와 병목 재현
```

CPU 사용률만 높고 run queue와 latency가 정상이라면 즉시 증설하지 않습니다. 반대로 CPU 사용률이 낮아도 단일 스레드 또는 메모리 지연으로 SLA가 깨지면 CPU 구조와 애플리케이션 경로를 함께 분석합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 용량 계획과 하드웨어 선정

CPU를 선정할 때 GHz만 비교하지 않습니다. 워크로드의 특성에 따라 판단 기준이 달라집니다.

| 워크로드           | 주요 기준                                             |
|--------------------|-------------------------------------------------------|
| 웹·API             | 코어 수, 단일 스레드 latency, TLS 암호화 성능         |
| 데이터베이스       | 코어 성능, 메모리 용량·대역폭, NUMA, 스토리지 latency |
| 배치·렌더링        | 전체 코어 수, sustained all-core 성능, 전력·냉각      |
| 가상화 호스트      | 코어 수, 메모리 대역폭, NUMA, VM 경합 여유            |
| 암호화·압축        | AES-NI, AVX 계열, 라이브러리 지원 여부                |
| 라이선스 민감 제품 | 필요한 성능과 라이선스 산정 코어 수의 균형            |

### 용량 계획 원칙

- 평균 CPU 사용률뿐 아니라 peak, p95/p99 latency, run queue를 사용합니다.
- 확장 후에도 NUMA node와 메모리 채널 균형이 유지되는지 확인합니다.
- CPU 증설 전에 메모리 대역폭, 디스크, 네트워크가 병목인지 확인합니다.
- 운영 중인 OS·Hypervisor·애플리케이션의 CPU 지원 목록을 확인합니다.
- 전력·발열·냉각 용량과 장애 시 여유 용량을 포함합니다.
- 코어 수 증가로 상용 소프트웨어 라이선스가 증가하는지 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 보안과 유지보수

CPU와 플랫폼 유지보수는 성능뿐 아니라 보안과도 연결됩니다.

- Spectre·Meltdown 계열 취약점과 같은 CPU 취약점의 mitigation 상태를 확인합니다.
- BIOS, UEFI, microcode, OS 업데이트의 적용 순서와 재부팅 영향을 관리합니다.
- 보안 mitigation 적용 후 성능 변화와 SLA 영향을 측정합니다.
- 운영 서버의 CPU feature를 임의로 변경하지 않고 변경 이력을 남깁니다.
- 라이브 마이그레이션 환경에서는 클러스터 노드 간 공통 CPU feature를 유지합니다.
- 신규 CPU 도입 시 Hypervisor, 백업 솔루션, 모니터링 에이전트의 지원 여부를 확인합니다.

🟡 보안 패치로 성능이 변할 수 있으므로 패치 전후에 동일한 workload와 지표로 비교해야 합니다. 측정 없이 mitigation을 해제하는 것은 권장하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 운영 체크리스트

### Linux

```bash
# CPU 토폴로지와 기능
lscpu
lscpu --extended

# NUMA 구성
numactl -H

# CPU별 사용률과 run queue 관찰
mpstat -P ALL 1
vmstat 1

# 프로세스별 CPU 사용량
ps -eo pid,psr,pcpu,stat,comm --sort=-pcpu | head

# 프로세스 성능 카운터 예시
perf stat -p <PID>
```

### Windows Server

```powershell
# CPU 토폴로지
Get-CimInstance Win32_Processor |
    Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed

# 전체 CPU 사용률
Get-Counter '\Processor(_Total)\% Processor Time'

# 실행 큐 길이
Get-Counter '\System\Processor Queue Length'
```

### 점검 질문

| 질문                                          | 확인 결과                                |
|-----------------------------------------------|------------------------------------------|
| 물리 코어와 논리 프로세서 수를 알고 있는가?   | 서버 인벤토리에 기록합니다.              |
| CPU 병목과 I/O·메모리 병목을 구분했는가?      | 분해 지표와 latency를 함께 봅니다.       |
| VM의 CPU 경합 지표를 확인했는가?              | Host와 guest 지표를 함께 봅니다.         |
| NUMA 배치가 워크로드에 적합한가?              | 소켓·메모리·vCPU 배치를 확인합니다.      |
| CPU feature와 플랫폼 지원을 검증했는가?       | 대표 실물 장비와 VM 테스트를 조합합니다. |
| 증설 후 라이선스·전력·냉각 비용을 계산했는가? | 구매 의사결정에 포함합니다.              |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [CPU 아키텍처: CISC vs RISC](cpu_cisc_risc_concepts.md)
- [Linux 스케줄러 개념](../linux/scheduler_concepts.md)
- [Linux perf](../linux/perf.md)
- [Windows Server 리소스 분석](../windows/windows_server_resource_analysis.md)
- Microsoft Learn: [Hyper-V processor compatibility](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/processor-compatibility-mode) — ★★★☆☆
- Linux Kernel Documentation: [Scheduler](https://docs.kernel.org/scheduler/) — ★★★☆☆
- Linux man-pages: [lscpu(1)](https://man7.org/linux/man-pages/man1/lscpu.1.html) — ★★★☆☆
- Linux man-pages: [perf-stat(1)](https://man7.org/linux/man-pages/man1/perf-stat.1.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-21

**마지막 업데이트**: 2026-08-21

© 2026 siasia86. Licensed under CC BY 4.0.
