# pidstat - 프로세스별 I/O 통계
<!-- reference: _reference/storage_tools_official_notes.md -->

`pidstat`는 Linux task별 CPU·메모리·디바이스 I/O 등의 통계를 주기적으로 표시하는 sysstat 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`pidstat`는 프로세스별 통계를 샘플링합니다. 시스템 전체 디바이스 상태가 아니라 어떤 프로세스가 I/O를 발생시키는지 확인할 때 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v pidstat
pidstat --help
man pidstat
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션         | 설명                                              |
|--------------|---------------------------------------------------|
| `-d`         | task별 디바이스 I/O 통계를 표시합니다.            |
| `-p PID`     | 지정한 프로세스를 대상으로 합니다.                |
| `-C COMMAND` | 명령 이름으로 프로세스를 선택합니다.              |
| `-h`         | 스크립트 처리에 적합한 한 줄 형식으로 표시합니다. |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
pidstat -d 1 5
pidstat -d -p 1234 1 5
pidstat -d -C postgres 1 5
```

첫 번째 숫자는 샘플링 간격, 두 번째 숫자는 반복 횟수입니다. 프로세스별 읽기·쓰기량과 I/O 지연 관련 열을 함께 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- 프로세스가 짧게 실행되면 샘플 간격에 잡히지 않을 수 있습니다.
- 프로세스별 통계와 디바이스 전체 통계는 `iostat`로 별도 확인합니다.
- 권한과 커널 설정에 따라 일부 task 통계가 제한될 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

프로세스 원인 분석은 `pidstat -d`, 디바이스 병목 분석은 `iostat`, 실시간 프로세스 화면은 `iotop`을 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [man7.org/linux/man-pages/man1/pidstat.1.html](https://man7.org/linux/man-pages/man1/pidstat.1.html) — ★★★☆☆
- 공식 저장소: [github.com/sysstat/sysstat](https://github.com/sysstat/sysstat) — ★★★☆☆

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
