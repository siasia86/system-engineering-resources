# du - 파일·디렉토리 공간 사용량 확인
<!-- reference: _reference/storage_tools_official_notes.md -->

`du`는 지정한 파일과 하위 디렉토리가 사용하는 파일시스템 공간을 추정합니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`du`는 디렉토리별 사용량을 내려가며 확인하는 기본 도구입니다. `df`에서 공간 부족이 발견되었을 때 큰 디렉토리와 파일을 찾는 데 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v du
du --help
man du
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션            | 설명                                |
|-----------------|-------------------------------------|
| `-h`            | 사람이 읽기 쉬운 단위를 사용합니다. |
| `-s`            | 각 인수의 합계만 표시합니다.        |
| `-x`            | 다른 파일시스템을 건너뜁니다.       |
| `--max-depth=N` | 지정한 깊이까지만 표시합니다.       |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
du -xh --max-depth=1 /var
du -xsh /var/log
du -xh --max-depth=1 /home | sort -h
```

`--max-depth=1`은 대상 디렉토리 바로 아래 수준의 비교에 적합합니다. 다른 파일시스템이 포함될 수 있는 경로에서는 `-x`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- 권한이 없는 디렉토리는 경고와 함께 일부 결과가 누락될 수 있습니다.
- 파일이 생성·삭제되는 동안 실행하면 결과가 측정 시점에 따라 달라집니다.
- 마운트 경계를 넘지 않아야 하는 경우 `-x`를 명시합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

`df`로 파일시스템 부족을 확인한 뒤 `du -xh --max-depth=1`로 원인 디렉토리를 좁힙니다. 대화형 분석은 `ncdu`가 적합합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [GNU Coreutils du invocation](https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html) — ★★★☆☆

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
