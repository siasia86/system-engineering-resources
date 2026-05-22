---
name: reference-index
description: _reference 디렉토리 인덱스. 기술별 공식 문서 참조 노트 위치와 버전 현황. 상세 내용은 각 파일을 직접 읽을 것.
---

# _reference INDEX

문서 작성/검토 시 해당 기술의 참조 파일을 읽어 공식 권장사항을 확인합니다.

| 기술      | 파일                                     | 최신 버전                     | 확인일     |
|-----------|------------------------------------------|-------------------------------|------------|
| Docker    | `_reference/docker_official_notes.md`    | Engine 29.5.2, Compose v5.1.4 | 2026-05-22 |
| Terraform | `_reference/terraform_official_notes.md` | v1.15.4, AWS Provider v6.46.0 | 2026-05-22 |
| Zabbix    | `_reference/zabbix_official_notes.md`    | 7.4 (LTS: 7.0)                | 2026-05-22 |

## 사용 규칙

- `.md` 파일 작성/수정 전 해당 기술의 참조 파일 존재 여부 확인
- 없으면 공식 홈페이지 스캔 후 생성 (`lynx -dump` 또는 GitHub/PyPI API)
- 있으면 `last_checked` 날짜 확인 — 6개월 이상 경과 시 재확인 권장
- 파일 경로: `/root/32_system-engineering-resources/_reference/{기술명}_official_notes.md`
