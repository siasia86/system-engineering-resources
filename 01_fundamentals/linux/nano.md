# nano
<!-- reference: _reference/nano_official_notes.md -->

화면 아래에 단축키가 늘 보이는 간단한 터미널 편집기입니다. Vim처럼 모드를 바꿀 필요가 없어 설정 파일을 잠깐 고칠 때 쓰기 쉽습니다. 이 문서만으로 설치 → 기본 편집 → 설정 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: GNU nano 9.3 (2026-11-23 확인)
- 예제 시험: 2026-11-23, Ubuntu 24.04의 nano 7.2에서 하단 도움말·명령줄 옵션·설정 파일을 확인. 9.x 단축키는 공식 단축키표와 대조

## 목차

| 섹션                                                                               |
|------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치와 실행](#2-설치와-실행) / [3. 단축키](#3-단축키)     |
| [4. 설정 파일](#4-설정-파일) / [5. 검증](#5-검증) / [6. 트러블슈팅](#6-트러블슈팅) |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                  |

---

## 1. 개요

| 항목       | nano                             | Vim                                 |
|------------|----------------------------------|-------------------------------------|
| 배우기     | 화면에 단축키가 보여 바로 사용   | 모드와 명령을 익혀야 함             |
| 기본 설치  | Debian·Ubuntu에 기본 포함이 많음 | 대부분 vi·vim-tiny·vim-minimal 포함 |
| 잘 맞는 일 | 설정 파일 몇 줄 수정             | 큰 파일, 반복 편집, 매크로          |

단축키 표기에서 `^`는 Ctrl, `M-`는 Alt(또는 Esc를 누른 뒤 그 키)입니다. 예: `^X` = Ctrl+X.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치와 실행

```bash
nano --version | head -1        # GNU nano, version 7.x / 9.x
sudo apt-get install -y nano    # Ubuntu / Debian
sudo dnf install -y nano        # RHEL 계열

nano /etc/hosts                 # 파일 열기 (없으면 새로 만듦)
nano +25 app.conf               # 25번째 줄로 바로 이동
nano -l app.conf                # 줄 번호 표시
nano -v /etc/passwd             # 읽기 전용으로 보기
nano -B app.conf                # 저장할 때 원본을 app.conf~로 백업
sudoedit /etc/ssh/sshd_config   # root 파일은 sudoedit로 (EDITOR=nano 설정 시)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 단축키

7.x 판과 최신 판은 기본 단축키가 일부 다릅니다. 화면 아래 도움말 줄에 그 판의 키가 나오므로, 판이 헷갈리면 아래쪽을 봅니다.

| 동작           | 7.x 이전 (Ubuntu 24.04 등) | 최신 판 (공식 단축키표)      |
|----------------|----------------------------|------------------------------|
| 저장           | `^O` (Write Out) 후 Enter  | `^S` (다른 이름 저장은 `^O`) |
| 종료           | `^X`                       | `^X`                         |
| 찾기           | `^W` (Where Is)            | `^F` (뒤로 찾기 `^B`)        |
| 바꾸기         | `^\` (Replace)             | `M-R`                        |
| 줄 이동        | `^_`                       | `M-G`                        |
| 한 줄 잘라내기 | `^K`                       | `^K`                         |
| 붙여넣기       | `^U`                       | `^U`                         |
| 한 줄 복사     | `M-6`                      | `M-6`                        |
| 되돌리기·다시  | `M-U` / `M-E`              | `M-U` / `M-E`                |
| 현재 위치      | `^C`                       | `^C`                         |
| 도움말         | `^G`                       | `^G`                         |

여러 줄을 지울 때는 `M-A`로 시작 위치를 표시한 뒤 이동하고 `^K`로 잘라냅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설정 파일

| 파일          | 범위                           |
|---------------|--------------------------------|
| `/etc/nanorc` | 시스템 전체                    |
| `~/.nanorc`   | 사용자 (시스템 설정 뒤에 읽음) |

```text
# ~/.nanorc
set linenumbers          # 줄 번호
set tabsize 4            # 탭 너비
set tabstospaces         # 탭 대신 공백
set autoindent           # 새 줄을 앞 줄 들여쓰기에 맞춤
include "/usr/share/nano/*.nanorc"   # 언어별 구문 강조
```

같은 효과를 한 번만 쓰려면 명령줄 옵션(`-l`, `-T 4`, `-E`, `-i`)을 씁니다. 기본 편집기로 쓰려면 셸 설정 파일에 `export EDITOR=nano`를 넣습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 검증

| 순서 | 확인 내용      | 방법                                             | 기대 결과             |
|------|----------------|--------------------------------------------------|-----------------------|
| 1    | 설치와 판      | `nano --version \| head -1`                      | 판 번호               |
| 2    | 단축키 판 확인 | nano를 열어 화면 아래 도움말 줄 확인             | 저장·찾기 키가 표시됨 |
| 3    | 설정 적용      | `~/.nanorc`에 `set linenumbers`를 넣고 파일 열기 | 왼쪽에 줄 번호        |
| 4    | 설정 오류      | 잘못된 줄이 있으면 열 때 화면 아래에 오류 표시   | 오류 메시지가 없음    |
| 5    | 저장           | 고친 뒤 저장·종료, `cat`으로 확인                | 변경 내용 반영        |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 트러블슈팅

| 증상                                 | 원인                                  | 해결 방법                                                          |
|--------------------------------------|---------------------------------------|--------------------------------------------------------------------|
| `^S`를 눌렀더니 화면이 멈춤 (옛 판)  | 터미널 흐름 제어(XOFF)로 해석됨       | `^Q`로 풀고 `^O`로 저장                                            |
| 저장할 때 `Permission denied`        | 파일 쓰기 권한 없음                   | `sudoedit 파일` 또는 `sudo nano 파일`                              |
| 긴 줄이 화면에서 잘림                | 접어 보기가 꺼져 있음                 | `M-S`로 접어 보기 전환 (최신 판 단축키표)                          |
| YAML 붙여넣기 뒤 들여쓰기가 망가짐   | `autoindent`가 붙여넣은 줄에도 적용됨 | `~/.nanorc`의 `set autoindent`를 빼거나 `nano -I`로 연 뒤 붙여넣기 |
| 탭이 공백으로 바뀌어 Makefile이 깨짐 | `tabstospaces` 설정                   | 그 파일은 `nano -I`(설정 파일 무시)로 열기                         |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Vim](./vim.md) — 큰 파일과 반복 편집
- [텍스트 처리](./text_processing.md) — 편집기 없이 sed로 일괄 수정
- [Bash 스크립트](./bash_scripting.md) — `EDITOR` 같은 셸 설정

---

## 참고 자료

- GNU nano: [nano cheatsheet](https://www.nano-editor.org/cheatsheet.html) — ★★★☆☆
- GNU nano: [nano(1)](https://www.nano-editor.org/dist/latest/nano.1.html) · [nanorc(5)](https://www.nano-editor.org/dist/latest/nanorc.5.html) — ★★★☆☆
- GNU nano: [Download](https://www.nano-editor.org/download.php) — 9.3 확인 2026-11-23 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
