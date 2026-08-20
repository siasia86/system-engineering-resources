# Kiro mirror manifest

`kiro_files.txt`는 `/home/siasia/.kiro/`를 기준으로 중앙 mirror에 복사할 public 파일만 기록합니다.

## 1. 규칙

- 한 줄에 하나의 상대 경로를 기록합니다.
- `/.local/`, `memory.md`, `memory_private.md`, `sessions/`, `settings/`는 등록하지 않습니다.
- 비밀번호, token, private key, access key는 어떤 manifest에도 등록하지 않습니다.
- 새 skill이나 agent 파일은 review 후 명시적으로 추가합니다.
- 실행 기준은 이 홈 manifest이며 중앙 저장소의 사본은 backup입니다.

## 2. 동기화

동기화 기준 script는 `02_home-sjyun-kiro.sh`입니다. `01_home-sjyun-kiro.sh`는 기존 broad sync 원본 보존본입니다. `01`은 실제 실행하지 않고 원문 보관·비교 용도로만 사용합니다.

---

**작성일**: 2026-08-20

**마지막 업데이트**: 2026-08-20

© 2026 siasia86. Licensed under CC BY 4.0.
