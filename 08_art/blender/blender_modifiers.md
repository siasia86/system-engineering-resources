# Blender 모디파이어
<!-- reference: _reference/blender_official_notes.md -->

모디파이어(Modifier)는 원본 메시를 바꾸지 않고 결과 모양만 바꾸는 비파괴 편집 기능입니다. 언제든 값을 바꾸거나 끄거나 지울 수 있고, 필요할 때 적용(Apply)해 메시에 반영합니다. 이 문서는 기본 사용법 → 스택 순서 → 자주 쓰는 모디파이어 6개 → 적용 시점 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 정육면체에 Subdivision Surface·Mirror·Array·Solidify·Bevel·Boolean을 붙여 기본값과 평가 결과(정점/모서리/면 수), 스택 순서 차이, 적용을 확인. 화면의 모디파이어 패널 조작은 실행하지 않았음

## 목차

| 섹션                                                                                 |
|--------------------------------------------------------------------------------------|
| [1. 기본 사용법](#1-기본-사용법) / [2. 스택 순서](#2-스택-순서) / [3. 종류](#3-종류) |
| [4. 자주 쓰는 모디파이어](#4-자주-쓰는-모디파이어) / [5. 적용 시점](#5-적용-시점)    |
| [6. 예제: 대칭 모델링](#6-예제-대칭-모델링) / [7. 트러블슈팅](#7-트러블슈팅)         |

---

## 1. 기본 사용법

1. 객체를 선택하고 Properties 편집기의 Modifiers 탭(렌치 모양)을 엽니다.
2. `Add Modifier` 메뉴에서 고릅니다. 위에서부터 차례로 쌓여 스택(Stack)이 됩니다.
3. 패널 머리줄 아이콘으로 Edit 모드 표시, 뷰포트 표시, 렌더 반영을 따로 켜고 끕니다.
4. 패널 오른쪽 아래쪽 화살표 메뉴에서 `Apply`(적용), `Duplicate`(복제), 순서 이동을 합니다.

- 단축키: Object 모드에서 `Ctrl+1`~`Ctrl+5`는 Subdivision Surface를 해당 단계로 추가하거나 바꿉니다.
- 같은 모디파이어를 여러 객체에 복사하려면 대상들을 선택하고 원본을 마지막에 선택한 뒤 `Ctrl+L` > `Copy Modifiers`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 스택 순서

모디파이어는 위에서 아래로 차례로 계산됩니다. 순서가 바뀌면 결과도 바뀝니다.

```text
원본 메시 ──▶ [1] Mirror ──▶ [2] Bevel ──▶ [3] Subdivision ──▶ 화면·렌더 결과
```

시험(정육면체, Subdivision 단계 1과 Bevel 폭 0.05):

| 순서                | 결과 (정점/모서리/면) | 모양                                         |
|---------------------|-----------------------|----------------------------------------------|
| Subdivision → Bevel | 96/192/98             | 먼저 둥글게 만든 뒤 모든 모서리를 깎음       |
| Bevel → Subdivision | 98/192/96             | 깎은 모서리가 지지 루프 역할, 각진 형태 유지 |

일반적인 순서:

| 위치    | 모디파이어                           | 이유                                       |
|---------|--------------------------------------|--------------------------------------------|
| 위쪽    | Mirror, Array                        | 모양을 먼저 복제해야 뒤 단계가 전체에 적용 |
| 가운데  | Boolean, Bevel, Solidify             | 기본 모양을 만드는 단계                    |
| 아래쪽  | Subdivision Surface, Smooth by Angle | 마지막에 매끈하게                          |
| 맨 아래 | Armature 등 변형                     | 완성된 모양을 움직임 (리깅 때)             |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 종류

5.3.0에는 Grease Pencil·물리 시뮬레이션용을 포함해 내장 모디파이어 83종이 있습니다. `Add Modifier` 메뉴는 여섯 분류로 나뉩니다(메뉴 정의 파일 확인).

| 분류     | 하는 일                 | 메시용 대표                                                                |
|----------|-------------------------|----------------------------------------------------------------------------|
| Edit     | 데이터(UV·가중치) 편집  | Data Transfer, UV Project, Vertex Weight Edit                              |
| Generate | 모양을 만들거나 바꿈    | Array, Bevel, Boolean, Mirror, Solidify, Subdivision Surface, Remesh, Weld |
| Deform   | 정점 위치만 옮김        | Armature, Curve, Displace, Lattice, Shrinkwrap, Simple Deform              |
| Normals  | 법선 조정               | Normal Edit, Weighted Normal, Smooth by Angle                              |
| Physics  | 시뮬레이션              | Cloth, Collision, Fluid, Soft Body, Ocean                                  |
| Color    | 색 (Grease Pencil 전용) | -                                                                          |

- 지오메트리 노드(Geometry Nodes)로 만든 모디파이어도 메뉴에 함께 나옵니다. 5.3은 기본 제공 노드 에셋으로 Array, Smooth by Angle, Curve to Tube, Scatter on Surface를 넣어 두었습니다.
- 5.3 Generate 메뉴의 "Array"는 노드 기반 새 판이고, 예전 내장 Array는 "Array (Legacy)"로 표시됩니다(4.3절).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 자주 쓰는 모디파이어

시험 결과는 기본 정육면체(정점 8/모서리 12/면 6)에 모디파이어 하나만 붙였을 때의 평가 결과입니다.

### 4.1 Subdivision Surface

면을 나눠 매끈하게 만듭니다.

| 항목        | 초기값                      | 시험               |
|-------------|-----------------------------|--------------------|
| 뷰포트 단계 | 1                           | 단계 2 → 98/192/96 |
| 렌더 단계   | 2                           | -                  |
| 방식        | Catmull-Clark (또는 Simple) | -                  |

- 단계가 하나 오를 때마다 면 수가 약 4배가 됩니다. 뷰포트는 낮게, 렌더는 높게 둡니다.
- 모서리를 덜 둥글게 하려면 지지 루프를 넣거나 Edit 모드에서 모서리 주름(Crease, `Shift+E`)을 씁니다.

### 4.2 Mirror

축을 기준으로 대칭 복제합니다. 기준은 객체의 원점(Origin)입니다.

| 항목     | 초기값 | 시험                                                         |
|----------|--------|--------------------------------------------------------------|
| 축       | X만    | 정육면체 → 16/24/12                                          |
| Merge    | 켬     | 한 면이 대칭면에 닿은 정육면체는 닿은 정점이 합쳐져 12/20/11 |
| Clipping | 끔     | 켜면 정점이 대칭면을 넘지 못함                               |

- 절반만 모델링하고 Mirror로 나머지를 만드는 것이 대칭 모델링의 기본입니다(6절).

### 4.3 Array

같은 모양을 일정 간격으로 반복합니다. 5.3에는 두 가지가 있습니다.

| 구분              | 방식                 | 초기값                                       | 시험              |
|-------------------|----------------------|----------------------------------------------|-------------------|
| Array (메뉴 기본) | 지오메트리 노드 에셋 | 모양 Line, 개수 3, 상대 간격 X 1.0, Merge 끔 | 그대로 24/36/18   |
| Array (Legacy)    | 내장 모디파이어      | Fixed Count, 상대 간격 X 1.0, Merge 끔       | 개수 3 → 24/36/18 |

- 새 Array는 모양(직선·원·곡선), 위치·회전·크기 무작위화, 첫·마지막 복제본 제외 같은 입력이 더 있습니다. 노드 그룹이라 Geometry Nodes 작업 공간에서 내부를 열어 볼 수 있습니다.
- 옛 파일의 Array는 Legacy 판으로 그대로 열립니다. 새로 만들 때는 메뉴 기본(새 판)이 붙습니다.
- 계단·울타리·체인에 씁니다. Legacy 판은 방식을 Fit Curve로 바꾸고 Curve 모디파이어와 함께 쓰면 곡선을 따라 늘어섭니다.

### 4.4 Solidify

면에 두께를 줍니다.

| 항목 | 초기값 | 시험                             |
|------|--------|----------------------------------|
| 두께 | 0.01   | 정육면체 → 16/24/12 (안팎 두 겹) |

- 평면으로 만든 벽·천·컵에 두께를 줄 때 씁니다. 두께 방향이 반대면 법선을 확인하거나 Offset을 바꿉니다.

### 4.5 Bevel

모서리를 깎습니다. Edit 모드 베벨(`Ctrl+B`)과 달리 값을 계속 바꿀 수 있습니다.

| 항목      | 초기값 | 시험                      |
|-----------|--------|---------------------------|
| 폭        | 0.1    | 정육면체 → 24/48/26       |
| 분할 수   | 1      | -                         |
| 제한 방식 | Angle  | 일정 각도 이상인 모서리만 |

- 실제 물체는 모서리가 완전히 날카롭지 않아서, 폭을 작게 준 Bevel만으로도 렌더의 하이라이트가 자연스러워집니다.
- 객체 크기를 적용하지 않으면 축마다 폭이 달라집니다([모델링](./blender_modeling.md) 4절).

### 4.6 Boolean

다른 객체로 빼기·합치기·교집합을 합니다.

| 항목 | 초기값     | 선택지                                                                                            |
|------|------------|---------------------------------------------------------------------------------------------------|
| 연산 | Difference | Intersect, Union, Difference                                                                      |
| 해법 | Exact      | Float(빠름, 겹친 형상 미지원), Exact(느림, 같은 평면 처리 우수), Manifold(가장 빠름, 닫힌 메시만) |

- 시험: 정육면체에서 UV 구를 빼면 265/526/263, 원기둥으로 구멍을 내면 세 해법 모두 72/112/40이었습니다.
- 자르는 객체는 Object Properties > Viewport Display에서 Display As를 `Wire`로 바꾸고 렌더에서 숨깁니다.
- 결과 면이 불규칙(다각형·가는 3각형)해서 서브디비전과 잘 맞지 않습니다. 하드 서피스(기계·건물)용으로 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 적용 시점

적용(Apply)하면 결과가 메시에 반영되고 해당 모디파이어는 스택에서 빠집니다. 되돌리려면 `Ctrl+Z`뿐입니다.

| 적용하는 경우                                  | 적용하지 않는 경우                                   |
|------------------------------------------------|------------------------------------------------------|
| 결과 메시를 직접 손봐야 할 때(Boolean 뒤 정리) | 값을 계속 조정할 때                                  |
| 스컬프팅·리깅 전에 모양을 확정할 때            | Subdivision처럼 뷰포트·렌더 단계를 나눌 때           |
| 모디파이어를 지원하지 않는 곳으로 내보낼 때    | FBX·glTF 내보내기에서 "Apply Modifiers" 옵션을 쓸 때 |

- 적용은 스택 맨 위부터 차례로 합니다. 아래 모디파이어를 먼저 적용하면 계산 순서가 바뀌어 결과가 달라질 수 있습니다.
- 시험: Array(Legacy, 개수 2)와 Subdivision이 차례로 쌓인 상태에서 첫 번째(Array)를 적용하자 메시가 16/24/12가 되고 스택에는 Subdivision만 남았습니다.
- 적용 전에 객체를 복제(`Shift+D`)해 숨겨 두면 원본을 남길 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 예제: 대칭 모델링

1. 정육면체를 추가하고 `Tab`으로 Edit 모드에 들어갑니다.
2. `Ctrl+R`로 가운데(X=0)에 루프 컷을 넣고, 한쪽 절반의 면을 선택해 `X` > Faces로 지웁니다.
3. `Tab`으로 나와 Mirror를 추가하고 Clipping을 켭니다. 가운데 정점이 대칭면에서 벗어나지 않습니다.
4. 남은 절반을 편집하면 반대쪽이 함께 바뀝니다.
5. Mirror 아래에 Subdivision Surface를 추가합니다. 순서가 반대면 가운데 이음매가 보입니다.
6. 모양이 확정되면 Mirror부터 위에서 차례로 적용합니다.

- 2·3단계의 루프 컷과 Clipping 동작은 화면에서 실행하지 않았습니다. 4.2절의 Mirror 기본값과 결과만 시험으로 확인했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                             | 원인                                      | 해결                                                           |
|----------------------------------|-------------------------------------------|----------------------------------------------------------------|
| Mirror 결과가 엉뚱한 위치에 생김 | 객체 원점이 대칭 중심에 없음              | 원점 옮기기(오른쪽 클릭 > Set Origin), 또는 Mirror Object 지정 |
| Mirror 가운데에 틈·겹침          | Merge 꺼짐, 가운데 정점이 0에서 벗어남    | Merge·Clipping 켬                                              |
| Subdivision 후 가운데 이음매     | Subdivision이 Mirror보다 위에 있음        | Mirror를 위로                                                  |
| Boolean 결과가 비거나 깨짐       | 자르는 객체가 닫힌 메시가 아님, 면이 겹침 | 해법을 Exact로, 자르는 메시의 구멍 메우기                      |
| Bevel이 일부 모서리에만 생김     | 제한 방식 Angle 기준 각도 미달            | 각도 낮추기 또는 제한 방식 None·Weight                         |
| Solidify 두께가 반대 방향        | 법선 방향                                 | `Shift+N` 또는 Offset 값 바꾸기                                |
| Apply가 회색으로 안 됨           | 다른 객체와 메시 데이터를 공유(연결 복제) | Object > Relations > Make Single User                          |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 모델링 기초](./blender_modeling.md) — Edit 모드 도구, 크기 적용
- [Blender 재질과 셰이딩](./blender_materials_shading.md) — 모양을 만든 다음 단계

---

## 참고 자료

- Blender Manual: [Modifiers](https://docs.blender.org/manual/en/latest/modeling/modifiers/index.html) · [Subdivision Surface](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/subdivision_surface.html) · [Boolean](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/booleans.html) — ★★★☆☆
- Blender Python API: [Modifier](https://docs.blender.org/api/current/bpy.types.Modifier.html) — 시험에 쓴 속성 — ★★★☆☆

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
