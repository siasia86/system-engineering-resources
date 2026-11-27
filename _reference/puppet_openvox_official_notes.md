---
name: puppet-openvox-official-notes
description: 오픈소스 Puppet 배포 변경(2024-11 공지), Puppet Core 25노드 무료, OpenVox 8·9 판과 패키지, 컨테이너 시험 결과 정리.
tags:
  - puppet
  - openvox
  - configuration-management
last_checked: 2026-11-27
sources:
  - https://www.puppet.com/blog/open-source-puppet-updates-2025
  - https://puppet.com/products/puppet-core
  - https://voxpupuli.org/openvox/
  - https://voxpupuli.org/openvox/install/
  - https://github.com/OpenVoxProject/openvox/releases
  - https://github.com/puppetlabs/puppet
---

# Puppet·OpenVox 공식 자료 참조 노트

## 1. Puppet 배포 변경

- Puppet 블로그(2024-11-07, "early 2025" 계획): 새 바이너리·패키지는 "a private, hardened, and controlled location". "There will be no license changes for the open source version of Puppet."(Apache 2.0). 개발자는 "free access to our hardened Puppet releases (up to 25 nodes)", 그 이상은 상용 라이선스.
- Puppet Core 제품 페이지: "a hardened, vendor-backed version of Puppet", "free Developer License for use on up to 25 nodes".
- GitHub `puppetlabs/puppet`: 마지막 커밋 2024-12-11, 마지막 릴리스 8.10.0·7.34.0(2024-10-22), 라이선스 Apache-2.0.
- Puppet Core의 현재 판은 확인하지 않음(미확인).

## 2. OpenVox

- 소개: "the modern open source implementation of the world's most capable configuration management platform", "soft-fork ... maintain downstream compatibility for as long as we are able".
- 설치 문서: "As of release 8.11, OpenVox is functionally equivalent to Puppet; the command names are the same", Puppet과 같은 시스템에 함께 설치 불가.
- 패키지: `openbolt`, `openvox-agent`, `openvox-server`, `openvoxdb`, `openvoxdb-termini`. 저장소 패키지 `openvox9-release`(기본), `openvox8-release`(EOL까지 중요·보안 수정만). apt.voxpupuli.org, yum.voxpupuli.org.
- 판(GitHub 릴리스): 9.5.0·8.34.0(2026-11-19), 9.4.1·8.33.1(11-18), 9.4.0·8.33.0(11-13). 저장소 라이선스 Apache-2.0(voxpupuli.org/license는 웹사이트 라이선스라 근거로 쓰지 않음).
- 9.0.0(첫 9 계열): Ruby 4.0.7(8.29.0은 3.2.11), OpenSSL 3.5.9, OpenFact 6.2.1. 제거: `--configprint`, `pluginsync`, hiera indirector, `data_binding_terminus` 등. 기본값 변경: `server` 기본값 없음, `reports` 기본 `none`, `preprocess_deferred` 기본 true. 지원 중단: EL 7, Amazon Linux 2, Fedora 42, Ubuntu 25.04. 9.x 서버는 `openvox-agent >= 9.0.0` 필요.

## 3. 컨테이너 시험 (2026-11-27, Ubuntu 24.04, openvox8-release)

- `openvox-agent 8.34.0-1+ubuntu24.04` 설치, `puppet --version` 8.34.0, 명령 경로 `/opt/puppetlabs/bin`.
- `puppet parser validate` 정상 0. 문법 오류: `Syntax error at 'ensure' (file: /w/bad.pp, line: 1, column: 13)`.
- `puppet apply --noop`: `(noop)` 표시와 `Would have triggered 'refresh' from 2 events`.
- `--detailed-exitcodes`: 첫 적용 2, 재적용 0.
- `facter os.name` Ubuntu, `os.release.full` 24.04.
- 미실행: openvox9, openvox-server, openvoxdb, 여러 노드.
