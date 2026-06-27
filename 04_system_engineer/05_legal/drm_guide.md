# DRM (Digital Rights Management) 가이드

## 목차

| 섹션 |
|------|
| [1. DRM 개념](#1-drm-개념) / [2. DRM 기술 방식](#2-drm-기술-방식) / [3. DRM과 오픈소스](#3-drm과-오픈소스) |
| [4. DMCA와 법적 근거](#4-dmca와-법적-근거) / [5. 실무 적용](#5-실무-적용) |

---

## 1. DRM 개념

DRM(Digital Rights Management)은 디지털 콘텐츠의 **무단 복제, 배포, 수정을 기술적으로 제한**하는 수단입니다.
저작권자가 콘텐츠 사용 조건을 강제하기 위해 소프트웨어/하드웨어 수준에서 적용합니다.

### DRM의 목적

| 목적      | 설명                           |
|-----------|--------------------------------|
| 복제 방지 | 무단 복사 차단                 |
| 접근 제어 | 인증된 사용자/기기만 접근 허용 |
| 사용 제한 | 재생 횟수, 기간, 기기 수 제한  |
| 배포 추적 | 콘텐츠 유통 경로 추적          |

### DRM 적용 분야

| 분야       | 예시                             |
|------------|----------------------------------|
| 스트리밍   | Netflix Widevine, Apple FairPlay |
| 전자책     | Amazon Kindle, Adobe ADEPT       |
| 게임       | Steam, Denuvo                    |
| 소프트웨어 | 라이선스 키, 하드웨어 바인딩     |
| 음악/영상  | iTunes DRM (현재 폐지)           |

[⬆ 목차로 돌아가기](#목차)

---

## 2. DRM 기술 방식

### 암호화 기반

콘텐츠를 암호화하고 인증된 플레이어만 복호화 키를 받는 방식.

```
콘텐츠 암호화 → 라이선스 서버 → 인증 → 복호화 키 발급 → 재생
```

### 하드웨어 바인딩

특정 기기의 고유 식별자(UUID, MAC, TPM)와 라이선스를 묶는 방식.

```bash
# TPM 기반 하드웨어 바인딩 예시
# 기기 고유 키로 콘텐츠 키를 암호화
openssl rsautl -encrypt -inkey device_pubkey.pem -in content_key.bin -out encrypted_key.bin
```

### Trusted Execution Environment (TEE)

ARM TrustZone, Intel SGX 등 하드웨어 보안 영역에서 DRM 처리.
일반 OS에서 접근 불가한 영역에서 복호화 수행.

### Watermarking (워터마킹)

콘텐츠에 식별 정보를 삽입하여 유출 시 출처 추적.

| 방식              | 설명                                       |
|-------------------|--------------------------------------------|
| 가시적 워터마크   | 화면에 표시 (스트리밍 서비스 사용자 ID 등) |
| 비가시적 워터마크 | 콘텐츠 데이터에 숨겨진 식별자              |

[⬆ 목차로 돌아가기](#목차)

---

## 3. DRM과 오픈소스

### Tivoization — GPL v2의 허점

TiVo는 GPL v2 Linux 커널을 사용하면서 하드웨어 서명으로 수정된 소프트웨어 실행을 차단했다.
소스코드는 공개했지만 실제로 수정해서 실행할 수 없는 구조 — GPL의 자유 소프트웨어 취지를 우회한 사례.

```
GPL v2 준수 (소스 공개) + 하드웨어 서명 (수정 실행 차단)
→ 법적으로는 합법, 취지상으로는 위반
```

### GPL v3의 대응 — 설치 정보 제공 의무

GPL v3 Section 6은 소스코드뿐 아니라 **설치 정보(Installation Information)** 도 제공하도록 요구합니다.
수정된 소프트웨어를 실제로 설치·실행할 수 있는 서명 키, 인증 코드 등을 포함해야 한다.

```
GPL v3 = 소스코드 공개 + 설치 정보 제공
→ Tivoization 방지
```

> — [GPL v3 Section 6](https://www.gnu.org/licenses/gpl-3.0.html#section6)

### DRM과 라이선스 선택 기준

| 상황                   | 권장 라이선스    | 이유                          |
|------------------------|------------------|-------------------------------|
| DRM 적용 하드웨어 제품 | GPL v2 (only)    | v3의 설치 정보 의무 회피 가능 |
| 완전한 자유 소프트웨어 | GPL v3           | Tivoization 방지              |
| DRM 무관 라이브러리    | MIT / Apache 2.0 | 제약 없음                     |

🟡 Linux 커널은 "GPL v2 only"를 명시하여 GPL v3 적용을 의도적으로 배제하고 있다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. DMCA와 법적 근거

### DMCA (Digital Millennium Copyright Act, 1998)

미국 저작권법의 DRM 관련 조항. 두 가지 핵심 금지 사항:

| 조항                   | 내용                         |
|------------------------|------------------------------|
| **Anti-circumvention** | DRM 우회 기술 개발/배포 금지 |
| **Anti-trafficking**   | DRM 우회 도구 거래 금지      |

```
DRM 우회 → DMCA 위반 → 민사/형사 책임
(연구 목적 예외 조항 있으나 범위 제한적)
```

### 한국 저작권법

저작권법 제2조 제28호: 기술적 보호조치 정의.
저작권법 제104조의2: 기술적 보호조치 무력화 금지.

> — [한국 저작권법](https://www.law.go.kr/법령/저작권법)

### 주요 판례

| 사건                  | 연도 | 내용                               |
|-----------------------|------|------------------------------------|
| **DVD CCA v. Bunner** | 2001 | DeCSS(DVD 암호화 우회) 배포 금지   |
| **MGM v. Grokster**   | 2005 | P2P 서비스의 저작권 침해 방조 책임 |
| **Oracle v. Google**  | 2021 | Java API 사용의 공정 이용 인정     |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실무 적용

### 스트리밍 서비스 DRM 구현

```
Widevine (Google) — Chrome, Android
FairPlay (Apple)  — Safari, iOS
PlayReady (MS)    — Edge, Windows

EME (Encrypted Media Extensions) API로 브라우저에서 통합 처리
```

### 소프트웨어 라이선스 보호

```python
# 하드웨어 바인딩 라이선스 검증 예시
import hashlib, uuid

def get_machine_id():
    return str(uuid.getnode())  # MAC 주소 기반

def verify_license(license_key: str) -> bool:
    machine_id = get_machine_id()
    expected = hashlib.sha256(f"{machine_id}:SecureKey123".encode()).hexdigest()
    return license_key == expected
```

### DRM 없는 대안

| 방식          | 설명                       | 예시           |
|---------------|----------------------------|----------------|
| 오픈소스 공개 | DRM 대신 커뮤니티 신뢰     | Linux, Firefox |
| SaaS 모델     | 코드 배포 없이 서비스 제공 | GitHub, Figma  |
| 듀얼 라이선스 | 오픈소스 + 상업용 분리     | MySQL, Qt      |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- DMCA 원문: [copyright.gov/dmca](https://www.copyright.gov/dmca/) — ★★★☆☆
- FSF - GPL v3 DRM 조항: [gnu.org/licenses/rms-why-gplv3](https://www.gnu.org/licenses/rms-why-gplv3.html) — ★★★☆☆
- W3C EME 명세: [w3.org/TR/encrypted-media](https://www.w3.org/TR/encrypted-media/) — ★★★☆☆
- 한국 저작권법: [law.go.kr](https://www.law.go.kr/법령/저작권법) — ★★☆☆☆
- 라이선스 가이드 (작성 예정)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-30

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
