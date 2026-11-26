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

| 모디파이어          | 기본값                                        | 결과                                                    |
|---------------------|-----------------------------------------------|---------------------------------------------------------|
| Subdivision Surface | 단계 2로 설정                                 | 98/192/96                                               |
| Mirror              | X축만, Merge 켬, Clipping 끔                  | 16/24/12 (원점 기준 복제)                               |
| Array (Legacy)      | Fixed Count, 상대 간격 X 1.0, Merge 끔        | 개수 3에서 24/36/18                                     |
| Array (노드 에셋)   | 모양 Line, 개수 3, 상대 간격 X 1.0, Merge 끔  | 그대로 24/36/18                                         |
| Solidify            | 두께 0.01                                     | 16/24/12                                                |
| Bevel               | 폭 0.1, 분할 1, 제한 방식 Angle               | 24/48/26                                                |
| Boolean             | Difference, 해법 Exact (Float·Exact·Manifold) | UV 구 265/526/263, 원기둥 구멍은 세 해법 모두 72/112/40 |
| Apply               | Array(Legacy, 2개)·Subdivision 중 첫째 적용   | 메시 16/24/12, 스택에 Subdivision만 남음                |
| 순서                | Subdivision 1 → Bevel 0.05 / 반대 순서        | 96/192/98 / 98/192/96                                   |

- 5.3 `Add Modifier` 메뉴(`bl_ui/properties_data_modifier.py`): 분류 Edit·Generate·Deform·Normals·Physics·Color. Generate의 "Array"는 기본 제공 노드 에셋(`datafiles/assets/nodes/geometry_nodes_essentials.blend`의 `Array`)이고 내장 모디파이어는 "Array (Legacy)"로 표시. 같은 파일에 Smooth by Angle·Curve to Tube·Scatter on Surface.
- Edit 모드 연산자(정육면체): 윗면 `extrude_region_move` z+1 → 12/20/10, 이어서 `inset` 0.2 → 16/28/14, 이어서 전체 `bevel` 0.05·3분할 → 224/448/226. `subdivide` 1회 → 26/48/24. 전체 복제 뒤 `remove_doubles`(Merge by Distance) → 26/48/24. `flip_normals` 뒤 `normals_make_consistent(inside=False)` → 윗면 법선 z 1.0. `shade_auto_smooth` → 지오메트리 노드 모디파이어 "Smooth by Angle" 추가.
- Subdivision Surface 기본값: 뷰포트 1, 렌더 2, Catmull-Clark. 원기둥 추가 기본 꼭짓점 32.

## 6. Principled BSDF 입력 (5.3.0, 기본값)

Base Color (0.8, 0.8, 0.8, 1), Metallic 0, Roughness 0.5, IOR 1.5, Alpha 1, Thin Wall 끔, Normal, Weight, Diffuse Roughness 0, Subsurface Weight 0·Radius (1, 0.2, 0.1)·Scale 0.005·IOR 1.4·Anisotropy 0, Specular IOR Level 0.5, Specular Tint 흰색, Anisotropic 0, Anisotropic Rotation 0, Tangent, Transmission Weight 0, Transmission Dispersion Scale 0·Abbe Number 20, Coat Weight 0·Roughness 0.03·IOR 1.5·Tint 흰색·Normal, Sheen Weight 0·Roughness 0.5·Tint 흰색, Emission Color 흰색·Strength 0, Thin Film Thickness 0·IOR 1.33.

### 6.1 재질·색 관리 (5.3.0)

- 새 재질과 기본 정육면체 재질은 노드 트리(Principled BSDF + Material Output)를 처음부터 가짐. 기본 정육면체는 UV 맵 `UVMap`, 재질 슬롯 연결 `DATA`.
- EEVEE 재질 Render Method: `DITHERED`(초기값), `BLENDED`.
- 입력 색 공간에 `sRGB`(새 이미지 초기값), `Non-Color`, `Linear Rec.709`, ACES·AgX·카메라 로그 계열.
- 보기 변환 초기값 AgX, Look None, Display sRGB. `Standard` 지정 가능.
- EEVEE 렌더 샘플 64. Cycles 샘플 4096, 적응 샘플링 켬(0.01), 노이즈 제거 켬(OpenImageDenoise).
- Normal Map 노드 입력: Strength, Color. ShaderNode 종류 108개(`bpy.types` 이름 기준).
- 기본 장면 정육면체에 생성 이미지(Color Grid)를 Base Color로 연결해 EEVEE·Cycles(CPU 16샘플) 128×128 렌더 성공, 결과 이미지에서 텍스처 확인.

