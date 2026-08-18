# fio - 통제된 블록 I/O 성능 테스트
<!-- reference: _reference/storage_tools_official_notes.md -->

`fio`는 블록 I/O 부하를 생성하고 처리량, IOPS, 지연시간을 측정하는 Flexible I/O Tester입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`fio`는 블록 크기, 읽기·쓰기 비율, 큐 깊이, 작업자 수, 접근 패턴과 실행 시간을 제어하여 저장장치 성능을 비교합니다.

> IOPS(Input/Output Operations Per Second): 1초 동안 완료한 I/O 요청 수입니다. 요청 크기와 접근 패턴에 따라 처리량과 지연시간이 달라지므로 조건을 함께 기록해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v fio
fio --version
fio --help
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션                | 설명                                |
|---------------------|-------------------------------------|
| `--name=JOB`        | 작업 이름을 지정합니다.             |
| `--filename=PATH`   | 테스트 파일 또는 장치를 지정합니다. |
| `--rw=PATTERN`      | 읽기·쓰기와 접근 패턴을 지정합니다. |
| `--bs=SIZE`         | I/O 요청 크기를 지정합니다.         |
| `--iodepth=N`       | 비동기 I/O 큐 깊이를 지정합니다.    |
| `--runtime=SECONDS` | 실행 시간을 지정합니다.             |
| `--time_based`      | 지정한 시간 동안 작업을 유지합니다. |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
fio --name=read-test \
    --filename=/path/to/existing-file \
    --readonly --rw=read --bs=1M --iodepth=16 \
    --runtime=60 --time_based --direct=1
```

테스트 결과의 처리량, IOPS, 평균·백분위 지연시간과 설정 조건을 함께 저장합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

🟡 `fio`를 블록 장치나 파일에 쓰기 모드로 실행하면 기존 데이터를 덮어쓸 수 있습니다. 대상 경로를 확인하고, 운영 장치 대신 별도 테스트 장치나 파일을 사용합니다.

- 캐시 사용 여부, 파일시스템, 큐 깊이와 동시성을 결과에 함께 기록합니다.
- 테스트 전후에 장치 상태와 파일시스템 사용량을 확인합니다.
- 서비스 중인 장치에 부하를 주면 지연시간과 서비스 품질에 영향을 줄 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

`fio`는 재현 가능한 저장장치 성능 테스트에 적합합니다. 테스트 대상과 쓰기 여부를 먼저 확정하고 동일한 조건으로 결과를 비교합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 저장소: [github.com/axboe/fio](https://github.com/axboe/fio) — ★★★☆☆

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
