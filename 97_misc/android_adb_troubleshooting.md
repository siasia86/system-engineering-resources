# Android ADB 트러블슈팅

앱 강제 종료, 크래시 분석 시 ADB(Android Debug Bridge) 로그를 활용하는 방법을 정리합니다.

## 목차

| 섹션                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| [1. ADB vs 루팅 안전성 비교](#1-adb-vs-루팅-안전성-비교) / [2. 사전 준비](#2-사전-준비)                   |
| [3. 로그 확인 명령어](#3-로그-확인-명령어) / [4. 크래시 원인별 조치](#4-크래시-원인별-조치)                |
| [5. 삼성 기기 전용 방법](#5-삼성-기기-전용-방법) / [6. 참고 자료](#6-참고-자료)                           |

---

## 1. ADB vs 루팅 안전성 비교

ADB logcat은 **읽기 전용 로그 조회**입니다. 시스템을 변조하지 않으므로 금융앱에 영향이 없습니다.

| 항목          | ADB logcat (로그 확인) | 루팅 (Magisk 등)      |
|---------------|------------------------|-----------------------|
| 시스템 변조   | ❌ 없음                | ✅ 시스템 파티션 변조 |
| Knox 트립     | ❌ 안 됨               | ✅ 비가역적 트립      |
| 금융앱 차단   | ❌ 영향 없음           | ✅ 차단됨             |
| 삼성페이      | ❌ 정상 동작           | ✅ 사용 불가          |
| OEM 잠금 해제 | 불필요                 | 필요                  |
| 워런티        | 유지                   | 상실                  |

🟡 금융앱(토스, 카카오뱅크, 삼성페이 등)이 차단되는 경우는 **OEM 부트로더 언락 + 루팅** 시에만 해당합니다. USB 디버깅 + logcat은 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사전 준비

### 개발자 옵션 활성화

```
설정 → 휴대전화 정보 → 소프트웨어 정보 → 빌드번호 7회 탭
설정 → 개발자 옵션 → USB 디버깅 활성화
```

### ADB 설치 (PC)

```bash
# Ubuntu/Debian
sudo apt-get install -y android-tools-adb

# macOS
brew install --cask android-platform-tools

# Windows — platform-tools zip 다운로드 후 PATH 추가
# https://developer.android.com/tools/releases/platform-tools
```

### 연결 확인

```bash
adb devices
# List of devices attached
# XXXXXXXXXX    device
```

🟡 "unauthorized" 상태 시 기기 화면에서 USB 디버깅 허용을 승인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 로그 확인 명령어

### 실시간 전체 로그

```bash
adb logcat
```

### 특정 앱 로그 필터링 (PID 기반)

```bash
# Clash of Clans
adb logcat --pid=$(adb shell pidof com.supercell.clashofclans)

# 패키지명 확인 방법
adb shell pm list packages | grep supercell
```

### 크래시/에러 로그만 필터링

```bash
# Error 레벨 이상 + 키워드 필터
adb logcat *:E | grep -i "clash\|supercell\|FATAL\|ANR"

# Fatal exception만
adb logcat -s AndroidRuntime:E
```

### 크래시 덤프 확인

```bash
# dropbox (시스템 크래시 기록)
adb shell dumpsys dropbox --print | grep -A 20 "crash"

# ANR (Application Not Responding)
adb shell dumpsys dropbox --print | grep -A 20 "anr"

# 최근 크래시 파일 목록
adb shell ls /data/anr/ 2>/dev/null
```

### 로그 파일로 저장

```bash
# 5분간 로그 수집 후 자동 종료
timeout 300 adb logcat > crash_log_$(date +%Y%m%d_%H%M%S).txt

# 크래시 발생 직전 버퍼 덤프 (현재 버퍼 내용만)
adb logcat -d > buffer_dump.txt
```

### 메모리 상태 확인

```bash
# 앱 메모리 사용량
adb shell dumpsys meminfo com.supercell.clashofclans

# 전체 메모리 요약
adb shell cat /proc/meminfo | head -5
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 크래시 원인별 조치

### 로그 키워드 → 원인 매핑

| 로그 키워드                         | 원인            | 조치                              |
|-------------------------------------|-----------------|-----------------------------------|
| `java.lang.OutOfMemoryError`        | 메모리 부족     | 백그라운드 앱 정리, RAM Plus 확인 |
| `ANR in com.supercell.clashofclans` | 앱 응답 없음    | 캐시 삭제, 저장공간 확인          |
| `FATAL EXCEPTION`                   | 앱 내부 크래시  | 앱 업데이트 또는 재설치           |
| `signal 11 (SIGSEGV)`               | 네이티브 크래시 | GPU 드라이버 문제, 기기 업데이트  |
| `EGL_BAD_ALLOC`                     | GPU 메모리 부족 | Game Booster 성능 모드 → 표준     |
| `Thermal throttling`                | 발열 쓰로틀링   | 기기 냉각 후 재시도, 케이스 제거  |

### 일반 조치 순서

| 순서 | 조치                                                        |
|------|-------------------------------------------------------------|
| 1    | 캐시 삭제: 설정 → 앱 → Clash of Clans → 저장공간 → 캐시     |
| 2    | Play 스토어 앱 업데이트 확인                                |
| 3    | 기기 소프트웨어 업데이트 (One UI 패치)                      |
| 4    | Game Booster 설정 확인 (성능 모드를 "표준"으로)             |
| 5    | 문제 지속 시 앱 삭제 → 재설치 (Supercell ID 연동 확인 필수) |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 삼성 기기 전용 방법

### Samsung Members 앱

```
Samsung Members → 도움받기 → 오류 관리
```

에러 로그 확인 및 Samsung에 리포트 전송이 가능합니다.

### Game Booster 로그

```
Game Booster → 게임 실행 중 → 하단 패널 → 성능 모니터링
```

FPS 드롭, 온도, 메모리 사용량을 실시간으로 확인할 수 있습니다.

### 버그 리포트 생성

```bash
# ADB로 전체 버그 리포트 생성 (시간 소요)
adb bugreport bugreport_$(date +%Y%m%d).zip
```

또는 기기에서:

```
설정 → 개발자 옵션 → 버그 보고서 가져오기
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 참고 자료

- Android Developers: [developer.android.com/tools/logcat](https://developer.android.com/tools/logcat) — ★★★☆☆
- ADB Command Reference: [developer.android.com/tools/adb](https://developer.android.com/tools/adb) — ★★★☆☆
- Samsung Knox Whitepaper: [samsungknox.com/whitepaper](https://docs.samsungknox.com/admin/whitepaper/) — ★★☆☆☆

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-07-16

**마지막 업데이트**: 2026-07-16

© 2026 siasia86. Licensed under CC BY 4.0.
