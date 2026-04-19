# Python 가상환경과 의존성 관리

venv, pip, 프로젝트 환경 관리 가이드입니다.

## 목차
- [venv](#venv)
- [pip](#pip)
- [requirements.txt](#requirementstxt)
- [pyenv](#pyenv)
- [프로젝트 구조](#프로젝트-구조)
- [실전 팁](#실전-팁)
- [요약](#요약)

---

## venv

### 생성/활성화/비활성화

```bash
# 가상환경 생성
python3 -m venv .venv

# 활성화
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# 비활성화
deactivate

# 확인
which python    # /path/to/.venv/bin/python
python --version
```

### 가상환경 삭제

```bash
# 디렉토리 삭제만 하면 됨
rm -rf .venv
```

### 왜 가상환경을 쓰는가?

```
프로젝트 A: requests==2.28, flask==2.3
프로젝트 B: requests==2.31, django==4.2

→ 시스템 전역에 설치하면 버전 충돌
→ 가상환경으로 프로젝트별 격리
```

---

## pip

### 기본 명령

```bash
# 설치
pip install requests
pip install requests==2.31.0        # 특정 버전
pip install 'requests>=2.28,<3.0'   # 버전 범위
pip install package1 package2       # 여러 패키지

# 업그레이드
pip install --upgrade requests
pip install --upgrade pip           # pip 자체 업그레이드

# 삭제
pip uninstall requests

# 목록
pip list                    # 설치된 패키지
pip list --outdated         # 업데이트 가능한 패키지
pip show requests           # 패키지 정보
```

### freeze

```bash
# 현재 설치된 패키지 목록 출력
pip freeze
# requests==2.31.0
# urllib3==2.1.0

# requirements.txt 생성
pip freeze > requirements.txt
```

---

## requirements.txt

### 형식

```txt
# 정확한 버전 (권장)
requests==2.31.0
flask==3.0.0

# 버전 범위
pyyaml>=6.0,<7.0
boto3~=1.34.0    # 1.34.x 허용

# 최소 버전
paramiko>=3.0

# Git 저장소
# git+https://github.com/user/repo.git@main

# 개발 의존성은 별도 파일
# -r requirements-dev.txt
```

### 설치

```bash
# requirements.txt에서 설치
pip install -r requirements.txt

# 개발 환경
pip install -r requirements-dev.txt
```

### requirements-dev.txt 예시

```txt
-r requirements.txt
pytest==8.0.0
black==24.1.0
flake8==7.0.0
mypy==1.8.0
```

---

## pyenv

### 설치 및 사용

```bash
# 설치 (Linux)
curl https://pyenv.run | bash

# .bashrc에 추가
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Python 버전 설치
pyenv install 3.12.2
pyenv install 3.11.8

# 버전 전환
pyenv global 3.12.2       # 시스템 전체
pyenv local 3.11.8        # 현재 디렉토리 (.python-version 생성)
pyenv shell 3.12.2        # 현재 셸만

# 확인
pyenv versions
pyenv version
```

---

## 프로젝트 구조

### 기본 구조

```
my-project/
├── .venv/                  # 가상환경 (git 제외)
├── .python-version         # pyenv 버전 지정
├── .gitignore
├── requirements.txt        # 운영 의존성
├── requirements-dev.txt    # 개발 의존성
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
└── README.md
```

### .gitignore

```gitignore
# 가상환경
.venv/
venv/
env/

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# IDE
.idea/
.vscode/
*.swp
```

---

## 실전 팁

### 새 프로젝트 시작

```bash
mkdir my-project && cd my-project
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install requests pyyaml  # 필요한 패키지
pip freeze > requirements.txt
```

### 기존 프로젝트 참여

```bash
git clone <repo-url>
cd <project>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### pipx (CLI 도구 격리 설치)

```bash
# 설치
pip install pipx
pipx ensurepath

# CLI 도구를 격리된 환경에 설치
pipx install black
pipx install ansible
pipx install httpie

# 시스템 어디서든 사용 가능
black --check .
ansible --version
```

### uv (차세대 패키지 관리자)

```bash
# 설치
pip install uv

# 가상환경 생성 (pip보다 10~100배 빠름)
uv venv .venv
source .venv/bin/activate

# 패키지 설치
uv pip install requests pyyaml
uv pip install -r requirements.txt

# requirements.txt 생성
uv pip freeze > requirements.txt
```

---

## 요약

| 도구 | 용도 |
|------|------|
| `venv` | 프로젝트별 가상환경 생성 |
| `pip` | 패키지 설치/관리 |
| `pip freeze` | 의존성 목록 추출 |
| `requirements.txt` | 의존성 명세 |
| `pyenv` | Python 버전 관리 |
| `pipx` | CLI 도구 격리 설치 |

**관련 문서:**
- [패키지](./python_packages.md) - 패키지 구조
- [subprocess](./python_subprocess.md) - 외부 명령 실행
