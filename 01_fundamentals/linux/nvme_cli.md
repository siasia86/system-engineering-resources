# nvme-cli - NVMe 장치 관리와 로그 확인
<!-- reference: _reference/storage_tools_official_notes.md -->

`nvme` 명령은 NVMe 장치의 컨트롤러·네임스페이스 정보와 로그를 조회하고 관리하는 nvme-cli 도구입니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 명령어](#3-주요-명령어) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)             |

---

## 1. 개요

`nvme-cli`는 NVMe 장치와 네임스페이스를 조회하고 표준·벤더 로그를 확인하는 명령행 도구입니다.

> NVMe(Non-Volatile Memory Express): 비휘발성 메모리 저장장치를 위해 설계된 호스트 인터페이스와 프로토콜입니다. SATA 장치와 다른 장치 경로·명령 체계를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v nvme
nvme version
nvme help
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 명령어

| 명령어             | 설명                                        |
|--------------------|---------------------------------------------|
| `nvme list`        | NVMe 장치와 네임스페이스 목록을 표시합니다. |
| `nvme list-subsys` | NVMe subsystem 정보를 표시합니다.           |
| `nvme id-ctrl`     | 컨트롤러 식별 정보를 조회합니다.            |
| `nvme id-ns`       | 네임스페이스 식별 정보를 조회합니다.        |
| `nvme smart-log`   | SMART 로그를 조회합니다.                    |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
sudo nvme list
sudo nvme list-subsys
sudo nvme id-ctrl /dev/nvme0
sudo nvme smart-log /dev/nvme0
```

세부 명령어의 인수와 지원 여부는 `nvme help COMMAND`와 공식 `Documentation/`을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

🟡 `nvme`에는 로그 조회 외에 장치 상태와 설정에 영향을 줄 수 있는 명령도 있습니다. 운영 장치에서는 조회 명령과 변경 명령을 구분합니다.

- 컨트롤러 경로와 네임스페이스 경로를 혼동하지 않습니다.
- 벤더 전용 로그는 장치 모델과 플러그인 지원 여부에 따라 달라질 수 있습니다.
- NVMe 상태 확인은 `smartctl` 결과와 함께 비교할 수 있지만 출력 항목의 의미는 장치 문서를 우선합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

장치 목록은 `nvme list`, 컨트롤러·네임스페이스 정보는 `id-ctrl`·`id-ns`, 건강 관련 정보는 `smart-log`로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 저장소: [github.com/linux-nvme/nvme-cli](https://github.com/linux-nvme/nvme-cli) — ★★★☆☆
- 공식 명령어 문서: [nvme-cli Documentation](https://github.com/linux-nvme/nvme-cli/tree/master/Documentation) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-18

**마지막 업데이트**: 2026-08-18

© 2026 siasia86. Licensed under CC BY 4.0.
