# CVE-2026-43284 — Linux Kernel xfrm/ESP (Dirty Frag)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 취약점 상세](#2-취약점-상세) / [3. 영향 범위 확인](#3-영향-범위-확인) |
| [4. 대처 방안](#4-대처-방안) / [5. 사후 검증](#5-사후-검증) |

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| CVE | CVE-2026-43284 |
| 별칭 | Dirty Frag / Copy Fail 2 |
| CVSS | 8.8 (HIGH) |
| 공격 벡터 | LOCAL / LOW privilege / CHANGED scope |
| 컴포넌트 | `net/ipv4`, `net/ipv6` — `esp4`, `esp6` 모듈 |
| 발견자 | Hyunwoo Kim (@v4bel) |
| 공개일 | 2026-05-07 (엠바고 파기로 조기 공개) |
| 발표일 | 2026-05-08 |
| 도입 커밋 | `cac2661c53f3` (2017년 1월) |
| 패치 커밋 | `f4c50a4034e6` (2026-05-07) |
| CISA KEV | ❌ |
| PoC | 공개됨 |
| 영향 | 비권한 로컬 사용자 → root 권한 상승 |

⚠️ **공개된 Dirty Frag PoC는 CVE-2026-43284 (xfrm/ESP) + CVE-2026-43500 (rxrpc) 두 경로를 체인으로 사용합니다.**

- CVE-2026-43284 단독: Ubuntu AppArmor가 XFRM 소켓을 제한할 수 있어 불안정
- CVE-2026-43500 단독: `rxrpc` 모듈이 기본 미로드인 배포판에서 동작 안 함
- **두 CVE 체인**: 서로의 제약을 보완 → 대부분 배포판에서 안정적 root 획득

따라서 임시 완화 시 **`esp4`, `esp6`, `rxrpc` 세 모듈을 모두 차단**해야 합니다. 하나만 차단하면 나머지 경로로 우회 가능합니다.

CVE-2026-31431 (`algif_aead`)은 동일한 skb shared frag in-place 복호화 버그 클래스이지만 **독립적인 별개 경로**이며 별도 완화가 필요합니다. → [cve_2026_31431.md](./cve_2026_31431_copy_fail.md)

> 동일 계열 취약점: [CVE-2026-31431](./cve_2026_31431_copy_fail.md) (CISA KEV) / [CVE-2026-43500](./cve_2026_43500_dirty_frag.md) (rxrpc)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 취약점 상세

`MSG_SPLICE_PAGES`로 pipe 페이지를 UDP skb에 붙일 때 IPv4/IPv6 datagram append 경로가 `SKBFL_SHARED_FRAG` 플래그를 설정하지 않습니다. ESP input이 uncloned skb로 판단하여 **외부 소유 메모리에 in-place 복호화**를 수행합니다.

```
MSG_SPLICE_PAGES → UDP skb (SKBFL_SHARED_FRAG 미설정)
                        ↓
              ESP input (no-COW fast path)
                        ↓
              외부 소유 frag 페이지 in-place 복호화
              → page cache 임의 쓰기 → 권한 상승
```

**패치 내용:** IPv4/IPv6 datagram splice 시 `SKBFL_SHARED_FRAG` 설정 + ESP input에서 해당 플래그 존재 시 `skb_cow_data()` 호출로 fallback.

**취약 버전:**

| 브랜치 | 취약 범위       | 패치 버전      | RHEL/CentOS          | Ubuntu              | Amazon Linux      |
|--------|-----------------|----------------|----------------------|---------------------|-------------------|
| 5.10.x | 4.11 ~ 5.10.254 | **5.10.255+**  | RHEL 8 (백포트 확인) | 20.04 LTS (HWE)     | AL2 (5.10 kernel) |
| 5.15.x | 5.12 ~ 5.15.204 | **5.15.205+**  | RHEL 9.0~9.2         | 22.04 LTS           | AL2023            |
| 6.1.x  | 5.16 ~ 6.1.170  | **6.1.171+**   | RHEL 9.3~9.4         | 22.04 LTS (HWE)     | AL2023 (6.1)      |
| 6.6.x  | 6.2 ~ 6.6.137   | **6.6.138+**   | RHEL 9.5+            | 24.04 LTS           | AL2023 (6.6)      |
| 6.12.x | 6.7 ~ 6.12.86   | **6.12.87+**   | RHEL 10              | **24.04 LTS** ⚠️    | —                 |
| 6.18.x | 6.13 ~ 6.18.27  | **6.18.28+**   | —                    | 25.04               | —                 |
| 7.0.x  | 7.0 ~ 7.0.4     | **7.0.5+**     | —                    | 25.10 (예정)        | —                 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영향 범위 확인

### Ubuntu 24.04 실제 테스트 결과 (2026-05-14)

테스트 환경: Ubuntu 24.04.4 LTS / kernel `6.8.0-101-generic`

**PoC 빌드 테스트:**

```bash
git clone https://github.com/V4bel/dirtyfrag.git
gcc -O0 -Wall -o exp exp.c -lutil
```

| 항목 | 결과 | 비고 |
|------|------|------|
| PoC 빌드 | ✅ 성공 | `exp` 바이너리 생성 (62,320 bytes) |
| 커널 버전 | ❌ 취약 | 6.8.0-101 — 6.12.x 브랜치 취약 범위 |
| CVE-2026-43284 패치 | ❌ 미적용 | Ubuntu 백포트 미배포 (2026-05-14 기준) |
| `esp4` 모듈 | ⚠️ 미로드 | 모듈 파일 존재, auto-load 가능, blacklist 없음 |
| `esp6` 모듈 | ⚠️ 미로드 | 모듈 파일 존재, auto-load 가능, blacklist 없음 |
| XFRM netlink 소켓 | ❌ **OPEN** | 비권한 접근 성공 — ESP 익스플로잇 경로 활성 |
| 비권한 user namespace | ❌ 활성 | `kernel.unprivileged_userns_clone=1` |
| blacklist | ❌ 없음 | `/etc/modprobe.d/` dirtyfrag 설정 없음 |
| AppArmor | ✅ 활성 | XFRM 소켓 차단 안 됨 |

**결론: PoC 빌드 성공, XFRM 소켓 비권한 접근 가능 — CVE-2026-43284 익스플로잇 조건 충족**

> PoC 실행은 수행하지 않았습니다. 실행 시 `/usr/bin/su` page cache를 덮어씁니다. 실행 후 반드시 `echo 3 > /proc/sys/vm/drop_caches` 또는 재부팅이 필요합니다.

**원문 테스트 완료 배포판 (github.com/V4bel/dirtyfrag):**

| 배포판 | 커널 버전 |
|--------|---------|
| Ubuntu 24.04.4 | 6.17.0-23-generic |
| RHEL 10.1 | 6.12.0-124.49.1.el10_1.x86_64 |
| CentOS Stream 10 | 6.12.0-224.el10.x86_64 |
| AlmaLinux 10 | 6.12.0-124.52.3.el10_1.x86_64 |
| openSUSE Tumbleweed | 7.0.2-1-default |
| Fedora 44 | 6.19.14-300.fc44.x86_64 |

⚠️ **Copy Fail 완화(`algif_aead` blacklist)를 적용해도 Dirty Frag는 여전히 취약합니다.** xfrm-ESP 경로는 `algif_aead` 모듈과 무관하게 동작합니다.

### 탐지 명령어

```bash
uname -r
lsmod | grep -E "^esp4|^esp6"
grep -r "esp4\|esp6" /etc/modprobe.d/ 2>/dev/null

# XFRM netlink 소켓 비권한 접근 여부
python3 -c "
import socket
s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,15)
print('XFRM: OPEN (취약)')
s.close()
" 2>/dev/null || echo "XFRM: BLOCKED"

# DirtyFrag-Detector 실행
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
ip xfrm state list
ip xfrm policy list
lsmod | grep -E "^esp4|^esp6"
```

| 모듈 | 사용 중인 경우 | 언로드 시 영향 |
|------|--------------|----------------|
| `esp4` / `esp6` | IPsec VPN 터널 활성 | 기존 VPN 세션 즉시 끊김, 패킷 드롭 |
| `esp4` / `esp6` | strongSwan / Libreswan 실행 중 | 데몬이 모듈 재로드 시도 — blacklist 있으면 실패 |

**Step 2. modprobe.d 백업 확인**

```bash
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null || echo "파일 없음"
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

> 원문이 `esp4`, `esp6`, `rxrpc` 세 모듈을 모두 차단합니다. CVE-2026-43284 단독 차단 시 CVE-2026-43500 (rxrpc) 경로로 우회 가능하므로 반드시 세 모듈을 함께 차단해야 합니다.

모듈이 사용 중이면 `rmmod` 가 `Module is in use` 오류로 실패합니다:

```bash
sudo systemctl stop strongswan-starter 2>/dev/null || sudo systemctl stop ipsec 2>/dev/null
sudo modprobe -r esp4 esp6

# 그래도 실패 시 — 의존 모듈 확인 후 재부팅
for mod in esp4 esp6; do
    if lsmod | grep -q "^${mod} "; then
        echo "[WARN] ${mod} 언로드 실패:"
        cat /proc/modules | grep "^${mod} " | awk '{print "  used by:", $4}'
    fi
done
```

**Step 4. 언로드 결과 확인**

```bash
lsmod | grep -E "^esp4|^esp6"
# 출력 없으면 정상
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사후 검증

```bash
uname -r
lsmod | grep -E "^esp4|^esp6"

curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
rm -f dirty_frag_detect.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- NVD CVE-2026-43284: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43284) — ★★★☆☆
- Dirty Frag PoC: [github.com/0xBlackash/CVE-2026-43284](https://github.com/0xBlackash/CVE-2026-43284) — ★★☆☆☆
- Dirty Frag 원본 (V4bel): [github.com/V4bel/dirtyfrag](https://github.com/V4bel/dirtyfrag) — ★★★☆☆
- DirtyFrag-Detector: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — ★★☆☆☆
- Linux Kernel Patch: [git.kernel.org](https://git.kernel.org/stable/c/f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4) — ★★★★☆
- [cve_2026_31431.md](./cve_2026_31431_copy_fail.md) — CVE-2026-31431 (CISA KEV)
- [cve_2026_43500.md](./cve_2026_43500_dirty_frag.md) — CVE-2026-43500 (rxrpc)

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
