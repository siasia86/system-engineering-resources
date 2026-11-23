---
name: nano-official-notes
description: GNU nano의 판, 판별 기본 단축키 차이, 명령줄 옵션, nanorc 설정의 공식 출처 기준 사실 정리.
tags:
  - linux
  - editor
  - nano
last_checked: 2026-11-23
sources:
  - https://www.nano-editor.org/download.php
  - https://www.nano-editor.org/cheatsheet.html
  - https://www.nano-editor.org/dist/latest/nano.1.html
  - https://www.nano-editor.org/dist/latest/nanorc.5.html
---

# nano 공식 참조 노트

## 1. 공식 소스

| 소스            | URL                                                   | 용도                |
|-----------------|-------------------------------------------------------|---------------------|
| nano download   | https://www.nano-editor.org/download.php              | 최신 판             |
| nano cheatsheet | https://www.nano-editor.org/cheatsheet.html           | 최신 판 기본 단축키 |
| nano(1)         | https://www.nano-editor.org/dist/latest/nano.1.html   | 명령줄 옵션         |
| nanorc(5)       | https://www.nano-editor.org/dist/latest/nanorc.5.html | 설정 파일           |

## 2. 검증된 사실 (2026-11-23)

| 항목           | 값                                                                                                                                                                                                                                     | 출처                          |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| 최신 판        | 9.3                                                                                                                                                                                                                                    | download                      |
| 최신 판 단축키 | 저장 `Ctrl+S`, 다른 이름 저장 `Ctrl+O`, 종료 `Ctrl+X`, 찾기 `Ctrl+F`·`Ctrl+B`, 바꾸기 `Alt+R`, 줄 이동 `Alt+G`, 잘라내기 `Ctrl+K`, 붙여넣기 `Ctrl+U`, 복사 `Alt+6`, 되돌리기 `Alt+U`, 다시 `Alt+E`, 줄 번호 `Alt+N`, 접어 보기 `Alt+S` | cheatsheet                    |
| 7.2 단축키     | 하단 도움말 줄: `^O` Write Out, `^W` Where Is, `^\` Replace, `^K` Cut, `^U` Paste, `^X` Exit, `^C` Location, `^G` Help                                                                                                                 | Ubuntu 24.04 nano 7.2 화면    |
| 명령줄 옵션    | `+줄`, `-l` 줄 번호, `-v` 읽기 전용, `-B` 백업, `-I` 설정 파일 무시, `-T` 탭 너비, `-E` 탭을 공백으로, `-i` 자동 들여쓰기                                                                                                              | nano(1), `nano --help`        |
| 설정 파일      | `/etc/nanorc`, `~/.nanorc`. `set linenumbers`, `set tabsize`, `set tabstospaces`, `set autoindent`, `include "/usr/share/nano/*.nanorc"`                                                                                               | nanorc(5), 설치된 /etc/nanorc |

## 3. 검증 기록

- 1차: nano-editor.org의 download·cheatsheet·man 페이지에서 판과 최신 판 단축키를 확인했습니다.
- 2차: Ubuntu 24.04의 nano 7.2에서 `nano --help`, 설치된 `/etc/nanorc`, 실행 화면의 하단 도움말 줄을 확인해 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
