# Seccomp / Capabilities — 컨테이너 보안

Linux Capabilities와 Seccomp을 이용한 권한 최소화 및 시스템 콜 제한을 정리합니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. Capabilities](#1-capabilities) / [2. Seccomp](#2-seccomp) / [3. Docker 적용](#3-docker-적용) |
| [4. 확인 및 디버깅](#4-확인-및-디버깅) / [5. 실무 TIP](#5-실무-tip)                              |

---

## 1. Capabilities

root 권한을 세분화한 단위입니다. 프로세스에 필요한 권한만 부여합니다.

### 주요 Capability

| Capability             | 의미                             |
|------------------------|----------------------------------|
| `CAP_NET_BIND_SERVICE` | 1024 이하 포트 바인딩            |
| `CAP_NET_ADMIN`        | 네트워크 설정 변경               |
| `CAP_SYS_ADMIN`        | 마운트, namespace 등 시스템 관리 |
| `CAP_SYS_PTRACE`       | 다른 프로세스 추적 (strace 등)   |
| `CAP_CHOWN`            | 파일 소유자 변경                 |
| `CAP_KILL`             | 다른 프로세스에 시그널 전송      |
| `CAP_DAC_OVERRIDE`     | 파일 권한 무시                   |
| `CAP_SYS_TIME`         | 시스템 시간 변경                 |

```bash
# 현재 프로세스 capability 확인
cat /proc/$$/status | grep Cap
# CapInh: 0000000000000000  <- 상속 가능
# CapPrm: 0000000000000000  <- 허용됨
# CapEff: 0000000000000000  <- 현재 유효
# CapBnd: 000001ffffffffff  <- 바운딩 셋

# 16진수 → 이름 변환
capsh --decode=000001ffffffffff

# 파일에 부여된 capability
getcap /usr/bin/ping
# /usr/bin/ping cap_net_raw=ep

# 파일 capability 설정
setcap cap_net_bind_service=ep /usr/bin/myapp

# 제거
setcap -r /usr/bin/myapp
```

### Capability 셋 종류

| 셋          | 설명                                            |
|-------------|-------------------------------------------------|
| Effective   | 현재 실제로 사용 중인 capability                |
| Permitted   | 가질 수 있는 최대 capability                    |
| Inheritable | exec() 후 자식에게 상속 가능한 capability       |
| Bounding    | 절대 초과할 수 없는 상한선                      |
| Ambient     | 비특권 프로세스가 exec() 후 유지하는 capability |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Seccomp

프로세스가 사용할 수 있는 시스템 콜을 화이트리스트/블랙리스트로 제한합니다.

### 동작 방식

```
process -> syscall
                │
                v
         seccomp filter check
                │
        ┌───────┴───────┐
     allow             deny
        │               │
        v               v
   kernel exec      SIGKILL / SIGSYS / errno
```

### 모드

| 모드                  | 설명                              |
|-----------------------|-----------------------------------|
| `SECCOMP_MODE_STRICT` | read/write/exit/sigreturn 만 허용 |
| `SECCOMP_MODE_FILTER` | BPF 필터로 세밀하게 제어          |

```bash
# 프로세스 seccomp 상태 확인
cat /proc/<pid>/status | grep Seccomp
# Seccomp: 2
# 0=비활성, 1=strict, 2=filter

# 시스템 콜 번호 확인
ausyscall --dump | grep openat
```

### Docker 기본 seccomp 프로파일

Docker는 기본적으로 300여 개 시스템 콜 중 위험한 약 44개를 차단합니다.

```bash
# 기본 프로파일 위치
cat /etc/docker/seccomp.json 2>/dev/null || \
  curl -s https://raw.githubusercontent.com/moby/moby/master/profiles/seccomp/default.json | head -30

# seccomp 비활성화 (테스트용, 운영 금지)
docker run --security-opt seccomp=unconfined ubuntu
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Docker 적용

### Capability 제어

```bash
# 모든 capability 제거 후 필요한 것만 추가
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx

# 특정 capability 추가
docker run --cap-add=SYS_PTRACE ubuntu strace ls

# docker-compose.yml
# services:
#   app:
#     cap_drop:
#       - ALL
#     cap_add:
#       - NET_BIND_SERVICE
#       - CHOWN
```

### 커스텀 Seccomp 프로파일

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", "stat", "exit_group"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

```bash
docker run --security-opt seccomp=/path/to/profile.json ubuntu
```

### Kubernetes 적용

```yaml
# Pod securityContext
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault   # 기본 seccomp 프로파일
  containers:
  - name: app
    securityContext:
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 확인 및 디버깅

```bash
# seccomp으로 차단된 시스템 콜 확인
dmesg | grep "audit.*SECCOMP"
# audit: type=1326 ... syscall=xxx

# strace로 어떤 시스템 콜 사용하는지 확인
strace -c ./myapp 2>&1 | sort -k4 -rn | head -20

# 필요한 시스템 콜 목록 추출 (프로파일 생성용)
strace -f ./myapp 2>&1 | grep -oP "(?<=^)[a-z_]+" | sort -u

# capability 부족으로 실패하는 경우
strace ./myapp 2>&1 | grep "EPERM\|EACCES"
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실무 TIP

| 상황              | 권장 설정                                                      |
|-------------------|----------------------------------------------------------------|
| 웹 서버 (nginx)   | `cap_drop=ALL`, `cap_add=NET_BIND_SERVICE,CHOWN,SETUID,SETGID` |
| 모니터링 에이전트 | `cap_add=SYS_PTRACE,DAC_READ_SEARCH`                           |
| 네트워크 도구     | `cap_add=NET_ADMIN,NET_RAW`                                    |
| 일반 앱           | `cap_drop=ALL`, seccomp=RuntimeDefault                         |

⚠️ `CAP_SYS_ADMIN`은 거의 모든 권한을 포함합니다. 꼭 필요한 경우가 아니면 부여하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux man pages — capabilities: [man7.org/linux/man-pages/man7/capabilities.7.html](https://man7.org/linux/man-pages/man7/capabilities.7.html) — ★★★☆☆
- Docker seccomp: [docs.docker.com/engine/security/seccomp](https://docs.docker.com/engine/security/seccomp/) — ★★★☆☆
- [namespace.md](namespace.md)

---

**작성일** : 2026-05-21

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
