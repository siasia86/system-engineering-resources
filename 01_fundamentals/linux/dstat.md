# dstat - 통합 시스템 자원 통계
<!-- reference: _reference/storage_tools_official_notes.md -->

`dstat`는 CPU, 디스크, 네트워크, 페이징과 메모리 통계를 한 화면에 표시하는 자원 통계 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`dstat`는 여러 시스템 자원 통계를 같은 시간축으로 관찰하는 데 사용합니다. 공식 저장소는 `v0.7.4` 릴리스 이후 archived 상태이므로 배포판과 설치 버전에 차이가 있을 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v dstat
dstat --version
dstat --help
```

실행 파일과 배포판 패키지의 기능이 다를 수 있으므로 실제 설치 버전의 도움말을 우선합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션 | 설명                        |
|------|-----------------------------|
| `-c` | CPU 통계를 선택합니다.      |
| `-d` | 디스크 통계를 선택합니다.   |
| `-n` | 네트워크 통계를 선택합니다. |
| `-m` | 메모리 통계를 선택합니다.   |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
dstat
dstat 1 5
dstat --help
```

플러그인과 옵션은 설치 버전에 따라 다를 수 있으므로 특정 조합을 자동화하기 전에 `dstat --help`를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

🟡 공식 저장소가 archived 상태이므로 신규 환경에서는 배포판 패키지의 유지 상태와 대체 도구를 함께 검토합니다.

- 통합 화면의 수치는 세부 원인 분석보다 상황 파악에 적합합니다.
- 디바이스 확장 통계는 `iostat`, 프로세스별 I/O는 `pidstat`로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

`dstat`는 여러 자원의 추세를 한 화면에서 보는 도구입니다. 유지 상태와 설치 버전을 확인한 뒤 제한된 범위에서 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 저장소: [github.com/dstat-real/dstat](https://github.com/dstat-real/dstat) — ★★★☆☆

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
