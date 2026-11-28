# Hyper-V

Windows에 들어 있는 하이퍼바이저입니다. Windows Server와 Windows 10·11 Pro·Enterprise에서 켜서 가상 머신(VM)을 만들고 운영합니다. 이 문서만으로 요구 사항 확인 → 설치 → 가상 스위치 → Linux VM 만들기 → 검증까지 PowerShell로 따라 할 수 있게 썼습니다.

- 기준: Windows Server 2025, Windows 11 Pro·Enterprise의 Hyper-V
- 예제 시험: 미실행. 명령과 요구 사항은 Microsoft Learn 문서와 Microsoft 공식 저장소의 스크립트(2026-11-23 확인)와 대조했습니다

## 목차

| 섹션                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 요구 사항](#2-요구-사항) / [3. 설치](#3-설치)                                                      |
| [4. 가상 스위치](#4-가상-스위치) / [5. Linux VM 만들기](#5-linux-vm-만들기) / [6. 운영 명령](#6-운영-명령)                  |
| [7. 체크포인트](#7-체크포인트) / [8. VM 안에서 가상화·컨테이너 쓰기](#8-vm-안에서-가상화컨테이너-쓰기) / [9. 검증](#9-검증) |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                        |

---

## 1. 개요

| 항목           | 내용                                                                   |
|----------------|------------------------------------------------------------------------|
| 종류           | Type 1 하이퍼바이저 (Windows 자체도 하이퍼바이저 위의 파티션으로 동작) |
| 관리 도구      | Hyper-V 관리자(GUI), PowerShell `Hyper-V` 모듈, Windows Admin Center   |
| VM 세대        | Generation 1(BIOS), Generation 2(UEFI, 보안 부팅). 새 VM은 Gen 2 권장  |
| 디스크 형식    | VHDX (VHD보다 큰 용량과 손상 방지 지원)                                |
| 여러 서버 관리 | 장애 조치 클러스터, SCVMM                                              |

같은 PC에서 VirtualBox·VMware Workstation을 함께 쓰면, Hyper-V를 켠 뒤로는 그 프로그램들이 Hyper-V 위에서(Windows Hypervisor Platform) 동작해 성능이나 기능이 달라질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 요구 사항

| 항목   | 조건                                                                                         |
|--------|----------------------------------------------------------------------------------------------|
| OS     | Windows Server, 또는 Windows 10·11 Pro·Enterprise·Education (Home 불가)                      |
| CPU    | 64비트, SLAT(Second Level Address Translation), VM Monitor Mode 확장(Intel VT-x·VT-c, AMD-V) |
| 펌웨어 | BIOS·UEFI에서 가상화 기능(Intel VT, AMD SVM)과 DEP(XD·NX) 켜짐                               |
| 메모리 | 최소 4 GB (VM 메모리 합계만큼 더 필요)                                                       |

확인 명령 (PowerShell 또는 명령 프롬프트):

```powershell
systeminfo
# 영문 Windows 기준: "Hyper-V Requirements" 항목이 모두 "Yes"이면 설치 가능
# "A hypervisor has been detected"라고 나오면 이미 켜져 있음
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설치

관리자 권한 PowerShell에서 실행하고, 끝나면 재부팅합니다.

```powershell
# Windows Server
Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart

# Windows 10·11
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

설치 확인:

```powershell
Get-WindowsFeature -Name Hyper-V                                   # Server: Installed
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V  # Client: State Enabled
Get-VMHost | Select-Object Name, VirtualMachinePath, VirtualHardDiskPath
```

VM과 디스크 기본 저장 위치는 여유 공간이 큰 드라이브로 바꿔 두면 좋습니다.

```powershell
Set-VMHost -VirtualMachinePath 'D:\Hyper-V' -VirtualHardDiskPath 'D:\Hyper-V\Disks'
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 가상 스위치

VM의 네트워크는 가상 스위치에 연결합니다.

| 종류           | 연결 범위                                   | 주 용도                          |
|----------------|---------------------------------------------|----------------------------------|
| External       | 물리 네트워크 (호스트 NIC를 공유)           | VM을 사내망의 장비처럼 노출      |
| Internal       | 호스트 ↔ VM                                 | 호스트와만 통신, NAT와 함께 사용 |
| Private        | VM ↔ VM                                     | 격리된 시험망                    |
| Default Switch | NAT로 외부 접속 (Windows 10·11에 자동 생성) | 설정 없이 인터넷만 필요할 때     |

```powershell
Get-NetAdapter                                                     # 물리 NIC 이름 확인

# External: 호스트도 이 스위치를 통해 계속 통신하게 함
New-VMSwitch -Name 'External' -NetAdapterName 'Ethernet' -AllowManagementOS $true

# Internal / Private
New-VMSwitch -Name 'Internal' -SwitchType Internal
New-VMSwitch -Name 'Lab'      -SwitchType Private

Get-VMSwitch
```

External 스위치를 만드는 순간 호스트 네트워크가 잠깐 끊깁니다. 원격(RDP)으로 작업 중이면 연결이 끊길 수 있으므로 콘솔에서 하거나 시점을 정해 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Linux VM 만들기

Ubuntu Server ISO로 Generation 2 VM을 만드는 예입니다.

```powershell
$vm   = 'ubuntu01'
$iso  = 'D:\ISO\ubuntu-24.04-live-server-amd64.iso'
$vhdx = "D:\Hyper-V\Disks\$vm.vhdx"

New-VM -Name $vm -Generation 2 -MemoryStartupBytes 2GB `
       -NewVHDPath $vhdx -NewVHDSizeBytes 40GB -SwitchName 'External'

Set-VMProcessor -VMName $vm -Count 2
Set-VMMemory    -VMName $vm -DynamicMemoryEnabled $false

# Linux는 Microsoft UEFI CA 보안 부팅 템플릿을 써야 부팅됨
Set-VMFirmware -VMName $vm -SecureBootTemplate MicrosoftUEFICertificateAuthority

Add-VMDvdDrive -VMName $vm -Path $iso
Set-VMFirmware -VMName $vm -FirstBootDevice (Get-VMDvdDrive -VMName $vm)

Start-VM -Name $vm
vmconnect.exe localhost $vm          # 콘솔 창을 열어 OS 설치
```

| 설정                 | 이유                                                              |
|----------------------|-------------------------------------------------------------------|
| `-Generation 2`      | UEFI·보안 부팅, 최근 배포판 권장. 만든 뒤에는 세대를 바꿀 수 없음 |
| `SecureBootTemplate` | 기본 템플릿(Microsoft Windows)으로는 Linux 부트로더가 거부됨      |
| 동적 메모리 끔       | 시험·DB 서버는 고정 메모리가 결과를 예측하기 쉬움                 |
| `FirstBootDevice`    | 처음 한 번 ISO로 부팅. 설치 후 `Remove-VMDvdDrive`로 빼도 됨      |

설치가 끝난 Linux 안에서는 Hyper-V 연동 서비스를 확인합니다. 최근 배포판 커널에는 드라이버가 들어 있고, 호스트에서 VM IP를 보려면 KVP 데몬이 필요합니다.

```bash
lsmod | grep hv_                                     # hv_vmbus, hv_netvsc, hv_storvsc 등
sudo apt-get install -y linux-cloud-tools-virtual    # Ubuntu: KVP 데몬 (RHEL 계열은 hyperv-daemons)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영 명령

| 목적              | 명령                                                                                                   |
|-------------------|--------------------------------------------------------------------------------------------------------|
| 목록·상태         | `Get-VM`                                                                                               |
| 시작·종료         | `Start-VM -Name <VM>`, `Stop-VM -Name <VM>` (게스트 종료 요청)                                         |
| 강제 종료         | `Stop-VM -Name <VM> -TurnOff`                                                                          |
| VM IP             | `Get-VMNetworkAdapter -VMName <VM> \| Select-Object VMName, IPAddresses`                               |
| CPU·메모리 변경   | `Set-VMProcessor -VMName <VM> -Count 4`, `Set-VMMemory -VMName <VM> -StartupBytes 4GB` (종료 상태에서) |
| 디스크 늘리기     | `Resize-VHD -Path <vhdx> -SizeBytes 80GB` 후 게스트에서 파티션 확장                                    |
| 자동 시작         | `Set-VM -Name <VM> -AutomaticStartAction Start -AutomaticStopAction ShutDown`                          |
| 내보내기·가져오기 | `Export-VM -Name <VM> -Path D:\Export`, `Import-VM -Path <vmcx> -Copy -GenerateNewId`                  |
| 삭제              | `Remove-VM -Name <VM> -Force` (VHDX 파일은 남으므로 따로 지움)                                         |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 체크포인트

시험 전 상태를 저장해 두고 되돌릴 때 씁니다.

```powershell
Checkpoint-VM   -Name ubuntu01 -SnapshotName 'clean-install'
Get-VMSnapshot  -VMName ubuntu01
Restore-VMSnapshot -VMName ubuntu01 -Name 'clean-install' -Confirm:$false
Remove-VMSnapshot  -VMName ubuntu01 -Name 'clean-install'
```

| 종류              | 동작                                                  | 용도              |
|-------------------|-------------------------------------------------------|-------------------|
| Production (기본) | 게스트 안에서 VSS·파일 시스템 동결로 일관된 상태 저장 | 운영 VM           |
| Standard          | 메모리까지 그대로 저장                                | 시험 중 상태 보존 |

```powershell
Set-VM -Name ubuntu01 -CheckpointType Standard
```

체크포인트는 차등 디스크(`.avhdx`)로 쌓여 디스크 성능과 공간에 영향을 주므로, 백업으로 오래 두지 않고 시험이 끝나면 지웁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. VM 안에서 가상화·컨테이너 쓰기

### 8-1. MAC 주소 스푸핑

VM 안에서 Docker macvlan, 브리지, 다른 VM처럼 여러 MAC을 쓰는 경우 켭니다.

```powershell
Get-VMNetworkAdapter -VMName ubuntu01 | Set-VMNetworkAdapter -MacAddressSpoofing On
Get-VMNetworkAdapter -VMName ubuntu01 | Select-Object VMName, MacAddressSpoofing
```

### 8-2. 중첩 가상화

VM 안에서 다시 Hyper-V·KVM·kind 같은 가상화를 쓰려면 VM이 꺼진 상태에서 CPU 가상화 확장을 노출합니다.

```powershell
Stop-VM -Name ubuntu01
Set-VMProcessor -VMName ubuntu01 -ExposeVirtualizationExtensions $true
Set-VMMemory    -VMName ubuntu01 -DynamicMemoryEnabled $false
Get-VMNetworkAdapter -VMName ubuntu01 | Set-VMNetworkAdapter -MacAddressSpoofing On   # 안쪽 VM이 네트워크를 쓰려면
Start-VM -Name ubuntu01
```

```bash
# Linux 게스트 안에서 확인
grep -c -E 'vmx|svm' /proc/cpuinfo       # 0보다 크면 노출됨
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용        | 명령                                                           | 기대 결과                                                                |
|------|------------------|----------------------------------------------------------------|--------------------------------------------------------------------------|
| 1    | 요구 사항        | `systeminfo`                                                   | Hyper-V Requirements 모두 "Yes"                                          |
| 2    | 설치             | `Get-WindowsFeature Hyper-V` 또는 `Get-WindowsOptionalFeature` | Installed / Enabled                                                      |
| 3    | 스위치           | `Get-VMSwitch`                                                 | 만든 스위치와 종류                                                       |
| 4    | VM 상태          | `Get-VM -Name ubuntu01`                                        | `State Running`                                                          |
| 5    | 보안 부팅 템플릿 | `Get-VMFirmware -VMName ubuntu01`                              | `MicrosoftUEFICertificateAuthority`                                      |
| 6    | VM IP            | `Get-VMNetworkAdapter -VMName ubuntu01`                        | `IPAddresses`에 주소 (KVP 데몬 필요)                                     |
| 7    | 게스트 네트워크  | 게스트에서 `ip -br addr`, `ping <게이트웨이>`                  | 주소와 응답                                                              |
| 8    | 원격 접속        | 다른 PC에서 `ssh <VM IP>`                                      | 접속                                                                     |
| 9    | 체크포인트       | `Checkpoint-VM` → 변경 → `Restore-VMSnapshot`                  | 변경 전 상태로 돌아옴                                                    |
| 10   | 8절 설정         | `Get-VMProcessor`, `Get-VMNetworkAdapter`                      | 필요할 때만 `ExposeVirtualizationExtensions`·`MacAddressSpoofing`이 켜짐 |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                            | 원인                                 | 해결 방법                                              |
|-------------------------------------------------|--------------------------------------|--------------------------------------------------------|
| 설치 목록에 Hyper-V가 없음                      | Windows Home, 또는 CPU 미지원        | 에디션 확인, `systeminfo` 요구 사항 확인               |
| 펌웨어에서 가상화가 꺼져 있다는 설치 오류       | BIOS·UEFI에서 가상화 꺼짐            | 펌웨어 설정에서 Intel VT·AMD SVM 켜기                  |
| Linux VM이 부팅 중 `Secure Boot` 오류로 멈춤    | 보안 부팅 템플릿이 Microsoft Windows | `MicrosoftUEFICertificateAuthority` 템플릿 (5절)       |
| VM에서 외부 통신 안 됨                          | 스위치 종류가 Private·Internal       | External 또는 Default Switch, Internal이면 NAT 구성    |
| External 스위치 생성 후 호스트 네트워크 끊김    | `-AllowManagementOS` 없이 만듦       | `Set-VMSwitch -Name External -AllowManagementOS $true` |
| 호스트에서 VM IP가 보이지 않음                  | 게스트에 KVP 데몬 없음               | `linux-cloud-tools-virtual`·`hyperv-daemons` 설치      |
| VM 안 Docker macvlan 컨테이너에 외부 접속 안 됨 | MAC 스푸핑 꺼짐                      | 8-1                                                    |
| VM 안에서 KVM·kind·Docker Desktop이 가상화 오류 | 중첩 가상화 꺼짐                     | 8-2                                                    |
| 디스크 공간이 계속 줄어듦                       | 체크포인트 `.avhdx`가 쌓임           | 쓰지 않는 체크포인트 삭제 (7절)                        |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Windows Server 핵심 개념](./windows_server_key_concepts.md) — 장애 조치 클러스터, CSV, S2D
- [SCVMM](./scvmm_guide.md) — 여러 Hyper-V 호스트 관리
- [Windows Server 에디션과 라이선스](./windows_server_editions_licensing.md) — 가상화 권한
- [Vagrant](../iac/vagrant.md) — Hyper-V provider로 VM을 코드로 만들기 (10절)
- [Packer](../iac/packer.md) — `hyperv-iso` 빌더로 VM 이미지 만들기 (4절)
- [Windows 골든 이미지](./windows_golden_image_sysprep.md) — Packer·sysprep로 일반화 VHDX 만들기
- [Docker 네트워크](../containers/docker_network.md) — VM 안 macvlan과 MAC 스푸핑

---

## 참고 자료

- Microsoft Learn: [Install Hyper-V (Windows Server)](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v) — ★★★☆☆
- Microsoft Learn: [Enable Hyper-V on Windows](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v) — ★★★☆☆
- Microsoft Learn: [System requirements for Hyper-V on Windows](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/system-requirements-for-hyper-v-on-windows) — ★★★☆☆
- Microsoft Learn: [Create a virtual switch](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/create-a-virtual-switch-for-hyper-v-virtual-machines) — ★★★☆☆
- Microsoft Learn: [Create a virtual machine in Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/create-a-virtual-machine-in-hyper-v) — ★★★☆☆
- Microsoft Learn: [Best practices for running Linux on Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/best-practices-for-running-linux-on-hyper-v) — ★★★☆☆
- Microsoft Learn: [Nested virtualization](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/nested-virtualization) — ★★★☆☆
- Microsoft Learn: [Set-VMFirmware](https://learn.microsoft.com/en-us/powershell/module/hyper-v/set-vmfirmware) · [Checkpoint-VM](https://learn.microsoft.com/en-us/powershell/module/hyper-v/checkpoint-vm) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-28

© 2026 siasia86. Licensed under CC BY 4.0.
