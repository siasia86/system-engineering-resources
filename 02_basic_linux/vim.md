# Vim 사용법

## 목차

| 섹션 |
|------|
| [모드](#모드) |
| [커서 이동](#커서-이동) |
| [편집](#편집) |
| [검색 및 치환](#검색-및-치환) |
| [파일 저장 및 종료](#파일-저장-및-종료) |
| [유용한 설정](#유용한-설정) |
| [분할 창](#분할-창) |
| [매크로](#매크로) |

---


[⬆ 목차로 돌아가기](#목차)

---

## 모드

| 모드    | 진입 키 | 설명                 |
|---------|---------|----------------------|
| Normal  | Esc     | 기본 모드, 명령 실행 |
| Insert  | i       | 텍스트 입력          |
| Visual  | v       | 텍스트 선택          |
| Command | :       | Ex 명령 실행         |

[⬆ 목차로 돌아가기](#목차)

---

## 커서 이동

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

## 편집

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

## 검색 및 치환

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

## 파일 저장 및 종료

| 명령  | 설명                 |
|-------|----------------------|
| `:w`  | 저장                 |
| `:q`  | 종료                 |
| `:wq` | 저장 후 종료         |
| `:q!` | 저장 없이 강제 종료  |
| `:x`  | 변경 시 저장 후 종료 |

[⬆ 목차로 돌아가기](#목차)

---

## 유용한 설정

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

## 분할 창

```vim
:split file        " 수평 분할
:vsplit file       " 수직 분할
Ctrl+w h/j/k/l    " 창 간 이동
Ctrl+w =           " 창 크기 균등 분배
:close             " 현재 창 닫기
```

[⬆ 목차로 돌아가기](#목차)

---

## 매크로

```
qa       " start recording macro a
(actions) " perform actions to repeat
q        " stop recording
@a       " run macro a
10@a     " run macro a 10 times
```

---

## 참고 자료

- Vim Documentation: [vimdoc.sourceforge.net](http://vimdoc.sourceforge.net/) — ★★★☆☆
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

**마지막 업데이트**: 2026-04-12

© 2026 siasia86. Licensed under CC BY 4.0.
