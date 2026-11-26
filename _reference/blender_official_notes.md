---
name: blender-official-notes
description: Blender 5.3 판·LTS 지원 기간·시스템 요구사항·명령줄 인수와 bpy 5.3.0 컨테이너 확인 결과(작업 공간, 엔진, 모디파이어, Principled BSDF, 기본 키맵) 정리.
tags:
  - blender
  - 3d
  - bpy
  - modeling
  - rendering
last_checked: 2026-11-26
sources:
  - https://github.com/blender/blender/tags
  - https://raw.githubusercontent.com/blender/blender/v5.3.0/source/blender/blenkernel/BKE_blender_version.h
  - https://raw.githubusercontent.com/blender/blender/v5.2.5/source/blender/blenkernel/BKE_blender_version.h
  - https://raw.githubusercontent.com/blender/blender/v4.5.16/source/blender/blenkernel/BKE_blender_version.h
  - https://raw.githubusercontent.com/blender/blender/v5.3.0/source/creator/creator_args.cc
  - https://pypi.org/pypi/bpy/json
  - https://www.blender.org/download/requirements/
  - https://www.blender.org/download/lts/
  - https://developer.blender.org/docs/release_notes/
  - https://docs.blender.org/manual/en/latest/
---

# Blender 공식 자료 참조 노트

## 1. 판 (2026-11-26)

| 항목        | 내용                                                                      | 근거                                      |
|-------------|---------------------------------------------------------------------------|-------------------------------------------|
| 최신판      | 5.3.0 (태그 2026-11-09, 빌드 날짜 2026-11-10, 해시 `02f0899`)             | GitHub 미러 태그, `bpy` 5.3.0 실행        |
| LTS         | 5.2 (5.2.5, 2026-11-23)와 4.5 (4.5.17, 2026-11-23)                        | 판 정의 헤더 `BLENDER_VERSION_SUFFIX LTS` |
| 5.3.0 헤더  | `BLENDER_VERSION 503`, `CYCLE release`, `SUFFIX` 비어 있음(LTS 아님)      | `BKE_blender_version.h`                   |
| 주기        | 약 4개월마다 새 판, 1년에 한 번 LTS를 내고 2년 유지                       | 검색 요약 (원문 403)                      |
| LTS 지원 끝 | 4.5는 2027-07, 5.2는 2028-07                                              | 검색 요약 (원문 403)                      |
| Python      | 판마다 Python 한 판만 지원. 5.3은 3.13 (`bpy` `requires_python ==3.13.*`) | PyPI `bpy`                                |
| 라이선스    | GPL-3.0 이상                                                              | 저장소 README, PyPI                       |

- blender.org, docs.blender.org, download.blender.org, developer.blender.org, projects.blender.org는 이번 확인에서 자동 조회가 모두 HTTP 403이었습니다. 위 "검색 요약"은 검색 결과 요약이며 원문 문장 대조는 미완료입니다.
- 내려받기 파일 이름(압축판·설치판)과 체크섬 파일 이름은 확인하지 못했습니다.

## 2. 시스템 요구사항 (검색 요약, 원문 403)

| 항목 | 최소                      | 권장  |
|------|---------------------------|-------|
| CPU  | 4코어, SSE4.2 지원        | 8코어 |
| RAM  | 8GB                       | 32GB  |
| GPU  | VRAM 2GB, OpenGL 4.3 이상 | -     |

- 5.0에서 Windows·Linux의 최소 GPU를 올렸습니다: NVIDIA Maxwell(GeForce 900) 이상, AMD GCN 4세대 이상, Intel Kaby Lake 이상. 그보다 오래된 GPU는 동작할 수 있지만 지원하지 않습니다.
- Cycles GPU: OptiX는 NVIDIA compute capability 5.0 이상과 드라이버 575 이상, HIP는 AMD RDNA1 이상(5.3 매뉴얼 검색 요약).

## 3. 명령줄 인수 (`creator_args.cc` v5.3.0)

원문 파일이 길어 앞부분만 그대로 읽었고 나머지는 요약으로 확인했습니다.

| 인수                        | 뜻                                                                          |
|-----------------------------|-----------------------------------------------------------------------------|
| `-b`, `--background`        | 화면 없이 실행. 오디오 장치도 기본으로 꺼짐 (원문)                          |
| `-o`, `--render-output`     | 출력 경로와 파일 이름, `#`은 프레임 번호 자리                               |
| `-f`, `--render-frame`      | 지정 프레임 렌더·저장, `1,3,5`·`1..10` 형식 가능                            |
| `-a`, `--render-anim`       | 시작부터 끝 프레임까지 렌더                                                 |
| `-s`, `-e`, `-j`            | 시작·끝 프레임, 프레임 간격                                                 |
| `-E`, `--engine`            | 렌더 엔진, `-E help`로 목록                                                 |
| `-F`, `--render-format`     | 출력 형식(`PNG`·`JPEG`·`OPEN_EXR`·`FFMPEG` 등)                              |
| `-t`, `--threads`           | 스레드 수, 0이면 프로세서 수                                                |
| `-P`, `--python`            | Python 스크립트 파일 실행                                                   |
| `--python-expr`             | Python 식 실행                                                              |
| `--python-exit-code`        | Python 예외 때 종료 코드(0~255)                                             |
| `--factory-startup`         | 사용자 시작 파일을 읽지 않음                                                |
| `-noaudio`                  | 사운드 시스템 없음                                                          |
| `--addons`                  | 추가로 켤 애드온(쉼표 구분)                                                 |
| `-- --cycles-device <장치>` | `CPU` `CUDA` `OPTIX` `HIP` `ONEAPI` `METAL`, `+CPU` 덧붙여 함께 사용 (원문) |

