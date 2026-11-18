---
name: windows-code-signing-official-notes
description: Windows Authenticode 코드 서명 공식 사실 정리. SmartScreen 평판, UAC 표시, CA/B Forum 코드 서명 기본 요구사항(키 보관·유효 기간), Azure Artifact Signing, SignTool, 타임스탬프, 커널 드라이버 서명. windows_code_signing_guide.md 작성/검토 시 참조.
tags:
  - windows
  - code-signing
  - authenticode
  - smartscreen
  - security
last_checked: 2026-11-18
sources:
  - https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation
  - https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options
  - https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart
  - https://learn.microsoft.com/en-us/azure/artifact-signing/faq
  - https://azure.microsoft.com/en-us/pricing/details/artifact-signing/
  - https://cabforum.org/working-groups/code-signing/requirements/
  - https://cabforum.org/2025/11/17/ballot-csc-31-maximum-validity-reduction
  - https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool
  - https://learn.microsoft.com/en-us/windows/win32/seccrypto/time-stamping-authenticode-signatures
  - https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works
  - https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-reqs
  - https://www.microsoft.com/en-us/wdsi/filesubmission
---

# Windows 코드 서명 공식 참조 노트

## 1. SmartScreen 평판 (확인일: 2026-11-18)

출처: Microsoft Learn "SmartScreen reputation for Windows app developers"(`ms.date` 2026-05-04, 갱신 2026-08-17)

| 항목                           | 공식 내용                                                                                                                  |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| 평가 신호                      | 게시자 평판(서명 여부, 서명 인증서) + 파일 해시 평판                                                                       |
| 서명된 새 파일                 | 해시나 게시자 인증서가 충분한 긍정 평판을 쌓기 전까지 경고가 나올 수 있음                                                  |
| 서명 안 된 파일                | 새 버전마다 평판 0에서 시작. 같은 게시자 ID로 서명한 경우에만 이전 버전 평판이 이어짐                                      |
| 평판 쌓이는 기간               | 정해진 기준 없음. "몇 주, 넓은 사용자층의 수백 건 정상 설치"가 걸릴 수 있음                                                |
| 일반 사용자용 수동 제출        | 필요 없고 방법도 없음. 다운로드량으로 자연히 쌓임                                                                          |
| 기업 환경                      | IT 관리자는 Microsoft Security Intelligence 포털로 제출 가능                                                               |
| Microsoft Store                | MSIX는 Microsoft가 다시 서명해 SmartScreen 다운로드 경고 없음                                                              |
| Smart App Control (Windows 11) | SmartScreen보다 우선할 수 있음. 평판이 없는 서명 안 된 파일 실행 차단. 인터넷에서 받은 파일만이 아니라 모든 실행 파일 대상 |

### EV 인증서의 SmartScreen 효과

- 공식 문서: "EV certificates no longer bypass SmartScreen." EV 서명이 기본으로 긍정 평판을 주던 동작은 없어졌습니다.
- 바뀐 시기: Microsoft Learn "Code signing options" 문서에 "That behavior was removed in 2024"로 적혀 있습니다.
- 현재 취급: EV로 서명한 파일도 OV와 같은 평판 쌓기 과정을 거칩니다. SmartScreen만을 위해 EV 비용을 내는 것은 "no longer justified"라고 적혀 있습니다.

### 평판 관리 권장 사항 (공식 문서 목록)

1. 가능하면 Microsoft Store로 배포
2. 모든 릴리스에 서명
3. 서명 뒤 파일 수정 금지
4. 원치 않는 프로그램(PUA)으로 볼 수 있는 동작이 있는 파일에는 서명하지 않음. 인증서가 부정 평판을 얻을 수 있음
5. 서명 ID를 일관되게 유지. 인증서를 바꾸면 게시자 신호에 영향
6. 초기 사용자에게 SmartScreen 안내를 미리 알림

---

## 2. 서명 방식 비교 (확인일: 2026-11-18)

출처: Microsoft Learn "Code signing options for Windows app developers"(`ms.date` 2026-10-29, 갱신 2026-11-10)

