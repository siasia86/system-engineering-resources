# SELinux 거부 분석과 정책 조정 가이드

SELinux(Security-Enhanced Linux)는 프로세스와 파일에 붙은 보안 문맥(label)을 비교해 접근을 허용하거나 거부하는 강제 접근 제어(MAC, Mandatory Access Control) 기능입니다. 이 문서는 [Linux 서버 보안 강화](./linux_hardening.md)의 SELinux 절을 이어서, 서비스가 SELinux 때문에 실패할 때 끄지 않고 원인을 찾아 고치는 순서를 다룹니다.

## 목차

| 섹션                                                                                                  |
|-------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 보안 문맥 읽기](#2-보안-문맥-읽기)                                           |
| [3. 거부 기록 찾기](#3-거부-기록-찾기) / [4. 원인 분류와 해결 순서](#4-원인-분류와-해결-순서)         |
| [5. 파일 문맥 고치기](#5-파일-문맥-고치기) / [6. 불리언과 포트](#6-불리언과-포트)                     |
| [7. 숨은 거부와 도메인 단위 permissive](#7-숨은-거부와-도메인-단위-permissive)                        |
| [8. 로컬 정책 모듈은 마지막 수단](#8-로컬-정책-모듈은-마지막-수단) / [9. 운영 점검표](#9-운영-점검표) |

---

## 1. 개요

### 왜 끄지 않는가

웹 서버가 뚫려도 SELinux가 강제(enforcing) 상태면, 공격자는 웹 서버 도메인(`httpd_t`)이 허용받은 범위 밖으로 나가기 어렵습니다. `setenforce 0`이나 비활성화는 문제를 숨길 뿐 원인을 고치지 않고, 이 보호를 서버 전체에서 없앱니다.

| 모드       | 동작                      | 쓰는 때                           |
|------------|---------------------------|-----------------------------------|
| Enforcing  | 정책 위반을 거부하고 기록 | 운영 기본                         |
| Permissive | 거부하지 않고 기록만      | 짧은 진단, 가능하면 도메인 단위로 |
| Disabled   | SELinux 미적재            | 권장하지 않음                     |

🟡 RHEL 9에서는 `/etc/selinux/config`에 `SELINUX=disabled`만 적으면 SELinux가 켜진 채 정책 없이 부팅됩니다. 완전히 끄려면 커널 인수 `selinux=0`이 필요하고, 다시 켤 때는 전체 파일 재라벨이 필요합니다. 끄기 전에 이 문서의 절차로 원인을 먼저 찾습니다.

### 대상 환경

RHEL·Rocky·Alma·Fedora처럼 SELinux targeted 정책이 기본인 배포판을 기준으로 합니다. 분석 도구는 다음 패키지에 있습니다.

```bash
sudo dnf install policycoreutils-python-utils setroubleshoot-server setools-console
# semanage, audit2allow, audit2why : policycoreutils-python-utils
# sealert                          : setroubleshoot-server
# sesearch                         : setools-console
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 보안 문맥 읽기

보안 문맥은 `사용자:역할:타입:수준` 네 부분입니다. targeted 정책에서 접근 판단에 주로 쓰이는 것은 세 번째 타입(type)입니다. 프로세스의 타입을 도메인(domain)이라고도 부릅니다.

```bash
ls -Z /var/www/html/index.html
# unconfined_u:object_r:httpd_sys_content_t:s0 /var/www/html/index.html

ps -eZ | grep httpd
# system_u:system_r:httpd_t:s0   1234 ?  00:00:00 httpd

id -Z                    # 현재 셸의 문맥
ss -ltnpZ | grep :80     # 소켓을 연 프로세스 문맥 (iproute2 지원 판)
```

### 자주 보는 타입

| 타입                     | 의미                                     |
|--------------------------|------------------------------------------|
| `httpd_t`                | 웹 서버 프로세스 도메인                  |
| `httpd_sys_content_t`    | 웹 서버가 읽을 수 있는 정적 콘텐츠       |
| `httpd_sys_rw_content_t` | 웹 서버가 쓸 수 있는 콘텐츠(업로드 경로) |
| `httpd_log_t`            | 웹 서버 로그                             |
| `user_home_t`            | 사용자 홈 아래 파일                      |
| `tmp_t`                  | `/tmp` 아래 일반 파일                    |
| `http_port_t`            | 웹 서버가 열 수 있는 포트 타입           |

정책은 "어느 도메인이 어느 타입에 어떤 권한을 갖는가"를 규칙으로 정의합니다. 대부분의 거부는 파일이 기대와 다른 타입을 갖고 있어서 생깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 거부 기록 찾기

### 기록 위치

auditd가 동작하면 거부 기록(AVC, Access Vector Cache 메시지)은 `/var/log/audit/audit.log`에 남습니다. auditd가 없으면 커널 로그(journal)로 갑니다.

```bash
# 최근 10분 거부 기록
sudo ausearch -m AVC,USER_AVC,SELINUX_ERR -ts recent -i

# 오늘 거부 기록 중 httpd 관련
sudo ausearch -m AVC -ts today -c httpd -i

# auditd가 없을 때
sudo journalctl -k | grep -i 'avc:  denied'
```

auditd 조회 옵션은 [auditd 감사 규칙과 로그 조회 가이드](./auditd_rules_and_search_guide.md)에서 다룹니다.

### AVC 메시지 읽기

```text
type=AVC msg=audit(1763270000.123:456): avc:  denied  { read } for  pid=1234
  comm="httpd" name="index.html" dev="dm-0" ino=12345
  scontext=system_u:system_r:httpd_t:s0
  tcontext=unconfined_u:object_r:user_home_t:s0 tclass=file permissive=0
```

| 필드          | 의미                                            |
|---------------|-------------------------------------------------|
| `denied { }`  | 거부된 권한                                     |
| `comm`, `pid` | 요청한 프로세스                                 |
| `name`        | 대상 이름 (경로 전체는 같은 이벤트의 `PATH` 줄) |
| `scontext`    | 요청한 쪽(source) 문맥                          |
| `tcontext`    | 대상(target) 문맥                               |
| `tclass`      | 대상 종류 (`file`, `dir`, `tcp_socket` 등)      |
| `permissive`  | 1이면 기록만 되고 실제로는 허용됨               |

위 예는 웹 서버(`httpd_t`)가 사용자 홈 타입(`user_home_t`) 파일을 읽으려다 거부된 경우입니다. 홈에서 `mv`로 옮긴 파일이 원래 타입을 그대로 가져온 전형적인 상황입니다.

### 사람이 읽기 쉬운 설명 얻기

```bash
# 거부 이유 설명
sudo ausearch -m AVC -ts recent | audit2why

# setroubleshoot 분석 (해결 제안 포함)
sudo sealert -a /var/log/audit/audit.log
```

`audit2why`는 원인을 "파일 문맥 불일치", "불리언으로 허용 가능", "정책에 허용 규칙 없음" 등으로 알려 줍니다. `sealert` 제안 중 `audit2allow`로 모듈을 만들라는 항목은 8절 기준을 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 원인 분류와 해결 순서

거부를 만나면 아래 순서로 확인합니다. 위쪽일수록 변경 범위가 좁고 안전합니다.

```text
 AVC denied
     |
     v
 [1] file label wrong? -------- yes --> restorecon / semanage fcontext
     | no
     v
 [2] boolean exists? ---------- yes --> setsebool -P
     | no
     v
 [3] non-default port? -------- yes --> semanage port -a
     | no
     v
 [4] hidden denials? ---------- check with semodule -DB
     | no
     v
 [5] local policy module (review audit2allow output)
```

| 단계 | 원인                         | 해결                               | 영향 범위             |
|------|------------------------------|------------------------------------|-----------------------|
| 1    | 파일 타입이 기본 규칙과 다름 | `restorecon`                       | 해당 파일             |
| 1    | 비표준 경로라 기본 규칙 없음 | `semanage fcontext` + `restorecon` | 지정한 경로           |
| 2    | 정책이 선택 기능으로 막아 둠 | `setsebool -P`                     | 그 도메인의 해당 기능 |
| 3    | 비표준 포트 사용             | `semanage port -a`                 | 해당 포트             |
| 5    | 정책에 규칙 자체가 없음      | 로컬 모듈                          | 작성한 규칙 범위      |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 파일 문맥 고치기

### 기본 규칙대로 되돌리기

```bash
# 이 경로의 기본 문맥 확인
matchpathcon /var/www/html/index.html

# 기본 규칙대로 되돌림 (-v 변경 내용 출력, -n 실제 변경 없이 확인)
sudo restorecon -Rvn /var/www/html
sudo restorecon -Rv /var/www/html
```

`mv`는 원래 문맥을 유지하고, `cp`는 대상 디렉터리 기본 문맥을 따릅니다. 배포 스크립트가 `mv`를 쓰면 배포 뒤 `restorecon`을 붙입니다.

### 비표준 경로에 규칙 추가

웹 루트를 `/srv/www`처럼 바꾸면 기본 규칙이 없어 `var_t` 등 다른 타입이 붙습니다. `chcon`은 임시 변경이라 재라벨 때 사라지므로, `semanage fcontext`로 규칙을 등록하고 `restorecon`으로 적용합니다.

```bash
# 읽기 전용 콘텐츠
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www(/.*)?"
# 웹 서버가 써야 하는 업로드 경로만 쓰기 타입
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/srv/www/uploads(/.*)?"
sudo restorecon -Rv /srv/www

# 기존 경로와 같은 규칙을 그대로 적용 (동등 경로)
sudo semanage fcontext -a -e /var/www /srv/www

# 직접 추가한 규칙만 보기
sudo semanage fcontext -l -C
```

쓰기 타입(`httpd_sys_rw_content_t`)은 업로드처럼 꼭 필요한 하위 경로에만 줍니다. 웹 루트 전체에 주면 웹 서버 침해 시 코드 파일도 바뀔 수 있습니다.

### 전체 재라벨

```bash
# 다음 부팅 때 전체 파일 시스템 재라벨
sudo fixfiles -F onboot
# 또는
sudo touch /.autorelabel
```

🟡 전체 재라벨은 파일 수에 비례해 부팅 시간이 길어집니다. SELinux를 껐다가 다시 켰을 때처럼 대량 불일치가 예상될 때만 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 불리언과 포트

### 불리언

불리언(boolean)은 정책 작성자가 미리 만들어 둔 선택 기능 스위치입니다. 예를 들어 웹 서버의 외부 네트워크 연결은 기본으로 막혀 있고 불리언으로 켭니다.

```bash
# httpd 관련 불리언과 현재 값
getsebool -a | grep httpd
sudo semanage boolean -l | grep httpd_can_network

# 켜기 (-P 없으면 재부팅 때 원래 값으로 돌아감)
sudo setsebool -P httpd_can_network_connect on

# 기본값과 다르게 바꾼 불리언만 보기
sudo semanage boolean -l -C
```

| 불리언 예                      | 허용하는 것                  |
|--------------------------------|------------------------------|
| `httpd_can_network_connect`    | 웹 서버의 임의 TCP 외부 연결 |
| `httpd_can_network_connect_db` | 웹 서버의 DB 포트 연결       |
| `httpd_enable_homedirs`        | 사용자 홈 디렉터리 제공      |
| `httpd_use_nfs`                | NFS 위 콘텐츠 사용           |

더 좁은 불리언이 있으면 그것을 고릅니다. 예를 들어 웹 서버가 DB에만 붙으면 `httpd_can_network_connect`보다 `httpd_can_network_connect_db`가 범위가 좁습니다. 불리언 목록은 정책 판에 따라 다르므로 `semanage boolean -l`로 실제 존재를 확인합니다.

### 포트

서비스를 기본이 아닌 포트에 띄우면 포트 타입이 맞지 않아 bind가 거부됩니다.

```bash
# 이미 정의된 포트 타입
sudo semanage port -l | grep -w http_port_t

# 웹 서버가 TCP 8081을 열 수 있게 추가
sudo semanage port -a -t http_port_t -p tcp 8081

# SSH를 2222로 옮길 때
sudo semanage port -a -t ssh_port_t -p tcp 2222

# 직접 추가한 포트만 보기
sudo semanage port -l -C
```

이미 다른 타입에 정의된 포트는 `-a` 대신 `-m`(수정)을 써야 합니다. 이때 그 포트를 쓰던 다른 서비스에 영향이 없는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 숨은 거부와 도메인 단위 permissive

### dontaudit 규칙 잠시 끄기

정책에는 흔하고 무해한 거부를 기록하지 않게 하는 `dontaudit` 규칙이 있습니다. 서비스가 실패하는데 AVC가 보이지 않으면 이 규칙에 가려졌을 수 있습니다.

```bash
sudo semodule -DB     # dontaudit 규칙을 빼고 정책 다시 빌드
# 문제 재현 후 ausearch로 거부 확인
sudo semodule -B      # dontaudit 규칙 복구
```

🟡 `-DB` 상태에서는 거부 기록이 크게 늘어 로그 디스크를 빠르게 씁니다. 재현이 끝나면 바로 `-B`로 되돌립니다.

### 도메인 하나만 permissive

`setenforce 0`은 서버 전체를 permissive로 바꿉니다. 진단이 필요하면 문제 도메인 하나만 permissive로 두고, 나머지는 강제 상태를 유지합니다.

```bash
sudo semanage permissive -a httpd_t   # httpd_t만 기록 모드
# 재현 후 ausearch로 필요한 접근 전체 수집
sudo semanage permissive -l           # permissive 도메인 목록
sudo semanage permissive -d httpd_t   # 원복
```

permissive 상태에서 생긴 AVC는 `permissive=1`로 표시됩니다. 원복을 잊지 않도록 변경 기록에 남기고, 점검표에서 `semanage permissive -l` 결과가 비어 있는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 로컬 정책 모듈은 마지막 수단

`audit2allow`는 거부 기록을 그대로 허용 규칙으로 바꿉니다. 원인이 파일 문맥 오류인데 모듈을 만들면, 잘못된 상태를 고치는 대신 웹 서버에 사용자 홈 읽기 같은 넓은 권한을 주게 됩니다.

### 쓰기 전 확인

| 확인 항목                                     | 아니면                   |
|-----------------------------------------------|--------------------------|
| 4절 1~4단계로 해결되지 않았는가               | 해당 단계로 돌아감       |
| 거부 대상이 정말 그 서비스가 써야 하는 것인가 | 애플리케이션 설정을 고침 |
| 침해 시도로 생긴 거부가 아닌가                | 침해 점검 절차로 넘김    |
| 생성된 규칙을 한 줄씩 이해했는가              | 모듈을 적재하지 않음     |

### 작성과 검토

```bash
# 해당 서비스 거부만 골라 규칙 초안 생성
sudo ausearch -m AVC -ts today -c myapp | audit2allow -M myapp_local
# 생성 파일: myapp_local.te (사람이 읽는 규칙), myapp_local.pp (적재용)
cat myapp_local.te
```

`.te` 파일을 열어 `allow` 줄마다 도메인·타입·권한이 의도와 맞는지 확인합니다. 특히 다음은 다시 검토합니다.

| 위험 신호                                             | 이유                                 |
|-------------------------------------------------------|--------------------------------------|
| 대상 타입이 `user_home_t`, `admin_home_t`, `shadow_t` | 민감 파일 접근 허용                  |
| `unconfined`가 들어간 타입                            | 제한 해제에 가까움                   |
| `execute`, `execute_no_trans` 권한                    | 다른 프로그램 실행 허용              |
| 거부되었으나 서비스 동작에 영향 없는 접근             | 허용 대신 `dontaudit`가 맞을 수 있음 |

검토가 끝난 모듈만 적재하고, `.te` 파일은 구성 관리 저장소에 보관합니다.

```bash
sudo semodule -i myapp_local.pp
sudo semodule -l | grep myapp_local
# 제거
sudo semodule -r myapp_local
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 점검표

| 항목                                 | 확인 방법                                 |
|--------------------------------------|-------------------------------------------|
| 모든 서버가 Enforcing                | `getenforce`                              |
| 커널 인수에 `selinux=0` 없음         | `cat /proc/cmdline`                       |
| permissive 도메인 없음(진단 중 제외) | `semanage permissive -l`                  |
| 로컬 변경 내역이 구성 관리에 기록됨  | `semanage export`, 저장소 대조            |
| 로컬 정책 모듈마다 `.te` 원본 보관   | `semodule -l`과 저장소 대조               |
| dontaudit 복구 상태                  | 진단 후 `semodule -B` 실행 기록           |
| 배포 후 파일 문맥 정상               | `restorecon -Rvn <경로>` 출력이 비어 있음 |
| 반복 AVC가 없는지 정기 확인          | `aureport -a --summary`                   |

`semanage export`는 직접 바꾼 fcontext·불리언·포트·permissive 설정을 한 번에 출력하므로, 서버 간 차이를 비교하거나 새 서버에 같은 설정을 넣을 때(`semanage import`) 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- semanage-fcontext(8): [manpages.debian.org](https://manpages.debian.org/bookworm/policycoreutils-python-utils/semanage-fcontext.8.en.html) (확인일 2026-11-16) — ★★★☆☆
- semanage-port(8): [manpages.debian.org](https://manpages.debian.org/bookworm/policycoreutils-python-utils/semanage-port.8.en.html) (확인일 2026-11-16) — ★★★☆☆
- semanage-permissive(8): [manpages.debian.org](https://manpages.debian.org/bookworm/policycoreutils-python-utils/semanage-permissive.8.en.html) (확인일 2026-11-16) — ★★★☆☆
- semodule(8)(`-DB`, `-B`): [manpages.debian.org](https://manpages.debian.org/bookworm/policycoreutils/semodule.8.en.html) (확인일 2026-11-16) — ★★★☆☆
- audit2allow(1)·audit2why: [manpages.debian.org](https://manpages.debian.org/bookworm/policycoreutils-python-utils/audit2allow.1.en.html) (확인일 2026-11-16) — ★★★☆☆
- SELinux Notebook, Auditing SELinux Events(AVC 형식): [github.com/SELinuxProject/selinux-notebook](https://github.com/SELinuxProject/selinux-notebook/blob/main/src/auditing.md) (확인일 2026-11-16) — ★★★☆☆
- Red Hat RHEL 9 Using SELinux, Changing SELinux states and modes(`selinux=0`): [docs.redhat.com](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/changing-selinux-states-and-modes_using-selinux) (확인일 2026-11-16) — ★★★☆☆
- Red Hat Bugzilla 1932222(RHEL 9 `SELINUX=disabled` 동작 변경): [bugzilla.redhat.com](https://bugzilla.redhat.com/show_bug.cgi?id=1932222) (확인일 2026-11-16) — ★★★☆☆

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
