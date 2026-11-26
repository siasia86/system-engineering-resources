# Blender 지오메트리 노드
<!-- reference: _reference/blender_official_notes.md -->

지오메트리 노드(Geometry Nodes)는 노드를 연결해 모양을 절차적으로 만들거나 바꾸는 기능입니다. 결과는 모디파이어로 붙으므로 원본을 바꾸지 않고, 입력값만 바꿔 여러 변형을 만들 수 있습니다. 이 문서는 구조 → 첫 노드 트리 → 필드 → 인스턴스 → 모디파이어 입력 → 존(Zone) → 스크립트 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 평면 위에 작은 구를 흩뿌리는 노드 트리와 위치를 사인파로 바꾸는 노드 트리를 Python으로 만들어 평가 결과(정점 수, 높이 범위)를 확인하고, 모디파이어 입력값 변경과 존 노드 생성을 확인. Node Editor 화면 조작은 실행하지 않았음

## 목차

| 섹션                                                                                                                   |
|------------------------------------------------------------------------------------------------------------------------|
| [1. 구조](#1-구조) / [2. 첫 노드 트리](#2-첫-노드-트리) / [3. 필드](#3-필드)                                           |
| [4. 인스턴스](#4-인스턴스) / [5. 모디파이어 입력](#5-모디파이어-입력) / [6. 존](#6-존)                                 |
| [7. 기본 제공 에셋](#7-기본-제공-에셋) / [8. Python으로 만들기](#8-python으로-만들기) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 구조

```text
객체의 메시 ──▶ [Group Input] ──▶ 노드들 ──▶ [Group Output] ──▶ 화면·렌더 결과
                     │
                     └─ 모디파이어 패널에 보이는 입력값(숫자·객체·재질 등)
```

- 노드 트리는 Geometry Nodes 모디파이어에 붙습니다. 같은 노드 트리를 여러 객체가 함께 쓸 수 있습니다.
- Geometry Nodes 작업 공간을 열고 Node Editor 머리줄의 `New`를 누르면 모디파이어와 기본 노드 두 개(Group Input → Group Output)가 만들어집니다.
- 5.3.0에는 지오메트리 노드 종류가 292개 있습니다(`bpy.types`의 `GeometryNode` 이름 기준). 노드 추가는 `Shift+A`입니다.
- 오른쪽의 Spreadsheet 편집기는 평가된 정점·면·속성 값을 표로 보여 줍니다. 결과를 확인할 때 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 첫 노드 트리

평면 위에 작은 구를 흩뿌리는 트리입니다.

```text
[Group Input]
   ├─ Geometry ─────────────────────────────────────────────┐
   │                                                        ▼
   ├─ Geometry ─▶ [Distribute Points on Faces] ─Points─▶ [Instance on Points] ─▶ [Realize Instances] ─▶ [Join Geometry] ─▶ [Group Output]
   └─ Density ──▶      (Density 입력)            ▲
                                                 │ Instance
                              [Ico Sphere] ──Mesh┘ (Radius 0.05)
```

| 노드                       | 하는 일                                      |
|----------------------------|----------------------------------------------|
| Distribute Points on Faces | 면 위에 점을 뿌림. 초기값 Random, Seed 0     |
| Ico Sphere                 | 작은 구 메시. Subdivisions 초기값 1(정점 12) |
| Instance on Points         | 점마다 구를 인스턴스로 배치                  |
| Realize Instances          | 인스턴스를 실제 메시로 바꿈                  |
| Join Geometry              | 원래 평면과 합침                             |

- 시험: 4m×4m 평면(16m²)에 Density 10을 주자 점 약 160개가 생겨 결과 정점이 1924개(구 12 × 160 + 평면 4), 20으로 올리자 3844개로 두 배가 되었습니다.
- Join Geometry로 원본을 합치지 않으면 결과에서 평면이 사라집니다. Group Input의 Geometry를 그대로 Group Output에 함께 넘겨야 원본이 남습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 필드

필드(Field)는 "정점마다 다른 값"을 나타내는 함수입니다. 노드 소켓 모양으로 구분합니다.

| 소켓 모양      | 뜻                                     |
|----------------|----------------------------------------|
| 원             | 값 하나(단일 값)                       |
| 마름모         | 필드(요소마다 계산)                    |
| 점 있는 마름모 | 지금은 단일 값이지만 필드가 될 수 있음 |

예: 격자 정점을 x 좌표에 따라 위아래로 출렁이게 하기.

```text
[Position] ─▶ [Separate XYZ] ─X─▶ [Math: Sine] ─▶ [Combine XYZ] ─Z─▶ [Set Position] (Offset)
```

- 시험: 2m 격자(10×10)에 이 트리를 붙이자 정점 높이가 -0.841 ~ 0.841(= sin(±1))로 바뀌었습니다.
- Position, Normal, Index 같은 입력 노드는 필드입니다. Set Position 노드가 정점마다 계산합니다.
- 필드 소켓은 노드 위로 마우스를 올리면 값의 범위를 보여 줍니다(화면 기능, 시험하지 않음).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 인스턴스

- 인스턴스(Instance)는 같은 메시를 여러 위치에 "참조"로 놓는 것입니다. 메모리를 거의 쓰지 않아 수만 개도 가볍습니다.
- Realize Instances를 쓰면 실제 메시로 바뀌어 각각 편집할 수 있지만 무거워집니다. 모양을 더 바꿀 필요가 없으면 인스턴스로 둡니다.
- 컬렉션을 인스턴스로 쓰려면 `Collection Info` 노드를 Instance on Points의 Instance에 연결하고 `Pick Instance`를 켜면 컬렉션 안 객체 중 무작위로 고릅니다(매뉴얼 기준, 시험하지 않음).
- 회전·크기를 무작위로 하려면 `Random Value` 노드를 Instance on Points의 Rotation·Scale에 연결합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 모디파이어 입력

Group Input에 소켓을 추가하면 모디파이어 패널에 입력값이 생깁니다. 같은 노드 트리를 객체마다 다른 값으로 씁니다.

- Node Editor 사이드바(`N`) > Group 탭에서 입력 소켓을 추가·이름 변경·기본값 지정합니다.
- 입력 옆 버튼으로 값을 속성(Attribute) 이름으로 바꿔, 정점 그룹이나 칠한 값으로 밀도 등을 조절할 수 있습니다.

Python에서 값 넣기 (5.3에서 바뀜):

```python
import bpy

mod = bpy.context.object.modifiers["GeometryNodes"]
ident = "Socket_2"                      # 입력 소켓 식별자 (node_group.interface에서 확인)
getattr(mod.properties.inputs, ident).value = 20.0
```

- 시험: 이전 판에서 쓰던 `mod["Socket_2"] = 20.0` 방식은 5.3.0에서 "id properties not supported for this type" 오류가 났습니다. `mod.properties.inputs.<식별자>.value`로 넣어야 했습니다.
- 식별자(`Socket_0`, `Socket_2` 등)는 소켓 이름이 아니라 생성 순서로 정해집니다. `node_group.interface.items_tree`에서 이름과 `identifier`를 대조합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 존

존(Zone)은 입력·출력 노드 한 쌍으로 둘러싼 영역입니다. 안쪽 노드가 특별한 방식으로 실행됩니다.

| 존               | 동작                               | 쓰는 곳               |
|------------------|------------------------------------|-----------------------|
| Simulation       | 이전 프레임 결과를 이어 받아 계산  | 입자·성장·물리 흉내   |
| Repeat           | 정한 횟수만큼 반복                 | 반복 세분·프랙털      |
| For Each Element | 요소(면·점·인스턴스)마다 따로 실행 | 조각마다 다른 처리    |
| Closure          | 노드 묶음을 값처럼 넘김            | 고급 재사용(5.x 기능) |

- 시험: 5.3.0에서 Simulation·Repeat·For Each Element·Closure 입력 노드를 모두 만들 수 있었습니다. 존 안 동작은 시험하지 않았습니다.
- Simulation 결과는 모디파이어 패널의 Bake로 디스크에 저장합니다. 베이크하지 않으면 1프레임부터 차례로 재생해야 결과가 맞습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 기본 제공 에셋

5.3에는 바로 쓸 수 있는 노드 그룹이 들어 있습니다(`geometry_nodes_essentials.blend`, 33개). 모디파이어 추가 메뉴에 함께 나옵니다.

| 에셋               | 메뉴 위치 | 하는 일                        |
|--------------------|-----------|--------------------------------|
| Array              | Generate  | 배열 복제(5.3 메뉴 기본 Array) |
| Curve to Tube      | Generate  | 곡선을 관으로                  |
| Scatter on Surface | Generate  | 표면에 흩뿌리기                |
| Smooth by Angle    | Normals   | 각도 기준 부드럽게 보이기      |

- 이 에셋들도 노드 그룹이라 Node Editor에서 열어 내부를 보고 복사해 고칠 수 있습니다. 공부할 때 좋은 예제입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Python으로 만들기

2절 트리를 스크립트로 만드는 핵심 부분입니다(시험에 쓴 코드를 줄임).

```python
import bpy

ng = bpy.data.node_groups.new("Scatter", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
dens = ng.interface.new_socket("Density", in_out="INPUT", socket_type="NodeSocketFloat")
dens.default_value = 10.0

n, link = ng.nodes, ng.links.new
gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
dist = n.new("GeometryNodeDistributePointsOnFaces")
ico = n.new("GeometryNodeMeshIcoSphere")
ico.inputs["Radius"].default_value = 0.05
inst = n.new("GeometryNodeInstanceOnPoints")
join = n.new("GeometryNodeJoinGeometry")

link(gi.outputs["Geometry"], dist.inputs["Mesh"])
link(gi.outputs["Density"], dist.inputs["Density"])
link(dist.outputs["Points"], inst.inputs["Points"])
link(ico.outputs["Mesh"], inst.inputs["Instance"])
link(gi.outputs["Geometry"], join.inputs["Geometry"])
link(inst.outputs["Instances"], join.inputs["Geometry"])
link(join.outputs["Geometry"], go.inputs["Geometry"])

obj = bpy.context.object
obj.modifiers.new("GN", "NODES").node_group = ng
```

- 노드는 만들어도 화면 위치가 겹쳐 보입니다. 사람이 볼 트리면 `node.location`으로 자리를 잡아 줍니다.
- 평가 결과는 `obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()`로 읽습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                  | 원인                               | 해결                                                 |
|---------------------------------------|------------------------------------|------------------------------------------------------|
| 노드를 붙였더니 원래 모양이 사라짐    | 원본 Geometry를 출력에 넘기지 않음 | Join Geometry로 원본 합치기                          |
| 연결선이 빨갛게 표시                  | 필드를 단일 값만 받는 소켓에 연결  | 소켓 모양 확인, 필드를 받는 노드로 바꾸기            |
| 점·인스턴스가 하나도 안 생김          | Density 0, 면이 없는 메시          | Density·입력 메시 확인                               |
| 매우 느려짐                           | 인스턴스를 너무 일찍 Realize       | 인스턴스로 유지, 마지막에만 Realize                  |
| 스크립트에서 `mod["Socket_x"]` 오류   | 5.3에서 입력 접근 방식이 바뀜      | `mod.properties.inputs.Socket_x.value`               |
| 시뮬레이션이 프레임을 건너뛰면 틀어짐 | 베이크 안 됨                       | 모디파이어 패널 Bake                                 |
| 내보낸 파일에 결과가 없음             | 내보내기에서 모디파이어 적용 꺼짐  | [파일 형식](./blender_file_formats.md) 2절 옵션 확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 모디파이어](./blender_modifiers.md) — 스택 순서, 노드 기반 Array
- [Blender 파일 형식](./blender_file_formats.md) — 결과를 내보낼 때 모디파이어 적용

---

## 참고 자료

- Blender Manual: [Geometry Nodes](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html) · [Fields](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/fields.html) · [Instances](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/instances.html) — ★★★☆☆
- Blender Python API: [NodesModifier](https://docs.blender.org/api/current/bpy.types.NodesModifier.html) — 5.3 입력 접근 확인 — ★★★☆☆

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
