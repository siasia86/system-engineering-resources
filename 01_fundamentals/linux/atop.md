# atop - 종합 시스템·프로세스 모니터링
<!-- reference: _reference/storage_tools_official_notes.md -->

`atop`은 CPU, 메모리, 스왑, 디스크, 네트워크와 프로세스 상태를 종합적으로 표시하고 활동을 로그로 기록할 수 있는 모니터링 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`atop`은 시스템 전체와 프로세스별 자원 사용량을 시간축으로 관찰합니다. 공식 저장소의 최신 릴리스는 `v2.13.0`입니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v atop
atop -V
man atop
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션       | 설명                                         |
|------------|----------------------------------------------|
| `-V`       | 버전 정보를 표시합니다.                      |
| `-w FILE`  | 원시 시스템 활동 데이터를 파일에 기록합니다. |
| `-r FILE`  | 기록된 활동 데이터를 읽습니다.               |
| `INTERVAL` | 화면 갱신 간격을 초 단위로 지정합니다.       |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
atop
atop 5
atop -w /var/tmp/atop.raw 60
```

기록 파일을 재생하는 옵션과 기본 로그 경로는 설치 버전의 `atop --help`와 매뉴얼을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- 로그 기록은 저장공간과 수집 주기에 영향을 줍니다.
- 화면의 디스크 통계와 `iostat`의 디바이스 통계를 함께 비교하면 원인 범위를 좁힐 수 있습니다.
- 기록 파일에는 프로세스와 시스템 운영 정보가 포함될 수 있으므로 접근 권한을 제한합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

단기 종합 관찰은 `atop`, 장기 사건 재구성은 로그 기록 기능, 디바이스 세부 분석은 `iostat`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 저장소: [github.com/Atoptool/atop](https://github.com/Atoptool/atop) — ★★★☆☆

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
