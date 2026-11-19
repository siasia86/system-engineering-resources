---
name: python-uv-official-notes
description: uv(Astral의 Python 패키지·버전 관리 도구) 공식 문서 기반 참조 노트. python_uv.md, python_virtual_env.md 작성/검토 시 참조.
tags:
  - python
  - uv
  - package-manager
last_checked: 2026-11-19
sources:
  - https://github.com/astral-sh/uv/releases
  - https://docs.astral.sh/uv/getting-started/installation/
  - https://docs.astral.sh/uv/getting-started/features/
  - https://docs.astral.sh/uv/concepts/python-versions/
  - https://docs.astral.sh/uv/reference/storage/
  - https://docs.astral.sh/uv/reference/cli/
  - https://peps.python.org/pep-0668/
  - https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
---

# uv 공식 참조 노트

## 1. 판 현황 (확인일: 2026-11-19)

출처: github.com/astral-sh/uv/releases

| 항목          | 내용                                                                          |
|---------------|-------------------------------------------------------------------------------|
| 최신 판       | 0.13.9 (2026-11-17 게시)                                                      |
| Linux 배포물  | `uv-x86_64-unknown-linux-gnu.tar.gz`, `uv-aarch64-unknown-linux-gnu.tar.gz`   |
| 무결성 파일   | 각 배포물과 같은 이름에 `.sha256`을 붙인 파일                                 |
| 구현 언어     | Rust, 단일 실행 파일 `uv`와 보조 실행 파일 `uvx`                              |
| Python 배포판 | Astral의 `python-build-standalone` 빌드 (CPython 공식 배포 바이너리가 없어서) |

---

## 2. 명령 분류와 대체 도구 (확인일: 2026-11-19)

출처: docs.astral.sh/uv/getting-started/features/

| 분류        | 명령                                                                  | 공식 문서가 밝힌 대체 대상     |
|-------------|-----------------------------------------------------------------------|--------------------------------|
| Python 버전 | `uv python install`·`list`·`find`·`pin`·`uninstall`                   | (버전 관리, 예: pyenv 역할)    |
| 스크립트    | `uv run`, `uv add --script`, `uv remove --script`                     | -                              |
| 프로젝트    | `uv init`·`add`·`remove`·`sync`·`lock`·`run`·`tree`·`build`·`publish` | (poetry 등 프로젝트 관리 역할) |
| 도구        | `uvx`(=`uv tool run`), `uv tool install`·`uninstall`·`list`           | (pipx 역할)                    |
| 가상환경    | `uv venv`                                                             | `venv`, `virtualenv`           |
| 패키지      | `uv pip install`·`show`·`freeze`·`check`·`list`·`uninstall`·`tree`    | `pip`, `pipdeptree`            |
| 잠금        | `uv pip compile`, `uv pip sync`                                       | `pip-tools`                    |
| 유틸리티    | `uv cache clean`·`prune`·`dir`, `uv python dir`, `uv self update`     | -                              |

🟡 공식 문서가 "replacing"이라고 직접 적은 대상은 `venv`·`virtualenv`·`pip`·`pipdeptree`·`pip-tools`입니다. pyenv·pipx·poetry 대응은 기능 범위로 정리한 것입니다. 문서는 pip 인터페이스 명령이 원래 도구의 인터페이스와 동작을 "정확히 구현하지는 않는다"고 적습니다.

---

## 3. Python 실행 파일과 저장 위치 (확인일: 2026-11-19)

출처: docs.astral.sh/uv/concepts/python-versions/, docs.astral.sh/uv/reference/storage/, docs.astral.sh/uv/reference/cli/

| 항목                      | Linux 기본값                                                            | 바꾸는 변수             |
|---------------------------|-------------------------------------------------------------------------|-------------------------|
| 관리 Python 설치 위치     | `~/.local/share/uv/python`                                              | `UV_PYTHON_INSTALL_DIR` |
| Python 실행 파일 위치     | `$XDG_BIN_HOME`, `$XDG_DATA_HOME/../bin`, `$HOME/.local/bin` 중 첫 번째 | `UV_PYTHON_BIN_DIR`     |
| 도구 실행 파일 위치       | 위와 같은 실행 디렉토리                                                 | `UV_TOOL_BIN_DIR`       |
| uv 실행 파일(설치기 사용) | 위와 같은 실행 디렉토리                                                 | `UV_INSTALL_DIR`        |
| 캐시                      | `$XDG_CACHE_HOME/uv`, 없으면 `$HOME/.cache/uv`                          | `XDG_CACHE_HOME` 등     |

