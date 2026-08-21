---
name: scvmm-official-notes
description: SCVMM(System Center Virtual Machine Manager) 공식 문서 참조 노트. 아키텍처, 설치 요구사항, Hyper-V 호스트 관리, VMware 연동, 베어메탈 배포, PowerShell 자동화, Azure Arc 연동 정리.
tags:
  - scvmm
  - system-center
  - hyper-v
  - windows-server
  - virtualization
  - powershell
last_checked: 2026-08-21
sources:
  - https://learn.microsoft.com/en-us/system-center/vmm/overview
  - https://learn.microsoft.com/en-us/system-center/vmm/install
  - https://learn.microsoft.com/en-us/system-center/vmm/hyper-v-existing
  - https://learn.microsoft.com/en-us/system-center/vmm/vm-template
  - https://learn.microsoft.com/en-us/system-center/vmm/network-sdn
  - https://learn.microsoft.com/en-us/system-center/vmm/about-arc-enabled-system-center-virtual-machine-manager
  - https://learn.microsoft.com/en-us/system-center/vmm/plan-ports-protocols
---

# SCVMM 공식 문서 참조 노트

## 1. 제품 정의

- SCVMM은 Microsoft System Center 제품군의 인프라 관리 컴포넌트입니다.
- Hyper-V 호스트, 물리 서버(Bare Metal), 스토리지(SAN/NAS), 가상 네트워크(SDN)를 단일 콘솔에서 통합 관리합니다.
- VMware ESXi는 제한적으로 지원합니다 (VM 조회, 시작/중지, V2V 마이그레이션).
- KVM, Proxmox, Docker, Kubernetes는 지원하지 않습니다.

## 2. 설치 사전 요구사항

- OS: Windows Server 2019 / 2022
- RAM: VMM 서버 최소 4GB 권장 16GB / SQL Server 별도 서버 최소 8GB 권장 16GB
- 컴퓨터 이름: 15자 이하 (NetBIOS 제한, 초과 시 설치 실패)
- SQL Server: VMM 2022는 2016/2017/2019/2022 지원, VMM 2025는 2019/2022/2025 지원 (설치 전 구성 필수)
- Active Directory 도메인 가입 필수 (워크그룹 환경 불가)
- 서비스 계정: 도메인 계정 필요 (로컬 계정 불가)
- Windows ADK: 베어메탈 배포 기능 사용 시 필요

## 3. 구성 요소

- SCVMM Server: 핵심 관리 서버
- SCVMM Console: 관리자 GUI (별도 PC에 설치 가능)
- SCVMM DB (SQL Server): 클러스터 상태 및 구성 저장
- VMM Agent: 각 Hyper-V 호스트에 설치되는 에이전트

## 4. 주요 통신 포트

공식 문서(plan-ports-protocols) 기준 통신 방향과 포트입니다.

- 콘솔 → VMM 서버: 8100(HTTP, WCF) / 8101(HTTPS, WCF) / 8102(Net.TCP, WCF)
- VMM 서버 → VMM Agent (Windows 호스트/원격 라이브러리 서버): 80(WinRM) / 135(RPC) / 139(NetBIOS) / 445(SMB over TCP)
- VMM 서버 → VMM Agent: 443(HTTPS, BITS 데이터 채널)
- VMM 서버 → VMM Agent: 5985(WinRM 제어 채널) / 5986(WinRM SSL 제어 채널)
- VMM 서버 → 원격 SQL Server: 1433(TDS, SQL Server listener)
- VMM 서버 → VMware ESXi: 22(SFTP) / 443(HTTPS)
- VMM 서버 → BMC(베어메탈 배포): 443(SMASH over WS-Management) / 623(IPMI)
- VMM 서버 → WDS PXE provider: 8102(WCF)
- VMM 서버 → Windows PE agent: 8101(WCF 제어 채널) / 8103(WCF, time sync)
- 동적 포트 범위 49152~65535: Hyper-V 호스트·파일 서버·라이브러리 서버 통신에 필요

## 5. 베어메탈 배포

- PXE 부팅을 통해 빈 물리 서버에 OS를 자동 배포합니다.
- `New-SCVMHost` + `PhysicalComputerProfile` 조합으로 프로비저닝합니다.
- 배포 완료 후 Hyper-V 호스트로 자동 등록됩니다.

## 6. SQL Server Browser 주의사항

- SQL Server Browser는 named instance 사용 시에만 필요합니다.
- 기본 인스턴스(MSSQLSERVER)는 고정 포트 1433을 사용하므로 Browser 서비스가 필요하지 않습니다.
- VMMConfig.ini에서 `SqlInstanceName=MSSQLSERVER` 사용 시 Browser 서비스 시작 단계를 생략할 수 있습니다.

## 7. PowerShell 자동화

- `Import-Module VirtualMachineManager` 로 모듈 로드합니다.
- `Get-SCVMMServer` 로 SCVMM 서버에 연결합니다.
- VM 생성: `New-SCVirtualMachine -VMTemplate ... -VMHost ...`
- 라이브 마이그레이션: `Move-SCVirtualMachine -VM ... -VMHost ...`
- 호스트 등록: `Add-SCVMHost -ComputerName ... -Credential ...`

## 8. VMware 연동 제한

- `Add-SCVMHost -VirtualizationManager` 로 vCenter를 등록할 수 있습니다.
- VMware VM 생성/삭제는 불가합니다.
- VM 시작/중지, 모니터링, V2V 변환(VMware → Hyper-V)은 가능합니다.
- 라이브 마이그레이션은 제한적으로 지원합니다.

## 9. Azure Arc 연동

- SCVMM + Azure Arc 연동 시 온프레미스 Hyper-V VM을 Azure 포털에서 관리할 수 있습니다.
- Azure Policy, Azure Monitor 적용이 가능합니다.
- Azure Arc for SCVMM은 별도 Arc 에이전트 설치가 필요합니다.

## 10. System Center 제품군 관계

- SCVMM: VM/인프라 관리
- SCOM (Operations Manager): 성능 모니터링/알림 — SCVMM과 연동하여 사용합니다.
- SCCM (Configuration Manager): 엔드포인트 관리
- DPM (Data Protection Manager): 백업/복구
- SCO (Orchestrator): 워크플로 자동화

## 11. 현업 적용 범위

- 금융/제조/공공 등 레거시 엔터프라이즈 환경의 Hyper-V 클러스터 중앙 관리에 사용합니다.
- 신규 프로젝트는 Kubernetes(EKS/AKS)로 전환하는 추세이며, SCVMM은 레거시 VM 유지 목적으로 운영됩니다.
- Terraform (taliesins/hyperv provider), Ansible (WinRM) 연동으로 IaC 자동화가 가능합니다.
