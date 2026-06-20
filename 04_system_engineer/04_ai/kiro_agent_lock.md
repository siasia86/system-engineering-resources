# Kiro Agent Lock — 협업 디렉토리 동시 작업 방지

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 구현 방식](#2-구현-방식) / [3. 동작 흐름](#3-동작-흐름)                             |
| [4. 엣지 케이스](#4-엣지-케이스) / [5. 유사 오픈소스 프로젝트](#5-유사-오픈소스-프로젝트) / [6. 비교](#6-비교) |

## 1. 개요

팀원들이 동일 프로젝트 디렉토리에서 kiro agent를 동시에 실행할 때 파일 충돌을 방지하는 방법입니다.
프로젝트 루트에 `.kiro-lock` 파일을 생성하여 advisory lock을 구현합니다.

### 핵심 원리

- 작업 시작 시 lock 파일 생성 (user, host, session, task 기록)
- lock 파일이 존재하면 다른 agent는 작업을 중단합니다
- 작업 완료 시 lock 파일 삭제

## 2. 구현 방식

kiro의 `.kiro/skills/` 디렉토리에 스킬로 등록하여 agent가 규칙을 따르도록 합니다.

### Lock 파일 형식

```
user: yunli
host: sjyun
started: 2026-06-09T11:52:31+09:00
session: 1780973551
task: ansible playbook 수정
```

### 스킬 등록

```
.kiro/skills/kiro-lock/SKILL.md    # lock 규칙 정의
.kiro/skills/work-rules/SKILL.md   # "lock 필수" 참조 추가
agents/*.json                       # resources에 skill://kiro-lock 추가
```

### 적용 대상 판별

| 에이전트 유형   | 적용 여부 | 이유                         |
|-----------------|-----------|------------------------------|
| 쓰기 가능 agent | ✅        | 파일 수정 가능 → lock 필요   |
| 읽기 전용 agent | ❌        | 파일 수정 없음 → lock 불필요 |

## 3. 동작 흐름

```
Agent Start                           
    │                                 
    v                                 
┌─────────────────────────┐           
│ [ -f .kiro-lock ] ?     │           
└─────────────────────────┘           
    │              │                  
   Yes            No                  
    │              │                  
    v              v                  
┌──────────┐  ┌──────────────────────┐
│ Show     │  │ Create .kiro-lock    │
│ content  │  │ (user/host/session)  │
│ + STOP   │  └──────────────────────┘
└──────────┘           │              
                       v              
               ┌──────────────┐       
               │ Do work      │       
               └──────────────┘       
                       │              
                       v              
               ┌──────────────┐       
               │ rm .kiro-lock│       
               └──────────────┘       
```

### 확인 명령어

```bash
# lock 확인
if [ -f .kiro-lock ]; then
    cat .kiro-lock 2>/dev/null || echo "lock 파일 읽기 권한 없음"
fi

# lock 획득
printf "user: $(whoami)\nhost: $(hostname)\nstarted: $(date -Iseconds)\nsession: $(date +%s)\ntask: <작업 요약>\n" > .kiro-lock

# lock 해제
rm -f .kiro-lock
```

## 4. 엣지 케이스

| 케이스                   | 처리 방법                                            |
|--------------------------|------------------------------------------------------|
| Stale lock (30분 경과)   | 사용자 확인 후 삭제                                  |
| 자기 lock (이전 세션)    | session 값 비교, 다르면 확인 후 삭제                 |
| 손상된 lock 파일         | 파싱 불가 시 stale 취급, 확인 후 삭제                |
| lock 파일 읽기 권한 없음 | `[ -f .kiro-lock ]`으로 존재 감지 → 작업 중단        |
| lock 생성 권한 없음      | 오류 출력 + 작업 미진행                              |
| delegate 호출 시         | 오케스트레이터가 lock 보유, 하위 agent는 재확인 생략 |
| context compaction 후    | 10분 이상 경과 시 자기 lock 재확인                   |
| 읽기 전용 작업           | lock 확인/획득 없이 수행                             |

## 5. 유사 오픈소스 프로젝트

### BEXAI/Mutex

- GitHub: [BEXAI/Mutex](https://github.com/BEXAI/Mutex)
- Python + `fcntl` OS 레벨 lock + JSON 상태 관리
- 특징: CLI/API, 큐잉, checksum, 히스토리 추적, force-release
- stale lock 자동 감지 (기본 5분)

```bash
# 사용 예시
python mutex.py --agent Agent_01 --acquire --files "main.py" --operation write --intent "Adding validation"
python mutex.py --agent Agent_01 --release --changes "Added validate_input()"
```

### RoscoeTheDog/async-crud-mcp

- GitHub: [RoscoeTheDog/async-crud-mcp](https://github.com/RoscoeTheDog/async-crud-mcp)
- MCP 서버에 file-locking CRUD 내장
- Python 3.12+, FastMCP 기반
- 별도 데몬 프로세스로 동작

## 6. 비교

| 항목             | .kiro-lock (스킬)   | BEXAI/Mutex          | flock (OS)         |
|------------------|---------------------|----------------------|--------------------|
| 설치             | 없음 (스킬 파일만)  | Python 스크립트 필요 | 시스템 내장        |
| Lock 단위        | 프로젝트 전체       | 파일 단위            | 파일 단위          |
| 가시성           | ✅ 파일 내용 확인   | ✅ JSON + CLI        | ❌ 종료 시 소멸    |
| 비정상 종료 대응 | stale 판정 (30분)   | stale 판정 (5분)     | ✅ 커널 자동 해제  |
| Race condition   | 있음 (advisory)     | 없음 (fcntl atomic)  | 없음 (atomic)      |
| Agent 인식       | ✅ 스킬로 읽기 가능 | ❌ 별도 호출 필요    | ❌ agent 인식 불가 |
| 적합 시나리오    | 소규모 팀 협업      | 다수 agent 동시 실행 | 프로세스 레벨 차단 |

### 선택 기준

- **소규모 팀 + kiro 간 협업** → `.kiro-lock` 스킬 방식 (현재 구현)
- **다수 agent 동시 실행 + 파일 단위 lock** → BEXAI/Mutex
- **OS 레벨 원천 차단** → `flock` 래퍼 스크립트

## 참고 자료

- BEXAI/Mutex: [github.com/BEXAI/Mutex](https://github.com/BEXAI/Mutex) — ★★☆☆☆
- async-crud-mcp: [github.com/RoscoeTheDog/async-crud-mcp](https://github.com/RoscoeTheDog/async-crud-mcp) — ★★☆☆☆
- flock(1) man page: [linux.die.net/man/1/flock](https://linux.die.net/man/1/flock) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-06-09

**마지막 업데이트**: 2026-06-09

© 2026 siasia86. Licensed under CC BY 4.0.