- 기본 동작: `uv python install 3.12`는 `~/.local/bin`에 `python3.12`를 만듭니다. 공식 문서는 "uv installs Python executables into your `PATH` by default"라고 적습니다.
- `--default`(실험 기능): `python`·`python3` 이름의 실행 파일까지 만듭니다.
- `--no-bin`: "Do not install a Python executable into the bin directory." `UV_PYTHON_INSTALL_BIN=0`과 같습니다.
- 덮어쓰기: uv가 관리하는 실행 파일만 덮어씁니다. 다른 실행 파일은 `--force`가 있어야 덮어씁니다.
- Python 탐색: 관리 설치를 먼저 보고, 그다음 PATH의 `python`·`python3`·`python3.x`를 봅니다. 시스템 Python은 가장 새 판이 아니라 먼저 찾은 호환 판을 씁니다.
- `python-preference` 기본값은 `managed`입니다. `--managed-python`은 관리 설치만, `--no-managed-python`은 시스템 설치만 씁니다.

---

## 4. 설치·갱신·제거 (확인일: 2026-11-19)

출처: docs.astral.sh/uv/getting-started/installation/

| 방법                    | 내용                                                                            |
|-------------------------|---------------------------------------------------------------------------------|
| 공식 독립 설치 스크립트 | `https://astral.sh/uv/install.sh`를 받아 `sh`로 실행, 판을 URL에 고정할 수 있음 |
| GitHub Releases         | 모든 지원 플랫폼의 바이너리를 직접 받음                                         |
| PyPI                    | `pipx install uv` 권장(격리 환경)                                               |
| 패키지 관리자           | Homebrew, MacPorts, WinGet, Scoop                                               |
| 갱신                    | 독립 설치기로 설치했을 때만 `uv self update`. 다른 방법은 그 관리자로 갱신      |

- 셸 profile: 공식 문서는 갱신이 설치기를 다시 실행해 셸 profile을 바꿀 수 있다고 적고, `UV_NO_MODIFY_PATH=1`로 막는다고 안내합니다.
- 제거: `uv cache clean` 뒤 `uv python dir`·`uv tool dir`이 가리키는 디렉토리를 지우고, `~/.local/bin/uv`·`~/.local/bin/uvx`를 지웁니다. 0.5.0 이전 판은 `~/.cargo/bin`에 설치되었습니다.

---

## 5. 시스템 Python 관련 근거 (확인일: 2026-11-19)

| 출처            | 내용                                                                                                                                                                                                                                                        |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PEP 668 (Final) | 배포판은 stdlib 디렉토리에 `EXTERNALLY-MANAGED` 파일을 둡니다. pip는 기본적으로 전역 설치를 거부하고 가상환경을 안내합니다. `pip install`로 Fedora의 `dnf`가 깨질 수 있다는 예를 듭니다                                                                     |
| deadsnakes PPA  | "more recent Python versions packaged for Ubuntu". 22.04·24.04·26.04용이며 각 배포판 기본 판은 제외합니다. "no guarantee of timely updates in case of security problems"라고 밝힙니다. Ubuntu 저장소의 컴파일 모듈은 이 PPA 인터프리터와 대개 맞지 않습니다 |

---

## 6. 실행 확인 (확인일: 2026-11-19)

| 환경                                 | 확인한 내용                                                                                                                                                                                                                                                          |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ubuntu:24.04` 컨테이너, 일반 사용자 | GitHub 배포물 sha256 대조 OK, uv 0.13.9. `uv python install 3.13 --no-bin`으로 3.13.18 설치 뒤 `~/.local/bin`에 `uv`·`uvx`만 있음. `uv venv --python 3.13 .venv`, `uv pip install --python .venv requests`, `uv init`·`uv add`·`uv run`, `uv tool install ruff` 동작 |
| 30 저장소 실기 시험 [보고]           | Ubuntu 24.04 사용자 단위 설치에서 uv 0.13.9, Python 3.13.18, 설치 전후 `/usr/bin/python3`와 `command -v python3` 동일, `~/.local/bin`에 `python3.X` 미생성 (30 devenv README 6절, 2026-11-19)                                                                        |

🟡 컨테이너 이미지에는 시스템 Python이 없어 시스템 Python 불변은 컨테이너에서 확인하지 못했습니다. 이 항목은 30의 실기 시험 결과를 인용합니다.

---

**작성일**: 2026-11-19

**마지막 업데이트**: 2026-11-19

© 2026 siasia86. Licensed under CC BY 4.0.
