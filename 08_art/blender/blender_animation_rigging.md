# Blender 애니메이션과 리깅
<!-- reference: _reference/blender_official_notes.md -->

애니메이션은 시간(프레임)에 따라 값이 바뀌게 하는 작업이고, 리깅(Rigging)은 모델을 뼈대(Armature)로 움직일 수 있게 준비하는 작업입니다. 이 문서는 키프레임 → 보간과 그래프 편집기 → 액션·NLA → 뼈대 만들기 → 스키닝(가중치) → Pose 모드와 IK 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 위치 키프레임 2개를 넣어 Bezier·Linear 보간 값과 Cycles F-Modifier를 확인하고, 뼈 2개짜리 아마추어를 원기둥에 자동 가중치로 연결한 뒤 위쪽 뼈를 90도 돌려 변형 결과를 확인. 그래프 편집기·타임라인 화면 조작과 재생은 실행하지 않았음

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 키프레임](#1-키프레임) / [2. 보간과 그래프 편집기](#2-보간과-그래프-편집기) / [3. 액션과 NLA](#3-액션과-nla) |
| [4. 뼈대 만들기](#4-뼈대-만들기) / [5. 스키닝](#5-스키닝) / [6. Pose 모드와 IK](#6-pose-모드와-ik)               |
| [7. 예제: 팔 굽히기](#7-예제-팔-굽히기) / [8. 트러블슈팅](#8-트러블슈팅)                                         |

---

## 1. 키프레임

키프레임(Keyframe)은 특정 프레임에서의 값입니다. 키프레임 사이의 값은 Blender가 계산(보간)합니다.

| 키                | 동작                                        |
|-------------------|---------------------------------------------|
| `I`               | 키프레임 넣기 (3D 뷰포트, Object·Pose 모드) |
| `K`               | 넣을 속성 고르는 메뉴(Location·Rotation 등) |
| `Alt+I`           | 키프레임 지우기                             |
| 속성 위에서 `I`   | 그 속성 하나에만 키프레임                   |
| `Space`           | 재생·정지                                   |
| `←` `→` / `↑` `↓` | 한 프레임 / 이전·다음 키프레임              |

- 키프레임이 있는 속성은 Properties에서 노란색(현재 프레임에 키 있음)·초록색(애니메이션 있음)으로 칠해집니다.
- 자동 키(Auto Keying, 타임라인의 원 버튼)는 초기값이 꺼짐입니다. 켜면 값을 바꿀 때마다 키가 들어가므로 실수로 키가 쌓이지 않게 주의합니다.
- 시험: 정육면체 위치를 1프레임 x=0, 25프레임 x=4로 넣자 X·Y·Z 위치 곡선 3개가 생겼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 보간과 그래프 편집기

### 2.1 보간 방식

| 방식     | 동작                              | 시험(1→25프레임, 0→4)의 7·13·19프레임 값 |
|----------|-----------------------------------|------------------------------------------|
| Bezier   | 천천히 출발해 천천히 멈춤(초기값) | 0.625 / 2.0 / 3.375                      |
| Linear   | 일정한 속도                       | 1.0 / 2.0 / 3.0                          |
| Constant | 다음 키까지 값 유지(뚝 끊김)      | -                                        |

- 그 밖에 Sine·Quad·Cubic·Quart·Quint·Expo·Circ(가감속 곡선), Back·Bounce·Elastic(튀는 효과)이 있습니다.
- 새 키프레임의 보간 초기값은 Bezier, 핸들 초기값은 Auto Clamped입니다(Preferences > Animation에서 바꿈).
- 키프레임 종류는 Keyframe(초기값), Breakdown, Moving Hold, Extreme, Jitter, Generated로 표시만 다르고 계산은 같습니다.

### 2.2 그래프 편집기 (Graph Editor)

값의 변화를 곡선으로 보고 고칩니다.

| 키            | 동작                        |
|---------------|-----------------------------|
| `T`           | 보간 방식 메뉴              |
| `V`           | 핸들 종류 메뉴              |
| `Ctrl+E`      | 가감속(Easing) 메뉴         |
| `Home`        | 곡선 전체 보기              |
| 숫자 패드 `.` | 선택 키에 맞춤              |
| `I`           | 키프레임 넣기               |
| `Alt+S`       | 곡선 다듬기(Smoothing) 메뉴 |

- F-Modifier(곡선 수정자)로 곡선을 반복·잡음 처리합니다. 시험: Linear 곡선(1→25프레임, 0→4)에 Cycles F-Modifier를 붙이자 26프레임에서 0.167로 처음부터 다시 시작했고, 37프레임 2.0, 49프레임 4.0으로 24프레임마다 반복했습니다.
- Dope Sheet는 키프레임을 점으로만 보여 줘서 타이밍(언제)을 옮길 때 편합니다. `T`로 보간을 바꾸는 것은 같습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 액션과 NLA

- 키프레임 묶음은 액션(Action)에 저장됩니다. 시험에서 `CubeAction`이 자동으로 생겼습니다.
- 5.x의 액션은 층(Layer)과 슬롯(Slot)을 가진 구조입니다. 한 액션 안에 여러 객체용 슬롯을 둘 수 있고, 시험에서는 슬롯 `OBCube`가 생겼습니다. 스크립트에서 곡선을 찾을 때는 `action.layers[...].strips[...].channelbags[...].fcurves` 경로를 씁니다.
- NLA(Nonlinear Animation) 편집기는 액션을 클립처럼 배치합니다. 걷기·뛰기 같은 동작을 따로 만들어 이어 붙이거나 섞을 때 씁니다.
- 액션 이름 옆 방패(Fake User)를 켜야 쓰지 않는 액션이 저장 때 지워지지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 뼈대 만들기

`Shift+A` > `Armature`로 뼈 하나짜리 아마추어를 추가하고, Edit 모드(`Tab`)에서 뼈를 늘립니다.

| 키 (아마추어 Edit 모드) | 동작                                  |
|-------------------------|---------------------------------------|
| `E`                     | 선택한 뼈 끝에서 새 뼈를 돌출(이어짐) |
| `Shift+D`               | 뼈 복제                               |
| `Ctrl+P`                | 부모 뼈 지정(Connected / Keep Offset) |
| `X`                     | 삭제                                  |
| 오른쪽 클릭             | 문맥 메뉴(Subdivide, Symmetrize 등)   |

- 뼈는 머리(Head)·꼬리(Tail)·뼈 회전(Roll)을 가집니다. 이어진(Connected) 뼈는 부모의 꼬리에 머리가 붙어 따로 움직이지 않습니다.
- 뼈 이름에 `.L`·`.R`을 붙이면 좌우 대칭 기능(Symmetrize, 포즈 대칭 붙여넣기)이 동작합니다.
- 시험: 아마추어 표시 방식 초기값은 Octahedral이고, 뼈 모음(Bone Collection)은 `Bones` 하나가 있었습니다. `Lower`(0→2m) 위에 이어진 `Upper`(2→4m)를 만들었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 스키닝

스키닝(Skinning)은 메시 정점이 어느 뼈를 얼마나 따라갈지(가중치) 정하는 작업입니다.

1. Object 모드에서 메시를 먼저 선택하고, `Shift`를 누른 채 아마추어를 마지막에 선택합니다.
2. `Ctrl+P` > `With Automatic Weights`.

결과:

- 메시에 Armature 모디파이어가 붙고, 뼈 이름과 같은 정점 그룹(Vertex Group)이 생깁니다.
- 시험: 원기둥(정점 1152)을 `Lower`·`Upper` 아마추어에 자동 가중치로 연결하자 정점 그룹 `Lower`·`Upper`와 Armature 모디파이어가 생겼고, 맨 위 정점은 `Upper` 가중치 1.0이었습니다.

| 부모 지정 방식         | 동작                                         |
|------------------------|----------------------------------------------|
| With Automatic Weights | 뼈와의 거리로 가중치 자동 계산(가장 많이 씀) |
| With Empty Groups      | 정점 그룹만 만들고 가중치는 직접 칠함        |
| With Envelope Weights  | 뼈 주변 범위(Envelope)로 가중치 계산         |
| Armature Deform        | 모디파이어만 붙임                            |
| Object / Bone          | 메시 전체가 한 뼈를 따라감(딱딱한 물체)      |

- 가중치는 Weight Paint 모드에서 칠해 고칩니다. 빨강 = 1.0(완전히 따라감), 파랑 = 0.
- 자동 가중치가 실패하면("Bone Heat Weighting: failed to find solution for one or more bones") 메시에 겹친 정점·떨어진 조각이 있는지 확인합니다([모델링](./blender_modeling.md) 4절).

[⬆ 목차로 돌아가기](#목차)

---

## 6. Pose 모드와 IK

아마추어를 선택하고 3D 뷰포트 머리줄의 모드 목록에서 Pose Mode를 고릅니다. 뼈를 `R`로 돌리면 메시가 따라 움직입니다.

| 키 (Pose 모드)              | 동작                                    |
|-----------------------------|-----------------------------------------|
| `R` / `G` / `S`             | 뼈 회전 / 이동 / 크기                   |
| `Alt+R` / `Alt+G` / `Alt+S` | 회전 / 이동 / 크기 초기화               |
| `I`                         | 키프레임 넣기                           |
| `[` / `]`                   | 부모 / 자식 뼈 선택                     |
| `Shift+I`                   | IK 추가                                 |
| `Ctrl+Alt+I`                | IK 지우기                               |
| `Ctrl+A`                    | 포즈 적용 메뉴(지금 포즈를 기본 자세로) |

- 포즈 뼈의 회전 방식 초기값은 Quaternion입니다. 그래프 편집기에서 각도로 보고 싶으면 뼈 속성에서 XYZ Euler로 바꿉니다(짐벌 잠김 주의).
- 시험: 위쪽 뼈를 X축으로 90도 돌리자 원기둥 맨 위 점이 (y 0.3, z 4.0)에서 (y -0.48, z 2.31)로 옮겨졌습니다. 가중치가 섞이는 관절 부분은 휘어지고 끝부분은 뼈를 따라 돌았습니다.
- IK(Inverse Kinematics)는 끝 뼈를 목표로 끌면 부모 뼈들이 알아서 굽는 방식입니다. 팔·다리에 씁니다. IK 제약의 Chain Length로 몇 개 뼈까지 영향을 줄지 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 예제: 팔 굽히기

1. 원기둥을 세워 두고 Edit 모드에서 세로로 여러 번 루프 컷을 넣습니다(관절이 휘려면 면이 필요).
2. 아마추어를 추가하고 Edit 모드에서 `E`로 뼈를 하나 더 돌출해 위팔·아래팔 두 뼈를 만듭니다.
3. Object 모드에서 원기둥 → 아마추어 순으로 선택하고 `Ctrl+P` > With Automatic Weights.
4. 아마추어를 Pose 모드로 바꾸고 아래팔 뼈를 `R`로 돌립니다.
5. 1프레임에서 펴진 자세로 `I`, 20프레임에서 굽힌 자세로 `I`. `Space`로 재생합니다.

- 1~4단계는 6절 시험(원기둥을 나눠 정점 1152개, 뼈 2개, 자동 가중치, 90도 회전)과 같은 구성입니다. 5단계 재생은 화면에서 실행하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                               | 원인                                 | 해결                                                     |
|------------------------------------|--------------------------------------|----------------------------------------------------------|
| 뼈를 돌려도 메시가 안 움직임       | 부모 지정 안 됨, 모디파이어 꺼짐     | Armature 모디파이어·대상 확인, `Ctrl+P` 다시             |
| 관절이 접히며 찌그러짐             | 관절 부근 면 부족                    | 루프 컷 추가, 가중치 다듬기                              |
| 메시 일부가 엉뚱한 뼈를 따라감     | 자동 가중치 오류                     | Weight Paint로 수정                                      |
| "Bone Heat Weighting: failed"      | 겹친 정점·떨어진 조각·아주 작은 크기 | Merge by Distance, 크기 적용                             |
| 키프레임을 넣었는데 저장 후 사라짐 | 액션 사용자 0                        | Fake User 켜기                                           |
| 동작이 계속 자동으로 키가 들어감   | Auto Keying 켜짐                     | 타임라인의 원 버튼 끄기                                  |
| 회전 그래프가 튐                   | Euler 각도 넘김(짐벌)                | Quaternion 사용, 또는 그래프 편집기 Discontinuity Filter |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 단축키](./blender_shortcuts.md) — 애니메이션 재생·프레임 이동 키
- [Blender 파일 형식](./blender_file_formats.md) — 애니메이션을 다른 프로그램으로 내보내기

---

## 참고 자료

- Blender Manual: [Animation](https://docs.blender.org/manual/en/latest/animation/index.html) · [Graph Editor](https://docs.blender.org/manual/en/latest/editors/graph_editor/index.html) · [NLA](https://docs.blender.org/manual/en/latest/editors/nla/index.html) — ★★★☆☆
- Blender Manual: [Rigging > Armatures](https://docs.blender.org/manual/en/latest/animation/armatures/index.html) · [Skinning](https://docs.blender.org/manual/en/latest/animation/armatures/skinning/index.html) — ★★★☆☆

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
