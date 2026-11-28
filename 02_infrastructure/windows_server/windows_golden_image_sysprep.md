# Windows 골든 이미지 — Packer·Hyper-V·sysprep

Windows 11을 Hyper-V Generation 2 VM에 무인 설치하고, 공통 설정을 넣은 뒤 sysprep로 일반화해 여러 VM에 나눠 쓸 VHDX를 만드는 과정을 정리했습니다. 개념은 [sysprep 참조 노트](../../_reference/windows_sysprep_official_notes.md)와 [무인 설치 응답 파일 참조 노트](../../_reference/windows_unattend_answer_file_official_notes.md)에 출처와 함께 두었습니다.

- 기준: Windows 11(Pro 등 클라이언트판), Packer 1.16.x, `hashicorp/hyperv` 플러그인 v1.1.5, Windows PowerShell 5.1 또는 PowerShell 7
- 예제 시험: Windows·Hyper-V 실행은 미실행. Linux에서 HCL은 `packer fmt -check`·`packer validate -syntax-only`(1.16.3)로, 응답 파일 XML은 형식(well-formed)만, PowerShell 예제는 컨테이너 안 pwsh 7.4로 구문만 검사했습니다(2026-11-28)
- 예제의 이름·크기·언어는 자리표나 예시 값입니다. 환경에 맞게 바꿉니다

## 목차

