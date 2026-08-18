# findmnt - 마운트 정보 조회
<!-- reference: _reference/storage_tools_official_notes.md -->

`findmnt`는 현재 마운트된 파일시스템과 마운트 옵션을 `/proc/self/mountinfo`, `/etc/mtab`, `/etc/fstab`에서 조회하는 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`findmnt`는 마운트 지점, 소스 장치, 파일시스템 유형과 옵션을 검색합니다. 특정 경로가 어떤 파일시스템에 속하는지 확인할 때 유용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v findmnt
findmnt --help
man findmnt
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션        | 설명                                     |
|-------------|------------------------------------------|
| `-t TYPE`   | 지정한 파일시스템 유형을 검색합니다.     |
| `-T PATH`   | 경로에 해당하는 파일시스템을 검색합니다. |
| `-S SOURCE` | 소스 장치 또는 소스를 검색합니다.        |
| `-o LIST`   | 표시할 열을 선택합니다.                  |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
findmnt
findmnt -T /var
findmnt -t ext4
findmnt -no SOURCE,FSTYPE,OPTIONS /var
```

`-n`은 헤더를 생략하고, `-o`는 필요한 열만 표시하도록 합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- `/etc/fstab`의 설정과 현재 실제 마운트 상태를 혼동하지 않습니다.
- 컨테이너나 mount namespace 안에서는 실행 위치에 따라 결과가 달라질 수 있습니다.
- 마운트 해제나 옵션 변경은 `findmnt`가 수행하는 작업이 아니며 별도 명령의 영향 범위를 확인해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

특정 경로의 실제 파일시스템과 마운트 옵션을 확인하려면 `findmnt -T PATH`를 사용합니다. 장치·파티션 계층은 `lsblk`, 식별자는 `blkid`로 보완합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [man7.org/linux/man-pages/man8/findmnt.8.html](https://man7.org/linux/man-pages/man8/findmnt.8.html) — ★★★☆☆

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
