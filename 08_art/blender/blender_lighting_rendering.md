# Blender 조명과 렌더
<!-- reference: _reference/blender_official_notes.md -->

렌더(Render)는 장면을 카메라 시점의 이미지·영상으로 계산하는 작업입니다. 이 문서는 조명 종류 → 월드 → 카메라 → 렌더 엔진 고르기 → 엔진별 설정 → 출력 형식 → GPU 렌더 → 렌더 시간 줄이기 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 조명 네 종류·월드·카메라 기본값, EEVEE·Cycles 렌더 설정 기본값, 출력 형식 목록을 확인하고 Workbench로 3프레임 PNG 연속 렌더와 MKV(H264) 영상 출력을 실행. GPU 렌더는 GPU가 없는 환경이라 실행하지 않았음

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 조명](#1-조명) / [2. 월드](#2-월드) / [3. 카메라](#3-카메라)                                         |
| [4. 렌더 엔진](#4-렌더-엔진) / [5. 엔진별 설정](#5-엔진별-설정) / [6. 출력](#6-출력)                     |
| [7. GPU 렌더](#7-gpu-렌더) / [8. 렌더 시간 줄이기](#8-렌더-시간-줄이기) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 조명

`Shift+A` > `Light`로 추가합니다. 세기는 와트(W) 단위이고, Sun만 단위 면적당 세기(W/m²)입니다.

| 종류  | 빛의 모양                 | 추가 시 초기값(5.3.0)      | 쓰는 곳                           |
|-------|---------------------------|----------------------------|-----------------------------------|
| Point | 한 점에서 사방으로        | 10W, 반지름 0              | 전구, 작은 광원                   |
| Sun   | 무한히 먼 곳에서 평행하게 | 세기 1.0, 각도 약 0.53도   | 햇빛, 야외                        |
| Spot  | 원뿔 모양                 | 10W, 원뿔 45도, Blend 0.15 | 무대 조명, 손전등                 |
| Area  | 사각형·원 면에서          | 10W, 크기 1m, Square       | 창문, 소프트박스, 부드러운 그림자 |

- 기본 장면의 조명은 Point 1000W, 반지름 0.1m입니다. 새로 추가한 Point(10W)는 기본 장면 기준으로 매우 어둡습니다.
- 반지름(Radius)·크기(Size)가 클수록 그림자 가장자리가 부드러워집니다.
- 기본 3점 조명: 주 조명(Key, 가장 밝음), 보조 조명(Fill, 그림자를 옅게), 뒤쪽 조명(Rim, 윤곽 강조).
- 발광 재질(Emission)도 광원으로 쓸 수 있습니다([재질과 셰이딩](./blender_materials_shading.md) 5절).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 월드

월드(World)는 배경과 주변광입니다. Properties > World 탭에서 설정합니다.

- 기본 월드는 Background 노드 하나이고 색은 어두운 회색(0.051), 세기 1.0입니다.
- HDRI(전방위 사진)를 쓰면 사실적인 주변광과 반사가 생깁니다. World의 Color 입력에 `Environment Texture` 노드를 연결하고 `.hdr`·`.exr` 파일을 엽니다.
- 배경만 투명하게 하고 조명은 유지하려면 Properties > Render > Film > `Transparent`를 켭니다(초기값 꺼짐). 출력은 PNG·EXR처럼 알파를 지원하는 형식으로 저장합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 카메라

| 항목             | 기본 장면 카메라 초기값      |
|------------------|------------------------------|
| 종류             | Perspective                  |
| 초점 거리        | 50mm                         |
| 센서 폭          | 36mm                         |
| 보이는 범위      | 0.1m ~ 100m (Clip Start/End) |
| 피사계 심도(DOF) | 꺼짐, F-Stop 2.8             |

- 숫자 패드 0으로 카메라 시점을 봅니다. 지금 보는 시점에 카메라를 맞추려면 `Ctrl+Alt+숫자 패드 0`, 선택한 객체를 활성 카메라로 쓰려면 `Ctrl+숫자 패드 0`을 누릅니다(키맵 확인).
- 카메라 시점에서 사이드바(`N`) > View > `Lock Camera to View`를 켜면 시점 조작으로 카메라를 움직입니다.
- 장면에 카메라가 없으면 렌더가 "Cannot render, no camera" 오류로 멈춥니다(시험 확인).
- 여러 카메라가 있으면 렌더에는 Scene 속성의 활성 카메라를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 렌더 엔진

Properties > Render 탭 맨 위에서 고릅니다.

| 엔진      | 방식                                | 장점                          | 단점                                 |
|-----------|-------------------------------------|-------------------------------|--------------------------------------|
| EEVEE     | 실시간 래스터화(일부 레이 트레이싱) | 빠름, 뷰포트와 결과가 같음    | 굴절·간접광·그림자가 근사적          |
| Cycles    | 경로 추적(Path Tracing)             | 사실적인 빛, 굴절·간접광 정확 | 느림, 노이즈 → 샘플·노이즈 제거 필요 |
| Workbench | 단색·와이어 표시                    | 매우 빠름                     | 재질·조명 표현 없음                  |

- 기본 장면의 엔진은 EEVEE입니다.
- 고르는 기준: 애니메이션·제품 미리 보기·스타일 렌더는 EEVEE, 실사 정지 이미지·유리·물·실내 간접광은 Cycles, 모델 점검·포트폴리오 와이어 렌더는 Workbench.
- 시험: 같은 기본 장면을 EEVEE, Cycles(CPU), Workbench로 64×64 렌더해 모두 성공했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 엔진별 설정

### 5.1 Cycles (5.3.0 초기값)

| 항목              | 초기값                   | 설명                                   |
|-------------------|--------------------------|----------------------------------------|
| Render Samples    | 4096                     | 상한값. 적응 샘플링이 일찍 멈춤        |
| Viewport Samples  | 1024                     | 뷰포트 Rendered 표시                   |
| Adaptive Sampling | 켬, Noise Threshold 0.01 | 노이즈가 기준 아래면 그 픽셀 계산 중단 |
| Denoise (렌더)    | 켬, OpenImageDenoise     | 노이즈 제거                            |
| Denoise (뷰포트)  | 꺼짐                     | 켜면 미리 보기가 깨끗해짐              |
| Max Bounces       | 12                       | 빛 반사 총 횟수                        |
| Diffuse / Glossy  | 4 / 4                    | 확산·반사 반사 횟수                    |
| Transmission      | 12                       | 투과(유리) 횟수                        |
| Transparent       | 8                        | 투명 면 통과 횟수                      |
| Caustics          | 반사·굴절 모두 켬        | 끄면 노이즈 감소                       |
| Time Limit        | 0 (없음)                 | 프레임당 시간 상한                     |
| Device            | CPU                      | GPU는 환경설정에서 장치를 고른 뒤 선택 |

### 5.2 EEVEE (5.3.0 초기값)

| 항목               | 초기값                   |
|--------------------|--------------------------|
| Render Samples     | 64                       |
| Viewport Samples   | 16                       |
| Ray Tracing        | 꺼짐 (방식 Screen-Trace) |
| Shadows            | 켬, Rays 1, Steps 6      |
| Fast GI            | 켬, Global Illumination  |
| Volumetric Shadows | 꺼짐                     |

- EEVEE에서 반사·굴절을 정확히 하려면 Ray Tracing을 켭니다. 유리는 재질 설정(Properties > Material > Settings)의 Render Method와 투과 관련 항목도 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 출력

Properties > Output 탭에서 해상도·프레임·형식을 정합니다.

| 항목      | 기본 장면 초기값           |
|-----------|----------------------------|
| 해상도    | 1920×1080, 100%            |
| 프레임    | 1~250, 24fps               |
| 출력 경로 | `/tmp/` (Linux 확인값)     |
| 매체 종류 | Image                      |
| 형식      | PNG, RGBA, 8비트, 압축 15% |

5.x에서는 먼저 매체 종류(Media Type)를 고르고, 그 안에서 형식을 고릅니다.

| 매체 종류         | 형식                                                                                                |
|-------------------|-----------------------------------------------------------------------------------------------------|
| Image             | PNG, JPEG, OpenEXR, WebP, AVIF, TIFF, BMP, TGA, HDR, JPEG 2000, DPX, Cineon, Iris                   |
| Multi-Layer Image | OpenEXR Multilayer (패스·레이어를 한 파일에)                                                        |
| Video             | FFmpeg: 컨테이너 MKV(초기값)·MPEG-4·WebM·QuickTime 등, 코덱 H.264(초기값)·H.265·AV1·ProRes·DNxHD 등 |

- `F12`는 현재 프레임, `Ctrl+F12`는 애니메이션 전체를 렌더합니다. 결과 창에서 Image > Save As로 저장합니다.
- 애니메이션은 영상 파일 대신 이미지 시퀀스(PNG·EXR)로 렌더하고 나중에 합치는 것을 권장합니다. 중간에 멈춰도 렌더한 프레임이 남고, 다시 시작할 때 이어서 할 수 있습니다.
- 출력 경로의 `#`은 프레임 번호 자리입니다. 시험에서 `frame_####`로 3프레임을 렌더하자 `frame_0001.png`~`frame_0003.png`가 만들어졌고, Video(MKV·H264)로 바꾸자 `movie_0001-0003.mkv` 한 파일이 만들어졌습니다.
- 화면 없이 렌더 서버에서 돌리는 방법은 [설치](./blender_install.md) 7절의 `blender -b`를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. GPU 렌더

Cycles는 GPU로 훨씬 빨라집니다.

1. `Edit > Preferences > System > Cycles Render Devices`에서 방식을 고릅니다.
2. 목록에 나온 GPU에 체크합니다.
3. Properties > Render > Device를 `GPU Compute`로 바꿉니다.

| 방식   | GPU                            | 조건(검색 요약)                                |
|--------|--------------------------------|------------------------------------------------|
| CUDA   | NVIDIA                         | -                                              |
| OptiX  | NVIDIA (RTX에서 하드웨어 가속) | compute capability 5.0 이상, 드라이버 575 이상 |
| HIP    | AMD                            | RDNA1 이상                                     |
| oneAPI | Intel Arc                      | -                                              |
| Metal  | Apple Silicon, 일부 AMD(macOS) | -                                              |

- 시험 환경(GPU·드라이버 없음)에서는 장치 목록이 비어 있었고 `CUDA` 라이브러리 초기화 경고가 나왔습니다. 정상 동작이며 CPU 렌더는 됩니다.
- 명령줄에서는 `blender -b scene.blend -f 1 -- --cycles-device OPTIX`처럼 고릅니다. `+CPU`를 붙이면 CPU와 함께 씁니다(`OPTIX+CPU`).
- EEVEE는 그래픽 API(OpenGL·Vulkan)로 그리며 Cycles 장치 선택과 관계없습니다. GPU 없는 시험 컨테이너에서도 EEVEE 렌더는 성공했지만 느렸습니다(64×64에 7~22초).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 렌더 시간 줄이기

| 방법                                   | 효과                                |
|----------------------------------------|-------------------------------------|
| 해상도 %를 50%로 낮춰 시험 렌더        | 픽셀 수 1/4                         |
| Cycles 샘플 낮추고 노이즈 제거 유지    | 적응 샘플링·OpenImageDenoise로 보완 |
| Noise Threshold 높이기(0.01 → 0.05)    | 일찍 멈춤, 약간 거칠어짐            |
| 반사 횟수(Bounces) 줄이기              | 실내 장면에서 효과 큼               |
| Caustics 끄기                          | 노이즈·시간 감소                    |
| 렌더 영역 지정(`Ctrl+B`, 카메라 시점)  | 일부만 렌더해 확인                  |
| 시뮬레이션·지오메트리 노드 캐시·베이크 | 프레임마다 다시 계산하지 않음       |

- 렌더 영역은 `Ctrl+B`로 지정하고 `Ctrl+Alt+B`로 해제합니다(키맵 확인, 화면 조작은 시험하지 않음).

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                       | 원인                              | 해결                                         |
|----------------------------|-----------------------------------|----------------------------------------------|
| "Cannot render, no camera" | 활성 카메라 없음                  | 카메라 추가, Scene 속성에서 Camera 지정      |
| 렌더가 새까맣게 나옴       | 조명이 너무 약함(새 Point 10W 등) | 세기 올리기, 월드 세기 확인                  |
| 하얗게 날아감              | 조명 과다                         | 세기 줄이기, View Transform AgX 유지         |
| Cycles 결과가 자글자글함   | 샘플 부족                         | 샘플·노이즈 제거 확인                        |
| GPU가 목록에 없음          | 드라이버·세대 미지원              | [설치](./blender_install.md) 2절 조건 확인   |
| 영상 파일이 중간에 깨짐    | 렌더 중단                         | 이미지 시퀀스로 렌더 후 합치기               |
| 배경이 투명하지 않음       | Film Transparent 꺼짐, JPEG 출력  | Transparent 켜고 PNG RGBA·EXR로 저장         |
| 렌더 결과가 저장되지 않음  | `F12`는 창에만 표시               | Image > Save As, 애니메이션은 출력 경로 확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 재질과 셰이딩](./blender_materials_shading.md) — 색 관리, 발광, 투명
- [Blender UV와 텍스처링](./blender_uv_texturing.md) — 베이크

---

## 참고 자료

- Blender Manual: [Lights](https://docs.blender.org/manual/en/latest/render/lights/index.html) · [Cameras](https://docs.blender.org/manual/en/latest/render/cameras.html) · [Output Properties](https://docs.blender.org/manual/en/latest/render/output/index.html) — ★★★☆☆
- Blender Manual: [Cycles](https://docs.blender.org/manual/en/latest/render/cycles/index.html) · [GPU Rendering](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html) · [EEVEE](https://docs.blender.org/manual/en/latest/render/eevee/index.html) — ★★★☆☆

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
