# Linux Kernel CVE — Dirty Frag (2026)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 긴급 — CVE-2026-31431 CISA KEV](#2-긴급--cve-2026-31431-cisa-kev) / [3. CVE 상세](#3-cve-상세) |
| [4. 영향 범위 확인](#4-영향-범위-확인) / [5. 대처 방안](#5-대처-방안) / [6. 사후 검증](#6-사후-검증) |

---

## 1. 개요

**Dirty Frag** (Copy Fail 2)는 2026년 5월 7일 보안 연구자 Hyunwoo Kim(@v4bel)이 공개한 Linux 커널 로컬 권한 상승 취약점입니다. 엠바고 파기로 인해 패치 준비 전 조기 공개됐습니다.

`splice(2)` / `sendfile(2)` 로 page cache 페이지를 소켓 버퍼(skb)에 연결할 때 복호화 경로가 외부 소유 페이지에 **in-place 복호화**를 수행하여 **page cache 임의 쓰기 프리미티브**를 제공합니다. 이를 통해 비권한 로컬 사용자가 root 권한을 획득합니다.

- 레이스 컨디션 없음 — 단일 명령으로 안정적 root 획득
- PoC 공개됨 — 실제 악용 중으로 간주

| CVE | CVSS | 심각도 | CISA KEV | 조치 기한 | 직접 기재 |
|-----|------|--------|----------|-----------|-----------|
| ★ CVE-2026-31431 | 7.8 | HIGH | ✅ **등재** | **2026-05-15** | ✅ |
| ★ CVE-2026-43284 | 8.8 | HIGH | ❌ | — | ✅ |
| ★ CVE-2026-43500 | 7.8 | HIGH | ❌ | — | ✅ |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 긴급 — CVE-2026-31431 CISA KEV

> ⚠️ **조치 기한: 2026-05-15** — CISA KEV 등재. 실제 익스플로잇 확인됨. 즉시 패치 또는 완화 조치 필요.

CVE-2026-31431은 Dirty Frag 계열이지만 **별도 CVE**로 CISA KEV에 등재된 독립적인 취약점입니다.
CVE-2026-43284 / CVE-2026-43500 (xfrm/rxrpc)과 달리 `crypto/algif_aead` 컴포넌트를 통해 익스플로잇됩니다.

```bash
# 즉시 완화 — algif_aead 모듈 차단
sudo rmmod algif_aead 2>/dev/null || true
echo "install algif_aead /bin/false" | sudo tee /etc/modprobe.d/disable-algif-aead.conf

# 즉시 패치 (커널 업데이트)
# RHEL / CentOS / Amazon Linux
sudo yum update kernel -y && sudo reboot

# Ubuntu / Debian
sudo apt update && sudo apt dist-upgrade -y && sudo reboot
```

| 항목 | 내용 |
|------|------|
| CISA KEV 등재 | 2026-05-01 |
| 조치 기한 | **2026-05-15** |
| 컴포넌트 | `crypto/algif_aead` |
| 영향 | 비권한 로컬 사용자 → root 권한 상승 |
| PoC | 공개됨 (copy.fail) |

상세 내용은 [섹션 3. CVE 상세](#3-cve-상세) 참고.

[⬆ 목차로 돌아가기](#목차)

---

## 3. CVE 상세

### ★ CVE-2026-31431 — Linux Kernel `crypto/algif_aead` ⚠️ CISA KEV

- **발표일**: 2026-04-22
- **CVSS**: 7.8 (LOCAL / LOW privilege / NO interaction)
- **CWE**: CWE-669 (Incorrect Resource Transfer Between Spheres)
- **컴포넌트**: `crypto/algif_aead` (커널 암호화 소켓 인터페이스)

**취약점 내용:**

`algif_aead`에서 in-place 복호화 시 `skb_cloned()` 체크만 수행하고 `skb_has_frag_list()` / `skb_has_shared_frag()` 는 체크하지 않습니다. `splice()`로 UDP 소켓에 연결된 shared frag 페이지를 AEAD 복호화 경로에 전달하면 **page cache를 직접 덮어쓸 수 있어 권한 상승**이 가능합니다.

```
splice() → UDP socket → shared frag pages
                              ↓
                    algif_aead 복호화 (in-place)
                              ↓
                    page cache 덮어쓰기 → 권한 상승
```

**취약 버전:**

| 브랜치 | 취약 범위       | 패치 버전      | RHEL/CentOS       | Ubuntu            | Amazon Linux      |
|--------|-----------------|----------------|-------------------|-------------------|-------------------|
| 5.10.x | 4.14 ~ 5.10.253 | **5.10.254+**  | RHEL 8 (백포트 확인) | 20.04 LTS (HWE) | AL2 (5.10 kernel) |
| 5.15.x | 5.11 ~ 5.15.203 | **5.15.204+**  | RHEL 9.0~9.2      | 22.04 LTS         | AL2023            |
| 6.1.x  | 5.16 ~ 6.1.169  | **6.1.170+**   | RHEL 9.3~9.4      | 22.04 LTS (HWE)   | AL2023 (6.1)      |
| 6.6.x  | 6.2 ~ 6.6.136   | **6.6.137+**   | RHEL 9.5+         | 24.04 LTS         | AL2023 (6.6)      |
| 6.12.x | 6.7 ~ 6.12.84   | **6.12.85+**   | RHEL 10           | **24.04 LTS** ⚠️  | —                 |
| 6.18.x | 6.13 ~ 6.18.21  | **6.18.22+**   | —                 | 25.04             | —                 |
| 6.19.x | 6.19 ~ 6.19.11  | **6.19.12+**   | —                 | 25.10 (예정)      | —                 |

⚠️ 실제 익스플로잇 공개됨. CISA KEV 등재 (조치 기한: **2026-05-15**).

> RHEL/CentOS는 자체 백포트 패치를 적용하므로 upstream 버전과 다릅니다. `rpm -q --changelog kernel | grep CVE-2026-31431` 으로 패치 포함 여부를 직접 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

### ★ CVE-2026-43284 — Linux Kernel `xfrm/ESP` (IPsec) — Dirty Frag

- **발표일**: 2026-05-08 (공개: 2026-05-07)
- **발견자**: Hyunwoo Kim (@v4bel)
- **별칭**: Dirty Frag / Copy Fail 2
- **CVSS**: 8.8 (LOCAL / LOW privilege / CHANGED scope)
- **컴포넌트**: `net/ipv4`, `net/ipv6` — ESP-in-UDP (`esp4`, `esp6` 모듈)
- **도입 커밋**: `cac2661c53f3` (2017년 1월)
- **패치 커밋**: `f4c50a4034e6` (2026-05-07)

**취약점 내용:**

`MSG_SPLICE_PAGES`로 pipe 페이지를 UDP skb에 붙일 때 IPv4/IPv6 datagram append 경로가 `SKBFL_SHARED_FRAG` 플래그를 설정하지 않습니다. ESP input이 uncloned skb로 판단하여 **외부 소유 메모리에 in-place 복호화**를 수행합니다.

```
MSG_SPLICE_PAGES → UDP skb (SKBFL_SHARED_FRAG 미설정)
                        ↓
              ESP input (no-COW fast path)
                        ↓
              외부 소유 frag 페이지 in-place 복호화
              → 메모리 손상 / 데이터 변조
```

**패치 내용:** IPv4/IPv6 datagram splice 시 `SKBFL_SHARED_FRAG` 설정 + ESP input에서 해당 플래그 존재 시 `skb_cow_data()` 호출로 fallback.

**취약 버전:**

| 브랜치 | 취약 범위       | 패치 버전      | RHEL/CentOS       | Ubuntu            | Amazon Linux      |
|--------|-----------------|----------------|-------------------|-------------------|-------------------|
| 5.10.x | 4.11 ~ 5.10.254 | **5.10.255+**  | RHEL 8 (백포트 확인) | 20.04 LTS (HWE) | AL2 (5.10 kernel) |
| 5.15.x | 5.12 ~ 5.15.204 | **5.15.205+**  | RHEL 9.0~9.2      | 22.04 LTS         | AL2023            |
| 6.1.x  | 5.16 ~ 6.1.170  | **6.1.171+**   | RHEL 9.3~9.4      | 22.04 LTS (HWE)   | AL2023 (6.1)      |
| 6.6.x  | 6.2 ~ 6.6.137   | **6.6.138+**   | RHEL 9.5+         | 24.04 LTS         | AL2023 (6.6)      |
| 6.12.x | 6.7 ~ 6.12.86   | **6.12.87+**   | RHEL 10           | **24.04 LTS** ⚠️  | —                 |
| 6.18.x | 6.13 ~ 6.18.27  | **6.18.28+**   | —                 | 25.04             | —                 |
| 7.0.x  | 7.0 ~ 7.0.4     | **7.0.5+**     | —                 | 25.10 (예정)      | —                 |

[⬆ 목차로 돌아가기](#목차)

---

### ★ CVE-2026-43500 — Linux Kernel `rxrpc` — Dirty Frag

- **발표일**: 2026-05-11 (공개: 2026-05-07)
- **발견자**: Hyunwoo Kim (@v4bel)
- **별칭**: Dirty Frag / Copy Fail 2
- **CVSS**: 7.8 (LOCAL / LOW privilege)
- **컴포넌트**: `net/rxrpc` (RxRPC 프로토콜, `rxrpc` 모듈)
- **도입 커밋**: `2dc334f1a63a` (2023년 6월)
- **패치 커밋**: `aa54b1d27fe0` (2026-05-10)

**취약점 내용:**

`rxrpc` DATA/RESPONSE 패킷 처리 시 `skb_cloned()` 체크만 수행하고 `skb_has_frag_list()` / `skb_has_shared_frag()` 는 체크하지 않습니다. `splice()` 루프백 벡터 등으로 외부 소유 frag 페이지가 AEAD/skcipher SGL에 직접 바인딩되어 **in-place 복호화**가 수행됩니다.

**패치 내용:** `skb_has_frag_list()` 또는 `skb_has_shared_frag()` 가 true일 때도 unshare 처리하도록 gate 확장.

**취약 버전:**

| 브랜치 | 취약 범위       | 패치 버전      | RHEL/CentOS       | Ubuntu            | Amazon Linux      |
|--------|-----------------|----------------|-------------------|-------------------|-------------------|
| ~6.18  | ~ 6.18.28       | **6.18.29+**   | RHEL 8~10 (백포트 확인) | 20.04~25.04  | AL2, AL2023       |
| 6.19.x | 6.19 ~ 7.0.5    | **7.0.6+**     | —                 | 25.10 (예정)      | —                 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 영향 범위 확인

### Ubuntu 24.04 실제 테스트 결과 (2026-05-13)

테스트 환경: Ubuntu 24.04.4 LTS / kernel `6.8.0-101-generic`

| 항목 | 결과 | 비고 |
|------|------|------|
| 커널 버전 | ❌ 취약 | 6.8.0-101 — CVE-2026-43284/43500 취약 범위 |
| CVE-2026-43284 패치 | ❌ 미적용 | Ubuntu 백포트 미배포 (2026-05-13 기준) |
| CVE-2026-43500 패치 | ❌ 미적용 | upstream 패치 2026-05-10, 배포판 백포트 진행 중 |
| CVE-2026-31431 패치 | ⚠️ 미확인 | `algif_aead` blacklist 적용으로 완화됨 |
| `esp4` 모듈 | ❌ 취약 | 미로드, auto-load 가능, blacklist 없음 |
| `esp6` 모듈 | ❌ 취약 | 미로드, auto-load 가능, blacklist 없음 |
| `rxrpc` 모듈 | ❌ 취약 | 미로드, auto-load 가능, blacklist 없음 |
| `algif_aead` 모듈 | ✅ 완화 | `/etc/modprobe.d/` blacklist 적용됨 |
| XFRM netlink 소켓 | ❌ 취약 | 비권한 사용자 접근 가능 |
| AF_RXRPC 소켓 | ✅ 안전 | rxrpc 미로드로 접근 불가 |
| AppArmor | ✅ 활성 | 완전 차단은 아님, 정책 확인 필요 |
| SELinux | ❌ 비활성 | Ubuntu 기본값 |
| 비권한 user namespace | ❌ 활성 | `kernel.unprivileged_userns_clone=1` |

**결론: CVE-2026-43284 / CVE-2026-43500 즉시 완화 조치 필요**

### 탐지 명령어

```bash
# 커널 버전 확인
uname -r

# RHEL/CentOS 패치 적용 여부
rpm -q --changelog kernel | grep -E "CVE-2026-31431|CVE-2026-43284|CVE-2026-43500" | head -5

# Ubuntu 패치 적용 여부
apt-get changelog linux-image-$(uname -r) 2>/dev/null | grep -E "CVE-2026-31431|CVE-2026-43284|CVE-2026-43500" | head -5

# 모듈 로드/blacklist 상태
lsmod | grep -E "esp4|esp6|rxrpc|algif"
grep -r "esp4\|esp6\|rxrpc\|algif_aead" /etc/modprobe.d/ 2>/dev/null

# XFRM netlink 소켓 비권한 접근 여부
python3 -c "import socket; s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,15); print('XFRM: OPEN (취약)'); s.close()" 2>/dev/null || echo "XFRM: BLOCKED"

# DirtyFrag-Detector 실행 (root 불필요)
curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
rm -f dirty_frag_detect.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대처 방안

### 즉시 조치 (CVE-2026-31431 — CISA KEV, 기한 2026-05-15)

```bash
# RHEL / CentOS / Amazon Linux
sudo yum update kernel -y
sudo reboot

# Ubuntu / Debian
sudo apt update && sudo apt dist-upgrade -y
sudo reboot

# 재부팅 후 버전 확인
uname -r
```

### 임시 완화 (패치 적용 전)

> 출처: [github.com/0xBlackash/CVE-2026-43284](https://github.com/0xBlackash/CVE-2026-43284) — Mitigation & Remediation 섹션
> 출처: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — Recommended immediate actions 섹션

```bash
# ---- 원문 (DirtyFrag-Detector / CVE-2026-43284 PoC 권장) ---- #
# Dirty Frag 취약 모듈 일괄 차단 (CVE-2026-43284 + CVE-2026-43500)
sudo sh -c 'printf "install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n" \
  > /etc/modprobe.d/dirtyfrag.conf'

# 모듈 즉시 언로드
sudo rmmod esp4 esp6 rxrpc 2>/dev/null || true

# page cache 즉시 드롭
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
# ---- 원문 끝 ---- #
```

⚠️ `esp4` / `esp6` 언로드 시 IPsec VPN 중단됩니다. `rxrpc` 언로드 시 AFS(Andrew File System) 사용 불가합니다.

**모듈이 이미 로드되어 사용 중일 때 발생하는 문제:**

| 모듈 | 사용 중인 경우 | 언로드 시 영향 |
|------|--------------|----------------|
| `esp4` / `esp6` | IPsec VPN 터널 활성 상태 | 기존 VPN 세션 즉시 끊김, 패킷 드롭 |
| `esp4` / `esp6` | strongSwan / Libreswan 데몬 실행 중 | 데몬이 모듈 재로드 시도 — blacklist 있으면 실패 |
| `rxrpc` | AFS 마운트 포인트 사용 중 | 마운트된 AFS 파일시스템 접근 불가, I/O 에러 |
| `algif_aead` | OpenSSL / GnuTLS AF_ALG 엔진 사용 중 | 암호화 연산 실패, 애플리케이션 오류 |

```bash
# 언로드 전 사용 여부 확인
# esp4/esp6: 활성 IPsec SA 확인
ip xfrm state list
ip xfrm policy list

# rxrpc: AFS 마운트 확인
mount | grep afs
cat /proc/mounts | grep afs

# algif_aead: AF_ALG 소켓 사용 프로세스 확인
ss -A alg 2>/dev/null | head -10
```

모듈이 사용 중이면 `rmmod` 는 `Module is in use` 오류로 실패합니다. 이 경우:
1. 해당 서비스를 먼저 중지 후 언로드
2. 또는 재부팅 후 blacklist가 적용된 상태로 부팅

```bash
# 예: strongSwan 중지 후 esp 모듈 언로드
sudo systemctl stop strongswan-starter 2>/dev/null || sudo systemctl stop ipsec 2>/dev/null
sudo modprobe -r esp4 esp6
```

모듈이 실제로 로드된 경우 언로드 성공 여부를 확인합니다:

```bash
# 언로드 후 상태 확인
lsmod | grep -E "^esp4|^esp6|^rxrpc"
# 출력 없으면 정상 언로드

# rmmod 실패 시 (다른 모듈이 의존 중인 경우) — 의존 모듈 포함 언로드
sudo modprobe -r esp4 esp6 rxrpc 2>/dev/null

# 그래도 실패 시 — 사용 중인 프로세스 확인
for mod in esp4 esp6 rxrpc; do
    if lsmod | grep -q "^${mod} "; then
        echo "[WARN] ${mod} 언로드 실패 — 사용 중:"
        cat /proc/modules | grep "^${mod} " | awk '{print "  used by:", $4}'
    fi
done
```

```bash
# algif_aead 모듈 언로드 (CVE-2026-31431)
# ⚠️ AF_ALG 소켓을 사용하는 애플리케이션 영향 가능
sudo rmmod algif_aead
echo "install algif_aead /bin/false" | sudo tee /etc/modprobe.d/disable-algif-aead.conf
```

### 배포판별 보안 공지

| 배포판 | 공지 URL |
|--------|---------|
| RHEL/CentOS | https://access.redhat.com/security/cve/CVE-2026-31431 |
| Ubuntu | https://ubuntu.com/security/CVE-2026-31431 |
| Debian | https://security-tracker.debian.org/tracker/CVE-2026-31431 |
| Amazon Linux | https://alas.aws.amazon.com/ |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 사후 검증

```bash
# 패치 적용 후 커널 버전 확인
uname -r

# CVE-2026-31431 패치 커밋 포함 여부 (kernel.org)
# 5.10.254+, 5.15.204+, 6.1.170+, 6.6.137+, 6.12.85+ 확인

# 모듈 상태 재확인
lsmod | grep -E "algif|rxrpc|esp4|esp6"

# DirtyFrag-Detector 탐지 스크립트 실행 (root 불필요)
curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
```

탐지 항목:
- 커널 버전 취약 범위 여부
- `esp4` / `esp6` / `rxrpc` 모듈 로드/로드 가능/차단 상태
- XFRM netlink 소켓 비권한 접근 가능 여부
- AF_RXRPC 소켓 비권한 접근 가능 여부
- AppArmor / SELinux / 비권한 user namespace 완화 적용 여부

```bash
# CISA KEV 최신 목록 확인
curl -s "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" \
  | python3 -c "
import sys,json
data=json.load(sys.stdin)
linux=[v for v in data['vulnerabilities'] if 'linux' in v.get('product','').lower()]
linux_sorted=sorted(linux,key=lambda x:x['dateAdded'],reverse=True)
for v in linux_sorted[:5]:
    print(v['cveID'], v['dateAdded'], v['dueDate'])
"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- NVD CVE-2026-31431: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-31431) — ★★★☆☆
- NVD CVE-2026-43284: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43284) — ★★★☆☆
- NVD CVE-2026-43500: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43500) — ★★★☆☆
- CISA KEV Catalog: [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) — ★★★☆☆
- Dirty Frag PoC (CVE-2026-43284): [github.com/0xBlackash/CVE-2026-43284](https://github.com/0xBlackash/CVE-2026-43284) — ★★☆☆☆
- DirtyFrag-Detector 탐지 스크립트: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — ★★☆☆☆
- Linux Kernel Patch (CVE-2026-31431): [git.kernel.org](https://git.kernel.org/stable/c/19d43105a97be0810edbda875f2cd03f30dc130c) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-13

**마지막 업데이트**: 2026-05-13

© 2026 siasia86. Licensed under CC BY 4.0.
