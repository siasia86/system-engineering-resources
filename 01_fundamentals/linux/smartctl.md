# smartctl - 저장장치 SMART 상태 확인
<!-- reference: _reference/storage_tools_official_notes.md -->

`smartctl`은 ATA/SATA, SCSI/SAS, NVMe 장치의 SMART 정보와 건강 상태를 조회·모니터링하는 smartmontools 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`smartctl`은 장치가 제공하는 SMART 정보, 온도와 오류 관련 로그를 조회합니다. 장치의 건강 상태를 판단할 때 한 번의 상태 코드만 보지 않고 상세 로그와 추세를 함께 확인합니다.

> SMART(Self-Monitoring, Analysis and Reporting Technology): 저장장치가 자체 상태와 오류 관련 정보를 보고하는 기능입니다. 장치·인터페이스에 따라 지원 항목과 의미가 달라질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v smartctl
smartctl --version
smartctl --help
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션     | 설명                                             |
|----------|--------------------------------------------------|
| `-H`     | 장치 건강 상태를 표시합니다.                     |
| `-a`     | 사용 가능한 SMART 정보와 장치 정보를 표시합니다. |
| `-i`     | 장치 식별 정보를 표시합니다.                     |
| `-l LOG` | 지정한 로그를 표시합니다.                        |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
sudo smartctl -H /dev/sdX
sudo smartctl -a /dev/sdX
sudo smartctl -i /dev/sdX
```

장치 유형이나 뒤의 컨트롤러에 따라 추가 옵션이 필요할 수 있으므로 `smartctl --help`와 장치별 매뉴얼을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- SMART 결과는 장치 모델과 연결 방식에 따라 지원 범위가 다릅니다.
- 건강 상태가 정상이어도 파일시스템 오류나 애플리케이션 장애가 없다는 뜻은 아닙니다.
- 장치 경로를 잘못 지정하지 않도록 `lsblk`와 `nvme list` 결과를 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

일반적인 건강 상태는 `-H`, 상세 정보는 `-a`로 확인합니다. NVMe 전용 로그는 `nvme smart-log`로 교차 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 저장소: [github.com/smartmontools/smartmontools](https://github.com/smartmontools/smartmontools) — ★★★☆☆
- 공식 프로젝트: [smartmontools.org](https://www.smartmontools.org/) — ★★★☆☆

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
