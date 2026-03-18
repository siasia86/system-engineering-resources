# Root Password Recovery Guide

각 OS별 root 패스워드 분실 시 복구 절차.
모든 작업은 물리 콘솔 또는 IPMI/iLO/iDRAC 등 원격 콘솔 접근이 필요하다.

---

## 사전 확인: SELinux 상태

RHEL 계열(CentOS, Rocky)은 복구 전 SELinux 상태를 알아두면 좋다.
정상 부팅이 가능한 상태라면 아래 명령으로 확인:

```bash
getenforce          # Enforcing / Permissive / Disabled
sestatus            # 상세 정보
cat /etc/selinux/config  # 설정 파일 직접 확인
```

- `Enforcing` → 복구 후 `touch /.autorelabel` 필수
- `Permissive` / `Disabled` → `touch /.autorelabel` 생략 가능

---

## CentOS 5 (EOL: 2017-03)

GRUB Legacy 사용. EOL이므로 레거시 환경 유지보수 목적으로만 참고.

1. 부팅 시 GRUB 메뉴에서 커널 라인 선택 → `e` 키
2. `kernel` 줄 선택 → `e` 키로 편집
3. 줄 끝에 ` single` 추가 → Enter
4. `b` 키로 부팅
5. single user mode 진입 후:

```bash
passwd root
reboot
```

> **참고:** GRUB 자체에 패스워드가 걸려있으면 rescue CD로 부팅 필요.

---

## CentOS 7 (EOL: 2024-06)

GRUB2 + systemd 사용. single mode에서도 root 패스워드를 물어볼 수 있어 `rd.break` 방식 사용.

1. 부팅 시 GRUB 메뉴에서 커널 선택 → `e` 키
2. `linux16` (UEFI 환경이면 `linuxefi`) 줄 끝에서 `rhgb quiet` 삭제
3. 같은 줄 끝에 `rd.break` 추가
4. `Ctrl + x` 로 부팅
5. initramfs emergency shell 진입 후:

```bash
mount -o remount,rw /sysroot
chroot /sysroot
passwd root
touch /.autorelabel    # SELinux enforcing일 때만 필요
exit
exit
```

> **중요:** SELinux enforcing 환경이면 `touch /.autorelabel` 필수. 빠뜨리면 로그인 불가.
> SELinux가 disabled 또는 permissive면 `touch /.autorelabel` 생략 가능.

---

## Rocky Linux 9 / Rocky Linux 10

GRUB2 + systemd. CentOS 7과 동일한 `rd.break` 방식.

> Rocky 10은 기본 SELinux enforcing.

1. 부팅 시 GRUB 메뉴에서 커널 선택 → `e` 키
2. `linux` (UEFI 환경이면 `linuxefi`) 줄 끝에서 `rhgb quiet` 삭제
3. 같은 줄 끝에 `rd.break` 추가
4. `Ctrl + x` 로 부팅
5. initramfs emergency shell 진입 후:

```bash
mount -o remount,rw /sysroot
chroot /sysroot
passwd root
touch /.autorelabel    # SELinux enforcing일 때만 필요
exit
exit
```

> **중요:** SELinux enforcing 환경이면 `touch /.autorelabel` 필수. 빠뜨리면 로그인 불가.
> SELinux가 disabled 또는 permissive면 `touch /.autorelabel` 생략 가능.

---

## Ubuntu 14.04 / 16.04 / 18.04 / 20.04 / 22.04 / 24.04

모든 버전 동일한 절차. GRUB2 사용.

| 버전 | Init System | 비고 |
|---|---|---|
| 14.04 | Upstart | EOL (2019-04) |
| 16.04 | systemd | EOL (2021-04, ESM 2026-04) |
| 18.04 | systemd | EOL (2023-05, ESM 2028-04) |
| 20.04 | systemd | LTS (2025-04까지, ESM 2030-04) |
| 22.04 | systemd | LTS (2027-04까지) |
| 24.04 | systemd | LTS (2029-04까지) |

1. 부팅 시 GRUB 메뉴에서 커널 선택 → `e` 키
2. `linux` 줄에서 `ro quiet splash` 를 `rw init=/bin/bash` 로 변경
3. `Ctrl + x` 로 부팅
4. root shell 진입 후:

```bash
passwd root
sync
reboot -f
```

> Ubuntu는 SELinux를 사용하지 않으므로 relabel 불필요.

---

## 요약 비교

| OS | Bootloader | 핵심 파라미터 | SELinux relabel |
|---|---|---|---|
| CentOS 5 | GRUB Legacy | `single` | 불필요 |
| CentOS 7 | GRUB2 | `rd.break` | enforcing일 때만 `touch /.autorelabel` |
| Rocky 9 | GRUB2 | `rd.break` | enforcing일 때만 `touch /.autorelabel` |
| Rocky 10 | GRUB2 | `rd.break` | enforcing일 때만 `touch /.autorelabel` |
| Ubuntu 전 버전 | GRUB2 | `rw init=/bin/bash` | 불필요 |

---

## 주의사항

- GRUB에 패스워드가 설정된 경우 → rescue/live CD 부팅 후 chroot로 복구
- 디스크 암호화(LUKS) 환경 → 암호화 패스프레이즈 없으면 복구 불가
- 클라우드 VM(AWS, GCP 등) → 콘솔 접근 불가하므로 rescue mode 또는 디스크 분리 후 다른 VM에 마운트하여 복구
