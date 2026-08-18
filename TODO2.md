# TODO2
<!-- reference: _reference/INDEX.md, _reference/iotop_official_notes.md, _reference/linux_filesystem_official_notes.md, _reference/linux_kernel_official_notes.md, _reference/linux_process_official_notes.md -->

저장장치 도구 문서 확장 작업과 공식 참고 문서 관리 순서입니다.

## 목차

| 섹션                                                                            |
|---------------------------------------------------------------------------------|
| [1. 작업 목표](#1-작업-목표) / [2. 작업 흐름](#2-작업-흐름)                     |
| [3. 문서 작성 대상 도구](#3-문서-작성-대상-도구) / [4. 검증 기준](#4-검증-기준) |

---

## 1. 작업 목표

저장장치 도구를 개별 `.md` 문서로 확장하고, 각 문서의 사실 주장을 공식 출처와 대조합니다.

- `_reference/`는 공식 홈페이지·공식 매뉴얼·공식 GitHub 문서만 기록합니다.
- 본문 문서보다 `_reference/` 작성과 `_reference/INDEX.md` 등록을 먼저 수행합니다.
- 기존 문서는 중복 작성하지 않고, 현재 상태와 완료 여부를 TODO2에서 관리합니다.

## 2. 작업 흐름

다음 순서를 각 도구 문서에 적용합니다.

1. **대상 확인** → 기존 `.md`, `_reference/INDEX.md`, 관련 `_reference` 파일을 확인합니다.
2. **공식 출처 조사** → 공식 사이트, 공식 매뉴얼, 공식 GitHub 저장소만 `lynx -dump` 또는 `curl`로 확인합니다.
3. **참고 문서 작성** → `_reference/{tool}_official_notes.md`가 없으면 먼저 생성합니다.
4. **참고 인덱스 등록** → `_reference/INDEX.md`에 파일, 버전 또는 범위, 확인일을 추가합니다.
5. **도구 문서 작성** → `_reference`에서 확인한 내용만 사용하여 `01_fundamentals/linux/{tool}.md`를 작성합니다.
6. **형식 검증** → `md-style-check.py`, `md-link-check.py`, `git diff --check`를 실행합니다.
7. **Fact-check** → 문서 전체의 사실 주장, 명령어, 옵션, 버전과 주의사항을 공식 출처와 다시 대조합니다.
8. **최종 확인** → 변경 범위, 내부 링크, 참고 주석, 비밀정보 노출 여부를 확인합니다.
9. **Git 반영** → 검증 통과 후 요청이 있을 때만 대상 파일을 명시적으로 commit하고 push합니다.

🟡 `_reference` 파일이 없는 상태에서 본문 `.md`를 먼저 작성하지 않습니다.

### 2.1 참고 문서 작성 규칙

- 기존 참고 문서가 있으면 `last_checked` 날짜를 확인합니다.
- `last_checked`가 6개월 이상 지난 경우 공식 출처를 재확인합니다.
- 버전은 GitHub Releases API 또는 공식 버전 페이지에서 확인합니다.
- 공식 출처에서 확인할 수 없는 내용은 본문과 참고 문서에 단정적으로 기록하지 않습니다.
- 기존 참고 문서를 실제로 사용한 본문에는 다음 형식의 참조 주석을 추가합니다.

```markdown
# 문서 제목
<!-- reference: _reference/tool_official_notes.md -->
```

## 3. 문서 작성 대상 도구

### 3.1 완료 문서

- [x] `iotop.md` — 프로세스별 I/O 모니터링.
- [x] `ioping.md` — 파일시스템·저장장치 I/O 지연시간 측정.
- [x] `storage_tools.md` — 저장장치 도구 전체 선택 가이드.

### 3.2 추가 작성 예정 문서

장치·마운트 확인:

- [x] `lsblk.md` — 블록 장치와 파일시스템 계층 확인.
- [x] `findmnt.md` — 마운트된 파일시스템과 마운트 옵션 확인.
- [x] `blkid.md` — 블록 장치의 UUID·LABEL·파일시스템 유형 확인.

공간 사용량 확인:

- [x] `df.md` — 파일시스템 전체·사용·가용 공간 확인.
- [x] `du.md` — 파일·디렉토리별 공간 사용량 확인.
- [x] `ncdu.md` — 대화형 디스크 사용량 분석.

프로세스·디바이스 I/O:

- [x] `pidstat.md` — 프로세스별 I/O 통계 확인.
- [x] `iostat.md` — 디바이스별 처리량·대기시간·사용률 확인.

종합 시스템 모니터링:

- [x] `dstat.md` — CPU·메모리·디스크·네트워크 통합 통계 확인.
- [x] `atop.md` — 시스템 자원과 프로세스 상태의 종합 모니터링.
- [x] `nmon.md` — CPU·메모리·디스크·네트워크 관찰.

성능·장치 상태:

- [x] `fio.md` — 통제된 블록 I/O 성능 테스트.
- [x] `hdparm.md` — ATA/SATA 장치 정보와 읽기 테스트.
- [x] `smartctl.md` — SMART 기반 저장장치 상태·진단.
- [x] `nvme_cli.md` — NVMe 장치 정보와 SMART 로그 확인.

## 4. 검증 기준

각 문서의 완료 조건은 다음과 같습니다.

- [x] 공식 출처를 `_reference`에 기록했습니다.
- [x] `_reference/INDEX.md`를 갱신했습니다.
- [x] 본문에 `_reference` 참조 주석을 추가했습니다.
- [x] 명령어 예시와 옵션이 실제 공식 매뉴얼에 존재합니다.
- [x] 운영 환경에서 데이터 손실이나 서비스 영향을 줄 수 있는 명령에 주의사항을 표시했습니다.
- [x] `md-style-check.py` 결과가 이슈 0건입니다.
- [x] `md-link-check.py` 결과가 깨진 링크 0건입니다.
- [x] `git diff --check`가 통과합니다.
- [x] Fact-check에서 오류가 없습니다.

---

**작성일**: 2026-08-18

**마지막 업데이트**: 2026-08-18

© 2026 siasia86. Licensed under CC BY 4.0.
