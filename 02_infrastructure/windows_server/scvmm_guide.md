# SCVMM (System Center Virtual Machine Manager) 가이드

SCVMM은 Microsoft의 엔터프라이즈급 VM 중앙 관리 플랫폼입니다.
여러 Hyper-V 호스트에 분산된 VM을 한 곳에서 프로비저닝, 모니터링, 관리합니다.

🟡 이 문서는 **VMM 2022 / VMM 2025** 기준으로 작성되었습니다. 버전별 차이가 있는 항목은 해당 섹션에 명시합니다.

## 목차

| 섹션                                                                        |
|-----------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 설치](#3-설치)        |
| [4. Hyper-V 호스트 관리](#4-hyper-v-호스트-관리) / [5. VM 관리](#5-vm-관리) |
| [6. 네트워크 및 스토리지](#6-네트워크-및-스토리지) / [7. 자동화](#7-자동화) |
| [8. 모니터링](#8-모니터링) / [9. 타 도구 비교](#9-타-도구-비교)             |

---

## 1. 개요

### SCVMM이란?

Microsoft System Center 제품군의 인프라 관리 컴포넌트입니다.
단일 콘솔에서 Hyper-V 호스트, 물리 서버, 스토리지, 네트워크를 통합 관리합니다.

```
SCVMM 없음 — 서버마다 개별 접속
  관리자 → Hyper-V Host A 직접 접속 → VM 생성
  관리자 → Hyper-V Host B 직접 접속 → VM 생성
  관리자 → Hyper-V Host C 직접 접속 → VM 생성

SCVMM 있음 — 중앙 콘솔에서 통합 관리
  관리자 → SCVMM 콘솔
              ├─→ Hyper-V Host A
              ├─→ Hyper-V Host B
              └─→ Hyper-V Host C
```

### System Center 제품군 내 위치

| 제품      | 약자  | 역할                           |
|-----------|-------|--------------------------------|
| **VMM**   | SCVMM | VM/인프라 관리                 |
| **SCOM**  | SCOM  | 모니터링 (Operations Manager)  |
| **SCCM**  | SCCM  | 엔드포인트 관리 (ConfigMgr)    |
| **SCDPM** | DPM   | 백업/복구                      |
| **SCO**   | SCO   | 워크플로 자동화 (Orchestrator) |

### 주요 기능

| 기능                    | 설명                                              |
|-------------------------|---------------------------------------------------|
| **VM 프로비저닝**       | 템플릿 기반 VM 대량 생성                          |
| **라이브 마이그레이션** | 서비스 중단 없이 VM을 다른 호스트로 이동          |
| **패브릭 관리**         | 호스트, 네트워크, 스토리지 통합 관리              |
| **베어메탈 배포**       | 물리 서버에 OS 배포 후 Hyper-V 호스트로 자동 등록 |
| **프라이빗 클라우드**   | 셀프서비스 포털 구성                              |
| **SDN 관리**            | 소프트웨어 정의 네트워크 구성                     |
| **역할 기반 접근**      | 팀별 권한 분리 (관리자/운영자/셀프서비스)         |
| **PowerShell 연동**     | 모든 작업 자동화 가능                             |

### 관리 가능한 대상

| 대상                   | 지원 수준                     |
|------------------------|-------------------------------|
| Hyper-V 호스트         | ✅ 완전 지원                  |
| VMware ESXi            | 🟡 제한적 (조회/마이그레이션) |
| Citrix XenServer       | 🟡 제한적                     |
| 물리 서버 (Bare Metal) | ✅ OS 배포까지                |
| SAN/NAS 스토리지       | ✅ 완전 지원                  |
| 가상 네트워크/SDN      | ✅ 완전 지원                  |
| KVM/Proxmox            | ❌ 미지원                     |
| Docker/Kubernetes      | ❌ Azure Arc 별도 필요        |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

### 구성 요소

```
┌──────────────────────────────────────────────────────────┐
│                      SCVMM Components                    │
│                                                          │
│  SCVMM Server          - core management server          │
│  SCVMM Console         - admin GUI (installable on PC)   │
│  SCVMM DB (SQL Server) - state/config store              │
│  VMM Agent             - installed on each Hyper-V host  │
└──────────────────────────────────────────────────────────┘
         │
         ├─→ Hyper-V Host 01 (VMM Agent)
         │     └─→ VM, VM, VM
         ├─→ Hyper-V Host 02 (VMM Agent)
         │     └─→ VM, VM
         └─→ Hyper-V Host 03 (VMM Agent)
               └─→ VM, VM, VM
```

### 통신 포트

Microsoft Learn 공식 문서(Identify VMM ports and protocols) 기준입니다.

| 포트        | 방향                                                | 용도                      |
|-------------|-----------------------------------------------------|---------------------------|
| 8100        | 콘솔 → VMM 서버                                     | HTTP (WCF)                |
| 8101        | 콘솔 → VMM 서버                                     | HTTPS (WCF)               |
| 8102        | 콘솔 → VMM 서버                                     | Net.TCP (WCF)             |
| 80          | VMM 서버 → VMM Agent                                | WinRM                     |
| 135         | VMM 서버 → VMM Agent                                | RPC                       |
| 139         | VMM 서버 → VMM Agent                                | NetBIOS                   |
| 445         | VMM 서버 → VMM Agent                                | SMB (TCP)                 |
| 443         | VMM 서버 → VMM Agent                                | HTTPS, BITS 데이터 채널   |
| 5985        | VMM 서버 → VMM Agent                                | WinRM 제어 채널           |
| 5986        | VMM 서버 → VMM Agent                                | WinRM SSL 제어 채널       |
| 1433        | VMM 서버 → 원격 SQL Server                          | TDS (SQL Server listener) |
| 22          | VMM 서버 → VMware ESXi                              | SFTP                      |
| 443         | VMM 서버 → VMware ESXi                              | HTTPS                     |
| 443         | VMM 서버 → BMC (베어메탈)                           | SMASH over WS-Management  |
| 623         | VMM 서버 → BMC (베어메탈)                           | IPMI                      |
| 8102        | VMM 서버 → WDS PXE provider                         | WCF                       |
| 8101        | VMM 서버 → Windows PE agent                         | WCF 제어 채널             |
| 8103        | VMM 서버 → Windows PE agent                         | WCF, time sync            |
| 49152~65535 | VMM 서버 ↔ Hyper-V 호스트/파일 서버/라이브러리 서버 | 동적 포트 범위            |

🟡 같은 포트(443, 8101, 8102)가 통신 상대에 따라 다른 용도로 재사용됩니다. 방화벽 규칙은 통신 방향(콘솔·서버·Agent·SQL·BMC)별로 구분해서 적용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설치

### 사전 요구사항

| 항목        | 요구사항                                                                   |
|-------------|----------------------------------------------------------------------------|
| OS          | Windows Server 2019 / 2022                                                 |
| CPU         | 4코어 이상                                                                 |
| RAM         | VMM 서버 최소 4GB, 권장 16GB / SQL Server 별도 서버 시 최소 8GB, 권장 16GB |
| 디스크      | 최소 80GB                                                                  |
| 컴퓨터 이름 | 15자 이하 (NetBIOS 제한, 초과 시 설치 실패)                                |
| SQL Server  | VMM 2022: 2016/2017/2019/2022 지원 / VMM 2025: 2019/2022/2025 지원         |
| Windows ADK | 베어메탈 배포 기능 사용 시 필요                                            |
| 도메인      | Active Directory 도메인 가입 필수                                          |
| 서비스 계정 | 도메인 계정 필요 (로컬 계정 불가)                                          |

### 설치 순서

```
1. Active Directory 도메인 구성
        │
        v
2. SQL Server 설치
        │
        v
3. Windows ADK 설치
        │
        v
4. 서비스 계정 생성 (AD)
        │
        v
5. SCVMM 서버 설치
        │
        v
6. SCVMM 콘솔 설치 (관리자 PC)
        │
        v
7. Hyper-V 호스트 등록
```

### 1단계: SQL Server 준비

```powershell
# SQL Server 설치 후 방화벽 포트 허용
New-NetFirewallRule `
    -DisplayName "SQL Server" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 1433 `
    -Action Allow

# SQL Server Browser — named instance 사용 시에만 필요
# 기본 인스턴스(MSSQLSERVER) 사용 시 고정 포트 1433을 직접 사용하므로 생략 가능
# Set-Service -Name SQLBrowser -StartupType Automatic
# Start-Service SQLBrowser
```

### 2단계: Windows ADK 설치

```powershell
# ADK 다운로드 후 무인 설치
.\adksetup.exe /features OptionId.DeploymentTools `
               OptionId.WindowsPreinstallationEnvironment `
               /quiet /norestart
```

### 3단계: 서비스 계정 생성

```powershell
# 도메인 컨트롤러에서 실행
Import-Module ActiveDirectory

New-ADUser `
    -Name "svc-scvmm" `
    -SamAccountName "svc-scvmm" `
    -AccountPassword (ConvertTo-SecureString "SecurePassword123" -AsPlainText -Force) `
    -PasswordNeverExpires $true `
    -Enabled $true

# SCVMM 서버 로컬 관리자 그룹에 추가
Add-LocalGroupMember -Group "Administrators" -Member "DOMAIN\svc-scvmm"
```

### 4단계: SCVMM 서버 무인 설치

응답 파일 `VMMConfig.ini` 생성 후 설치합니다.

```ini
[OPTIONS]
CompanyName=MyCompany
CreateNewSqlDatabase=1
SqlInstanceName=MSSQLSERVER
SqlServerName=sql-server.example.com
SqlDatabaseName=VirtualManagerDB
IndigoTcpPort=8100
IndigoHTTPSPort=8101
IndigoNETTCPPort=8102
IndigoHTTPPort=8103
WSManTcpPort=5985
BitsTcpPort=443
VmmServiceLocalAccount=0
UserName=DOMAIN\svc-scvmm
Password=SecurePassword123
VmmServerName=scvmm-server.example.com
ProgramFiles=C:\Program Files\Microsoft System Center\Virtual Machine Manager
```

```powershell
# 무인 설치 실행
.\setup.exe /server /i /f VMMConfig.ini `
    /IACCEPTSCEULA `
    /VmmServiceAccount DOMAIN\svc-scvmm `
    /VmmServiceAccountPassword SecurePassword123
```

### 5단계: 콘솔 설치 (관리자 PC)

```powershell
# 콘솔만 설치
.\setup.exe /console /i /IACCEPTSCEULA
```

### 6단계: 방화벽 규칙 일괄 등록

```powershell
$ports = @(8100, 8101, 8102, 8103, 443, 5985, 5986)
foreach ($port in $ports) {
    New-NetFirewallRule `
        -DisplayName "SCVMM Port $port" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort $port `
        -Action Allow
}
```

### 설치 확인

```powershell
# SCVMM 서비스 상태 확인
Get-Service -Name SCVMMService

# SCVMM 서버 연결 테스트
Get-SCVMMServer -ComputerName "scvmm-server.example.com"
```

🟡 도메인 가입과 SQL Server 준비가 선행되지 않으면 설치가 실패합니다. 순서를 반드시 지킵니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Hyper-V 호스트 관리

### 호스트 등록

```powershell
Import-Module VirtualMachineManager

# SCVMM 서버 연결
$vmmServer = Get-SCVMMServer -ComputerName "scvmm-server.example.com"

# 자격증명 설정
$credential = Get-SCRunAsAccount -Name "HyperV-Admin"

# Hyper-V 호스트 추가
Add-SCVMHost `
    -ComputerName "hyperv-host01.example.com" `
    -Credential $credential `
    -VMHostGroup "All Hosts"

# 호스트 전체 목록 확인
Get-SCVMHost | Select-Object Name, OperatingSystem, CPUCount, MemoryAvailableMB
```

### 베어메탈 물리 서버 배포

빈 물리 서버에 OS를 배포하고 Hyper-V 호스트로 자동 등록합니다.

```
Empty physical server
  │
  └─→ SCVMM PXE boot
        │
        ├─→ OS image deploy (Windows Server 2022)
        ├─→ Hyper-V role auto install
        ├─→ Network config
        └─→ Register as Hyper-V host
```

```powershell
# 베어메탈 서버를 Hyper-V 호스트로 프로비저닝
$physicalMachine = Get-SCPhysicalComputerProfile -Name "HyperV-Profile"

New-SCVMHost `
    -PhysicalComputerProfile $physicalMachine `
    -BMCAddress "192.0.2.100" `
    -BMCRunAsAccount $credential
```

### 라이브 마이그레이션

서비스 중단 없이 VM을 다른 호스트로 이동합니다.

```powershell
# VM을 다른 호스트로 이동
Move-SCVirtualMachine `
    -VM "web-server-01" `
    -VMHost (Get-SCVMHost -ComputerName "hyperv-host02.example.com")
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. VM 관리

### 템플릿 기반 VM 생성

```powershell
# 템플릿 및 호스트 조회
$template = Get-SCVMTemplate -Name "WS2022-Template"
$vmhost   = Get-SCVMHost -ComputerName "hyperv-host01.example.com"

# VM 생성
New-SCVirtualMachine `
    -Name "web-server-01" `
    -VMTemplate $template `
    -VMHost $vmhost `
    -Path "C:\VMs"

# VM 시작
Start-SCVirtualMachine -VM "web-server-01"
```

### VM 기본 관리

```powershell
# VM 전체 목록
Get-SCVirtualMachine | Select-Object Name, Status, HostName

# VM 시작/중지/재시작
Start-SCVirtualMachine   -VM "web-server-01"
Stop-SCVirtualMachine    -VM "web-server-01"
Restart-SCVirtualMachine -VM "web-server-01"

# VM 삭제
Remove-SCVirtualMachine -VM "web-server-01"

# VM 스냅샷 생성
New-SCVMCheckpoint -VM "web-server-01" -Name "before-patch"

# 스냅샷 복원
Restore-SCVMCheckpoint -VMCheckpoint (
    Get-SCVMCheckpoint -VM "web-server-01" -Name "before-patch"
)
```

### VMware 연동 (제한적)

```powershell
# VMware vCenter 연결
Add-SCVMHost `
    -ComputerName "vcenter.example.com" `
    -VirtualizationManager `
    -TCPPort 443

# VMware VM 조회
Get-SCVirtualMachine | Where-Object { $_.HostType -eq "VMware" }
```

| 기능                 | Hyper-V | VMware ESXi |
|----------------------|---------|-------------|
| VM 생성/삭제         | ✅      | ❌          |
| VM 시작/중지         | ✅      | ✅          |
| 라이브 마이그레이션  | ✅      | 🟡 제한적   |
| 모니터링             | ✅      | ✅          |
| V2V 변환 (VMware→HV) | ✅      | -           |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 네트워크 및 스토리지

### 가상 네트워크 관리

```powershell
# 논리 네트워크 생성
New-SCLogicalNetwork -Name "Production-Network"

# VM 네트워크 생성
New-SCVMNetwork `
    -Name "VM-Production" `
    -LogicalNetwork (Get-SCLogicalNetwork -Name "Production-Network")

# 가상 스위치 생성
New-SCVirtualNetwork `
    -Name "ExternalSwitch" `
    -VMHost (Get-SCVMHost -ComputerName "hyperv-host01.example.com") `
    -NetworkAdapterName "Ethernet"
```

### 스토리지 관리

```powershell
# 스토리지 공급자 등록 (iSCSI/FC SAN)
Add-SCStorageProvider `
    -Name "SAN-Storage" `
    -URI "https://san-storage.example.com:5989/cimom"

# 스토리지 풀 조회
Get-SCStoragePool

# 논리 디스크 생성
New-SCStorageLogicalUnit `
    -StoragePool (Get-SCStoragePool -Name "Pool-01") `
    -Name "LUN-web-01" `
    -Size 100GB
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 자동화

### PowerShell 기본 패턴

```powershell
# SCVMM 모듈 로드 및 연결
Import-Module VirtualMachineManager
$vmmServer = Get-SCVMMServer -ComputerName "scvmm-server.example.com"

# VM 일괄 생성 예시
$hosts    = Get-SCVMHost | Where-Object { $_.MemoryAvailableMB -gt 4096 }
$template = Get-SCVMTemplate -Name "WS2022-Template"

foreach ($host in $hosts) {
    $vmName = "auto-vm-$($host.Name)"
    New-SCVirtualMachine `
        -Name $vmName `
        -VMTemplate $template `
        -VMHost $host `
        -Path "C:\VMs"
    Write-Output "Created: $vmName on $($host.Name)"
}
```

### Ansible WinRM 연동

SCVMM 없이 Ansible로 Hyper-V를 직접 관리하는 패턴입니다.

```yaml
# inventory.ini
[hyperv_hosts]
hyperv-host01.example.com
hyperv-host02.example.com

[hyperv_hosts:vars]
ansible_connection=winrm
ansible_winrm_transport=ntlm
ansible_port=5985
```

```yaml
# playbook: create_vm.yml
- name: Hyper-V VM 생성
  hosts: hyperv_hosts
  tasks:
    - name: VM 생성
      community.windows.win_hyperv_vm:
        name: web-server-01
        memory_mb: 2048
        cpu_count: 2
        state: present
```

### Terraform Hyper-V provider

```hcl
terraform {
  required_providers {
    hyperv = {
      source  = "taliesins/hyperv"
      version = "1.0.4"
    }
  }
}

resource "hyperv_machine_instance" "web_server" {
  name               = "web-server-01"
  generation         = 2
  processor_count    = 2
  dynamic_memory     = true
  memory_startup_mb  = 2048
  memory_maximum_mb  = 4096

  network_adaptors {
    name        = "eth0"
    switch_name = "ExternalSwitch"
  }

  hard_disk_drives {
    path = "C:\\VMs\\web-server-01\\disk.vhdx"
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 모니터링

### 기본 상태 확인

```powershell
# 호스트 리소스 현황
Get-SCVMHost | Select-Object Name, CPUUtilization, MemoryAvailableMB, OverallState

# VM 상태 전체 조회
Get-SCVirtualMachine | Select-Object Name, Status, HostName, CPUCount, Memory

# 비정상 VM 필터링
Get-SCVirtualMachine | Where-Object { $_.Status -ne "Running" }

# 호스트별 VM 수
Get-SCVMHost | ForEach-Object {
    $vmCount = (Get-SCVirtualMachine -VMHost $_).Count
    [PSCustomObject]@{
        Host    = $_.Name
        VMCount = $vmCount
        MemFree = "$($_.MemoryAvailableMB) MB"
    }
}
```

### SCOM 연동

```
SCVMM + SCOM 조합
  SCVMM → 프로비저닝/관리
  SCOM  → 성능 모니터링/알림
```

```powershell
# SCOM 연결 구성
Set-SCOMManagementServer `
    -ManagementServerName "scom-server.example.com"
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 타 도구 비교

### SCVMM vs vCenter vs Proxmox

| 항목          | SCVMM                         | vCenter (VMware)         | Proxmox         |
|---------------|-------------------------------|--------------------------|-----------------|
| 하이퍼바이저  | Hyper-V 전용 (ESXi 제한 지원) | ESXi 전용                | KVM/LXC         |
| 비용          | 유료 (System Center 라이선스) | 유료 (고가)              | 무료 (커뮤니티) |
| 주요 고객     | Microsoft 엔터프라이즈        | 대기업 표준              | 중소기업/학습   |
| GUI           | Windows 콘솔                  | 웹 UI                    | 웹 UI           |
| 자동화        | PowerShell / REST API         | PowerCLI / REST API      | API / Terraform |
| 베어메탈 배포 | ✅                            | ✅ (vSphere Auto Deploy) | 🟡 제한적       |
| SDN 관리      | ✅                            | ✅ (NSX)                 | 🟡 제한적       |

### SCVMM vs Kubernetes

| 항목          | SCVMM                | Kubernetes              |
|---------------|----------------------|-------------------------|
| 관리 대상     | VM (가상 머신)       | 컨테이너                |
| 워크로드      | 레거시 앱, MSSQL, AD | 마이크로서비스, 신규 앱 |
| 자동 스케일링 | 🟡 제한적            | ✅                      |
| 자동 복구     | 🟡 클러스터링 별도   | ✅ Self-healing         |
| 현업 추세     | 레거시 유지          | 신규 프로젝트 표준      |

> 현업 대기업/금융 환경은 **SCVMM으로 레거시 VM 유지 + Kubernetes로 신규 서비스 도입**하는 혼용 구조가 일반적입니다.

### Azure Arc 확장

온프레미스 SCVMM을 Azure 포털에서 관리할 수 있습니다.

```
SCVMM + Azure Arc
  │
  ├─→ On-premises Hyper-V VM → Azure portal management
  ├─→ Azure Policy apply
  └─→ Azure Monitor integration
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Microsoft Docs: [docs.microsoft.com/system-center/vmm](https://docs.microsoft.com/en-us/system-center/vmm/) — ★★★☆☆
- Microsoft Evaluation Center: [microsoft.com/evalcenter](https://www.microsoft.com/en-us/evalcenter/evaluate-system-center) — ★★☆☆☆
- [windows_server_key_concepts.md](./windows_server_key_concepts.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-21

**마지막 업데이트**: 2026-08-21

© 2026 siasia86. Licensed under CC BY 4.0.
