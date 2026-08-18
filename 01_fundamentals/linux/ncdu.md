# ncdu - 대화형 디스크 사용량 분석
<!-- reference: _reference/storage_tools_official_notes.md -->

`ncdu`는 `du`와 유사한 디스크 사용량을 curses 기반 대화형 화면으로 탐색하는 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`ncdu`는 큰 디렉토리를 화면에서 정렬·탐색하며 확인할 수 있습니다. `du`의 결과를 반복해서 입력하지 않고 공간 사용량의 원인을 찾을 때 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v ncdu
ncdu --help
man ncdu
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션               | 설명                                   |
|--------------------|----------------------------------------|
| `-x`               | 다른 파일시스템 경계를 넘지 않습니다.  |
| `-r`               | 읽기 전용 모드로 실행합니다.           |
| `--disable-delete` | 브라우저의 삭제 기능을 비활성화합니다. |
| `--confirm-delete` | 삭제 전 확인을 요구합니다.             |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
ncdu -x /var
ncdu --disable-delete -x /home
ncdu -r -x /data
```

화면에서 디렉토리를 선택하여 하위 항목의 사용량을 확인합니다. 실제 파일시스템을 스캔하는 환경에서는 삭제 기능을 비활성화한 실행을 기본값으로 고려합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

🟡 `ncdu`는 실제 파일 삭제 기능을 제공할 수 있습니다. 운영 환경에서는 `-r` 또는 `--disable-delete`를 사용하고, 삭제 키를 누르기 전에 대상과 확인 메시지를 검토합니다.

- `-x`를 사용하지 않으면 다른 마운트 파일시스템의 사용량이 함께 포함될 수 있습니다.
- 스캔 중 파일이 변경되면 표시된 크기와 현재 크기가 달라질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

빠른 합계 확인은 `du`, 대화형 탐색은 `ncdu`를 사용합니다. 삭제 기능을 차단한 읽기 전용 실행을 우선합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [dev.yorhel.nl/ncdu/man](https://dev.yorhel.nl/ncdu/man) — ★★★☆☆
- 공식 프로젝트: [dev.yorhel.nl/ncdu](https://dev.yorhel.nl/ncdu) — ★★★☆☆

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
