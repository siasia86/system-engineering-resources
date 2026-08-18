# blkid - 블록 장치 식별 정보 조회
<!-- reference: _reference/storage_tools_official_notes.md -->

`blkid`는 블록 장치의 파일시스템 유형, LABEL, UUID 같은 콘텐츠 메타데이터를 식별하는 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`blkid`는 장치의 파일시스템 식별 정보를 조회합니다. `/etc/fstab`에 사용할 UUID와 파일시스템 유형을 확인할 때 사용합니다.

> LABEL: 관리자가 지정한 사람이 읽기 쉬운 파일시스템 이름입니다. UUID와 달리 동일한 LABEL이 여러 장치에 존재할 수 있으므로 장치 식별의 유일성을 따로 확인해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v blkid
blkid --help
man blkid
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션        | 설명                       |
|-------------|----------------------------|
| `-o FORMAT` | 출력 형식을 선택합니다.    |
| `-s TAG`    | 지정한 태그만 표시합니다.  |
| `-L LABEL`  | LABEL로 장치를 조회합니다. |
| `-U UUID`   | UUID로 장치를 조회합니다.  |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
sudo blkid
sudo blkid /dev/sdX1
sudo blkid -o export /dev/sdX1
sudo blkid -s UUID -o value /dev/sdX1
```

장치 경로 `/dev/sdX1`은 실제 대상 장치로 바꾸기 전에 `lsblk`로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- 장치 경로를 잘못 지정하지 않도록 실행 전 `lsblk`와 `findmnt` 결과를 대조합니다.
- 권한과 캐시 상태에 따라 일반 조회와 저수준 탐지 결과가 다를 수 있습니다.
- `blkid`는 장치 건강 상태나 성능을 측정하는 도구가 아닙니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

파일시스템 식별 정보가 필요하면 `blkid`, 장치 계층은 `lsblk`, 현재 마운트 상태는 `findmnt`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [man7.org/linux/man-pages/man8/blkid.8.html](https://man7.org/linux/man-pages/man8/blkid.8.html) — ★★★☆☆

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