## 7. 기본 키맵 (초기 설정)

- 기본 설정 파일 `Blender.py`: 선택 마우스는 기본값을 지정하지 않아 첫 항목 `LEFT`, 스페이스바 기본값 `PLAY`.
- `Params()`를 인수 없이 만들면 `select_mouse='RIGHT'`, `spacebar_action='TOOL'`이라 초기 설정과 다른 키가 나옵니다. 문서의 단축키는 초기 설정 기준으로 뽑은 값입니다.
- 왼쪽·오른쪽 클릭 선택에 따라 달라지는 키: 문맥 메뉴(오른쪽 클릭 ↔ W), 루프 선택(Alt+왼쪽 클릭 ↔ Alt+오른쪽 클릭), 끌어서 이동, Space(재생 ↔ 도구 모음).

## 8. 2순위 확인 (2026-11-26, `bpy` 5.3.0 컨테이너)

| 분야            | 확인 결과                                                                                                                                                                                                       |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| UV              | Unwrap 방식 Conformal(초기값)·Angle Based·Minimum Stretch, 여백 0.001. Smart UV Project 각도 66도, 섬 여백 0                                                                                                    |
| 베이크          | Cycles 종류 12개(Combined·AO·Shadow·Position·Normal·UV·Roughness·Emit·Environment·Diffuse·Glossy·Transmission). 활성 Image Texture 노드 없으면 "No active and selected image texture node found"                |
| 조명            | `light_add` 초기값 Point·Spot·Area 10W, Sun 1.0, Area 크기 1.0. 기본 장면 조명 Point 1000W, 반지름 0.1                                                                                                          |
| 월드·카메라     | 월드 Background (0.051) 세기 1.0. 카메라 50mm, 센서 36mm, 클립 0.1~100m, DOF 꺼짐 F2.8                                                                                                                          |
| Cycles          | 뷰포트 샘플 1024, Max Bounces 12, Diffuse·Glossy 4, Transmission 12, Transparent 8, 뷰포트 노이즈 제거 꺼짐                                                                                                     |
| EEVEE           | 뷰포트 샘플 16, Ray Tracing 꺼짐(Screen-Trace), 그림자 Rays 1·Steps 6, Fast GI 켬                                                                                                                               |
| 출력            | `media_type` IMAGE·MULTI_LAYER_IMAGE·VIDEO. VIDEO는 FFmpeg, 컨테이너 MKV·코덱 H264 초기값. 3프레임 PNG 시퀀스와 `movie_0001-0003.mkv` 생성                                                                      |
| GPU             | GPU 없는 컨테이너에서 Cycles 장치 목록 비어 있음, CUEW 초기화 경고                                                                                                                                              |
| 애니메이션      | 액션은 layers·slots 구조(슬롯 `OBCube`). 키 보간 Bezier·핸들 Auto Clamped. 1→25프레임 0→4: Bezier 7·13·19프레임 0.625·2.0·3.375, Linear 1·2·3. Cycles F-Modifier 24프레임 주기 반복. Auto Keying 꺼짐           |
| 리깅            | 아마추어 표시 Octahedral, 뼈 모음 `Bones`. `ARMATURE_AUTO`로 정점 그룹·Armature 모디파이어 생성. 포즈 뼈 회전 방식 Quaternion. 위쪽 뼈 X 90도 → 끝점 (y 0.3, z 4.0)→(y -0.48, z 2.31)                           |
| 지오메트리 노드 | GeometryNode 종류 292개. 16m² 평면 Density 10 → 정점 1924, 20 → 3844. 모디파이어 입력은 `mod.properties.inputs.<Socket_n>.value`(`mod["Socket_n"]`은 오류). Simulation·Repeat·For Each·Closure 노드 생성 가능   |
| 스컬프팅        | 기본 브러시 64개, 처음 브러시 Draw, 크기 기준 VIEW. 복셀 크기 초기값 0.1: UV 구 482 → 2000 정점, 0.05 → 7672. Multires 3단계 정육면체 386 정점. Dyntopo Relative 12px Subdivide Collapse. 메시 대칭 초기값 꺼짐 |
| 파일 형식       | glTF `export_apply` 꺼짐(모디파이어 미적용), USD `export_animation` 꺼짐, OBJ 가져오기 객체 회전 X 90도, STL 3각형·재질 없음. FBX `apply_scale_options` FBX_SCALE_NONE("All Local"), Add Leaf Bones 켬          |
