# Blender Python 스크립트
<!-- reference: _reference/blender_official_notes.md -->

Blender는 내장 Python과 `bpy` 모듈로 거의 모든 작업을 자동화할 수 있습니다. 이 문서는 `bpy` 구조 → 스크립트 실행 방법 → 데이터 API와 연산자 → 문맥(context) → 연산자·패널 만들기 → 속성과 이벤트 → 외부 패키지 순서로 정리합니다.

- 기준 판: Blender 5.3.0, 내장 Python 3.13.13 (2026-11-26 확인)
- 예제 시험: 2026-11-26, Blender 5.3.0 Linux판(공식 압축판, sha256 확인)을 컨테이너에서 화면 없이(`-b`) 실행해 이 문서의 코드, 데이터 API와 연산자 속도 비교, 문맥 오류와 `temp_override`, 연산자 등록, 핸들러, 종료 코드, 내장 pip를 확인. 화면(Scripting 작업 공간, 패널 표시)에서의 동작은 확인하지 않았음

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. bpy 구조](#1-bpy-구조) / [2. 스크립트 실행](#2-스크립트-실행) / [3. 데이터 API와 연산자](#3-데이터-api와-연산자) |
| [4. 문맥과 temp_override](#4-문맥과-temp_override) / [5. 연산자와 패널 만들기](#5-연산자와-패널-만들기)              |
| [6. 속성과 핸들러](#6-속성과-핸들러) / [7. 외부 패키지](#7-외부-패키지) / [8. 트러블슈팅](#8-트러블슈팅)             |

---

## 1. bpy 구조

| 모듈·객체     | 하는 일                                               | 예                                           |
|---------------|-------------------------------------------------------|----------------------------------------------|
| `bpy.data`    | 파일 안의 모든 데이터(객체, 메시, 재질, 이미지, 장면) | `bpy.data.objects["Cube"]`                   |
| `bpy.context` | 지금 상태(활성 객체, 선택, 장면, 모드, 편집기)        | `bpy.context.active_object`                  |
| `bpy.ops`     | 연산자. 메뉴·단축키로 하는 동작과 같음                | `bpy.ops.mesh.primitive_cube_add()`          |
| `bpy.types`   | 클래스 정의. 연산자·패널을 만들 때 상속               | `bpy.types.Operator`                         |
| `bpy.props`   | 사용자 속성 정의                                      | `bpy.props.IntProperty()`                    |
| `bpy.app`     | 판, 실행 상태, 핸들러                                 | `bpy.app.version_string`, `bpy.app.handlers` |
| `bmesh`       | 메시를 정점·모서리·면 단위로 편집                     | `bmesh.new()`                                |
| `mathutils`   | 벡터, 행렬, 회전                                      | `mathutils.Vector((1, 0, 0))`                |

- 화면에서 메뉴 위에 마우스를 올리면 해당 Python 명령이 툴팁에 보입니다(Preferences > Interface > Python Tooltips, 초기값 꺼짐).
- Scripting 작업 공간의 Info 편집기에는 방금 한 조작이 Python 명령으로 기록돼 스크립트의 출발점으로 쓸 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 스크립트 실행

| 방법           | 명령·위치                                    | 쓰임                    |
|----------------|----------------------------------------------|-------------------------|
| Text Editor    | Scripting 작업 공간에서 `Run Script`         | 작업 중 바로 실행       |
| Python Console | Scripting 작업 공간의 콘솔                   | 한 줄씩 시험, 자동 완성 |
| 명령줄 파일    | `blender -b file.blend -P script.py`         | 자동화, 서버            |
| 명령줄 식      | `blender -b --python-expr "import bpy; ..."` | 짧은 확인               |
| 애드온         | 설치 후 켬                                   | 반복해서 쓰는 도구      |

스크립트에 인수를 넘길 때는 `--` 뒤에 둡니다. Blender는 `--` 뒤를 읽지 않고 `sys.argv`에 그대로 남깁니다.

```bash
blender -b --factory-startup -P make_scene.py -- --name test
```

```python
# make_scene.py
import sys
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
print(argv)   # ['--name', 'test']
```

자동화에서는 예외가 났을 때 종료 코드를 꼭 지정합니다. 지정하지 않으면 스크립트가 실패해도 Blender는 0으로 끝납니다.

| 실행                                        | 스크립트에서 `ValueError` | 종료 코드 |
|---------------------------------------------|---------------------------|-----------|
| `blender -b -P err.py`                      | 오류 출력 뒤 계속         | 0         |
| `blender -b --python-exit-code 3 -P err.py` | 오류 출력 뒤 종료         | 3         |

- `--python-exit-code`는 `-P`보다 앞에 둡니다. 인수는 적은 순서대로 처리됩니다.
- `--factory-startup`을 주면 사용자 시작 파일과 설정을 읽지 않아, PC마다 결과가 달라지는 것을 막습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 데이터 API와 연산자

같은 일을 `bpy.data`로 직접 만들 수도 있고 `bpy.ops` 연산자로 할 수도 있습니다.

```python
import bpy

# 데이터 API: 메시와 객체를 직접 만들고 장면 컬렉션에 연결
me = bpy.data.meshes.new("tri")
me.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
ob = bpy.data.objects.new("tri", me)
bpy.context.collection.objects.link(ob)

# 연산자: 메뉴의 Add > Mesh > Cube와 같음
bpy.ops.mesh.primitive_cube_add(location=(3, 0, 0))

# 지우기
bpy.data.objects.remove(ob, do_unlink=True)
```

시험 결과(객체 200개 만들기):

| 방법       | 시간    |
|------------|---------|
| 데이터 API | 0.013초 |
| 연산자     | 0.629초 |

| 구분      | 데이터 API              | 연산자                                      |
|-----------|-------------------------|---------------------------------------------|
| 속도      | 빠름                    | 느림(호출마다 장면 갱신·Undo 기록)          |
| 문맥 필요 | 없음                    | 연산자에 따라 필요(4절)                     |
| 기능      | 데이터 구조를 직접 다룸 | 메뉴 기능을 그대로 씀(베벨, 불리언 적용 등) |
| 권장      | 많이 만들거나 고칠 때   | 같은 기능을 데이터 API로 하기 어려울 때     |

- 연산자는 `{'FINISHED'}`나 `{'CANCELLED'}`를 돌려줍니다.
- 파일을 저장할 때는 `bpy.ops.wm.save_as_mainfile(filepath="...")`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 문맥과 temp_override

연산자에는 실행 가능 조건(`poll`)이 있어, 필요한 편집기나 활성 객체가 없으면 실패합니다. 화면 없이 실행하면 3D 뷰가 없어 이런 오류가 자주 납니다.

```text
RuntimeError: Operator bpy.ops.view3d.snap_cursor_to_center.poll() failed, context is incorrect
```

필요한 문맥 값을 `temp_override`로 넘깁니다.

```python
import bpy
ob = bpy.data.objects["Cube"]
with bpy.context.temp_override(active_object=ob, selected_objects=[ob], object=ob):
    bpy.ops.object.modifier_add(type='BEVEL')
print([m.type for m in ob.modifiers])   # ['BEVEL']
```

- 3D 뷰 영역 자체가 필요한 연산자(`view3d.*`)는 화면 없는 실행에서 넘길 영역이 없습니다. 데이터 API로 바꿉니다. 예: 커서 위치는 `bpy.context.scene.cursor.location = (0, 0, 0)`.
- 모디파이어 추가처럼 데이터 API가 있는 작업은 처음부터 `ob.modifiers.new("Bevel", 'BEVEL')`로 쓰면 문맥 문제가 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 연산자와 패널 만들기

```python
import bpy

class SIMPLE_OT_hello(bpy.types.Operator):
    bl_idname = "simple.hello"          # bpy.ops.simple.hello 로 호출
    bl_label = "Hello"
    bl_options = {'REGISTER', 'UNDO'}   # 실행 뒤 조정 패널, Undo 지원

    count: bpy.props.IntProperty(default=2, min=1)

    def execute(self, context):
        for i in range(self.count):
            bpy.ops.mesh.primitive_uv_sphere_add(location=(0, i * 3, 5))
        self.report({'INFO'}, f"added {self.count}")
        return {'FINISHED'}

class SIMPLE_PT_panel(bpy.types.Panel):
    bl_label = "Simple"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'                # 3D 뷰 오른쪽 사이드바(N)
    bl_category = "Simple"               # 사이드바 탭 이름

    def draw(self, context):
        self.layout.operator("simple.hello")

bpy.utils.register_class(SIMPLE_OT_hello)
bpy.utils.register_class(SIMPLE_PT_panel)

bpy.ops.simple.hello(count=3)   # {'FINISHED'}, 구 3개 추가
```

| 규칙             | 내용                                                         |
|------------------|--------------------------------------------------------------|
| `bl_idname`      | `분류.이름` 소문자. 연산자 클래스 이름은 `분류_OT_이름`      |
| 패널 클래스 이름 | `분류_PT_이름`                                               |
| 속성 선언        | 클래스 본문에 `이름: bpy.props.XxxProperty(...)` (콜론 표기) |
| 등록·해제        | `bpy.utils.register_class` / `unregister_class`              |

- Text Editor에서 실행한 등록은 Blender를 다시 켜면 사라집니다. 계속 쓰려면 애드온으로 만듭니다([Blender 애드온](./blender_addons.md)).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 속성과 핸들러

```python
import bpy

# 장면 전체에 붙는 사용자 속성 (등록한 동안 유효)
bpy.types.Scene.my_note = bpy.props.StringProperty(default="hi")
print(bpy.context.scene.my_note)        # hi

# 데이터 하나에 붙는 사용자 속성 (파일에 저장됨)
ob = bpy.data.objects["Cube"]
ob["custom_id"] = 42
print(ob["custom_id"], ob.get("nope", "default"))   # 42 default

# 프레임이 바뀔 때마다 호출
def on_frame(scene, depsgraph=None):
    print("frame", scene.frame_current)
bpy.app.handlers.frame_change_post.append(on_frame)
for f in (1, 5, 9):
    bpy.context.scene.frame_set(f)      # frame 1, 5, 9
```

| 핸들러                     | 호출 시점           |
|----------------------------|---------------------|
| `frame_change_post`        | 프레임 변경 뒤      |
| `load_post`                | 파일을 연 뒤        |
| `save_pre`                 | 저장 직전           |
| `render_pre`·`render_post` | 렌더 앞뒤           |
| `depsgraph_update_post`    | 장면 데이터 갱신 뒤 |

- 시험한 것은 `frame_change_post`뿐입니다. 나머지는 `bpy.app.handlers` 목록 이름입니다.
- 핸들러 안에서 무거운 작업을 하면 화면 조작이 느려집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 외부 패키지

Blender는 시스템 Python이 아니라 함께 들어 있는 Python을 씁니다.

```bash
# 내장 Python 위치 (Linux 압축판)
blender -b --python-expr "import sys; print(sys.executable)"
# .../blender-5.3.0-linux-x64/5.3/python/bin/python3.13

P=/opt/blender-5.3.0-linux-x64/5.3/python/bin/python3.13
$P -m pip --version                      # pip 26.2.2 (내장)
$P -m pip install --target ./bl_modules <패키지>
```

```python
import sys
sys.path.append("/path/to/bl_modules")
import tomli_w
```

- Blender는 사용자 site-packages를 읽지 않습니다(시험 값 `sys.flags.no_user_site == 1`). `pip install --user`로 넣은 패키지는 보이지 않습니다.
- `PYTHONPATH` 같은 시스템 환경 변수도 기본으로 무시합니다. 쓰려면 `--python-use-system-env`를 줍니다.
- 설치 폴더에 직접 넣으면 Blender를 올릴 때 사라집니다. 애드온이 쓰는 패키지는 확장의 wheels 기능으로 함께 묶는 방법이 있습니다(이 문서에서는 미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                         | 원인                                 | 조치                                                 |
|--------------------------------------------------------------|--------------------------------------|------------------------------------------------------|
| `poll() failed, context is incorrect`                        | 연산자가 요구하는 편집기·객체가 없음 | `temp_override`로 넘기거나 데이터 API로 바꿈         |
| 스크립트가 실패했는데 CI가 성공으로 처리                     | `--python-exit-code` 없음            | `--python-exit-code 1`을 `-P` 앞에 둠                |
| 연산자로 많이 만들 때 매우 느림                              | 호출마다 장면 갱신·Undo 기록         | 데이터 API 사용                                      |
| `ModuleNotFoundError` (pip로 설치했는데)                     | 시스템 Python이나 사용자 site에 설치 | 내장 Python으로 `--target` 설치 뒤 `sys.path`에 추가 |
| 등록한 연산자가 다시 켜면 사라짐                             | Text Editor 실행은 그 세션에만 유효  | 애드온으로 만들어 설치                               |
| `KeyError: 'bpy_prop_collection[key]: key "Cube" not found'` | 이름이 다름(`Cube.001` 등)           | `bpy.data.objects.get("Cube")`로 없을 때 처리        |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 명령줄과 일괄 렌더](./blender_cli_batch_render.md) — `-b`·`-P`로 렌더 자동화
- [Blender 애드온](./blender_addons.md) — 만든 도구를 확장으로 배포
- [Blender 트러블슈팅](./blender_troubleshooting.md) — 실행·렌더 문제

---

## 참고 자료

- Blender Python API: [Quickstart](https://docs.blender.org/api/current/info_quickstart.html) · [Gotchas](https://docs.blender.org/api/current/info_gotcha.html) — ★★★☆☆
- Blender Python API: [bpy.app.handlers](https://docs.blender.org/api/current/bpy.app.handlers.html) · [Context.temp_override](https://docs.blender.org/api/current/bpy.types.Context.html) — ★★★☆☆
- Blender Manual: [Command Line Arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html) — ★★★☆☆

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
