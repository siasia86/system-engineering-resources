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
  - https://github.com/openstf/stf
  - https://appium.io/docs/en/latest/intro/
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

| 프로젝트                                  | 확인된 범위                                                   | 상태·판단                                      |
|-------------------------------------------|---------------------------------------------------------------|------------------------------------------------|
| DeviceFarmer/stf                          | 브라우저 기반 Android 기기 제어·관리                          | 개발 진행 중, `v3.7.9` release 확인            |
| openstf/stf                               | 기존 Android device farm                                     | 개발이 DeviceFarmer로 이동, 신규 선택 비권장   |
| Appium                                    | W3C WebDriver 기반 다중 플랫폼 앱 자동화                     | Apache-2.0, 개발 진행 중                       |
| Maestro                                   | Android·iOS·Web UI·E2E 자동화, 물리 Android 기기             | Apache-2.0, 개발 진행 중                       |
| Android Emulator Container Scripts        | Docker 등에서 Android Emulator 실행을 위한 스크립트          | Apache-2.0, Google 저장소                      |
| Mobly                                     | 복잡한 환경 요구사항을 가진 Android E2E 테스트 프레임워크     | Apache-2.0, Google 저장소                      |

DeviceFarmer 저장소의 GitHub license metadata는 `NOASSERTION`으로 표시되므로 상용·사내 서비스에 적용하기 전에 저장소 LICENSE와 third-party dependency를 법무·보안 기준으로 확인해야 합니다.

## 3. 관리형 서비스

| 서비스             | 공식 확인 내용                                                   |
|--------------------|------------------------------------------------------------------|
| AWS Device Farm    | AWS 호스팅 실제 Android·iOS·Web 기기, Appium·XCTest, 병렬 실행 |
| Firebase Test Lab  | 클라우드 실제·가상 Android·iOS 기기, CLI·Game Loop              |

AWS Device Farm 문서에는 Device Farm 서비스가 `us-west-2`에서 제공된다고 기재되어 있습니다. AWS 문서는 Android·iOS·Web 테스트, 원격 브라우저 접근, client-side Appium, service-side 병렬 실행을 설명합니다.

Firebase Test Lab의 Game Loop 문서는 게임 엔진에 맞춘 테스트를 작성하여 선택한 기기에서 실행하는 방식을 설명합니다. Game Loop는 일반 UI selector에만 의존하지 않고 게임 플레이 흐름을 검증하는 용도로 사용할 수 있습니다.

## 4. 가상화·멀티 머신

Vagrant 공식 문서는 Multi-Machine으로 여러 VM을 하나의 `Vagrantfile`에서 정의하고 관리하는 기능을 제공합니다. Hyper-V provider도 별도 지원하지만, Vagrant는 VM 수명주기·프로비저닝 도구이며 모바일 실기기나 대규모 사용자 부하 생성 도구가 아닙니다.

Android Emulator는 실제 모바일 기기의 GPU·배터리·발열·무선망을 완전히 재현하지 않습니다. 에뮬레이터 수용량은 메모리뿐 아니라 CPU, GPU 또는 가상 GPU, 디스크 I/O, ADB, 네트워크에 의해 결정됩니다.

## 5. 게임·Unity 적용 시 주의

Unity 게임 화면이 일반적인 접근성 트리나 네이티브 UI로 노출되지 않으면 Appium·Maestro의 selector 기반 자동화가 제한될 수 있습니다. 다음을 분리하여 검토해야 합니다.

- Game Loop 또는 게임 내부 test hook: 게임 입력·상태·시나리오 검증.
- Appium·Maestro: 로그인, 권한, 패치, 백그라운드, 딥 링크 등 외부 UI 흐름.
- Protocol load generator: HTTP·WebSocket·게임 메시지 기반 대규모 backend 부하.

## 6. iOS 제약

iOS 실기기 자동화는 일반적으로 Apple의 macOS·Xcode·XCTest toolchain과 연결됩니다. Windows 서버만으로 자체 iOS 실기기 farm을 구성하는 것보다 AWS Device Farm, Firebase Test Lab, 상용 device cloud 또는 별도 Mac host를 사용하는 방식이 현실적입니다.

## 7. 보안·운영 확인 항목

- 테스트 계정·토큰·결제 sandbox를 production 자격증명과 분리합니다.
- Device farm 관리 API와 ADB/Appium endpoint를 사설 네트워크로 제한합니다.
- 기기 화면·로그·스크린샷에 개인정보와 token이 남지 않도록 합니다.
- USB device farm은 powered hub, USB host controller, 케이블, 배터리, 발열을 별도 관리합니다.
- 관리형 서비스는 업로드 artifact, 리전, 보존 기간, 네트워크 경로, 비용을 확인합니다.
- 실제 backend 부하는 device farm의 UI 테스트와 분리하여 protocol load generator로 수행합니다.
