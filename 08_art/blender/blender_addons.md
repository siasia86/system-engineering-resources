# Blender 애드온
<!-- reference: _reference/blender_official_notes.md -->

애드온은 Blender에 메뉴·도구·가져오기 형식을 더하는 Python 패키지입니다. 4.2부터는 `blender_manifest.toml`을 가진 확장(extension) 형식이 기본이고, 예전 `bl_info` 방식 애드온도 계속 쓸 수 있습니다. 이 문서는 두 형식 비교 → 설치·켜기 → 확장 만들기 → 명령줄 관리 → 예전 애드온 → 안전하게 쓰기 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, Blender 5.3.0 Linux판을 컨테이너에서 실행해 이 문서의 확장을 `--command extension validate`·`build`·`install-file`·`remove`로 처리하고, 켜기 상태 유지, `--addons`, 예전 `bl_info` 애드온 켜기, 잘못된 manifest 오류를 확인. 화면의 Preferences 조작과 온라인 저장소(extensions.blender.org) 내려받기는 확인하지 않았음

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 형식 비교](#1-형식-비교) / [2. 설치와 켜기](#2-설치와-켜기) / [3. 확장 만들기](#3-확장-만들기)     |
| [4. 명령줄로 관리](#4-명령줄로-관리) / [5. 예전 애드온](#5-예전-애드온) / [6. 켜기 범위](#6-켜기-범위) |
| [7. 안전하게 쓰기](#7-안전하게-쓰기) / [8. 트러블슈팅](#8-트러블슈팅)                                  |

---

## 1. 형식 비교

| 항목      | 확장 (4.2 이상)                                                | 예전 애드온                       |
|-----------|----------------------------------------------------------------|-----------------------------------|
| 정보 위치 | `blender_manifest.toml`                                        | 코드 안 `bl_info` 딕셔너리        |
| 배포      | zip, 온라인 저장소(extensions.blender.org 등)                  | `.py` 하나 또는 폴더 zip          |
| 설치 위치 | `<설정>/5.3/extensions/<저장소>/<id>`                          | `<설정>/5.3/scripts/addons/`      |
| 모듈 이름 | `bl_ext.<저장소>.<id>` (예 `bl_ext.user_default.simple_tools`) | 파일·폴더 이름 (예 `legacy_tool`) |
| 업데이트  | 저장소에서 판 비교·업데이트                                    | 직접 교체                         |
| 종류      | `add-on`, `theme`, `asset-library`                             | 애드온만                          |

- Linux 설정 폴더는 `~/.config/blender/5.3/`입니다. 다른 OS 위치는 [Blender 설치](./blender_install.md)를 봅니다.
- 기본 저장소: `user_default`(직접 설치한 확장, 사용자 폴더), `system`(설치 폴더 `5.3/extensions/system`).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치와 켜기

화면에서는 `Edit > Preferences > Get Extensions`(온라인) 또는 `Add-ons` 탭 메뉴의 `Install from Disk...`(zip 파일)로 설치하고, 목록에서 체크해 켭니다. 탭 이름은 5.3 환경 설정 목록(`Get Extensions`, `Add-ons`) 기준입니다.

| 단계      | 확인할 것                                              |
|-----------|--------------------------------------------------------|
| 출처      | 공식 저장소인지, 개발자·저장소가 믿을 만한지           |
| 판 범위   | manifest의 `blender_version_min`이 지금 판 이하인지    |
| 권한      | manifest `permissions`(파일, 네트워크 등) 요청 내용    |
| 켜기 뒤   | 메뉴·사이드바에 도구가 생겼는지, 콘솔에 오류가 없는지  |
| 설정 저장 | Preferences 자동 저장이 꺼져 있으면 `Save Preferences` |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 확장 만들기

폴더 하나에 `blender_manifest.toml`과 `__init__.py`를 둡니다.

```toml
# simple_tools/blender_manifest.toml
schema_version = "1.0.0"
id = "simple_tools"
version = "1.0.0"
name = "Simple Tools"
tagline = "Add a row of cubes"
maintainer = "Example <example@example.com>"
type = "add-on"
blender_version_min = "4.2.0"
license = ["SPDX:GPL-3.0-or-later"]
```

```python
# simple_tools/__init__.py
import bpy

class SIMPLE_OT_cube_row(bpy.types.Operator):
    bl_idname = "simple.cube_row"
    bl_label = "Cube Row"
    bl_options = {'REGISTER', 'UNDO'}
    count: bpy.props.IntProperty(name="Count", default=3, min=1, max=50)

    def execute(self, context):
        for i in range(self.count):
            bpy.ops.mesh.primitive_cube_add(location=(i * 2.5, 0, 0))
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(SIMPLE_OT_cube_row.bl_idname)

def register():
    bpy.utils.register_class(SIMPLE_OT_cube_row)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)    # Add > Mesh 메뉴에 추가

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(SIMPLE_OT_cube_row)
```

```bash
cd simple_tools
blender --command extension validate                 # Success parsing TOML in "."
blender --command extension build --output-dir ..    # created: "../simple_tools-1.0.0.zip"
```

| manifest 키           | 내용                                       |
|-----------------------|--------------------------------------------|
| `id`                  | 모듈 이름이 됨. 영문 소문자·숫자·밑줄      |
| `version`             | 판(의미 있는 버전 형식)                    |
| `type`                | `add-on`, `theme`, `asset-library` 중 하나 |
| `blender_version_min` | 지원하는 가장 낮은 판                      |
| `license`             | `SPDX:` 접두사를 붙인 라이선스 식별자      |
| `permissions` (선택)  | 파일·네트워크·클립보드 등 쓰는 권한과 이유 |
| `wheels` (선택)       | 함께 묶을 Python 패키지 wheel 파일         |

- `unregister()`는 `register()`의 반대 순서로 지웁니다. 켜고 끄기를 반복해도 메뉴가 중복되지 않습니다.
- `permissions`·`wheels`는 이 문서에서 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 명령줄로 관리

```bash
blender --command extension repo-list                     # 저장소 목록과 폴더
blender --command extension install-file -r user_default -e simple_tools-1.0.0.zip
#  STATUS Installed "simple_tools"   (-e: 설치하며 켬)
blender --command extension list                          # simple_tools [installed]
blender --command extension remove user_default.simple_tools
#  STATUS Removed "simple_tools"
```

| 하위 명령                                           | 하는 일                         |
|-----------------------------------------------------|---------------------------------|
| `build`, `validate`                                 | zip 만들기, manifest 검사       |
| `install-file`                                      | zip 파일 설치                   |
| `install`, `update`                                 | 온라인 저장소에서 설치·업데이트 |
| `list`, `remove`                                    | 목록, 제거                      |
| `sync`                                              | 온라인 저장소 목록 받기         |
| `repo-list`, `repo-add`, `repo-remove`, `repo-info` | 저장소 관리                     |
| `server-generate`                                   | 자체 저장소용 목록 만들기       |

- `blender --command help`로 명령 목록(`asset_listing`, `extension`, `maketx`)을 봅니다.
- `-e` 없이 설치하면 설치만 되고 꺼진 상태입니다.
- 시험에서 `remove`가 `blender_org` 폴더가 없다는 `[Errno 2]` 문구를 냈지만 제거는 성공했습니다(온라인 저장소를 한 번도 받지 않은 상태).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 예전 애드온

```python
# legacy_tool.py → ~/.config/blender/5.3/scripts/addons/ 에 복사
bl_info = {
    "name": "Legacy Tool",
    "author": "Example",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "category": "Object",
}
import bpy

class LEGACY_OT_hello(bpy.types.Operator):
    bl_idname = "legacy.hello"
    bl_label = "Legacy Hello"
    def execute(self, context):
        print("LEGACY_RUN")
        return {'FINISHED'}

def register(): bpy.utils.register_class(LEGACY_OT_hello)
def unregister(): bpy.utils.unregister_class(LEGACY_OT_hello)
```

```python
# 스크립트로 켜고 설정에 저장
import addon_utils, bpy
addon_utils.enable("legacy_tool", default_set=True)
bpy.ops.wm.save_userpref()
```

- 새로 만드는 도구는 확장 형식을 씁니다. 예전 애드온을 확장으로 바꿀 때는 `bl_info`의 내용을 manifest로 옮기고, 같은 패키지 안의 모듈을 상대 import(`from . import x`)로 부릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 켜기 범위

| 방법                                   | 이번 실행 | 다음 실행 | 시험 결과                                          |
|----------------------------------------|-----------|-----------|----------------------------------------------------|
| `install-file -e`                      | 켜짐      | 켜짐      | 다음 실행에서 `bpy.ops.simple.cube_row` 동작       |
| `install-file` (`-e` 없음)             | 꺼짐      | 꺼짐      | 환경 설정 애드온 목록에 없음                       |
| `--addons <모듈>`                      | 켜짐      | 안 남음   | 클래스는 등록되지만 환경 설정 애드온 목록에는 없음 |
| `addon_utils.enable` + `save_userpref` | 켜짐      | 켜짐      | 다음 실행 목록에 있음                              |
| `--factory-startup`                    | 꺼짐      | -         | 사용자 설정을 읽지 않아 켜 둔 애드온도 꺼짐        |

```bash
# 렌더 서버에서 이번 실행에만 켜기 (확장은 bl_ext.<저장소>.<id>)
blender -b --addons bl_ext.user_default.simple_tools scene.blend -f 1
```

- `--factory-startup`과 `--addons`를 함께 쓰면 이번 실행에서 확장 클래스가 등록됐습니다(시험 값 `True`).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 안전하게 쓰기

- 애드온은 Python 코드라 파일 읽기·쓰기·네트워크 접근을 모두 할 수 있습니다. 출처를 모르는 zip은 설치하지 않습니다.
- 설치 전 압축을 풀어 `__init__.py`와 manifest의 `permissions`를 읽어 봅니다.
- 작업용 PC와 렌더 서버의 애드온·판을 맞춥니다. 애드온이 만든 데이터가 있는 파일을 애드온 없는 서버에서 렌더하면 결과가 달라질 수 있습니다.
- `.blend` 파일 안의 스크립트 자동 실행은 애드온과 별개로 기본 꺼짐입니다([Blender 트러블슈팅](./blender_troubleshooting.md) 5절).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                                       | 원인                                      | 조치                                        |
|----------------------------------------------------------------------------|-------------------------------------------|---------------------------------------------|
| `key "type" invalid: Expected to be one of [add-on, asset-library, theme]` | manifest `type` 철자(`addon` 등)          | `add-on`으로 고침. `validate`는 종료 코드 1 |
| 설치했는데 메뉴에 없음                                                     | `-e` 없이 설치해 꺼진 상태                | Preferences에서 켜거나 `install-file -e`    |
| 렌더 서버에서 애드온이 꺼져 있음                                           | `--factory-startup` 사용                  | `--addons <모듈>` 추가                      |
| 켠 상태가 다음 실행에 사라짐                                               | 설정 저장 안 함, `--addons`로만 켬        | `save_userpref` 또는 Preferences 저장       |
| 켜고 끌 때마다 메뉴 항목이 늘어남                                          | `unregister`에서 메뉴 함수를 지우지 않음  | `append`한 것을 `remove`                    |
| `ModuleNotFoundError` (예전 애드온을 확장으로 옮긴 뒤)                     | 모듈 이름이 `bl_ext.<저장소>.<id>`로 바뀜 | 패키지 안은 상대 import                     |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender Python 스크립트](./blender_python_scripting.md) — 연산자·패널 작성
- [Blender 명령줄과 일괄 렌더](./blender_cli_batch_render.md) — 서버 렌더
- [Blender 설치](./blender_install.md) — 설정 폴더 위치

---

## 참고 자료

- Blender Manual: [Extensions](https://docs.blender.org/manual/en/latest/advanced/extensions/index.html) · [Getting Started (extension 만들기)](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html) — ★★★☆☆
- Blender Manual: [Add-ons](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html) · [Command Line Arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html) — ★★★☆☆
- Blender Extensions Platform: [extensions.blender.org](https://extensions.blender.org/) — ★★★☆☆

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
