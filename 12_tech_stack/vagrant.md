# Vagrant

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 설치](#4-설치) / [5. 주요 명령어](#5-주요-명령어) / [6. Vagrantfile](#6-vagrantfile) |
| [7. 프로비저닝](#7-프로비저닝) / [8. 멀티 머신](#8-멀티-머신) / [9. Tips](#9-tips) |

---

## 1. 개요

VM을 코드로 정의하고 자동으로 생성·관리하는 도구입니다. HashiCorp에서 개발했으며 VirtualBox, VMware, Hyper-V 등 다양한 하이퍼바이저를 지원합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                     Vagrant Flow                            │
│                                                             │
│  Vagrantfile ──> vagrant up ──> VM create + provisioning    │
│                                                             │
│  Provider: VirtualBox / VMware / Hyper-V / libvirt          │
│  Provisioner: shell / Ansible / Chef / Puppet               │
└─────────────────────────────────────────────────────────────┘
```

Docker 대비 완전한 OS 환경을 제공하므로 systemd, 커널 모듈, Windows Guest 등 컨테이너로 재현하기 어려운 환경에 적합합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Host Machine                           │
│                                                             │
│  vagrant CLI ──> Vagrant Core                               │
│                      │                                      │
│              ┌───────┴────────┐                             │
│              v                v                             │
│         Provider           Provisioner                      │
│     (VirtualBox/VMware)  (shell/Ansible)                    │
│              │                                              │
│              v                                              │
│    ┌───────────────────────┐                                │
│    │  Guest VM (full OS)   │                                │
│    │  - independent kernel │                                │
│    │  - systemd running    │                                │
│    └───────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념         | 설명                                                        |
|--------------|-------------------------------------------------------------|
| Box          | VM 베이스 이미지 (Vagrant Cloud에서 배포)                   |
| Vagrantfile  | VM 정의 파일 (Ruby DSL)                                     |
| Provider     | VM을 실제로 실행하는 하이퍼바이저                           |
| Provisioner  | VM 생성 후 자동 설정 도구 (shell, Ansible 등)               |
| Synced Folder| 호스트-게스트 간 공유 디렉토리                              |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

```bash
# Ubuntu
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vagrant virtualbox
```

```bash
vagrant --version
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령어

```bash
vagrant up                  # VM 생성 + 부팅 + 프로비저닝
vagrant halt                # VM 종료
vagrant suspend             # VM 일시 중지 (상태 저장)
vagrant resume              # 일시 중지 해제
vagrant reload              # 재시작 (Vagrantfile 변경 반영)
vagrant reload --provision  # 재시작 + 프로비저닝 재실행
vagrant destroy             # VM 삭제
vagrant destroy -f          # 확인 없이 삭제
vagrant ssh                 # SSH 접속
vagrant ssh <name>          # 멀티 머신 시 이름 지정
vagrant status              # VM 상태 확인
vagrant box list            # 로컬 box 목록
vagrant box add ubuntu/jammy64  # box 다운로드
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Vagrantfile

### 기본 구조

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "dev-server"

  # 네트워크
  config.vm.network "private_network", ip: "192.168.56.10"
  config.vm.network "forwarded_port", guest: 80, host: 8080

  # 공유 폴더
  config.vm.synced_folder "./src", "/var/www/html"

  # 리소스
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus   = 2
    v.name   = "dev-server"
  end
end
```

### 주요 Box

| OS                    | Box 이름                                      |
|-----------------------|-----------------------------------------------|
| Ubuntu 22.04          | `ubuntu/jammy64`                              |
| Ubuntu 24.04          | `ubuntu/noble64`                              |
| Rocky Linux 9         | `rockylinux/9`                                |
| Amazon Linux 2        | `bento/amazonlinux-2`                         |
| Windows Server 2022   | `gusztavvargadr/windows-server-2022-standard` |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 프로비저닝

### Shell

```ruby
config.vm.provision "shell", inline: <<-SHELL
  apt-get update
  apt-get install -y nginx
  systemctl enable nginx
SHELL
```

### Ansible

```ruby
config.vm.provision "ansible" do |ansible|
  ansible.playbook = "playbook.yml"
  ansible.inventory_path = "inventory"
  ansible.verbose = "v"
end
```

### 프로비저닝 재실행

```bash
vagrant provision           # 실행 중인 VM에 프로비저닝만 재실행
vagrant up --provision      # up 시 강제 프로비저닝
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 멀티 머신

Ansible 멀티 OS 테스트 환경 예시입니다.

```ruby
Vagrant.configure("2") do |config|

  {
    "ubuntu22"  => { box: "ubuntu/jammy64",                              ip: "192.168.56.11" },
    "ubuntu24"  => { box: "ubuntu/noble64",                              ip: "192.168.56.12" },
    "rocky9"    => { box: "rockylinux/9",                                ip: "192.168.56.13" },
    "win2022"   => { box: "gusztavvargadr/windows-server-2022-standard", ip: "192.168.56.20" },
  }.each do |name, cfg|
    config.vm.define name do |node|
      node.vm.box      = cfg[:box]
      node.vm.hostname = name
      node.vm.network "private_network", ip: cfg[:ip]

      node.vm.provider "virtualbox" do |v|
        v.memory = 1024
        v.cpus   = 1
      end

      # Windows는 WinRM, Linux는 SSH
      if name.start_with?("win")
        node.vm.communicator = "winrm"
      end

      # 마지막 머신(ubuntu22)에서 Ansible로 전체 머신 일괄 프로비저닝
      if name == "ubuntu22"
        node.vm.provision "ansible" do |ansible|
          ansible.playbook = "site.yml"
          ansible.limit    = "all"
        end
      end
    end
  end

end
```

```bash
vagrant up                  # 전체 VM 생성
vagrant up ubuntu22         # 특정 VM만 생성
vagrant ssh rocky9          # 특정 VM 접속
vagrant destroy -f          # 전체 삭제
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Tips

```bash
# VM 스냅샷 (VirtualBox 한정)
vagrant snapshot save   baseline
vagrant snapshot restore baseline
vagrant snapshot list

# box 업데이트
vagrant box update

# SSH 설정 확인 (ansible inventory 작성 시 활용)
vagrant ssh-config
```

공유 폴더 없이 빠른 기동이 필요하면 Vagrantfile에 추가합니다.

```ruby
config.vm.synced_folder ".", "/vagrant", disabled: true
```

⚠️ Windows Guest 사용 시 라이선스가 필요합니다. `gusztavvargadr` box는 평가판(180일)입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Vagrant Documentation: [developer.hashicorp.com/vagrant/docs](https://developer.hashicorp.com/vagrant/docs) — ★★★☆☆
- Vagrant Cloud (Box 검색): [portal.cloud.hashicorp.com/vagrant/discover](https://portal.cloud.hashicorp.com/vagrant/discover) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-15

**마지막 업데이트**: 2026-05-15

© 2026 siasia86. Licensed under CC BY 4.0.
