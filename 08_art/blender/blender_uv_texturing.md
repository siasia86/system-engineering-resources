# Blender UV와 텍스처링
<!-- reference: _reference/blender_official_notes.md -->

UV는 3D 표면을 2D 평면에 펼친 좌표입니다. 이미지 텍스처는 이 좌표를 따라 표면에 붙습니다. 이 문서는 UV 개념 → 심(Seam) 표시 → 펼치기 방법 → 정리·배치 → 텍스처 페인팅 → 베이크 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 정육면체에 Smart UV Project·심 표시·Unwrap·Cube Projection·Pack Islands를 실행하고 연산자 기본값을 확인. Cycles(CPU)로 Diffuse·Normal·Roughness·AO 베이크와 이미지 저장을 실행. UV Editor 화면 조작과 텍스처 페인팅 붓질은 실행하지 않았음

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. UV 개념](#1-uv-개념) / [2. 심 표시](#2-심-표시) / [3. 펼치기 방법](#3-펼치기-방법)           |
| [4. 정리와 배치](#4-정리와-배치) / [5. 텍스처 페인팅](#5-텍스처-페인팅) / [6. 베이크](#6-베이크) |
| [7. 예제: 상자 텍스처](#7-예제-상자-텍스처) / [8. 트러블슈팅](#8-트러블슈팅)                     |

---

## 1. UV 개념

```text
3D 메시 (정점마다 위치 x,y,z)          UV 공간 (정점마다 좌표 u,v, 0~1)
      +------+                          +------------------+
     /|     /|      ── 펼치기 ──▶       | [면][면][면]     |
    +------+ |                          | [면][면][면]     |  ← 이미지 텍스처가 놓이는 사각형
    | +----|-+                          |                  |
    |/     |/                           +------------------+
    +------+                           (0,0)            (1,0)
```

- UV 좌표는 0~1 사각형 안에 놓는 것이 기본입니다. 밖으로 나가면 텍스처가 반복(타일)됩니다.
- 펼친 조각 하나를 섬(Island)이라고 합니다. 섬 경계는 심(Seam)으로 정합니다.
- 한 메시에 UV 맵을 여러 개 둘 수 있습니다(Properties > Data > UV Maps). 기본 도형에는 `UVMap` 하나가 있습니다.
- UV Editing 작업 공간은 왼쪽 UV Editor, 오른쪽 3D 뷰포트(Edit 모드)로 열립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 심 표시

심은 "여기를 잘라서 펼친다"는 표시입니다. 종이 상자 전개도의 자르는 선과 같습니다.

1. Edit 모드에서 모서리 선택(`2`)으로 바꿉니다.
2. 자를 모서리를 선택하고 `Ctrl+E` > `Mark Seam`. 빨간 선으로 표시됩니다.
3. 잘못 넣은 심은 `Ctrl+E` > `Clear Seam`.

| 모델           | 심 넣는 곳                                |
|----------------|-------------------------------------------|
| 상자           | 전개도처럼 윗면 3변, 아랫면 3변, 세로 1변 |
| 원기둥         | 위·아래 원 테두리, 세로 1줄               |
| 캐릭터 팔·다리 | 안쪽(잘 안 보이는 곳)으로 세로 1줄        |
| 얼굴           | 귀 뒤, 머리카락 경계                      |

- 심은 눈에 덜 띄는 곳에 넣습니다. 이음매에서 텍스처가 끊겨 보일 수 있기 때문입니다.
- 시험: 정육면체 모든 모서리(12개)를 선택해 Mark Seam을 실행하면 심 12개가 표시되었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 펼치기 방법

Edit 모드에서 면을 선택하고 `U`를 누르면 펼치기 메뉴가 나옵니다.

| 메뉴                         | 동작                                | 쓰는 때                            |
|------------------------------|-------------------------------------|------------------------------------|
| Unwrap                       | 심을 따라 펼침                      | 심을 직접 넣은 모델(기본)          |
| Smart UV Project             | 면 각도 기준으로 자동으로 잘라 펼침 | 기계·건물처럼 각진 모델, 빠른 작업 |
| Cube Projection              | 6방향에서 투영                      | 상자 모양                          |
| Cylinder / Sphere Projection | 원기둥·구 모양으로 투영             | 병·공                              |
| Project From View            | 지금 시점에서 그대로 투영           | 정면에서 보이는 평면 장식          |

연산자 기본값(5.3.0):

| 연산자           | 항목        | 초기값                                           |
|------------------|-------------|--------------------------------------------------|
| Unwrap           | 방식        | Conformal (그 밖에 Angle Based, Minimum Stretch) |
| Unwrap           | 여백        | 0.001                                            |
| Unwrap           | 종횡비 보정 | 켬                                               |
| Smart UV Project | 각도 한계   | 66도 (1.152 라디안)                              |
| Smart UV Project | 섬 여백     | 0                                                |

- 시험: Smart UV Project, Mark Seam 뒤 Unwrap(Angle Based), Cube Projection을 차례로 실행해 모두 성공했습니다.
- Conformal은 각도를 지키고 빠릅니다. Angle Based는 굽은 면에서 늘어남이 적습니다. 결과가 이상하면 방식을 바꿔 다시 펼칩니다(`F9`).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 정리와 배치

| 작업           | 방법                                                |
|----------------|-----------------------------------------------------|
| 섬 자동 배치   | UV Editor > UV > Pack Islands                       |
| 늘어남 확인    | UV Editor 오버레이 > Display Stretch                |
| 텍셀 밀도 확인 | 격자 이미지(UV Grid·Color Grid)를 입혀 칸 크기 비교 |
| 섬 선택        | UV Editor에서 `L`(마우스 아래 섬)                   |
| 이동·회전·크기 | UV Editor에서 `G`·`R`·`S`                           |

- 시험: Cube Projection 뒤 Pack Islands(여백 0.01)를 실행하자 UV 좌표가 u 0.001~0.499, v 0.001~0.999 안으로 모였습니다.
- 격자 이미지는 Image Editor > New Image에서 Generated Type을 `Color Grid` 또는 `UV Grid`로 만듭니다. 칸이 정사각형이고 크기가 고르면 잘 펼쳐진 것입니다.
- 텍셀 밀도(표면 1m당 텍스처 픽셀 수)를 모델 전체에서 비슷하게 맞추면 해상도가 고르게 보입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 텍스처 페인팅

모델 위에 직접 색을 칠해 이미지 텍스처를 만듭니다.

1. 객체에 재질과 이미지 텍스처 노드가 있어야 합니다. 없으면 Texture Paint 작업 공간 Properties의 Texture Slots에서 `+`로 Base Color 이미지를 만듭니다.
2. Texture Paint 작업 공간에서 왼쪽 버튼으로 칠합니다. `F`로 브러시 크기, `Shift+F`로 세기를 바꿉니다(키맵 확인).
3. 칠한 이미지는 저장해야 남습니다. Image Editor > Image > Save, 또는 `File > External Data > Pack Resources`로 `.blend`에 넣습니다.

- 칠하기 전에 UV가 펼쳐져 있어야 합니다. UV가 겹치면 한 곳을 칠할 때 겹친 곳에도 칠해집니다.
- 이 절의 붓질은 화면 조작이라 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 베이크

베이크(Bake)는 조명·재질·고해상도 모양의 결과를 이미지 텍스처에 구워 넣는 작업입니다. 게임 엔진으로 옮기거나 렌더를 가볍게 할 때 씁니다.

준비:

1. 렌더 엔진을 Cycles로 바꿉니다(베이크는 Cycles 기능).
2. 재질의 Node Editor에 대상 이미지를 고른 `Image Texture` 노드를 하나 두고, 그 노드를 클릭해 활성 노드로 만듭니다(다른 곳에 연결하지 않아도 됨).
3. Properties > Render > Bake에서 종류를 고르고 `Bake`를 누릅니다.
4. 결과 이미지를 저장합니다(Image > Save As).

| 종류      | 굽는 내용                                               | 쓰는 곳                  |
|-----------|---------------------------------------------------------|--------------------------|
| Combined  | 조명까지 포함한 최종 색                                 | 조명 고정 장면(라이트맵) |
| Diffuse   | 색(Color만 고르면 조명 없는 알베도)                     | 재질 단순화              |
| Normal    | 법선(고해상도 → 저해상도 디테일 옮기기)                 | 게임용 노멀 맵           |
| AO        | 주변 차폐(틈 그림자)                                    | 질감 강조, 게임 텍스처   |
| Roughness | 거칠기                                                  | PBR 텍스처 내보내기      |
| Emit      | 발광                                                    | 발광 맵                  |
| 그 밖에   | Shadow, Position, UV, Environment, Glossy, Transmission | -                        |

- 시험: 정육면체(UV 펼침)에 128×128 이미지를 두고 Diffuse(Color만)·Normal·Roughness·AO를 Cycles CPU로 베이크해 모두 성공했고 PNG로 저장했습니다.
- 고해상도 모델의 디테일을 저해상도 모델에 굽으려면 고해상도 → 저해상도 순으로 선택하고 Bake 설정에서 `Selected to Active`를 켭니다(매뉴얼 기준, 시험하지 않음).
- 이음매에 틈이 보이면 Bake 설정의 Margin(여백 픽셀)을 늘립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 예제: 상자 텍스처

1. 정육면체를 선택하고 UV Editing 작업 공간으로 갑니다.
2. 모서리 선택으로 전개도 모양의 심을 넣습니다(2절 표).
3. `A`로 모두 선택하고 `U` > `Unwrap`.
4. UV Editor에서 New Image > Color Grid 이미지를 만들어 격자가 고른지 확인합니다.
5. Shading 작업 공간에서 이 이미지를 Image Texture로 Base Color에 연결합니다([재질과 셰이딩](./blender_materials_shading.md) 3절).
6. 실제 텍스처 이미지로 바꾸거나 Texture Paint로 칠합니다.

- 4~5단계(Color Grid 이미지를 Base Color에 연결해 렌더)는 재질 문서 시험에서 확인했습니다. 2단계의 전개도 심 배치는 화면에서 실행하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                        | 원인                            | 해결                                           |
|-------------------------------------------------------------|---------------------------------|------------------------------------------------|
| 텍스처가 한쪽으로 쭉 늘어남                                 | 심이 부족해 억지로 펼쳐짐       | 심 추가 후 다시 Unwrap, Display Stretch로 확인 |
| 일부 면에 텍스처가 안 보임                                  | 그 면의 UV가 한 점으로 모임     | 해당 면 선택 후 다시 펼치기                    |
| 칠하면 다른 곳에도 칠해짐                                   | UV 섬이 겹침                    | Pack Islands로 겹침 제거                       |
| 베이크 시 "No active and selected image texture node found" | 활성 Image Texture 노드가 없음  | 재질에 Image Texture 노드를 두고 클릭해 활성화 |
| 베이크 결과가 까맣게 나옴                                   | 조명 없는 Combined, 법선 뒤집힘 | 종류·Pass 확인, `Shift+N`                      |
| 베이크 결과 이음매에 선이 보임                              | Margin이 작음                   | Margin 늘리기                                  |
| 저장 후 칠한 텍스처가 사라짐                                | 이미지를 저장하지 않음          | Image > Save 또는 Pack Resources               |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 재질과 셰이딩](./blender_materials_shading.md) — 텍스처 연결, 색 공간
- [Blender 모델링 기초](./blender_modeling.md) — Edit 모드 선택

---

## 참고 자료

- Blender Manual: [UVs](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/index.html) · [Unwrapping](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html) · [Texture Paint](https://docs.blender.org/manual/en/latest/sculpt_paint/texture_paint/index.html) — ★★★☆☆
- Blender Manual: [Cycles Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html) — ★★★☆☆

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