| 방식                      | 비용(문서 표기) | 첫 다운로드 SmartScreen                            | 비고                                                           |
|---------------------------|-----------------|----------------------------------------------------|----------------------------------------------------------------|
| Microsoft Store (MSIX)    | 무료            | 경고 없음                                          | Microsoft가 다시 서명                                          |
| Microsoft Store (MSI/EXE) | CA 인증서 비용  | Store 설치 중 SmartScreen 없음(UAC는 나올 수 있음) | 설치 파일과 PE 파일을 신뢰 루트 프로그램 CA 인증서로 직접 서명 |
| Azure Artifact Signing    | 약 $9.99/월부터 | 평판 쌓일 때까지 경고                              | 하드웨어 토큰 불필요, CI 연동                                  |
| OV 인증서                 | $150~300/년     | Artifact Signing과 같음                            | 2023-06부터 하드웨어 키 보관 필수                              |
| EV 인증서                 | $400+/년        | OV와 같음 (2024년부터)                             | 드라이버 포털 계정에는 필요(6절)                               |
| 자체 서명                 | 무료            | 서명 없음과 같음                                   | 개발·사내 배포 전용                                            |
| 서명 없음                 | 무료            | "Windows가 PC를 보호했습니다" 경고                 | 기업 정책이 실행을 막을 수 있음                                |

🟡 비용은 Microsoft 문서의 대략적 표기이며 CA·상품·환율에 따라 다릅니다.

---

## 3. Azure Artifact Signing (구 Trusted Signing) (확인일: 2026-11-18)

출처: Azure Artifact Signing Quickstart(`ms.date` 2026-05-21, 갱신 2026-11-17), FAQ(갱신 2026-10-27), 가격 페이지

| 항목                          | 공식 내용                                                                                              |
|-------------------------------|--------------------------------------------------------------------------------------------------------|
| Public Trust 대상 지역 (법인) | 미국, 캐나다, EU, 영국, 호주, 뉴질랜드, 일본, **한국**, 싱가포르, 스위스, 노르웨이, 이스라엘           |
| Public Trust 대상 지역 (개인) | 미국, 캐나다                                                                                           |
| Azure 리전                    | Korea Central(`https://krc.codesigning.azure.net`) 포함 15개                                           |
| 구독 조건                     | 유료 구독(종량제·기업 계약). 무료·체험·후원 구독 불가                                                  |
| 신원 확인 처리 기간           | 1~30 영업일(추가 서류 요청 시 더 걸림), 서류 업로드 기회 3회                                           |
| 인증서 주체                   | CN·O는 검증된 법인명. 사용자 지정 불가                                                                 |
| 인증서 보관                   | 인증서·키는 서비스 안에만 있고 사용자에게 주지 않음                                                    |
| 보안 수준                     | FIPS 140-3 Level 3                                                                                     |
| EV 발급                       | 하지 않으며 계획도 없음                                                                                |
| 서명 도구                     | SignTool(`/dlib`), PowerShell, GitHub Actions, Azure DevOps 작업, SDK                                  |
| 타임스탬프 서버               | `http://timestamp.acs.microsoft.com`                                                                   |
| 요금제                        | Basic 월 5,000건·인증서 프로필 유형별 1개, Premium 월 100,000건·유형별 10개. 일할 계산 없음            |
| 가격                          | Microsoft Learn 표기 "Starts at $9.99/month"(Basic). Premium 금액은 가격 페이지에 표시되지 않아 미확인 |
| 커널 드라이버                 | 대상 아님. 커널 모드 서명은 Partner Center(6절)                                                        |

🟡 지역 목록이 문서마다 다릅니다. Windows 앱 개발자 문서("Code signing options", 2026-11-10 갱신)는 법인 대상을 미국·캐나다·EU·영국으로만 적고 있고, Azure Quickstart(2026-11-17 갱신)는 한국을 포함한 12개 지역을 적고 있습니다. 실제 신청 가능 여부는 Azure 포털 신원 확인 화면의 국가 목록에서 확인합니다.

"Set up signing integrations" 문서(갱신 2026-08-03)는 "Artifact Signing certificates have a three-day validity"라고 적고, 그래서 타임스탬프가 필수라고 안내합니다(5절).

