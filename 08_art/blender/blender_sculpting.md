# Blender 스컬프팅
<!-- reference: _reference/blender_official_notes.md -->

스컬프팅(Sculpting)은 점토를 빚듯 브러시로 표면을 밀고 당겨 모양을 만드는 작업입니다. 정점을 하나씩 옮기는 모델링과 달리 수십만~수백만 면을 다룹니다. 이 문서는 시작 준비 → 브러시 → 해상도 관리(복셀 리메시·다인토포·Multires) → 대칭과 마스크 → 리토폴로지 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 기본 제공 스컬프트 브러시 목록, Sculpt 모드 키맵, 복셀 리메시(크기 0.1·0.05)와 Multires 3단계 결과, 다인토포 켜기와 기본값을 확인. 브러시 붓질은 화면 조작이라 실행하지 않았음

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 시작 준비](#1-시작-준비) / [2. 브러시](#2-브러시) / [3. 붓질 조작](#3-붓질-조작)                     |
| [4. 해상도 관리](#4-해상도-관리) / [5. 대칭과 마스크](#5-대칭과-마스크) / [6. 리토폴로지](#6-리토폴로지) |
| [7. 예제: 돌멩이](#7-예제-돌멩이) / [8. 트러블슈팅](#8-트러블슈팅)                                       |

---

## 1. 시작 준비

1. 시작 도형을 추가합니다. 고르게 나뉜 면이 좋으므로 Ico Sphere나 Quad Sphere(정육면체 + Subdivision 적용)를 많이 씁니다.
2. 상단 탭에서 Sculpting 작업 공간을 엽니다. 객체가 Sculpt 모드로 바뀝니다.
3. 면이 너무 적으면 붓질이 뭉개지므로 먼저 해상도를 올립니다(4절). 복셀 리메시가 가장 간단합니다.

- 펜 태블릿을 쓰면 필압으로 크기·세기를 조절할 수 있습니다. 브러시 설정의 필압 버튼을 켭니다.
- 마우스로도 할 수 있지만 세기를 낮추고 여러 번 겹쳐 칠합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 브러시

5.x에서 브러시는 에셋(Asset)입니다. 기본 제공 메시 스컬프트 브러시는 64개이고 `Shift+Space`의 브러시 선반(Asset Shelf)에서 고릅니다. Sculpt 모드에 처음 들어가면 Draw 브러시가 선택되어 있습니다.

자주 쓰는 브러시와 단축키(초기 설정 키맵 확인):

| 키        | 브러시          | 하는 일                            |
|-----------|-----------------|------------------------------------|
| `V`       | Draw            | 표면을 밀어 올림(기본)             |
| `C`       | Clay Strips     | 점토 띠를 덧붙이듯 쌓음, 형태 잡기 |
| `S`       | Smooth          | 울퉁불퉁한 곳을 고름               |
| `G`       | Grab            | 영역을 잡아 끌어 큰 형태 이동      |
| `K`       | Snake Hook      | 길게 잡아 늘림(뿔·촉수)            |
| `P`       | Pinch/Magnify   | 모아서 날카로운 주름               |
| `I`       | Inflate/Deflate | 부풀리거나 줄임                    |
| `Shift+T` | Scrape/Fill     | 깎아 평평하게 / 오목한 곳 채움     |
| `Shift+C` | Crease Polish   | 깊은 주름 새기기                   |
| `M`       | Mask            | 칠한 곳을 보호(5절)                |

- 그 밖에 Clay, Clay Thumb, Layer, Flatten/Contrast, Blob, Elastic Grab, Pose, Boundary, 천(Cloth) 계열 등이 있습니다.
- 작업 순서는 큰 형태(Grab·Clay Strips) → 중간 형태(Draw·Inflate) → 세부(Crease·Pinch) → 정리(Smooth)입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 붓질 조작

| 키                    | 동작                         |
|-----------------------|------------------------------|
| 왼쪽 버튼 끌기        | 칠하기                       |
| `Ctrl` + 끌기         | 반대 방향(누르기 ↔ 올리기)   |
| `Shift` + 끌기        | 잠시 Smooth 브러시로         |
| `Alt` + 끌기          | 잠시 Mask 브러시로           |
| `F` / `Shift+F`       | 브러시 크기 / 세기           |
| `[` / `]`             | 크기 10% 줄이기 / 늘리기     |
| `Shift` + 오른쪽 클릭 | 회전 중심을 표면의 그 점으로 |
| `Shift+Space`         | 브러시 선반                  |

- 크기는 화면 기준(새 브러시 초기값 `VIEW`, 시험 확인)이라 확대하면 같은 크기여도 모델 위에서는 작게 칠해집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 해상도 관리

면 수를 어떻게 늘리고 관리할지 세 가지 방법이 있습니다.

| 방법              | 동작                                     | 장점                             | 단점                            |
|-------------------|------------------------------------------|----------------------------------|---------------------------------|
| 복셀 리메시       | 모양을 일정한 크기의 격자로 다시 만듦    | 고르게 분포, 늘어난 면 정리      | 세부가 크기에 따라 뭉개짐       |
| 다인토포(Dyntopo) | 붓질하는 곳만 실시간으로 면을 나눔·합침  | 필요한 곳만 세밀                 | 3각형 메시, UV·정점 그룹이 깨짐 |
| Multires          | 단계별 세분 모디파이어, 단계 오가며 조각 | 저해상도 원본 유지, 노멀 맵 굽기 | 원래 토폴로지가 좋아야 함       |

### 4.1 복셀 리메시

| 키       | 동작                             |
|----------|----------------------------------|
| `R`      | 복셀 크기 조절(화면에 격자 표시) |
| `Ctrl+R` | 리메시 실행                      |

- 시험: UV 구(정점 482)에 복셀 크기 0.1(초기값)로 리메시하자 정점 2000개, 0.05로 하자 7672개가 되었습니다. 크기를 반으로 줄이면 면 수는 약 4배입니다.
- 리메시는 UV·정점 그룹 등 데이터를 잃을 수 있으니 세부 작업 전에 합니다.
- 4각형 위주의 메시가 필요하면 QuadriFlow 리메시(Object Data > Remesh)를 씁니다(5.3.0에 연산자 있음 확인, 결과는 시험하지 않음).

### 4.2 다인토포

- 머리줄의 Dyntopo 체크로 켭니다. 시험에서 켜기가 성공했고 기본값은 세부 방식 Relative Detail, 세부 크기 12픽셀, Subdivide Collapse(나누기와 합치기 모두)였습니다.
- `R`로 세부 크기, `Ctrl+R`로 지정한 세부로 전체를 채웁니다(Dyntopo 켠 상태의 키맵).

### 4.3 Multires

- Properties > Modifiers에서 Multiresolution을 추가하고 `Subdivide`를 누를 때마다 한 단계 올라갑니다. 방식은 Catmull-Clark(초기값)·Simple·Linear입니다.
- 시험: 정육면체에 Multires를 붙이고 3번 세분하자 뷰포트·스컬프트·렌더 단계가 모두 3, 평가 결과 정점 386·면 384가 되었습니다.
- 낮은 단계에서 큰 형태, 높은 단계에서 세부를 칠하고, 낮은 단계 메시를 게임 엔진용으로 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대칭과 마스크

### 5.1 대칭

- 3D 뷰포트 머리줄 오른쪽의 대칭(Mirror) X·Y·Z 버튼으로 켭니다. 얼굴·몸은 X를 켭니다.
- 대칭 설정은 메시마다 저장됩니다. 시험한 기본 정육면체·새 UV 구는 모두 꺼져 있었습니다(`use_mirror_x` False).
- 대칭은 객체의 원점과 지역 축 기준입니다. 원점이 가운데가 아니면 엇갈려 칠해집니다.

### 5.2 마스크

마스크는 칠한 곳을 붓질에서 보호합니다(검게 표시).

| 키                        | 동작                |
|---------------------------|---------------------|
| `M` 브러시, `Alt` + 끌기  | 마스크 칠하기       |
| `Ctrl+I`                  | 마스크 반전         |
| `Alt+M`                   | 마스크 지우기       |
| `B`                       | 상자로 마스크       |
| `Ctrl` + 오른쪽 버튼 끌기 | 올가미로 마스크     |
| `A`                       | 마스크 원형 메뉴    |
| `Shift+A`                 | 마스크 확장(Expand) |

- 면 집합(Face Set)은 영역을 색으로 나누는 기능입니다. `H`로 활성 면 집합 숨기기, `Shift+H`로 그것만 보기, `Alt+H`로 모두 보이기.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 리토폴로지

스컬프팅 결과는 면이 너무 많고 흐름이 불규칙해서 애니메이션·게임에 그대로 쓰기 어렵습니다. 리토폴로지(Retopology)는 그 위에 깔끔한 저해상도 메시를 새로 덮어 만드는 작업입니다.

1. 새 평면을 추가하고 Edit 모드에서 정점 하나만 남깁니다.
2. 스냅을 켜고(`Shift+Tab`) 스냅 대상을 Face Project(표면에 붙이기)로 바꿉니다.
3. 정점을 `E`로 돌출하고 `F`로 면을 만들며 표면을 따라 4각형을 깝니다.
4. Shrinkwrap 모디파이어로 표면에 붙여 둡니다.
5. 스컬프트의 세부는 노멀 맵으로 구워 옮깁니다([UV와 텍스처링](./blender_uv_texturing.md) 6절 Selected to Active).

- 빠른 방법으로 복셀 리메시나 QuadriFlow 결과를 다듬어 쓰기도 합니다.
- 이 절은 화면 조작이라 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 예제: 돌멩이

1. Ico Sphere(Subdivisions 4 정도)를 추가하고 Sculpting 작업 공간으로 갑니다.
2. `R`로 복셀 크기를 정하고 `Ctrl+R`로 리메시합니다.
3. Grab(`G`)으로 둥근 모양을 찌그러뜨려 불규칙하게 만듭니다.
4. Scrape/Fill(`Shift+T`)로 평평한 면을 몇 군데 깎습니다.
5. Crease Polish(`Shift+C`)로 갈라진 틈을 새기고, Smooth(`Shift` + 끌기)로 다듬습니다.
6. Object 모드로 돌아가 재질을 입힙니다([재질과 셰이딩](./blender_materials_shading.md)).

- 2단계 리메시는 4.1절에서 시험했고, 3~5단계 붓질은 실행하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                           | 원인                                  | 해결                                          |
|------------------------------------------------|---------------------------------------|-----------------------------------------------|
| 칠해도 각지게 뭉개짐                           | 면 수 부족                            | 복셀 리메시·Multires·다인토포로 해상도 올리기 |
| 아무것도 안 칠해짐                             | 마스크가 덮임, 숨긴 면                | `Alt+M`으로 마스크 지우기, `Alt+H`            |
| 대칭이 엇갈림                                  | 원점이 가운데가 아님, 회전 적용 안 됨 | 원점 옮기기, `Ctrl+A`로 회전·크기 적용        |
| 리메시 후 구멍이 메워지거나 얇은 부분이 사라짐 | 복셀 크기가 부분 두께보다 큼          | 복셀 크기 줄이기                              |
| 다인토포를 켰더니 UV가 사라졌다는 경고         | 다인토포는 UV를 보존하지 않음         | 스컬프트 후 리토폴로지·UV를 새로 만듦         |
| 매우 느려짐                                    | 면 수가 너무 많음                     | 복셀 크기 키우기, Multires 낮은 단계에서 작업 |
| 브러시 크기가 확대·축소 때 바뀜                | 크기가 화면 기준                      | 브러시 설정에서 Scene 기준으로 바꾸기         |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 모델링 기초](./blender_modeling.md) — 토폴로지 원칙
- [Blender UV와 텍스처링](./blender_uv_texturing.md) — 노멀 맵 베이크

---

## 참고 자료

- Blender Manual: [Sculpt Mode](https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/index.html) · [Brushes](https://docs.blender.org/manual/en/latest/sculpt_paint/brush/index.html) · [Remesh](https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html) — ★★★☆☆
- Blender Manual: [Multiresolution Modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/multiresolution.html) — ★★★☆☆

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
