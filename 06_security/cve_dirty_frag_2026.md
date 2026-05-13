# Linux Kernel CVE — Dirty Frag (CVE-2026-43284 / CVE-2026-43500)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. CVE 상세](#2-cve-상세) / [3. 영향 범위 확인](#3-영향-범위-확인) |
| [4. 대처 방안](#4-대처-방안) / [5. 사후 검증](#5-사후-검증) |

---

## 1. 개요

**Dirty Frag** (Copy Fail 2)는 2026년 5월 7일 보안 연구자 Hyunwoo Kim(@v4bel)이 공개한 Linux 커널 로컬 권한 상승 취약점입니다. 엠바고 파기로 인해 패치 준비 전 조기 공개됐습니다.

`splice(2)` / `sendfile(2)` 로 page cache 페이지를 소켓 버퍼(skb)에 연결할 때 복호화 경로가 외부 소유 페이지에 **in-place 복호화**를 수행하여 **page cache 임의 쓰기 프리미티브**를 제공합니다. 비권한 로컬 사용자가 root 권한을 획득합니다.

- 레이스 컨디션 없음 — 단일 명령으로 안정적 root 획득
- PoC 공개됨 — 실제 악용 중으로 간주

| CVE | CVSS | 심각도 | CISA KEV | 컴포넌트 |
|-----|------|--------|----------|---------|
| CVE-2026-43284 | 8.8 | HIGH | ❌ | `xfrm/ESP` (`esp4`, `esp6`) |
| CVE-2026-43500 | 7.8 | HIGH | ❌ | `rxrpc` |

> 동일 계열 취약점 CVE-2026-31431 (`algif_aead`, CISA KEV 등재)은 [cve_linux_kernel_2026.md](./cve_linux_kernel_2026.md) 참고.

[⬆ 목차로 돌아가기](#목차)

---

## 2. CVE 상세

### CVE-2026-43284 — Linux Kernel `xfrm/ESP` (IPsec)

- **발표일**: 2026-05-08 (공개: 2026-05-07)
- **발견자**: Hyunwoo Kim (@v4bel)
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
              → 메모리 손상 / 데이터 변조 / 권한 상승
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

### CVE-2026-43500 — Linux Kernel `rxrpc`

- **발표일**: 2026-05-11 (공개: 2026-05-07)
- **발견자**: Hyunwoo Kim (@v4bel)
- **CVSS**: 7.8 (LOCAL / LOW privilege)
- **컴포넌트**: `net/rxrpc` (RxRPC 프로토콜, `rxrpc` 모듈)
- **도입 커밋**: `2dc334f1a63a` (2023년 6월)
- **패치 커밋**: `aa54b1d27fe0` (2026-05-10)

**취약점 내용:**

`rxrpc` DATA/RESPONSE 패킷 처리 시 `skb_cloned()` 체크만 수행하고 `skb_has_frag_list()` / `skb_has_shared_frag()` 는 체크하지 않습니다. `splice()` 루프백 벡터 등으로 외부 소유 frag 페이지가 AEAD/skcipher SGL에 직접 바인딩되어 **in-place 복호화**가 수행됩니다.

**패치 내용:** `skb_has_frag_list()` 또는 `skb_has_shared_frag()` 가 true일 때도 unshare 처리하도록 gate 확장.

**취약 버전:**

| 브랜치 | 취약 범위    | 패치 버전    | RHEL/CentOS          | Ubuntu       | Amazon Linux |
|--------|-------------|-------------|----------------------|--------------|--------------|
| ~6.18  | ~ 6.18.28   | **6.18.29+** | RHEL 8~10 (백포트 확인) | 20.04~25.04 | AL2, AL2023  |
| 6.19.x | 6.19 ~ 7.0.5 | **7.0.6+** | —                    | 25.10 (예정) | —            |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영향 범위 확인

### Ubuntu 24.04 실제 테스트 결과 (2026-05-13)

테스트 환경: Ubuntu 24.04.4 LTS / kernel `6.8.0-101-generic`

| 항목 | 결과 | 비고 |
|------|------|------|
| CVE-2026-43284 패치 | ❌ 미적용 | Ubuntu 백포트 미배포 (2026-05-13 기준) |
| CVE-2026-43500 패치 | ❌ 미적용 | upstream 패치 2026-05-10, 배포판 백포트 진행 중 |
| `esp4` 모듈 | ❌ 취약 | 미로드, auto-load 가능, blacklist 없음 |
| `esp6` 모듈 | ❌ 취약 | 미로드, auto-load 가능, blacklist 없음 |
| `rxrpc` 모듈 | ❌ 취약 | 미로드, auto-load 가능, blacklist 없음 |
| XFRM netlink 소켓 | ❌ 취약 | 비권한 사용자 접근 가능 |
| AF_RXRPC 소켓 | ✅ 안전 | rxrpc 미로드로 접근 불가 |

### 탐지 명령어

```bash
# 커널 버전 확인
uname -r

# 모듈 로드/blacklist 상태
lsmod | grep -E "^esp4|^esp6|^rxrpc"
grep -r "esp4\|esp6\|rxrpc" /etc/modprobe.d/ 2>/dev/null

# XFRM netlink 소켓 비권한 접근 여부
python3 -c "
import socket
s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,15)
print('XFRM: OPEN (취약)')
s.close()
" 2>/dev/null || echo "XFRM: BLOCKED"

# DirtyFrag-Detector 실행 (root 불필요)
curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
rm -f dirty_frag_detect.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 대처 방안

### 즉시 패치

```bash
# RHEL / CentOS / Amazon Linux
sudo yum update kernel -y && sudo reboot

# Ubuntu / Debian
sudo apt update && sudo apt dist-upgrade -y && sudo reboot
```

### 임시 완화 (패치 적용 전)

> 출처: [github.com/0xBlackash/CVE-2026-43284](https://github.com/0xBlackash/CVE-2026-43284) — Mitigation & Remediation 섹션
> 출처: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — Recommended immediate actions 섹션

**Step 1. 모듈 사용 여부 사전 확인**

```bash
# esp4/esp6: 활성 IPsec SA/정책 확인
ip xfrm state list
ip xfrm policy list

# rxrpc: AFS 마운트 확인
mount | grep afs

# 현재 로드 상태 확인
lsmod | grep -E "^esp4|^esp6|^rxrpc"
```

| 모듈 | 사용 중인 경우 | 언로드 시 영향 |
|------|--------------|----------------|
| `esp4` / `esp6` | IPsec VPN 터널 활성 | 기존 VPN 세션 즉시 끊김, 패킷 드롭 |
| `esp4` / `esp6` | strongSwan / Libreswan 실행 중 | 데몬이 모듈 재로드 시도 — blacklist 있으면 실패 |
| `rxrpc` | AFS 마운트 포인트 사용 중 | AFS 파일시스템 접근 불가, I/O 에러 |

**Step 2. modprobe.d 백업 확인**

```bash
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null || echo "파일 없음 — 안전하게 생성 가능"
sudo cp /etc/modprobe.d/dirtyfrag.conf /etc/modprobe.d/dirtyfrag.conf.bak 2>/dev/null
```

**Step 3. blacklist 생성 + 언로드 (원문)**

⚠️ `>` 는 파일을 덮어씁니다. Step 2에서 백업 확인 후 실행합니다.

```bash
# ---- 원문 (DirtyFrag-Detector / CVE-2026-43284 PoC 권장) ---- #
sudo sh -c 'printf "install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n" \
  > /etc/modprobe.d/dirtyfrag.conf'

sudo rmmod esp4 esp6 rxrpc 2>/dev/null || true

echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
# ---- 원문 끝 ---- #
```

모듈이 사용 중이면 `rmmod` 가 `Module is in use` 오류로 실패합니다:

```bash
# 서비스 중지 후 재시도
sudo systemctl stop strongswan-starter 2>/dev/null || sudo systemctl stop ipsec 2>/dev/null
sudo modprobe -r esp4 esp6

# 그래도 실패 시 — 의존 모듈 확인 후 재부팅
for mod in esp4 esp6 rxrpc; do
    if lsmod | grep -q "^${mod} "; then
        echo "[WARN] ${mod} 언로드 실패:"
        cat /proc/modules | grep "^${mod} " | awk '{print "  used by:", $4}'
    fi
done
```

**Step 4. 언로드 결과 확인**

```bash
lsmod | grep -E "^esp4|^esp6|^rxrpc"
# 출력 없으면 정상 언로드
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사후 검증

```bash
# 모듈 상태 확인
lsmod | grep -E "^esp4|^esp6|^rxrpc"

# DirtyFrag-Detector 재실행
curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
rm -f dirty_frag_detect.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- NVD CVE-2026-43284: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43284) — ★★★☆☆
- NVD CVE-2026-43500: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43500) — ★★★☆☆
- Dirty Frag PoC (CVE-2026-43284): [github.com/0xBlackash/CVE-2026-43284](https://github.com/0xBlackash/CVE-2026-43284) — ★★☆☆☆
- DirtyFrag-Detector: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — ★★☆☆☆
- Linux Kernel Patch (CVE-2026-43284): [git.kernel.org](https://git.kernel.org/stable/c/f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4) — ★★★★☆
- [cve_linux_kernel_2026.md](./cve_linux_kernel_2026.md) — CVE-2026-31431 (CISA KEV)

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
