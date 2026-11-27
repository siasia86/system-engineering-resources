---
name: packer-manifest-official-notes
description: Packer 1.16.3 manifest·checksum·vagrant 후처리기 옵션과 HCP Packer 버킷·채널·revoke, 컨테이너 시험 결과 정리.
tags:
  - packer
  - manifest
  - hcp-packer
last_checked: 2026-11-27
sources:
  - https://developer.hashicorp.com/packer/docs/post-processors/manifest
  - https://developer.hashicorp.com/packer/docs/post-processors/checksum
  - https://developer.hashicorp.com/packer/integrations/hashicorp/vagrant/latest/components/post-processor/vagrant
  - https://developer.hashicorp.com/packer/docs/templates/hcl_templates/blocks/build/hcp_packer_registry
  - https://developer.hashicorp.com/hcp/docs/packer
  - https://developer.hashicorp.com/hcp/docs/packer/manage/channel
  - https://developer.hashicorp.com/hcp/docs/packer/manage/revoke-restore
  - https://developer.hashicorp.com/hcp/docs/packer/manage/ancestry
  - https://api.releases.hashicorp.com/v1/releases/packer
---

# Packer manifest·HCP Packer 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- Packer 1.16.3(2026-11-25), license_class `oss`. vagrant 플러그인 v1.1.7(`packer init`으로 설치됨).

## 2. 후처리기

- manifest: `output`(기본 `packer-manifest.json`), `strip_path`, `strip_time`, `custom_data`(template 변수 사용 가능). 구조: `builds[]`(`name`, `builder_type`, `build_time`, `files[{name,size}]`, `artifact_id`, `packer_run_uuid`, `custom_data`), `last_run_uuid`. 다시 실행하면 덧붙이고, `-force`면 비움.
- checksum: `checksum_types`(비우면 md5; md5, sha1, sha224, sha256, sha384, sha512), `output` 기본 `packer_{{.BuildName}}_{{.BuilderType}}_{{.ChecksumType}}.checksum`.
- vagrant: `output` 기본 `packer_{{.BuildName}}_{{.Provider}}_{{.Architecture}}.box`, `architecture`, `compression_level`(기본 6), `include`, `keep_input_artifact`, `provider_override`, `vagrantfile_template`. 지원: AWS, Azure, DigitalOcean, Docker, File, Hyper-V, LXC, Parallels, QEMU, VirtualBox, VMware.

## 3. HCP Packer

- `hcp_packer_registry` 블록(1.7.7부터): `bucket_name`, `description`(255자), `bucket_labels`, `build_labels`. `HCP_CLIENT_ID`·`HCP_CLIENT_SECRET`이 없으면 빌드 실패.
- 판(version)은 fingerprint로 구분, 같은 fingerprint의 완료된 판이 있으면 빌드 실패.
- 채널: 완료된 판만 지정 가능, `latest` 채널은 자동 관리. 채널을 바꿔도 사용처에 알림이 가지 않음.
- revoke: 취소된 판을 참조하는 템플릿은 빌드 불가, 예약 취소는 Standard. 복원해도 채널에 자동으로 다시 넣지 않음.
- ancestry: Packer 1.8.2 이상, 부모가 채널에 있어야 함. 상태 `Up to date`·`Out of date`·`Undetermined`.
- 데이터 소스: Packer `hcp-packer-version`·`hcp-packer-artifact`, Terraform `hcp_packer_artifact`.
- 등급: Essentials와 유료 Standard. 버킷·판 수 한도와 금액은 읽은 페이지에 없음(미확인).

## 4. 시험 (debian:13-slim, Packer 1.16.3 zip sha256 일치)

- `file` 빌더 결과에 `vagrant` 후처리기 `provider_override = "libvirt"`를 주면 플러그인이 panic(`libvirt.go:71`, nil 변환). 실제 디스크 정보를 주는 빌더가 필요.
- `shell-local`로 box를 묶고 `artifice`로 결과물을 바꾼 뒤 `checksum`·`manifest` 연결: 두 판 빌드 시 manifest에 2건, `custom_data`에 판·commit 기록, `-force` 실행 뒤 1건.
- checksum 파일은 "해시<탭>파일 이름" 한 줄이며 `sha256sum -c`로 확인됨. 같은 output 이름으로 다시 빌드하면 줄이 덧붙음.
