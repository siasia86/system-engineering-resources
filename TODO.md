# TODO

레포 잔여 이슈 및 향후 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                                                                                                                                    |
|-----------------------------------------------------------------------------------------------------------------------------------------|
| [1. 잔여 이슈](#1-잔여-이슈) / [2. md-style-check.py 개선](#2-md-style-checkpy-개선) / [3. reference 미검증](#3-_reference-미검증-항목) |

---

## 1. 잔여 이슈

| 파일                                                                               | 이슈 유형  | 설명                                                                               |
|------------------------------------------------------------------------------------|------------|------------------------------------------------------------------------------------|
| `06_career/ai_tools/kiro_cli_command_reference.md`                                 | _reference | frontmatter 없음 (FILE_SKIP 예외)                                                  |
| `[private] hyperv_version_centos5_compatibility.md` (34_system~ 비공개 레포)       | fact-check | ESU 종료일 오류: `2024 (Y4)` → `2023-01-10` (on-premises Y3 기준, 2026-07-27 확인) |
| `[private] hyperv_myisam_io_timeout_incident_20260715.md` (34_system~ 비공개 레포) | fact-check | Storage QoS 미설정: 2022는 기능 지원됨, "(기능 지원됨, 미적용)" 명시 필요          |

### 검사 예외 파일

| 파일                                                       | 사유                                   |
|------------------------------------------------------------|----------------------------------------|
| `01_fundamentals/linux/vim_airline.md`                     | 외부 프로젝트(vim-airline) README 원본 |
| `06_career/ai_tools/kiro_cli_command_reference.md`         | Kiro CLI 문서 (다이어그램 한글 의도적) |
| `02_infrastructure/cicd/infra_monorepo_and_boilerplate.md` | 4-backtick 내부 표 (파서 한계)         |

---

## 2. md-style-check.py 개선

code-review (2026-07-07) 결과 기반 개선 항목입니다.

### 🟡 개선 권장 (4건)

| # | 위치     | 문제                                                       | 제안                                                   |
|---|----------|------------------------------------------------------------|--------------------------------------------------------|
| 1 | L73-86   | `strip_code_blocks()` 반복 호출 (5개 검사에서 각각 재계산) | `check_file()`에서 1회 호출 후 캐시하여 각 검사에 전달 |
| 2 | L97      | `get_code_blocks` 닫힘 조건이 3-backtick만 매칭            | 4-backtick 블록 지원: fence 길이 기반 매칭             |
| 3 | L218-240 | `check_diagram` 중첩 박스 조기 종료                        | depth 카운터 또는 indent 기반 분리                     |
| 4 | L99      | 인용구(`>`) 내부 코드블록 잘못 인식 가능                   | 인용구 prefix strip 후 코드블록 판정                   |

### 선택 개선 (6건)

| #  | 위치     | 문제                          | 제안                                                        |
|----|----------|-------------------------------|-------------------------------------------------------------|
| 5  | L44-52   | `dw()` 한글 범위 이중 체크    | 성능 의도적이면 주석 추가, 아니면 `east_asian_width`만 사용 |
| 6  | L141     | `_OUTPUT_PATTERNS` 30+ 패턴   | 별도 리스트/파일로 분리                                     |
| 7  | L503-510 | `EXCLUDE_DIRS/FILES` 하드코딩 | `.md-style-check.toml` 설정 파일 분리                       |
| 8  | L577-588 | `skip_checks` 반복 if 문      | dict comprehension으로 간소화                               |
| 9  | L350-365 | 이모지 유니코드 범위          | 새 Unicode 버전 대비 주석 추가                              |
| 10 | L703     | trailing newline 3개          | 1개로 축소                                                  |

### 현재 우회책

| 이슈            | 우회                                                 |
|-----------------|------------------------------------------------------|
| 4-backtick (#2) | `infra_monorepo_and_boilerplate.md` → FILE_SKIP 예외 |
| 중첩 박스 (#3)  | 실제 문서에서 발생한 적 없음 (모니터링 중)           |

---

## 3. _reference 미검증 항목

fact-check에서 도구(lynx/curl)로 확인 불가했던 항목입니다. CHANGES 파일 직접 확인 시 해결됩니다.

| _reference 파일                | 항목                                         | 상태 |
|--------------------------------|----------------------------------------------|------|
| `web_server_official_notes.md` | Nginx 1.19.0 ssl_protocols TLSv1.3 기본 포함 | ⬜   |
| `web_server_official_notes.md` | Nginx 1.15.0 ssl 없이 ssl_certificate 가능   | ⬜   |
| `web_server_official_notes.md` | Nginx 1.9.5 stream 모듈 추가                 | ⬜   |
| `web_server_official_notes.md` | Apache 2.4.58 mod_http2 TLS 1.3 early data   | ⬜   |

- `grep -r "unverified" _reference/` 로 전체 미확인 항목 조회 가능
- 확인 완료 시: _reference 내 `<!-- unverified: -->` 주석 제거 + 이 표 ⬜ → ✅


---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-07-29

© 2026 siasia86. Licensed under CC BY 4.0.

