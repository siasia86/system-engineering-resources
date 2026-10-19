# SSD 마모 분산과 fio 성능 검수

같은 파일을 반복해서 쓰는 경우의 SSD 마모와 성능 시험 결과를 구분해 읽는 요약입니다. 실제 장비를 시험한 결과나 수명 보증이 아닙니다.

## 목차

| 섹션                                                       |
|------------------------------------------------------------|
| [1. 주소 변환과 마모 분산](#1-주소-변환과-마모-분산)       |
| [2. fio 설정과 실제 쓰기량](#2-fio-설정과-실제-쓰기량)     |
| [3. SSS-PTS로 성능 결과 읽기](#3-sss-pts로-성능-결과-읽기) |

## 1. 주소 변환과 마모 분산

FTL(Flash Translation Layer)은 호스트의 논리 주소를 NAND의 물리 주소로 매핑합니다. Wear leveling은 쓰기·지우기 부담을 셀에 분산하는 관리 기능입니다. 같은 1 GB 파일을 반복해서 덮어써도 같은 물리 셀에 고정해서 쓰는 것은 아닙니다. 그렇다고 마모가 없거나 매번 모든 셀에 정확히 균등하게 쓰인다는 뜻도 아닙니다.

영향은 누적 쓰기량, 내부 WAF(Write Amplification Factor: NAND 쓰기량/호스트 쓰기량), 사용 가능한 여유 공간과 장치 상태를 함께 봅니다. RAID의 SSD 사이 쓰기 배치와 SSD 내부 셀의 마모 분산은 다른 층입니다. 제조사 TBW 정격이 호스트 쓰기 기준이면 같은 기준의 누적 쓰기량과 비교하고, NAND 기준 쓰기량을 혼합하거나 WAF를 임의로 다시 곱하지 않습니다.

## 2. fio 설정과 실제 쓰기량

| 항목               | 읽는 방법                                                                                                             |
|--------------------|-----------------------------------------------------------------------------------------------------------------------|
| `size`·파일 점유량 | 작업 범위·설정된 I/O 크기이며 실제 누적 쓰기량과 항상 같지 않습니다. 읽기 비율·반복·다른 종료 조건을 함께 확인합니다. |
| `runtime`          | `time_based`가 없으면 실행 시간의 상한입니다. 설정된 I/O가 먼저 끝나면 더 일찍 종료할 수 있습니다.                    |
| `numjobs`          | 동일 설정으로 복제하는 작업 수입니다.                                                                                 |
| `cpus_allowed`     | 작업이 실행될 CPU의 배치 범위이며 작업 수를 뜻하지 않습니다.                                                          |

실제 쓰기량은 fio의 쓰기 결과와 시험 전후 **SSD별** NVMe SMART `Data Units Written` 차이로 대조합니다. 이 카운터는 호스트가 컨트롤러에 쓴 양이며 내부 NAND 쓰기량 자체가 아닙니다. 단위·보고 범위와 다른 작업의 쓰기도 확인해야 하므로, 파일 크기나 CPU 수만으로 장치별 쓰기량·수명 소모율을 확정하지 않습니다.

## 3. SSS-PTS로 성능 결과 읽기

SSS-PTS(Solid State Storage Performance Test Specification)는 SNIA의 **장치 수준 성능 시험 규격**입니다. 사전 부하로 시험 상태를 준비하고 정상상태 도달 여부를 확인한 뒤 IOPS·처리량·지연을 시험 조건과 함께 보고합니다. 정상상태는 지표의 안정 조건이며 장치 건강을 보증하는 표현이 아닙니다.

fio를 실행했다는 사실만으로 PTS 준수·SSD 내구성 보증·GRAID 전체 구성 검증을 주장할 수 없습니다. 규격 판본·시험 대상·사전 부하·정상상태 판정·결과 보고 범위를 명시해야 합니다.

## 참고 자료

공식 자료 확인일: 2026-10-19. fio master 문서는 조회 당시 3.42 계열, SSS-PTS는 v2.0.2를 기준으로 확인했습니다. 실제 적용 시 설치 버전과 시험 대상을 대조합니다.

- [Samsung: FTL과 쓰기 증폭](https://semiconductor.samsung.com/news-events/tech-blog/a-brief-history-of-data-placement-technologies/) — ★★☆☆☆
- [Samsung: Wear Leveling FAQ](https://semiconductor.samsung.com/kr/consumer-storage/support/faqs/internalssd-product-information/) — ★★★☆☆
- [fio 공식 문서](https://fio.readthedocs.io/en/master/fio_doc.html) — ★★★☆☆
- [libnvme: SMART 로그 필드 정의](https://github.com/linux-nvme/libnvme/blob/master/src/nvme/types.h) — ★★★☆☆
- [SNIA: SSS-PTS 규격](https://www.snia.org/tech_activities/standards/curr_standards/pts) · [v2.0.2](https://www.snia.org/sites/default/files/technical-work/pts/release/SNIA-SSS-PTS-2.0.2.pdf) · [처리량 시험 개요](https://www.snia.org/forums/sssi/pts/tp) — ★★★☆☆
- 관련 문서: [fio 사용법](../../01_fundamentals/linux/fio.md), [SupremeRAID SMART·수명·성능 기준선 점검](../monitoring/graid_supremeraid_server_check.md). 상세 절차는 해당 문서를 따릅니다.

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-19

**마지막 업데이트**: 2026-10-19

© 2026 siasia86. Licensed under CC BY 4.0.
