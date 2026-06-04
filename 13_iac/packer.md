# Packer — 머신 이미지 자동 빌드

HashiCorp Packer로 VM 이미지를 코드로 정의하고 자동 빌드합니다.

## 목차

| 섹션                                                                                         |
|----------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 핵심 개념](#3-핵심-개념)                       |
| [4. Hyper-V 빌더](#4-hyper-v-빌더) / [5. kickstart 전달](#5-kickstart-전달) / [6. 팁](#6-팁) |

---

## 1. 개요

Packer는 동일한 머신 이미지를 여러 플랫폼에 자동으로 생성하는 도구입니다.
하나의 템플릿으로 개발/스테이징/운영 환경에 동일한 이미지를 배포할 수 있습니다.

```
HCL template (.pkr.hcl)
       │
       v
packer init ──> plugin download
       │
       v
packer build ──> ISO boot ──> OS install ──> provisioner ──> shutdown ──> image output
                    │              │               │
                    v              v               v
              boot_command   kickstart/       shell/ansible/
              (keystrokes)   cloud-init       powershell
```

### 지원 플랫폼 (빌더)

| 빌더         | 출력 형식           | 주요 용도               |
|--------------|---------------------|-------------------------|
| `hyperv-iso` | VHDX / Vagrant box  | 로컬 개발 VM            |
| `amazon-ebs` | AMI                 | AWS EC2                 |
| `azure-arm`  | VHD / Managed Image | Azure VM                |
| `vmware-iso` | VMDK / OVA          | VMware ESXi/Workstation |
| `qemu`       | qcow2               | KVM/libvirt             |
| `docker`     | Docker image        | 컨테이너 베이스 이미지  |

## 2. 설치

### Linux (apt)

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
|  | sudo tee /etc/apt/sources.list.d/hashicorp.list |
sudo apt-get update && sudo apt-get install -y packer
```

### Windows (Chocolatey)

```powershell
choco install packer -y
```

### 버전 확인

```bash
packer version
```

## 3. 핵심 개념

| 개념           | 설명                                              |
|----------------|---------------------------------------------------|
| Source         | VM 생성 방법 정의 (빌더, ISO, 하드웨어)           |
| Build          | source + provisioner + post-processor 조합        |
| Provisioner    | OS 설치 후 추가 구성 (shell, ansible, powershell) |
| Post-processor | 빌드 결과물 변환 (vagrant box, compress 등)       |
| Variable       | 외부 입력값 (ISO 경로, 패스워드 등)               |

### HCL 템플릿 기본 구조

```hcl
packer {
  required_plugins {
    hyperv = {
      source  = "github.com/hashicorp/hyperv"
      version = "~> 1"
    }
  }
}

variable "switch_name" {
  default = "External"
}

source "hyperv-iso" "example" {
  iso_url      = "https://..."
  iso_checksum = "file:https://..."
  vm_name      = "packer-example"
  generation   = 1
  cpus         = 2
  memory       = 2048
  disk_size    = 51200
  switch_name  = var.switch_name

  communicator = "ssh"
  ssh_username = "vagrant"
  ssh_password = "vagrant"
  ssh_timeout  = "30m"

  shutdown_command = "sudo systemctl poweroff"
}

build {
  sources = ["source.hyperv-iso.example"]

  provisioner "shell" {
    inline = ["echo done"]
  }

  post-processor "vagrant" {
    output = "example.box"
  }
}
```

### 빌드 라이프사이클

```
packer build 실행
    │
    ├── 1. ISO 다운로드 (packer_cache/ 에 캐시)
    ├── 2. VM 생성 (Hyper-V/VMware/QEMU)
    ├── 3. boot_command 입력 (키스트로크 시뮬레이션)
    ├── 4. OS 설치 대기 (kickstart/cloud-init/unattend)
    ├── 5. SSH/WinRM 연결 대기 (communicator)
    ├── 6. provisioner 실행 (shell, ansible 등)
    ├── 7. shutdown_command 실행
    ├── 8. VM export / 이미지 변환
    └── 9. post-processor (vagrant box 패키징 등)
```

### 명령어

| 명령어                         | 설명                 | 비고                       |
|--------------------------------|----------------------|----------------------------|
| `packer init .`                | 플러그인 다운로드    | 최초 1회 또는 버전 변경 시 |
| `packer validate .`            | 문법 검증            | CI/CD에서 사용             |
| `packer build file.hcl`        | 빌드 실행            | `-var` 옵션으로 변수 주입  |
| `packer build -force file.hcl` | 기존 output 덮어쓰기 | output_directory 충돌 시   |
| `packer fmt file.hcl`          | HCL 포맷팅           | terraform fmt와 동일       |
| `packer inspect file.hcl`      | 템플릿 요약 출력     | source/variable 확인       |

```bash
packer init .          # 플러그인 다운로드
packer validate .      # 문법 검증
packer build file.hcl  # 빌드 실행
```

## 4. Hyper-V 빌더

### Generation 선택

| Generation | 부트       | 용도                      |
|------------|------------|---------------------------|
| Gen1       | BIOS (MBR) | Rocky/CentOS, 레거시 OS   |
| Gen2       | UEFI (GPT) | Ubuntu 20+, Windows 2016+ |

### 주요 옵션

| 옵션                   | 설명                                                        |
|------------------------|-------------------------------------------------------------|
| `memory`               | RAM (MB). ~~`ram_size`~~ 는 deprecated                      |
| `switch_name`          | Hyper-V 가상 스위치 이름                                    |
| `enable_secure_boot`   | Gen2 전용, UEFI Secure Boot                                 |
| `secure_boot_template` | `MicrosoftWindows` 또는 `MicrosoftUEFICertificateAuthority` |
| `secondary_iso_images` | 추가 CD-ROM 마운트 (kickstart ISO 등)                       |
| `http_directory`       | Packer HTTP 서버 디렉토리 (cloud-init 등)                   |
| `ssh_host`             | SSH 접속 대상 IP (static IP 사용 시 필수)                   |
| `output_directory`     | VHDX 출력 경로 (기본: `output-<vm_name>`)                   |
| `boot_wait`            | VM 시작 후 boot_command 전송까지 대기 시간                  |
| `shutdown_timeout`     | shutdown 명령 후 VM 종료 대기 시간                          |

### boot_command 키 시퀀스

boot_command는 VM 콘솔에 키스트로크를 전송합니다. 특수 키 표기:

| 키              | 설명                         |
|-----------------|------------------------------|
| `<enter>`       | Enter 키                     |
| `<tab>`         | Tab 키 (GRUB 편집 모드 진입) |
| `<up>` `<down>` | 방향키 (메뉴 선택)           |
| `<wait>`        | 1초 대기                     |
| `<wait10>`      | 10초 대기                    |
| `<wait30s>`     | 30초 대기                    |
| `<esc>`         | Esc 키                       |
| `<spacebar>`    | 스페이스바                   |

#### OS별 boot_command 패턴

```hcl
 # Rocky/RHEL Gen1 BIOS — GRUB 메뉴에서 tab으로 커널 파라미터 편집
boot_command = ["<wait10><tab> inst.ks=cdrom:/dev/sr1:/ks.cfg<enter>"]

 # Ubuntu Gen2 UEFI — GRUB command line 진입
boot_command = [
  "c<wait>",
  "linux /casper/vmlinuz --- autoinstall ds='nocloud-net;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/'<enter><wait>",
  "initrd /casper/initrd<enter><wait>",
  "boot<enter>"
]

 # Windows — floppy 기반 무인 설치 (boot_command 불필요)
boot_command = ["<enter>"]
```

## 5. kickstart 전달

RHEL/Rocky/CentOS 계열 자동 설치에 kickstart 파일을 전달하는 방법입니다.

### 방법 비교

| 방식             | 동작 원리                              | Hyper-V 호환             |
|------------------|----------------------------------------|--------------------------|
| `http_directory` | Packer가 HTTP 서버 시작, VM이 다운로드 | ❌ 불안정                |
| `secondary_iso`  | ISO를 CD-ROM으로 마운트                | ✅ 안정적                |
| `floppy_files`   | 플로피 디스크 이미지로 전달            | ✅ (Windows unattend 용) |

### secondary_iso 방식 (권장)

```bash
# 1. ISO 생성 (볼륨 라벨 OEMDRV 필수)
genisoimage -o ks.iso -V OEMDRV -r -J /path/to/ks_dir/

# 2. pkr.hcl에서 참조
secondary_iso_images = ["C:\\path\\to\\ks.iso"]
boot_command         = ["<wait10><tab> inst.ks=cdrom:/dev/sr1:/ks.cfg<enter>"]
```

### OEMDRV 자동 감지

Rocky/RHEL anaconda는 볼륨 라벨 `OEMDRV`인 미디어에서 `ks.cfg`를 자동 검색합니다.
`boot_command`에 `inst.ks` 파라미터 없이도 동작할 수 있으나, 명시하는 것이 안정적입니다.

### kickstart %packages 주의사항

minimal ISO에 포함되지 않은 패키지를 `%packages`에 지정하면
anaconda가 대화형 프롬프트에서 멈춥니다.

```bash
 # ❌ minimal ISO에 없는 패키지 → 설치 멈춤
%packages
hyperv-daemons
%end

 # ✅ %post에서 네트워크 설치
%post
dnf install -y hyperv-daemons || true
%end
```

### Ubuntu autoinstall (cloud-init)

Ubuntu 20.04+ live-server ISO는 kickstart 대신 cloud-init autoinstall을 사용합니다.

#### 필요 파일

| 파일             | 역할                            |
|------------------|---------------------------------|
| `http/user-data` | autoinstall 설정 (YAML)         |
| `http/meta-data` | 빈 파일 (필수, cloud-init 규격) |

#### user-data 예시

```yaml
 #cloud-config
autoinstall:
  version: 1
  locale: en_US.UTF-8
  identity:
    hostname: ubuntu24
    username: vagrant
    password: "$6$..."   # mkpasswd --method=SHA-512
  ssh:
    install-server: true
    allow-pw: true
  storage:
    layout:
      name: lvm
  packages:
    - openssh-server
    - linux-tools-virtual      # Hyper-V Integration Services
    - linux-cloud-tools-virtual
  late-commands:
    - echo 'vagrant ALL=(ALL) NOPASSWD:ALL' > /target/etc/sudoers.d/vagrant
```

#### password 해시 생성

```bash
mkpasswd --method=SHA-512 --salt=randomsalt vagrant
```

## 6. 팁

### static IP + ssh_host

DHCP가 불안정한 환경에서는 kickstart에 static IP를 설정하고
`ssh_host`를 명시하면 packer가 해당 IP로 직접 SSH를 시도합니다.

```hcl
ssh_host = "10.200.101.174"
```

```
# ks.cfg
network --bootproto=static --ip=10.200.101.174 --netmask=255.255.255.0 --gateway=10.200.101.1 --nameserver=8.8.8.8 --activate
```

### provisioner SSH disconnect 방지

장시간 명령어(`dracut -f`, 대용량 `dnf install`)는 SSH 타임아웃을 유발합니다.

- 불필요한 명령 제거 (Gen1 BIOS에서 `dracut -f` 불필요)
- 필요 시 `expect_disconnect = true` 추가
- `dnf install`에 `--setopt=timeout=60` 추가

### 원격 빌드 (Task Scheduler 경유)

Packer는 Hyper-V 호스트에서 실행해야 합니다.
Linux 서버에서 SSH + Task Scheduler로 원격 빌드를 실행합니다:

```bash
 # Task Scheduler 실행 (SSH 세션 종료 후에도 유지)
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes ansibleuser@<host> \
  "cmd /c \"chcp 65001 > nul && schtasks /Run /TN PackerBuild\""
```

🟡 Packer를 SSH 세션 내에서 직접 실행하면 세션 종료 시 빌드가 중단됩니다.
Task Scheduler 등록이 필수입니다.

### 빌드 로그

PowerShell에서 실시간 로그:

```powershell
packer build rocky9.pkr.hcl *>&1 | Tee-Object -FilePath packer_build.log -Append
```

🟡 `Out-File` 파이프는 packer 종료 후에야 flush됩니다.
실시간 확인이 필요하면 `Tee-Object`를 사용합니다.

### ISO 캐시 관리

다운로드된 ISO는 `packer_cache/` 디렉토리에 저장됩니다.
동일 ISO를 재빌드할 때 다시 다운로드하지 않습니다.

```powershell
 # 캐시 크기 확인
Get-ChildItem packer_cache -Recurse | Measure-Object -Property Length -Sum

 # 캐시 삭제 (ISO 재다운로드 필요 시)
Remove-Item -Recurse packer_cache
```

### 디버깅

| 레벨                 | 방법                                         |
|----------------------|----------------------------------------------|
| 로그 상세            | `$env:PACKER_LOG=1; packer build file.hcl`   |
| VM 콘솔 확인         | `vmconnect.exe localhost <vm_name>`          |
| SSH 직접 테스트      | `ssh vagrant@<ip>` (빌드 중 VM이 떠 있을 때) |
| 빌드 중단 시 VM 정리 | `Remove-VM -Name packer-* -Force`            |

---

## 참고 자료

- Packer Documentation: [developer.hashicorp.com/packer/docs](https://developer.hashicorp.com/packer/docs) — ★★★☆☆
- Hyper-V Builder: [developer.hashicorp.com/packer/integrations/hashicorp/hyperv](https://developer.hashicorp.com/packer/integrations/hashicorp/hyperv) — ★★★☆☆
- Red Hat Kickstart: [docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/performing_an_advanced_rhel_9_installation/kickstart-commands-and-options-reference_installing-rhel-as-an-experienced-user](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/performing_an_advanced_rhel_9_installation/kickstart-commands-and-options-reference_installing-rhel-as-an-experienced-user) — ★★★☆☆

---

**작성일**: 2026-06-04

**마지막 업데이트**: 2026-06-04

© 2026 sjyun. Licensed under CC BY 4.0.
