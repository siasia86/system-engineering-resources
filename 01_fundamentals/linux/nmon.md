# nmon - 시스템 자원 관찰
<!-- reference: _reference/storage_tools_official_notes.md -->

`nmon`은 CPU, 메모리, 디스크, 네트워크, 파일시스템과 프로세스 관련 시스템 통계를 인터랙티브 화면 또는 파일로 표시합니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`nmon`은 여러 시스템 자원을 한 화면에서 관찰하는 시스템 관리자용 도구입니다. 화면 키와 기능은 배포판·빌드에 따라 다를 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v nmon
nmon -h
man nmon
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션 또는 키 | 설명                                        |
|--------------|---------------------------------------------|
| `-s SECONDS` | 화면 갱신 간격을 지정합니다.                |
| `-c COUNT`   | 갱신 횟수를 지정합니다.                     |
| `-f`         | 스프레드시트 형식의 기록 모드를 사용합니다. |
| `d`          | 디스크 화면을 선택합니다.                   |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
nmon
nmon -s 30 -c 120
nmon -f -s 30 -c 120
```

인터랙티브 화면에서 `d` 키로 디스크 통계를 확인할 수 있습니다. 실제 키와 출력 열은 설치된 버전의 도움말을 우선합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- 기록 모드는 파일을 생성하므로 출력 경로와 보존 기간을 확인합니다.
- 종합 화면의 수치만으로 원인을 단정하지 않고 `iostat`, `pidstat`와 교차 확인합니다.
- 시스템 자원 수집 정보에는 운영 정보가 포함될 수 있으므로 기록 파일의 권한을 제한합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

빠른 종합 관찰은 `nmon`, 디스크 세부 통계는 `iostat`, 프로세스별 I/O는 `pidstat`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 프로젝트: [nmon.sourceforge.net/pmwiki.php](https://nmon.sourceforge.net/pmwiki.php) — ★★★☆☆

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
