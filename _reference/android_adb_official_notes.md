---
name: android-adb-official-notes
description: Android ADB/logcat 공식 문서 기반 명령어, 옵션, Knox 안전성 정리.
tags:
  - android
  - adb
  - logcat
  - troubleshooting
  - mobile
last_checked: 2026-07-16
sources:
  - https://developer.android.com/tools/adb
  - https://developer.android.com/tools/logcat
  - https://android.googlesource.com/platform/system/logging/+/refs/heads/main/logcat/logcat.cpp
  - https://formulae.brew.sh/cask/android-platform-tools
  - https://docs.samsungknox.com/
---

# Android ADB 공식 문서 참조 노트

## 1. ADB 설치

| 플랫폼          | 설치 방법                                            | 비고                  |
|-----------------|------------------------------------------------------|-----------------------|
| Ubuntu/Debian   | `sudo apt-get install -y android-tools-adb`          | 24.04+: `adb` 패키지 |
| macOS (Homebrew)| `brew install --cask android-platform-tools`         | cask 필수             |
| Windows         | platform-tools zip 다운로드 후 PATH 추가             | SDK Manager 또는 독립 |
| 공식 다운로드   | https://developer.android.com/tools/releases/platform-tools | 전 플랫폼      |

- 현재 버전: **37.0.1** (formulae.brew.sh 확인, 2026-07-16)

## 2. logcat 핵심 옵션

| 옵션               | 설명                                      | 비고                    |
|--------------------|-------------------------------------------|-------------------------|
| `--pid=PID`        | 특정 PID 로그만 출력                      | Android 7.0+ 지원       |
| `-s TAG:PRIORITY`  | 특정 태그+우선순위 필터                   | `*:S`로 나머지 숨김     |
| `*:E`              | Error 이상만 출력                         | 쉘에서 따옴표 필요할 수 있음 |
| `-v FORMAT`        | 출력 포맷 지정                            | threadtime이 기본       |
| `-b BUFFER`        | 버퍼 지정 (main, system, crash, all 등)   | crash 버퍼 별도 존재    |
| `-d`               | 현재 버퍼 덤프 후 종료                    | 스크립트 자동화 용도    |
| `-c`               | 버퍼 클리어                               | 재현 전 초기화에 사용   |
| `--wrap`           | 줄바꿈 출력                               |                         |

### 우선순위 레벨

```
V (Verbose) < D (Debug) < I (Info) < W (Warning) < E (Error) < F (Fatal) < S (Silent)
```

### 출력 포맷

```
brief | long | process | raw | tag | thread | threadtime (default) | time
```

## 3. 크래시 분석 명령어

| 명령어                                     | 용도                        |
|--------------------------------------------|-----------------------------|
| `adb logcat -s AndroidRuntime:E`           | Java 크래시 (uncaught)      |
| `adb logcat -b crash`                      | 크래시 버퍼 직접 조회       |
| `adb shell dumpsys dropbox --print`        | 시스템 크래시/ANR 이력      |
| `adb shell dumpsys meminfo <package>`      | 앱 메모리 사용량            |
| `adb bugreport <filename>.zip`             | 전체 버그 리포트 (대용량)   |
| `adb shell pidof <package>`                | 실행 중 앱의 PID 확인       |

## 4. Samsung Knox 안전성

### Knox 트립 조건 (비가역)

| 행위                       | Knox 트립 | 워런티 | 금융앱 |
|----------------------------|-----------|--------|--------|
| 개발자 옵션 활성화         | ❌        | 유지   | 정상   |
| USB 디버깅 활성화          | ❌        | 유지   | 정상   |
| ADB logcat 실행            | ❌        | 유지   | 정상   |
| OEM 부트로더 언락          | ✅        | 상실   | 차단   |
| 커스텀 리커버리 설치       | ✅        | 상실   | 차단   |
| 루팅 (Magisk 등)           | ✅        | 상실   | 차단   |

- Knox Warranty Bit: eFuse 기반, 한 번 트립되면 복원 불가
- 금융앱 차단 메커니즘: SafetyNet/Play Integrity API → Knox Attestation 연동

### 검증 한계

- Samsung Knox 공식 문서 일부 페이지 접근 제한 (403)
- Knox 트립 조건은 커뮤니티 검증 + Samsung 공식 FAQ 기반 (직접 whitepaper 확인 불가)

## 5. Clash of Clans 정보

| 항목         | 값                              |
|--------------|---------------------------------|
| 패키지명     | `com.supercell.clashofclans`    |
| 개발사       | Supercell                       |
| Play 스토어  | 확인 완료 (2026-07-16)         |
| 엔진         | 자체 엔진 (C++ native + Java)  |

- 네이티브 크래시 시 `signal 11 (SIGSEGV)` 로그 출력
- GPU 관련 이슈 시 `Adreno`, `Mali`, `OpenGL`, `EGL` 키워드 확인

## 6. macOS Homebrew 패키지 확인 결과

- URL: https://formulae.brew.sh/cask/android-platform-tools
- 설치 명령: `brew install --cask android-platform-tools`
- 버전: 37.0.1
- 유형: **cask** (formula 아님, `--cask` 플래그 필수)

🟡 `brew install android-platform-tools` (cask 없이)도 자동 해석되는 경우 있으나, 명시적 `--cask` 권장.
