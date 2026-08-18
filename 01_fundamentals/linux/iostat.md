# iostat - 디바이스 I/O 통계
<!-- reference: _reference/storage_tools_official_notes.md -->

`iostat`는 CPU와 디바이스·파티션의 I/O 처리량 및 확장 통계를 표시하는 sysstat 도구입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`iostat`는 디바이스별 읽기·쓰기 처리량, 요청 수, 대기와 사용률을 확인하는 기본 도구입니다. 프로세스가 아니라 블록 디바이스 관점의 병목을 분석합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v iostat
iostat --help
man iostat
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션       | 설명                                        |
|------------|---------------------------------------------|
| `-x`       | 확장 디바이스 통계를 표시합니다.            |
| `-z`       | 활동이 없는 디바이스를 생략합니다.          |
| `-p [ALL]` | 디바이스 파티션 통계를 표시합니다.          |
| `-y`       | 첫 번째 부팅 이후 평균 보고서를 생략합니다. |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
iostat -xz 1 5
iostat -p ALL -xz 1 5
iostat -y -xz 1 5
```

`await`, `avgqu-sz`, `%util` 같은 열은 확장 디바이스 통계에서 확인합니다. 측정 전 첫 번째 보고서가 부팅 이후 누적값인지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

- `%util` 하나만으로 저장장치 성능을 단정하지 않고 처리량·대기시간·큐와 함께 해석합니다.
- 가상화 환경에서는 게스트 통계와 호스트 저장장치 통계가 다를 수 있습니다.
- 샘플링 간격과 workload를 함께 기록해야 결과를 비교할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

디바이스 전체 상태는 `iostat -xz`, 특정 프로세스 원인은 `pidstat -d`와 `iotop`으로 교차 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [man7.org/linux/man-pages/man1/iostat.1.html](https://man7.org/linux/man-pages/man1/iostat.1.html) — ★★★☆☆
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