- 원문: "Arguments are executed in the order they are given." `.blend` 파일을 읽으면 출력 경로가 파일 값으로 덮이므로 `blender -b test.blend -o /tmp -f 1` 순서로 씁니다(원문 예시).

## 4. 컨테이너 확인 (2026-11-26)

구성: `python:3.13-slim` 컨테이너, `pip install bpy==5.3.0`, X11·GL 런타임 라이브러리 추가(`libx11-6`, `libgl1`, `libegl1` 등). `bpy`는 Blender를 Python 모듈로 빌드한 것이라 `blender` 실행 파일과 화면은 없습니다.

| 확인                       | 결과                                                                                                                          |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| 판                         | `5.3.0`, 빌드 날짜 `2026-11-10`, 해시 `02f0899d78e3`                                                                          |
| 기본 장면                  | Camera, Cube, Light. 1920×1080, 100%, 24fps, 프레임 1~250, 출력 PNG                                                           |
| 기본 작업 공간 11개        | Layout, Modeling, Sculpting, UV Editing, Texture Paint, Shading, Animation, Rendering, Compositing, Geometry Nodes, Scripting |
| 기본 렌더 엔진             | `BLENDER_EEVEE`                                                                                                               |
| 렌더 64×64                 | EEVEE 성공(GPU 없이, 약 7~22초), Cycles CPU 8샘플 성공, Workbench 성공                                                        |
| Cycles 기본값              | 샘플 4096, 장치 CPU                                                                                                           |
| 새 재질                    | 노드 트리가 처음부터 있음(Principled BSDF + Material Output). `use_nodes`는 6.0에서 없앨 예정 경고                            |
| Principled BSDF            | 입력 36개, 분포 `MULTI_GGX`, 표면 아래 산란 `RANDOM_WALK` (6절)                                                               |
| 모디파이어 종류            | 83개(메시·Grease Pencil·물리 포함)                                                                                            |
| 정육면체 연산 (bmesh)      | 기본 8/12/6 (정점/모서리/면) → 윗면 돌출 12/20/11 → 모든 모서리 베벨 2분할 68/132/67                                          |
| 모디파이어 결과 (정육면체) | 5절                                                                                                                           |
| 기본 키맵                  | 내장 `keymap_data/blender_default.py`에 초기 설정값(왼쪽 클릭 선택, Space 재생)을 넣어 생성 (7절)                             |

- `RenderSettings.engine`의 RNA 열거 목록은 `BLENDER_EEVEE`만 돌려줬지만 `CYCLES`·`BLENDER_WORKBENCH`를 직접 지정하면 렌더됐습니다. 엔진 목록은 실행 중 등록되는 값입니다.
- GPU 렌더(CUDA·OptiX·HIP), 화면 조작, 애드온·확장 설치는 시험하지 않았습니다.

## 5. 모디파이어 시험값 (정육면체, 평가 결과 정점/모서리/면)

| 모디파이어          | 기본값                                 | 결과                          |
|---------------------|----------------------------------------|-------------------------------|
| Subdivision Surface | 단계 2로 설정                          | 98/192/96                     |
| Mirror              | X축만, Merge 켬, Clipping 끔           | 16/24/12 (원점 기준 복제)     |
| Array               | Fixed Count, 상대 간격 X 1.0, Merge 끔 | 개수 3에서 24/36/18           |
| Solidify            | 두께 0.01                              | 16/24/12                      |
| Bevel               | 폭 0.1, 분할 1, 제한 방식 Angle        | 24/48/26                      |
| Boolean             | Difference, 해법 Exact                 | UV 구와 겹쳐 265/526/263      |
| Apply               | 스택 첫 모디파이어 적용                | 메시에 반영되고 스택에서 빠짐 |

## 6. Principled BSDF 입력 (5.3.0, 기본값)

Base Color (0.8, 0.8, 0.8, 1), Metallic 0, Roughness 0.5, IOR 1.5, Alpha 1, Thin Wall 끔, Normal, Weight, Diffuse Roughness 0, Subsurface Weight 0·Radius (1, 0.2, 0.1)·Scale 0.005·IOR 1.4·Anisotropy 0, Specular IOR Level 0.5, Specular Tint 흰색, Anisotropic 0, Anisotropic Rotation 0, Tangent, Transmission Weight 0, Transmission Dispersion Scale 0·Abbe Number 20, Coat Weight 0·Roughness 0.03·IOR 1.5·Tint 흰색·Normal, Sheen Weight 0·Roughness 0.5·Tint 흰색, Emission Color 흰색·Strength 0, Thin Film Thickness 0·IOR 1.33.

## 7. 기본 키맵 (초기 설정)

- 기본 설정 파일 `Blender.py`: 선택 마우스는 기본값을 지정하지 않아 첫 항목 `LEFT`, 스페이스바 기본값 `PLAY`.
- `Params()`를 인수 없이 만들면 `select_mouse='RIGHT'`, `spacebar_action='TOOL'`이라 초기 설정과 다른 키가 나옵니다. 문서의 단축키는 초기 설정 기준으로 뽑은 값입니다.
- 왼쪽·오른쪽 클릭 선택에 따라 달라지는 키: 문맥 메뉴(오른쪽 클릭 ↔ W), 루프 선택(Alt+왼쪽 클릭 ↔ Alt+오른쪽 클릭), 끌어서 이동, Space(재생 ↔ 도구 모음).
