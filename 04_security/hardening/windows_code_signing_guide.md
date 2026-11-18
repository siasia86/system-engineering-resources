# Windows 실행 파일 코드 서명 가이드 (게임 배포)
<!-- reference: _reference/windows_code_signing_official_notes.md -->

게임 클라이언트·런처·설치 파일을 Windows 사용자에게 배포할 때 필요한 Authenticode 코드 서명을 정리합니다. 인증서 선택, 서명 대상, 빌드 파이프라인, 키 관리, SmartScreen 평판, 백신 오탐 대응까지 다룹니다. 정책 사실과 출처는 [Windows 코드 서명 공식 참조 노트](../../_reference/windows_code_signing_official_notes.md)에 있습니다.

## 목차

| 섹션                                                                                                                                           |
|------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 왜 서명하는가](#1-왜-서명하는가) / [2. 동작 원리](#2-동작-원리) / [3. 서명 방식 선택](#3-서명-방식-선택)                                   |
| [4. 무엇에 서명하는가](#4-무엇에-서명하는가) / [5. 빌드 파이프라인과 서명 순서](#5-빌드-파이프라인과-서명-순서) / [6. 서명 명령](#6-서명-명령) |
| [7. CI 자동화](#7-ci-자동화) / [8. 인증서와 키 운영](#8-인증서와-키-운영) / [9. SmartScreen 평판 쌓기](#9-smartscreen-평판-쌓기)               |
| [10. 백신 오탐 대응](#10-백신-오탐-대응) / [11. 릴리스 점검표](#11-릴리스-점검표) / [12. 트러블슈팅](#12-트러블슈팅)                           |

---

## 1. 왜 서명하는가

서명하지 않은 `.exe`를 배포하면 사용자는 실행 전에 세 단계의 경고를 만납니다.

| 증상             | 화면                                              | 사용자 영향                                                          |
|------------------|---------------------------------------------------|----------------------------------------------------------------------|
| SmartScreen 차단 | "Windows가 PC를 보호했습니다" / 알 수 없는 게시자 | "추가 정보 → 실행"을 눌러야 실행됨. 많은 사용자가 여기서 설치를 포기 |
| UAC 권한 상승 창 | 노란색 배경, 게시자 "알 수 없음"                  | 설치·패치처럼 관리자 권한이 필요한 단계에서 불신을 줌                |
| 백신 오탐        | 격리·삭제, "위험한 파일" 알림                     | 게임이 실행되지 않거나 패치 파일이 사라짐. 고객 문의 증가            |

UAC 창 색은 Microsoft 문서 기준으로, 확인된 게시자로 서명된 앱은 회색, 서명이 없거나 신뢰되지 않은 앱은 노란색입니다.

### 서명이 해결하는 것과 못 하는 것

| 항목                         | 서명 효과                                                                                                                                                                              |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| UAC 게시자 표시              | 즉시 해결. 회사 법인명이 "확인된 게시자"로 표시되고 창이 회색으로 바뀜                                                                                                                 |
| 파일 변조 감지               | 즉시 해결. 서명 뒤 1바이트라도 바뀌면 서명이 깨짐                                                                                                                                      |
| SmartScreen 경고             | **즉시 해결되지 않음.** 서명된 파일도 평판이 쌓일 때까지 "인식할 수 없는 앱" 경고가 나올 수 있음. 다만 게시자 이름이 표시되고, 같은 인증서로 계속 서명하면 평판이 다음 버전으로 이어짐 |
| 백신 오탐                    | 확률을 낮추는 요인 중 하나. 서명만으로 오탐이 없어지지는 않음                                                                                                                          |
| Windows 11 Smart App Control | 서명이 없고 평판도 없는 파일은 차단되므로, 이 기능이 켜진 PC에서는 서명이 사실상 필수                                                                                                  |

🟡 EV 인증서를 사면 SmartScreen 경고가 바로 사라진다는 안내가 아직 많지만, 2024년에 없어진 동작입니다. 현재 Microsoft 문서는 EV도 OV와 같은 평판 쌓기 과정을 거친다고 적고 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 동작 원리

### Authenticode 서명 구조

```
signtool sign
    |
    | (1) hash file (SHA-256)
    | (2) sign hash with private key  <---- token / HSM / signing service
    | (3) send signature to TSA, attach timestamp countersignature
    v
+------------------------------------------------+
|  game.exe                                      |
|  ┌──────────────────────────────────────────┐  |
|  │  PE body (code, resources)               │  |
|  ├──────────────────────────────────────────┤  |
|  │  Security directory (PKCS #7 SignedData) │  |
|  │   - file hash + signature                │  |
|  │   - signer cert + intermediate CA cert   │  |
|  │   - timestamp countersignature           │  |
|  └──────────────────────────────────────────┘  |
+------------------------------------------------+
```

| 단계·영역          | 설명                                                                            |
|--------------------|---------------------------------------------------------------------------------|
| (1) 해시 계산      | 서명이 들어갈 영역을 뺀 파일 내용의 SHA-256 해시                                |
| (2) 해시 서명      | 개인 키로 해시에 서명. 키는 하드웨어 토큰·HSM·서명 서비스 안에서만 사용         |
| (3) 타임스탬프     | 타임스탬프 기관(TSA)이 서명값에 "이 시각에 존재했음"을 서명해 덧붙임            |
| Security directory | PE 파일 끝의 서명 영역. 서명, 서명 인증서와 중간 CA 인증서, 타임스탬프가 들어감 |

Windows는 실행할 때 해시를 다시 계산해 서명과 비교하고, 인증서가 Microsoft 신뢰 루트 프로그램의 CA로 이어지는지 확인합니다.

### 타임스탬프가 필수인 이유

| 상황                          | 타임스탬프 있음                             | 타임스탬프 없음                       |
|-------------------------------|---------------------------------------------|---------------------------------------|
| 인증서 유효 기간 중           | 유효                                        | 유효                                  |
| 인증서 만료 후                | 유효 (서명 시점에 인증서가 유효했음을 증명) | **서명 무효, 서명 안 된 파일로 취급** |
| Artifact Signing (인증서 3일) | 유효                                        | 3일 뒤 무효                           |

게임은 몇 년씩 같은 클라이언트 파일을 배포하므로, 타임스탬프 없이 서명하면 인증서 만료일에 모든 배포 파일이 한꺼번에 "서명 안 됨"으로 바뀝니다.

### SmartScreen 판단

SmartScreen은 두 신호로 판단합니다.

1. **게시자 평판:** 서명했는지, 그 인증서(게시자 ID)가 알려진 게시자인지
2. **파일 해시 평판:** 이 파일이 악성 징후 없이 충분히 내려받아졌는지

새 게임을 출시하면 두 신호 모두 0에서 시작하므로 경고가 나옵니다. 같은 인증서로 계속 서명하면 게시자 평판이 쌓여, 이후 패치 파일은 해시 평판이 없어도 경고가 줄어들 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 서명 방식 선택

### 비교

| 방식                     | 대략 비용                       | 키 보관                            | 장점                                                      | 단점                                                                      |
|--------------------------|---------------------------------|------------------------------------|-----------------------------------------------------------|---------------------------------------------------------------------------|
| Azure Artifact Signing   | 월 $9.99부터 (Basic 월 5,000건) | Microsoft HSM (FIPS 140-3 Level 3) | 토큰 없음, CI 연동 쉬움, 인증서 3일 주기로 유출 피해 작음 | 지역 조건, Azure 유료 구독 필요, 법인명 고정, EV 없음, 커널 드라이버 불가 |
| OV 인증서 + 클라우드 HSM | 연 $150~300 + HSM 비용          | CA 또는 클라우드 HSM               | CA 선택 자유, CI 연동 가능                                | HSM 연동 설정 필요                                                        |
| OV 인증서 + USB 토큰     | 연 $150~300                     | USB 토큰                           | 단순, 소량 서명에 적합                                    | 토큰이 꽂힌 PC에서만 서명. CI·원격 빌드에 불리, 분실·고장 위험            |
| EV 인증서                | 연 $400+                        | 토큰 또는 HSM                      | 커널 드라이버 제출 계정에 필요                            | SmartScreen 효과는 OV와 같음                                              |
| Microsoft Store (MSIX)   | 무료                            | Microsoft                          | SmartScreen 경고 없음                                     | 게임 구조·안티치트·런처와 맞지 않는 경우가 많음                           |

비용은 Microsoft 문서의 대략적 표기이며 CA·환율·상품에 따라 다릅니다.

### 한국 법인 게임사 기준 선택 흐름

```
자체 커널 드라이버(안티치트 등)를 직접 제출하는가?
  ├─ 예 → EV 인증서 필요 (Hardware Dev Center 계정)
  │        + 사용자 모드 파일은 아래 흐름으로 별도 선택 가능
  └─ 아니오
       |
       v
Azure 포털 신원 확인 국가 목록에 한국이 있는가? (Public Trust, 법인)
  ├─ 예 → Azure Artifact Signing (권장)
  └─ 아니오 → OV 인증서 + 클라우드 HSM (CI 서명)
              또는 OV 인증서 + USB 토큰 (소규모, 수동 서명)
```

🟡 Artifact Signing의 대상 지역은 Microsoft 문서끼리 다릅니다. Azure Quickstart(2026-11-17 갱신)는 한국을 포함한 12개 지역을 적고 있지만, Windows 앱 개발자 문서(2026-11-10 갱신)는 미국·캐나다·EU·영국만 적고 있습니다. 신청 전에 Azure 포털의 신원 확인 화면에서 국가 목록을 확인합니다.

### 결정 전 확인할 것

| 항목                 | 확인 내용                                                                                                   |
|----------------------|-------------------------------------------------------------------------------------------------------------|
| 서명 주체 법인명     | 인증서의 CN·O는 등기상 법인명. 게임 브랜드명이 아니라 회사명이 표시됨                                       |
| 퍼블리셔·개발사 관계 | 퍼블리싱 계약이면 누구 이름으로 서명할지 계약서와 맞춤. 한 번 정하면 바꾸기 어려움(평판이 게시자 ID에 쌓임) |
| 서명 건수            | 빌드마다 서명하는 파일 수 × 하루 빌드 수. Artifact Signing Basic은 월 5,000건                               |
| 안티치트             | 상용 안티치트는 공급사가 드라이버를 서명해 제공하는지 계약에서 확인                                         |
| 배포 경로            | 웹 다운로드 설치 파일, 자체 런처, Steam 등 플랫폼별로 서명 요구가 다름                                      |

[⬆ 목차로 돌아가기](#목차)

## 4. 무엇에 서명하는가

원칙은 "우리가 만들어 배포하는 실행 가능한 파일은 모두 서명"입니다.

| 대상                                                     | 서명       | 비고                                                                  |
|----------------------------------------------------------|------------|-----------------------------------------------------------------------|
| 설치 파일 (`Setup.exe`, `.msi`)                          | 필수       | SmartScreen이 가장 먼저 보는 파일                                     |
| 제거 프로그램 (`unins000.exe` 등)                        | 필수       | 설치 도구가 빌드 중 생성하므로 도구 설정으로 서명                     |
| 런처                                                     | 필수       | 사용자가 매일 실행, 관리자 권한 요청이 잦음                           |
| 업데이터·패처                                            | 필수       | 관리자 권한으로 파일을 바꾸므로 변조 대상이 되기 쉬움                 |
| 게임 본체 `.exe`                                         | 필수       |                                                                       |
| 자체 제작 `.dll`                                         | 필수       | 백신 오탐 대상이 되기 쉬움                                            |
| 크래시 리포터, 보조 도구                                 | 필수       | 자주 잊는 파일                                                        |
| 안티치트 사용자 모드 모듈                                | 필수       | 자체 개발 시                                                          |
| 커널 드라이버 (`.sys`, `.cat`)                           | 필수       | EV 계정으로 Microsoft 서명 절차(Hardware Dev Center)를 거쳐야 함      |
| PowerShell 스크립트 (`.ps1`)                             | 배포한다면 | 실행 정책이 서명을 요구할 수 있음                                     |
| 타사 재배포 파일 (VC++ 재배포 패키지, 엔진·미들웨어 DLL) | 하지 않음  | 공급사 서명을 그대로 둠. 서명이 없는 타사 파일은 공급사에 서명본 요청 |

### 설치 도구별 제거 프로그램 서명

| 도구       | 방법                                                                                          |
|------------|-----------------------------------------------------------------------------------------------|
| Inno Setup | `[Setup]`의 `SignTool` 지시어로 서명 명령을 지정하면 설치 파일과 제거 프로그램을 빌드 중 서명 |
| NSIS       | `!finalize`(설치 파일), `!uninstfinalize`(제거 프로그램, 3.08 이상)에 서명 명령 지정          |
| WiX (MSI)  | 빌드 뒤 `.msi`와 포함된 `.exe`·`.dll`을 서명. 외부 `.cab`을 쓰면 `.cab`도 서명                |

🟡 설치 도구 지시어는 각 도구 공식 문서에서 사용하는 판의 문법을 확인합니다(이 문서에서 원문 대조하지 않음).

[⬆ 목차로 돌아가기](#목차)

## 5. 빌드 파이프라인과 서명 순서

서명은 **파일 내용이 마지막으로 바뀐 뒤**에 해야 합니다. 서명 뒤에 패커·프로텍터·리소스 수정·압축 해제 후 재구성이 일어나면 서명이 깨집니다.

```
1. 컴파일·링크
      |
2. 후처리 (실행 파일 프로텍터, 난독화, 리소스·버전 정보 삽입)
      |
3. 내부 바이너리 서명 (game.exe, launcher.exe, *.dll)
      |
4. 서명 검증 (signtool verify /pa)
      |
5. 패키징 (설치 파일 생성, 패치 파일·매니페스트 생성)
      |
6. 설치 파일·제거 프로그램 서명
      |
7. 최종 검증 (설치 파일 + 설치 후 파일 전체)
      |
8. 배포 (CDN, 런처 패치 서버, 플랫폼 업로드)
```

### 패치 시스템 주의점

| 방식                           | 서명 관련 주의                                                                        |
|--------------------------------|---------------------------------------------------------------------------------------|
| 파일 단위 교체                 | 서명된 파일을 그대로 배포하면 문제 없음                                               |
| 바이너리 차등 패치 (bsdiff 등) | 패치 적용 결과가 서명된 최종 파일과 바이트 단위로 같아야 함. 패치 후 해시 검증을 넣음 |
| 실행 중 자체 수정              | 디스크의 실행 파일을 고쳐 쓰면 서명이 깨짐. 설정·데이터는 별도 파일로 분리            |

런처가 패치 후 `WinVerifyTrust`나 해시 매니페스트로 파일을 확인하면, 손상·변조된 파일을 실행 전에 찾을 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 서명 명령

`signtool.exe`는 Windows SDK에 들어 있습니다(예: `C:\Program Files (x86)\Windows Kits\10\bin\<SDK 판>\x64\signtool.exe`). 아래 명령은 PowerShell·cmd 기준입니다.

### 공통 옵션

| 옵션           | 의미                                   | 권장                  |
|----------------|----------------------------------------|-----------------------|
| `/fd SHA256`   | 파일 다이제스트 알고리즘               | 필수 (없으면 오류)    |
| `/tr <URL>`    | RFC 3161 타임스탬프 서버               | 필수                  |
| `/td SHA256`   | 타임스탬프 다이제스트                  | `/tr`과 함께 필수     |
| `/d "<설명>"`  | 서명 설명 (UAC 창 등에 표시될 수 있음) | 게임명                |
| `/du <URL>`    | 설명 URL                               | 공식 홈페이지         |
| `/sha1 <지문>` | 사용할 인증서를 지문으로 지정          | 인증서가 여러 개일 때 |
| `/v`           | 자세한 출력                            | CI 로그용             |

`/t`(옛 타임스탬프 프로토콜)는 쓰지 않고 `/tr`을 씁니다. 타임스탬프 서버 주소는 인증서를 산 CA가 안내하는 주소를 씁니다.

### USB 토큰·인증서 저장소의 인증서로 서명

토큰 드라이버를 설치하면 인증서가 Windows 인증서 저장소(`My`)에 보입니다. 지문으로 지정하면 엉뚱한 인증서가 선택되지 않습니다.

```powershell
# 인증서 지문 확인
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
    Select-Object Subject, Thumbprint, NotAfter

# 서명 (지문과 타임스탬프 주소는 실제 값으로)
signtool sign /sha1 0123456789ABCDEF0123456789ABCDEF01234567 `
    /fd SHA256 /tr http://timestamp.example-ca.com /td SHA256 `
    /d "My Game" /du https://www.example.com `
    .\build\MyGame.exe .\build\Launcher.exe .\build\GameCore.dll
```

토큰은 서명할 때 PIN을 묻습니다. 무인 CI에서 PIN 입력 창이 뜨면 빌드가 멈추므로, CI 서명은 클라우드 HSM이나 Artifact Signing을 권장합니다.

### Azure Artifact Signing으로 서명

준비물: SignTool 10.0.2261.755 이상, .NET 8 Runtime, VC++ 재배포 패키지, Artifact Signing dlib. 한 번에 설치하려면:

```powershell
winget install -e --id Microsoft.Azure.ArtifactSigningClientTools
```

`metadata.json` (계정을 만든 리전의 Endpoint를 씀. 예: Korea Central):

```json
{
  "Endpoint": "https://krc.codesigning.azure.net",
  "CodeSigningAccountName": "<Artifact Signing 계정 이름>",
  "CertificateProfileName": "<인증서 프로필 이름>",
  "CorrelationId": "<빌드 번호 등, 선택>"
}
```

```powershell
& "<SDK bin 경로>\x64\signtool.exe" sign /v /fd SHA256 `
    /tr "http://timestamp.acs.microsoft.com" /td SHA256 `
    /dlib "<dlib 경로>\x64\Azure.CodeSigning.Dlib.dll" `
    /dmdf "<경로>\metadata.json" `
    .\build\MyGame.exe
```

- x64 SignTool에는 x64 dlib, x86 SignTool에는 x86 dlib을 짝지어 씁니다.
- Endpoint가 계정 리전과 다르면 403 오류와 `SignerSign()` 실패가 납니다.
- 서명하는 계정(사용자·관리 ID·서비스 주체)에는 "Artifact Signing Certificate Profile Signer" 역할이 있어야 합니다.

### 검증

```powershell
# 서명·체인·타임스탬프 확인. /tw: 타임스탬프 없으면 경고
signtool verify /pa /v /tw .\build\MyGame.exe

# 폴더 전체 점검: 서명 상태가 Valid가 아닌 파일 찾기
Get-ChildItem .\build -Recurse -Include *.exe,*.dll,*.sys |
    Get-AuthenticodeSignature |
    Where-Object Status -ne 'Valid' |
    Select-Object Path, Status, StatusMessage
```

`signtool verify /pa`를 빼면 드라이버 확인 정책으로 검사해 일반 프로그램이 실패로 나올 수 있습니다. 종료 코드는 0 성공, 1 실패, 2 경고입니다.

[⬆ 목차로 돌아가기](#목차)

## 7. CI 자동화

### GitHub Actions + Artifact Signing

`azure/artifact-signing-action`(v2) 예입니다. Azure 인증은 비밀번호 대신 OIDC(페더레이션 자격 증명)를 권장합니다.

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  sign:
    runs-on: windows-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: game-build
          path: build

      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Sign binaries
        uses: azure/artifact-signing-action@v2
        with:
          endpoint: https://krc.codesigning.azure.net/
          signing-account-name: ${{ vars.SIGNING_ACCOUNT }}
          certificate-profile-name: ${{ vars.SIGNING_PROFILE }}
          files-folder: ${{ github.workspace }}\build
          files-folder-filter: exe,dll
          files-folder-recurse: true
          file-digest: SHA256
          timestamp-rfc3161: http://timestamp.acs.microsoft.com
          timestamp-digest: SHA256

      - name: Verify
        shell: pwsh
        run: |
          $bad = Get-ChildItem build -Recurse -Include *.exe,*.dll |
                 Get-AuthenticodeSignature | Where-Object Status -ne 'Valid'
          if ($bad) { $bad | Format-Table Path, Status; exit 1 }
```

🟡 `azure/login`과의 조합, `files-folder-recurse` 값 형식은 Action 저장소의 OIDC 안내 문서에서 사용하는 판에 맞춰 확인합니다. 위 예는 Action README의 기본 예에 검증 단계를 더한 것이며 실제 실행은 하지 않았습니다.

### 파이프라인 설계 원칙

| 원칙                                | 이유                                                                     |
|-------------------------------------|--------------------------------------------------------------------------|
| 서명은 별도 작업(job)·별도 권한으로 | 빌드 스크립트가 탈취돼도 서명 권한까지 넘어가지 않게                     |
| 릴리스 브랜치·태그에서만 서명       | 임의 브랜치 코드가 회사 이름으로 서명되는 것 방지                        |
| 서명 대상 목록을 명시               | 타사 DLL이나 테스트 도구가 섞여 서명되는 것 방지                         |
| 서명 전 악성코드 검사               | 감염된 빌드 서버 산출물에 서명하면 인증서 평판이 손상되고 폐기 대상이 됨 |
| 서명 기록 보존                      | 파일 해시, 빌드 번호, 서명 시각, 서명자. 유출·오용 조사에 필요           |

[⬆ 목차로 돌아가기](#목차)

## 8. 인증서와 키 운영

### 바뀐 규칙 (CA/B Forum)

| 시행일     | 규칙                                            | 영향                                                                  |
|------------|-------------------------------------------------|-----------------------------------------------------------------------|
| 2023-06-01 | 개인 키는 하드웨어 암호 모듈에서 생성·저장·사용 | `.pfx` 파일을 받아 빌드 서버에 두는 방식은 새 공개 신뢰 인증서로 불가 |
| 2026-03-01 | 새로 발급하는 인증서 유효 기간 최대 460일       | 다년 인증서 불가. 매년 갱신 일정 필요                                 |

### 운영 기준

| 항목                       | 기준                                                                                            |
|----------------------------|-------------------------------------------------------------------------------------------------|
| 담당자                     | 인증서 관리 책임자 1명 + 대리 1명. 퇴사·휴가에도 갱신 가능하게                                  |
| 갱신                       | 만료 60일 전에 갱신 시작. CA 신원 확인에 영업일 며칠~몇 주가 걸릴 수 있음                       |
| 같은 게시자 ID 유지        | 갱신해도 법인명(CN·O)이 같으면 게시자 신호가 이어짐. 법인명 변경·법인 분할은 평판에 영향        |
| 토큰 보관                  | 잠금 보관함, 사용 기록 대장. 토큰 PIN은 비밀 관리 도구에                                        |
| 접근 권한                  | 서명 권한자 최소화. Artifact Signing은 Azure RBAC 역할로 분리(신원 확인 담당과 서명 담당 구분)  |
| 유출 의심                  | 즉시 CA(또는 Microsoft)에 폐기 요청 → 유출 시점 이후 서명 파일 조사 → 새 인증서로 재서명·재배포 |
| Artifact Signing 신원 확인 | 만료 전 갱신. 놓치면 인증서 갱신이 멈추고 서명이 중단됨(60일 전부터 알림)                       |

비밀 정보 보관은 [시크릿 관리](./secret_management.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

## 9. SmartScreen 평판 쌓기

서명은 출발점이고, 경고가 사라지려면 정상 다운로드가 쌓여야 합니다. Microsoft는 기준을 공개하지 않으며 "몇 주, 넓은 사용자층의 수백 건 정상 설치"가 걸릴 수 있다고 적고 있습니다. 일반 사용자 대상에는 수동 제출 방법이 없습니다.

| 전략                                    | 방법                                                                                                           |
|-----------------------------------------|----------------------------------------------------------------------------------------------------------------|
| 출시 전부터 같은 인증서로 서명          | CBT·OBT·사전 다운로드 기간에 게시자 평판을 미리 쌓음                                                           |
| 런처를 오래 유지                        | 런처 실행 파일이 자주 바뀌지 않게 하고, 게임 파일은 런처가 받게 하면 사용자가 브라우저로 받는 파일 수가 줄어듦 |
| 설치 파일을 작게·안정적으로             | 웹 설치 파일(부트스트래퍼)을 자주 바꾸지 않으면 그 파일의 해시 평판이 유지됨                                   |
| 서명 ID 일관                            | 인증서 공급자를 바꾸더라도 같은 법인명 유지. 개발사·퍼블리셔 이름을 섞지 않음                                  |
| 공식 HTTPS 도메인에서 배포              | 다운로드 주소를 자주 바꾸지 않음                                                                               |
| 사용자 안내                             | 다운로드 페이지 FAQ에 경고 화면 예시와 "게시자: (회사 법인명) 확인 후 실행" 안내                               |
| 원치 않는 프로그램처럼 보이는 동작 금지 | 번들 설치, 몰래 시작 프로그램 등록, 브라우저 설정 변경 등은 인증서 평판을 부정적으로 만듦                      |

🟡 게임 플랫폼 클라이언트(Steam 등)나 자체 런처가 내려받은 파일에 SmartScreen 다운로드 경고가 똑같이 적용되는지는 공식 자료로 확인하지 못했습니다. 이 경우에도 UAC 표시, Smart App Control, 백신 검사는 서명 여부의 영향을 받습니다.

[⬆ 목차로 돌아가기](#목차)

## 10. 백신 오탐 대응

### 오탐을 줄이는 빌드 습관

| 습관                                       | 이유                                                                           |
|--------------------------------------------|--------------------------------------------------------------------------------|
| 모든 자체 실행 파일·DLL 서명               | 서명 없는 파일이 오탐 대상이 되기 쉬움                                         |
| 실행 파일 패커·프로텍터 최소화             | 압축·암호화된 실행 파일은 악성코드와 특징이 겹침. 쓴다면 보호 대상만 좁게 적용 |
| 버전 정보 리소스 채우기                    | 회사명, 제품명, 파일 버전, 저작권을 `VERSIONINFO`에 넣음                       |
| 런타임 코드 생성·외부 다운로드 실행 최소화 | 다운로더처럼 보이는 동작이 오탐 원인이 됨                                      |
| 업데이트 시 실행 파일 이름·경로 고정       | 매번 새 이름의 실행 파일이 생기면 평판이 쌓이지 않음                           |

### 오탐이 났을 때

1. 오탐 파일의 해시(SHA-256), 버전, 탐지명, 백신 제품·엔진 판을 기록합니다.
2. Microsoft Defender는 Microsoft Security Intelligence 파일 제출(`https://www.microsoft.com/en-us/wdsi/filesubmission`)로 "오탐"을 신고합니다.
3. 국내 사용자가 많은 백신(안랩 V3, 이스트시큐리티 알약 등)과 해외 주요 백신에는 각 회사의 오탐 신고 창구로 신고합니다. 창구 주소는 각 회사 공식 페이지에서 확인합니다.
4. 고객 공지에는 "백신 예외 등록"보다 "오탐 신고 진행 중, 정식 서명 파일 확인 방법"을 먼저 안내합니다. 예외 등록 안내는 실제 악성 파일에도 같은 행동을 유도할 수 있습니다.

🟡 VirusTotal 같은 다중 검사 서비스에 올린 파일은 보안 업체와 공유될 수 있습니다. 출시 전 빌드나 내부 정보가 든 파일은 올리기 전에 정책을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 11. 릴리스 점검표

| 점검                                                | 확인 방법                               |
|-----------------------------------------------------|-----------------------------------------|
| 배포 폴더의 모든 자체 `.exe`·`.dll`·`.sys`가 서명됨 | 6절 PowerShell 점검, 결과 0건           |
| 모든 서명에 타임스탬프 있음                         | `signtool verify /pa /tw` 경고 없음     |
| 서명자가 회사 법인명                                | 파일 속성 → 디지털 서명 탭              |
| 설치 파일·제거 프로그램 서명                        | 설치 후 제거 프로그램도 확인            |
| 서명 뒤 파일 변경 없음                              | 배포 직전 해시와 서명 직후 해시 일치    |
| 깨끗한 Windows 10·11 PC에서 설치 시험               | UAC 회색 창과 게시자 이름 표시 확인     |
| 인증서 만료일                                       | 다음 릴리스 일정보다 60일 이상 남았는지 |

[⬆ 목차로 돌아가기](#목차)

## 12. 트러블슈팅

| 증상                                                                          | 원인                                                           | 조치                                                |
|-------------------------------------------------------------------------------|----------------------------------------------------------------|-----------------------------------------------------|
| 서명했는데 SmartScreen 경고가 그대로                                          | 평판 부족 (정상 동작)                                          | 9절. 게시자 이름이 표시되는지만 먼저 확인           |
| 인증서 만료 뒤 "서명 안 됨"으로 바뀜                                          | 타임스탬프 누락                                                | 타임스탬프와 함께 다시 서명해 재배포                |
| `SignTool Error: No certificates were found that met all the given criteria.` | 토큰 미연결, 다른 저장소, Artifact Signing은 dlib 경로·판 오류 | 인증서 저장소·지문 확인, dlib 경로·SignTool 판 확인 |
| `/fd` 관련 오류                                                               | 최신 SDK는 `/fd` 필수                                          | `/fd SHA256` 추가                                   |
| 타임스탬프 실패                                                               | TSA 접속 불가, 방화벽                                          | 빌드 서버에서 TSA 주소 접속 허용, 재시도            |
| Artifact Signing 403                                                          | 역할 없음, Endpoint 리전 불일치, 신원 확인 미완료              | 역할·Endpoint·신원 확인 상태 확인                   |
| `SignerSign() failed` (0x80070032)                                            | 오래된 SignTool                                                | 최신 SDK SignTool                                   |
| CI에서 서명 단계가 멈춤                                                       | USB 토큰 PIN 입력 창                                           | 클라우드 HSM·Artifact Signing으로 전환              |
| 패치 후 서명 깨짐                                                             | 차등 패치 결과가 원본과 다름, 실행 파일 자체 수정              | 패치 후 해시 검증, 실행 파일 수정 금지              |
| 파일 속성에 디지털 서명 탭이 없음                                             | 서명 안 됨 또는 탭을 보여 주지 않는 파일 형식                  | `signtool verify /v /pa`로 확인                     |

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- SmartScreen 평판: [Microsoft Learn](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation) — ★★★☆☆
- 코드 서명 방식 비교: [Microsoft Learn](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options) — ★★★☆☆
- Azure Artifact Signing 시작하기: [Microsoft Learn Quickstart](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart) — ★★★☆☆
- Artifact Signing 연동(SignTool, GitHub Actions): [Microsoft Learn](https://learn.microsoft.com/en-us/azure/artifact-signing/how-to-signing-integrations), [azure/artifact-signing-action](https://github.com/azure/artifact-signing-action) — ★★★☆☆
- SignTool: [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool) — ★★★☆☆
- 타임스탬프: [Time Stamping Authenticode Signatures](https://learn.microsoft.com/en-us/windows/win32/seccrypto/time-stamping-authenticode-signatures) — ★★★☆☆
- UAC 동작: [How User Account Control works](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works) — ★★★☆☆
- 드라이버 서명 요건: [Driver Code Signing Requirements](https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-reqs) — ★★★☆☆
- CA/B Forum 코드 서명 기본 요구사항: [cabforum.org](https://cabforum.org/working-groups/code-signing/requirements/) — ★★★☆☆
- Microsoft Defender 오탐 제출: [Microsoft Security Intelligence](https://www.microsoft.com/en-us/wdsi/filesubmission) — ★★★☆☆

확인일: 2026-11-18. 정책·명령은 공식 문서와 대조했으며, 서명 명령과 CI 예시는 실제 인증서로 실행해 보지 않았습니다.

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-18

**마지막 업데이트**: 2026-11-18

© 2026 siasia86. Licensed under CC BY 4.0.
