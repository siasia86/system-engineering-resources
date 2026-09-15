# 모바일 게임 기기 테스트 솔루션 검토
<!-- reference: _reference/mobile_device_testing_official_notes.md -->

Node.js·C# backend와 Unity client로 구성된 모바일 게임의 사전 오픈 검증을 위해, 실제 모바일 기기·에뮬레이터·UI 자동화·게임 흐름·backend 부하를 분리하여 사용할 수 있는 오픈소스와 관리형 솔루션을 비교합니다. 조사 기준일은 2026-09-15입니다.

## 목차

| 섹션                                                                                                                                                       |
|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 결론과 테스트 계층](#1-결론과-테스트-계층) / [2. 오픈소스 후보](#2-오픈소스-후보) / [3. 관리형 서비스](#3-관리형-서비스)                               |
| [4. Unity 게임 적용 시 주의](#4-unity-게임-적용-시-주의) / [5. Windows 서버와 AWS 활용](#5-windows-서버와-aws-활용) / [6. 권장 아키텍처](#6-권장-아키텍처) |
| [7. 파일럿·검증·롤백](#7-파일럿검증롤백) / [8. 선택 기준과 미결 사항](#8-선택-기준과-미결-사항)                                                            |

---

## 1. 결론과 테스트 계층

### 결론

실제 모바일 기기와 backend 대규모 부하는 하나의 도구로 해결하지 않습니다.

- 실제 Android·iOS 기기: AWS Device Farm 또는 Firebase Test Lab 우선 검토.
- 자체 Android 기기 farm: DeviceFarmer + Appium 또는 Maestro 검토.
- Android 에뮬레이터 대량 실행: Windows Hyper-V·Linux KVM·Android Emulator 검토.
- Unity 게임 흐름: Firebase Game Loop 또는 게임 내부 test hook 검토.
- 수천 virtual users의 backend 부하: k6·Locust·custom protocol runner 사용.
- Windows game client 반복 실행: Vagrant·Hyper-V를 보조 수단으로 사용.

### 테스트 계층

```text
┌─────────────────────────────────────────────────────────────────────┐
│                       Mobile Test Strategy                          │
├─────────────────────────────────────────────────────────────────────┤
│  Physical devices   → device compatibility, thermal, battery, UX    │
│  Emulators          → device matrix, repeatability, scale           │
│  UI automation      → login, patch, permission, reconnect           │
│  Game loop          → Unity gameplay flow and state                 │
│  Protocol load      → CCU, RPS, WebSocket, DB, cache, queue         │
└─────────────────────────────────────────────────────────────────────┘
```

> Device farm: 실제 스마트폰·태블릿을 여러 대 연결하거나 클라우드에서 대여하여 원격으로 테스트하는 환경입니다. 기기 관리, 앱 설치, 자동화 실행, 로그·화면 수집을 한 계층에서 처리합니다.

### 도구 역할을 혼합하지 않는 이유

실기기 UI 테스트를 수천 명의 사용자 부하 생성기로 사용하면 기기 렌더링·ADB·자동화 도구가 병목이 되어 backend 부하를 정확히 측정하기 어렵습니다. 반대로 protocol runner만 사용하면 GPU·발열·앱 생명주기·OS별 동작을 검증할 수 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 오픈소스 후보

### 후보 비교

| 프로젝트                           | 주된 역할                           | Android | iOS | 권장 용도                                 |
|------------------------------------|-------------------------------------|---------|-----|-------------------------------------------|
| DeviceFarmer/stf                   | 브라우저 기반 기기 연결·관리        | ✅      | ❌  | 자체 Android 실기기 farm                  |
| Appium                             | WebDriver 기반 앱 자동화            | ✅      | ✅  | 표준 UI·E2E 자동화                        |
| Maestro                            | YAML 기반 UI·E2E 자동화             | ✅      | ✅  | 로그인·패치·재접속 회귀 테스트            |
| Android Emulator Container Scripts | 컨테이너 기반 Android Emulator 실행 | ✅      | ❌  | Android emulator scale-out                |
| Mobly                              | 복잡한 장치·네트워크 환경 테스트    | ✅      | ❌  | Android 하드웨어·통합 테스트              |
| OpenSTF                            | 기존 Android device farm            | ✅      | ❌  | 신규 선택보다 DeviceFarmer migration 권장 |

### DeviceFarmer

DeviceFarmer/stf는 브라우저에서 Android 기기를 관리하고, ADB 기반 제어와 원격 화면·입력 기능을 제공하는 자체 device farm 후보입니다.

현재 확인된 상태입니다.

- GitHub 저장소 비보관 상태.
- `v3.7.9` release 확인.
- Android 중심이며 iOS device farm은 제공하지 않습니다.
- USB hub·전원·USB host controller·ADB 연결 안정성이 운영 핵심입니다.
- GitHub license metadata가 `NOASSERTION`이므로 사내·상용 사용 전 법적 검토가 필요합니다.

OpenSTF 원본 저장소는 README에서 active development가 DeviceFarmer 조직으로 이동했다고 안내합니다. 신규 구축은 OpenSTF 원본보다 DeviceFarmer를 우선 검토합니다.

### Appium

Appium은 W3C WebDriver 기반의 다중 플랫폼 앱 자동화 프레임워크입니다.

적합한 테스트입니다.

- Android·iOS 로그인·권한·설정 화면.
- 앱 설치·삭제·업데이트.
- 백그라운드 전환·재실행.
- 딥 링크·푸시·외부 브라우저 전환.
- 물리 기기와 emulator를 동일한 시나리오로 반복 실행.

Appium은 device farm 자체가 아닙니다. 기기 할당·초기화·병렬 실행·로그 수집은 DeviceFarmer, Selenium Grid, 관리형 device cloud 또는 별도 runner가 담당해야 합니다.

### Maestro

Maestro는 Android·iOS·Web을 대상으로 YAML flow를 작성하는 오픈소스 UI·E2E 자동화 도구입니다.

- 테스트 흐름을 짧게 작성하기 쉽습니다.
- Android physical device와 emulator를 사용할 수 있습니다.
- iOS simulator·physical device 환경은 host와 toolchain 조건을 별도로 확인해야 합니다.
- Maestro Cloud의 병렬 실행은 오픈소스 CLI와 별도의 관리형 서비스 범위입니다.
- Unity Canvas가 접근성 트리에 노출되지 않으면 selector 기반 테스트가 제한될 수 있습니다.

### Android Emulator Container Scripts

Google의 `android-emulator-container-scripts`는 Docker 등 컨테이너 환경에서 Android Emulator를 실행하기 위한 최소 스크립트 모음입니다.

Windows 서버 10대에서 바로 적용하기 전에 다음을 검증해야 합니다.

- Hyper-V 또는 WSL2의 nested virtualization.
- GPU 또는 virtual GPU와 렌더링 모드.
- 컨테이너별 CPU·메모리·디스크 사용량.
- ADB 포트와 emulator 식별자 충돌.
- Windows Server·Docker·GPU driver 조합의 지원 범위.

RAM 512GB만으로 동시 emulator 수를 추정하지 않습니다. 4개 emulator의 기준선을 먼저 측정한 뒤 8개, 16개로 늘려 서버별 수용량을 산출합니다.

### Mobly

Mobly는 일반적인 UI device farm보다 복잡한 Android 장치·네트워크·하드웨어 환경 테스트에 적합합니다.

- 여러 Android 기기와 주변 장치의 상호작용.
- 네트워크·Bluetooth·센서 등 복합 환경.
- Python 기반 테스트 코드.
- 게임 UI 회귀보다 장치 통합·환경 재현에 적합.

### 라이선스와 유지 상태

오픈소스 도구는 기능만 비교하지 않고 다음을 확인합니다.

- 저장소의 실제 LICENSE 파일.
- third-party dependency license.
- 최근 commit·release·보안 공지.
- Android SDK·Xcode·Java·Node.js 호환성.
- 회사의 배포·수정·내부 운영 정책.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 관리형 서비스

### AWS Device Farm

AWS Device Farm은 AWS가 호스팅하는 실제 Android·iOS·Web 기기를 대상으로 테스트하는 관리형 서비스입니다.

공식 문서에서 확인된 기능입니다.

- 실제 물리 Android·iOS·Web 기기.
- 브라우저를 통한 원격 기기 접근.
- client-side Appium endpoint.
- Android Appium·Instrumentation.
- iOS Appium·XCTest·XCTest UI.
- 여러 기기 병렬 실행.
- 로그·비디오·테스트 artifact 저장.

현재 공식 문서에는 Device Farm이 `us-west-2`에서 제공된다고 기재되어 있으므로, 게임 backend가 다른 AWS 리전에 있으면 다음을 별도 측정합니다.

- Device Farm에서 backend까지의 RTT.
- 로그인·패치·게임 명령의 latency.
- 지역별 CDN·WAF·인증 endpoint 경로.
- 테스트 트래픽과 실제 사용자 트래픽의 구분.

### Firebase Test Lab

Firebase Test Lab은 클라우드에서 실제·가상 Android·iOS 기기를 선택하여 테스트하는 서비스입니다.

특히 모바일 게임에서는 Game Loop 테스트를 검토할 가치가 있습니다.

- 게임 엔진에 맞춘 사용자 행동 시나리오 작성.
- 선택한 기기에서 전체 또는 부분 게임 흐름 실행.
- 일반 UI framework에만 의존하지 않는 게임 동작 검증.
- 기기별 결과·로그·crash 정보 비교.
- Android·iOS 테스트 범위는 현재 앱 package와 Test Lab 지원 조합으로 사전 검증.

### 상용 device cloud

BrowserStack, Sauce Labs, Kobiton, HeadSpin, Perfecto, LambdaTest 등도 후보입니다. 다음 항목을 같은 시나리오로 비교해야 합니다.

- 필요한 Android·iOS 모델 보유 여부.
- 실제 기기와 virtual device 구분.
- Appium·XCTest·Game Loop 지원 여부.
- 병렬 실행 수와 대기열.
- 한국·아시아 지역 네트워크 경로.
- 동영상·로그·crash artifact.
- CI 연동과 보존 기간.
- 테스트 분당 과금과 private device 비용.

### 관리형 서비스 선택 기준

| 기준      | 확인 질문                                                  |
|-----------|------------------------------------------------------------|
| 기기      | 필요한 OS·제조사·모델·화면 크기를 보유하는가?              |
| 게임 흐름 | Unity Game Loop 또는 custom input을 지원하는가?            |
| 자동화    | Appium·XCTest·CLI·CI를 지원하는가?                         |
| 지역성    | 테스트 기기와 backend 사이의 실제 네트워크 경로는 어떤가?  |
| 병렬성    | 동시에 몇 대를 실행하고 queue 대기는 얼마인가?             |
| artifact  | log·video·screenshot·crash를 다운로드할 수 있는가?         |
| 보안      | APK·IPA·계정·로그의 보존·삭제·접근통제가 가능한가?         |
| 비용      | 기기분·병렬성·private device·저장 비용을 예측할 수 있는가? |

[⬆ 목차로 돌아가기](#목차)

---

## 4. Unity 게임 적용 시 주의

### UI 자동화의 한계

Unity 게임 화면이 일반적인 접근성 트리나 네이티브 UI로 노출되지 않으면 Appium·Maestro의 selector 기반 자동화가 제한될 수 있습니다.

다음 요소가 조회되지 않을 수 있습니다.

- Unity Button과 GameObject 이름.
- Canvas 내부 텍스트.
- 게임 상태와 네트워크 상태.
- 특정 게임 오브젝트의 좌표.
- 렌더링 결과와 실제 frame 상태.

### 권장 테스트 분리

| 테스트 계층   | 권장 도구·방법                     | 검증 대상                              |
|---------------|------------------------------------|----------------------------------------|
| Game Loop     | Firebase Test Lab 또는 custom hook | 로그인·로비·매칭·플레이·보상·저장 흐름 |
| UI 회귀       | Appium 또는 Maestro                | 권한·패치·딥 링크·백그라운드·재실행    |
| 실기기 호환성 | AWS·Firebase 또는 자체 device farm | OS·GPU·화면·발열·배터리·네트워크       |
| backend 부하  | k6·Locust·custom protocol runner   | CCU·RPS·WebSocket·DB·cache·queue       |
| client 성능   | Unity Profiler·실기기 측정         | FPS·memory·battery·thermal·crash       |

> Game Loop: 게임 엔진에 맞춘 입력과 동작 흐름을 테스트 앱에 연결하여 실제 플레이어의 전체 또는 부분 행동을 반복 실행하는 방식입니다. 일반적인 UI selector보다 게임 상태와 플레이 흐름 검증에 적합합니다.

### 테스트 hook 권장 항목

Unity client에 테스트 전용 기능을 추가할 수 있다면 다음을 제공합니다.

```text
--test-mode
--test-run-id <id>
--account-id <test-account>
--scenario login_match_play_reconnect
--server-url <staging-endpoint>
--disable-analytics
--disable-real-payment
--seed <deterministic-seed>
```

테스트 mode는 production build에 활성화하지 않거나, build profile·서명·서버 allowlist로 제한해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Windows 서버와 AWS 활용

### 512GB Windows 서버 10대

Windows 서버는 실제 모바일 기기보다 Android emulator와 Windows client 검증에 적합합니다.

```text
Windows Server 01~06
  └── Android Emulator worker

Windows Server 07~08
  └── Windows game client·Vagrant·Hyper-V

Windows Server 09
  └── Appium·Maestro·Game Loop runner

Windows Server 10
  └── protocol load generator·로그·결과 수집
```

서버별 수용량은 다음 순서로 측정합니다.

1. Android emulator 1개 기준선 측정.
2. 4개 병렬 실행.
3. 8개 병렬 실행.
4. CPU·GPU·RAM·disk I/O·ADB·network 포화 확인.
5. backend 지표와 client 지표의 시간축 비교.
6. 결과가 안정적일 때만 16개 이상으로 확장.

Vagrant는 Windows VM의 생성·프로비저닝·삭제를 자동화할 수 있지만, Android 실기기 farm이나 수천 virtual user의 부하 생성기로 사용하지 않습니다.

### AWS 사용 분리

- 실제 Android·iOS 기기: AWS Device Farm 또는 Firebase Test Lab.
- Android emulator scale-out: GPU·가상화 조건을 확인한 EC2 또는 기존 Windows 서버.
- backend protocol load: 별도 EC2 worker fleet.
- 결과 저장: S3 또는 기존 ELK/OpenSearch.
- 대시보드: Grafana에서 Zabbix·ELK·테스트 결과를 통합.

AWS 리소스는 테스트 시간에만 생성하고, 테스트 종료 후 자동 종료·삭제하여 비용을 제한합니다. 관리형 device cloud를 사용하면 물리 기기 구매·전원·USB·배터리 운영 부담을 줄일 수 있습니다.

### 자체 Android farm

```text
Linux 또는 Windows Host
        │ USB
        v
Powered USB Hub
        │
        ├── Android Device 01
        ├── Android Device 02
        ├── Android Device 03
        └── Android Device N
        │
        v
DeviceFarmer / ADB
        │
        v
Appium / Maestro / Custom Runner
        │
        v
Grafana / ELK / Test Report
```

실기기 farm에서는 서버 RAM보다 다음 요소가 먼저 병목이 됩니다.

- powered USB hub의 동시 전원·데이터 처리.
- USB host controller 수.
- 케이블과 포트의 연결 안정성.
- 기기별 고유 serial.
- 배터리·발열·화면 잠금.
- ADB 재연결과 기기 재부팅.
- 앱 설치·초기화·로그 수집.

### iOS 제약

iOS 실기기 자동화는 일반적으로 macOS·Xcode·XCTest toolchain이 필요합니다. Windows 서버만으로 자체 iOS farm을 구성하기보다 다음을 우선 검토합니다.

- AWS Device Farm.
- Firebase Test Lab.
- 상용 real device cloud.
- Mac mini·Mac Studio 기반 자체 host.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 권장 아키텍처

### 전체 구성

```text
┌───────────────────────────────────────────────────────────────────────┐
│                         Test Layers                                   │
├───────────────────────────────────────────────────────────────────────┤
│  Protocol Load  ────────>  Game Backend                               │
│  Android Emulator ──────>  Android Client                             │
│  Physical Device ───────>  Mobile Client                              │
│  UI / Game Loop ─────────>  Scenario Runner                           │
│  Metrics / Logs ─────────>  Grafana / ELK                             │
└───────────────────────────────────────────────────────────────────────┘
```

### 권장 조합

- backend 부하: k6·Locust·custom protocol runner.
- Android emulator: Windows Hyper-V 또는 Linux KVM 기반 emulator.
- Android 실기기: DeviceFarmer + Appium 또는 Maestro.
- iOS 실기기: AWS Device Farm 또는 Firebase Test Lab.
- Unity 게임 흐름: Firebase Game Loop 또는 Unity 내부 test hook.
- 일반 UI 흐름: Appium 또는 Maestro.
- 서버 지표: Zabbix·Grafana.
- 상세 로그·artifact: ELK/OpenSearch 또는 S3.

### 도구 선택 결과

| 목표                       | 1순위                      | 2순위                    |
|----------------------------|----------------------------|--------------------------|
| 실제 Android·iOS 기기      | Firebase Test Lab          | AWS Device Farm          |
| 자체 Android 기기 farm     | DeviceFarmer               | Appium·Maestro 조합      |
| Unity 게임 흐름            | Game Loop·custom test hook | 관리형 device cloud      |
| UI 회귀                    | Maestro                    | Appium                   |
| Android emulator 대량 실행 | Android Emulator           | Google container scripts |
| backend 수천 virtual users | k6·Locust                  | custom protocol runner   |
| Windows client 반복 실행   | Hyper-V·Vagrant            | 직접 process runner      |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 파일럿·검증·롤백

### 파일럿 순서

1. Android APK와 테스트 계정 10개를 준비합니다.
2. Firebase Test Lab에서 Game Loop 1개를 실행합니다.
3. 동일한 로그인·로비·재접속 흐름을 Appium 또는 Maestro로 작성합니다.
4. Windows 서버 1대에서 Android Emulator 4개를 실행합니다.
5. DeviceFarmer는 Android 실기기 4대 연결부터 검증합니다.
6. AWS Device Farm에서 Android·iOS 대표 모델을 실행합니다.
7. 실기기·에뮬레이터·관리형 device cloud의 결과를 비교합니다.
8. 결과에 따라 자체 farm과 관리형 서비스의 비율을 결정합니다.

### 검증 명령

AWS Device Farm의 기기 목록과 프로젝트는 read-only CLI로 확인합니다.

```bash
aws devicefarm list-devices \
  --region us-west-2 \
  --profile 01_re

aws devicefarm list-projects \
  --region us-west-2 \
  --profile 01_re
```

Android 기기·Appium·Docker·Hyper-V를 확인합니다.

```bash
adb devices -l
appium --version
docker version
```

Windows Server에서는 다음을 확인합니다.

```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
Get-VM
Get-VMHost | Select-Object LogicalProcessorCount, MemoryCapacity
```

Vagrant를 사용할 경우 VM 환경만 검증합니다.

```powershell
vagrant validate
vagrant status
vagrant up client-01 --provider=hyperv
vagrant halt client-01
```

### 중단 기준

다음 조건이면 테스트를 즉시 중단하거나 ramp-down합니다.

- 실제 사용자·실제 결제·실제 푸시 대상에 접근합니다.
- 개인정보·token·인증 정보가 로그·화면·artifact에 노출됩니다.
- 기기에서 반복적인 데이터 유실·중복 보상·세션 충돌이 발생합니다.
- USB hub·ADB·emulator farm이 회복되지 않고 연쇄적으로 실패합니다.
- backend 오류율·queue lag·DB connection이 승인 기준을 초과합니다.
- managed service의 비용·병렬성·보존 정책이 예상과 다릅니다.

### 롤백·정리

- Appium·Maestro·Game Loop runner를 중단합니다.
- emulator와 Windows VM을 종료합니다.
- DeviceFarmer에서 테스트 기기를 offline 또는 maintenance 상태로 전환합니다.
- 테스트 계정·token·session·queue·DB 데이터를 `test_run_id` 기준으로 정리합니다.
- AWS worker와 임시 리소스를 종료합니다.
- device cloud에 업로드한 APK·IPA·로그·동영상을 보존 정책에 따라 삭제합니다.
- 테스트 backend 설정과 allowlist를 baseline으로 복구합니다.

이번 문서 작성에서는 AWS 리소스 생성, Windows 서버 변경, 기기 연결, 패키지 설치를 수행하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 선택 기준과 미결 사항

### 최종 선택 기준

- 수천 virtual users의 backend 부하와 실제 모바일 기기 검증을 분리합니다.
- Android는 자체 farm과 관리형 cloud를 비용·운영 난이도로 비교합니다.
- iOS는 Windows 서버만으로 해결하려 하지 않고 관리형 서비스 또는 Mac host를 사용합니다.
- Unity 게임은 Appium selector만으로 검증하지 않고 Game Loop 또는 test hook을 설계합니다.
- 512GB Windows 서버는 RAM이 아니라 CPU·GPU·disk I/O·ADB·network 측정 후 수용량을 정합니다.
- Vagrant는 Windows VM lifecycle 자동화에만 사용합니다.

### 미결 사항

- [ ] 지원 Android·iOS 최소 버전과 대표 기기 matrix.
- [ ] Unity Game Loop 또는 test hook 제공 여부.
- [ ] 실제 Android 기기 구매·보관·전원·USB 운영 가능 여부.
- [ ] iOS 테스트를 위한 AWS·Firebase·상용 cloud 예산.
- [ ] Windows 서버별 GPU·CPU·Hyper-V·Docker 지원 상태.
- [ ] 테스트 계정·sandbox 결제·push mock 정책.
- [ ] 기기별 네트워크 지역과 backend endpoint 경로.
- [ ] 결과 artifact 보존 기간과 개인정보 마스킹 정책.
- [ ] backend CCU·RPS 테스트와 mobile client 테스트의 분리된 성공 기준.

### 참고 문서 연결

- [모바일 게임 사전 오픈 부하 테스트 계획서](mobile_game_load_testing_plan.md)
- [Android ADB 트러블슈팅](android_adb_troubleshooting.md)
- [Vagrant](../02_infrastructure/iac/vagrant.md)

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- DeviceFarmer: [github.com/DeviceFarmer/stf](https://github.com/DeviceFarmer/stf) — ★★★☆☆
- Appium Documentation: [appium.io/docs](https://appium.io/docs/en/latest/intro/) — ★★★☆☆
- Maestro: [github.com/mobile-dev-inc/Maestro](https://github.com/mobile-dev-inc/Maestro) — ★★★☆☆
- Android Emulator Container Scripts: [github.com/google/android-emulator-container-scripts](https://github.com/google/android-emulator-container-scripts) — ★★★☆☆
- AWS Device Farm: [AWS Developer Guide](https://docs.aws.amazon.com/devicefarm/latest/developerguide/welcome.html) — ★★★☆☆
- Firebase Test Lab: [firebase.google.com/docs/test-lab](https://firebase.google.com/docs/test-lab) — ★★★☆☆
- Firebase Game Loop: [firebase.google.com/docs/test-lab/game-loop](https://firebase.google.com/docs/test-lab/game-loop) — ★★★☆☆
- Vagrant Multi-Machine: [developer.hashicorp.com/vagrant/docs/multi-machine](https://developer.hashicorp.com/vagrant/docs/multi-machine) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-15

**마지막 업데이트**: 2026-09-15

© 2026 siasia86. Licensed under CC BY 4.0.