| 섹션                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 준비](#2-준비) / [3. 응답 파일 두 개](#3-응답-파일-두-개)                                           |
| [4. Packer 템플릿](#4-packer-템플릿) / [5. provisioner](#5-provisioner) / [6. 비밀번호가 머무는 곳](#6-비밀번호가-머무는-곳) |
| [7. 결과물 다루기](#7-결과물-다루기) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                                   |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                                            |

---

## 1. 개요

골든 이미지는 OS 설치와 공통 설정을 미리 끝내 둔 기준 디스크입니다. 그대로 복사하면 컴퓨터 SID 같은 고유 정보까지 같아지므로, 배포 전에 `sysprep /generalize`로 고유 정보를 지우고 다음 부팅에서 새로 만들게 합니다. Microsoft는 일반화하지 않은 이미지를 다른 컴퓨터로 옮기는 것을 지원하지 않습니다.

```
 Packer 빌드 (hyperv-iso)
 ├── 1. Gen2 VM 생성, 설치 ISO + 응답 파일 ISO(두 번째 DVD)
 ├── 2. boot_command로 "Press any key to boot from CD or DVD" 넘김
 ├── 3. Windows 설치 (autounattend.xml: windowsPE → oobeSystem)
 ├── 4. 첫 로그온 명령으로 WinRM 켬 → Packer 접속
 ├── 5. provisioner: 공통 설정, sysprep 준비
 └── 6. shutdown_command: sysprep /generalize /oobe /shutdown
          │
          ▼
 일반화된 VHDX (켜기 전 사본 보관)
          │
          ▼  배포한 VM의 첫 부팅
 specialize(새 SID) → oobeSystem(unattend.xml) → 첫 로그온 가능
```

| 단계              | 응답 파일                           | 주로 하는 일                              |
|-------------------|-------------------------------------|-------------------------------------------|
| 설치              | `autounattend.xml`(미디어에서 찾음) | 언어, 디스크 분할, 에디션 선택, 빌드 계정 |
| 일반화 뒤 첫 부팅 | `unattend.xml`(sysprep `/unattend`) | OOBE 화면 넘기기, 배포용 계정, 시간대     |

## 2. 준비

| 항목               | 확인 방법                                                                           |
|--------------------|-------------------------------------------------------------------------------------|
| Hyper-V            | 호스트에서 켜져 있고 관리자 권한으로 실행. 설치는 [Hyper-V](./hyper_v.md) 3절       |
| Windows 11 VM 조건 | Generation 2, 보안 부팅, vTPM, 가상 CPU 2개 이상, 메모리 4GB 이상, 디스크 64GB 이상 |
| Packer·플러그인    | `packer version`, 템플릿의 `required_plugins`로 `packer init`                       |
| ISO 체크섬         | `Get-FileHash <ISO> -Algorithm SHA256`                                              |
| 에디션 번호        | ISO를 붙인 뒤 `dism /Get-ImageInfo /ImageFile:<드라이브>:\sources\install.wim`      |
| 응답 파일 ISO      | 아래 표 중 하나                                                                     |

에디션 번호(`/IMAGE/INDEX`)는 ISO마다 순서가 다르므로 매번 dism으로 확인합니다.

Gen2 VM에는 플로피가 없어 응답 파일을 ISO로 붙입니다.

| 방법                                   | 필요한 것                                                   | 비고                                                                        |
|----------------------------------------|-------------------------------------------------------------|-----------------------------------------------------------------------------|
| Packer `cd_files`                      | 호스트에 `oscdimg`(Windows ADK)·`xorriso`·`mkisofs` 중 하나 | Packer가 ISO를 만들어 붙임                                                  |
| 미리 만든 ISO + `secondary_iso_images` | Windows 내장 IMAPI2 COM(PowerShell로 호출)                  | 추가 설치 없음. 자리표를 바꾼 사본으로 만들고 빌드 뒤 지움                  |
| Linux에서 만들기                       | `genisoimage`·`xorriso`                                     | `genisoimage -o answer.iso -V UNATTEND -J -r autounattend.xml unattend.xml` |

## 3. 응답 파일 두 개

예제는 필요한 요소만 남긴 것입니다. `__ADMIN_PASSWORD__`, `__IMAGE_INDEX__`, `__LOCAL_USER__`는 자리표이며, 저장소에는 자리표만 두고 빌드할 때 임시 사본에서 바꿉니다. 비밀번호를 넣을 때는 XML 특수 문자(`&`, `<`, `>` 등)를 바꿔 넣어야 합니다.

### 3-1. 설치 단계 `autounattend.xml`

설치 프로그램은 각 구성 패스 시작 때 이동식 미디어 루트의 `Autounattend.xml`을 드라이브 문자 순서로 찾습니다. 두 번째 DVD도 이 규칙으로 찾는 것으로 보지만, 문서에 따로 적혀 있지는 않습니다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
  <settings pass="windowsPE">
    <component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <SetupUILanguage><UILanguage>ko-KR</UILanguage></SetupUILanguage>
      <InputLocale>0412:00000412</InputLocale>
      <SystemLocale>ko-KR</SystemLocale>
      <UILanguage>ko-KR</UILanguage>
      <UserLocale>ko-KR</UserLocale>
    </component>
    <component name="Microsoft-Windows-Setup" processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
               xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <DiskConfiguration>
        <Disk wcm:action="add">
          <DiskID>0</DiskID>
          <WillWipeDisk>true</WillWipeDisk>
          <CreatePartitions>
            <CreatePartition wcm:action="add"><Order>1</Order><Type>EFI</Type><Size>100</Size></CreatePartition>
            <CreatePartition wcm:action="add"><Order>2</Order><Type>MSR</Type><Size>16</Size></CreatePartition>
            <CreatePartition wcm:action="add"><Order>3</Order><Type>Primary</Type><Extend>true</Extend></CreatePartition>
          </CreatePartitions>
          <ModifyPartitions>
            <ModifyPartition wcm:action="add"><Order>1</Order><PartitionID>1</PartitionID><Format>FAT32</Format></ModifyPartition>
            <ModifyPartition wcm:action="add"><Order>2</Order><PartitionID>3</PartitionID><Format>NTFS</Format></ModifyPartition>
          </ModifyPartitions>
        </Disk>
      </DiskConfiguration>
      <ImageInstall>
        <OSImage>
          <InstallTo><DiskID>0</DiskID><PartitionID>3</PartitionID></InstallTo>
          <InstallFrom>
            <MetaData wcm:action="add"><Key>/IMAGE/INDEX</Key><Value>__IMAGE_INDEX__</Value></MetaData>
          </InstallFrom>
        </OSImage>
      </ImageInstall>
      <UserData>
        <AcceptEula>true</AcceptEula>
      </UserData>
    </component>
  </settings>
  <settings pass="oobeSystem">
    <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
               xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <OOBE>
        <HideEULAPage>true</HideEULAPage>
        <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
        <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
        <ProtectYourPC>3</ProtectYourPC>
      </OOBE>
      <UserAccounts>
        <AdministratorPassword><Value>__ADMIN_PASSWORD__</Value><PlainText>true</PlainText></AdministratorPassword>
      </UserAccounts>
      <AutoLogon>
        <Password><Value>__ADMIN_PASSWORD__</Value><PlainText>true</PlainText></Password>
        <Username>Administrator</Username>
        <Enabled>true</Enabled>
        <LogonCount>1</LogonCount>
      </AutoLogon>
      <FirstLogonCommands>
        <SynchronousCommand wcm:action="add">
          <Order>1</Order>
          <CommandLine>powershell -NoProfile -Command "Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private"</CommandLine>
        </SynchronousCommand>
        <SynchronousCommand wcm:action="add">
          <Order>2</Order>
          <CommandLine>cmd /c winrm quickconfig -q -force</CommandLine>
        </SynchronousCommand>
        <SynchronousCommand wcm:action="add">
          <Order>3</Order>
          <CommandLine>powershell -NoProfile -Command "Set-Item WSMan:\localhost\Service\Auth\Basic $true; Set-Item WSMan:\localhost\Service\AllowUnencrypted $true"</CommandLine>
        </SynchronousCommand>
      </FirstLogonCommands>
    </component>
  </settings>
</unattend>
```

| 요소                                 | 이유                                                                                                         |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------|
| `DiskConfiguration`                  | Gen2(UEFI)는 GPT: EFI(FAT32) → MSR → Windows(NTFS)                                                           |
| `/IMAGE/INDEX`                       | 다중 에디션 ISO에서 설치할 에디션 선택. 제품 키가 없을 때 키·에디션 화면이 뜨는지는 미확인이므로 콘솔로 확인 |
| `ProductKey`를 넣지 않음             | 넣으려면 `Key`에 25자 키가 있어야 함(빈 값 금지). 키 없이 `WillShowUI`만 두면 설치가 오류로 멈춘 사례가 있음 |
| `AutoLogon` `Username`=Administrator | 클라이언트판은 기본 Administrator가 꺼져 있음. 이 설정이 계정을 켬. `LogonCount`는 필수                      |
| 네트워크를 개인 프로필로             | 공용 프로필이면 `winrm quickconfig`가 방화벽 예외를 만들지 못해 실패함                                       |
| Basic·암호화 없음                    | 호스트 안 NAT 스위치에서만 접속하는 빌드용 설정. 일반화 전에 되돌리거나 HTTPS(5986)를 씀                     |

### 3-2. 일반화 뒤 첫 부팅 `unattend.xml`

sysprep `/unattend:`로 넘기는 파일입니다. 배포한 VM의 OOBE 화면을 넘기고 쓸 계정을 만듭니다. AutoLogon을 설정하면 OOBE의 사용자 계정 만들기 단계를 건너뜁니다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
  <settings pass="oobeSystem">
    <component name="Microsoft-Windows-International-Core" processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <InputLocale>0412:00000412</InputLocale>
      <SystemLocale>ko-KR</SystemLocale>
      <UILanguage>ko-KR</UILanguage>
      <UserLocale>ko-KR</UserLocale>
    </component>
    <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
               xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <TimeZone>Korea Standard Time</TimeZone>
      <OOBE>
        <HideEULAPage>true</HideEULAPage>
        <HideLocalAccountScreen>true</HideLocalAccountScreen>
        <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
        <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
        <ProtectYourPC>3</ProtectYourPC>
      </OOBE>
      <UserAccounts>
        <LocalAccounts>
          <LocalAccount wcm:action="add">
            <Name>__LOCAL_USER__</Name>
            <Group>Administrators</Group>
            <Password><Value>__ADMIN_PASSWORD__</Value><PlainText>true</PlainText></Password>
          </LocalAccount>
        </LocalAccounts>
      </UserAccounts>
    </component>
  </settings>
</unattend>
```

- 인터넷이 연결된 상태로 첫 부팅하면 OOBE가 "업데이트 확인 중" 단계를 거치며, 위 화면 숨김 설정으로는 꺼지지 않고 업데이트 뒤 다시 시작할 수 있다는 사례가 보고되었습니다([보고]). 첫 부팅 시간을 예측해야 하면 네트워크 연결 시점을 함께 정합니다.
- `HideLocalAccountScreen`을 켜면 계정 만들기 화면이 사라지므로, `LocalAccounts`나 `AdministratorPassword` 중 하나로 로그온할 계정을 반드시 만듭니다.
- 배포 VM마다 비밀번호를 다르게 하려면 이 파일에 비밀번호를 넣지 말고, 배포 단계에서 VM별 응답 파일을 따로 넣는 방식을 검토합니다.

## 4. Packer 템플릿

```hcl
packer {
  required_plugins {
    hyperv = {
      source  = "github.com/hashicorp/hyperv"
      version = ">= 1.1.5, < 2.0.0"
    }
  }
}

variable "iso_path" { type = string }
variable "iso_checksum" { type = string }
variable "answer_iso" { type = string }
variable "temp_path" { type = string }
variable "output_dir" { type = string }

variable "admin_password" {
  type      = string
  sensitive = true
}

source "hyperv-iso" "win11" {
  iso_url      = var.iso_path
  iso_checksum = var.iso_checksum

  vm_name               = "packer-win11"
  generation            = 2
  cpus                  = 2
  memory                = 8192
  enable_dynamic_memory = false
  disk_size             = 81920
  switch_name           = "Default Switch"
  enable_secure_boot    = true
  secure_boot_template  = "MicrosoftWindows"
  enable_tpm            = true

  secondary_iso_images = [var.answer_iso]

  boot_wait    = "1s"
  boot_command = ["<spacebar><wait><spacebar><wait><spacebar><wait><spacebar><wait><spacebar>"]

  headless         = true
  temp_path        = var.temp_path
  output_directory = var.output_dir
  skip_export      = true
  keep_registered  = true

  communicator   = "winrm"
  winrm_username = "Administrator"
  winrm_password = var.admin_password
  winrm_timeout  = "90m"

  shutdown_command = "C:\\Windows\\System32\\Sysprep\\sysprep.exe /generalize /oobe /shutdown /quiet /unattend:C:\\Windows\\System32\\Sysprep\\unattend.xml"
  shutdown_timeout = "30m"
}

build {
  sources = ["source.hyperv-iso.win11"]

  provisioner "powershell" {
    script = "scripts/configure-base.ps1"
  }

  provisioner "powershell" {
    script = "scripts/prepare-sysprep.ps1"
  }
}
```

| 옵션                              | 설명                                                                                    |
|-----------------------------------|-----------------------------------------------------------------------------------------|
| `enable_secure_boot`·`enable_tpm` | 플러그인 기본값은 둘 다 `false`. Windows 11에는 켜야 함(`enable_tpm`은 v1.1.1에서 추가) |
| `secure_boot_template`            | Windows는 `MicrosoftWindows`, Linux는 `MicrosoftUEFICertificateAuthority`               |
| `secondary_iso_images`            | 부팅 때 붙일 ISO 목록. Gen2의 플로피 대신 응답 파일 전달에 씀                           |
| `temp_path`                       | 빌드 VM 파일 위치. 기본 `%TEMP%`(보통 시스템 드라이브)라 디스크가 큰 곳으로 지정        |
| `skip_export`                     | 내보내기를 건너뛰고 VHDX를 `<output_directory>/Virtual Hard Disks`에 둠                 |
| `keep_registered`                 | 빌드한 VM을 Hyper-V에 남김. VM 파일은 `temp_path` 아래 무작위 이름 폴더에 있음          |
| `shutdown_command`                | 비우면 Packer가 VM을 강제로 끔. sysprep는 끝나면 스스로 꺼지므로 여기에 둠              |
| `shutdown_timeout`                | 기본 5분. sysprep는 오래 걸릴 수 있어 늘림                                              |
| `winrm_timeout`                   | 기본 30분. 설치·업데이트가 길면 늘림                                                    |

### 4-1. sysprep를 WinRM으로 부를 때

위 템플릿처럼 `shutdown_command`에서 sysprep를 직접 실행하면, 일반화가 진행되는 동안 WinRM 연결이 끊겨 Packer가 명령 전송 실패(`Failed to send shutdown command`, `wsarecv` 등)로 처리하는 사례가 보고되었습니다([보고], 이 저장소에서 미재현). VM은 sysprep 뒤 스스로 꺼져도 Packer는 빌드를 실패로 보고 정리 단계에서 빌드 VM과 디스크를 지웁니다.

- `packer build -on-error=abort`는 정리하지 않고 끝내지만, 공식 문서는 `-on-error`가 "only affects the build during the provisioner run"이라고 적습니다. `shutdown_command` 단계 실패에도 적용되는지는 미확인이므로 결과물 보호 수단으로 믿지 않습니다.
- 대안: 마지막 provisioner에서 sysprep 예약 작업을 SYSTEM으로 등록하고, `shutdown_command`는 그 작업을 시작만 하고 곧바로 돌아오게 합니다. Packer는 `shutdown_timeout` 동안 VM이 꺼지기를 기다립니다. 이 방식으로 바꾼 뒤 VM이 스스로 꺼지고 Packer가 DVD 분리·디스크 압축까지 마친 빌드 사례가 보고되었습니다([보고], 이 저장소에서 미재현). 그 사례에서도 일반화 상태, sysprep 기록, OOBE 무인 통과는 따로 확인하지 않았으므로 8절 검증을 거칩니다.

```powershell
# 마지막 provisioner: sysprep 예약 작업 등록 (실행은 shutdown_command가 함)
$arg = '/generalize /oobe /shutdown /quiet /unattend:C:\Windows\System32\Sysprep\unattend.xml'
$action = New-ScheduledTaskAction -Execute 'C:\Windows\System32\Sysprep\sysprep.exe' -Argument $arg
# 트리거 없음(요청 때만 실행). 배터리 조건 때문에 시작이 막히지 않게 함
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'packer-sysprep' -Action $action -Settings $settings -User 'SYSTEM' -RunLevel Highest -Force | Out-Null
```

```hcl
shutdown_command = "schtasks /run /tn packer-sysprep"
shutdown_timeout = "30m"
```

- 예약 작업은 일반화된 이미지에 남으므로, 배포 VM 첫 부팅 정리 단계(`SetupComplete.cmd` 등)에서 `schtasks /delete /tn packer-sysprep /f`로 지우는 줄을 함께 둡니다.
- `keep_registered = true`로 VM을 남겨도 실패 정리 단계에서 디스크가 지워지면, 남은 VM이 없는 디스크를 가리킬 수 있습니다. 다시 빌드하기 전에 `Get-VMHardDiskDrive`로 경로를 확인하고 남은 VM을 정리합니다.

비밀번호는 템플릿·변수 파일에 쓰지 않고 환경 변수로 넘깁니다.

```powershell
# PowerShell 7 예. 5.1은 SecureString 변환 방법이 다름
$env:PKR_VAR_admin_password = Read-Host -AsSecureString | ConvertFrom-SecureString -AsPlainText
$env:PACKER_LOG = 1
$env:PACKER_LOG_PATH = "packer_build.log"
packer init .
packer build -var "iso_path=<ISO>" -var "iso_checksum=sha256:<값>" -var "answer_iso=<응답 파일 ISO>" `
  -var "temp_path=<작업 폴더>" -var "output_dir=<결과 폴더>" .
Remove-Item Env:\PKR_VAR_admin_password
```

## 5. provisioner

### 5-1. 공통 설정

Store 앱이 사용자별로 갱신되면 sysprep가 실패하므로, 일반화 전에 자동 내려받기를 막습니다. Microsoft는 이미지를 만드는 동안 인터넷 연결을 끊거나 자동 업데이트를 끄라고 안내합니다.

```powershell
$ErrorActionPreference = 'Stop'

# Store 앱 자동 내려받기 끄기 (2 = 끔)
$store = 'HKLM:\SOFTWARE\Policies\Microsoft\WindowsStore'
New-Item -Path $store -Force | Out-Null
Set-ItemProperty -Path $store -Name AutoDownload -Type DWord -Value 2

# 추천 앱 자동 설치(소비자 기능) 끄기
$cloud = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent'
New-Item -Path $cloud -Force | Out-Null
Set-ItemProperty -Path $cloud -Name DisableWindowsConsumerFeatures -Type DWord -Value 1
```

두 정책 값은 그룹 정책의 Store·클라우드 콘텐츠 항목에 해당합니다. 정책이 해당 에디션에서 적용되는지는 이 문서에서 확인하지 못했습니다(미확인).

### 5-2. sysprep 준비

```powershell
$ErrorActionPreference = 'Stop'
$target = 'C:\Windows\System32\Sysprep\unattend.xml'

# 1. 응답 파일 ISO에서 OOBE 응답 파일을 찾아 복사
$source = Get-CimInstance Win32_LogicalDisk -Filter 'DriveType = 5' |
    ForEach-Object { Join-Path ($_.DeviceID + '\') 'unattend.xml' } |
    Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $source) { throw 'unattend.xml not found on CD/DVD' }
Copy-Item -LiteralPath $source -Destination $target -Force

# 2. 설치 단계 응답 파일 캐시 삭제
foreach ($p in 'C:\Windows\Panther\unattend.xml', 'C:\Windows\Panther\unattend\unattend.xml') {
    if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force }
}

# 3. 첫 부팅 뒤 응답 파일을 지우는 SetupComplete.cmd
$scripts = 'C:\Windows\Setup\Scripts'
New-Item -ItemType Directory -Force -Path $scripts | Out-Null
Set-Content -LiteralPath (Join-Path $scripts 'SetupComplete.cmd') -Encoding ASCII -Value @(
    '@echo off',
    'del /f /q "C:\Windows\System32\Sysprep\unattend.xml" 2>nul',
    'del /f /q "C:\Windows\Panther\unattend.xml" 2>nul',
    'del /f /q "C:\Windows\Panther\unattend\unattend.xml" 2>nul',
    'schtasks /delete /tn packer-sysprep /f >nul 2>&1'
)

# 4. 모든 사용자용으로 준비되지 않고 사용자별로만 남은 Store 앱 제거
$provisioned = Get-AppxProvisionedPackage -Online | Select-Object -ExpandProperty DisplayName
Get-AppxPackage -AllUsers | Where-Object {
    -not $_.NonRemovable -and -not $_.IsFramework -and
    $_.SignatureKind -eq 'Store' -and $provisioned -notcontains $_.Name
} | ForEach-Object { Remove-AppxPackage -Package $_.PackageFullName -AllUsers -ErrorAction Continue }
```

- 응답 파일 ISO에 `autounattend.xml`과 `unattend.xml`을 함께 담으면, 설치 단계에서는 `Autounattend.xml`만 찾으므로 섞이지 않습니다.
- `SetupComplete.cmd`는 SYSTEM 권한으로 한 번 실행되고, 설치 프로그램은 종료 코드를 확인하지 않습니다. 결과는 `C:\Windows\Panther\UnattendGC\Setupact.log`에 남습니다.
- 위 정리 스크립트로 첫 부팅 뒤 Sysprep·Panther 응답 파일, sysprep 예약 작업, 스크립트 자신이 모두 지워진 사례가 보고되었습니다([보고], 이 저장소에서 미재현).
- 🟡 **OEM 제품 키로 정품 인증되는 경우 `SetupComplete.cmd`는 실행되지 않습니다**(Enterprise·Windows Server 제외). 이때는 응답 파일이 남으므로 첫 로그온 명령(`FirstLogonCommands`)이나 배포 뒤 관리 도구로 지우는 단계를 따로 둡니다(이 대안은 미시험).
- 4번은 [sysprep 참조 노트](../../_reference/windows_sysprep_official_notes.md) 5절의 실패 원인을 미리 없애는 단계입니다. 제거 대상이 환경마다 다르므로 처음에는 목록만 출력해 확인한 뒤 지우는 편이 안전합니다.

## 6. 비밀번호가 머무는 곳

응답 파일의 `PlainText=false`는 값을 숨길 뿐 보호 수단이 아닙니다. 그래서 비밀번호가 어디에 언제까지 남는지 정해 두고 지웁니다.

| 단계        | 남는 곳                                        | 지우는 시점                                                |
|-------------|------------------------------------------------|------------------------------------------------------------|
| 저장소      | 없음(자리표만)                                 | 해당 없음                                                  |
| 빌드 준비   | 환경 변수, 자리표를 바꾼 임시 응답 파일        | ISO를 만든 직후 임시 파일 삭제, 빌드 뒤 환경 변수 삭제     |
| 빌드 중     | 응답 파일 ISO, VM 안 `C:\Windows\Panther` 캐시 | sysprep 전 캐시 삭제, 빌드 뒤(실패해도) ISO 삭제·DVD 분리  |
| 일반화 VHDX | `C:\Windows\System32\Sysprep\unattend.xml`     | 배포 VM 첫 부팅 뒤 `SetupComplete.cmd`(OEM 키면 별도 단계) |
| 배포 VM     | 계정 비밀번호 자체                             | 첫 로그온 뒤 변경, LAPS 같은 관리 도구 검토                |

- 설치 프로그램은 각 구성 패스가 끝날 때 캐시된 응답 파일에서 민감 정보를 지운다고 하지만, Microsoft는 배포 전에 `%WINDIR%\Panther`의 캐시를 지우라고 따로 안내합니다.
- 🟡 일반화 VHDX에는 첫 부팅 전까지 OOBE 응답 파일이 들어 있습니다. VHDX 사본은 비밀번호와 같은 수준으로 보관합니다.
- `packer build -debug`는 WinRM 접속용 비밀번호를 화면에 보여 줄 수 있습니다. 로그를 공유하기 전에 확인합니다.

## 7. 결과물 다루기

- **켜기 전에 사본을 둡니다.** 일반화된 VHDX를 한 번 부팅하면 specialize·OOBE가 진행되어 일반화 상태가 사라집니다. 원본은 읽기 전용으로 보관하고 사본으로 VM을 만듭니다. 첫 부팅에 쓴 디스크는 크기가 늘고 일반화 상태가 사라진 반면, 켜기 전 사본은 크기·수정 시각이 그대로였다는 사례가 보고되었습니다([보고]). 사본은 SHA-256으로 원본과 같은지 확인해 둡니다.
- `skip_export = true`면 VHDX는 `<output_directory>/Virtual Hard Disks`에, `keep_registered = true`면 VM 설정 파일은 `temp_path` 아래에 남습니다. 두 옵션을 함께 쓰면 VHDX가 출력 폴더로 옮겨진 뒤에도 등록된 VM은 옛 임시 경로의 디스크를 가리켜 그대로는 켜지지 않는 사례가 보고되었습니다([보고]). `Get-VMHardDiskDrive -VMName <VM>`으로 경로를 확인하고, 그 VM을 쓰려면 일반화 원본이 아닌 사본을 다시 연결합니다(`Set-VMHardDiskDrive -Path <사본>`).
- 남긴 VM의 DVD에 응답 파일 ISO가 붙어 있으면 뗍니다(`Get-VMDvdDrive`·`Remove-VMDvdDrive`).
- Windows 클라이언트의 Hyper-V는 VM을 켤 때 자동 검사점을 만들어 변경을 `.avhdx`에 쌓고 원래 VHDX는 그대로 두는 사례가 보고되었습니다([보고]). 시험 VM에서 원본이 바뀌지 않은 것처럼 보여도 검사점을 병합하면 바뀌므로, 일반화 원본은 VM에 직접 연결하지 않습니다. 자동 검사점은 `Set-VM -Name <VM> -AutomaticCheckpointsEnabled $false`로 끌 수 있습니다. 이때 원래 VHDX 본체에는 OOBE 응답 파일(평문 비밀번호)이 그대로 남으므로, 시험에 쓴 사본도 비밀번호와 같은 수준으로 보관하고 끝나면 지웁니다.
- 같은 하드웨어 프로필의 Hyper-V VM에만 VHDX로 배포한다면 `sysprep /mode:vm`으로 첫 부팅을 줄일 수 있습니다. VM 안에서만 쓸 수 있으며, 문서는 함께 쓰는 추가 옵션으로 `/reboot`·`/shutdown`·`/quit`만 듭니다. 같은 프로필이 아닌 VM에 배포하면 예상하지 못한 문제가 생길 수 있다고 합니다.
- 한 이미지에 sysprep를 실행할 수 있는 횟수는 1001회입니다. 일반화한 이미지를 다시 켜서 고치고 또 일반화하는 대신, 템플릿을 고쳐 처음부터 다시 빌드하는 편이 기록과 재현에 좋습니다.
- 판 번호·체크섬 기록과 단계별 승격은 [VM 이미지 판 관리](../iac/vm_image_versioning.md)를 참고합니다.

## 8. 검증

| 항목               | 확인 방법                                                                                                                                                                                                                                                               |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 빌드 결과          | Packer 종료 코드 0, `<output_directory>/Virtual Hard Disks`에 VHDX                                                                                                                                                                                                      |
| 일반화 완료        | 같은 읽기 전용 마운트로 `Windows\System32\Sysprep\Panther\setupact.log` 끝에 일반화 성공 줄과 `Sysprep_succeeded.tag` 생성 기록, 이어서 종료 호출 기록. `setuperr.log`에 줄이 있으면 내용을 따로 확인                                                                   |
| 일반화 상태        | 켜지 않은 사본을 `Mount-DiskImage -Access ReadOnly`(관리자)로 붙여 `Windows\Setup\State\State.ini`의 `ImageState` 확인 후 바로 뗌. 일반화 뒤 OOBE 대기 상태로 `IMAGE_STATE_GENERALIZE_RESEAL_TO_OOBE`가 보고됨([보고], 공식 문서와 미대조)                              |
| 배포 사본 첫 부팅  | OOBE 화면 없이 로그온 화면까지 진행, 응답 파일의 계정으로 로그온                                                                                                                                                                                                        |
| 새 VM 부팅         | 켜기 전 사본을 복사(SHA-256 일치 확인)해 새 Gen2 VM(보안 부팅, vTPM)을 만들고, 첫 부팅과 게스트 재시작(`Restart-VM -Type Reboot`) 모두 자동 복구 화면 없이 로그온 화면까지 가는지 확인. vTPM은 호스트에서 `Get-VMSecurity`의 `TpmEnabled`, VM 안에서 `Get-Tpm`으로 확인 |
| 고유 정보          | 사본 2개의 컴퓨터 SID가 서로 다름(`whoami /user`의 SID 앞부분이나 Sysinternals `PsGetSid`)                                                                                                                                                                              |
| 응답 파일 정리     | 첫 부팅 뒤 `C:\Windows\System32\Sysprep\unattend.xml`, `C:\Windows\Panther\unattend.xml` 없음, 예약 작업 `packer-sysprep` 없음                                                                                                                                          |
| SetupComplete 실행 | `C:\Windows\Panther\UnattendGC\Setupact.log`에 실행 기록                                                                                                                                                                                                                |
| Windows 11 조건    | `Get-Tpm`(TpmPresent·TpmReady), `Confirm-SecureBootUEFI`가 True                                                                                                                                                                                                         |

권장 순서: ① 켜지 않은 사본을 읽기 전용으로 마운트해 `State.ini`·`setupact.log`·`setuperr.log` 확인 → ② 시험용 사본으로 OOBE 무인 통과와 첫 부팅 정리 확인 → ③ 다른 사본으로 새 VM(보안 부팅·vTPM) 첫 부팅 → ④ vTPM 확인 → ⑤ 게스트 재시작. 일반화 원본은 어느 단계에서도 VM에 직접 연결하지 않습니다.

## 9. 트러블슈팅

| 증상                                                                                           | 원인 후보                                                    | 확인·조치                                                                                                                                                                                                                                                                                                                                 |
|------------------------------------------------------------------------------------------------|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| VM은 켜졌는데 설치가 시작되지 않음(디스크 쓰기 없음)                                           | Gen2 DVD 부팅의 "Press any key" 대기를 놓침                  | `vmconnect`로 콘솔 확인. 키 입력을 놓치면 다음 부팅 장치로 넘어감(대기 시간은 공식 문서에서 미확인). `boot_wait`·키 입력 횟수·간격 조정                                                                                                                                                                                                   |
| 설치 초기 화면에서 멈춤                                                                        | 언어·에디션·키 화면, 응답 파일을 못 찾음                     | 콘솔 화면 확인. ISO 루트에 `Autounattend.xml` 이름이 맞는지, 에디션 번호가 맞는지                                                                                                                                                                                                                                                         |
| 제품 키·에디션 선택 화면                                                                       | 키 없는 설치, 에디션 번호 불일치                             | dism으로 번호 재확인. 키 처리 방식은 조직 라이선스 정책에 따름                                                                                                                                                                                                                                                                            |
| "<ProductKey> 설정을 읽을 수 없습니다" 오류                                                    | `ProductKey` 안에 `Key`가 없거나 비어 있음                   | 키가 없으면 `ProductKey` 요소를 통째로 뺌. 볼륨 라이선스면 [KMS 클라이언트 키 공식 표](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)의 GVLK 사용 검토(소매 인증 불가)                                                                                                                          |
| Packer가 WinRM만 오래 기다림                                                                   | 설치가 앞 단계(부팅·응답 파일 오류 대화상자)에서 멈춤        | 빌드 디스크 크기가 늘지 않으면 `vmconnect`로 VM 연결 창을 열어 설치 화면부터 확인                                                                                                                                                                                                                                                         |
| Packer가 WinRM 대기에서 시간 초과                                                              | 네트워크 공용 프로필, 첫 로그온 명령 실패, 자동 로그온 안 됨 | 콘솔로 로그온해 `winrm enumerate winrm/config/listener`, `Get-NetConnectionProfile` 확인                                                                                                                                                                                                                                                  |
| sysprep 실패(0x80073cf2)                                                                       | 사용자별로만 남은 Store 앱                                   | [sysprep 참조 노트](../../_reference/windows_sysprep_official_notes.md) 5절 명령으로 확인·제거                                                                                                                                                                                                                                            |
| shutdown 단계 시간 초과                                                                        | sysprep가 오류 화면에서 멈춤, `shutdown_timeout` 짧음        | 콘솔 확인, `%WINDIR%\System32\Sysprep\Panther\setuperr.log`                                                                                                                                                                                                                                                                               |
| `setuperr.log`에 `SYSPRP BCD: ... failed c000000d`, "Failed to export alterations to firmware" | sysprep가 UEFI 펌웨어(NVRAM) 부팅 항목을 갱신하지 못함       | 무해하다고 단정하지 않고 검증 절차로 다룸: 켜기 전 사본으로 새 VM(펌웨어 부팅 항목 없음)을 만들어 첫 부팅과 게스트 재시작 모두 자동 복구 없이 로그온 화면까지 가는지 확인. Windows 11 23H2 이미지 1회 시험에서 새 VM 첫 부팅과 재시작 모두 정상이었다는 사례가 보고됨([보고]). 다른 판(24H2 등)·업데이트 적용 뒤 sysprep는 따로 확인 대상 |
| `Failed to send shutdown command`(`wsarecv`)로 실패, 디스크가 지워짐                           | WinRM으로 동기 실행한 sysprep 도중 연결이 끊김               | 4-1절의 예약 작업 방식으로 바꿈. `-on-error=abort`는 provisioner 단계에만 적용된다고 문서에 적혀 있음                                                                                                                                                                                                                                     |
| 첫 부팅 뒤 응답 파일이 남음                                                                    | OEM 키라 `SetupComplete.cmd` 미실행                          | 5-2절의 별도 정리 단계                                                                                                                                                                                                                                                                                                                    |
| 빌드 기록에 packer 출력이 없음                                                                 | 셸 기록 기능만 사용                                          | `PACKER_LOG`·`PACKER_LOG_PATH`로 Packer 로그를 파일로 남김. 콘솔 출력도 함께 보려면 `Tee-Object`                                                                                                                                                                                                                                          |

- `PACKER_LOG_PATH`만 지정하면 로그가 남지 않습니다. `PACKER_LOG`도 비어 있지 않은 값(0 제외)으로 지정해야 합니다.
- PowerShell 5.1 `Start-Transcript`는 콘솔에 나타나는 출력을 기록한다고 설명하지만, `Write-Information` 출력은 5.1에서 기록되지 않는 문제가 문서에 적혀 있습니다. 외부 프로그램 출력이 빠지는 사례도 있으므로 Packer 로그는 위 환경 변수로 따로 남기는 편이 확실합니다.
- provisioner 단계 실패 지점을 보려면 `packer build -on-error=ask`(정리·중단·재시도 선택)나 `-on-error=abort`(정리 없이 종료, 다음 빌드에 `-force`가 필요할 수 있음)로 VM을 남긴 채 확인합니다.
- 설치 단계 로그: windowsPE 단계는 `X:\$Windows.~BT\Sources\Panther`(임시), 그 뒤는 `%WINDIR%\Panther`, OOBE 무인 처리는 `%WINDIR%\Panther\UnattendGC`. `setuperr.log`를 먼저, `setupact.log`를 다음에 봅니다.

TPM이 없는 호스트에서 시험할 때 쓰는 설치 검사 우회 레지스트리(`HKLM\SYSTEM\Setup\LabConfig`)는 Microsoft 문서에서 확인하지 못한 비공식 방법입니다. 지원 대상 이미지에는 쓰지 않고, Hyper-V vTPM(호스트 TPM과 무관하게 에뮬레이션)을 켜는 쪽을 먼저 검토합니다.

---

## 함께 보기

- [Hyper-V](./hyper_v.md) — 설치, 가상 스위치, VM 운영
- [Packer](../iac/packer.md) — `hyperv-iso` 빌더 옵션과 boot_command (4절)
- [VM 이미지 판 관리](../iac/vm_image_versioning.md) — 판 번호, manifest·checksum 기록
- [이미지 판 관리와 단계별 승격](../cicd/image_versioning_and_promotion.md) — 한 번 빌드하고 단계별로 올리는 원칙
- [Windows Server 에디션과 라이선스](./windows_server_editions_licensing.md) — 가상화 권한

---

## 참고 자료

- Microsoft Learn: [Sysprep (Generalize) a Windows installation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep--generalize--a-windows-installation) — ★★★☆☆
- Microsoft Learn: [Sysprep Command-Line Options](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-command-line-options) — ★★★☆☆
- Microsoft Learn: [Sysprep Process Overview](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-process-overview) — ★★★☆☆
- Microsoft Learn: [Sysprep fails after you remove or update Microsoft Store apps](https://learn.microsoft.com/en-us/troubleshoot/windows-client/setup-upgrade-and-drivers/sysprep-fails-remove-or-update-store-apps) — ★★★☆☆
- Microsoft Learn: [Windows Setup Automation Overview](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-setup-automation-overview) — ★★★☆☆
- Microsoft Learn: [Add a Custom Script to Windows Setup](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/add-a-custom-script-to-windows-setup) — ★★★☆☆
- Microsoft Learn: [Deployment Troubleshooting and Log Files](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/deployment-troubleshooting-and-log-files) — ★★★☆☆
- Microsoft Learn: [AutoLogon](https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-shell-setup-autologon) · [AdministratorPassword](https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-shell-setup-useraccounts-administratorpassword) — ★★★☆☆
- Microsoft Learn: [ProductKey](https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-setup-userdata-productkey) · [KMS client activation keys](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys) — ★★★☆☆
- Microsoft Learn: [Windows 11 requirements](https://learn.microsoft.com/en-us/windows/whats-new/windows-11-requirements) — ★★★☆☆
- Packer: [Hyper-V ISO builder](https://developer.hashicorp.com/packer/integrations/hashicorp/hyperv/latest/components/builder/iso) · [build 명령(-on-error)](https://developer.hashicorp.com/packer/docs/commands/build) · [Debugging](https://developer.hashicorp.com/packer/docs/debugging) · [WinRM communicator](https://developer.hashicorp.com/packer/docs/communicators/winrm) — ★★★☆☆

---

**작성일**: 2026-11-28

**마지막 업데이트**: 2026-11-28

© 2026 siasia86. Licensed under CC BY 4.0.
