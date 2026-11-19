# uv: Python 패키지·버전 관리
<!-- reference: _reference/python_uv_official_notes.md -->

uv는 Astral이 Rust로 만든 Python 패키지·버전 관리 도구입니다. 실행 파일 하나로 Python 설치, 가상환경, 패키지 설치, 잠금 파일, CLI 도구 설치를 처리합니다. 이 문서는 uv가 대신하는 도구, 시스템 Python을 바꾸지 않고 설치하는 원칙, 기본 사용 예를 정리합니다. venv·pip의 기본 개념은 [가상환경](./python_virtual_env.md)을 참고합니다.

## 목차

| 섹션                                                                                                                    |
|-------------------------------------------------------------------------------------------------------------------------|
| [1. uv란](#1-uv란) / [2. 대체하는 도구](#2-대체하는-도구) / [3. 시스템 Python 보호 원칙](#3-시스템-python-보호-원칙)    |
| [4. 설치](#4-설치) / [5. 기본 사용 예](#5-기본-사용-예) / [6. 프로젝트와 도구](#6-프로젝트와-도구) / [7. 요약](#7-요약) |

---

## 1. uv란

| 항목        | 내용                                                                              |
|-------------|-----------------------------------------------------------------------------------|
| 만든 곳     | Astral (Ruff를 만든 회사)                                                         |
| 형태        | Rust로 만든 단일 실행 파일 `uv`, 보조 실행 파일 `uvx`                             |
| 최신 판     | 0.13.9 (2026-11-17)                                                               |
| 하는 일     | Python 버전 설치, 가상환경, 패키지 설치·잠금, 프로젝트 관리, CLI 도구 설치        |
| Python 출처 | Astral의 `python-build-standalone` 빌드. CPython은 공식 배포 바이너리가 없기 때문 |
| 설치 단위   | 사용자 홈 아래(`~/.local/bin`, `~/.local/share/uv`). root 권한이 필요하지 않음    |

SE 관점의 장점은 세 가지입니다.

- **도구 하나로 통일**: pyenv·venv·pip·pipx·pip-tools를 각각 설치하고 맞출 필요가 없습니다.
- **배포판과 무관한 Python**: Ubuntu·Rocky Linux 어디서든 같은 방법으로 원하는 Python 판을 설치합니다.
- **시스템 Python과 분리**: 사용자 홈에 설치하므로 `/usr/bin/python3`를 쓰는 시스템 도구에 영향을 주지 않습니다(3절).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 대체하는 도구

| 기존 도구               | 역할                         | uv 명령                                             |
|-------------------------|------------------------------|-----------------------------------------------------|
| pyenv                   | Python 버전 설치·전환        | `uv python install`, `uv python pin`                |
| venv, virtualenv        | 가상환경 생성                | `uv venv`                                           |
| pip                     | 패키지 설치·목록·제거        | `uv pip install`, `uv pip list`                     |
| pip-tools               | 의존성 잠금 파일 생성·동기화 | `uv pip compile`, `uv pip sync`                     |
| pipx                    | CLI 도구 격리 설치           | `uv tool install`, `uvx`                            |
| poetry 등 프로젝트 관리 | 의존성 선언·잠금·실행        | `uv init`, `uv add`, `uv lock`, `uv sync`, `uv run` |

- 공식 문서가 "대체한다"고 직접 밝힌 대상은 venv·virtualenv·pip·pipdeptree·pip-tools입니다. pyenv·pipx·poetry 대응은 기능 범위로 묶은 것입니다.
- `uv pip` 명령은 pip의 인터페이스와 동작을 정확히 똑같이 구현하지는 않습니다. 기존 스크립트를 옮길 때는 결과를 한 번 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 시스템 Python 보호 원칙

Linux 배포판의 `apt`·`dnf`·`cloud-init`·`netplan` 같은 시스템 도구는 `/usr/bin/python3`에 의존합니다. 이 Python을 바꾸거나 PATH에서 가리면 패키지 관리자와 서비스가 깨질 수 있습니다. uv로 Python을 설치할 때는 다음을 지킵니다.

| 원칙                            | 이유                                                                                               |
|---------------------------------|----------------------------------------------------------------------------------------------------|
| `apt`·`dnf`·`sudo`를 쓰지 않음  | 패키지 관리자로 설치하면 `/usr` 아래 파일이 바뀌고 시스템 의존성과 엮임                            |
| `/usr`·`/usr/local`에 쓰지 않음 | uv와 Python을 사용자 홈(`~/.local/bin`, `~/.local/share/uv/python`)에만 둠                         |
| `update-alternatives` 미사용    | `python3`가 가리키는 대상을 바꾸면 시스템 도구가 다른 Python으로 실행됨                            |
| `--no-bin`으로 설치             | 기본값은 `~/.local/bin`에 `python3.X`를 만듦. `--no-bin`이면 PATH에 Python 실행 파일을 만들지 않음 |
| `--default` 미사용              | 실험 기능으로 `python`·`python3` 이름까지 만들어 PATH의 `python3`를 가릴 수 있음                   |
| 설치 전후 비교                  | `/usr/bin/python3`의 링크 대상·판과 `command -v python3` 결과가 같은지 확인                        |

설치 전후 비교는 다음처럼 합니다.

```bash
# 설치 전후에 같은 결과가 나와야 함
readlink -f /usr/bin/python3
/usr/bin/python3 --version
command -v python3
```

### 전역 pip 설치를 하지 않는 이유

PEP 668에 따라 Ubuntu 23.04 이후·Debian 12 이후처럼 `EXTERNALLY-MANAGED` 표시가 있는 배포판에서는 시스템 Python에 `pip install`이 기본으로 거부됩니다. PEP 668은 `pip install`로 Fedora의 `dnf`가 깨질 수 있다는 예를 듭니다. `--break-system-packages`로 우회하지 말고 uv 가상환경에 설치합니다.

### deadsnakes PPA를 쓰지 않는 이유

| 항목             | deadsnakes PPA                                         | uv                                     |
|------------------|--------------------------------------------------------|----------------------------------------|
| 설치 위치        | `apt`·`sudo`로 `/usr/bin/python3.X` 설치               | 사용자 홈, root 불필요                 |
| 대상 배포판      | Ubuntu만 (22.04·24.04·26.04, 각 배포판 기본 판은 제외) | Ubuntu·Rocky Linux 등 glibc Linux 공통 |
| 보안 갱신        | PPA 설명에 "적시 갱신을 보장하지 않음"이라고 명시      | uv로 새 patch 판을 설치해 교체         |
| 배포판 모듈 호환 | Ubuntu 저장소의 컴파일 모듈과 대개 맞지 않음           | 가상환경 안에서 PyPI 패키지 사용       |
| 시스템 영향      | `/usr` 아래 파일이 늘고 패키지 관리자 의존성에 엮임    | `/usr`를 건드리지 않음                 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

공식 독립 설치 스크립트(`https://astral.sh/uv/install.sh`)는 간단하지만 셸 profile을 바꿀 수 있습니다. 서버나 공용 계정에서는 GitHub Releases 배포물을 받아 sha256을 대조한 뒤 `~/.local/bin`에 직접 넣는 방법을 권합니다.

```bash
# Linux x86_64 기준 (aarch64는 이름의 x86_64를 aarch64로 바꿈)
UV_VER=0.13.9
BASE=https://github.com/astral-sh/uv/releases/download/$UV_VER/uv-x86_64-unknown-linux-gnu.tar.gz

curl -fsSL -o uv.tar.gz "$BASE"
curl -fsSL -o uv.tar.gz.sha256 "$BASE.sha256"
echo "$(cut -d' ' -f1 uv.tar.gz.sha256)  uv.tar.gz" | sha256sum -c -   # uv.tar.gz: OK

tar -xzf uv.tar.gz
mkdir -p ~/.local/bin
install -m 755 uv-x86_64-unknown-linux-gnu/uv uv-x86_64-unknown-linux-gnu/uvx ~/.local/bin/
~/.local/bin/uv --version   # uv 0.13.9 (x86_64-unknown-linux-gnu)
```

Python 설치:

```bash
# PATH에 python3.X 실행 파일을 만들지 않음
~/.local/bin/uv python install 3.13 --no-bin

# 설치된 관리 Python 확인
~/.local/bin/uv python list --only-installed
```

- 위 절차를 스크립트로 만든 예는 30 저장소의 [devenv README 4절](https://github.com/siasia86/30_sia-scripts/blob/main/devenv/README.md#4-linux-python과-시스템-python-보호)과 `devenv/linux/install_python.sh`에 있습니다. 비공개 저장소라 권한이 있는 사용자만 열 수 있습니다.
- 갱신: 직접 설치한 경우 새 판을 같은 방법으로 받아 교체합니다. `uv self update`는 공식 독립 설치기로 설치했을 때만 동작하며 셸 profile을 바꿀 수 있습니다(`UV_NO_MODIFY_PATH=1`로 막음).
- 제거: `uv cache clean` 뒤 `uv python dir`·`uv tool dir`이 가리키는 디렉토리와 `~/.local/bin/uv`·`~/.local/bin/uvx`를 지웁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 사용 예

### 가상환경과 패키지 설치

```bash
cd ~/work/myscript

# Python 3.13 가상환경 생성 (없으면 관리 Python을 받아 사용)
uv venv --python 3.13 .venv

# 활성화 없이 가상환경에 설치
uv pip install --python .venv requests pyyaml

# 또는 활성화 후 설치
source .venv/bin/activate
uv pip install -r requirements.txt
python --version   # Python 3.13.18
deactivate
```

### requirements.txt 잠금

```bash
# requirements.in(직접 의존성) → requirements.txt(전체 고정 판)
uv pip compile requirements.in -o requirements.txt

# 가상환경을 잠금 파일과 정확히 맞춤 (목록에 없는 패키지는 제거)
uv pip sync --python .venv requirements.txt
```

### 자주 쓰는 Python 관리 명령

| 명령                              | 용도                                   |
|-----------------------------------|----------------------------------------|
| `uv python list --only-installed` | 설치된 Python 목록                     |
| `uv python find 3.13`             | 3.13 실행 파일 경로                    |
| `uv python pin 3.13`              | 현재 디렉토리에 `.python-version` 작성 |
| `uv python uninstall 3.12`        | 관리 Python 제거                       |
| `uv python dir`                   | 관리 Python 설치 디렉토리              |

### cron·systemd에서 쓰기

가상환경의 Python을 절대 경로로 지정하면 PATH와 활성화에 의존하지 않습니다.

```bash
# crontab 예
*/10 * * * * /home/ops/work/myscript/.venv/bin/python /home/ops/work/myscript/check.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 프로젝트와 도구

### 프로젝트 관리 (`pyproject.toml` + `uv.lock`)

```bash
uv init --python 3.13 mytool     # pyproject.toml 등 생성
cd mytool
uv add requests                  # 의존성 추가, uv.lock 갱신, .venv 동기화
uv lock                          # 잠금 파일만 다시 생성
uv sync                          # .venv를 uv.lock과 맞춤 (다른 서버·CI에서)
uv run python -c "import requests; print('ok')"   # ok
```

- `uv.lock`은 commit해서 다른 서버·CI가 같은 판을 쓰게 합니다.
- `uv run`은 실행 전에 환경을 잠금 파일과 맞춘 뒤 프로젝트 가상환경에서 명령을 실행합니다.

### CLI 도구 설치 (pipx 대체)

```bash
uv tool install ruff      # ~/.local/bin/ruff 생성, 도구별 격리 환경
uvx ruff check .          # 설치 없이 임시 환경에서 한 번 실행
uv tool list
uv tool uninstall ruff
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 요약

| 하고 싶은 일              | 명령                                      |
|---------------------------|-------------------------------------------|
| Python 설치 (PATH 미변경) | `uv python install 3.13 --no-bin`         |
| 가상환경 생성             | `uv venv --python 3.13 .venv`             |
| 패키지 설치               | `uv pip install --python .venv PACKAGE`   |
| 잠금 파일 생성·동기화     | `uv pip compile`, `uv pip sync`           |
| 프로젝트 의존성 관리      | `uv init`, `uv add`, `uv lock`, `uv sync` |
| CLI 도구 설치             | `uv tool install TOOL`, `uvx TOOL`        |

- 시스템 Python(`/usr/bin/python3`)은 그대로 두고, 작업용 Python은 uv로 사용자 홈에 설치합니다.
- 설치 전후 `/usr/bin/python3`와 `command -v python3` 결과가 같은지 확인합니다.

**관련 문서:**
- [가상환경](./python_virtual_env.md) - venv, pip, pipx 기본
- [패키지](./python_packages.md) - 패키지 구조와 import

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- uv Documentation: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/) — ★★★☆☆
- uv Documentation: [Features](https://docs.astral.sh/uv/getting-started/features/) — ★★★☆☆
- uv Documentation: [Python versions](https://docs.astral.sh/uv/concepts/python-versions/) — ★★★☆☆
- uv Documentation: [Storage](https://docs.astral.sh/uv/reference/storage/) — ★★★☆☆
- uv Releases: [github.com/astral-sh/uv/releases](https://github.com/astral-sh/uv/releases) — ★★★☆☆
- Python PEPs: [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/) — ★★★☆☆
- Launchpad: [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-19

**마지막 업데이트**: 2026-11-19

© 2026 siasia86. Licensed under CC BY 4.0.
