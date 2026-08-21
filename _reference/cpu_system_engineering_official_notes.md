---
name: cpu-system-engineering-official-notes
description: CPU 시스템 운영·성능·NUMA·가상화·호환성 관련 공식 참조 노트.
tags:
  - cpu
  - performance
  - numa
  - virtualization
  - hyper-v
last_checked: 2026-08-21
sources:
  - https://docs.kernel.org/scheduler/
  - https://man7.org/linux/man-pages/man1/lscpu.1.html
  - https://man7.org/linux/man-pages/man1/perf-stat.1.html
  - https://man7.org/linux/man-pages/man5/proc_stat.5.html
  - https://man7.org/linux/man-pages/man8/numactl.8.html
  - https://man7.org/linux/man-pages/man8/numastat.8.html
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/processor-compatibility-mode
---

# CPU 시스템 운영 공식 참조 노트

## 1. 참조 범위

시스템 엔지니어 관점의 CPU 운영·성능·가상화·호환성 문서에서 사용하는 공식 정의와 검증 기준을 정리합니다. CISC/RISC 설계 철학 자체는 [CPU 아키텍처: CISC vs RISC](../01_fundamentals/cs/cpu_cisc_risc_concepts.md)에서 다룹니다.

## 2. Linux CPU 정보와 측정

### `lscpu`

Linux `lscpu(1)` 매뉴얼에 따르면 `lscpu`는 sysfs와 `/proc/cpuinfo` 등을 사용해 CPU 아키텍처 정보를 표시합니다. CPU 수, thread, core, socket, NUMA node, cache, microcode 정보를 확인할 수 있습니다.

가상화 환경에서는 출력 정보가 일반적으로 물리 호스트가 아니라 게스트 운영체제에 노출된 CPU 구성과 기능을 반영합니다. 따라서 VM 내부의 `lscpu` 결과만으로 물리 서버의 전체 CPU 토폴로지를 판단하지 않습니다.

### `perf stat`

`perf stat`은 명령어 또는 프로세스를 실행하면서 성능 카운터 통계를 수집합니다. CPU 사용률만으로 병목을 판단하기 어려울 때 cycles, instructions, branch와 같은 카운터를 함께 측정하는 기준으로 사용합니다.

## 3. Linux 스케줄러와 NUMA

Linux Kernel Documentation의 Scheduler 문서는 CPU 스케줄러, scheduler domain, CFS/EEVDF, capacity-aware scheduling, energy-aware scheduling, utilization clamping 등의 영역을 제공합니다.

운영 문서에서는 다음 지표를 함께 해석합니다.

| 지표           | 해석 기준                                                   |
|----------------|-------------------------------------------------------------|
| CPU 사용률     | 사용자·커널·유휴·I/O 대기 등으로 분해합니다.                |
| Run queue      | 실행 가능한 작업이 CPU를 기다리는 정도를 확인합니다.        |
| Context switch | 스레드 전환 비용과 과도한 스레드·경합 여부를 확인합니다.    |
| Steal time     | 가상화 게스트가 물리 CPU를 할당받지 못한 시간을 확인합니다. |
| NUMA 배치      | CPU·메모리 위치와 원격 메모리 접근 영향을 확인합니다.       |

## 4. Hyper-V Processor Compatibility

Microsoft Learn의 **Processor compatibility for Hyper-V virtual machines** 문서에 따르면 Hyper-V는 호스트의 CPU 기능을 VM에 노출할 수 있습니다. 호스트마다 CPU 기능이 다르면 Processor Compatibility mode가 VM에 공통 CPU 기능 집합을 노출하여 호스트·클러스터 간 VM 이동을 지원합니다.

이 기능은 다음과 같이 해석합니다.

- VM 이동성을 위한 CPU feature 제한 기능입니다.
- 실제 CPU의 성능·발열·BIOS·메모리 토폴로지를 에뮬레이션하지 않습니다.
- Microsoft는 일반적으로 마이그레이션 중에만 활성화하고, 이후에는 호스트의 전체 CPU 기능을 사용하도록 비활성화하는 방식을 안내합니다.
- CPU 세대가 다른 클러스터에서 라이브 마이그레이션을 계속 사용해야 한다면 호환성 모드를 유지할 수 있습니다.

## 5. 문서 적용 기준

| 검증 대상                 | VM·에뮬레이션 | 실제 하드웨어             |
|---------------------------|---------------|---------------------------|
| CPU feature·바이너리 실행 | 적합          | 대표 장비로 보완          |
| OS·애플리케이션 실행      | 적합          | 운영 플랫폼에서 최종 확인 |
| BIOS·POST·microcode       | 제한적        | 필요                      |
| NUMA·성능·전력·발열       | 제한적        | 필요                      |
| Hyper-V VM 이동성         | 적합          | 클러스터 노드 조합 확인   |

CPU 호환성 테스트는 모든 CPU 세대를 구매하기보다 최저 지원 CPU, 주요 Intel·AMD 플랫폼, 필요한 ISA feature, 운영과 동일한 Hypervisor 플랫폼을 대표 장비로 선정하고 VM 테스트를 보완하는 방식으로 구성합니다.
