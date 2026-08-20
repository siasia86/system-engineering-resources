# Tool Mirror Sync Policy

AI 도구 실행 환경 자료와 저장소 공개 미러 사이의 동기화 기준을 정의합니다. 현재 등록된 미러는 `~/.kiro/`와 `00_governance/02_kiro/`입니다.

## 목차

| 섹션                                                                                 |
|--------------------------------------------------------------------------------------|
| [1. 원본과 미러](#1-원본과-미러) / [2. 허용 범위](#2-허용-범위)                      |
| [3. 제외 범위](#3-제외-범위) / [4. 동기화 절차](#4-동기화-절차) / [5. 검증](#5-검증) |

---

## 1. 원본과 미러

- Kiro 실행 원본은 `~/.kiro/`입니다.
- Kiro 저장소 공개 미러는 `00_governance/02_kiro/`입니다.
- Kiro 동기화 방향은 `~/.kiro/`에서 `00_governance/02_kiro/`로만 제한합니다.
- Claude 등 새 도구를 추가할 때는 원본 경로와 미러 경로를 별도로 정의합니다.
- 저장소 내용을 실행 환경으로 자동 역동기화하지 않습니다.
- 동기화 결과는 자동 commit하지 않고 diff를 검토한 뒤 반영합니다.

## 2. 허용 범위

| 대상            | 조건                                                  |
|-----------------|-------------------------------------------------------|
| 일반 Skill 문서 | 개인 정보와 환경 종속 경로를 제거한 경우              |
| Hook 설명서     | 실행 스크립트가 아닌 공개 가능한 설명만 포함하는 경우 |
| Markdown 규칙   | 저장소에서 재사용 가능한 규칙만 포함하는 경우         |
| 템플릿          | 자격증명과 개인 환경 정보가 없는 경우                 |

허용 파일은 홈 실행 환경의 manifest에 등록합니다. 현재 Kiro 실행 source of truth는
`/home/siasia/.kiro/manifests/kiro_files.txt`이며, 중앙 mirror 사본은
[`../02_kiro/manifests/kiro_files.txt`](../02_kiro/manifests/kiro_files.txt)입니다.

## 3. 제외 범위

다음 내용은 공개 미러로 동기화하지 않습니다.

- `memory.md`의 개인 기억과 내부 환경 정보.
- 내부 IP, 호스트명, 사용자명, 개인 경로.
- API key, token, password, SSH key와 같은 자격증명.
- 개인용 prompt와 system context.
- `settings/`의 개인 설정과 세션 상태 파일.
- private repository 원문과 운영 정보.

## 4. 동기화 절차

1. 도구별 동기화 허용 목록에 등록된 대상만 선택합니다.
2. dry-run으로 추가·수정·삭제 예정 항목을 확인합니다.
3. 개인 정보와 비밀정보를 검색합니다.
4. 해당 도구 미러의 diff를 검토합니다.
5. Markdown 및 링크 검사를 실행합니다.
6. 검증을 통과한 변경만 commit합니다.

`--delete` 옵션은 기본으로 사용하지 않습니다. 삭제가 필요한 경우 대상과 영향을 먼저 확인합니다.

## 5. 검증

```bash
"$HOME/.kiro/02_home-sjyun-kiro.sh" \
  --target central \
  --dry-run
sudo gitleaks detect --source . --no-banner
sudo python3 md-link-check.py 00_governance/02_kiro/
sudo python3 md-style-check.py .
```

동기화 manifest가 없는 파일은 동기화 대상에 포함하지 않습니다. `memory.md`,
`memory_private.md`, `.local/`, `settings/`, `sessions/`는 manifest와 rsync에서
이중으로 제외합니다. 미러 원본의 형식 보존이 필요한 경우에도 공개 가능 여부를
먼저 검토합니다.

---

**작성일**: 2026-08-20

**마지막 업데이트**: 2026-08-20

© 2026 siasia86. Licensed under CC BY 4.0.
