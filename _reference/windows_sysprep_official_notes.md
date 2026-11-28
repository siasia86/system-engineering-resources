---
name: windows-sysprep-official-notes
description: Windows sysprep 명령 옵션, generalize가 지우는 것과 횟수 제한, 단계별 로그 위치, Store 앱 때문에 실패하는 원인과 복구, 서버 역할 지원 조건 정리.
tags:
  - windows
  - sysprep
  - golden-image
last_checked: 2026-11-28
sources:
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep--generalize--a-windows-installation
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-command-line-options
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-process-overview
  - https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-support-for-server-roles
  - https://learn.microsoft.com/en-us/troubleshoot/windows-client/setup-upgrade-and-drivers/sysprep-fails-remove-or-update-store-apps
---

# Windows sysprep 공식 자료 참조 노트

## 1. 문서 날짜 (2026-11-28 확인)

| 페이지                                      | ms.date    | 갱신       |
|---------------------------------------------|------------|------------|
| sysprep--generalize--a-windows-installation | 2021-09-30 | 2021-12-15 |
| sysprep-command-line-options                | 2021-10-02 | 2026-06-03 |
| sysprep-process-overview                    | 2021-10-08 | 2026-06-03 |
| sysprep-support-for-server-roles            | 2017-05-02 | 2021-10-25 |
| sysprep-fails-remove-or-update-store-apps   | 2026-02-12 | 2026-09-21 |

- 문서가 Windows 11 판(23H2·24H2 등)별로 나뉘어 있지 않습니다. 판별 차이는 미확인입니다.
- process overview: "The Sysprep user interface is deprecated." 명령줄로 실행합니다.

## 2. 명령 옵션

- 문법: `Sysprep.exe [/oobe | /audit] [/generalize] [/mode:vm] [/reboot | /shutdown | /quit] [/quiet] [/unattend:<answerfile>]`
- `/generalize`: "Sysprep removes all unique system information from the Windows installation."
- `/oobe`: "Restarts the computer into OOBE mode." 다음 부팅에서 oobeSystem 패스를 처리합니다.
- `/audit`: 감사 모드로 다시 시작합니다(드라이버·앱 추가와 시험용).
- `/shutdown`: "Shuts down the computer after the Sysprep command finishes running."
- `/quiet`: 확인 메시지를 띄우지 않습니다. Server Core는 명령줄과 `/quiet`로 실행해야 하며 그렇지 않으면 "the process will fail silently".
- `/unattend:<answerfile>`: 응답 파일 설정을 적용합니다.
- `/mode:vm`: "Generalizes a Virtual Hard Disk (VHD) so that you can deploy the VHD as a VHD on the same Virtual Machine (VM) or hypervisor." "You can only run VM mode from inside a VM." 같은 하드웨어 프로필의 VM에만 배포하며, 함께 쓸 수 있는 옵션은 `/reboot`·`/shutdown`·`/quit`뿐입니다.
- `/pnp`는 문서에 없습니다. 장치 설치를 유지하려면 응답 파일의 `Microsoft-Windows-PnpSysprep | PersistAllDeviceInstalls`(기본 `false`)를 씁니다.

## 3. generalize가 하는 일과 제한

- "Sysprep resets the security ID (SID), clears any system restore points, and deletes event logs." 새 SID는 다음 부팅의 specialize 패스에서 만들어집니다.
- "Windows replaces the computer SID only on the operating system volume where you ran Sysprep."
- 장치: "Generalizing a Windows installation uninstalls these configured devices, but doesn't remove device drivers from the PC."
- 횟수: "You can run `Sysprep` command up to 1001 times on a single Windows image." Windows 8.1·Server 2012 이상은 1001회, Windows 7·Server 2008 R2는 3회입니다. 넘으면 이미지를 다시 만들어야 합니다.
- 일반화 없이 이미지를 다른 컴퓨터로 옮기는 것은 지원하지 않습니다: "Moving or copying a Windows image to a different computer without running the `Sysprep /generalize` command is not supported."
- 실행 조건: "Only an administrator can run Sysprep. Only one instance of Sysprep can run at a time."
- 컴퓨터 이름·도메인 가입·업그레이드 설치에 대한 동작은 이 5개 페이지에서 미확인입니다.

## 4. 로그 위치 (process overview)

| 단계           | 위치                                |
|----------------|-------------------------------------|
| generalize     | `%WINDIR%\System32\Sysprep\Panther` |
| specialize     | `%WINDIR%\Panther`                  |
| 무인 설치 OOBE | `%WINDIR%\Panther\Unattendgc`       |

- "The **setupact.log** file is the main log file."
- generalize 패스가 설치 로그 일부를 지우므로 sysprep는 generalize 기록을 표준 위치 밖에 남깁니다.

## 5. Store 앱 때문에 실패 (KB 2769827)

- 로그 문구: "<package name> was installed for a user, but not provisioned for all users. This package will not function properly in the sysprep image." 이어서 "Failed to remove apps for the current user: 0x80073cf2."와 "A fatal error occurred while trying to sysprep the machine".
- 원인: 모든 사용자용으로 준비(provisioned)된 패키지를 한 사용자가 갱신했거나, 이미지에서 준비를 지웠는데 특정 사용자에게는 남은 경우.
- 확인: `Get-AppxPackage -AllUsers | Where PublisherId -eq 8wekyb3d8bbwe | Format-List -Property PackageFullName,PackageUserInformation`
- 복구: `Remove-AppxPackage -Package <packagefullname>`, `Remove-AppxProvisionedPackage -Online -PackageName <packagefullname>`. 설치된 것으로 표시된 사용자 계정은 지우거나 그 계정으로 로그온해 처리합니다.
- 예방: "To prevent Microsoft Store from updating apps, unplug the Internet connection or disable Automatic Updates in Audit mode before you create the image." generalize 문서는 Store에서 앱을 설치하지 말라고 합니다.
- "The issue does not occur if you are servicing an offline image."

## 6. 서버 역할

- AD DS·AD CS·AD FS 등 여러 역할은 sysprep를 지원하지 않습니다. "you must enable and configure any server roles that do not support Sysprep after you have performed the imaging and deployment process."
- Hyper-V 역할: "You must delete any virtual networks before you run the Sysprep tool."

## 7. 미확인

- `/unattend`로 준 응답 파일을 sysprep가 따로 복사해 두는지(이 5개 페이지에는 없음). 설치 단계의 캐시는 [무인 설치 응답 파일 참조 노트](./windows_unattend_answer_file_official_notes.md) 3절에 따로 정리했습니다.
- "Sysprep was not able to validate your Windows installation" 문구의 공식 설명.
- 실제 sysprep 실행 시험: 이 저장소 환경에 Windows가 없어 미실행.
