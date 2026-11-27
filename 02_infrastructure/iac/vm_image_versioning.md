# VM 이미지 판 관리 (Vagrant box·Packer)
<!-- reference: _reference/vagrant_box_versioning_official_notes.md -->

Packer로 만든 VM 이미지를 판 번호로 보관하고, Vagrant box catalog(`metadata.json`)로 배포해 사용하는 쪽에서 판을 고정하거나 갱신하게 하는 방법을 정리합니다. 원칙은 [이미지 판 관리와 단계별 승격](../cicd/image_versioning_and_promotion.md)에 있고, 이 문서는 box와 Packer 기록의 실제 설정을 다룹니다.

- 기준 판: Vagrant 2.4.9, Packer 1.16.3, packer-plugin-vagrant v1.1.7 (2026-11-27 확인)
- 예제 시험: 2026-11-27 debian:13-slim 컨테이너에서 3·5·6절(정적 HTTP 서버의 catalog로 판 고정 설치, 조건식 판 선택, 체크섬 불일치 거부, `outdated`·`update`·`prune`·`remove`), 7절(Packer `checksum`·`manifest` 후처리기), 8절 스크립트를 실행. provider가 필요한 Vagrantfile 시험은 docker provider box로 했고 VM은 띄우지 않았음. Hyper-V(VHDX)·VirtualBox·libvirt 실제 빌드와 `vagrant up`, Nexus 위 catalog 배포는 미시험(Nexus raw 올리기 자체는 [Nexus 문서](../cicd/nexus.md)에서 시험)

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 구성 개요](#1-구성-개요) / [2. box 파일 구조](#2-box-파일-구조) / [3. catalog 작성](#3-catalog-작성) |
| [4. 저장소에 올리기](#4-저장소에-올리기) / [5. Vagrantfile에서 판 고정](#5-vagrantfile에서-판-고정)      |
| [6. 갱신과 정리](#6-갱신과-정리) / [7. Packer로 판과 체크섬 기록](#7-packer로-판과-체크섬-기록)          |
| [8. catalog 갱신 스크립트](#8-catalog-갱신-스크립트) / [9. VHDX와 다른 형식](#9-vhdx와-다른-형식)        |
| [10. 검증](#10-검증) / [11. 트러블슈팅](#11-트러블슈팅) / [함께 보기](#함께-보기)                        |

---

## 1. 구성 개요

```text
Packer 빌드 (판 1.1.0, commit 3f2a9c1)
  ├─ app-1.1.0-libvirt-amd64.box
  ├─ app-1.1.0.sha256          (checksum 후처리기)
  └─ packer-manifest.json      (manifest 후처리기: 판·commit·시각)
        |
        v
파일 저장소 (HTTP)
  ├─ boxes/app/1.1.0/app-1.1.0-libvirt-amd64.box   ← 한 번 올리면 바꾸지 않음
  └─ catalog/app/metadata.json                     ← 판이 늘 때마다 갱신
        |
        v
Vagrant 사용자
  config.vm.box_url     = ".../catalog/app/metadata.json"
  config.vm.box_version = "~> 1.1.0"
```

- HCP Vagrant Registry(옛 Vagrant Cloud)는 공식 안내상 2026-11-02에 지원이 끝났고 2026-12-31에 운영을 마칩니다. 새로 구성한다면 box와 catalog를 직접 호스팅합니다.
- 파일 저장소는 정적 HTTP 서버, 객체 저장소, Nexus raw 저장소 등 HTTP로 파일을 줄 수 있으면 됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. box 파일 구조

| 구분      | box 안의 `metadata.json`                  | catalog `metadata.json`                     |
|-----------|-------------------------------------------|---------------------------------------------|
| 위치      | box 압축 파일 안                          | 저장소의 별도 파일                          |
| 내용      | 이 box의 `provider`(필수), `architecture` | box 이름, 판 목록, 판별 provider·URL·체크섬 |
| 바뀌는 때 | 바뀌지 않음                               | 새 판을 올릴 때마다                         |

box 파일은 tar, tar.gz, zip이며 VM 디스크 파일과 `metadata.json`(필수), 선택으로 `Vagrantfile`·`info.json`이 들어갑니다.

```bash
tar -tzf app-1.1.0-libvirt-amd64.box     # metadata.json, box.img ...
tar -xzOf app-1.1.0-libvirt-amd64.box metadata.json
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. catalog 작성

```json
{
  "name": "example/app",
  "description": "example application base box",
  "versions": [
    {
      "version": "1.0.0",
      "providers": [
        {
          "name": "libvirt",
          "architecture": "amd64",
          "default_architecture": true,
          "url": "https://boxes.example.com/boxes/app/1.0.0/app-1.0.0-libvirt-amd64.box",
          "checksum_type": "sha256",
          "checksum": "<SHA256>"
        }
      ]
    }
  ]
}
```

| 필드                       | 설명                                                             |
|----------------------------|------------------------------------------------------------------|
| `name`                     | `vagrant box list`에 보이는 이름. 조직/이름 형식이 일반적        |
| `versions[].version`       | X.Y.Z 정수만. `1.0`이나 `1.0.0-rc1`은 쓸 수 없음                 |
| `providers[].name`         | `virtualbox`, `libvirt`, `hyperv`, `vmware_desktop`, `docker` 등 |
| `architecture`             | `amd64`, `arm64` 등. 같은 판에 아키텍처별 항목을 둘 수 있음      |
| `default_architecture`     | 아키텍처를 지정하지 않은 사용자에게 줄 항목                      |
| `checksum_type`·`checksum` | md5, sha1, sha256, sha384, sha512. sha256 권장                   |

- 같은 판에 provider를 여러 개 둘 수 있습니다(예: 1.0.0에 libvirt와 hyperv).
- 검증하지 않은 판은 catalog에 넣지 않습니다. 시험에서 체크섬이 틀린 1.2.0이 catalog에 있자 `vagrant box outdated --global`이 1.2.0을 최신으로 알렸고, `vagrant box update --box`는 1.2.0을 받으려다 체크섬 오류로 실패했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 저장소에 올리기

box 파일은 한 번 올리면 바꾸지 않고, catalog는 판이 늘 때마다 덮어씁니다. 그래서 쓰기 정책을 둘로 나눕니다.

| 대상     | 쓰기 정책     | Nexus raw hosted 예       |
|----------|---------------|---------------------------|
| box 파일 | 한 번만 쓰기  | `writePolicy: allow_once` |
| catalog  | 덮어쓰기 허용 | `writePolicy: allow`      |

Nexus raw 저장소에 올리는 예입니다(저장소 만들기와 인증은 [Nexus 문서](../cicd/nexus.md#41-raw-hosted-파일-보관) 참고, `$NEXUS`·`$AUTH`는 자리표시자).

```bash
V=1.1.0
curl -fsS -u "$AUTH" --upload-file output/app-$V-libvirt-amd64.box \
  "$NEXUS/repository/boxes/app/$V/app-$V-libvirt-amd64.box"          # 201, 같은 경로 재업로드는 409
curl -fsS -u "$AUTH" --upload-file metadata.json \
  "$NEXUS/repository/box-catalog/app/metadata.json"
```

- Vagrant는 HTTP catalog에 기본 인증을 쓸 수 있고, `config.vm.box_download_options`로 curl 옵션을, `box_download_client_cert`·`box_download_ca_cert`로 인증서를 줄 수 있습니다. 비밀번호를 Vagrantfile에 적지 말고 환경 변수나 사용자별 설정에서 읽습니다.
- 단계별 승격이 필요하면 catalog를 단계별로 나눕니다(예: `box-catalog/dev/app/metadata.json`, `box-catalog/prod/app/metadata.json`). box 파일은 한 곳에 두고, 승격은 다음 단계 catalog에 같은 URL·체크섬 항목을 추가하는 일입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Vagrantfile에서 판 고정

```ruby
Vagrant.configure("2") do |config|
  config.vm.box         = "example/app"
  config.vm.box_url     = "https://boxes.example.com/box-catalog/app/metadata.json"
  config.vm.box_version = "~> 1.1.0"      # 1.1.x 중 최신
  config.vm.box_check_update = true       # vagrant up 때 새 판 알림만, 자동 갱신 안 함
end
```

| 조건                  | 뜻                    |
|-----------------------|-----------------------|
| `"1.1.0"`·`"= 1.1.0"` | 정확히 1.1.0          |
| `"~> 1.1.0"`          | `>= 1.1.0, < 1.2.0`   |
| `"~> 1.1"`            | `>= 1.1, < 2.0`       |
| `">= 1.0, < 1.5"`     | 쉼표로 여러 조건 결합 |
| 지정 안 함            | `>= 0`(가장 높은 판)  |

- 시험에서 `box_version = "~> 1.0.0"`, catalog에 1.0.0·1.0.1·1.1.0이 있을 때 `vagrant box outdated`는 1.0.1을 최신으로 알렸고, `vagrant box update`는 1.0.1만 받았습니다.
- 운영처럼 바뀌면 안 되는 환경은 정확한 판을, 개발 환경은 `~>`로 patch 갱신만 받게 하는 식으로 나눕니다.
- `box_url`은 box가 설치되어 있지 않을 때 받을 곳입니다. 시험은 `vagrant box add`로 catalog에서 box를 먼저 추가한 상태에서 했고, box가 없는 상태에서 `box_url`의 catalog로 처음 받는 동작(`vagrant up`)은 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 갱신과 정리

```bash
vagrant box add https://boxes.example.com/box-catalog/app/metadata.json \
  --box-version 1.1.0 --provider libvirt    # catalog로 추가, 체크섬 확인
vagrant box list                            # example/app (libvirt, 1.1.0, (amd64))
vagrant box outdated                        # 현재 Vagrantfile 조건 기준
vagrant box outdated --global               # 설치된 모든 box, 조건 무시
vagrant box update                          # 현재 환경의 box를 조건 안 최신으로
vagrant box prune --dry-run                 # 지울 이전 판 목록만 출력
vagrant box remove example/app --box-version 1.0.0 --provider libvirt
```

시험 결과:

| 명령                          | 결과                                                          |
|-------------------------------|---------------------------------------------------------------|
| `box add --box-version 1.0.0` | "Calculating and comparing box checksum" 뒤 추가              |
| 체크섬이 틀린 판 추가         | `Expected: ...` `Received: ...`로 거부                        |
| `box outdated --global`       | Vagrantfile 조건과 관계없이 catalog의 가장 높은 판을 알림     |
| `box update --box <이름>`     | 환경 밖 명령이라 조건 없이 가장 높은 판을 받으려 함           |
| 환경 안 `box update`          | 조건(`~> 1.0.0`) 안 최신(1.0.1)만 받음, 이전 판(1.0.0)은 남음 |
| `box prune --dry-run`         | "Would remove example/app docker 1.0.0"                       |

- `vagrant box update`는 새 판을 받을 뿐 실행 중인 VM을 바꾸지 않습니다. 새 판을 쓰려면 VM을 다시 만듭니다.
- Vagrantfile 안에서 실행하는 `box outdated`는 provider가 그 호스트에서 쓸 수 있어야 합니다. provider가 없으면 provider 사용 불가 오류로 끝납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Packer로 판과 체크섬 기록

실제 VM 빌더(qemu, hyperv-iso, virtualbox-iso 등) 뒤에 `vagrant` → `checksum` → `manifest` 후처리기를 이어 씁니다. 빌더 설정은 [Packer 문서](./packer.md)를 따릅니다.

```hcl
variable "version" { type = string }
variable "git_sha" { type = string }

build {
  sources = ["source.qemu.base"]          # 실제 빌더

  post-processors {
    post-processor "vagrant" {
      architecture = "amd64"
      output       = "output/app-${var.version}-{{.Provider}}-{{.Architecture}}.box"
    }
    post-processor "checksum" {
      checksum_types = ["sha256"]
      output         = "output/app-${var.version}.{{.ChecksumType}}"
    }
    post-processor "manifest" {
      output     = "output/packer-manifest.json"
      strip_path = true
      custom_data = {
        version = var.version
        git_sha = var.git_sha
      }
    }
  }
}
```

```bash
packer build -var version=1.1.0 -var git_sha=$(git rev-parse --short HEAD) .
```

manifest 결과(시험 출력 일부):

```json
{
  "builds": [
    {
      "name": "disk",
      "builder_type": "file",
      "build_time": 1795767953,
      "files": [
        { "name": "app-1.1.0-libvirt-amd64.box", "size": 221 },
        { "name": "app-1.1.0.sha256", "size": 93 }
      ],
      "packer_run_uuid": "449ed59d-dac9-10fc-1774-a0282aa3c408",
      "custom_data": { "git_sha": "3f2a9c1", "version": "1.1.0" }
    }
  ],
  "last_run_uuid": "449ed59d-dac9-10fc-1774-a0282aa3c408"
}
```

- `post-processors` 블록 안의 후처리기는 앞 단계 결과를 이어 받습니다. 위 예에서 checksum과 manifest는 box 파일을 대상으로 합니다.
- manifest는 다시 빌드하면 항목을 덧붙이고, `packer build -force`면 비우고 새로 씁니다(시험 확인). CI에서는 빌드마다 새 작업 폴더를 쓰거나 판별로 manifest 파일 이름을 나눕니다.
- checksum 파일은 "해시, 탭, 파일 이름" 한 줄이고 `sha256sum -c`로 확인됩니다. 같은 output 이름으로 다시 빌드하면 줄이 덧붙으므로, 이 파일을 읽는 스크립트는 마지막 줄이나 파일 이름이 맞는 줄을 고릅니다.
- 시험은 VM 빌더를 쓸 수 없어 `file` 빌더 → `shell-local`(box 묶기) → `artifice`(결과물 교체) → `checksum` → `manifest` 순서로 했습니다. `file` 빌더 결과에 `vagrant` 후처리기를 바로 쓰면 plugin v1.1.7이 panic으로 끝났습니다. `vagrant` 후처리기는 실제 VM 빌더 결과와 함께 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. catalog 갱신 스크립트

빌드 뒤 catalog에 새 판을 추가하는 예입니다. 이미 있는 판·provider·아키텍처는 덮어쓰지 않고 실패합니다.

```python
#!/usr/bin/env python3
"""Vagrant box catalog(metadata.json)에 새 판을 추가합니다. 같은 판·provider·아키텍처가 있으면 거부합니다."""
import argparse
import json
import re
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("catalog", type=Path)
    p.add_argument("--name", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--arch", default="amd64")
    p.add_argument("--url", required=True)
    p.add_argument("--sha256", required=True)
    a = p.parse_args()

    if not re.fullmatch(r"\d+\.\d+\.\d+", a.version):
        print(f"error: version must be X.Y.Z: {a.version}", file=sys.stderr)
        return 2
    cat = json.loads(a.catalog.read_text()) if a.catalog.exists() else {"name": a.name, "versions": []}
    entry = next((v for v in cat["versions"] if v["version"] == a.version), None)
    if entry is None:
        entry = {"version": a.version, "providers": []}
        cat["versions"].append(entry)
    for prov in entry["providers"]:
        if prov["name"] == a.provider and prov.get("architecture") == a.arch:
            print(f"error: {a.version} {a.provider} {a.arch} already exists", file=sys.stderr)
            return 1
    entry["providers"].append({
        "name": a.provider, "architecture": a.arch, "default_architecture": True,
        "url": a.url, "checksum_type": "sha256", "checksum": a.sha256,
    })
    cat["versions"].sort(key=lambda v: tuple(int(x) for x in v["version"].split(".")))
    tmp = a.catalog.with_suffix(".tmp")
    tmp.write_text(json.dumps(cat, indent=2) + "\n")
    tmp.replace(a.catalog)
    print(f"added {a.name} {a.version} {a.provider} {a.arch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```bash
V=1.1.0
python3 add_box_version.py metadata.json --name example/app --version $V --provider libvirt \
  --url "https://boxes.example.com/boxes/app/$V/app-$V-libvirt-amd64.box" \
  --sha256 "$(tail -1 output/app-$V.sha256 | cut -f1)"
```

- 시험에서 1.1.0 뒤 1.0.0을 추가해도 판 순서로 정렬됐고, 같은 1.0.0 libvirt를 다시 추가하면 rc=1, `1.0` 같은 판은 rc=2로 거부했습니다.
- 여러 빌드가 동시에 catalog를 고치면 한쪽 변경이 사라질 수 있습니다. catalog 갱신은 한 작업에서 차례로 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. VHDX와 다른 형식

Vagrant를 쓰지 않고 디스크 파일(VHDX, qcow2, VMDK, OVA)을 그대로 배포할 때도 같은 원칙을 씁니다.

```text
images/app/1.1.0/app-1.1.0.vhdx
images/app/1.1.0/app-1.1.0.vhdx.sha256
images/app/1.1.0/packer-manifest.json
```

- 경로에 판 번호를 넣고, 판 폴더는 한 번 올리면 바꾸지 않습니다.
- 체크섬과 manifest를 같은 판 폴더에 함께 둡니다. 받는 쪽은 `sha256sum -c`로 확인한 뒤 씁니다.
- "현재 운영 판"은 별도의 작은 파일(예: `images/app/prod.txt`에 `1.1.0`)이나 배포 설정에서 가리키게 하면, 되돌릴 때 그 값만 바꾸면 됩니다.
- Hyper-V의 VHDX 빌드와 가져오기는 이 문서에서 시험하지 않았습니다. Hyper-V 빌더 설정은 [Packer 문서](./packer.md)의 Hyper-V 절을 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용     | 방법                                               | 기대 결과                      |
|------|---------------|----------------------------------------------------|--------------------------------|
| 1    | 체크섬        | `sha256sum -c app-1.1.0.sha256`                    | `OK`                           |
| 2    | box 구조      | `tar -xzOf <box> metadata.json`                    | `provider` 키 있음             |
| 3    | catalog 문법  | `python3 -m json.tool metadata.json`               | 오류 없음                      |
| 4    | 판 고정 설치  | `vagrant box add <catalog URL> --box-version <판>` | 체크섬 확인 뒤 추가            |
| 5    | 조건 안 갱신  | Vagrantfile 폴더에서 `vagrant box outdated`        | 조건 안 최신 판만 알림         |
| 6    | manifest 기록 | `packer-manifest.json`의 `custom_data`             | 판·commit 값                   |
| 7    | 덮어쓰기 금지 | box 저장소에 같은 경로 다시 올리기                 | 거부(Nexus `allow_once`면 409) |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

| 증상                                      | 원인                                                | 조치                                               |
|-------------------------------------------|-----------------------------------------------------|----------------------------------------------------|
| `The metadata for the box was malformed`  | catalog JSON 문법 오류(체크섬 값에 줄바꿈 등)       | `python3 -m json.tool`로 확인, 체크섬 한 줄만 사용 |
| `Expected: ... Received: ...`             | catalog 체크섬과 파일이 다름                        | 파일을 다시 올리지 말고 새 판으로 빌드             |
| `box update`가 원하지 않는 판을 받으려 함 | `--box`나 `--global`은 Vagrantfile 조건을 보지 않음 | Vagrantfile 폴더에서 `vagrant box update`          |
| 판 문자열 오류                            | `1.0`, `1.0.0-rc1` 등 X.Y.Z가 아님                  | 정수 세 자리로                                     |
| manifest에 예전 빌드가 섞임               | manifest는 덧붙이는 방식                            | 빌드마다 새 폴더, 또는 `-force`                    |
| Packer `vagrant` 후처리기 panic           | 디스크 정보가 없는 결과물(file 빌더 등)에 사용      | 실제 VM 빌더 뒤에 사용                             |
| 공개 box 서비스 접속 실패                 | HCP Vagrant 운영 종료(2026-12-31)                   | box를 직접 호스팅                                  |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [이미지 판 관리와 단계별 승격](../cicd/image_versioning_and_promotion.md) — 원칙
- [컨테이너 이미지 승격](../containers/container_image_promotion.md) — 같은 원칙의 컨테이너판
- [이미지 관리 도구 비교](../cicd/image_management_tools_comparison.md) — HCP Packer, 클라우드 갤러리
- [Packer](./packer.md) · [Vagrant](./vagrant.md) · [Nexus Repository](../cicd/nexus.md)

---

## 참고 자료

- Vagrant: [Box file format](https://developer.hashicorp.com/vagrant/docs/boxes/format) · [Box versioning](https://developer.hashicorp.com/vagrant/docs/boxes/versioning) · [Creating a box repository](https://developer.hashicorp.com/vagrant/docs/boxes/box_repository) · [vagrant box](https://developer.hashicorp.com/vagrant/docs/cli/box) · [HCP Vagrant EOL](https://developer.hashicorp.com/hcp/docs/vagrant/hcp-vagrant-eol) — ★★★☆☆
- Packer: [manifest](https://developer.hashicorp.com/packer/docs/post-processors/manifest) · [checksum](https://developer.hashicorp.com/packer/docs/post-processors/checksum) · [Vagrant post-processor](https://developer.hashicorp.com/packer/integrations/hashicorp/vagrant/latest/components/post-processor/vagrant) — ★★★☆☆

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
