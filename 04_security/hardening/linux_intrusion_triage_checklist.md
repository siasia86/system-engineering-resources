# Linux 침해 의심 서버 초동 점검

침해가 의심되는 Linux 서버에서 증거를 덜 훼손하면서 "실제로 침해되었는가, 무엇을 먼저 막아야 하는가"를 판단하기 위한 초동 점검 순서입니다. 탐지·확인·격리 판단까지를 다루며, 정밀 포렌식 분석과 복구는 범위 밖입니다.

## 목차

| 섹션                                                                                              |
|---------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 시작 전 원칙](#2-시작-전-원칙)                                           |
| [3. 휘발성 정보 먼저 수집](#3-휘발성-정보-먼저-수집) / [4. 계정과 접속 흔적](#4-계정과-접속-흔적) |
| [5. 프로세스와 네트워크](#5-프로세스와-네트워크) / [6. 지속 실행 경로](#6-지속-실행-경로)         |
| [7. 파일 변조 확인](#7-파일-변조-확인) / [8. 로그 확인](#8-로그-확인)                             |
| [9. 판단과 격리](#9-판단과-격리) / [10. 평소 준비 점검표](#10-평소-준비-점검표)                   |

---

## 1. 개요

### 언제 이 절차를 쓰는가

| 계기 예                                  | 먼저 볼 절             |
|------------------------------------------|------------------------|
| 알 수 없는 프로세스가 CPU를 계속 씀      | 5. 프로세스와 네트워크 |
| 외부로 나가는 이상 트래픽 경보           | 5. 프로세스와 네트워크 |
| AIDE·패키지 검증에서 실행 파일 변경 발견 | 7. 파일 변조 확인      |
| 모르는 계정·SSH 키 발견                  | 4. 계정과 접속 흔적    |
| 클라우드 보안 서비스의 탐지 결과         | 3절부터 순서대로       |

장애 대응 체계(역할·등급·커뮤니케이션)는 [Incident Management](../../03_engineering/reliability/incident_management.md)를 따르고, 이 문서는 그 안에서 서버 한 대를 점검하는 기술 절차로 씁니다. NIST SP 800-61 Rev. 3도 사고 대응을 조직의 위험 관리 활동과 함께 다루도록 권고합니다.

### 점검 흐름

```text
 alert / suspicion
       |
       v
 [prepare] record time, notify, do not reboot
       |
       v
 [volatile] processes, network, sessions  --> save to external storage
       |
       v
 [persistent] accounts, persistence, file changes, logs
       |
       v
 [decide] confirmed? --> isolate / escalate
          not confirmed --> document, keep monitoring
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 시작 전 원칙

RFC 3227(증거 수집·보관 지침, BCP 55)의 "피할 것"을 운영 상황에 맞게 정리하면 다음과 같습니다.

| 원칙                                    | 이유                                                                     |
|-----------------------------------------|--------------------------------------------------------------------------|
| 수집이 끝나기 전에 재부팅·종료하지 않음 | 메모리·프로세스·연결 정보가 사라지고, 종료 스크립트가 변조되었을 수 있음 |
| 서버의 프로그램을 그대로 믿지 않음      | `ps`, `ss`, `ls`가 바뀌어 결과를 숨길 수 있음                            |
| 모든 파일 접근 시각을 바꾸는 명령 자제  | 전체 `tar`·`find -exec cat` 등은 atime 흔적을 덮음                       |
| 네트워크 차단 영향 고려                 | 연결이 끊기면 흔적을 지우는 장치가 있을 수 있음                          |
| 결과는 서버 밖에 저장                   | 같은 디스크에 쓰면 삭제된 파일 영역을 덮어씀                             |
| 한 일과 시각을 모두 기록                | 이후 분석·보고·법적 대응의 근거                                          |

### 수집 결과 저장

수집 결과는 점검 대상 디스크에 쓰지 않고 SSH로 바로 밖으로 보냅니다.

```bash
# 점검 PC에서 실행: 대상 서버 명령 결과를 점검 PC 파일로 저장
ssh admin@192.0.2.10 'sudo ps auxwwf' > case01_ps_$(date +%Y%m%dT%H%M%S).txt
sha256sum case01_ps_*.txt >> case01_hashes.txt
```

가능하면 신뢰할 수 있는 매체에 담은 정적 빌드 도구(busybox 등)를 함께 써서 서버의 명령 결과와 비교합니다. 결과가 다르면 바이너리 변조나 루트킷을 의심합니다.

### 클라우드·가상 서버

가상 서버는 점검 전에 디스크 스냅샷을 먼저 떠 두면 이후 분석을 원본 대신 사본에서 할 수 있습니다. 메모리 수집 기능이 있는 환경이면 그것도 함께 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 휘발성 정보 먼저 수집

RFC 3227은 사라지기 쉬운 순서로 수집하라고 권합니다. 서버 운영 관점으로 바꾸면 아래 순서입니다.

| 순서 | 대상                                 | 명령 예                             |
|------|--------------------------------------|-------------------------------------|
| 1    | 시각, 접속 세션                      | `date -u`, `w`, `who`               |
| 2    | 네트워크 연결, 라우팅, ARP           | `ss -tunap`, `ip route`, `ip neigh` |
| 3    | 프로세스 목록, 열린 파일             | `ps auxwwf`, `lsof -nP`             |
| 4    | 커널 모듈, 마운트                    | `lsmod`, `findmnt`                  |
| 5    | 임시 파일 시스템(`/tmp`, `/dev/shm`) | `ls -la --time-style=full-iso`      |
| 6    | 디스크(로그, 설정)                   | 4~8절                               |

```bash
date -u; uptime
w; who -a
ss -tunap
ip -br addr; ip route; ip neigh
ps auxwwf
lsmod
findmnt
ls -la --time-style=full-iso /tmp /var/tmp /dev/shm
```

`/dev/shm`은 메모리 위 파일 시스템이라 재부팅하면 사라집니다. 실행 권한이 있는 파일이 있으면 해시와 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 계정과 접속 흔적

### 계정

```bash
# UID 0 계정 (root 외에 있으면 즉시 확인)
awk -F: '$3 == 0 {print $1}' /etc/passwd

# 로그인 셸이 있는 계정
grep -vE '(nologin|false)$' /etc/passwd

# 최근 바뀐 계정 파일
ls -l --time-style=full-iso /etc/passwd /etc/shadow /etc/group /etc/sudoers
ls -la --time-style=full-iso /etc/sudoers.d/

# sudo 권한 보유자
getent group sudo wheel
```

### SSH 키

```bash
# 모든 사용자의 authorized_keys 위치·변경 시각
for h in /root $(awk -F: '$6 ~ /^\/home/ {print $6}' /etc/passwd); do
  ls -la --time-style=full-iso "$h/.ssh/" 2>/dev/null
done

# sshd 설정에서 키 파일 위치를 바꿨는지 확인
sudo sshd -T | grep -iE 'authorizedkeysfile|authorizedkeyscommand|permitrootlogin'
```

등록된 키마다 소유자와 등록 경위를 확인합니다. 설명(comment)이 없는 키, 최근 시각에 추가된 키, 서비스 계정에 있는 키를 먼저 봅니다.

### 로그인 기록

```bash
last -Faiw | head -50      # 성공 로그인 (/var/log/wtmp)
sudo lastb -Faiw | head -50 # 실패 로그인 (/var/log/btmp)
lastlog | grep -v 'Never'  # 계정별 마지막 로그인
```

🟡 `wtmp`·`btmp`·`lastlog`는 root 권한으로 쉽게 지울 수 있습니다. 비어 있거나 기간이 끊겨 있으면 그것 자체가 흔적입니다. 중앙 수집 로그와 대조합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 프로세스와 네트워크

### 의심 프로세스 기준

| 징후                                      | 확인 방법                                         |
|-------------------------------------------|---------------------------------------------------|
| 실행 파일이 삭제된 채 실행 중             | `ls -l /proc/*/exe 2>/dev/null \| grep deleted`   |
| `/tmp`, `/dev/shm`, `/var/tmp`에서 실행   | `ls -l /proc/<PID>/exe`                           |
| 이름은 커널 스레드 같지만 부모가 1이나 셸 | `ps -o pid,ppid,user,cmd -p <PID>`                |
| 웹 서버·DB 계정이 셸을 띄움               | `ps auxwwf`에서 트리 확인                         |
| 알 수 없는 프로세스가 외부로 연결         | `ss -tunap`                                       |
| CPU를 계속 높게 쓰는 모르는 프로세스      | `top -c`, `ps -eo pid,user,pcpu,cmd --sort=-pcpu` |

### 프로세스 하나 자세히 보기

```bash
PID=1234
ls -l /proc/$PID/exe            # 실행 파일 경로 (deleted 표시 확인)
tr '\0' ' ' < /proc/$PID/cmdline; echo
ls -l /proc/$PID/cwd            # 작업 디렉터리
sudo ls -l /proc/$PID/fd        # 열린 파일·소켓
sudo cat /proc/$PID/environ | tr '\0' '\n'
sudo sha256sum /proc/$PID/exe   # 삭제된 실행 파일도 해시 가능
```

실행 파일이 삭제된 경우에도 프로세스가 살아 있으면 `/proc/<PID>/exe`로 내용을 복사해 보존할 수 있습니다. 프로세스를 먼저 종료하면 이 기회가 사라지므로, 종료는 보존 뒤에 결정합니다.

```bash
# 보존: 점검 PC로 바로 전송
ssh admin@192.0.2.10 "sudo cat /proc/$PID/exe" > case01_pid${PID}_exe.bin
```

### 네트워크

```bash
sudo ss -tunap state established   # 수립된 연결과 프로세스
sudo ss -tulnp                     # 대기 중인 포트
sudo lsof -nP -i                   # 소켓을 연 프로세스 (교차 확인)
```

| 확인 항목                               | 판단 기준                               |
|-----------------------------------------|-----------------------------------------|
| 서비스 목록에 없는 대기 포트            | 구성 관리 기록과 대조                   |
| 업무와 무관한 국가·대역으로 나가는 연결 | 방화벽·흐름 로그와 대조                 |
| 웹 서버 프로세스의 외부 발신 연결       | 정상 업무 연동인지 확인                 |
| `ss`와 `lsof` 결과 불일치               | 도구 변조 의심, 외부 매체 도구로 재확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 지속 실행 경로

공격자는 재부팅 뒤에도 다시 실행되도록 흔적을 남깁니다. 아래 경로의 최근 변경을 확인합니다.

| 경로                 | 확인 명령                                                                  |
|----------------------|----------------------------------------------------------------------------|
| 사용자 crontab       | `sudo ls -la /var/spool/cron/ /var/spool/cron/crontabs/ 2>/dev/null`       |
| 시스템 cron          | `ls -la /etc/cron.d /etc/cron.*`, `cat /etc/crontab`                       |
| systemd unit·timer   | `systemctl list-unit-files --state=enabled`, `systemctl list-timers --all` |
| 직접 추가된 unit     | `ls -la --time-style=full-iso /etc/systemd/system/`                        |
| 사용자 systemd unit  | `ls -la /home/*/.config/systemd/user/ 2>/dev/null`                         |
| 셸 시작 파일         | `/etc/profile.d/`, `~/.bashrc`, `~/.profile`                               |
| 라이브러리 강제 적재 | `cat /etc/ld.so.preload` (보통 없음)                                       |
| 커널 모듈            | `lsmod`, `/etc/modules-load.d/`                                            |
| `at` 예약 작업       | `atq`                                                                      |
| SSH 강제 명령        | `authorized_keys`의 `command=` 옵션                                        |

```bash
# 최근 7일 안에 바뀐 시스템 설정·실행 파일 (읽기만 하는 검색)
sudo find /etc /usr/bin /usr/sbin /usr/lib/systemd /etc/systemd \
  -xdev -newermt "$(date -d '7 days ago' +%F)" -ls 2>/dev/null | head -100
```

변경 시각(mtime)은 공격자가 바꿀 수 있습니다. 시각만으로 판단하지 말고 패키지 검증·해시 비교(7절)와 함께 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 파일 변조 확인

### 패키지 검증

패키지 관리자가 설치한 파일을 설치 당시 정보와 비교합니다.

```bash
# RHEL 계열: 바뀐 파일만 출력
sudo rpm -Va 2>/dev/null | head -100

# Debian 계열
sudo dpkg --verify 2>/dev/null | head -100
```

`rpm -V` 출력의 앞 글자 묶음은 바뀐 속성을 뜻합니다.

| 글자 | 의미      | 글자 | 의미           |
|------|-----------|------|----------------|
| `S`  | 크기      | `U`  | 소유 사용자    |
| `M`  | 권한·종류 | `G`  | 소유 그룹      |
| `5`  | 내용 해시 | `T`  | 수정 시각      |
| `L`  | 링크 대상 | `P`  | capability     |
| `D`  | 장치 번호 | `c`  | 설정 파일 표시 |

설정 파일(`c`)의 변경은 흔하지만, `/usr/bin`·`/usr/sbin`·`/usr/lib` 아래 실행 파일·라이브러리의 해시(`5`) 변경은 우선 확인 대상입니다. Debian `dpkg --verify`는 현재 md5 해시 비교만 하고, 확인하지 않은 속성은 `?`로 표시합니다. dpkg 문서도 이것을 무결성 확인일 뿐 보안 검증으로 보지 말라고 밝힙니다.

🟡 패키지 DB 자체도 root 권한으로 바꿀 수 있습니다. 결과가 깨끗해도 외부 기준(AIDE 외부 DB, 같은 판 정상 서버 해시)과 교차 확인합니다.

### AIDE 결과

AIDE를 운영 중이면 서버 밖에 보관한 기준 DB와 해시를 먼저 확인한 뒤 점검합니다. 절차는 [AIDE 파일 무결성 감시 가이드](./aide_file_integrity_monitoring.md)에서 다룹니다.

### 웹 루트

웹 서비스 서버는 업로드 경로와 웹 루트에서 최근 생긴 스크립트 파일을 확인합니다. 업로드 경로 보호는 [CWE-434 파일 업로드](../web_cwe/cwe_434_file_upload.md)에서 다룹니다.

```bash
sudo find /var/www -xdev -type f -newermt "$(date -d '14 days ago' +%F)" \
  \( -name '*.php' -o -name '*.jsp' -o -name '*.py' -o -name '*.sh' \) -ls
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 로그 확인

| 로그                   | 위치                                                 | 볼 내용                          |
|------------------------|------------------------------------------------------|----------------------------------|
| 인증                   | `/var/log/auth.log`(Debian), `/var/log/secure`(RHEL) | SSH 로그인, sudo 사용            |
| systemd journal        | `journalctl`                                         | 서비스 시작·중지, 커널 메시지    |
| 감사 로그              | `/var/log/audit/audit.log`                           | 계정·설정 변경 주체              |
| 웹 서버 접근·오류 로그 | `/var/log/nginx/`, `/var/log/httpd/` 등              | 비정상 요청, 업로드 후 실행 요청 |
| 패키지 설치 기록       | `/var/log/dnf.log`, `/var/log/apt/history.log`       | 계획에 없는 설치                 |

```bash
# SSH 로그인 성공 기록 (최근 3일)
sudo journalctl -u ssh -u sshd --since "3 days ago" | grep -E 'Accepted|session opened'

# sudo 사용 기록
sudo journalctl _COMM=sudo --since "3 days ago"

# 감사 로그: 계정·sudoers 변경 (규칙이 있을 때)
sudo ausearch -k identity -ts week-ago -i 2>/dev/null | tail -50
sudo ausearch -k sudoers -ts week-ago -i 2>/dev/null | tail -50

# 로그 공백 확인: 시간대별 기록 수
sudo journalctl --since "3 days ago" -o short-iso | cut -c1-13 | uniq -c
```

시간대별 기록 수에서 평소에 있던 시간대가 통째로 비어 있으면 로그 삭제나 서비스 중단을 의심합니다. 로컬 로그는 지워질 수 있으므로 중앙 수집 로그를 기준으로 판단합니다. 감사 규칙 작성은 [auditd 감사 규칙과 로그 조회 가이드](./auditd_rules_and_search_guide.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 판단과 격리

### 판단 기준

| 결과                                                                            | 판단               | 다음 행동                             |
|---------------------------------------------------------------------------------|--------------------|---------------------------------------|
| 승인되지 않은 UID 0 계정, 실행 파일 해시 변경, 삭제된 실행 파일로 도는 프로세스 | 침해 확정에 가까움 | 격리, 사고 등급 상향, 보안 담당 호출  |
| 모르는 SSH 키, 계획에 없는 cron·unit                                            | 침해 의심          | 등록 경위 확인, 확인 전까지 격리 준비 |
| 설명 가능한 변경만 있음                                                         | 침해 근거 없음     | 기록 후 감시 강화                     |

### 격리 방법 비교

| 방법                                | 장점                      | 주의                                   |
|-------------------------------------|---------------------------|----------------------------------------|
| 보안 그룹·방화벽으로 외부 통신 차단 | 프로세스·메모리 상태 유지 | 관리 접속 경로는 남겨 둠               |
| 로드 밸런서에서 제외                | 서비스 영향 최소          | 서버 자체의 외부 통신은 계속될 수 있음 |
| 네트워크 분리                       | 확산 차단                 | 흔적 삭제 장치가 동작할 수 있음(2절)   |
| 전원 차단                           | 즉시 정지                 | 메모리·연결 정보 모두 소실             |

보통은 증거 수집을 마친 뒤 통신 차단으로 격리하고, 서비스는 깨끗한 이미지로 새 서버를 만들어 옮깁니다. 침해가 확인된 서버를 정리해서 다시 쓰는 것보다 새로 만드는 쪽이 남은 백도어 위험이 적습니다.

### 같이 바꿀 것

| 대상                                  | 이유                       |
|---------------------------------------|----------------------------|
| 그 서버에서 쓰던 비밀번호·API 키·토큰 | 이미 유출되었다고 가정     |
| 그 서버에서 다른 서버로 가는 SSH 키   | 횡적 이동 경로 차단        |
| 같은 이미지·설정을 쓰는 다른 서버     | 같은 취약점이 있을 수 있음 |

비밀 정보 교체 절차는 [시크릿 관리](./secret_management.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 평소 준비 점검표

초동 점검의 품질은 평소 준비에 달려 있습니다.

| 항목             | 준비 내용                                  |
|------------------|--------------------------------------------|
| 중앙 로그 수집   | 인증·journal·감사 로그를 서버 밖으로 전송  |
| auditd 규칙      | 계정·sudoers·cron·모듈 적재 감시           |
| 파일 무결성 기준 | AIDE 기준 DB와 해시를 서버 밖에 보관       |
| 시각 동기화      | 모든 서버 NTP 동기화(로그 시각 대조용)     |
| 점검 도구        | 신뢰할 수 있는 매체의 정적 빌드 도구 준비  |
| 대응 연락망      | 보안 담당·서비스 담당 연락처와 등급 기준   |
| 스냅샷 권한      | 점검자가 디스크 스냅샷을 만들 수 있는 권한 |
| 연습             | 시험 서버로 이 절차를 정기적으로 실습      |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- RFC 3227 Guidelines for Evidence Collection and Archiving(BCP 55): [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc3227) (확인일 2026-11-16) — ★★★★☆
- NIST SP 800-61 Rev. 3 Incident Response Recommendations and Considerations for Cybersecurity Risk Management(2025-04): [csrc.nist.gov](https://csrc.nist.gov/pubs/sp/800/61/r3/final) (확인일 2026-11-16) — ★★★★☆
- NIST SP 800-86 Guide to Integrating Forensic Techniques into Incident Response: [csrc.nist.gov](https://csrc.nist.gov/pubs/sp/800/86/final) (확인일 2026-11-16) — ★★★★☆
- proc(5)(`/proc/<pid>/exe`, `cmdline`, `environ`): [man7.org](https://man7.org/linux/man-pages/man5/proc.5.html) (확인일 2026-11-16) — ★★★☆☆
- ss(8): [man7.org](https://man7.org/linux/man-pages/man8/ss.8.html) (확인일 2026-11-16) — ★★★☆☆
- rpm verify 출력 형식: [rpm.org](https://rpm-software-management.github.io/rpm/man/rpm.8.html) (확인일 2026-11-16) — ★★★☆☆
- dpkg(1)(`--verify`): [manpages.debian.org](https://manpages.debian.org/bookworm/dpkg/dpkg.1.en.html) (확인일 2026-11-16) — ★★★☆☆

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