| 연동 항목        | 공식 내용                                                                                                                                                                                                                                                                                                                   |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SignTool 최소 판 | Windows SDK SignTool 10.0.2261.755 이상(20348 SDK는 dlib 미지원)                                                                                                                                                                                                                                                            |
| 필요 구성 요소   | .NET 8 Runtime, Visual C++ 재배포 패키지, Artifact Signing dlib (`Microsoft.ArtifactSigning.Client` NuGet)                                                                                                                                                                                                                  |
| 일괄 설치        | `winget install -e --id Microsoft.Azure.ArtifactSigningClientTools`                                                                                                                                                                                                                                                         |
| dlib 파일        | `Azure.CodeSigning.Dlib.dll` (SignTool과 같은 x64·x86 판을 사용)                                                                                                                                                                                                                                                            |
| 메타데이터 JSON  | `Endpoint`, `CodeSigningAccountName`, `CertificateProfileName`, 선택 `CorrelationId`, `ExcludeCredentials`                                                                                                                                                                                                                  |
| Endpoint         | 계정·인증서 프로필을 만든 리전의 주소와 같아야 함. 다르면 403과 `SignerSign()` 실패                                                                                                                                                                                                                                         |
| 인증             | `DefaultAzureCredential` 순서대로 시도                                                                                                                                                                                                                                                                                      |
| 필요 역할        | Artifact Signing Certificate Profile Signer                                                                                                                                                                                                                                                                                 |
| GitHub Actions   | `azure/artifact-signing-action` 최신 v2.0.0(2026-05-14). 필수 입력 `endpoint`, `certificate-profile-name`. 주요 입력 `signing-account-name`, `files-folder`, `files-folder-filter`, `file-digest`(기본 SHA256), `timestamp-rfc3161`(기본 `http://timestamp.acs.microsoft.com`), `timestamp-digest`. README는 OIDC 인증 권장 |

---

## 4. CA/B Forum 코드 서명 기본 요구사항 (확인일: 2026-11-18)

출처: CA/Browser Forum Code Signing Baseline Requirements v3.11.0(2026-06-16), Ballot CSC-31

| 조항      | 시행일     | 내용                                                                                              |
|-----------|------------|---------------------------------------------------------------------------------------------------|
| 6.2.7.4.2 | 2023-06-01 | 가입자 개인 키는 적합한 하드웨어 암호 모듈에서 생성·저장·사용                                     |
| 6.2.7.4   | 2021-06-01 | 서명 서비스의 개인 키는 FIPS 140-2 Level 2 이상(또는 동등) 모듈로 보호                            |
| 6.2.7.2   | 2025-04-15 | 타임스탬프 기관은 Time Stamping EKU가 있는 루트·하위 CA 키를 오프라인 하드웨어 모듈로 보호        |
| 6.3.2     | 2026-03-01 | 이날 이후 발급되는 코드 서명 인증서의 유효 기간은 460일을 넘을 수 없음 (CSC-31, 이전 최대 39개월) |
| 4.9.1     | 2024-04-15 | 폐기 사유 갱신 (키 유출, 의심 코드 등)                                                            |

- 하드웨어 모듈 형태: USB 토큰, 사내 HSM, 클라우드 HSM, 서명 서비스. Microsoft 문서도 "As of June 2023 ... private keys for OV certificates to be stored on a hardware security module (HSM) or hardware token"으로 적고 있습니다.
- `.pfx` 파일로 개인 키를 내려받아 빌드 서버에 두는 방식은 2023-06 이후 새로 발급하는 공개 신뢰 인증서로는 할 수 없습니다.

---

## 5. SignTool과 타임스탬프 (확인일: 2026-11-18)

출처: Microsoft Learn "SignTool"(갱신 2026-10-05), "Time Stamping Authenticode Signatures"(`ms.date` 2026-07-16)

