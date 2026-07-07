# CVE-2026-43503 — Linux Kernel skbuff frag-transfer (DirtyClone)

## 목차

| 섹션                                                                                           |
|------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 취약점 상세](#2-취약점-상세) / [3. 영향 범위 확인](#3-영향-범위-확인) |
| [4. 대처 방안](#4-대처-방안) / [5. 사후 검증](#5-사후-검증)                                    |

---

## 1. 개요

| 항목       | 내용                                                        |
|------------|-------------------------------------------------------------|
| CVE        | CVE-2026-43503                                              |
| 별칭       | **DirtyClone**                                              |
| CVSS       | 8.8 (HIGH)                                                  |
| 벡터       | `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`              |
| 공격 벡터  | LOCAL / LOW privilege / CHANGED scope / NO interaction      |
| 컴포넌트   | `net/core/skbuff.c` — `__pskb_copy_fclone()`, `skb_shift()` |
| 발견자     | Hyunwoo Kim (@v4bel) + JFrog (Eddy Tsalolikhin, Or Peles)   |
| 도입 커밋  | `cef401de7be8` (2013년)                                     |
| 패치 커밋  | `48f6a5356a33` (mainline, 2026-05-21)                       |
| NVD 공개   | 2026-05-23                                                  |
| JFrog 공개 | 2026-06-25                                                  |
| CISA KEV   | ❌                                                          |
| PoC        | ✅ 공개됨 (JFrog — page cache write via iptables TEE)       |
| 영향       | 비권한 로컬 사용자 → root 권한 상승                         |

🟡 **DirtyFrag 계열의 최신 변종입니다.** 기존 `dirtyfrag.conf` blacklist (`esp4`/`esp6`/`rxrpc`)를 이미 적용한 경우 추가 조치 불필요합니다.

> 동일 계열 취약점: [CVE-2026-31431](./cve_2026_31431_copy_fail.md) (CISA KEV) / [CVE-2026-43284](./cve_2026_43284_dirty_frag.md) (xfrm/ESP) / [CVE-2026-43500](./cve_2026_43500_dirty_frag.md) (rxrpc) / [CVE-2026-46300](./cve_2026_46300_fragnesia.md) (Fragnesia)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 취약점 상세

> 출처: [JFrog Research — DirtyClone](https://research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503/) / [NVD CVE-2026-43503](https://nvd.nist.gov/vuln/detail/CVE-2026-43503) / [커널 패치 커밋](https://git.kernel.org/stable/c/9bc9d6d6967a2239aa57af2aa53554eddd640d20)

`__pskb_copy_fclone()`과 `skb_shift()`가 frag descriptor를 복사할 때 `SKBFL_SHARED_FRAG` 비트를 전파하지 않습니다. `iptables TEE`(`nf_dup_ipv4()`) 규칙이 존재하면 `__pskb_copy_fclone()`을 통해 skb가 복제되며, 복제된 skb에서 shared frag 마커가 사라집니다.

이 skb가 loopback IPsec 경로의 `esp_input()`에 도달하면 커널이 `skb_cow_data()` 없이 **in-place 복호화**를 수행하여 page cache를 직접 덮어씁니다.

```
vmsplice/splice → UDP skb (page-cache backed)
                       ↓
          iptables TEE → __pskb_copy_fclone()
                       ↓
          cloned skb (SKBFL_SHARED_FRAG bit LOST)
                       ↓
          loopback IPsec → esp_input() (no COW)
                       ↓
          AES-CBC in-place decrypt → page cache write
                       ↓
          /usr/bin/su page cache overwrite → root
```

**기존 DirtyFrag 패치와의 차이:**

| CVE            | 버그 위치                 | 마커 누락 경로      |
|----------------|---------------------------|---------------------|
| CVE-2026-43284 | `ip_append_data()` splice | UDP splice → ESP    |
| CVE-2026-46300 | `skb_try_coalesce()`      | GRO coalesce → ESP  |
| CVE-2026-43503 | `__pskb_copy_fclone()`    | TEE/dup clone → ESP |

**패치 내용:** frag descriptor 이동 시 `SKBFL_SHARED_FRAG` 비트를 destination skb에도 설정합니다. 수정 대상: `__pskb_copy_fclone()`, `skb_shift()`, `skb_gro_receive()`, `skb_gro_receive_list()`, `tcp_clone_payload()`, `skb_segment()`.

**취약 버전:**

| 브랜치 | 취약 범위       | 패치 버전     | RHEL/CentOS          | Ubuntu           | Amazon Linux      |
|--------|-----------------|---------------|----------------------|------------------|-------------------|
| 5.10.x | 3.9 ~ 5.10.256  | **5.10.257+** | RHEL 8 (백포트 확인) | 20.04 LTS (HWE)  | AL2 (5.10 kernel) |
| 5.15.x | 5.11 ~ 5.15.207 | **5.15.208+** | RHEL 9.0~9.2         | 22.04 LTS        | AL2023            |
| 6.1.x  | 5.16 ~ 6.1.173  | **6.1.174+**  | RHEL 9.3~9.4         | 22.04 LTS (HWE)  | AL2023 (6.1)      |
| 6.6.x  | 6.2 ~ 6.6.140   | **6.6.141+**  | RHEL 9.5+            | 24.04 LTS        | AL2023 (6.6)      |
| 6.12.x | 6.7 ~ 6.12.90   | **6.12.91+**  | RHEL 10              | **24.04 LTS** 🟡 | —                 |
| 6.18.x | 6.13 ~ 6.18.32  | **6.18.33+**  | —                    | 25.04            | —                 |
| 7.0.x  | 6.19 ~ 7.0.9    | **7.0.10+**   | —                    | 25.10 (예정)     | —                 |

> 첫 패치 태그: v7.1-rc5 (2026-05-24)

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영향 범위 확인

### 익스플로잇 조건

| 조건                     | 설명                                           |
|--------------------------|------------------------------------------------|
| `CAP_NET_ADMIN`          | IPsec SA/policy 및 iptables 설정에 필요        |
| 비권한 user namespace    | Debian/Fedora/Ubuntu 기본 활성 → userns로 획득 |
| iptables TEE 또는 nf_dup | `__pskb_copy_fclone()` 트리거에 필요           |
| ESP 모듈 (`esp4`/`esp6`) | in-place decrypt 경로                          |

### JFrog 확인 배포판

| 배포판 | 익스플로잇 결과 |
|--------|-----------------|
| Debian | ✅ root 획득    |
| Ubuntu | ✅ root 획득    |
| Fedora | ✅ root 획득    |

### 탐지 명령어

```bash
uname -r

# 패치 적용 여부 (Ubuntu)
apt-get changelog linux-image-$(uname -r) 2>/dev/null | grep CVE-2026-43503 | head -3

# 패치 적용 여부 (RHEL/CentOS)
rpm -q --changelog kernel | grep CVE-2026-43503 | head -3

# 모듈 및 blacklist 상태
lsmod | grep -E "^esp4|^esp6|^rxrpc"
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null || echo "blacklist 없음"

# unprivileged userns 상태
cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || \
sysctl kernel.unprivileged_userns_clone 2>/dev/null || echo "확인 불가"
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

# 재부팅 후 확인
uname -r
```

### 임시 완화 (패치 적용 전)

> 출처: [JFrog Research](https://research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503/) — Staying Safe (Mitigation) 섹션

**Dirty Frag 완화를 이미 적용한 경우 추가 조치 불필요합니다.** `dirtyfrag.conf`가 존재하면 DirtyClone도 차단됩니다.

```bash
# 적용 여부 확인
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null || echo "미적용 — 아래 Step 실행 필요"
```

**미적용 시 — 방법 A. 모듈 blacklist (기존 DirtyFrag 완화와 동일)**

```bash
# Step 1. IPsec VPN 사용 여부 확인
ip xfrm state list
ip xfrm policy list

# Step 2. blacklist 등록 + 언로드
sudo sh -c 'printf "install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n" \
  > /etc/modprobe.d/dirtyfrag.conf'
sudo rmmod esp4 esp6 rxrpc 2>/dev/null || true

# Step 3. page cache 초기화
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
```

| 모듈            | 사용 중인 경우         | 언로드 시 영향           |
|-----------------|------------------------|--------------------------|
| `esp4` / `esp6` | IPsec VPN 터널 활성    | 기존 VPN 세션 즉시 끊김  |
| `rxrpc`         | AFS 클라이언트 사용 중 | AFS 파일시스템 접근 불가 |

🟡 IPsec / strongSwan / Libreswan 터널을 종단하는 호스트에는 방법 B를 사용합니다.

**미적용 시 — 방법 B. unprivileged userns 비활성화**

```bash
# CAP_NET_ADMIN 비권한 획득 차단
sudo sysctl -w kernel.unprivileged_userns_clone=0
echo "kernel.unprivileged_userns_clone=0" | sudo tee /etc/sysctl.d/99-no-userns.conf
```

🟡 이 방법은 비권한 userns에 의존하는 애플리케이션(Chrome sandbox, Flatpak 등)에 영향을 줄 수 있습니다.

**패치 후 완화 해제:**

```bash
sudo rm /etc/modprobe.d/dirtyfrag.conf
# 또는
sudo rm /etc/sysctl.d/99-no-userns.conf && sudo sysctl -w kernel.unprivileged_userns_clone=1
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

# 핵심 바이너리 무결성 확인
sudo dpkg --verify sudo bash su 2>/dev/null        # Ubuntu/Debian
sudo rpm -V sudo bash coreutils 2>/dev/null        # RHEL/CentOS

# page cache 초기화 (익스플로잇 흔적 제거)
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- JFrog Research: [research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503](https://research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503/) — ★★★☆☆
- NVD CVE-2026-43503: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43503) — ★★★☆☆
- Linux Kernel Patch (mainline): [git.kernel.org](https://git.kernel.org/stable/c/9bc9d6d6967a2239aa57af2aa53554eddd640d20) — ★★★★☆
- 데일리시큐 기사: [dailysecu.com](https://www.dailysecu.com/news/articleView.html?idxno=207338) — ★★☆☆☆
- [cve_2026_31431_copy_fail.md](./cve_2026_31431_copy_fail.md) — CVE-2026-31431 (Copy Fail / CISA KEV)
- [cve_2026_43284_dirty_frag.md](./cve_2026_43284_dirty_frag.md) — CVE-2026-43284 (Dirty Frag / xfrm ESP)
- [cve_2026_43500_dirty_frag.md](./cve_2026_43500_dirty_frag.md) — CVE-2026-43500 (Dirty Frag / rxrpc)
- [cve_2026_46300_fragnesia.md](./cve_2026_46300_fragnesia.md) — CVE-2026-46300 (Fragnesia)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-06-29

**마지막 업데이트**: 2026-06-29

© 2026 siasia86. Licensed under CC BY 4.0.
