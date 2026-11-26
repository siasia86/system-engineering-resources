# Blender 화면 구성
<!-- reference: _reference/blender_official_notes.md -->

Blender 화면은 작업 공간(Workspace) 탭 아래에 여러 편집기(Editor)를 나눠 배치한 구조입니다. 이 문서는 화면 요소 → 작업 공간 → 편집기 종류 → 모드 → 3D 뷰포트 조작 → 화면 나누기 → 처음 바꿀 설정 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 기본 작업 공간 11개의 모드·편집기 배치, 편집기 종류, 기본 장면을 읽어 확인. 화면을 띄워 조작하지는 않았음

## 목차

| 섹션                                                                                 |
|--------------------------------------------------------------------------------------|
| [1. 화면 요소](#1-화면-요소) / [2. 작업 공간](#2-작업-공간) / [3. 편집기](#3-편집기) |
| [4. 모드](#4-모드) / [5. 3D 뷰포트](#5-3d-뷰포트) / [6. 화면 나누기](#6-화면-나누기) |
| [7. 처음 바꿀 설정](#7-처음-바꿀-설정) / [8. 트러블슈팅](#8-트러블슈팅)              |

---

## 1. 화면 요소

```text
+------------------------------------------------------------------+
| Top Bar: 메뉴(File Edit Render ...) | 작업 공간 탭 | 장면·뷰 레이어 |
+---------------------------------------------+--------------------+
|                                                           | Outliner         |
|                                                           | (장면 객체 목록) |
| 3D Viewport                        +--------------------+ |                  |
| (주 작업 영역)                                            | Properties       |
|                                                           | (선택 대상 속성) |
+---------------------------------------------+                    |
| Timeline (Dope Sheet) |  |
+---------------------------------------------+--------------------+
| Status Bar: 마우스·키 안내, 장면 통계, 경고 |
+------------------------------------------------------------------+
```

- 기본 장면에는 Camera, Cube, Light 세 객체가 있고 해상도 1920×1080, 24fps, 프레임 1~250입니다.
- 편집기마다 머리줄(Header), 왼쪽 도구 모음(Toolbar, `T`), 오른쪽 사이드바(Sidebar, `N`)가 있습니다.
- 상태 표시줄 왼쪽은 지금 누를 수 있는 마우스·키를 보여 줍니다. 처음에는 이 안내를 보며 익히면 빠릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 작업 공간

작업 공간은 작업 목적에 맞춰 편집기 배치와 모드를 미리 정해 둔 탭입니다. 탭을 바꿔도 장면은 같습니다.

| 작업 공간      | 시작 모드     | 주요 편집기                                          | 용도                |
|----------------|---------------|------------------------------------------------------|---------------------|
| Layout         | Object        | 3D Viewport, Outliner, Properties, Dope Sheet        | 배치·전체 작업      |
| Modeling       | Edit          | 3D Viewport, Outliner, Properties                    | 메시 편집           |
| Sculpting      | Sculpt        | 3D Viewport, Outliner, Properties                    | 조각                |
| UV Editing     | Edit          | UV/Image Editor, 3D Viewport                         | UV 펼치기           |
| Texture Paint  | Texture Paint | UV/Image Editor, 3D Viewport                         | 텍스처 칠하기       |
| Shading        | Object        | Node Editor, File Browser, Image Editor, 3D Viewport | 재질·조명 확인      |
| Animation      | Pose          | 3D Viewport 2개, Dope Sheet                          | 키프레임 애니메이션 |
| Rendering      | Object        | Image Editor, Dope Sheet                             | 렌더 결과 확인      |
| Compositing    | Object        | Node Editor, Image Editor, Dope Sheet                | 렌더 후 합성        |
| Geometry Nodes | Object        | Node Editor, 3D Viewport, Spreadsheet                | 절차적 모델링       |
| Scripting      | Object        | Text Editor, Python Console, Info, 3D Viewport       | Python 스크립트     |

- 모든 작업 공간에 Properties가 있고, 대부분 Outliner가 있습니다.
- 탭 오른쪽 `+`로 작업 공간을 추가하고, 탭을 두 번 눌러 이름을 바꿉니다. 바꾼 배치는 `.blend` 파일에 저장됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 편집기

영역 왼쪽 위의 편집기 종류 버튼으로 아무 영역이나 다른 편집기로 바꿀 수 있습니다. 5.3.0의 편집기 종류는 다음과 같습니다.

| 분류       | 편집기                                                                         |
|------------|--------------------------------------------------------------------------------|
| 일반       | 3D Viewport, UV/Image Editor, Node Editor, Video Sequencer, Movie Clip Editor  |
| 애니메이션 | Dope Sheet, Graph Editor, Nonlinear Animation                                  |
| 스크립트   | Text Editor, Python Console, Info                                              |
| 데이터     | Outliner, Properties, File Browser, Spreadsheet, Preferences, Project Settings |

- Node Editor 하나에서 셰이더·지오메트리 노드·합성·텍스처 노드를 바꿔 가며 씁니다.
- Properties 편집기의 세로 탭은 선택 대상에 따라 바뀝니다. 자주 쓰는 탭은 Render, Output, Scene, World, Object, Modifiers, Material입니다.
- Info 편집기는 조작할 때마다 실행된 Python 명령을 기록합니다. 스크립트로 옮길 때 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 모드

같은 객체를 어떤 단위로 다룰지 정하는 상태입니다. 3D 뷰포트 머리줄 왼쪽 목록에서 고르고, Object ↔ Edit 전환은 `Tab`으로 합니다.

| 모드          | 다루는 단위         | 대표 작업                        |
|---------------|---------------------|----------------------------------|
| Object        | 객체 전체           | 이동·회전·크기, 모디파이어, 배치 |
| Edit          | 정점·모서리·면      | 돌출, 루프 컷, 베벨              |
| Sculpt        | 표면                | 브러시로 조각                    |
| Vertex Paint  | 정점 색             | 정점에 색 칠하기                 |
| Weight Paint  | 정점 가중치         | 뼈대 영향 범위 칠하기            |
| Texture Paint | 이미지 텍스처       | 모델 위에 직접 칠하기            |
| Pose          | 아마추어(뼈대)의 뼈 | 자세 잡기, 키프레임              |

- 모드는 객체 종류에 따라 다릅니다. 카메라·조명은 Object 모드만, 아마추어는 Edit·Pose 모드가 있습니다.
- Edit 모드에서 한 일은 Object 모드로 돌아갈 때 메시 데이터에 반영됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 3D 뷰포트

### 5.1 시점 이동

| 동작           | 마우스                        | 키보드·숫자 패드                      |
|----------------|-------------------------------|---------------------------------------|
| 회전           | 가운데 버튼 끌기              | 숫자 패드 2·4·6·8                     |
| 이동(Pan)      | `Shift` + 가운데 버튼 끌기    | `Ctrl` + 숫자 패드 2·4·6·8            |
| 확대·축소      | 휠, `Ctrl` + 가운데 버튼 끌기 | 숫자 패드 `+`·`-`, `Ctrl+=`·`Ctrl+-`  |
| 정면·옆·위     | -                             | 숫자 패드 1·3·7, `Ctrl`과 함께 반대쪽 |
| 반대편 보기    | -                             | 숫자 패드 9                           |
| 원근 ↔ 직교    | -                             | 숫자 패드 5                           |
| 카메라 시점    | -                             | 숫자 패드 0                           |
| 선택 대상 맞춤 | -                             | 숫자 패드 `.` (View Selected)         |
| 전체 맞춤      | -                             | `Home`                                |
| 시점 원형 메뉴 | -                             | 그레이브 키(숫자 1 왼쪽)              |

- 숫자 패드가 없으면 `Preferences > Input > Emulate Numpad`를 켜서 위쪽 숫자 키를 숫자 패드처럼 씁니다(매뉴얼 기준, 시험하지 않음). 시점 원형 메뉴(그레이브 키)를 쓰는 방법도 있습니다.
- 뷰포트 오른쪽 위의 축 위젯(Navigation Gizmo)을 눌러도 시점이 바뀝니다.

### 5.2 표시 방식 (Shading)

| 방식      | 보이는 것                             | 쓰는 때        |
|-----------|---------------------------------------|----------------|
| Wireframe | 모서리만                              | 겹친 구조 확인 |
| Solid     | 단색 면, 기본값                       | 모델링         |
| Material  | 재질과 미리 보기 조명(EEVEE)          | 재질 확인      |
| Rendered  | 장면 조명과 지정 엔진으로 실시간 렌더 | 최종 모습 확인 |

- `Z`로 원형 메뉴, `Alt+Z`로 엑스레이(X-Ray, 뒤쪽 면까지 선택)를 켭니다.
- 오버레이(Overlays)는 격자·축·법선 표시를, 기즈모(Gizmos)는 이동 손잡이 표시를 켜고 끕니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 화면 나누기

- 영역 모서리에서 안쪽으로 끌면 둘로 나뉩니다. 경계선에서 오른쪽 클릭 > `Join Areas`로 합칩니다.
- `Ctrl+Space`는 마우스가 있는 영역을 최대화했다가 되돌립니다.
- 영역 경계선을 끌어 크기를 바꿉니다. 바꾼 배치는 작업 공간과 함께 `.blend` 파일에 저장됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 처음 바꿀 설정

`Edit > Preferences`에서 바꾸고, 왼쪽 아래 메뉴의 `Save Preferences`로 저장합니다(자동 저장이 켜져 있으면 바로 저장됨).

| 위치                    | 항목                   | 초기값(5.3.0) | 권장                                  |
|-------------------------|------------------------|---------------|---------------------------------------|
| Interface               | Resolution Scale       | 1.0           | 고해상도 모니터면 1.25~1.5            |
| Interface > Translation | Language               | 시스템 기본   | 영문 유지(자료·검색이 영문 중심)      |
| Input                   | Emulate Numpad         | 끔            | 숫자 패드 없는 키보드면 켬            |
| Input                   | Emulate 3 Button Mouse | 끔            | 노트북 터치패드면 켬(`Alt`+왼쪽 클릭) |
| System                  | Cycles Render Devices  | 없음          | GPU 고르기                            |
| System                  | Undo Steps             | 32            | 메모리가 넉넉하면 늘림                |
| Save & Load             | Auto Save              | 켬, 2분       | 그대로                                |
| Save & Load             | Save Versions          | 1             | 2~3 (`.blend1`, `.blend2` 백업)       |

- 한국어 화면을 쓰면 메뉴 이름이 튜토리얼·검색 결과와 달라 찾기 어렵습니다. 처음에는 영문 화면을 권장합니다.
- 선택 마우스(왼쪽·오른쪽)는 `Input > Keymap`에서 바꿉니다. 초기값은 왼쪽 클릭 선택입니다. 바꾸면 단축키 일부가 달라집니다([단축키](./blender_shortcuts.md) 참고).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                               | 원인                               | 해결                                                  |
|------------------------------------|------------------------------------|-------------------------------------------------------|
| 도구 모음·사이드바가 사라짐        | `T`·`N`을 눌러 숨김                | 뷰포트에서 `T`·`N`, 또는 머리줄 `View` 메뉴           |
| 화면 배치가 엉망이 됨              | 영역을 잘못 나누거나 합침          | 작업 공간 탭을 새로 추가하거나 `File > New > General` |
| 객체가 안 보임                     | 숨김(`H`) 또는 로컬 뷰(`/`)        | `Alt+H`로 모두 보이기, `/`로 로컬 뷰 해제             |
| 확대해도 객체 안으로 들어가지 않음 | 시점 회전 중심이 멀리 있음         | 객체 선택 뒤 숫자 패드 `.`로 중심 맞춤                |
| Edit 모드로 안 바뀜                | 메시가 아닌 객체(카메라·조명) 선택 | 메시 객체를 선택하고 `Tab`                            |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 설치](./blender_install.md) — 판 고르기, 설정 폴더
- [Blender 단축키](./blender_shortcuts.md) — 초기 설정 기준 단축키

---

## 참고 자료

- Blender Manual: [User Interface](https://docs.blender.org/manual/en/latest/interface/index.html) · [Workspaces](https://docs.blender.org/manual/en/latest/interface/window_system/workspaces.html) · [Editors](https://docs.blender.org/manual/en/latest/editors/index.html) — ★★★☆☆
- Blender Manual: [Preferences](https://docs.blender.org/manual/en/latest/editors/preferences/index.html) — ★★★☆☆
- PyPI: [bpy](https://pypi.org/project/bpy/) — 5.3.0 컨테이너에서 기본 장면 확인 — ★★★☆☆

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
