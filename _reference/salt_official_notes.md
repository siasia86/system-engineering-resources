---
name: salt-official-notes
description: Salt 3008.5·3007.17·3006.30 판, 지원 주기 표, onedir 압축판 체크섬, 컨테이너 시험 결과 정리.
tags:
  - salt
  - configuration-management
last_checked: 2026-11-27
sources:
  - https://github.com/saltstack/salt/releases
  - https://docs.saltproject.io/salt/install-guide/en/latest/topics/salt-version-support-lifecycle.html
  - https://saltproject.io/blog/2026-05-27-salt-3008-0-available/
  - https://packages.broadcom.com/artifactory/saltproject-generic/onedir/
---

# Salt 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- GitHub 릴리스: v3008.5(2026-10-26), v3008.4(10-24), v3007.17·v3006.30(10-27). GitHub "latest" 표시는 v3007.17이라 판 판단에 쓰지 않음.
- 저장소 라이선스 Apache-2.0.
- 3008.0 LTS 공지(2026-05-27): "Salt 3008.0 is a Long-Term Support (LTS) release." 설치 경로는 PyPI와 Broadcom Artifactory(deb, rpm, mac, win, onedir). "it is highly recommended to upgrade your Salt Master first."

## 2. 지원 주기 (공식 표)

| 판       | 출시           | 일반 지원 끝 | CVE·중대 수정 끝 |
|----------|----------------|--------------|------------------|
| 3008 LTS | May 27, 2026   | June, 2027   | June, 2028       |
| 3007 STS | March 6, 2024  | June, 2026   | 표에 없음        |
| 3006 LTS | April 18, 2023 | July, 2026   | June, 2027       |

- 정책: LTS는 1년에 한 번, 일반 지원 최소 1년 + CVE·중대 수정 1년 더. STS는 다음 LTS 또는 STS 출시까지.

## 3. 컨테이너 시험 (2026-11-27)

- `python:3.13-slim`에서 `pip install salt==3008.5`: `timelib` wheel 빌드 실패로 설치 안 됨.
- Debian 13에 onedir `salt-3008.5-onedir-linux-x86_64.tar.xz` 사용. sha256 `3bbc89d18ff1cef340bfe662d0e973db8387c9affbb0633df1645725bb63786e`(같은 위치 `.sha256` 파일, Artifactory 저장소 API와 일치). `salt-call --version` → `3008.5 (Argon)`.
- `salt-call --local state.apply test=True`: `Result: None`. 적용: `Succeeded: 2 (changed=2)`, pillar 값 반영. 재적용: `Succeeded: 2`.
- `grains.item os osrelease`: Debian, 13.
- 잘못된 YAML: `Rendering SLS 'base:web' failed: mapping values are not allowed in this context`.
- 미실행: master·minion 구성, salt-ssh, reactor, 패키지 저장소 설치.
