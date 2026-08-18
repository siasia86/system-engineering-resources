# df - 파일시스템 공간 확인
<!-- reference: _reference/storage_tools_official_notes.md -->

`df`는 파일시스템별 전체 공간, 사용 공간, 가용 공간과 사용률을 표시합니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`df`는 지정한 파일이 속한 파일시스템 또는 마운트된 파일시스템의 공간 사용량을 확인합니다. 서버의 디스크 부족 여부를 빠르게 확인할 때 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v df
df --help
man df
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션      | 설명                                 |
|-----------|--------------------------------------|
| `-h`      | 사람이 읽기 쉬운 단위를 사용합니다.  |
| `-T`      | 파일시스템 유형을 표시합니다.        |
| `-i`      | 블록 대신 inode 사용량을 표시합니다. |
| `-x TYPE` | 지정한 파일시스템 유형을 제외합니다. |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
df -h
df -hT
df -ih
df -hT /var
```

용량이 충분해 보여도 inode가 고갈되면 파일을 만들 수 없으므로 `df -ih`를 함께 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- `df`는 파일시스템 관점의 사용량이고 `du`는 디렉토리 트리를 순회한 추정치이므로 값이 다를 수 있습니다.
- 삭제된 파일을 프로세스가 계속 열고 있으면 `df`에 공간이 즉시 반환되지 않을 수 있습니다.
- 예약 블록, 스냅샷, 파일시스템 구현에 따라 사용량 해석이 달라질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

파일시스템 전체 공간과 inode 상태는 `df -hT`와 `df -ih`로 확인합니다. 특정 디렉토리의 원인을 찾을 때는 `du` 또는 `ncdu`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [GNU Coreutils df invocation](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html) — ★★★☆☆

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
