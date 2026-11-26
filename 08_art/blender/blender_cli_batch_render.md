# Blender 명령줄과 일괄 렌더
<!-- reference: _reference/blender_official_notes.md -->

화면을 띄우지 않고 명령줄로 렌더하면 서버·렌더 팜·CI에서 여러 파일과 프레임을 자동으로 처리할 수 있습니다. 이 문서는 기본 명령 → 인수 순서 → 프레임 지정 → 엔진·형식·장치 → 렌더 전 설정 바꾸기 → 여러 파일과 여러 PC로 나누기 → 컨테이너 실행 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, Blender 5.3.0 Linux판(공식 압축판 `blender-5.3.0-linux-x64.tar.xz`, sha256 확인)을 GPU 없는 `ubuntu:24.04` 컨테이너에서 실행해 이 문서의 명령, 인수 순서에 따른 출력 경로, 프레임 범위 형식, Workbench·Cycles CPU 렌더, 영상 출력, 두 프로세스의 프레임 나눠 렌더(placeholder)를 확인. GPU 렌더(CUDA·OptiX·HIP), EEVEE 렌더 품질, 네트워크 공유 폴더를 쓰는 여러 PC 렌더는 확인하지 않았음

## 목차

| 섹션                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| [1. 기본 명령](#1-기본-명령) / [2. 인수 순서](#2-인수-순서) / [3. 프레임 지정](#3-프레임-지정)            |
| [4. 엔진·형식·장치](#4-엔진형식장치) / [5. 렌더 전에 설정 바꾸기](#5-렌더-전에-설정-바꾸기)               |
| [6. 여러 파일 일괄 렌더](#6-여러-파일-일괄-렌더) / [7. 여러 프로세스로 나누기](#7-여러-프로세스로-나누기) |
| [8. 컨테이너에서 실행](#8-컨테이너에서-실행) / [9. 트러블슈팅](#9-트러블슈팅)                             |

---

## 1. 기본 명령

```bash
# 1프레임 렌더 (파일에 저장된 출력 경로·형식 사용)
blender -b scene.blend -f 1

# 출력 경로 지정, #은 프레임 번호 자리(####이면 0001)
blender -b scene.blend -o /render/out/frame_#### -f 1

# 애니메이션 전체(파일의 시작~끝 프레임)
blender -b scene.blend -o /render/out/frame_#### -a
```

| 인수                    | 뜻                                                           |
|-------------------------|--------------------------------------------------------------|
| `-b`, `--background`    | 화면 없이 실행                                               |
| `-o`, `--render-output` | 출력 경로. `#` 자리에 프레임 번호, `//`는 `.blend` 폴더 기준 |
| `-f`, `--render-frame`  | 지정 프레임 렌더                                             |
| `-a`, `--render-anim`   | 시작~끝 프레임 렌더                                          |
| `-s`, `-e`, `-j`        | 시작 프레임, 끝 프레임, 간격                                 |
| `-E`, `--engine`        | 렌더 엔진                                                    |
| `-F`, `--render-format` | 출력 형식                                                    |
| `-x`, `--use-extension` | 파일 이름에 확장자 붙이기(1) 또는 빼기(0)                    |
| `-t`, `--threads`       | 스레드 수(0이면 프로세서 수)                                 |
| `-P`, `--python`        | Python 스크립트 실행                                         |

- 렌더가 끝나면 `Saved: '<경로>'`와 `Time: 00:00.34 (Saving: 00:00.16)` 같은 줄이 출력됩니다. 일괄 처리 로그에서 이 줄로 결과를 확인합니다.
- 없는 파일을 열면 `ERROR Cannot read file "...": No such file or directory`를 내고 종료 코드 1로 끝납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 인수 순서

Blender는 인수를 적은 순서대로 처리합니다. `.blend`를 열면 그 파일에 저장된 렌더 설정으로 바뀌므로, 렌더 설정 인수는 파일 뒤에 둡니다.

| 명령                                                | 실제 저장 위치                           |
|-----------------------------------------------------|------------------------------------------|
| `blender -b -o /w/out/before_#### scene.blend -f 1` | `/w/from_file_0001.png` (파일 값이 이김) |
| `blender -b scene.blend -o /w/out/after_#### -f 1`  | `/w/out/after_0001.png`                  |

- `-f`·`-a`는 렌더를 바로 시작하므로 맨 끝에 둡니다. 그 뒤에 적은 설정은 이미 끝난 렌더에 반영되지 않습니다.
- 정리하면 `blender -b <파일> [-E 엔진] [-o 경로] [-F 형식] [--python-expr ...] -f/-a [-- 스크립트 인수]` 순서입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 프레임 지정

| 명령                 | 렌더한 프레임 (시험) |
|----------------------|----------------------|
| `-f 1`               | 1                    |
| `-f 2..3,5`          | 2, 3, 5              |
| `-s 1 -e 6 -j 2 -a`  | 1, 3, 5              |
| `-a` (파일 범위 1~6) | 1~6                  |

- `-s`·`-e`·`-j`는 `-a`보다 앞에 둡니다.
- `-o /w/out/a_##`처럼 `#`이 2개면 `a_01.png`처럼 2자리로 채웁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 엔진·형식·장치

```bash
# 엔진 목록
blender -b -E help
#   BLENDER_EEVEE
#   BLENDER_WORKBENCH
#   CYCLES

# Cycles CPU로 렌더 (-- 뒤의 --cycles-device는 Cycles 전용 인수)
blender -b scene.blend -E CYCLES -o /render/out/cy_# -f 1 -- --cycles-device CPU

# JPEG로, 확장자 없이 저장
blender -b scene.blend -o /render/out/frame_# -F JPEG -x 0 -f 1     # frame_1

# 영상 파일 (FFmpeg, 기본 MKV/H264)
blender -b scene.blend -o /render/out/mov_ -F FFMPEG -s 1 -e 6 -a   # mov_0001-0006.mkv
```

| 장치 값 (`--cycles-device`) | 대상                |
|-----------------------------|---------------------|
| `CPU`                       | CPU                 |
| `CUDA`, `OPTIX`             | NVIDIA GPU          |
| `HIP`                       | AMD GPU             |
| `ONEAPI`                    | Intel GPU           |
| `METAL`                     | Apple Silicon·macOS |
| `OPTIX+CPU` 처럼 `+CPU`     | GPU와 CPU 함께      |

- GPU 장치는 시험하지 않았습니다. GPU가 없는 환경에서는 Cycles 장치 목록이 비어 CPU로 렌더됩니다.
- 영상은 프레임 하나가 실패하면 전체를 다시 렌더해야 합니다. 긴 작업은 PNG·EXR 이미지 시퀀스로 렌더한 뒤 따로 영상으로 묶는 편이 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 렌더 전에 설정 바꾸기

명령줄 인수에 없는 설정(샘플 수, 해상도 비율 등)은 Python으로 바꿉니다.

```bash
# 짧은 설정은 --python-expr, -f 앞에 둠
blender -b scene.blend -E CYCLES \
  --python-expr "import bpy; bpy.context.scene.cycles.samples = 64" \
  -o /render/out/cy_#### -f 1
```

```python
# render_pct.py : 해상도 비율을 인수로 받아 렌더
import bpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
s = bpy.context.scene
s.render.resolution_percentage = int(args[0])
s.render.filepath = "/render/out/pct" + args[0] + "_"
bpy.ops.render.render(write_still=True)
```

```bash
blender -b scene.blend -P render_pct.py -- 50   # 64×64 장면 → 32×32 PNG
```

- 스크립트 안에서 렌더할 때는 `bpy.ops.render.render(write_still=True)`(정지 화면)나 `animation=True`(애니메이션)를 씁니다. `write_still`이 없으면 파일로 저장하지 않습니다.
- 스크립트 실패를 감지하려면 `--python-exit-code 1`을 `-P` 앞에 둡니다([Blender Python 스크립트](./blender_python_scripting.md) 2절).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 여러 파일 일괄 렌더

```bash
#!/usr/bin/env bash
set -u
out=/render/out
fail=0
for f in /render/jobs/*.blend; do
  name=$(basename "$f" .blend)
  if ! blender -b "$f" -o "$out/${name}_####" -f 1 > "$out/${name}.log" 2>&1; then
    echo "FAIL $f"; fail=1
  fi
done
exit $fail
```

- 파일마다 로그를 따로 남기면 실패한 파일을 찾기 쉽습니다.
- 텍스처가 없어도 렌더는 경고만 내고 종료 코드 0으로 끝납니다(9절). 로그에서 `WARNING Image file ... does not exist`도 검색합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 여러 프로세스로 나누기

같은 애니메이션을 여러 프로세스나 PC가 나눠 렌더할 때는 "덮어쓰기 끔 + 자리 표시 파일 켬"을 씁니다. 렌더를 시작한 프레임에 빈 파일을 먼저 만들어, 다른 프로세스가 그 프레임을 건너뜁니다.

```bash
E="import bpy; r=bpy.context.scene.render; r.use_overwrite=False; r.use_placeholder=True"
blender -b scene.blend -o /shared/out/f_#### --python-expr "$E" -a &   # 프로세스 1
blender -b scene.blend -o /shared/out/f_#### --python-expr "$E" -a &   # 프로세스 2
wait
```

시험 결과(1~6프레임, Cycles 16샘플, 같은 출력 폴더):

| 프로세스 | 렌더한 프레임 |
|----------|---------------|
| 1        | 1, 3, 5       |
| 2        | 2, 4, 6       |

- 출력 폴더는 모든 프로세스가 같은 경로로 볼 수 있어야 합니다(여러 PC면 공유 폴더). 여러 PC 구성은 시험하지 않았습니다.
- 렌더 도중 프로세스가 죽으면 빈 자리 표시 파일이 남습니다. 다시 렌더하기 전에 크기 0인 파일을 지웁니다.
- 프레임 범위를 직접 나누는 방법(`-s 1 -e 50 -a`와 `-s 51 -e 100 -a`)도 됩니다. 프레임마다 시간 차이가 크면 자리 표시 방식이 고르게 나뉩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 컨테이너에서 실행

공식 압축판은 실행에 X11·GL 라이브러리가 필요합니다. 화면이 없어도 라이브러리는 있어야 합니다.

```bash
# ubuntu:24.04 기준 (시험에 쓴 패키지)
apt-get install -y --no-install-recommends xz-utils \
  libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 libice6 \
  libgl1 libegl1 libglx-mesa0 libgl1-mesa-dri libxext6 libxcursor1 libxinerama1 libxrandr2 \
  libwayland-client0 libwayland-cursor0 libwayland-egl1 libdbus-1-3 libfontconfig1 libfreetype6
tar -xJf blender-5.3.0-linux-x64.tar.xz -C /opt
/opt/blender-5.3.0-linux-x64/blender --version   # Blender 5.3.0
```

- 내려받은 압축판은 같은 폴더의 `blender-5.3.0.sha256`으로 확인합니다: `grep linux-x64 blender-5.3.0.sha256 | sha256sum -c -`.
- 라이브러리가 하나라도 없으면 `error while loading shared libraries: libX11.so.6` 같은 오류로 바로 끝납니다.
- 시험 이미지 크기는 약 2.4GB였습니다(압축판 풀기와 라이브러리 포함).

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                          | 원인                                        | 조치                                                                          |
|-----------------------------------------------|---------------------------------------------|-------------------------------------------------------------------------------|
| `-o`로 준 경로가 아니라 다른 곳에 저장됨      | `-o`를 `.blend`보다 앞에 둠                 | `.blend` 뒤, `-f`·`-a` 앞에 둠                                                |
| 설정을 줬는데 반영되지 않음                   | `-f`·`-a` 뒤에 둠                           | 렌더 인수를 맨 끝에 둠                                                        |
| `EGL Error (0x3009): EGL_BAD_MATCH` 출력      | GPU 없는 환경에서 Workbench·EEVEE가 GL을 씀 | 결과 파일이 생기면 무시해도 됨(시험에서 렌더 성공). Cycles는 출력 없음        |
| 텍스처가 빠진 채 렌더되는데 성공으로 끝남     | 없는 이미지는 경고만 내고 계속              | 로그에서 `does not exist` 검색, 렌더 전 `bpy.ops.file.report_missing_files()` |
| 영상 렌더가 중간에 멈추면 처음부터            | 영상 파일은 이어 붙일 수 없음               | 이미지 시퀀스로 렌더 뒤 묶기                                                  |
| 나눠 렌더할 때 같은 프레임을 두 번 렌더       | 덮어쓰기 켬·자리 표시 꺼짐                  | `use_overwrite=False`, `use_placeholder=True`                                 |
| `libX11.so.6: cannot open shared object file` | 컨테이너에 X11 라이브러리 없음              | 8절 패키지 설치                                                               |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 조명과 렌더](./blender_lighting_rendering.md) — 엔진별 설정, 출력 형식
- [Blender Python 스크립트](./blender_python_scripting.md) — 스크립트 작성, 종료 코드
- [Blender 트러블슈팅](./blender_troubleshooting.md) — 실행 오류, 충돌 로그

---

## 참고 자료

- Blender Manual: [Command Line Rendering](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html) · [Command Line Arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html) — ★★★☆☆
- Blender 소스: [creator_args.cc](https://github.com/blender/blender/blob/v5.3.0/source/creator/creator_args.cc) — 인수 정의 원문 — ★★★☆☆
- Blender: [Release 5.3 내려받기](https://download.blender.org/release/Blender5.3/) — 압축판과 sha256 — ★★★☆☆

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
