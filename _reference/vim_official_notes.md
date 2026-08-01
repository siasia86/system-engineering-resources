---
name: vim-official-notes
last_checked: 2026-08-01
sources:
  - https://vimhelp.org/
  - https://man7.org/linux/man-pages/man1/vim.1.html
  - https://github.com/vim/vim
---

# Vim 공식 참조 노트

## 1. Vim 개요

### 공식 소스

| 소스        | URL                                              | 용도                  |
|-------------|--------------------------------------------------|-----------------------|
| vimhelp.org | https://vimhelp.org/                             | 공식 도움말 HTML 버전 |
| vim.1       | https://man7.org/linux/man-pages/man1/vim.1.html | 시작 옵션, 모드 개요  |
| GitHub      | https://github.com/vim/vim                       | 최신 버전 확인        |

### 검증된 사실 (2026-08-01)

| 항목           | 값                                                                           | 출처        |
|----------------|------------------------------------------------------------------------------|-------------|
| 최신 버전      | 9.2 (patch 9.2.0888 기준, 2026-02-14)                                        | vimhelp.org |
| 기본 실행 방법 | `vim [options] [file ...]`                                                   | vim.1       |
| 정상 종료 방법 | `:q` (저장 없이 종료) / `:wq` (저장 후 종료) / `:x` (변경 시만 저장 후 종료) | vimhelp.org |
| 강제 종료      | `:q!` (변경 내용 무시하고 종료)                                              | vimhelp.org |

## 2. 편집 모드 (vimhelp.org 기반)

### 공식 소스

| 소스        | URL                  | 용도              |
|-------------|----------------------|-------------------|
| vimhelp.org | https://vimhelp.org/ | 모드, 명령어 설명 |

### 검증된 사실 (2026-08-01)

| 모드         | 진입 방법                                  | 출처        |
|--------------|--------------------------------------------|-------------|
| Normal 모드  | 기본 모드, `Esc`로 복귀                    | vimhelp.org |
| Insert 모드  | `i`(현재 위치), `a`(다음 위치), `o`(새 줄) | vimhelp.org |
| Visual 모드  | `v`(문자), `V`(줄), `Ctrl-v`(블록)         | vimhelp.org |
| Command 모드 | `:` 입력 후 Ex 명령어 실행                 | vimhelp.org |
| Replace 모드 | `R` (기존 문자 덮어쓰기)                   | vimhelp.org |

## 3. 주요 Normal 모드 명령어

### 검증된 사실 (2026-08-01)

| 명령어          | 동작                           | 출처        |
|-----------------|--------------------------------|-------------|
| `h`/`j`/`k`/`l` | 좌/하/상/우 이동               | vimhelp.org |
| `w` / `b`       | 다음/이전 단어 이동            | vimhelp.org |
| `gg` / `G`      | 파일 처음 / 끝으로 이동        | vimhelp.org |
| `dd`            | 현재 줄 삭제 (레지스터에 저장) | vimhelp.org |
| `yy`            | 현재 줄 복사 (yank)            | vimhelp.org |
| `p` / `P`       | 커서 다음/앞에 붙여넣기        | vimhelp.org |
| `u`             | 실행 취소 (undo)               | vimhelp.org |
| `Ctrl-r`        | 재실행 (redo)                  | vimhelp.org |
| `/pattern`      | 앞으로 검색                    | vimhelp.org |
| `?pattern`      | 뒤로 검색                      | vimhelp.org |
| `n` / `N`       | 다음/이전 검색 결과로 이동     | vimhelp.org |
| `:%s/old/new/g` | 전체 치환                      | vimhelp.org |
| `.`             | 마지막 변경 반복               | vimhelp.org |

## 4. 주요 시작 옵션 (vim.1 man page 기반)

### 공식 소스

| 소스  | URL                                              | 용도      |
|-------|--------------------------------------------------|-----------|
| vim.1 | https://man7.org/linux/man-pages/man1/vim.1.html | 옵션 목록 |

### 검증된 사실 (2026-08-01)

| 옵션           | 동작                        | 출처  |
|----------------|-----------------------------|-------|
| `-c <command>` | 파일 열기 후 Ex 명령어 실행 | vim.1 |
| `-R`           | 읽기 전용 모드로 열기       | vim.1 |
| `-r <file>`    | 스왑 파일로 복구            | vim.1 |
| `-u <vimrc>`   | 지정 vimrc 파일 사용        | vim.1 |
| `--noplugin`   | 플러그인 로드 안 함         | vim.1 |
| `--version`    | 버전 정보 출력              | vim.1 |
| `-p [N]`       | 탭으로 파일 열기            | vim.1 |
| `-o [N]`       | 수평 분할로 파일 열기       | vim.1 |
| `-O [N]`       | 수직 분할로 파일 열기       | vim.1 |

## 5. deprecated / 주의사항

| 항목           | 상태                                                | 출처        |
|----------------|-----------------------------------------------------|-------------|
| `vi` 호환 모드 | `vim -C` 또는 `set compatible` — 기능 제한됨        | vimhelp.org |
| swap 파일      | 비정상 종료 시 `.swp` 파일 생성 — 복구 후 삭제 필요 | vimhelp.org |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
