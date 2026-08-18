# lsblk - 블록 장치 계층 확인
<!-- reference: _reference/storage_tools_official_notes.md -->

`lsblk`는 Linux 블록 장치와 파티션의 계층 구조, 파일시스템, UUID, 마운트 지점을 목록으로 확인하는 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`lsblk`는 블록 장치를 트리 형태로 표시합니다. 디스크, 파티션, 장치 유형과 파일시스템 연결 상태를 한 번에 확인할 때 사용합니다.

> UUID(Universally Unique Identifier): 파일시스템이나 장치를 식별하기 위해 사용하는 고유 식별자입니다. `/etc/fstab`에서 장치를 이름 대신 식별할 때 사용할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v lsblk
lsblk --help
man lsblk
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션      | 설명                           |
|-----------|--------------------------------|
| `-f`      | 파일시스템 정보를 표시합니다.  |
| `-o LIST` | 표시할 열을 선택합니다.        |
| `-p`      | 장치의 전체 경로를 표시합니다. |
| `-J`      | JSON 형식으로 출력합니다.      |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
lsblk
lsblk -f
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
lsblk -J > lsblk.json
```

`-o`의 열 이름은 설치된 util-linux 버전의 `lsblk --help`와 매뉴얼에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- 장치 목록만으로 실제 I/O 상태나 장치 건강 상태를 판단하지 않습니다.
- 스크립트에서는 장치 이름의 순서에 의존하지 않고 `-o`로 필요한 열을 명시합니다.
- 장치 변경 직후에는 udev 상태와 마운트 정보를 함께 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

`lsblk`는 장치·파티션·파일시스템 관계를 빠르게 확인하는 첫 단계 도구입니다. 마운트 옵션은 `findmnt`, 식별자만 필요하면 `blkid`를 함께 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [man7.org/linux/man-pages/man8/lsblk.8.html](https://man7.org/linux/man-pages/man8/lsblk.8.html) — ★★★☆☆

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
