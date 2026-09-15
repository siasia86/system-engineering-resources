---
name: mobile-device-testing-official-notes
description: 모바일 게임 실기기·에뮬레이터·자동화·관리형 device farm 공식 참조 노트
tags:
  - mobile-testing
  - device-farm
  - android
  - ios
  - appium
  - firebase-test-lab
  - aws-device-farm
last_checked: 2026-09-15
sources:
  - https://github.com/DeviceFarmer/stf
  - https://github.com/DeviceFarmer/stf/releases/tag/v3.7.9
  - https://github.com/openstf/stf
  - https://appium.io/docs/en/latest/intro/
  - https://github.com/appium/appium/blob/master/LICENSE
  - https://appium.github.io/appium-xcuitest-driver/latest/
  - https://github.com/mobile-dev-inc/Maestro
  - https://github.com/google/android-emulator-container-scripts
  - https://github.com/google/mobly
  - https://docs.aws.amazon.com/devicefarm/latest/developerguide/welcome.html
  - https://docs.aws.amazon.com/devicefarm/latest/developerguide/test-types.html
  - https://firebase.google.com/docs/test-lab
  - https://firebase.google.com/docs/test-lab/game-loop
  - https://developer.hashicorp.com/vagrant/docs/multi-machine
  - https://developer.hashicorp.com/vagrant/docs/providers/hyperv
---

# 모바일 기기 테스트 공식 참조 노트

## 1. 확인 범위

모바일 게임의 실제 기기, 에뮬레이터, UI 자동화, 게임 루프, 관리형 device farm 후보를 2026-09-15에 공식 저장소·공식 문서 기준으로 확인했습니다.

## 2. 오픈소스 프로젝트

| 프로젝트                           | 공식 확인 사실                                                   |
|------------------------------------|------------------------------------------------------------------|
| DeviceFarmer/stf                   | Android 기기 브라우저 제어·inventory 관리, `v3.7.9` release 확인 |
| openstf/stf                        | README에서 active development가 DeviceFarmer로 이동했다고 안내   |
| Appium                             | W3C WebDriver 기반 앱 자동화, Apache-2.0 LICENSE                 |
| Maestro                            | Android·iOS·Web UI·E2E 자동화, YAML flow, 물리 Android 지원      |
| Android Emulator Container Scripts | Docker 등에서 Android Emulator 실행을 위한 Google 스크립트       |
| Mobly                              | Python 기반, 다중 장치·복잡한 환경·custom hardware 테스트        |

DeviceFarmer 저장소의 GitHub license metadata는 `NOASSERTION`으로 표시됩니다. 저장소 LICENSE와 third-party dependency license는 별도 확인 대상입니다.

## 3. 관리형 서비스

| 서비스             | 공식 확인 내용                                                   |
|--------------------|------------------------------------------------------------------|
| AWS Device Farm    | AWS 호스팅 실제 Android·iOS·Web 기기, Appium·XCTest, 병렬 실행 |
| Firebase Test Lab  | 클라우드 실제·가상 Android·iOS 기기, CLI·Game Loop              |

AWS Device Farm 문서에는 Device Farm 서비스가 `us-west-2`에서 제공된다고 기재되어 있습니다. AWS 문서는 Android·iOS·Web 테스트, 원격 브라우저 접근, client-side Appium, service-side 병렬 실행을 설명합니다.

Firebase Test Lab의 Game Loop 문서는 게임 엔진에 맞춘 테스트를 작성하여 선택한 기기에서 실행하는 방식을 설명합니다. Android·iOS 문서 모두 Game Loop test 흐름을 제공합니다.

## 4. 가상화·멀티 머신

Vagrant 공식 문서는 Multi-Machine으로 여러 VM을 하나의 `Vagrantfile`에서 정의하고 관리하는 기능을 제공합니다. Hyper-V provider도 별도 문서로 제공됩니다.

본 문서에서는 Vagrant를 VM 수명주기·프로비저닝 계층으로 분류하고, 모바일 실기기 제어와 대규모 사용자 부하는 별도 도구로 분리합니다.

## 5. 게임·Unity 적용 시 확인 항목

Maestro README는 플랫폼 접근성 계층을 이용하여 앱을 제어한다고 설명합니다. Unity 게임 화면이 접근성 계층이나 네이티브 UI로 노출되는지는 앱별로 다르므로 selector 기반 자동화를 적용하기 전에 확인해야 합니다.

다음 역할은 별도로 검증합니다.

- Game Loop 또는 게임 내부 test hook: 게임 입력·상태·시나리오 검증.
- Appium·Maestro: 로그인, 권한, 패치, 백그라운드, 딥 링크 등 외부 UI 흐름.
- Protocol load generator: HTTP·WebSocket·게임 메시지 기반 backend 부하.

## 6. iOS toolchain

Appium XCUITest driver 공식 문서는 iOS·iPadOS·tvOS·watchOS 자동화와 Xcode·host 관련 설정 항목을 제공합니다. iOS 실기기 자동화의 local host·Xcode·signing 요구사항은 해당 driver와 Apple toolchain 조합으로 별도 검증해야 합니다.

Windows 서버만으로 자체 iOS 실기기 farm을 구성할지 여부는 위 toolchain 요구사항과 운영 환경을 확인한 뒤 결정합니다.