| 항목          | 공식 내용                                                                                                 |
|---------------|-----------------------------------------------------------------------------------------------------------|
| 배포          | Windows SDK의 `\Bin` 폴더. 예: `C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe` |
| `/fd`         | 파일 다이제스트 알고리즘. 서명 시 지정하지 않으면 오류(SDK 20236 이후). SHA256 권장                       |
| `/tr` + `/td` | RFC 3161 타임스탬프 서버와 다이제스트. `/td` 없으면 오류                                                  |
| `/t`          | 옛 Authenticode 타임스탬프 프로토콜. `/tr`과 함께 쓸 수 없음                                              |
| `/a`          | 조건에 맞는 인증서 중 유효 기간이 가장 긴 것을 자동 선택                                                  |
| `/sha1`       | 인증서 SHA1 지문으로 선택 (여러 인증서가 있을 때)                                                         |
| `/dlib`       | `AuthenticodeDigestSign`을 구현한 DLL로 다이제스트 서명 (클라우드 HSM·Artifact Signing 연동)              |
| `verify /pa`  | 기본 인증 확인 정책 사용. 없으면 드라이버 정책으로 확인                                                   |
| `verify /tw`  | 타임스탬프가 없으면 경고                                                                                  |
| `verify /all` | 여러 서명이 있을 때 모두 확인                                                                             |
| 종료 코드     | 0 성공, 1 실패, 2 경고와 함께 완료                                                                        |

### 타임스탬프

- 공식 문서: "Always time-stamp your Authenticode signatures. Without a time stamp, the signature becomes invalid when the signing certificate expires, and Windows will treat the binary as unsigned."
- 타임스탬프가 있으면 서명 시점에 인증서가 유효했음을 증명하므로, 인증서가 만료되거나 폐기된 뒤에도 서명을 확인할 수 있습니다.
- 권장 설정: `/fd SHA256`, `/tr <RFC 3161 URL> /td SHA256`. SHA-1 단독 서명은 새 릴리스에 쓰지 않습니다. Windows 7 SP1 이상만 대상이면 SHA-256 단독 서명으로 충분합니다.
- SHA384 이상 검증은 Windows 11 또는 2022년 11월 업데이트를 받은 Windows 10이 필요합니다.

---

## 6. UAC 표시와 커널 드라이버 서명 (확인일: 2026-11-18)

### UAC 권한 상승 창

출처: Microsoft Learn "How User Account Control works"(`ms.date` 2026-04-23)

| 분류                                       | 배경색 |
|--------------------------------------------|--------|
| Windows 관리 앱, 확인된 게시자로 서명된 앱 | 회색   |
| 서명 안 된 앱, 서명됐지만 신뢰되지 않는 앱 | 노란색 |

서명된 앱은 확인된 게시자 이름이 표시되고, 서명이 없으면 게시자가 "알 수 없음"으로 표시됩니다.

### 커널 드라이버 (안티치트 등)

출처: Microsoft Learn "Driver Code Signing Requirements"(`ms.date` 2025-05-29)

- Hardware Dev Center 대시보드에 attestation 서명이나 WHCP 인증을 제출하려면 대시보드 계정에 EV 인증서가 최소 1개 연결되어 있어야 합니다.
- 개별 제출물은 EV 서명을 강하게 권장하지만, 계정에 등록된 Authenticode 인증서로 서명해도 됩니다.
- 모든 인증서는 SHA-2이고 `/fd sha256`으로 서명합니다.
- 커널 모드 서명은 Artifact Signing이 아니라 Partner Center에서 합니다(Artifact Signing FAQ).

---

## 7. 오탐 신고 (확인일: 2026-11-18)

| 대상                    | 방법                                                                                            |
|-------------------------|-------------------------------------------------------------------------------------------------|
| Microsoft Defender 오탐 | Microsoft Security Intelligence 파일 제출 `https://www.microsoft.com/en-us/wdsi/filesubmission` |
| 서명 인증서 오용 신고   | 같은 제출 주소(Artifact Signing FAQ)                                                            |
| 다른 백신               | 각 백신사의 오탐 신고 창구 (이 노트에서 확인하지 않음)                                          |

---

## 검증 기록

| 회차 | 날짜       | 방법                                                                                               |
|------|------------|----------------------------------------------------------------------------------------------------|
| 1    | 2026-11-18 | 2차 자료 검색으로 쟁점(EV 효과, 키 보관, 460일, Artifact Signing 지역) 수집                        |
| 2    | 2026-11-18 | 1~7절 각 항목을 표에 적은 1차 자료 원문과 대조. Artifact Signing 지역은 문서 간 차이를 그대로 기록 |
