# Blender 트러블슈팅
<!-- reference: _reference/blender_official_notes.md -->

Blender가 켜지지 않거나, 렌더 결과가 이상하거나, 작업이 날아갔을 때 원인을 좁히는 순서를 정리합니다. 각 분야 문서의 트러블슈팅 표는 그 문서에 두고, 이 문서는 여러 분야에 걸친 공통 문제와 진단 방법을 다룹니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, Blender 5.3.0 Linux판을 컨테이너에서 실행해 라이브러리 없는 환경의 오류, 충돌 로그 생성, 자동 저장 기본값, 텍스처 누락 렌더, `.blend` 안 스크립트 자동 실행 옵션, 로그·디버그 옵션을 확인. GPU 드라이버 문제, 화면(Windows·macOS) 관련 증상, 실제 작업 중 충돌 복구는 확인하지 않았음

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 진단 순서](#1-진단-순서) / [2. 실행되지 않음](#2-실행되지-않음) / [3. 충돌과 로그](#3-충돌과-로그)   |
| [4. 작업 복구](#4-작업-복구) / [5. 스크립트 자동 실행](#5-스크립트-자동-실행)                            |
| [6. 렌더 결과 문제](#6-렌더-결과-문제) / [7. 텍스처 누락](#7-텍스처-누락) / [8. 증상별 표](#8-증상별-표) |

---

## 1. 진단 순서

| 순서 | 확인                        | 방법                                                      |
|------|-----------------------------|-----------------------------------------------------------|
| 1    | 판                          | `blender --version`, 화면 `Help > About`                  |
| 2    | 사용자 설정·애드온 때문인지 | `blender --factory-startup`으로 실행해 같은 증상인지 확인 |
| 3    | 파일 때문인지               | 새 파일에서 같은 조작을 해 봄                             |
| 4    | GPU·드라이버 때문인지       | Cycles를 CPU로, 또는 `--gpu-backend`를 바꿔 실행          |
| 5    | 로그                        | `--log`·`--debug-*` 옵션, 충돌 로그(3절)                  |

- `--factory-startup`으로 문제가 사라지면 원인은 사용자 설정이나 애드온입니다. 애드온을 하나씩 꺼서 찾습니다.
- 설정을 완전히 초기화하려면 Blender를 끈 뒤 설정 폴더(Linux `~/.config/blender/5.3/`)의 이름을 바꿉니다. 지우지 말고 옮겨 두면 되돌릴 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 실행되지 않음

| 증상                                                | 원인                                         | 조치                                                                            |
|-----------------------------------------------------|----------------------------------------------|---------------------------------------------------------------------------------|
| `error while loading shared libraries: libX11.so.6` | Linux 압축판에 필요한 시스템 라이브러리 없음 | X11·GL 라이브러리 설치([명령줄과 일괄 렌더](./blender_cli_batch_render.md) 8절) |
| 창이 뜨자마자 꺼짐, GPU 관련 오류                   | 오래된 GPU·드라이버                          | 드라이버 업데이트, 지원 GPU 확인([Blender 설치](./blender_install.md))          |
| GPU 백엔드 문제로 의심                              | OpenGL·Vulkan 백엔드 차이                    | `blender --gpu-backend opengl` 또는 `vulkan`으로 비교                           |
| 설정·애드온을 읽다 멈춤                             | 깨진 사용자 설정, 문제 있는 애드온           | `--factory-startup`으로 실행                                                    |

- 라이브러리 오류는 GPU가 없는 서버·컨테이너에서도 납니다. 화면 없이(`-b`) 실행해도 실행 파일이 X11·GL 라이브러리를 링크하기 때문입니다.
- `--gpu-backend`의 값은 `opengl`, `vulkan`입니다(5.3 도움말). GPU 문제는 이 문서에서 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 충돌과 로그

Blender가 비정상 종료하면 충돌 로그를 임시 폴더에 씁니다.

```text
Writing: /tmp/blender.crash.txt
# Blender 5.3.0, Commit date: 2026-11-09 22:11, Hash 02f0899d78e3

# backtrace
blender() [0x14ba56d]
...
```

- 시험에서 강제로 충돌시키자 종료 코드 139(Segmentation fault)와 함께 위 파일이 생겼습니다. 위치는 Linux 임시 폴더의 `/tmp/blender.crash.txt`입니다(저장하지 않은 새 장면에서 시험).
- 버그를 보고할 때는 판·해시가 있는 이 파일과 재현 순서, `Help > Report a Bug`에서 모이는 시스템 정보를 함께 냅니다.

로그 옵션(5.3 도움말):

| 옵션                    | 내용                                                        |
|-------------------------|-------------------------------------------------------------|
| `--log "<분류>"`        | 분류별 로그. `"*"` 전부, `"render,cycles"`, `"*,^operator"` |
| `--log-level <수준>`    | 로그 수준                                                   |
| `--log-file <경로>`     | 로그를 파일로                                               |
| `--log-list-categories` | 분류 목록 출력                                              |
| `--debug-python`        | Python 디버그 메시지                                        |
| `--debug-gpu`           | GPU 디버그 정보(OpenGL 4.3 이상)                            |
| `--debug-cycles`        | Cycles 디버그                                               |
| `--debug-all`           | 모든 디버그                                                 |

- Windows에서는 콘솔 창이 기본으로 숨겨져 있어 `Window > Toggle System Console`로 봅니다. 5.3 메뉴 스크립트에서 이 항목은 Windows일 때만 표시됩니다(Windows 화면은 미확인).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 작업 복구

| 기능                   | 기본값 (5.3 시험)        | 복구 방법                             |
|------------------------|--------------------------|---------------------------------------|
| 자동 저장              | 켜짐, 2분마다            | `File > Recover > Auto Save...`       |
| 종료 시 세션 저장      | 임시 폴더에 `quit.blend` | `File > Recover > Last Session`       |
| 저장할 때 이전 판 보관 | 1개(`.blend1`)           | `.blend1`을 `.blend`로 이름 바꿔 열기 |
| Undo 단계              | 32                       | `Ctrl+Z`                              |

- 임시 폴더 설정(`temporary_directory`)이 비어 있으면 OS 임시 폴더를 씁니다(시험 값 `/tmp/blender_xxxxxx/` 형태의 세션 폴더).
- 임시 폴더는 재부팅 때 지워질 수 있습니다. 오래 작업한다면 Preferences > File Paths에서 임시 폴더를 지워지지 않는 위치로 바꿉니다.
- `quit.blend`·자동 저장 파일 이름과 복구 메뉴는 공식 매뉴얼 기준이며, 이 문서에서는 설정 기본값만 확인했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 스크립트 자동 실행

`.blend` 파일에는 Python 스크립트(텍스트 블록, Python 드라이버)가 들어 있을 수 있습니다. 남이 준 파일의 코드가 열자마자 실행되지 않도록 자동 실행은 기본으로 꺼져 있습니다.

```text
scripts disabled for "/w/out/auto.blend", skipping 'startup.py'
```

| 실행                               | 파일 안 등록 스크립트 | `bpy.app.autoexec_fail` |
|------------------------------------|-----------------------|-------------------------|
| `blender -b auto.blend` (기본)     | 실행 안 함            | `True`                  |
| `blender -b -y auto.blend`         | 실행                  | `False`                 |
| `blender -b --enable-autoexec ...` | 실행                  | `False`                 |
| `blender -b -Y auto.blend`         | 실행 안 함            | `True`                  |

- 켜는 옵션은 소문자 `-y`(`--enable-autoexec`)이고 대문자 `-Y`는 끄는 옵션(`--disable-autoexec`, 기본값)입니다. 헷갈리기 쉬우니 스크립트에는 긴 이름을 씁니다.
- 리깅에서 Python 드라이버를 쓰는 파일은 자동 실행이 꺼져 있으면 움직임이 다르게 나옵니다. 믿을 수 있는 파일만 이번 실행에 `--enable-autoexec`로 열거나, Preferences > Save & Load에서 믿는 폴더만 예외로 둡니다.
- 환경 설정 초기값 `use_scripts_auto_execute`는 `False`입니다(시험 값).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 렌더 결과 문제

| 증상                           | 확인할 것                                                             |
|--------------------------------|-----------------------------------------------------------------------|
| 화면에 보이는데 렌더에 없음    | Outliner의 렌더 표시(카메라 아이콘), 컬렉션의 렌더 제외               |
| 렌더가 검거나 너무 어두움      | 조명 세기, 월드 세기, 보기 변환(AgX·Standard), 노출                   |
| 재질이 분홍색                  | 텍스처 파일 누락(7절)                                                 |
| 화면과 렌더 결과가 다름        | 모디파이어의 렌더·뷰포트 단계 차이(Subdivision 기본 뷰포트 1, 렌더 2) |
| 노이즈가 많음                  | Cycles 샘플 수, 노이즈 제거, 조명 크기                                |
| 명령줄 렌더가 다른 경로에 저장 | 인수 순서([명령줄과 일괄 렌더](./blender_cli_batch_render.md) 2절)    |
| GPU 렌더가 CPU로 돎            | Preferences > System의 Cycles 장치, 명령줄 `-- --cycles-device`       |

- Subdivision 기본값(뷰포트 1, 렌더 2)과 보기 변환 초기값(AgX)은 시험으로 확인한 값입니다([Blender 모디파이어](./blender_modifiers.md), [재질과 셰이딩](./blender_materials_shading.md)).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 텍스처 누락

이미지 텍스처는 기본으로 바깥 파일을 경로로 참조합니다. 파일을 옮기면 경로가 깨져 재질이 분홍색으로 보입니다.

시험(텍스처 파일을 지운 뒤 명령줄 렌더):

```text
cycles  | WARNING Image file /w/out/tex_missing.png does not exist.
render  | Saved: '/w/out/miss_1.png'
Warning: Path '/w/out/tex_missing.png' not found, from local data-block 'IMtex_missing.png'
```

- 렌더는 경고만 내고 성공(종료 코드 0)으로 끝납니다. 일괄 렌더에서는 로그의 `does not exist`를 검색해 걸러야 합니다.
- 경로 정리:

| 작업               | 메뉴                                          | Python                                |
|--------------------|-----------------------------------------------|---------------------------------------|
| 상대 경로로 바꾸기 | `File > External Data > Make Paths Relative`  | `bpy.ops.file.make_paths_relative()`  |
| 없는 파일 목록     | `File > External Data > Report Missing Files` | `bpy.ops.file.report_missing_files()` |
| 폴더에서 다시 찾기 | `File > External Data > Find Missing Files`   | `bpy.ops.file.find_missing_files()`   |
| 파일 안에 넣기     | `File > External Data > Pack Resources`       | `bpy.ops.file.pack_all()`             |

- 상대 경로는 `//`로 시작하며 `.blend` 파일이 있는 폴더 기준입니다. 시험에서는 이미지를 불러온 뒤 같은 폴더에 `.blend`를 저장하자 경로가 `//tex_missing.png`로 바뀌었습니다(저장할 때 상대 경로로 다시 매기는 기본 동작).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 증상별 표

| 증상                                     | 원인                              | 조치                                                 |
|------------------------------------------|-----------------------------------|------------------------------------------------------|
| 켜지지 않음, 라이브러리 오류             | 시스템 라이브러리 없음            | 2절                                                  |
| 사용 중 갑자기 꺼짐                      | 충돌                              | `/tmp/blender.crash.txt` 확인, `File > Recover`      |
| 설정을 바꾼 뒤 이상해짐                  | 사용자 설정·애드온                | `--factory-startup`, 애드온 하나씩 끄기              |
| 남이 준 파일에서 리그가 움직이지 않음    | 스크립트 자동 실행 꺼짐           | 믿는 파일만 `--enable-autoexec`                      |
| 분홍색 재질                              | 텍스처 경로 깨짐                  | `Find Missing Files`, `Pack Resources`               |
| 스크립트 실패를 CI가 못 잡음             | `--python-exit-code` 없음         | [Python 스크립트](./blender_python_scripting.md) 2절 |
| `poll() failed, context is incorrect`    | 화면 없는 실행에 편집기 문맥 없음 | [Python 스크립트](./blender_python_scripting.md) 4절 |
| `EGL Error (0x3009): EGL_BAD_MATCH`      | GPU 없는 환경의 Workbench·EEVEE   | 결과 파일이 있으면 무시 가능                         |
| 애드온이 렌더 서버에서 꺼져 있음         | `--factory-startup`               | [Blender 애드온](./blender_addons.md) 6절            |
| 새 판에서 저장한 파일이 옛 판에서 이상함 | 옛 판은 새 기능을 모름            | 같은 판으로 맞추거나, 내보내기 형식으로 전달         |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 설치](./blender_install.md) — 판, 지원 GPU, 설정 폴더
- [Blender 명령줄과 일괄 렌더](./blender_cli_batch_render.md) — 서버 렌더 문제
- [Blender 애드온](./blender_addons.md) — 애드온 켜기 범위
- [Blender 파일 형식](./blender_file_formats.md) — 다른 판·프로그램으로 넘기기

---

## 참고 자료

- Blender Manual: [Troubleshooting](https://docs.blender.org/manual/en/latest/troubleshooting/index.html) · [Crashes](https://docs.blender.org/manual/en/latest/troubleshooting/crash.html) — ★★★☆☆
- Blender Manual: [Recovering Data](https://docs.blender.org/manual/en/latest/troubleshooting/recover.html) · [Python Security](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html) — ★★★☆☆
- Blender Manual: [Command Line Arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html) — ★★★☆☆

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
