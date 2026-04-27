# Linux 컨테이너 기술 스택 구조

> **내부 공유 자료**  
> 작성일: 2026-01-29  
> 버전: 1.0  
> 대상: 시스템 엔지니어, SRE

## 목차
- [전체 계층 구조](#전체-계층-구조)
- [상세 계층 설명](#상세-계층-설명)
- [기술별 관계도](#기술별-관계도)
- [Low-Level 직접 사용 사례](#low-level-직접-사용-사례)
- [실제 동작 예시](#실제-동작-예시)
- [트러블슈팅](#트러블슈팅)

## 전체 계층 구조

```
┌──────────────────────────────────────────────┐
│        사용자 / 애플리케이션                 │  ← 최상위
└──────────────────────────────────────────────┘
                     v
┌──────────────────────────────────────────────┐
│   High-Level Tools (사용자 친화적)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   LXD    │  │  Docker  │  │  Podman  │    │
│  │ (시스템) │  │  (앱)    │  │  (앱)    │    │
│  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────┘
                     v
┌──────────────────────────────────────────────┐
│   Mid-Level Libraries                        │
│  ┌──────────┐  ┌──────────────────────────┐  │
│  │   LXC    │  │   containerd/runc        │  │
│  │ (liblxc) │  │   (OCI runtime)          │  │
│  └──────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────┘
                     v
┌──────────────────────────────────────────────┐
│   Low-Level Kernel Features                  │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Namespaces  │  │     Cgroups          │  │
│  │   (격리)     │  │   (리소스 제한)      │  │
│  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Capabilities │  │     Seccomp          │  │
│  │   (권한)     │  │   (시스템콜)         │  │
│  └──────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────┘
                     v
┌──────────────────────────────────────────────┐
│        Linux Kernel                          │  ← 최하위
└──────────────────────────────────────────────┘
```

## 상세 계층 설명

### Layer 1: Linux Kernel (최하위)

**핵심 기능**
```
- 프로세스 관리
- 메모리 관리
- 파일시스템
- 네트워킹
- 하드웨어 드라이버
```

### Layer 2: Kernel Features (Low-Level)

#### Namespaces (격리)
```
PID Namespace:    프로세스 ID 격리
NET Namespace:    네트워크 스택 격리
MNT Namespace:    파일시스템 마운트 격리
UTS Namespace:    호스트명 격리
IPC Namespace:    프로세스 간 통신 격리
USER Namespace:   사용자/그룹 ID 격리
CGROUP Namespace: Cgroup 격리
```

#### Cgroups (리소스 제한)
```
cpu:     CPU 사용량 제한
memory:  메모리 사용량 제한
blkio:   디스크 I/O 제한
net:     네트워크 대역폭 제한
pids:    프로세스 수 제한
```

#### Capabilities (권한)
```
CAP_NET_ADMIN:    네트워크 관리
CAP_SYS_ADMIN:    시스템 관리
CAP_CHOWN:        파일 소유권 변경
등 40개 이상...
```

#### Seccomp (시스템 콜 필터링)
```
허용/차단할 시스템 콜 지정
보안 강화
```

### Layer 3: Mid-Level Libraries

#### LXC (Linux Containers)
```
역할:
- Kernel 기능을 라이브러리로 래핑
- liblxc 제공
- 컨테이너 생성/관리 API

명령어:
- lxc-create
- lxc-start
- lxc-attach
- lxc-stop

사용:
- 직접 사용 드묾
- LXD가 내부적으로 사용
```

#### containerd / runc (OCI Runtime)
```
역할:
- OCI(Open Container Initiative) 표준 구현
- 컨테이너 런타임

사용:
- Docker가 내부적으로 사용
- Kubernetes가 사용
```

### Layer 4: High-Level Tools (사용자 친화적)

#### LXD
```
역할:
- LXC 위에 구축
- 시스템 컨테이너 관리
- REST API 제공
- 이미지 관리

특징:
- 완전한 OS 실행
- VM처럼 사용
- systemd 지원

명령어:
- lxc launch
- lxc exec
- lxc stop
```

#### Docker
```
역할:
- containerd/runc 위에 구축
- 애플리케이션 컨테이너
- 이미지 빌드/배포

특징:
- 단일 프로세스
- 마이크로서비스
- 이미지 레이어

명령어:
- docker run
- docker build
- docker ps
```

#### Podman
```
역할:
- Docker 대체
- Daemonless
- rootless 지원

특징:
- Docker 호환
- 더 안전함
```

## 기술별 관계도

### LXD/LXC 스택

```
사용자
  v
lxc launch ubuntu:22.04 web  ← LXD (High-level)
  v
LXD Daemon (REST API)
  v
liblxc (라이브러리)           ← LXC (Mid-level)
  v
┌─────────────────────────┐
│ Namespaces + Cgroups    │  ← Kernel Features (Low-level)
└─────────────────────────┘
  v
Linux Kernel
```

### Docker 스택

```
사용자
  v
docker run nginx              ← Docker (High-level)
  v
Docker Daemon (dockerd)
  v
containerd                    ← Mid-level
  v
runc (OCI runtime)
  v
┌─────────────────────────┐
│ Namespaces + Cgroups    │  ← Kernel Features (Low-level)
└─────────────────────────┘
  v
Linux Kernel
```

## Low-Level 직접 사용 사례

### 언제 Low-Level을 직접 사용하나?

**1. 트러블슈팅**
- 컨테이너 문제 디버깅
- 네트워크 격리 문제
- 리소스 제한 확인

**2. 커스텀 컨테이너 런타임 개발**
- 특수 목적 컨테이너
- 보안 강화 컨테이너

**3. 성능 최적화**
- Cgroup 세밀 조정
- 네트워크 최적화

**4. 교육 및 학습**
- 컨테이너 내부 동작 이해

### 실전 예제 1: Namespace 직접 사용

#### 격리된 환경 만들기 (unshare)

```bash
# PID + NET + MNT namespace 격리
sudo unshare --pid --net --mount --fork /bin/bash

# 새로운 namespace 내부에서:
ps aux
# PID 1번만 보임 (격리됨)

ip addr
# lo만 보임 (네트워크 격리)

mount -t proc proc /proc
# 새로운 프로세스 트리
```

#### Docker 컨테이너의 Namespace 확인

```bash
# 컨테이너 실행
docker run -d --name test nginx

# 컨테이너 PID 확인
docker inspect test | grep Pid
# "Pid": 12345

# Namespace 확인
sudo ls -l /proc/12345/ns/
# lrwxrwxrwx 1 root root 0 Jan 29 08:00 net -> net:[4026532456]
# lrwxrwxrwx 1 root root 0 Jan 29 08:00 pid -> pid:[4026532457]
# lrwxrwxrwx 1 root root 0 Jan 29 08:00 mnt -> mnt:[4026532458]

# 컨테이너 네트워크 namespace 진입
sudo nsenter --target 12345 --net ip addr
# 컨테이너 내부 네트워크 인터페이스 확인
```

#### 네트워크 Namespace 수동 생성

```bash
# 네트워크 namespace 생성
sudo ip netns add container1

# namespace 목록
ip netns list

# namespace 내부에서 명령 실행
sudo ip netns exec container1 ip addr
# lo만 존재

# veth pair 생성 (호스트 <-> 컨테이너)
sudo ip link add veth0 type veth peer name veth1

# veth1을 namespace로 이동
sudo ip link set veth1 netns container1

# 호스트 측 설정
sudo ip addr add 10.0.0.1/24 dev veth0
sudo ip link set veth0 up

# 컨테이너 측 설정
sudo ip netns exec container1 ip addr add 10.0.0.2/24 dev veth1
sudo ip netns exec container1 ip link set veth1 up
sudo ip netns exec container1 ip link set lo up

# 통신 테스트
sudo ip netns exec container1 ping 10.0.0.1
```

### 실전 예제 2: Cgroup 직접 사용

#### Docker 컨테이너의 Cgroup 확인

```bash
# 컨테이너 실행 (CPU 제한)
docker run -d --name test --cpus=0.5 --memory=512m nginx

# Cgroup 경로 확인
docker inspect test | grep CgroupParent
# "CgroupParent": "/docker"

# Cgroup 파일 확인 (cgroup v2)
CONTAINER_ID=$(docker inspect test -f '{{.Id}}')
cat /sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope/cpu.max
# 50000 100000  (50% CPU)

cat /sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope/memory.max
# 536870912  (512MB)
```

#### Cgroup 수동 생성 및 제한

```bash
# CPU Cgroup 생성 (cgroup v2)
sudo mkdir /sys/fs/cgroup/myapp

# CPU 제한 (50%)
echo "50000 100000" | sudo tee /sys/fs/cgroup/myapp/cpu.max

# 메모리 제한 (512MB)
echo "536870912" | sudo tee /sys/fs/cgroup/myapp/memory.max

# 프로세스를 Cgroup에 추가
echo $$ | sudo tee /sys/fs/cgroup/myapp/cgroup.procs

# CPU 집약적 작업 실행 (제한 확인)
yes > /dev/null &
PID=$!

# CPU 사용률 확인 (50%로 제한됨)
top -p $PID

# 정리
kill $PID
```

#### Docker 컨테이너 Cgroup 실시간 수정

```bash
# 실행 중인 컨테이너 CPU 제한 변경
docker update --cpus=1.0 test

# 확인
cat /sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope/cpu.max
# 100000 100000  (100% CPU)

# 메모리 제한 변경
docker update --memory=1g test

# 확인
cat /sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope/memory.max
# 1073741824  (1GB)
```

### 실전 예제 3: 수동 컨테이너 생성

#### 최소한의 컨테이너 만들기

```bash
#!/bin/bash
# minimal-container.sh

# 1. 루트 파일시스템 준비
mkdir -p /tmp/container/rootfs
cd /tmp/container/rootfs

# 최소 파일시스템 생성
mkdir -p bin lib lib64 proc sys dev etc

# busybox 복사 (정적 링크 바이너리)
cp /bin/busybox bin/
ln -s busybox bin/sh
ln -s busybox bin/ls

# 2. Namespace 격리 + chroot
sudo unshare --pid --net --mount --uts --ipc --fork \
  chroot /tmp/container/rootfs /bin/sh -c '
    # 프로세스 파일시스템 마운트
    mount -t proc proc /proc
    mount -t sysfs sys /sys
    
    # 호스트명 변경
    hostname my-container
    
    # 쉘 실행
    /bin/sh
  '
```

#### runc로 컨테이너 직접 실행

```bash
# 1. 루트 파일시스템 준비
mkdir -p /tmp/mycontainer/rootfs
cd /tmp/mycontainer

# Alpine 루트 파일시스템 다운로드
curl -o alpine.tar.gz http://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.0-x86_64.tar.gz
tar -xzf alpine.tar.gz -C rootfs/

# 2. OCI 스펙 생성
runc spec

# 3. config.json 확인/수정
cat config.json
# process.args, mounts 등 설정

# 4. 컨테이너 실행
sudo runc run mycontainer

# 5. 다른 터미널에서 확인
sudo runc list
sudo runc state mycontainer
```

### 실전 예제 4: 네트워크 디버깅

#### Docker 네트워크 문제 디버깅

```bash
# 컨테이너 실행
docker run -d --name web nginx

# 컨테이너 PID
PID=$(docker inspect web -f '{{.State.Pid}}')

# 컨테이너 네트워크 namespace 진입
sudo nsenter --target $PID --net

# 네트워크 인터페이스 확인
ip addr
ip route

# 방화벽 규칙 확인
iptables -L -n

# 네트워크 연결 확인
ss -tulpn

# DNS 확인
cat /etc/resolv.conf

# 패킷 캡처
tcpdump -i eth0 -n

# 종료
exit
```

#### 컨테이너 간 네트워크 격리 확인

```bash
# 두 개의 컨테이너 실행
docker run -d --name web1 nginx
docker run -d --name web2 nginx

# 각 컨테이너의 네트워크 namespace
PID1=$(docker inspect web1 -f '{{.State.Pid}}')
PID2=$(docker inspect web2 -f '{{.State.Pid}}')

# Namespace ID 확인
sudo ls -l /proc/$PID1/ns/net
sudo ls -l /proc/$PID2/ns/net
# 다른 namespace (격리됨)

# 같은 네트워크에 있는지 확인
docker network inspect bridge | grep -A 5 web1
docker network inspect bridge | grep -A 5 web2
```

### 실전 예제 5: 리소스 모니터링

#### Cgroup 메트릭 직접 읽기

```bash
# 컨테이너 실행
docker run -d --name test --cpus=1 --memory=512m nginx

CONTAINER_ID=$(docker inspect test -f '{{.Id}}')
CGROUP_PATH="/sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope"

# CPU 사용량
cat $CGROUP_PATH/cpu.stat
# usage_usec 1234567890
# user_usec 1000000000
# system_usec 234567890

# 메모리 사용량
cat $CGROUP_PATH/memory.current
# 52428800  (50MB)

cat $CGROUP_PATH/memory.max
# 536870912  (512MB)

# 메모리 상세 통계
cat $CGROUP_PATH/memory.stat
# anon 12345678
# file 23456789
# ...

# I/O 통계
cat $CGROUP_PATH/io.stat
# 8:0 rbytes=1234567 wbytes=234567 rios=123 wios=45
```

#### 실시간 모니터링 스크립트

```bash
#!/bin/bash
# container-monitor.sh

CONTAINER_NAME=$1
CONTAINER_ID=$(docker inspect $CONTAINER_NAME -f '{{.Id}}')
CGROUP_PATH="/sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope"

while true; do
  clear
  echo "=== Container: $CONTAINER_NAME ==="
  echo
  
  # CPU
  CPU_USAGE=$(cat $CGROUP_PATH/cpu.stat | grep usage_usec | awk '{print $2}')
  echo "CPU Usage: $CPU_USAGE usec"
  
  # Memory
  MEM_CURRENT=$(cat $CGROUP_PATH/memory.current)
  MEM_MAX=$(cat $CGROUP_PATH/memory.max)
  MEM_PERCENT=$(awk "BEGIN {printf \"%.2f\", ($MEM_CURRENT/$MEM_MAX)*100}")
  echo "Memory: $(($MEM_CURRENT/1024/1024))MB / $(($MEM_MAX/1024/1024))MB ($MEM_PERCENT%)"
  
  # PIDs
  PID_COUNT=$(cat $CGROUP_PATH/cgroup.procs | wc -l)
  echo "Processes: $PID_COUNT"
  
  sleep 2
done
```

### 실전 예제 6: 보안 강화

#### Capabilities 확인 및 제한

```bash
# 기본 컨테이너 (많은 capabilities)
docker run --rm alpine sh -c 'apk add -q libcap; capsh --print'

# Capabilities 제거
docker run --rm --cap-drop=ALL --cap-add=NET_BIND_SERVICE alpine sh -c '
  apk add -q libcap
  capsh --print
'

# 컨테이너 프로세스 capabilities 확인
docker run -d --name test nginx
PID=$(docker inspect test -f '{{.State.Pid}}')
grep Cap /proc/$PID/status
# CapEff: 00000000a80425fb  (16진수)

# 해석
capsh --decode=00000000a80425fb
```

#### Seccomp 프로파일 적용

```bash
# 기본 seccomp 프로파일 확인
docker run --rm alpine sh -c 'grep Seccomp /proc/self/status'
# Seccomp: 2  (필터링 활성화)

# seccomp 비활성화 (위험!)
docker run --rm --security-opt seccomp=unconfined alpine sh -c '
  grep Seccomp /proc/self/status
'
# Seccomp: 0  (비활성화)

# 커스텀 seccomp 프로파일
cat > seccomp-profile.json <<EOF
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "exit", "exit_group"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

docker run --rm --security-opt seccomp=seccomp-profile.json alpine echo "test"
```

## 실제 동작 예시

### LXD 컨테이너 생성 시

```bash
$ lxc launch ubuntu:22.04 web
```

**내부 동작:**
```
1. LXD (High-level)
   - 이미지 다운로드
   - 설정 생성
   
2. LXC (Mid-level)
   - liblxc 호출
   - 컨테이너 설정 적용
   
3. Kernel (Low-level)
   - PID namespace 생성
   - NET namespace 생성
   - MNT namespace 생성
   - Cgroup 생성 (CPU, 메모리 제한)
   - 프로세스 시작 (init/systemd)
```

### Docker 컨테이너 생성 시

```bash
$ docker run -d nginx
```

**내부 동작:**
```
1. Docker (High-level)
   - 이미지 pull
   - 컨테이너 설정
   
2. containerd (Mid-level)
   - 이미지 압축 해제
   - 파일시스템 준비
   
3. runc (OCI runtime)
   - 컨테이너 스펙 생성
   
4. Kernel (Low-level)
   - Namespace 생성
   - Cgroup 생성
   - nginx 프로세스 시작
```

## 트러블슈팅

### 문제 1: 컨테이너가 시작되지 않음

```bash
# Docker 로그 확인
docker logs container-name

# Low-level 확인
PID=$(docker inspect container-name -f '{{.State.Pid}}')

# Namespace 확인
sudo ls -l /proc/$PID/ns/

# Cgroup 확인
cat /sys/fs/cgroup/system.slice/docker-*.scope/cgroup.procs

# OOM (메모리 부족) 확인
dmesg | grep -i oom
```

### 문제 2: 네트워크 연결 안 됨

```bash
# 컨테이너 네트워크 진입
PID=$(docker inspect container-name -f '{{.State.Pid}}')
sudo nsenter --target $PID --net

# 네트워크 설정 확인
ip addr
ip route
iptables -L -n

# DNS 확인
cat /etc/resolv.conf
nslookup google.com

# 호스트와 통신 확인
ping 172.17.0.1  # Docker bridge IP
```

### 문제 3: 리소스 제한 작동 안 함

```bash
# Cgroup 설정 확인
CONTAINER_ID=$(docker inspect container-name -f '{{.Id}}')
CGROUP_PATH="/sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope"

# CPU 제한 확인
cat $CGROUP_PATH/cpu.max

# 메모리 제한 확인
cat $CGROUP_PATH/memory.max

# 실제 사용량
cat $CGROUP_PATH/cpu.stat
cat $CGROUP_PATH/memory.current
```

### 문제 4: 권한 문제

```bash
# Capabilities 확인
PID=$(docker inspect container-name -f '{{.State.Pid}}')
grep Cap /proc/$PID/status

# User namespace 확인
sudo ls -l /proc/$PID/ns/user

# UID 매핑 확인
cat /proc/$PID/uid_map
cat /proc/$PID/gid_map
```

## 추상화 레벨 비교

```
High-level (추상화 높음, 사용 쉬움):
┌──────────────────────────┐
│  LXD, Docker, Podman     │  ← 사용자가 주로 사용
└──────────────────────────┘

Mid-level (중간 추상화):
┌──────────────────────────┐
│  LXC, containerd, runc   │  ← 도구가 내부적으로 사용
└──────────────────────────┘

Low-level (추상화 낮음, 직접 사용 어려움):
┌──────────────────────────┐
│  Namespaces, Cgroups     │  ← 커널 기능, 트러블슈팅 시 사용
└──────────────────────────┘
```

## 직접 사용 vs 간접 사용

### 사용자가 직접 사용 (High-level)
```bash
# LXD
lxc launch ubuntu:22.04 web

# Docker
docker run nginx

# Podman
podman run nginx
```

### 도구가 내부적으로 사용 (Mid-level)
```bash
# LXC (LXD가 내부적으로 호출)
lxc-create -n web -t ubuntu

# runc (Docker가 내부적으로 호출)
runc run container-id
```

### 커널이 제공 (Low-level)
```bash
# Namespace 생성 (시스템 콜)
unshare --pid --net --mount /bin/bash

# Cgroup 설정 (파일시스템)
echo 1000000 > /sys/fs/cgroup/cpu/mygroup/cpu.cfs_quota_us
```

## 유용한 도구

### Namespace 관련
```bash
# 모든 namespace 확인
lsns

# 특정 프로세스 namespace
lsns -p PID

# Namespace 진입
nsenter --target PID --all

# 특정 namespace만 진입
nsenter --target PID --net --pid
```

### Cgroup 관련
```bash
# Cgroup 트리 확인
systemd-cgls

# Cgroup 리소스 사용량
systemd-cgtop

# 프로세스의 Cgroup 확인
cat /proc/PID/cgroup

# Cgroup 버전 확인
mount | grep cgroup
# cgroup2 = v2 (통합)
# cgroup = v1 (레거시)
```

### 컨테이너 런타임
```bash
# runc 컨테이너 목록
sudo runc list

# containerd 컨테이너
sudo ctr containers list
sudo ctr namespaces list

# Docker 내부 정보
docker inspect container-name

# 컨테이너 프로세스 트리
pstree -p $(docker inspect container-name -f '{{.State.Pid}}')
```

## 실무 활용 시나리오

### 시나리오 1: 컨테이너 성능 문제

```bash
# 1. 리소스 사용량 확인
docker stats container-name

# 2. Cgroup 상세 확인
CONTAINER_ID=$(docker inspect container-name -f '{{.Id}}')
CGROUP_PATH="/sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope"

# CPU throttling 확인
cat $CGROUP_PATH/cpu.stat | grep throttled
# nr_throttled: 횟수
# throttled_usec: 총 시간

# 3. 제한 완화
docker update --cpus=2.0 container-name

# 4. 재확인
cat $CGROUP_PATH/cpu.max
```

### 시나리오 2: 네트워크 지연 문제

```bash
# 1. 컨테이너 네트워크 진입
PID=$(docker inspect container-name -f '{{.State.Pid}}')
sudo nsenter --target $PID --net

# 2. 네트워크 통계
ss -s
netstat -i

# 3. 패킷 손실 확인
ping -c 100 8.8.8.8 | grep loss

# 4. MTU 확인
ip link show eth0

# 5. 라우팅 테이블
ip route show

# 6. iptables 규칙 (NAT 확인)
iptables -t nat -L -n
```

### 시나리오 3: 메모리 부족 (OOM)

```bash
# 1. OOM 이벤트 확인
dmesg | grep -i "out of memory"
dmesg | grep -i "killed process"

# 2. 컨테이너 메모리 사용량
CONTAINER_ID=$(docker inspect container-name -f '{{.Id}}')
CGROUP_PATH="/sys/fs/cgroup/system.slice/docker-${CONTAINER_ID}.scope"

cat $CGROUP_PATH/memory.current
cat $CGROUP_PATH/memory.max
cat $CGROUP_PATH/memory.events | grep oom

# 3. 메모리 상세 분석
cat $CGROUP_PATH/memory.stat

# 4. 메모리 제한 증가
docker update --memory=2g container-name
```

### 시나리오 4: 보안 감사

```bash
# 1. 실행 중인 컨테이너 권한 확인
for container in $(docker ps -q); do
  echo "=== Container: $container ==="
  PID=$(docker inspect $container -f '{{.State.Pid}}')
  
  # Capabilities
  echo "Capabilities:"
  grep Cap /proc/$PID/status
  
  # Seccomp
  echo "Seccomp:"
  grep Seccomp /proc/$PID/status
  
  # User namespace
  echo "User namespace:"
  ls -l /proc/$PID/ns/user
  
  echo
done

# 2. 권한 과다 컨테이너 찾기
docker ps --format '{{.Names}}' | while read name; do
  if docker inspect $name | grep -q '"Privileged": true'; then
    echo "WARNING: $name is running in privileged mode!"
  fi
done

# 3. 호스트 네트워크 사용 컨테이너
docker ps --format '{{.Names}}' | while read name; do
  if docker inspect $name | grep -q '"NetworkMode": "host"'; then
    echo "WARNING: $name is using host network!"
  fi
done
```

## Cgroup v1 vs v2 차이

### Cgroup v1 (레거시)
```bash
# 경로
/sys/fs/cgroup/cpu/
/sys/fs/cgroup/memory/
/sys/fs/cgroup/blkio/

# 각 리소스별 별도 계층
```

### Cgroup v2 (현재)
```bash
# 경로
/sys/fs/cgroup/

# 통합 계층
# cpu.max, memory.max 등 한 곳에

# 확인
mount | grep cgroup2
```

### 호환성 확인
```bash
# 시스템 cgroup 버전
stat -fc %T /sys/fs/cgroup/
# cgroup2fs = v2
# tmpfs = v1

# Docker cgroup 드라이버
docker info | grep "Cgroup Driver"
# cgroupfs 또는 systemd
```

## 결론

**계층 구조 요약:**
```
High-level:  LXD, Docker, Podman (사용자 친화적)
             v 사용
Mid-level:   LXC, containerd, runc (라이브러리/런타임)
             v 사용
Low-level:   Namespaces, Cgroups (커널 기능)
             v 제공
Kernel:      Linux Kernel (기반)
```

**Low-level 직접 사용:**
- 트러블슈팅 (필수)
- 성능 최적화
- 보안 강화
- 커스텀 솔루션 개발
- 깊은 이해

**사용자 관점:**
- 일상: High-level 도구 (Docker, LXD)
- 문제 발생: Low-level 확인 (Namespace, Cgroup)
- 최적화: Low-level 조정

**간단히: "위로 갈수록 쉽고, 아래로 갈수록 복잡하지만 강력함"**

---

**참고 자료:**
- Linux Kernel Documentation: https://www.kernel.org/doc/
- Docker Documentation: https://docs.docker.com/
- LXD Documentation: https://linuxcontainers.org/lxd/
- OCI Specification: https://opencontainers.org/

**업데이트:**
- 2026-01-29: 초안 작성
