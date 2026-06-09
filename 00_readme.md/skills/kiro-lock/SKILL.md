---
name: kiro-lock
description: 협업 디렉토리 동시 작업 방지. 파일 수정 작업 전 lock 확인/획득, 완료 후 해제.
---

# Kiro Lock

## 1. 작업 시작 전 (필수)

파일 수정 작업 수행 전 반드시 실행합니다.

```bash
if [ -f .kiro-lock ]; then
    cat .kiro-lock 2>/dev/null || echo "⚠️ lock 파일 읽기 권한 없음 — 작업 중단"
fi
```

- 파일 존재 + 읽기 가능 → 내용 출력 + "다른 작업이 진행 중입니다." 안내 + **작업 즉시 중단**
- 파일 존재 + 읽기 불가 → 권한 문제 안내 + **작업 즉시 중단**
- 파일 없음 → Lock 획득 진행

## 2. Lock 획득

```bash
printf "user: $(whoami)\nhost: $(hostname)\nstarted: $(date -Iseconds)\nsession: $(date +%s)\ntask: <작업 요약>\n" > .kiro-lock
```

## 3. 작업 완료 후 (필수)

정상 완료 또는 오류 발생 시 모두 삭제합니다.

```bash
rm -f .kiro-lock
```

## 4. 규칙

- Lock 파일 경로: **프로젝트 루트** (`.git`이 위치한 디렉토리)의 `.kiro-lock`
- Lock 미획득 시 어떤 파일도 수정하지 않습니다
- 작업 중 오류가 발생해도 반드시 lock을 삭제합니다
- 매 `fs_write`/쓰기 명령 실행 전에 `.kiro-lock`이 자기 것인지 재확인합니다 (10분 이상 경과 시 또는 context compaction 후)
- `.gitignore`에 `.kiro-lock` 추가를 권장합니다

## 5. Stale lock 처리

`started` 시각이 30분 이상 경과한 경우:
1. 해당 사용자에게 확인 요청 안내를 출력합니다
2. 사용자가 "lock 해제해줘"라고 명시적으로 요청하면 삭제 후 작업을 진행합니다

## 6. 엣지 케이스

### 자기 lock 감지

lock 파일의 `user`와 `host`가 현재 `$(whoami)`/`$(hostname)`과 동일한 경우:
- `session` 값이 현재 세션과 동일하면 자기 lock입니다 (정상 진행)
- `session` 값이 다르면 이전 세션의 잔류 lock, "이전 세션의 lock이 남아있습니다. 삭제할까요?" 확인 후 진행합니다

### 손상된 lock 파일

lock 파일이 존재하나 `user`/`started` 필드를 파싱할 수 없는 경우:
- stale lock으로 취급합니다
- 사용자에게 "lock 파일이 손상되었습니다. 삭제할까요?" 확인 후 진행합니다

### 읽기 전용 작업

아래 작업은 lock 확인/획득 없이 수행합니다:
- `fs_read`, `grep`, `glob` 등 읽기 전용 도구만 사용하는 경우
- `git status`, `git log`, `git diff` 등 조회 명령어
- 상태 확인 (`cat`, `ls`, `find`)

### Lock 생성 실패

`.kiro-lock` 생성 시 권한 오류가 발생하면:
1. 오류 메시지를 출력합니다
2. 작업을 진행하지 않습니다
3. "프로젝트 디렉토리 쓰기 권한을 확인하세요" 안내합니다

### delegate 호출 시

오케스트레이터(system-engineer)가 lock을 획득한 상태에서 delegate로 하위 agent를 호출하면:
- 하위 agent는 lock을 재확인하지 않습니다 (이미 획득된 상태)
- lock 해제는 오케스트레이터가 최종 작업 완료 시 수행합니다
