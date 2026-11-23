# Vim 사용법
<!-- reference: _reference/vim_official_notes.md -->

서버에서 설정 파일을 고칠 때 쓰는 편집기 Vim의 기본 사용법입니다. 모드, 이동, 편집, 검색·치환, 저장과 종료, 설정 파일, 설치 확인과 검증까지 이 문서만으로 따라 할 수 있게 썼습니다.

- 기준 판: Vim 9.2 (2026-11-23 확인)
- 예제 시험: 2026-11-23, Ubuntu 24.04의 Vim 9.1에서 9·10절 명령을 실행해 확인

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. 모드](#1-모드) / [2. 커서 이동](#2-커서-이동) / [3. 편집](#3-편집)                                               |
| [4. 검색 및 치환](#4-검색-및-치환) / [5. 파일 저장 및 종료](#5-파일-저장-및-종료) / [6. 유용한 설정](#6-유용한-설정) |
| [7. 분할 창](#7-분할-창) / [8. 매크로](#8-매크로) / [9. 설치와 설정 파일](#9-설치와-설정-파일)                       |
| [10. 검증](#10-검증) / [함께 보기](#함께-보기)                                                                       |

---

## 1. 모드

| 모드    | 진입 키 | 설명                 |
|---------|---------|----------------------|
| Normal  | Esc     | 기본 모드, 명령 실행 |
| Insert  | i       | 텍스트 입력          |
| Visual  | v       | 텍스트 선택          |
| Command | :       | Ex 명령 실행         |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 커서 이동

```
h ← left    j v down    k ^ up    l → right

w   next word start
b   prev word start
0   line start
$   line end
gg  file start
G   file end
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 편집

| 명령     | 설명              |
|----------|-------------------|
| `i`      | 커서 앞에 입력    |
| `a`      | 커서 뒤에 입력    |
| `o`      | 아래에 새 줄 삽입 |
| `O`      | 위에 새 줄 삽입   |
| `x`      | 커서 위 문자 삭제 |
| `dd`     | 현재 줄 삭제      |
| `yy`     | 현재 줄 복사      |
| `p`      | 붙여넣기          |
| `u`      | 실행 취소         |
| `Ctrl+r` | 다시 실행         |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 검색 및 치환

```vim
/pattern          " 앞으로 검색
?pattern          " 뒤로 검색
n                 " 다음 결과
N                 " 이전 결과
:%s/old/new/g     " 전체 치환
:%s/old/new/gc    " 확인하며 치환
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 파일 저장 및 종료

| 명령  | 설명                 |
|-------|----------------------|
| `:w`  | 저장                 |
| `:q`  | 종료                 |
| `:wq` | 저장 후 종료         |
| `:q!` | 저장 없이 강제 종료  |
| `:x`  | 변경 시 저장 후 종료 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 유용한 설정

```vim
:set number        " 줄 번호 표시
:set relativenumber " 상대 줄 번호
:set hlsearch      " 검색 결과 하이라이트
:set ignorecase    " 대소문자 무시 검색
:set tabstop=4     " 탭 너비 4
:set expandtab     " 탭을 스페이스로 변환
:syntax on         " 구문 강조
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 분할 창

```vim
:split file        " 수평 분할
:vsplit file       " 수직 분할
Ctrl+w h/j/k/l    " 창 간 이동
Ctrl+w =           " 창 크기 균등 분배
:close             " 현재 창 닫기
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 매크로

```
qa       " start recording macro a
(actions) " perform actions to repeat
q        " stop recording
@a       " run macro a
10@a     " run macro a 10 times
```

---

## 9. 설치와 설정 파일

```bash
vim --version | head -1                  # VIM - Vi IMproved 9.x
sudo apt-get install -y vim              # Ubuntu / Debian (기본은 vim-tiny만 있는 경우가 많음)
sudo dnf install -y vim-enhanced         # RHEL 계열 (기본은 vim-minimal)
vim --version | grep -E 'vimrc file'     # 설정 파일 위치
```

| 설정 파일            | 위치                                     |
|----------------------|------------------------------------------|
| 사용자               | `~/.vimrc` (두 번째 후보 `~/.vim/vimrc`) |
| 시스템 (Debian 계열) | `/etc/vim/vimrc`                         |

서버 공용 계정에서 쓰기 좋은 최소 설정입니다.

```vim
" ~/.vimrc
set number          " 줄 번호
set hlsearch        " 검색 결과 강조
set ignorecase smartcase   " 소문자로 찾으면 대소문자 무시, 대문자가 있으면 구분
set expandtab tabstop=4 shiftwidth=4   " 탭 대신 공백 4칸
set backspace=indent,eol,start
syntax on
```

YAML처럼 들여쓰기가 중요한 파일을 붙여 넣을 때는 `:set paste`로 자동 들여쓰기를 끈 뒤 붙여 넣고 `:set nopaste`로 되돌립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용      | 명령                                      | 기대 결과                                             |
|------|----------------|-------------------------------------------|-------------------------------------------------------|
| 1    | 설치와 판      | `vim --version \| head -1`                | 판 번호                                               |
| 2    | 설정 파일 위치 | `vim --version \| grep vimrc`             | 사용자·시스템 설정 경로                               |
| 3    | 설정 적용      | Vim 안에서 `:set number?`                 | `number`                                              |
| 4    | 설정 파일 오류 | `vim -es -u ~/.vimrc -c 'q'; echo $?`     | `0`. 오류가 있으면 `1` (메시지는 `vim`으로 열어 확인) |
| 5    | 저장·종료      | 파일을 열어 고친 뒤 `:wq`, `cat`으로 확인 | 변경 내용 반영                                        |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Neovim](./neovim_guide.md) — Lua 설정, LSP
- [Vim airline](./vim_airline.md) — 상태 표시줄
- [nano](./nano.md) — 단축키가 화면에 보이는 간단한 편집기
- [텍스트 처리](./text_processing.md) — 편집기 밖에서 sed로 일괄 치환

---

## 참고 자료

- Vim Documentation: [vimhelp.org](https://vimhelp.org/) — ★★★☆☆
- Vim Cheat Sheet: [vim.rtorr.com](https://vim.rtorr.com/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-28

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
