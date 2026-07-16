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
  - https://source.android.com/docs/core/architecture/bootloader/locking_unlocking
  - https://source.android.com/docs/security/features/verifiedboot/boot-flow
  - https://developer.android.com/google/play/integrity/verdicts
  - https://topjohnwu.github.io/Magisk/install.html
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

| 옵션              | 설명                                     | 비고                             |
|-------------------|------------------------------------------|----------------------------------|
| `--pid=PID`       | 특정 PID 로그만 출력                     | 소스 확인, 버전 요건 미확인      |
| `-s TAG:PRIORITY` | 특정 태그+우선순위 필터                  | `*:S`로 나머지 숨김              |
| `*:E`             | Error 이상만 출력                        | 쉘에서 따옴표 필요할 수 있음     |
| `-v FORMAT`       | 출력 포맷 지정                           | threadtime이 기본                |
| `-b BUFFER`       | 버퍼 지정 (main, system, crash, all 등)  | crash 버퍼 별도 존재             |
| `-d`              | 현재 버퍼 덤프 후 종료                   | 스크립트 자동화 용도             |
| `-c`              | 버퍼 클리어                              | 재현 전 초기화에 사용            |
| `--wrap`          | 버퍼 wrap 직전까지 대기 (폴링 효율화)   | 2시간 또는 wrap 시점             |

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

- Knox Warranty Bit: eFuse 기반 하드웨어 퓨즈, 한 번 트립되면 복원 불가
- Magisk 공식 문서 명시: "Installing Magisk WILL trip your Knox Warranty Bit, this action is not reversible in any way"

### OEM 부트로더 언락 상세

AOSP 공식 정의에 따르면, 부트로더 언락은 비공식 이미지 플래싱을 허용하는 절차입니다.

#### 언락 절차 (Samsung)

1. 설정 → 개발자 옵션 → OEM 잠금 해제 활성화 (`get_unlock_ability = 1`)
2. 전원 종료 후 Download Mode 진입 (기기별 키 조합)
3. 볼륨 업 길게 눌러 부트로더 언락 확인
4. **자동 공장 초기화** (전체 데이터 삭제)
5. 초기 설정 진행 → Developer options에서 OEM unlocking 회색 처리 확인

#### 언락 시 발생하는 변화

| 항목                   | 상태                                          |
|------------------------|-----------------------------------------------|
| Verified Boot 상태     | GREEN → ORANGE (unlocked)                     |
| Knox Warranty Bit      | 트립 (eFuse 소손, 비가역)                     |
| 데이터               | 공장 초기화 수행 (AOSP 보안 요구사항)         |
| RAM                    | 초기화 (이전 부트 잔여 데이터 제거)           |
| 비공식 이미지 플래싱 | 허용                                          |
| Download Mode 표시     | OEM Lock: OFF (U)                             |

#### KnoxGuard (RMM) 확인

부트로더 언락 전 Download Mode에서 KnoxGuard 상태를 반드시 확인합니다.

| KnoxGuard 상태          | 의미                             | 언락 가능 |
|-------------------------|----------------------------------|-----------|
| Checking / Completed    | 정상                             | ✅        |
| Broken                  | 정상                             | ✅        |
| Prenormal               | 임시 잠금 (168시간 후 해제)      | 🟡 대기   |
| Active / Locked         | 통신사/보험사 원격 잠금          | ❌        |

#### Verified Boot 상태 (AOSP 정의)

| 상태   | 조건                                          |
|--------|-----------------------------------------------|
| GREEN  | LOCKED + OEM root of trust 사용               |
| YELLOW | LOCKED + 사용자 설정 root of trust 사용       |
| ORANGE | UNLOCKED (부트로더 언락 상태)                 |
| RED    | dm-verity 손상 또는 유효한 OS 없음            |

### 루팅 (Magisk) 상세

#### Samsung 기기 루팅 절차

1. 부트로더 언락 완료 (위 절차)
2. 기기에 맞는 공식 펌웨어 다운로드 (SamFirm.NET, Frija 등)
3. AP tar 파일을 기기로 복사
4. Magisk 앱에서 "Select and Patch a File" → AP tar 선택
5. 패치된 tar 파일을 PC로 전송: `adb pull /sdcard/Download/magisk_patched_*.tar`
6. Download Mode 진입 → Odin으로 플래싱:
   - AP: `magisk_patched.tar`
   - BL, CP, CSC: 원본 펌웨어 (HOME_CSC 아님, 초기 설치이므로)
7. 자동 재부팅 → 공장 초기화 동의 → Magisk 앱 설치 확인

#### 일반 기기 루팅 절차

1. 부트로더 언락 완료
2. boot.img (또는 init_boot.img) 추출
3. Magisk 앱에서 이미지 패치
4. `fastboot flash boot magisk_patched_*.img` (또는 `init_boot`)
5. (선택) vbmeta 비활성화: `fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img`

🟡 vbmeta 비활성화 시 데이터 삭제 가능성이 있습니다.

#### 루팅 후 금융앱 차단 메커니즘

| 계층                    | 검증 내용                                            |
|-------------------------|------------------------------------------------------|
| Play Integrity API      | 기기 무결성 verdict 발행                             |
| MEETS_DEVICE_INTEGRITY  | 부트로더 잠금 + 인증된 OS (루팅 시 실패)             |
| MEETS_BASIC_INTEGRITY   | 기본 무결성 (부트로더 잠금 불문, 루팅 시 실패)       |
| Empty (verdict 없음)    | 루팅/후킹/에뮬레이터 탐지 → 금융앱 실행 거부        |
| Knox Attestation        | Samsung 전용, Knox Warranty Bit 확인                 |

- MEETS_DEVICE_INTEGRITY: Android 13+ 하드웨어 증명으로 부트로더 잠금 + 인증 OS 확인
- 루팅된 기기: verdict가 빈 값(empty)으로 반환 → 앱이 실행을 거부
- SafetyNet은 2024년 deprecate, Play Integrity API로 대체

#### 루팅 주의사항

- Samsung: stock boot/init_boot/recovery/vbmeta를 절대 복원하면 안 됩니다 (벽돌 위험)
- OS 업그레이드 시 항상 AP를 다시 패치해야 합니다 (stock AP 플래싱 금지)
- 패치된 이미지는 동일 기기에서만 사용합니다 (다른 기기 공유 금지)

### 검증 한계

- Samsung Knox 공식 문서 일부 페이지 접근 제한 (403)
- Knox 트립 조건: Magisk 공식 문서 명시 + 커뮤니티 검증 + Samsung FAQ 기반
- eFuse 구현 세부 사항: Samsung whitepaper 비공개로 직접 확인 불가
- Play Integrity verdict: Google 공식 문서 기반 (developer.android.com)

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
