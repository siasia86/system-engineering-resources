# Blender 설치
<!-- reference: _reference/blender_official_notes.md -->

Blender는 모델링·스컬프팅·애니메이션·렌더·합성을 한 프로그램에서 하는 무료 오픈소스(GPL) 3D 제작 도구입니다. 이 문서는 판 고르기 → OS별 설치 → 첫 실행 확인 → 설정 폴더 → 여러 판 함께 쓰기 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-09 태그), LTS 5.2·4.5 (2026-11-26 확인)
- 예제 시험: 2026-11-26, Python 3.13 컨테이너에 `bpy` 5.3.0(Blender를 Python 모듈로 빌드한 패키지)을 설치해 판, 설정 폴더, 기본 환경설정을 확인. 매뉴얼은 자동 조회가 막혀(HTTP 403) 시스템 요구사항은 검색 요약으로만 확인했고 화면 설치 과정은 실행하지 않았음. 같은 날 뒤늦게 공식 내려받기 폴더(`download.blender.org/release/Blender5.3/`)가 열려 파일 이름·체크섬을 확인하고, Linux 압축판을 컨테이너에서 풀어 실행함

## 목차

| 섹션                                                                                      |
|-------------------------------------------------------------------------------------------|
| [1. 판 고르기](#1-판-고르기) / [2. 시스템 요구사항](#2-시스템-요구사항)                   |
| [3. OS별 설치](#3-os별-설치) / [4. 첫 실행 확인](#4-첫-실행-확인)                         |
| [5. 설정 폴더와 이전](#5-설정-폴더와-이전) / [6. 여러 판 함께 쓰기](#6-여러-판-함께-쓰기) |
| [7. 화면 없는 환경](#7-화면-없는-환경) / [8. 트러블슈팅](#8-트러블슈팅)                   |

---

## 1. 판 고르기

Blender는 약 4개월마다 새 판을 내고, 1년에 한 번 LTS(Long-term Support) 판을 정해 2년 동안 버그·보안 수정을 냅니다.

| 계열     | 2026-11 기준   | 지원        | 고르는 경우                                     |
|----------|----------------|-------------|-------------------------------------------------|
| 최신판   | 5.3.0          | 다음 판까지 | 새 기능이 필요할 때, 개인 학습                  |
| LTS (신) | 5.2.x (5.2.5)  | 2028-07까지 | 팀·회사 작업, 애드온 호환성이 중요한 프로젝트   |
| LTS (구) | 4.5.x (4.5.17) | 2027-07까지 | 4.x 파일·애드온을 그대로 유지해야 하는 프로젝트 |

- 판 번호는 `주.부.수정`입니다. 같은 `주.부` 안의 수정판(5.2.4 → 5.2.5)은 버그 수정만 들어 있어 바로 올려도 됩니다.
- 새 판에서 저장한 `.blend` 파일은 옛 판에서 열 때 새 기능이 빠지거나 열리지 않을 수 있습니다. 팀은 판을 하나로 맞춥니다.
- 판마다 내장 Python 판이 하나로 정해져 있습니다(5.3은 Python 3.13). 애드온이 쓰는 외부 Python 패키지는 이 판에 맞아야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 시스템 요구사항

| 항목 | 최소                      | 권장  |
|------|---------------------------|-------|
| CPU  | 4코어, SSE4.2 지원        | 8코어 |
| RAM  | 8GB                       | 32GB  |
| GPU  | VRAM 2GB, OpenGL 4.3 이상 | -     |

- 5.0부터 Windows·Linux의 최소 GPU가 NVIDIA GeForce 900(Maxwell), AMD GCN 4세대, Intel Kaby Lake 이상입니다. 더 오래된 GPU도 켜질 수는 있지만 지원 대상이 아닙니다.
- Cycles를 GPU로 렌더하려면 별도 조건이 있습니다. NVIDIA OptiX는 compute capability 5.0 이상과 드라이버 575 이상, AMD HIP는 RDNA1 이상입니다.
- 위 값은 공식 요구사항 페이지의 검색 요약입니다. 설치 전에 [공식 요구사항](https://www.blender.org/download/requirements/)에서 다시 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. OS별 설치

공식 내려받기 페이지(https://www.blender.org/download/)에서 OS에 맞는 파일을 받습니다. 지난 판과 LTS 수정판은 https://download.blender.org/release/ 에 판별 폴더로 있습니다.

### 3.1 Windows

| 방식             | 특징                                                 |
|------------------|------------------------------------------------------|
| 설치 프로그램    | 시작 메뉴 등록, `.blend` 파일 연결                   |
| 압축판(portable) | 압축을 풀면 바로 실행, 여러 판을 폴더별로 둘 수 있음 |
| Microsoft Store  | 자동 업데이트                                        |
| Steam            | 자동 업데이트, 베타 브랜치로 판 고르기               |

### 3.2 macOS

- 디스크 이미지(`.dmg`)를 열어 `Blender.app`을 응용 프로그램 폴더로 끌어 놓습니다.
- 5.3.0 내려받기 폴더의 macOS 파일은 `blender-5.3.0-macos-arm64.dmg`(Apple Silicon) 하나입니다. Intel Mac용 파일은 목록에 없었습니다.

### 3.3 Linux

압축판을 `/opt`에 풀고 실행 파일을 연결하는 방법이 배포판과 상관없이 같습니다.

```bash
# 파일 이름은 내려받은 판에 맞게 바꿈
VER=5.3.0
sudo tar -xf "blender-${VER}-linux-x64.tar.xz" -C /opt
sudo ln -sfn "/opt/blender-${VER}-linux-x64" /opt/blender
sudo ln -sfn /opt/blender/blender /usr/local/bin/blender
blender --version
```

| 방식                    | 특징                                                            |
|-------------------------|-----------------------------------------------------------------|
| 공식 압축판 (`.tar.xz`) | 공식 빌드 그대로, 판별로 폴더를 나눠 함께 둘 수 있음            |
| Snap                    | `sudo snap install blender --classic`, 자동 업데이트            |
| Steam                   | 자동 업데이트                                                   |
| 배포판 패키지           | `apt`·`dnf`로 설치, 판이 늦거나 일부 기능이 빠진 빌드일 수 있음 |

- 받은 파일은 같은 폴더의 체크섬 파일 `blender-5.3.0.sha256`(모든 OS 파일의 값이 한 파일에)으로 대조합니다.

```bash
grep linux-x64 blender-5.3.0.sha256 | sha256sum -c -
# blender-5.3.0-linux-x64.tar.xz: OK
```

- 5.3.0 파일: Linux `linux-x64.tar.xz`, Windows `windows-x64`·`windows-arm64`의 `.msi`·`.msix`·`.zip`, macOS `macos-arm64.dmg`, 체크섬 `.sha256`·`.md5`.
- 압축을 풀면 `blender` 실행 파일, `5.3/`(datafiles·extensions·python·scripts), `lib/`, `blender.desktop`, 아이콘이 있습니다. 화면 없는 서버에서도 X11·GL 라이브러리가 필요합니다([명령줄과 일괄 렌더](./blender_cli_batch_render.md) 8절).
- 압축판의 `blender.desktop`과 아이콘을 `~/.local/share/applications/`에 복사하면 데스크톱 메뉴에 나옵니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 첫 실행 확인

1. 판 확인: 시작 화면(splash) 또는 `Help > About Blender`, 명령줄은 `blender --version`.
2. GPU 확인: `Edit > Preferences > System`에서 Cycles 렌더 장치(CUDA·OptiX·HIP·oneAPI·Metal)를 고르고 GPU가 목록에 나오는지 봅니다.
3. 화면 크기: 고해상도 모니터는 `Preferences > Interface > Resolution Scale`로 글자 크기를 키웁니다.
4. 온라인 접근: 5.3 초기값은 꺼짐입니다(컨테이너에서 확인). 확장(Extensions) 저장소에서 애드온을 받으려면 `Preferences > System > Network`에서 켭니다.

초기 환경설정 값(5.3.0, 컨테이너에서 확인):

| 항목           | 초기값                      |
|----------------|-----------------------------|
| 실행 취소 단계 | 32                          |
| 자동 저장      | 켬, 2분마다 임시 파일       |
| 저장 판 수     | 1 (`.blend1` 백업 파일 1개) |
| 단위           | Metric, 미터, 배율 1.0      |
| GPU 백엔드     | Vulkan (Linux 확인값)       |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 설정 폴더와 이전

환경설정, 시작 파일, 애드온은 판별 사용자 폴더에 저장됩니다.

| OS      | 사용자 폴더                                                        |
|---------|--------------------------------------------------------------------|
| Linux   | `~/.config/blender/5.3/` (컨테이너 확인)                           |
| Windows | `%APPDATA%\Blender Foundation\Blender\5.3\` (매뉴얼 기준, 미확인)  |
| macOS   | `~/Library/Application Support/Blender/5.3/` (매뉴얼 기준, 미확인) |

```text
5.3/
├── config/      userpref.blend(환경설정), startup.blend(시작 장면)
├── scripts/     사용자 스크립트·옛 방식 애드온
└── extensions/  확장 플랫폼에서 받은 애드온·테마
```

- 새 판을 처음 켜면 시작 화면에 "Load Previous Settings"가 나옵니다. 누르면 이전 판 폴더를 복사합니다.
- `File > Defaults > Save Startup File`은 지금 장면을 새 파일의 시작 장면으로 저장합니다. 되돌리려면 `File > Defaults > Load Factory Settings`를 씁니다.
- 설정을 초기화하려면 Blender를 끄고 해당 판 폴더의 이름을 바꿉니다(지우지 말고 보관).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 여러 판 함께 쓰기

- 압축판은 판별 폴더(`/opt/blender-5.2.5-linux-x64`, `/opt/blender-5.3.0-linux-x64`)로 나눠 두면 함께 쓸 수 있습니다. 사용자 폴더도 `5.2/`, `5.3/`으로 나뉘어 설정이 섞이지 않습니다.
- 압축판 폴더 안에 `portable` 폴더를 만들면 설정을 사용자 폴더 대신 그 안에 저장합니다(USB·공용 PC용). 동작은 매뉴얼 기준이며 이 문서에서는 시험하지 않았습니다.
- 팀 작업은 프로젝트 문서에 판(예: 5.2 LTS)을 적고, 애드온 목록도 함께 적어 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 화면 없는 환경

렌더 서버·CI처럼 화면이 없는 곳에서는 두 가지 방법이 있습니다.

| 방법                  | 사용                                            | 비고                                  |
|-----------------------|-------------------------------------------------|---------------------------------------|
| `blender -b` (압축판) | `blender -b scene.blend -o //out/frame_#### -a` | 실행 파일 그대로, 명령줄 렌더         |
| `bpy` 모듈 (PyPI)     | `pip install bpy==5.3.0` 뒤 `import bpy`        | Python 3.13 전용, 실행 파일·화면 없음 |

- 명령줄 인수는 쓴 순서대로 실행됩니다. `.blend` 파일을 먼저 읽고 `-o`, `-f`/`-a`를 그 뒤에 둡니다. 파일을 읽으면 출력 경로가 파일 값으로 덮이기 때문입니다.
- `bpy`를 최소 컨테이너(`python:3.13-slim`)에 설치하면 `import bpy`가 `libX11.so.6`이 없다며 실패합니다. 컨테이너에 `libx11-6 libxrender1 libxxf86vm1 libxfixes3 libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libglib2.0-0`을 설치하면 불러오기와 EEVEE·Cycles(CPU)·Workbench 렌더가 됩니다(시험 확인).

```bash
python -c "import bpy; print(bpy.app.version_string, bpy.app.build_date)"
# 5.3.0 b'2026-11-10'
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                 | 원인                                 | 해결                                                |
|--------------------------------------|--------------------------------------|-----------------------------------------------------|
| 켜자마자 꺼지거나 화면이 검게 나옴   | GPU 드라이버가 오래됨, 최소 GPU 미달 | 드라이버 갱신, 2절 GPU 조건 확인                    |
| Cycles 장치 목록에 GPU가 없음        | 드라이버 판 부족, 지원하지 않는 세대 | NVIDIA 드라이버 575 이상, AMD RDNA1 이상 확인       |
| 애드온 목록이 비어 있고 받을 수 없음 | 온라인 접근이 꺼짐(초기값)           | `Preferences > System > Network`에서 온라인 접근 켬 |
| 새 판에서 이전 설정이 사라짐         | 사용자 폴더가 판별로 나뉨            | 시작 화면 "Load Previous Settings" 또는 폴더 복사   |
| `import bpy`에서 `libX11.so.6` 오류  | 최소 이미지에 X11·GL 런타임 없음     | 7절의 라이브러리 설치                               |
| 배포판 패키지에서 일부 기능이 없음   | 배포판 빌드 옵션 차이                | 공식 압축판 사용                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 화면 구성](./blender_interface.md) — 작업 공간·편집기·모드

---

## 참고 자료

- Blender: [Download](https://www.blender.org/download/) · [Requirements](https://www.blender.org/download/requirements/) · [LTS](https://www.blender.org/download/lts/) — ★★★☆☆
- Blender Manual: [Installing Blender](https://docs.blender.org/manual/en/latest/getting_started/installing/index.html) — ★★★☆☆
- GitHub 미러: [blender/blender 태그](https://github.com/blender/blender/tags) — 5.3.0·5.2.5·4.5.17 확인 2026-11-26 — ★★★☆☆
- PyPI: [bpy](https://pypi.org/project/bpy/) — 5.3.0, Python 3.13 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-26

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
