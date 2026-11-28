---
name: windows-unattend-answer-file-official-notes
description: Windows 무인 설치 응답 파일의 암시적 검색 순서, Panther 캐시와 민감 정보 제거, SetupComplete.cmd 실행 조건, AutoLogon·AdministratorPassword 동작, 설치 로그 위치 정리.
tags:
  - windows
  - unattend
  - autounattend
last_checked: 2026-11-28
sources:
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-setup-automation-overview
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-setup-configuration-passes
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/add-a-custom-script-to-windows-setup
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/deployment-troubleshooting-and-log-files
  - https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-shell-setup-autologon
  - https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-shell-setup-autologon-password
  - https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-shell-setup-useraccounts-administratorpassword
  - https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-setup-userdata-productkey
  - https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-setup-userdata-productkey-key
  - https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-setup-userdata-productkey-willshowui
  - https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys
---

# Windows 무인 설치 응답 파일 공식 자료 참조 노트

## 1. 문서 날짜 (2026-11-28 확인)

- automation overview: ms.date 2021-09-30. configuration passes: 2017-05-02(본문이 소개 한 줄뿐이라 패스별 시점은 이 페이지로 확인하지 못함). custom script: 2021-10-04. troubleshooting and log files: 2021-05-02. AutoLogon: 2020-02-18. 관리자 비밀번호 설정 페이지는 2017-05-02.
- `hide-sensitive-data-in-an-answer-file` 페이지는 2026-11-28에 404였습니다.

## 2. 암시적 검색 순서 (automation overview 표)

| 순서 | 위치                                                                                    | 파일 이름                       | 비고                                                                  |
|------|-----------------------------------------------------------------------------------------|---------------------------------|-----------------------------------------------------------------------|
| 1    | 레지스트리 `HKLM\System\Setup\UnattendFile`                                             | 제한 없음                       | 경로를 직접 지정                                                      |
| 2    | `%WINDIR%\Panther\Unattend`                                                             | Unattend.xml·Autounattend.xml   | "only on downlevel installations"                                     |
| 3    | `%WINDIR%\Panther`                                                                      | 캐시된 파일                     | "Do not use, modify, or overwrite the answer file in this directory." |
| 4    | 이동식 읽기·쓰기 미디어 루트                                                            | Autounattend.xml                | "in order of drive letter"                                            |
| 5    | 이동식 읽기 전용 미디어(CD·DVD) 루트                                                    | Autounattend.xml                | "in order of drive letter"                                            |
| 6    | windowsPE·offlineServicing: 설치 미디어 `\Sources` / 그 밖: `%WINDIR%\System32\Sysprep` | Autounattend.xml / Unattend.xml | 패스에 따라 다름                                                      |
| 7    | `%SYSTEMDRIVE%`                                                                         | Unattend.xml·Autounattend.xml   |                                                                       |
| 8    | setup.exe가 실행 중인 드라이브 루트                                                     | Unattend.xml·Autounattend.xml   |                                                                       |

- "The answer file that has the highest precedence is used." 검색은 "at the beginning of each configuration pass"에 합니다.
- 두 번째 DVD 드라이브: 문서에 따로 적혀 있지 않습니다. 5번이 드라이브 문자 순서로 검색한다는 문구로 미루어 대상이라고 보지만 추정입니다.

## 3. 캐시와 민감 정보

- "a copy of the answer file is cached to the %WINDIR%\Panther directory". windowsPE 동안은 `$Windows.~BT\Sources\Panther`에 둡니다.
- "Setup removes sensitive data in the cached answer file at the end of each configuration pass."
- 남는 파일 주의: "Before you deliver the computer to a customer, you must delete the cached answer file in the %WINDIR%\panther directory."
- `%WINDIR%\Panther\Unattend\Unattend.xml` 같은 내장 응답 파일이 있으면 패스마다 다시 처리되어 앞 패스의 민감 정보 제거가 적용되지 않을 수 있다고 합니다.
- overview: "You can add a command to the Setupcomplete.cmd command script that deletes any cached or embedded answer files on the computer."
- 제거된 값이 어떤 문자열로 바뀌는지, 제거 대상 설정 목록: 미확인.
- `PlainText=false`: 설정 페이지는 값이 "hidden"이라고만 하고 암호화라고 하지 않습니다. 404 페이지 때문에 인코딩 방식 설명은 미확인입니다. 숨김은 보호 수단으로 보지 않는 것이 안전합니다(이 노트의 판단).

## 4. SetupComplete.cmd (custom script)

