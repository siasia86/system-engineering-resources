---
name: vagrant-box-versioning-official-notes
description: Vagrant 2.4.9 box 판 관리(catalog metadata, box_version 조건, box 명령)와 HCP Vagrant 종료 일정, 컨테이너 시험 결과 정리.
tags:
  - vagrant
  - box
  - versioning
last_checked: 2026-11-27
sources:
  - https://developer.hashicorp.com/vagrant/docs/boxes/format
  - https://developer.hashicorp.com/vagrant/docs/boxes/versioning
  - https://developer.hashicorp.com/vagrant/docs/boxes/box_repository
  - https://developer.hashicorp.com/vagrant/docs/vagrantfile/machine_settings
  - https://developer.hashicorp.com/vagrant/docs/cli/box
  - https://developer.hashicorp.com/hcp/docs/vagrant/hcp-vagrant-eol
  - https://api.releases.hashicorp.com/v1/releases/vagrant
---

# Vagrant box 판 관리 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- releases API 최신 2.4.9(2025-08-21), license_class `oss`. GitHub 저장소 라이선스 MIT.
- 문서 판 선택기도 v2.4.9(latest). 페이지 갱신일 표시 없음.

## 2. box와 catalog

- box 파일: tar, tar.gz, zip. VM 파일, `metadata.json`(필수, 최소 `provider` 키), 선택 `info.json`·`Vagrantfile`. 코어가 쓰는 키는 `provider`, `architecture`.
- Box Catalog Metadata: `name`, `description`, `versions[]` → `version`, `providers[]` → `name`, `url`, `checksum_type`, `checksum`, `architecture`, `default_architecture`. 파일 경로나 URL로 `vagrant box add`에 직접 넘길 수 있음.
- checksum 종류: md5, sha1, sha256, sha384, sha512.
- 판 형식: "X.Y.Z where X, Y, and Z are all positive integers". pre-release 불가.
- 조건 연산자: `=`, `>`, `<`, `>=`, `<=`, `~>`, 쉼표로 결합. `~> 1.1.5`는 `>= 1.1.5, < 1.2.0`.

## 3. Vagrantfile 설정

- `config.vm.box_version` 기본 `>= 0`. `config.vm.box_url`은 문자열 또는 배열, 차례로 시도.
- `config.vm.box_check_update` 기본 true, `vagrant up`마다 확인. 자동으로 내려받지는 않음.
- `config.vm.box_download_checksum`·`_type`, `box_download_client_cert`, `box_download_ca_cert`, `box_download_options`(curl 옵션 이름 map).
- `config.vm.box_architecture` 기본 `:auto`.

## 4. 명령

- `box add`: catalog 주소면 `--box-version`(정확한 판 또는 조건) 사용. box 파일 직접 주소면 `--name` 필요, 판·갱신 기능 없음. HTTP catalog는 기본 인증 지원. 중단된 내려받기는 24시간 이어 받기.
- `box outdated`(`--global`, `--force`로 1시간 캐시 무시), `box update`(`--box`, `--provider`), `box prune`(`--dry-run`, `--name`, `--provider`, `--force`, `--keep-active-boxes`), `box remove`(`--box-version`, `--all`, `--force`).

## 5. HCP Vagrant 종료

- 종료 안내 표: 새 box·registry 생성 종료 2026-10-01, 지원·유지 보수 종료 2026-11-02, 운영 종료 2026-12-31. box는 다른 곳으로 옮겨 직접 호스팅해야 함.
- 다른 Vagrant 문서 페이지는 "end of operations date of December 31, 2026"만 적음.

## 6. 시험 (debian:13-slim 컨테이너, Vagrant 2.4.9 deb, sha256 일치)

- 정적 HTTP 서버의 catalog로 `box add --box-version 1.0.0` 성공, "Calculating and comparing box checksum" 뒤 추가.
- checksum이 틀린 판: `Expected: 0000` `Received: <sha256>`로 거부.
- `box outdated --global`과 `box update --box`는 Vagrantfile 조건을 보지 않고 catalog 최신 판을 고름(체크섬이 깨진 1.2.0을 받으려다 실패).
- docker provider box로 환경 시험: `box_version = "~> 1.0.0"`이면 `box outdated`가 1.0.1을 최신으로 알리고 `box update`가 1.0.1만 받음(1.1.0 무시). 이전 판 1.0.0은 남고 `prune --dry-run`이 "Would remove example/app docker 1.0.0" 출력.
- libvirt provider가 없는 환경에서는 Vagrantfile 기반 `box outdated`가 provider 사용 불가 오류로 실패.
