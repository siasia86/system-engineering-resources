# hdparm - ATA/SATA 장치 정보와 읽기 테스트
<!-- reference: _reference/storage_tools_official_notes.md -->

`hdparm`은 ATA/SATA 장치의 식별 정보를 조회하고 장치·캐시 읽기 타이밍을 측정하는 유틸리티입니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 및 확인](#2-설치-및-확인) / [3. 주요 옵션](#3-주요-옵션) |
| [4. 사용 예시](#4-사용-예시) / [5. 주의사항](#5-주의사항) / [6. 요약](#6-요약)         |

---

## 1. 개요

`hdparm`은 장치 식별 정보와 읽기 타이밍을 확인할 때 사용합니다. 일부 옵션은 장치 설정을 변경하므로 조회와 변경 작업을 구분해야 합니다.

> ATA(Advanced Technology Attachment): 저장장치와 호스트 사이의 명령·전송 인터페이스 계열입니다. SATA는 ATA 계열의 직렬 전송 방식입니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 및 확인

```bash
command -v hdparm
hdparm -V
man hdparm
```

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 옵션

| 옵션 | 설명                              |
|------|-----------------------------------|
| `-I` | 장치 식별 정보를 표시합니다.      |
| `-t` | 장치 읽기 타이밍을 수행합니다.    |
| `-T` | 캐시 읽기 타이밍을 수행합니다.    |
| `-q` | 다음 옵션의 일반 출력을 줄입니다. |

[⬆ 목차로 돌아가기](#목차)

## 4. 사용 예시

```bash
sudo hdparm -I /dev/sdX
sudo hdparm -tT /dev/sdX
```

`-t`와 `-T`의 결과를 구분하여 해석합니다. 반복 측정 시 다른 I/O 부하와 캐시 상태를 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 주의사항

🟡 `hdparm`에는 장치 설정을 변경하거나 위험한 동작을 수행하는 옵션이 있습니다. 문서에서 확인하지 않은 변경 옵션은 운영 장치에 사용하지 않습니다.

- `/dev/sdX`를 실제 장치로 바꾸기 전에 `lsblk`로 대상과 마운트 상태를 확인합니다.
- 읽기 타이밍도 서비스 중인 장치의 I/O에 영향을 줄 수 있습니다.
- `-t`와 `-T`는 종합적인 성능 테스트가 아니므로 `fio`와 결과를 동일시하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 요약

장치 식별 정보는 `hdparm -I`, 간단한 읽기 타이밍은 `hdparm -tT`로 확인합니다. 변경 옵션은 별도 위험 검토가 필요합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- 저장장치 도구 공식 참고 노트: [`_reference/storage_tools_official_notes.md`](../../_reference/storage_tools_official_notes.md)
- 저장장치 도구 개요: [`storage_tools.md`](./storage_tools.md)
- 공식 매뉴얼: [man7.org/linux/man-pages/man8/hdparm.8.html](https://man7.org/linux/man-pages/man8/hdparm.8.html) — ★★★☆☆

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
