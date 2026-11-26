# Blender 재질과 셰이딩
<!-- reference: _reference/blender_official_notes.md -->

재질(Material)은 표면이 빛을 어떻게 반사·투과·발광하는지 정하는 설정이고, Blender는 셰이더 노드(Shader Node)를 연결해 재질을 만듭니다. 이 문서는 재질 만들기 → Principled BSDF 주요 입력 → 텍스처 연결 → 색 공간 → 투명·발광 → 재질 슬롯 → 미리 보기 순서로 정리합니다.

- 기준 판: Blender 5.3.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `bpy` 5.3.0 컨테이너에서 새 재질의 기본 노드, Principled BSDF 입력 36개와 기본값, 이미지 텍스처 연결, 색 공간 목록, 투명 렌더 방식, 보기 변환 기본값을 확인하고 이미지 텍스처를 입힌 기본 장면을 EEVEE·Cycles(CPU)로 128×128 렌더. Shading 작업 공간의 화면 조작과 GPU 렌더는 실행하지 않았음

## 목차

| 섹션                                                                                                           |
|----------------------------------------------------------------------------------------------------------------|
| [1. 재질 만들기](#1-재질-만들기) / [2. Principled BSDF](#2-principled-bsdf) / [3. 텍스처 연결](#3-텍스처-연결) |
| [4. 색 공간](#4-색-공간) / [5. 투명과 발광](#5-투명과-발광) / [6. 재질 슬롯](#6-재질-슬롯)                     |
| [7. 미리 보기와 엔진](#7-미리-보기와-엔진) / [8. 재질 예시값](#8-재질-예시값) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 재질 만들기

1. 객체를 선택하고 상단 작업 공간 탭에서 `Shading`을 엽니다(가운데 아래가 Node Editor).
2. Node Editor 머리줄의 `New`를 누르거나 Properties > Material 탭에서 `New`를 누릅니다.
3. 새 재질에는 처음부터 `Principled BSDF` → `Material Output` 두 노드가 연결되어 있습니다.

```text
[Principled BSDF] ──BSDF──▶ Surface [Material Output]
```

- 노드 추가는 Node Editor에서 `Shift+A`, 노드 연결은 출력 소켓에서 입력 소켓으로 끌기, 연결 끊기는 `Ctrl` + 오른쪽 버튼 끌기(자르기)입니다(매뉴얼 기준, 화면 조작은 시험하지 않음).
- 기본 정육면체에는 처음부터 재질(`Material`)과 UV 맵(`UVMap`)이 있습니다.
- 5.3에서 새 재질은 노드 트리를 처음부터 가집니다. 스크립트에서 `material.use_nodes = True`를 쓰면 6.0에서 없앨 예정이라는 경고가 나옵니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Principled BSDF

여러 재질을 입력값만 바꿔 표현하는 만능 셰이더입니다. 5.3.0 입력은 36개이고, 자주 쓰는 것은 다음과 같습니다.

| 입력                      | 기본값          | 뜻                                            |
|---------------------------|-----------------|-----------------------------------------------|
| Base Color                | (0.8, 0.8, 0.8) | 기본 색(알베도)                               |
| Metallic                  | 0               | 0 = 비금속, 1 = 금속. 중간값은 거의 쓰지 않음 |
| Roughness                 | 0.5             | 0 = 거울처럼 매끈, 1 = 완전히 거침            |
| IOR                       | 1.5             | 굴절률. 유리 1.5, 물 1.33                     |
| Alpha                     | 1               | 불투명도. 0이면 완전히 투명                   |
| Normal                    | -               | 노멀 맵·범프 연결 자리                        |
| Subsurface Weight         | 0               | 피부·밀랍처럼 빛이 안으로 스며드는 정도       |
| Specular IOR Level        | 0.5             | 비금속 반사 세기 조절                         |
| Transmission Weight       | 0               | 1이면 유리처럼 빛이 통과                      |
| Coat Weight               | 0               | 표면 위 투명 코팅(자동차 도장·니스)           |
| Sheen Weight              | 0               | 천·벨벳의 가장자리 광택                       |
| Emission Color / Strength | 흰색 / 0        | 스스로 빛남. Strength가 0이면 꺼짐            |

- 입력은 Diffuse, Subsurface, Specular, Transmission, Coat, Sheen, Emission, Thin Film 묶음으로 접혀 있습니다. 전체 목록과 기본값은 [참조 노트](../../_reference/blender_official_notes.md) 6절에 있습니다.
- 기본 반사 모델은 Multiscatter GGX, 표면 아래 산란 방식은 Random Walk입니다.
- 실제 재질 값을 쓸 때는 Metallic을 0 또는 1로, 색은 Base Color로, 거칠기는 Roughness로 나눠 생각하면 대부분 맞습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 텍스처 연결

이미지 텍스처는 `Image Texture` 노드로 불러와 Principled BSDF 입력에 연결합니다.

```text
[Image Texture: 색]       ──Color──▶ Base Color ─┐
[Image Texture: 거칠기]   ──Color──▶ Roughness  ─┤
[Image Texture: 노멀]     ──Color──▶ [Normal Map] ──Normal──▶ Normal ─┤
                                                                     ▼
                                                 [Principled BSDF] ──▶ [Material Output]
```

| 텍스처 종류 | 연결 위치                | 색 공간   |
|-------------|--------------------------|-----------|
| 색(Albedo)  | Base Color               | sRGB      |
| 거칠기      | Roughness                | Non-Color |
| 금속성      | Metallic                 | Non-Color |
| 노멀 맵     | Normal Map 노드 → Normal | Non-Color |
| 높이(Bump)  | Bump 노드 → Normal       | Non-Color |
| 발광        | Emission Color           | sRGB      |

- 텍스처가 모델에 제대로 붙으려면 UV 맵이 필요합니다. 기본 도형은 UV가 있지만 직접 만든 모양은 UV를 펼쳐야 합니다(Edit 모드 `U`).
- Normal Map 노드 입력은 Strength와 Color 두 개입니다. 노멀 맵 이미지를 Normal 입력에 바로 연결하면 틀린 결과가 나옵니다.
- 시험: 기본 정육면체 재질에 생성 이미지(Color Grid)를 Image Texture로 Base Color에 연결해 EEVEE와 Cycles로 렌더했고, 두 엔진 모두 성공했습니다.
- Node Wrangler 애드온의 `Ctrl+Shift+T`(Principled 텍스처 한꺼번에 연결)는 애드온 기능이라 이 문서에서 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 색 공간

색 공간을 잘못 고르면 색이 뿌옇거나 금속성·거칠기가 틀어집니다.

- 색이 있는 이미지(색·발광): `sRGB`. 새 이미지의 초기값입니다.
- 데이터 이미지(거칠기·금속성·노멀·높이): `Non-Color`. 값 자체를 그대로 써야 하기 때문입니다.
- EXR·HDR 같은 선형 이미지: `Linear Rec.709` 등 선형 색 공간.

화면 표시는 Properties > Render > Color Management에서 정합니다.

| 항목           | 5.3.0 초기값 | 설명                                  |
|----------------|--------------|---------------------------------------|
| Display Device | sRGB         | 모니터 종류                           |
| View Transform | AgX          | 밝은 부분이 하얗게 날아가지 않게 압축 |
| Look           | None         | 대비 조절 프리셋                      |

- 텍스처 원래 색 그대로 보고 싶으면(예: UI 그림, 픽셀 아트) View Transform을 `Standard`로 바꿉니다(설정 가능 확인).
- 5.3의 입력 색 공간 목록에는 ACES·AgX·카메라 로그(ARRI·Canon·Apple Log 등)도 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 투명과 발광

### 5.1 투명

- 구멍 뚫린 잎·철망: 이미지 텍스처의 Alpha 출력을 Principled BSDF의 Alpha에 연결합니다.
- 유리·물: Transmission Weight를 1로, Roughness를 0 근처로, IOR을 재질 값으로 둡니다.
- EEVEE는 재질 설정(Properties > Material > Settings)의 Render Method에 따라 투명을 그립니다.

| Render Method | 초기값 | 특징                                                  |
|---------------|--------|-------------------------------------------------------|
| Dithered      | 초기값 | 점 패턴으로 투명 처리, 겹친 투명 면에 강함            |
| Blended       | -      | 실제 혼합, 반투명 표현이 부드럽지만 겹친 면 순서 문제 |

### 5.2 발광

- Emission Strength를 0보다 크게 하면 표면이 빛납니다. 색은 Emission Color로 정합니다.
- Cycles에서는 발광 면이 실제로 주변을 비춥니다. EEVEE도 주변을 비추지만 Cycles보다 근사적입니다(엔진 차이는 매뉴얼 기준, 시험하지 않음).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 재질 슬롯

한 객체에 여러 재질을 쓰려면 재질 슬롯(Material Slot)을 여러 개 둡니다.

1. Properties > Material 탭의 슬롯 목록 오른쪽 `+`로 슬롯을 추가하고 재질을 고릅니다.
2. Edit 모드에서 면을 선택하고 슬롯을 고른 뒤 `Assign`을 누릅니다.

- 슬롯은 객체(Object) 또는 메시 데이터(Data)에 연결됩니다. 초기값은 메시 데이터 연결이라, 같은 메시를 쓰는 연결 복제본은 재질도 같습니다.
- 재질 이름 옆 숫자는 그 재질을 쓰는 사용자 수입니다. 0이면 파일을 저장·다시 열 때 지워질 수 있으니 방패(Fake User)를 켜서 보관합니다.
- 같은 재질을 여러 객체에 주려면 대상들을 선택하고 원본을 마지막에 선택한 뒤 `Ctrl+L` > `Link Materials`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 미리 보기와 엔진

| 3D 뷰포트 표시 | 조명                     | 쓰는 때                  |
|----------------|--------------------------|--------------------------|
| Material       | 내장 HDRI 미리 보기 조명 | 재질 색·질감 빠르게 확인 |
| Rendered       | 장면의 실제 조명과 월드  | 최종 결과 확인           |

| 엔진      | 특징                                        | 5.3.0 기본값                                                                 |
|-----------|---------------------------------------------|------------------------------------------------------------------------------|
| EEVEE     | 실시간(래스터화), 빠름. 장면 기본 엔진      | 렌더 샘플 64                                                                 |
| Cycles    | 경로 추적, 사실적이지만 느림. GPU 가속 가능 | 샘플 4096, 적응 샘플링 켬(기준 0.01), 노이즈 제거 OpenImageDenoise, 장치 CPU |
| Workbench | 모델링 확인용 단색 표시                     | -                                                                            |

- 같은 재질 노드를 EEVEE와 Cycles가 함께 씁니다. 다만 일부 노드·설정은 한 엔진에서만 동작합니다.
- 렌더 엔진은 Properties > Render 탭에서 바꿉니다. 조명·렌더 설정은 별도 문서에서 다룰 예정입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 재질 예시값

Principled BSDF 입력만으로 만드는 출발점 값입니다. 실제 모습은 조명·텍스처에 따라 조정합니다.

| 재질           | Base Color          | Metallic | Roughness | 기타                                    |
|----------------|---------------------|----------|-----------|-----------------------------------------|
| 플라스틱(광택) | 원하는 색           | 0        | 0.2~0.4   | -                                       |
| 고무           | 어두운 색           | 0        | 0.8~1.0   | -                                       |
| 철·알루미늄    | 밝은 회색           | 1        | 0.3~0.5   | -                                       |
| 금             | 노란 주황           | 1        | 0.2~0.3   | -                                       |
| 유리           | 흰색                | 0        | 0~0.05    | Transmission Weight 1, IOR 1.5          |
| 물             | 흰색                | 0        | 0         | Transmission Weight 1, IOR 1.33         |
| 자동차 도장    | 원하는 색           | 0~1      | 0.3~0.5   | Coat Weight 1, Coat Roughness 0.03      |
| 천             | 원하는 색           | 0        | 0.8~1.0   | Sheen Weight 0.5~1                      |
| 피부           | 피부색              | 0        | 0.4~0.5   | Subsurface Weight 0.1~0.3               |
| 네온           | 검정 또는 어두운 색 | 0        | 0.5       | Emission Color 원하는 색, Strength 5~20 |

- 위 값은 일반적인 출발점이며 이 문서에서 렌더 비교로 검증하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                | 원인                                      | 해결                                                               |
|-------------------------------------|-------------------------------------------|--------------------------------------------------------------------|
| Solid 표시에서 재질 색이 안 보임    | Solid는 재질 노드를 그리지 않음           | Material 또는 Rendered 표시로 바꿈                                 |
| 텍스처가 늘어나거나 엉뚱하게 붙음   | UV가 없거나 잘못 펼쳐짐                   | Edit 모드 `U`로 UV 펼치기, UV Editing 작업 공간에서 확인           |
| 텍스처 색이 뿌옇고 흐림             | 데이터 맵이 sRGB, 또는 색 맵이 Non-Color  | 4절 색 공간 표대로 설정                                            |
| 노멀 맵이 울퉁불퉁 이상하게 보임    | Normal Map 노드 없이 바로 연결, sRGB 설정 | Normal Map 노드 경유, Non-Color                                    |
| 렌더가 분홍색(마젠타)으로 나옴      | 이미지 파일을 찾지 못함                   | `File > External Data > Find Missing Files`, 또는 `Pack Resources` |
| 투명이 검게·불투명하게 나옴(EEVEE)  | Render Method·그림자 설정                 | Render Method를 Blended로 바꿔 비교                                |
| 저장 후 다시 열었더니 재질이 사라짐 | 사용자 0인 재질이 정리됨                  | Fake User(방패) 켜기                                               |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Blender 모디파이어](./blender_modifiers.md) — 모양을 만드는 비파괴 편집
- [Blender 화면 구성](./blender_interface.md) — Shading 작업 공간, 표시 방식

---

## 참고 자료

- Blender Manual: [Materials](https://docs.blender.org/manual/en/latest/render/materials/index.html) · [Principled BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html) · [Color Management](https://docs.blender.org/manual/en/latest/render/color_management.html) — ★★★☆☆
- Blender Python API: [ShaderNodeBsdfPrincipled](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html) — 시험에 쓴 입력 이름 — ★★★☆☆

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
