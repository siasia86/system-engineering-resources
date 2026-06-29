# CVE-2026-46300 — Linux Kernel XFRM ESP-in-TCP (Fragnesia)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 취약점 상세](#2-취약점-상세) / [3. 영향 범위 확인](#3-영향-범위-확인) |
| [4. 대처 방안](#4-대처-방안) / [5. 사후 검증](#5-사후-검증) |

---

## 1. 개요

| 항목      | 내용                                          |
|-----------|-----------------------------------------------|
| CVE       | CVE-2026-46300                                |
| 별칭      | **Fragnesia**                                 |
| CVSS      | 미등재 (NVD 등재 전)                          |
| 공격 벡터 | LOCAL / LOW privilege / NO race condition     |
| 컴포넌트  | `net/xfrm` — `espintcp` ULP (ESP-in-TCP 경로) |
| 발견자    | William Bowling, V12 team                     |
| 발표일    | 2026-05-13                                    |
| NVD 등재  | ❌ (2026-05-18 기준 미등재)                   |
| CISA KEV  | ❌                                            |
| PoC       | ✅ 공개됨 (단일 명령어로 root 획득)           |
| 영향      | 비권한 로컬 사용자 → root 권한 상승           |

> Dirty Frag(CVE-2026-43284/43500)와 **별개 버그**입니다. 동일한 XFRM/ESP 클래스이며 임시 완화 방법은 동일합니다.

> 🟡 **Dirty Frag 완화(`dirtyfrag.conf`)를 이미 적용한 경우 추가 조치 불필요.** 동일한 `esp4`/`esp6`/`rxrpc` blacklist가 Fragnesia도 차단합니다.

> 동일 계열 취약점: [CVE-2026-31431](./cve_2026_31431_copy_fail.md) (CISA KEV) / [CVE-2026-43284](./cve_2026_43284_dirty_frag.md) (xfrm/ESP) / [CVE-2026-43500](./cve_2026_43500_dirty_frag.md) (rxrpc) / [CVE-2026-43503](./cve_2026_43503_dirty_clone.md) (DirtyClone)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 취약점 상세

> 출처: [CVE.org CVE-2026-46300](https://www.cve.org/CVERecord?id=CVE-2026-46300) / [CloudLinux Blog](https://blog.cloudlinux.com/fragnesia-mitigation-and-kernel-update)

TCP 소켓이 `espintcp` ULP 모드로 전환되기 전에 `splice(2)` / `sendfile(2)`로 파일 페이지가 수신 큐에 이미 적재된 경우, 커널이 해당 파일 페이지를 ESP 암호문으로 간주하여 **in-place 복호화**를 수행합니다.

AES-GCM 키스트림이 캐시된 파일 페이지에 XOR되며, IV nonce를 제어하면 **임의 파일의 page cache에 1바이트씩 결정론적 쓰기 프리미티브**를 획득합니다.

```
splice(2)/sendfile(2) → TCP recv queue (file pages queued)
                               ↓
          TCP socket → espintcp ULP 전환
                               ↓
          커널: 파일 페이지를 ESP 암호문으로 오인
                               ↓
          AES-GCM in-place 복호화 (IV nonce 제어)
                               ↓
          page cache 1-byte arbitrary write primitive
                               ↓
          /usr/bin/su page cache 덮어쓰기 → root
```

**공개 PoC 동작:**
- 192바이트 position-independent ELF stub을 `/usr/bin/su` page cache에 기록
- 다음 `su` 호출 시 root로 실행
- Race condition 불필요 — 단일 명령어로 root 획득

**Dirty Frag 버그 클래스 전체 구조:**

```
버그 클래스: skb/page shared frag in-place 복호화 → page cache write primitive

CVE-2026-31431   algif_aead (Copy Fail)      — Xint Code        (2026-04-22)
CVE-2026-43284   xfrm/ESP (esp4, esp6)       — @v4bel           (2026-05-07)
CVE-2026-43500   rxrpc                       — @v4bel           (2026-05-07)
CVE-2026-46300   XFRM ESP-in-TCP (Fragnesia) — William Bowling  (2026-05-13)
```

**주요 특징:**
- Race condition 불필요 — 결정론적 익스플로잇
- 디스크 파일 무변경 → AIDE/Tripwire 등 파일 무결성 도구 우회
- 재부팅 시 page cache 초기화 → 익스플로잇 흔적 소멸
- AppArmor 비특권 user namespace 제한은 **부분적** 완화만 제공

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영향 범위 확인

### 영향 배포판

| 배포판 / 버전        | 영향 여부    | 패치 버전                            |
|----------------------|--------------|--------------------------------------|
| AlmaLinux 9          | ✅ 영향 있음 | `kernel-5.14.0-611.54.5.el9_7` 이상  |
| AlmaLinux 10         | ✅ 영향 있음 | `kernel-6.12.0-124.56.3.el10_1` 이상 |
| Ubuntu Noble (24.04) | ✅ 영향 있음 | 패치 배포됨                          |
| Debian 12            | ✅ 영향 있음 | 패치 배포됨                          |
| RHEL / CentOS        | ✅ 영향 있음 | 배포판 공지 확인 필요                |
| Amazon Linux         | ✅ 영향 있음 | 배포판 공지 확인 필요                |

> 상세 upstream 취약 버전 범위는 NVD 등재 후 업데이트 예정.

### 탐지 명령어

```bash
uname -r

# 모듈 상태 및 blacklist 확인
lsmod | grep -E "^esp4|^esp6|^rxrpc"
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null || echo "blacklist 없음"

# XFRM netlink 소켓 비권한 접근 여부
python3 -c "
import socket
s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,15)
print('XFRM: OPEN (취약 가능성)')
s.close()
" 2>/dev/null || echo "XFRM: BLOCKED"
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 대처 방안

### 즉시 패치 (근본 대응)

```bash
# Ubuntu / Debian
sudo apt update && sudo apt dist-upgrade -y && sudo reboot

# RHEL / CentOS / Amazon Linux
sudo yum update kernel -y && sudo reboot
```

### 임시 완화 (패치 적용 전)

> 출처: CloudLinux Blog — [Fragnesia Mitigation and Kernel Update](https://blog.cloudlinux.com/fragnesia-mitigation-and-kernel-update) (2026-05-13)

**Dirty Frag 완화를 이미 적용한 경우 추가 조치 불필요.** `dirtyfrag.conf`가 존재하면 Fragnesia도 차단됩니다.

```bash
# 적용 여부 확인
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null || echo "미적용 — 아래 명령어 실행 필요"
```

**미적용 시 — Step 1. IPsec VPN 사용 여부 확인**

```bash
ip xfrm state list
ip xfrm policy list
```

| 모듈            | 사용 중인 경우         | 언로드 시 영향           |
|-----------------|------------------------|--------------------------|
| `esp4` / `esp6` | IPsec VPN 터널 활성    | 기존 VPN 세션 즉시 끊김  |
| `rxrpc`         | AFS 클라이언트 사용 중 | AFS 파일시스템 접근 불가 |

🟡 IPsec / strongSwan / Libreswan 터널을 종단하는 호스트에는 이 완화를 적용하지 않습니다.

**미적용 시 — Step 2. blacklist 등록 + 언로드 (원문)**

```bash
# ---- 원문 권장 ---- #
sudo sh -c "printf 'install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n' > /etc/modprobe.d/dirtyfrag.conf; rmmod esp4 esp6 rxrpc 2>/dev/null; true"
# ---- 원문 끝 ---- #
```

**Step 3. page cache 초기화 (완화 적용 후 필수)**

완화 적용 전 이미 익스플로잇이 실행됐을 가능성에 대비하여 page cache를 초기화합니다.

```bash
sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
```

**패치 후 완화 해제**

```bash
sudo rm /etc/modprobe.d/dirtyfrag.conf
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사후 검증

```bash
# 커널 버전 확인
uname -r

# 모듈 언로드 확인
lsmod | grep -E "^esp4|^esp6|^rxrpc"
# 출력 없으면 정상

# 비정상 SUID 파일 확인 (익스플로잇 흔적)
find / -perm -4000 -newer /etc/passwd 2>/dev/null

# 핵심 바이너리 무결성 확인
sudo dpkg --verify sudo bash 2>/dev/null        # Ubuntu/Debian
sudo rpm -V sudo bash coreutils 2>/dev/null     # RHEL/CentOS

# NVD 등재 확인
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-46300" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('NVD results:', d['totalResults'])"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- CloudLinux Blog: [blog.cloudlinux.com/fragnesia-mitigation-and-kernel-update](https://blog.cloudlinux.com/fragnesia-mitigation-and-kernel-update) — ★★☆☆☆
- 보안뉴스 기사: [boannews.com](https://m.boannews.com/html/detail.html?idx=143652) — ★★☆☆☆
- NVD CVE-2026-46300: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-46300) — ★★★☆☆ (등재 후 유효)
- CVE.org: [cve.org](https://www.cve.org/CVERecord?id=CVE-2026-46300) — ★★★☆☆
- [cve_2026_43284_dirty_frag.md](./cve_2026_43284_dirty_frag.md) — CVE-2026-43284 (xfrm/ESP)
- [cve_2026_43500_dirty_frag.md](./cve_2026_43500_dirty_frag.md) — CVE-2026-43500 (rxrpc)
- [cve_2026_31431_copy_fail.md](./cve_2026_31431_copy_fail.md) — CVE-2026-31431 (CISA KEV)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-18

**마지막 업데이트**: 2026-05-18

© 2026 siasia86. Licensed under CC BY 4.0.