- 위치 `%WINDIR%\Setup\Scripts\SetupComplete.cmd`, "This script runs with local system permissions".
- 실행 시점 문구가 페이지 안에서 두 가지입니다: "starts immediately after the user sees the desktop."와 "After Windows is installed but before the logon screen appears". 정확한 시점은 미확인입니다.
- 실행되지 않는 조건: "This setting is disabled when using OEM product keys, except on Enterprise editions and Windows Server operating systems." 대안으로 응답 파일의 `RunSynchronousCommand`·`RunAsynchronousCommand`를 안내합니다.
- "Setup does not verify any exit codes or error levels in the script after it executes SetupComplete.cmd."
- 다시 시작 금지: "You should not reboot the system by adding a command such as shutdown -r."
- 기록: `C:\Windows\Panther\UnattendGC\Setupact.log`.
- `ErrorHandler.cmd`: 같은 폴더, 치명적 오류 때 SYSTEM으로 실행되며 여러 번 실행될 수 있습니다.
- sysprep 뒤 OOBE를 마친 다음에도 실행되는지, 시간 제한: 문서에서 미확인.

## 5. 계정 설정

- AdministratorPassword 유효 패스: auditSystem, oobeSystem.
- 기본 Administrator: "By default, the built-in administrator account is disabled in all default clean installations." AutoLogon `Username`을 Administrator로 두면 비밀번호 설정이 없어도 켜집니다. 비밀번호도 Username도 없으면 꺼진 채입니다.
- AutoLogon 유효 패스: auditSystem, oobeSystem, specialize. `LogonCount`는 AutoLogon을 쓰면 반드시 지정합니다.
- "AutoLogon credentials are deleted from the unattended installation answer file after Windows Setup is complete."
- "Make sure AutoLogon is disabled on computers that are delivered to customers."
- "In Windows 10, if you configure AutoLogon, the OS will skip the user account creation phase during OOBE."
- "Creating a blank administrator password is a security risk."
- 자동 로그온 비밀번호가 레지스트리에 남는지: 이 페이지들에서 미확인.

## 6. 제품 키 (Microsoft-Windows-Setup\UserData\ProductKey)

- 문서 날짜: ProductKey·Key·WillShowUI 페이지 ms.date 2017-05-02(갱신 2021-03-18), KMS client activation keys ms.date 2025-06-25(갱신 2026-04-02).
- "`ProductKey` contains settings that specify which edition of Windows to install." 유효 패스는 windowsPE, 하위 요소는 `Key`와 `WillShowUI`.
- `Key`: "the 25-character product key that determines which edition of Windows to install." 빈 값 금지: "This string type does not support empty elements. Do not create an empty value for this setting."
- `WillShowUI`: `Always`, `OnError`(기본값, "the UI is displayed if an error occurs"), `Never`. `Never`도 치명적 오류 메시지는 막지 못한다고 적혀 있습니다.
- `ProductKey` 안에 `Key` 없이 `WillShowUI`만 두는 경우의 동작은 문서에 없습니다. 실제 빌드에서 이 구성이 "무인 응답 파일에서 <ProductKey> 설정을 읽을 수 없습니다" 오류로 windowsPE 단계에서 멈춘 사례가 보고되었습니다([보고], 이 저장소에서 미재현). 키를 넣지 않을 때는 `ProductKey` 요소를 통째로 빼는 편이 안전합니다(이 노트의 판단).
- 정품 인증용 키는 `Microsoft-Windows-Shell-Setup\ProductKey`로 따로 줄 수 있으며, 설치 키와 다를 수 있습니다.
- KMS 클라이언트 키(GVLK) 공식 표: Windows 11 Pro·Pro for Workstations·Pro Education·Education·Enterprise 등을 포함하고 Home은 없습니다. "intended for volume licensing scenarios and can't be used with retail editions." 볼륨 라이선스 환경의 설치·전환(`slmgr /ipk`)용이며 소매 정품 인증은 되지 않습니다. 키 값은 이 노트에 옮기지 않습니다.
- 오류 문구 "Windows cannot read the <ProductKey> setting from the unattend answer file"의 공식 설명: 미확인.

## 7. 로그 (troubleshooting and log files)

- windowsPE 단계 로그는 메모리에 쓰며 임시입니다. "Log files created during the Windows PE phase are temporary."
- `Setupact.log`: specialize는 `X:\Windows\panther`, OOBE·LogonUI는 `%windir%\panther`, OOBE 무인 처리는 `%windir%\panther\unattendGC`.
- `Setuperr.log`(`%windir%\panther`): 오류 요약만 있으므로 "review the entries in the Setuperr.log file first, then the Setupact.log file second".
- 그 밖에 `%windir%\inf\Setupapi.dev.log`, `%windir%\panther\Cbs_unattend.log`.

## 8. 미확인

- 7개 구성 패스의 실행 시점 전체 표(이번 조회 페이지 본문에 없음). 일반적으로 windowsPE → offlineServicing → specialize → oobeSystem이고, sysprep `/generalize` 뒤에는 generalize → specialize → oobeSystem이 이어진다고 알려져 있으나 이번에 원문으로 다시 확인하지 못했습니다.
- 응답 파일 시험: 이 저장소 환경에 Windows가 없어 미실행. 예제 XML은 형식(well-formed)만 검사했습니다.
