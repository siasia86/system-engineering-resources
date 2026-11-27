# 설정 관리 도구 비교 (Ansible · Chef · Puppet · Salt)
<!-- reference: _reference/chef_official_notes.md, _reference/puppet_openvox_official_notes.md, _reference/salt_official_notes.md -->

서버 안의 패키지·파일·서비스를 원하는 상태로 맞추는 설정 관리 도구 네 가지를 비교합니다. 같은 작업(디렉터리와 설정 파일 하나 만들기)을 각 도구로 쓴 예시와, 2024~2026년에 바뀐 배포·라이선스 조건을 함께 정리했습니다. 설치·운영 가이드가 아니라 도구를 고를 때 보는 문서입니다.

- 기준 판: ansible-core 2.22.0, Chef Infra Client 19.5.19, OpenVox 8.34.0·9.5.0(Puppet 호환), Salt 3008.5 LTS (2026-11-27 확인)
- 예제 시험: 2026-11-27 3절의 Puppet 예시는 Ubuntu 24.04 컨테이너의 OpenVox 8.34.0 `puppet apply`로, Salt 예시는 Debian 13 컨테이너의 Salt 3008.5 onedir `salt-call --local`로 실행해 적용·재적용·미리 보기·문법 오류를 확인. Ansible 예시는 이 저장소의 Ansible 문서 문법을 따랐고 이번에 실행하지 않음. Chef 예시는 내려받기에 라이선스 키가 필요해 미실행. 서버(master) 구성, 여러 노드 관리는 미실행

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 한눈에 비교](#2-한눈에-비교) / [3. 같은 작업 예시](#3-같은-작업-예시)             |
| [4. 배포와 라이선스 변화](#4-배포와-라이선스-변화) / [5. 고르는 기준](#5-고르는-기준) / [6. 검증](#6-검증) |
| [함께 보기](#함께-보기)                                                                                    |

---

## 1. 개요

```text
push (agentless)                         pull (agent)
[control node] --SSH/WinRM--> [hosts]    [server] <--periodic check-- [agent on each host]
  Ansible, Salt-SSH                         Chef, Puppet/OpenVox, Salt minion
```

| 용어 | 뜻                                                                                 |
|------|------------------------------------------------------------------------------------|
| push | 관리 노드가 대상에 접속해 실행. 대상에 상주 프로그램이 없어도 됨                   |
| pull | 대상마다 agent가 있어 주기적으로 서버에서 설정을 받아 적용. 설정이 틀어지면 되돌림 |
| 멱등 | 여러 번 실행해도 결과가 같음. 이미 원하는 상태면 바꾸지 않음                       |

- Terraform·Pulumi가 클라우드 리소스(서버·네트워크)를 만드는 쪽이라면, 설정 관리 도구는 만들어진 서버 안을 맞추는 쪽입니다. 둘을 함께 쓰는 경우가 많습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 항목          | Ansible                                   | Chef                               | Puppet / OpenVox                                  | Salt                                    |
|---------------|-------------------------------------------|------------------------------------|---------------------------------------------------|-----------------------------------------|
| 작성 언어     | YAML(playbook) + Jinja2                   | Ruby DSL(recipe)                   | Puppet DSL(manifest)                              | YAML(SLS) + Jinja2                      |
| 방식          | push, agent 없음(SSH)                     | pull(agent), 단독 실행 가능        | pull(agent), 단독 `puppet apply` 가능             | push·pull 모두(minion), SSH 방식도 있음 |
| 서버          | 없음(AWX·AAP는 선택)                      | Chef Infra Server                  | Puppet Server / openvox-server                    | Salt master                             |
| 단독 실행     | `ansible-playbook -i localhost, -c local` | `chef-client --local-mode`         | `puppet apply`                                    | `salt-call --local`                     |
| 미리 보기     | `--check --diff`                          | `--why-run`                        | `--noop`                                          | `test=True`                             |
| 최신 판       | ansible-core 2.22.0(2026-11-02)           | 19.5.19(2026-11-24 태그)           | OpenVox 9.5.0·8.34.0(2026-11-19)                  | 3008.5(2026-10-26), 3007.17, 3006.30    |
| 소스 라이선스 | GPL-3.0                                   | Apache-2.0                         | Apache-2.0(Puppet, OpenVox 저장소)                | Apache-2.0                              |
| 배포 조건     | 제한 없음                                 | 공식 배포판 내려받기에 라이선스 키 | Puppet은 비공개 배포(무료 25노드), OpenVox는 공개 | 공개, 저장소가 Broadcom Artifactory     |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 같은 작업 예시

`/opt/app` 디렉터리와 `/opt/app/app.conf`(`port=8080`)를 만드는 예시입니다.

### 3.1 Ansible (미실행)

```yaml
- hosts: all
  become: true
  tasks:
    - name: app dir
      ansible.builtin.file:
        path: /opt/app
        state: directory
        mode: "0755"
    - name: app conf
      ansible.builtin.copy:
        dest: /opt/app/app.conf
        content: "port=8080\n"
        mode: "0644"
```

### 3.2 Chef (미실행)

```ruby
directory '/opt/app' do
  mode '0755'
end

file '/opt/app/app.conf' do
  content "port=8080\n"
end
```

- Chef는 recipe에 쓴 순서대로 실행합니다. 단독으로는 `chef-client --local-mode`로 돌립니다.

### 3.3 Puppet / OpenVox (시험함)

```puppet
file { '/opt/app':
  ensure => directory,
  mode   => '0755',
}
file { '/opt/app/app.conf':
  ensure  => file,
  content => "port=8080\n",
  require => File['/opt/app'],
}
```

```bash
puppet parser validate site.pp
puppet apply --noop site.pp                  # 미리 보기
puppet apply --detailed-exitcodes site.pp    # 0: 변경 없음, 2: 변경함, 4·6: 실패 포함
```

- 시험 결과: 첫 적용 종료 코드 2, 재적용 0. 문법 오류는 `Syntax error at 'ensure' (file: ..., line: 1, column: 13)`.
- 의존 관계가 없는 리소스는 manifest에 쓴 순서로 적용됩니다. 순서가 중요한 곳은 `require`·`before`·`notify`로 관계를 적어 두어야 파일을 나누거나 옮겨도 순서가 유지됩니다.

### 3.4 Salt (시험함)

`/srv/salt/web/init.sls`:

```yaml
app_dir:
  file.directory:
    - name: /opt/app
    - mode: '0755'

app_conf:
  file.managed:
    - name: /opt/app/app.conf
    - contents: |
        port={{ pillar.get('port', 8080) }}
    - require:
      - file: app_dir
```

```bash
salt-call --local state.apply test=True    # 미리 보기
salt-call --local state.apply
```

- 시험 결과: pillar에 `port: 9090`을 두면 파일에 `port=9090`. 재적용은 `Succeeded: 2`에 변경 없음. YAML 오류는 `Rendering SLS 'base:web' failed: mapping values are not allowed in this context`.
- Python 3.13 컨테이너에서 `pip install salt==3008.5`는 의존 패키지(`timelib`) 빌드 실패로 설치되지 않았습니다. 공식 onedir 압축판이나 패키지 저장소를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 배포와 라이선스 변화

### 4.1 Puppet과 OpenVox

- Perforce(Puppet 소유사)는 2024-11-07 공지에서 2025년 초부터 새 오픈소스 Puppet 바이너리·패키지를 비공개 저장소로 옮긴다고 밝혔습니다. 소스는 Apache 2.0을 유지하고, 개발자는 EULA 아래 25노드까지 무료로 받을 수 있으며 그 이상은 상용 라이선스가 필요합니다. 이 배포판 이름이 Puppet Core입니다.
- 공개 저장소 `puppetlabs/puppet`의 마지막 커밋은 2024-12이고, GitHub 릴리스의 마지막은 8.10.0(2024-10-22)입니다.
- Vox Pupuli 커뮤니티가 만든 OpenVox가 공개 패키지를 이어 냅니다. 설치 문서는 "As of release 8.11, OpenVox is functionally equivalent to Puppet; the command names are the same"라고 하고, Puppet과 같은 서버에 함께 설치할 수는 없습니다.
- 패키지: `openvox-agent`, `openvox-server`, `openvoxdb`, `openvoxdb-termini`, `openbolt`. 저장소 패키지는 `openvox9-release`가 기본이고 `openvox8-release`는 EOL까지 중요·보안 수정만 받습니다.
- OpenVox 9는 Ruby 4.0.7을 쓰며, `server` 설정의 기본값(`puppet`) 제거, `reports` 기본값 `none`, `--configprint` 제거, EL 7·Amazon Linux 2 지원 중단 같은 변화가 있습니다. 서버를 9로 올리면 agent도 9.0.0 이상이 필요합니다.

### 4.2 Chef

- Chef Infra Client 19부터 공식 배포판 내려받기에 Chef 라이선스 키 인증이 필요합니다. 공식 배포판을 받은 뒤 실행할 때는 키를 검사하지 않고, 공개 Ruby gem 같은 비공식 경로나 실행 중 설치 방식에서는 키가 필요합니다.
- 키는 `CHEF_LICENSE_KEY` 환경 변수나 `chef-client --chef-license-key=<키>`로 줍니다. EULA 동의(`CHEF_LICENSE`, `--chef-license accept`)와는 다른 설정입니다.
- 19는 Habitat 기반 패키지(`chef-ice`)로 바뀌어 설치 경로가 `/opt/chef`에서 `/hab/pkgs/chef/chef-infra-client`로 바뀌었고, Ruby가 3.4.8이 됐습니다. Chef Workstation 26 이상이 필요합니다.

### 4.3 Salt

- Salt는 2026-05-27에 3008.0을 LTS로 냈습니다. 공식 지원 표 기준:

| 판       | 출시       | 일반 지원 끝 | CVE·중대 수정 끝 |
|----------|------------|--------------|------------------|
| 3008 LTS | 2026-05-27 | 2027-06      | 2028-06          |
| 3007 STS | 2024-03-06 | 2026-06      | 표에 없음        |
| 3006 LTS | 2023-04-18 | 2026-07      | 2027-06          |

- 2026-11 기준 새로 구성한다면 3008입니다. 3006은 CVE 수정만 받는 기간이고, 3007은 일반 지원이 끝났습니다.
- 패키지 저장소와 onedir 압축판은 Broadcom Artifactory(`packages.broadcom.com`)에서 받습니다.

### 4.4 Ansible

- 소스 라이선스가 GPL-3.0이고 배포 조건 변화는 없습니다. 판과 설치는 [Ansible 팀 운영](./ansible_install_and_team_operation.md) 문서를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 고르는 기준

| 상황                                                    | 먼저 볼 도구             | 이유                                                        |
|---------------------------------------------------------|--------------------------|-------------------------------------------------------------|
| 대상 서버에 agent를 두기 어렵다, 작은 규모로 시작       | Ansible                  | SSH만 있으면 됨, YAML                                       |
| 수천 대에 같은 설정을 계속 유지(설정이 틀어지면 되돌림) | Puppet/OpenVox, Salt     | agent가 주기적으로 적용, 보고서                             |
| 이벤트에 바로 반응(로그·상태 변화 → 조치)               | Salt                     | 이벤트 버스, reactor                                        |
| Ruby에 익숙한 팀, 기존 Chef 자산이 많음                 | Chef                     | 기존 cookbook 재사용. 19의 라이선스 키 조건 확인            |
| 기존 Puppet 오픈소스를 쓰고 있음                        | OpenVox 또는 Puppet Core | 25노드 이하는 Puppet Core 무료, 그 이상은 OpenVox 또는 상용 |

- 이미 Ansible을 쓰는 팀이 새 도구를 들일 이유는 주로 "agent로 계속 맞추기"가 필요할 때입니다. Ansible도 주기 실행(cron, AWX 일정)으로 비슷하게 할 수 있습니다.
- 바꾸기 전에 라이선스·배포 조건을 운영 규모(노드 수)에 맞춰 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용 | Puppet / OpenVox                   | Salt                                   |
|------|-----------|------------------------------------|----------------------------------------|
| 1    | 판        | `puppet --version` → 8.34.0        | `salt-call --version` → 3008.5 (Argon) |
| 2    | 문법      | `puppet parser validate`           | `state.apply test=True`                |
| 3    | 미리 보기 | `--noop`에 `(noop)` 표시           | `Result: None`                         |
| 4    | 적용      | `--detailed-exitcodes` 종료 코드 2 | `Succeeded: 2 (changed=2)`             |
| 5    | 멱등      | 다시 적용 종료 코드 0              | 다시 적용 `changed` 없음               |
| 6    | 사실 수집 | `facter os.name`                   | `grains.item os`                       |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ansible 기초](./ansible_basic_guide.md) — 인벤토리, 플레이북, 롤
- [Terraform](./terraform.md) — 클라우드 리소스 만들기
- [Pulumi](./pulumi.md) — 일반 언어 IaC
- [SOPS](./sops.md) — 설정에 들어갈 비밀값 파일 암호화

---

## 참고 자료

- Puppet: [Open source Puppet updates 2025](https://www.puppet.com/blog/open-source-puppet-updates-2025) · [Puppet Core](https://puppet.com/products/puppet-core) — ★★★☆☆
- Vox Pupuli: [OpenVox](https://voxpupuli.org/openvox/) · [Install](https://voxpupuli.org/openvox/install/) · [9.0.0 release](https://github.com/OpenVoxProject/openvox/releases/tag/9.0.0) — ★★★☆☆
- Chef Docs: [Infra Client 19 license](https://docs.chef.io/client/19/license/) · [Infra Client 18과 19 차이](https://www.chef.io/blog/what-s-the-difference-between-progress-chef-infra-client-18-and-19) — ★★★☆☆
- Salt: [Version support lifecycle](https://docs.saltproject.io/salt/install-guide/en/latest/topics/salt-version-support-lifecycle.html) · [3008.0 LTS](https://saltproject.io/blog/2026-05-27-salt-3008-0-available/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
