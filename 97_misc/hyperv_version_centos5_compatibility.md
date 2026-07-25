# Hyper-V 버전별 CentOS 5.11 호환성 비교

Windows Server 2008, 2008 R2, 2012 Hyper-V에서 CentOS 5.11을 운영할 때의 호환성, 제약, I/O 대응 능력을 비교합니다.

## 목차

| 섹션                                                                                                                           |
|--------------------------------------------------------------------------------------------------------------------------------|
| [1. 종합 비교](#1-종합-비교) / [2. 호스트 라이프사이클](#2-호스트-라이프사이클) / [3. Hyper-V 기능 비교](#3-hyper-v-기능-비교) |
| [4. CentOS 5.11 호환성](#4-centos-511-호환성) / [5. I/O 경합 대응 능력](#5-io-경합-대응-능력) / [6. 참고 자료](#6-참고-자료)   |

---

## 1. 종합 비교

| 항목             | 2008 (Hyper-V 1.0) | 2008 R2 (Hyper-V 2.0)     | 2012 (Hyper-V 3.0)           |
|------------------|--------------------|---------------------------|------------------------------|
| CentOS 5.11 동작 | ✅ 정상            | ✅ 정상                   | ✅ 정상                      |
| 호스트 EOL       | 2020-01-14         | 2020-01-14                | 2023-10-10 (ESU 2026-10)     |
| LIS 지원         | LIS 2.x (폐쇄)     | LIS 3.x (폐쇄)            | LIS 4.x (폐쇄)               |
| Storage QoS      | ❌                 | ❌                        | ❌                           |
| Live Migration   | ❌                 | ✅                        | ✅                           |
| VHDX 지원        | ❌ (VHD만)         | ❌ (VHD만)                | ✅                           |
| CSV 클러스터     | ❌                 | ✅                        | ✅                           |
| I/O 경합 대응    | VHD 분리만 가능    | VHD 분리 + Live Migration | VHD 분리 + Storage Migration |
| 보안 상태        | ❌ EOL 종료        | ❌ EOL 종료               | 🟡 ESU 2026-10 종료 예정     |
| 운영 권장 여부   | ❌ 즉시 교체       | ❌ 즉시 교체              | 🟡 1년 내 교체 권장          |

**결론**: 세 버전 모두 CentOS 5.11과의 **동작 호환성 문제는 없습니다**. 당시 공식 지원 조합이었기 때문입니다. 차이는 I/O 경합 대응 능력과 보안 상태에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 호스트 라이프사이클

| 버전           | 출시       | Mainstream 종료 | Extended 종료 | ESU 종료   | 현재 상태 (2026-07)    |
|----------------|------------|-----------------|---------------|------------|------------------------|
| Server 2008    | 2008-05-06 | 2015-01-13      | 2020-01-14    | 2024 (Y4)  | ❌ 지원 종료           |
| Server 2008 R2 | 2009-10-22 | 2015-01-13      | 2020-01-14    | 2024 (Y4)  | ❌ 지원 종료           |
| Server 2012    | 2012-10-30 | 2018-10-09      | 2023-10-10    | 2026-10-13 | 🟡 ESU 중 (3개월 남음) |
| Server 2012 R2 | 2012-10-18 | 2018-10-09      | 2023-10-10    | 2026-10-13 | 🟡 ESU 중 (3개월 남음) |

### EOL 호스트 운영 위험

| 위험 요소                  | 2008/2008 R2 | 2012                 |
|----------------------------|--------------|----------------------|
| 보안 패치                  | 없음 (2020~) | ESU만 (2026-10 종료) |
| 신규 CVE 대응              | 불가         | 제한적               |
| Microsoft 기술지원         | 없음         | ESU 계약 시만        |
| 하드웨어 드라이버 업데이트 | 없음         | 없음                 |
| 컴플라이언스 감사          | 부적합       | 조건부 적합          |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Hyper-V 기능 비교

### 가상화 핵심 기능

| 기능            | 2008      | 2008 R2   | 2012             |
|-----------------|-----------|-----------|------------------|
| Hyper-V 버전    | 1.0       | 2.0       | 3.0              |
| 최대 vCPU/VM    | 4         | 4         | 64               |
| 최대 메모리/VM  | 64GB      | 64GB      | 1TB              |
| 최대 VM/호스트  | ~150      | ~384      | 1024             |
| VHD 최대 크기   | 2TB (VHD) | 2TB (VHD) | 64TB (VHDX)      |
| VHDX 지원       | ❌        | ❌        | ✅               |
| Generation 2 VM | ❌        | ❌        | ❌ (2012 R2부터) |

### 클러스터 및 고가용성

| 기능                      | 2008 | 2008 R2      | 2012           |
|---------------------------|------|--------------|----------------|
| Failover Clustering       | ✅   | ✅           | ✅             |
| CSV (Cluster Shared Vol.) | ❌   | ✅           | ✅             |
| Live Migration            | ❌   | ✅ (1회 1VM) | ✅ (동시 다수) |
| Storage Live Migration    | ❌   | ❌           | ✅             |
| Hyper-V Replica           | ❌   | ❌           | ✅             |

### 스토리지

| 기능                          | 2008 | 2008 R2 | 2012       |
|-------------------------------|------|---------|------------|
| VHD 포맷                      | VHD  | VHD     | VHD + VHDX |
| VHDX 온라인 확장              | —    | —       | ✅         |
| Virtual Fibre Channel         | ❌   | ❌      | ✅         |
| Storage QoS                   | ❌   | ❌      | ❌ (2016+) |
| ODX (Offloaded Data Transfer) | ❌   | ❌      | ✅         |

### 네트워크

| 기능                 | 2008           | 2008 R2        | 2012             |
|----------------------|----------------|----------------|------------------|
| 가상 스위치          | 기본           | 기본           | 확장 가능 스위치 |
| NIC Teaming (호스트) | ❌ (3rd party) | ❌ (3rd party) | ✅ (내장)        |
| SR-IOV               | ❌             | ❌             | ✅               |
| PVLAN                | ❌             | ❌             | ✅               |
| 포트 미러링          | ❌             | ❌             | ✅               |

[⬆ 목차로 돌아가기](#목차)

---

## 4. CentOS 5.11 호환성

### 동작 호환성 판정

| 호스트  | CentOS 5.11 부팅 | 기본 동작 | LIS 필요 | 비고                        |
|---------|------------------|-----------|----------|-----------------------------|
| 2008    | ✅               | ✅        | 선택     | Gen 1 + IDE 에뮬레이션 정상 |
| 2008 R2 | ✅               | ✅        | 선택     | 동일                        |
| 2012    | ✅               | ✅        | 선택     | 동일                        |

세 버전 모두 **CentOS 5.11과 동작 호환성 문제 없습니다.** Gen 1 VM + IDE 에뮬레이션 조합은 모든 버전에서 지원됩니다.

### LIS 상태

| 항목                         | 현황                                        |
|------------------------------|---------------------------------------------|
| Microsoft 공식 지원 매트릭스 | CentOS 5.x/6.x **삭제됨** (7.x 이상만 나열) |
| LIS 다운로드                 | Microsoft 다운로드 센터 **폐쇄**            |
| 기존 설치된 LIS              | 정상 동작 (업데이트 불가)                   |
| LIS 없이 동작                | 가능 (IDE + Legacy NIC 에뮬레이션으로 동작) |

### LIS 유무에 따른 차이

| 컴포넌트    | LIS 없음                   | LIS 있음                |
|-------------|----------------------------|-------------------------|
| 디스크      | IDE 에뮬레이션 (큐 깊이 1) | storvsc (큐 깊이 64+)   |
| 네트워크    | Legacy NIC (100Mbps)       | netvsc (10Gbps)         |
| 시간 동기화 | NTP 수동 설정 필요         | Hyper-V TimeSync IC     |
| 셧다운      | ACPI만 (지연 있음)         | Shutdown IC (즉시 응답) |
| 하트비트    | 없음                       | 호스트가 VM 상태 감지   |
| 백업 일관성 | 비일관 (크래시 일관만)     | VSS 연동 (일관 백업)    |
| I/O 성능    | ~5,000 IOPS                | ~50,000+ IOPS           |

**[근거] storvsc 큐 깊이 vs IDE 에뮬레이션**

Linux 커널 `hv_storvsc` 드라이버는 SCSI 호스트 템플릿에서 LUN당 명령 큐 깊이를 깊게 정의합니다. 현재 mainline 기준 `cmd_per_lun = 2048`이며, LIS/커널 버전에 따라 실제 값은 다르지만 모두 IDE 에뮬레이션의 단일 명령 한계(큐 깊이 1)보다 훨씬 큽니다. 위 표의 `64+`는 보수적 하한값입니다.

```c
// drivers/scsi/storvsc_drv.c
static struct scsi_host_template scsi_driver = {
	.cmd_per_lun =		2048,
	.track_queue_depth =	1,
};
```

반면 Hyper-V Generation 1 VM의 IDE 컨트롤러는 legacy 하드웨어 에뮬레이션이며 명령 큐잉(NCQ/TCQ)을 지원하지 않아 큐 깊이가 사실상 1입니다. Microsoft 공식 문서는 IDE를 legacy 에뮬레이션으로 규정합니다.

> "Generation 1 virtual machines use legacy BIOS firmware and provide compatibility with legacy applications that require older hardware support, including 32-bit systems and legacy hardware emulation such as IDE controllers and virtual floppy disk files."

출처:

- Linux kernel `storvsc` driver: [drivers/scsi/storvsc_drv.c](https://github.com/torvalds/linux/blob/master/drivers/scsi/storvsc_drv.c) — ★★★★☆
- Hyper-V feature terminology (Microsoft): [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/features-terminology) — ★★★☆☆

### 실제 동작 시나리오

| 시나리오                    | LIS 없음                   | LIS 있음           |
|-----------------------------|----------------------------|--------------------|
| 게임 서버 기본 동작         | ✅ 동작                    | ✅ 동작            |
| I/O 경합 시 영향            | 극심 (큐 깊이 1)           | 완화 (큐 깊이 64+) |
| 호스트 셧다운 시 정상 종료  | 지연/강제 종료 가능        | 즉시 정상 종료     |
| 시간 동기화                 | drift 발생 가능            | 자동 동기화        |
| 호스트에서 VM 상태 모니터링 | 불가 (검은 화면 여부 불명) | 하트비트 감지      |

[⬆ 목차로 돌아가기](#목차)

---

## 5. I/O 경합 대응 능력

### 버전별 대응 수단

| 완화 방법                 | 2008 | 2008 R2 | 2012 | 효과  |
|---------------------------|------|---------|------|-------|
| VHD 물리 분리             | ✅   | ✅      | ✅   | ★★★★★ |
| Fixed VHD 사용            | ✅   | ✅      | ✅   | ★★★☆☆ |
| I/O timeout 조정 (게스트) | ✅   | ✅      | ✅   | ★★☆☆☆ |
| Live Migration            | ❌   | ✅      | ✅   | ★★★☆☆ |
| Storage Live Migration    | ❌   | ❌      | ✅   | ★★★★☆ |
| Storage QoS               | ❌   | ❌      | ❌   | —     |
| CSV 볼륨 분리             | ❌   | ✅      | ✅   | ★★★★☆ |

### 버전별 권장 대응

#### Windows Server 2008

```
유일한 방법: VHD를 별도 물리 디스크에 배치
```

- Live Migration 불가 → 서비스 중단 없이 VHD 이동 불가능
- CSV 없음 → 클러스터 공유 스토리지 활용 불가
- **VM 정지 → VHD 이동 → VM 시작** (다운타임 발생)

#### Windows Server 2008 R2

```
1순위: VHD 물리 분리 (다운타임 필요)
2순위: Live Migration으로 I/O 부하 낮은 노드 이동
```

- Live Migration 가능하지만 **한 번에 1 VM만** 이동 가능
- Storage Live Migration 불가 → VHD 자체 이동은 여전히 다운타임 필요
- CSV 지원 → 클러스터 볼륨 활용 가능

#### Windows Server 2012

```
1순위: Storage Live Migration (무중단 VHD 이동)
2순위: VHD를 별도 VHDX/물리 디스크로 이동
3순위: Live Migration으로 노드 이동
```

- **Storage Live Migration**: VM 실행 중 VHD를 다른 물리 디스크로 이동 가능 (무중단)
- VHDX 지원 → 4KB 정렬, 온라인 확장
- 동시 다수 Live Migration 가능

### 대응 능력 요약

| 호스트  | 무중단 I/O 분리 가능 여부 | 방법                       |
|---------|---------------------------|----------------------------|
| 2008    | ❌                        | VM 정지 후 VHD 이동만 가능 |
| 2008 R2 | 🟡 (노드 이동만)          | Live Migration (VM 이동)   |
| 2012    | ✅                        | Storage Live Migration     |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 참고 자료

- Windows Server 2008 Lifecycle: [learn.microsoft.com](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2008) — ★★★☆☆
- Windows Server 2008 R2 Lifecycle: [learn.microsoft.com](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2008-r2) — ★★★☆☆
- Windows Server 2012 Lifecycle: [learn.microsoft.com](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2012) — ★★★☆☆
- Hyper-V Generation 1 vs 2: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/should-i-create-a-generation-1-or-2-virtual-machine-in-hyper-v) — ★★★☆☆
- Supported Linux VMs on Hyper-V: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/Supported-CentOS-and-Red-Hat-Enterprise-Linux-virtual-machines-on-Hyper-V) — ★★★☆☆
- [_reference/hyperv_version_comparison_notes.md](../_reference/hyperv_version_comparison_notes.md)
- [_reference/hyperv_io_contention_notes.md](../_reference/hyperv_io_contention_notes.md)

---

**작성일**: 2026-07-16

**마지막 업데이트**: 2026-07-16

© 2026 siasia86. Licensed under CC BY 4.0.
