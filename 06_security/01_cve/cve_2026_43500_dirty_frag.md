# CVE-2026-43500 — Linux Kernel rxrpc (Dirty Frag)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 취약점 상세](#2-취약점-상세) / [3. 영향 범위 확인](#3-영향-범위-확인) |
| [4. 대처 방안](#4-대처-방안) / [5. 사후 검증](#5-사후-검증) |

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| CVE | CVE-2026-43500 |
| 별칭 | Dirty Frag / Copy Fail 2 |
| CVSS | 7.8 (HIGH) |
| 공격 벡터 | LOCAL / LOW privilege / NO interaction |
| 컴포넌트 | `net/rxrpc` — `rxrpc` 모듈 |
| 발견자 | Hyunwoo Kim (@v4bel) |
| 공개일 | 2026-05-07 (엠바고 파기로 조기 공개) |
| 발표일 | 2026-05-11 |
| 도입 커밋 | `2dc334f1a63a` (2023년 6월) |
| 패치 커밋 | `aa54b1d27fe0` (2026-05-10) |
| CISA KEV | ❌ |
| PoC | 공개됨 |
| 영향 | 비권한 로컬 사용자 → root 권한 상승 |

⚠️ **공개된 Dirty Frag PoC는 CVE-2026-43284 (xfrm/ESP) + CVE-2026-43500 (rxrpc) 두 경로를 체인으로 사용합니다.**

- CVE-2026-43284 단독: Ubuntu AppArmor가 XFRM 소켓을 제한할 수 있어 불안정
- CVE-2026-43500 단독: `rxrpc` 모듈이 기본 미로드인 배포판에서 동작 안 함
- **두 CVE 체인**: 서로의 제약을 보완 → 대부분 배포판에서 안정적 root 획득

따라서 임시 완화 시 **`esp4`, `esp6`, `rxrpc` 세 모듈을 모두 차단**해야 합니다. 하나만 차단하면 나머지 경로로 우회 가능합니다.

CVE-2026-31431 (`algif_aead`)은 동일한 skb shared frag in-place 복호화 버그 클래스이지만 **독립적인 별개 경로**이며 별도 완화가 필요합니다. → [cve_2026_31431.md](./cve_2026_31431_copy_fail.md)

> 동일 계열 취약점: [CVE-2026-31431](./cve_2026_31431_copy_fail.md) (CISA KEV) / [CVE-2026-43284](./cve_2026_43284_dirty_frag.md) (xfrm/ESP)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 취약점 상세

`rxrpc` DATA/RESPONSE 패킷 처리 시 `skb_cloned()` 체크만 수행하고 `skb_has_frag_list()` / `skb_has_shared_frag()` 는 체크하지 않습니다. `splice()` 루프백 벡터 등으로 외부 소유 frag 페이지가 AEAD/skcipher SGL에 직접 바인딩되어 **in-place 복호화**가 수행됩니다.

```
splice() → rxrpc socket → shared frag pages
                               ↓
                  AEAD/skcipher SGL 직접 바인딩
                               ↓
                  in-place 복호화 → page cache 쓰기 → 권한 상승
```

**패치 내용:** `skb_has_frag_list()` 또는 `skb_has_shared_frag()` 가 true일 때도 unshare 처리하도록 gate 확장.

**취약 버전:**

| 브랜치 | 취약 범위      | 패치 버전      | RHEL/CentOS          | Ubuntu       | Amazon Linux |
|--------|---------------|----------------|----------------------|--------------|--------------|
| ~6.18  | ~ 6.18.28     | **6.18.29+**   | RHEL 8~10 (백포트 확인) | 20.04~25.04 | AL2, AL2023  |
| 6.19.x | 6.19 ~ 7.0.5  | **7.0.6+**     | —                    | 25.10 (예정) | —            |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영향 범위 확인

### Ubuntu 24.04 실제 테스트 결과 (2026-05-13)

테스트 환경: Ubuntu 24.04.4 LTS / kernel `6.8.0-101-generic`

| 항목 | 결과 | 비고 |
|------|------|------|
| 커널 버전 | ❌ 취약 | 6.8.0-101 — ~6.18 취약 범위 |
| CVE-2026-43500 패치 | ❌ 미적용 | upstream 패치 2026-05-10, 배포판 백포트 진행 중 |
| `rxrpc` 모듈 | ❌ **로드됨** | `lsmod` 확인: `rxrpc 438272 0` — used_by 없음 |
| AF_RXRPC 소켓 | ✅ BLOCKED | rxrpc 로드됐으나 소켓 접근 차단됨 |
| AFS 마운트 | ✅ 없음 | AFS 파일시스템 미사용 |
| blacklist | ❌ 없음 | `/etc/modprobe.d/` dirtyfrag 설정 없음 |

⚠️ `rxrpc` 모듈이 **이미 로드된 상태**입니다. `rmmod rxrpc` 실행 전 사용 여부를 반드시 확인합니다. 현재 `used_by: -` 이므로 언로드 가능합니다.

**결론: rxrpc 로드됨 — 즉시 blacklist 등록 및 언로드 필요**

### 탐지 명령어

```bash
uname -r
lsmod | grep "^rxrpc"
grep "rxrpc" /etc/modprobe.d/*.conf 2>/dev/null

# AF_RXRPC 소켓 접근 여부
python3 -c "
import socket
s=socket.socket(34,socket.SOCK_DGRAM,0)
print('AF_RXRPC: OPEN (취약)')
s.close()
" 2>/dev/null || echo "AF_RXRPC: BLOCKED"

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

> 출처: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — Recommended immediate actions 섹션

**Step 1. 모듈 사용 여부 사전 확인**

```bash
mount | grep afs
lsmod | grep "^rxrpc"
```

| 모듈 | 사용 중인 경우 | 언로드 시 영향 |
|------|--------------|----------------|
| `rxrpc` | AFS 마운트 포인트 사용 중 | AFS 파일시스템 접근 불가, I/O 에러 |

**Step 2. blacklist 등록 + 언로드**

> 출처: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — Recommended immediate actions 섹션

```bash
# ---- 원문 (DirtyFrag-Detector 권장) ---- #
sudo sh -c 'printf "install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n" \
  > /etc/modprobe.d/dirtyfrag.conf'

sudo rmmod esp4 esp6 rxrpc 2>/dev/null || true

echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
# ---- 원문 끝 ---- #
```

> 원문이 `esp4`, `esp6`, `rxrpc` 세 모듈을 모두 차단합니다. CVE-2026-43500 단독 차단 시 CVE-2026-43284 (xfrm/ESP) 경로로 우회 가능하므로 반드시 세 모듈을 함께 차단해야 합니다.

모듈이 사용 중이면 `rmmod` 가 실패합니다:

```bash
# 의존 모듈 확인 후 재부팅
cat /proc/modules | grep "^rxrpc " | awk '{print "used by:", $4}'
# → 재부팅 후 blacklist 적용 상태로 부팅
```

**Step 3. 결과 확인**

```bash
lsmod | grep "^rxrpc"
# 출력 없으면 정상
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사후 검증

```bash
uname -r
lsmod | grep "^rxrpc"

curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
rm -f dirty_frag_detect.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- NVD CVE-2026-43500: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-43500) — ★★★☆☆
- DirtyFrag-Detector: [github.com/liamromanis101/DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector) — ★★☆☆☆
- Linux Kernel Patch: [git.kernel.org](https://git.kernel.org/stable/c/aa54b1d27fe0) — ★★★★☆
- [cve_2026_31431.md](./cve_2026_31431_copy_fail.md) — CVE-2026-31431 (CISA KEV)
- [cve_2026_43284.md](./cve_2026_43284_dirty_frag.md) — CVE-2026-43284 (xfrm/ESP)

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
