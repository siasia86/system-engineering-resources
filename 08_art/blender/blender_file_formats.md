# Blender 파일 형식과 내보내기
<!-- reference: _reference/blender_official_notes.md -->

Blender 작업 파일은 `.blend`이고, 다른 프로그램·게임 엔진·3D 프린터로 보낼 때는 형식을 바꿔 내보냅니다. 이 문서는 `.blend` 관리 → 형식별 특징 → 내보내기 기본값 → 왕복 시험 결과 → 게임 엔진으로 보낼 때 점검 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 Bevel 모디파이어·빨간 재질·위치 애니메이션을 가진 상자를 OBJ·STL·PLY·FBX·glTF(GLB)·USD·Alembic으로 내보낸 뒤 각각 다시 가져와 정점·면 수, 크기, 재질, 애니메이션이 남는지 확인하고 내보내기 연산자 기본값을 확인. 외부 프로그램(게임 엔진·다른 3D 도구)에서 연 결과는 확인하지 않았음

## 목차

| 섹션                                                                                         |
|----------------------------------------------------------------------------------------------|
| [1. blend 파일](#1-blend-파일) / [2. 형식 비교](#2-형식-비교) / [3. 왕복 시험](#3-왕복-시험) |
| [4. 내보내기 기본값](#4-내보내기-기본값) / [5. 축과 단위](#5-축과-단위)                      |
| [6. 게임 엔진으로 보내기](#6-게임-엔진으로-보내기) / [7. 트러블슈팅](#7-트러블슈팅)          |

---

## 1. blend 파일

- `.blend`에는 장면·메시·재질·애니메이션·설정이 모두 들어 있습니다. 이미지 텍스처는 기본으로 바깥 파일을 경로로 참조합니다.
- 이미지까지 한 파일에 넣으려면 `File > External Data > Pack Resources`. 다른 PC로 옮길 때 텍스처가 분홍색으로 빠지는 문제를 막습니다.
- 경로를 상대 경로(`//textures/a.png`)로 두면 폴더째 옮겨도 깨지지 않습니다. `File > External Data > Make Paths Relative`.
- 저장하면 이전 판이 `.blend1`로 남습니다(Save Versions 초기값 1). 자동 저장 임시 파일은 2분마다 만들어집니다([설치](./blender_install.md) 4절).
- 다른 `.blend`의 객체·재질은 `File > Append`(복사해 오기) 또는 `File > Link`(원본 참조, 원본을 고치면 따라 바뀜)로 가져옵니다.
- 새 판에서 저장한 `.blend`는 옛 판에서 일부 기능이 빠지거나 열리지 않을 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 형식 비교

| 형식     | 확장자                   | 담는 것                               | 주로 쓰는 곳                             |
|----------|--------------------------|---------------------------------------|------------------------------------------|
| glTF 2.0 | `.glb`, `.gltf`          | 메시·PBR 재질·텍스처·뼈대·애니메이션  | 웹(three.js 등), Godot, 범용 교환        |
| FBX      | `.fbx`                   | 메시·재질(단순)·뼈대·애니메이션       | Unity, Unreal, Maya·3ds Max 교환         |
| OBJ      | `.obj` + `.mtl`          | 메시·UV·법선·단순 재질                | 정적 모델 교환, 오래된 도구              |
| USD      | `.usd`, `.usdc`, `.usda` | 장면 계층·메시·재질·(선택) 애니메이션 | 영상 파이프라인, Omniverse, Apple 생태계 |
| Alembic  | `.abc`                   | 프레임별 메시 캐시(변형 애니메이션)   | 시뮬레이션·변형을 다른 렌더러로 넘기기   |
| STL      | `.stl`                   | 3각형 메시만                          | 3D 프린팅                                |
| PLY      | `.ply`                   | 메시·정점 색                          | 3D 스캔, 점군                            |

- 5.3.0의 OBJ·STL·PLY·USD·Alembic 입출력은 내장 기능(`wm.*_export`)이고, glTF와 FBX는 함께 배포되는 애드온(`io_scene_gltf2`, `io_scene_fbx`)입니다. 시험 환경(`bpy` 모듈)에서는 두 애드온을 켠 뒤에 쓸 수 있었습니다.
- 처음 고를 때: 웹·Godot·범용은 glTF, Unity·Unreal은 FBX 또는 glTF, 3D 프린터는 STL, 영상 합성 파이프라인은 USD·Alembic.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 왕복 시험

크기 2m 상자에 Bevel 모디파이어(폭 0.1, 적용 전 원본 정점 8)·재질 `Red`·위치 키프레임 2개를 넣고 내보낸 뒤 다시 가져왔습니다(내보내기 기본값 그대로).

| 형식       | 파일 크기 | 다시 가져온 정점/면 | 크기 2m 유지 | 재질   | 애니메이션 | 비고                                     |
|------------|-----------|---------------------|--------------|--------|------------|------------------------------------------|
| OBJ        | 2,986 B   | 24 / 26             | 예           | 예     | 아니요     | 객체 회전이 X 90도로 들어옴(축 변환)     |
| STL        | 2,284 B   | 24 / 44             | 예           | 아니요 | 아니요     | 모든 면이 3각형으로 바뀜                 |
| PLY        | 1,317 B   | 33 / 26             | 예           | 아니요 | 아니요     | -                                        |
| FBX        | 21,852 B  | 24 / 26             | 예           | 예     | 예         | -                                        |
| glTF (GLB) | 2,540 B   | 24 / 12             | 예           | 예     | 예         | Bevel이 빠지고 3각형 12개(원래 정육면체) |
| USD (usdc) | 3,509 B   | 24 / 26             | 예           | 예     | 아니요     | 기본값에서 애니메이션 내보내기 꺼짐      |
| Alembic    | 6,587 B   | 24 / 26             | 예           | 아니요 | 예         | 캐시로 재생                              |

알 수 있는 점:

- glTF는 기본값에서 모디파이어를 적용하지 않습니다(`export_apply` 꺼짐). 베벨·서브디비전·지오메트리 노드 결과를 내보내려면 내보내기 창의 Mesh 옵션에서 `Apply Modifiers`를 켭니다.
- OBJ·FBX·USD·Alembic·STL·PLY는 기본값에서 모디파이어를 적용해 내보냈습니다(정점 24 = 베벨 결과).
- USD는 애니메이션을 내보내려면 `Animation` 옵션을 켜야 합니다.
- 3D 프린팅용 STL·PLY에는 재질이 들어가지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 내보내기 기본값

`File > Export`의 각 형식 창 오른쪽에 옵션이 있습니다. 5.3.0 연산자 기본값:

| 형식 | 주요 기본값                                                                                                                                             |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| OBJ  | Apply Modifiers 켬, Materials 켬, UV·Normals 켬, 3각형 변환 끔, Forward -Z, Up Y, Scale 1.0                                                             |
| FBX  | Apply Modifiers 켬, Apply Unit 켬, Apply Scalings "All Local", Forward -Z, Up Y, Scale 1.0, Bake Animation 켬, Add Leaf Bones 켬, 텍스처 포함(Embed) 끔 |
| glTF | Apply Modifiers 끔, +Y Up 켬, Animation 켬, 이미지 형식 Automatic, Draco 압축 끔, 선택만 끔                                                             |
| USD  | Materials 켬, Animation 끔, 평가 모드 Render, 축 변환 끔, 텍스처 새로 쓰기                                                                              |

- FBX의 Apply Scalings 기본값 표시 이름은 연산자 값 `FBX_SCALE_NONE`("All Local")입니다.
- FBX는 Add Leaf Bones가 켜져 있으면 뼈 끝마다 `_end` 뼈가 추가됩니다. 게임 엔진에서 뼈 수가 늘어나는 것이 싫으면 끕니다.
- FBX의 Path Mode를 `Copy`로 바꾸고 Embed Textures(오른쪽 상자 아이콘)를 켜면 텍스처를 파일 안에 넣습니다.
- 내보내기 창 위쪽에서 설정을 프리셋으로 저장해 두면 매번 같은 옵션을 쓸 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 축과 단위

| 프로그램      | 위쪽 축 | 단위(일반) |
|---------------|---------|------------|
| Blender       | Z       | 1 = 1m     |
| glTF 규격     | Y       | 1 = 1m     |
| Unity         | Y       | 1 = 1m     |
| Unreal Engine | Z       | 1 = 1cm    |
| Godot         | Y       | 1 = 1m     |

- 내보내기의 Forward·Up 축 설정이 축 차이를 바꿔 줍니다. OBJ·FBX 기본값(Forward -Z, Up Y)과 glTF의 +Y Up은 Y 위쪽 프로그램을 기준으로 한 값입니다.
- 내보내기 전에 객체의 회전·크기를 적용(`Ctrl+A` > All Transforms)해 두면 다른 프로그램에서 회전 90도·크기 100배 같은 문제가 줄어듭니다.
- Unreal로 FBX를 보낼 때 크기 문제는 장면 단위 설정(Scene > Units > Unit Scale)이나 내보내기 Scale로 맞춥니다. 이 표의 엔진 축·단위는 각 엔진의 일반 기본값이며 이 문서에서 엔진으로 열어 확인하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 게임 엔진으로 보내기

내보내기 전 점검:

1. 모든 객체의 회전·크기 적용(`Ctrl+A`).
2. 원점(Origin) 위치를 엔진에서 쓸 기준점(바닥 가운데 등)으로.
3. 법선 방향 확인(Overlays > Face Orientation, 빨간 면 없음).
4. 겹친 정점 정리(Merge by Distance).
5. UV 펼침 확인, 텍스처는 PNG 등 엔진이 읽는 형식.
6. 재질은 Principled BSDF 하나에 텍스처를 직접 연결하는 단순 구조(복잡한 노드는 대부분 옮겨지지 않음).
7. 모디파이어 적용 여부 확인(glTF는 옵션 필요).
8. 애니메이션은 액션 이름을 정리하고 필요 없는 액션은 지움.
9. 이름에 한글·공백 대신 영문·밑줄 사용.

| 엔진   | 권장 형식      | 참고                                                 |
|--------|----------------|------------------------------------------------------|
| Unity  | FBX, glTF      | glTF는 별도 패키지가 필요할 수 있음(엔진 문서 확인)  |
| Unreal | FBX, glTF, USD | 단위 cm 차이 주의                                    |
| Godot  | glTF           | `.blend`를 직접 가져오는 기능도 있음(엔진 문서 확인) |
| 웹     | glTF(GLB)      | Draco 압축으로 크기 줄이기                           |

- 엔진 쪽 설명(패키지·가져오기 기능)은 각 엔진 문서 기준이며 이 문서에서 확인하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                              | 원인                            | 해결                                            |
|-----------------------------------|---------------------------------|-------------------------------------------------|
| glTF에 베벨·서브디비전이 빠짐     | glTF 기본값이 모디파이어 미적용 | Apply Modifiers 켜기                            |
| 다른 프로그램에서 누워 있음(90도) | 축 설정 차이, 회전 미적용       | 회전 적용 후 Forward·Up 축 확인                 |
| 크기가 100배·0.01배               | 단위 차이(m ↔ cm)               | Unit Scale·내보내기 Scale·Apply Unit 확인       |
| 텍스처가 빠짐(분홍·흰색)          | 이미지가 외부 경로, 복사 안 됨  | Pack Resources, FBX Path Mode Copy + Embed, GLB |
| USD에 애니메이션 없음             | 기본값에서 Animation 꺼짐       | 내보내기 창에서 Animation 켬                    |
| 뼈가 하나씩 더 생김(`_end`)       | FBX Add Leaf Bones 켜짐         | 옵션 끄기                                       |
| STL로 출력했더니 색이 없음        | STL은 형상만 담음               | 색이 필요하면 다른 형식(3MF·PLY 정점 색 등)     |
| 메뉴에 glTF·FBX가 없음            | 해당 애드온이 꺼짐              | Preferences > Add-ons에서 켜기                  |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 모디파이어](./blender_modifiers.md) — 적용 시점
- [Blender 애니메이션과 리깅](./blender_animation_rigging.md) — 액션, 뼈대

---

## 참고 자료

- Blender Manual: [Import & Export](https://docs.blender.org/manual/en/latest/files/import_export/index.html) · [glTF 2.0](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html) · [FBX](https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html) — ★★★☆☆
- Blender Manual: [USD](https://docs.blender.org/manual/en/latest/files/import_export/usd.html) · [Linked Libraries](https://docs.blender.org/manual/en/latest/files/linked_libraries/index.html) — ★★★☆☆
- Khronos: [glTF 2.0 규격](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) — Y 위쪽, 미터 단위 — ★★★☆☆

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
