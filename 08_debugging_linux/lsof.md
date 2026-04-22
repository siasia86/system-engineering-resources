# lsof - List Open Files

## lsof란?

**List Open Files** - 시스템에서 열린 파일과 파일을 사용하는 프로세스를 확인하는 도구입니다.

## 주요 기능

- 열린 파일 목록
- 프로세스별 파일 사용
- 네트워크 연결 확인
- 포트 사용 확인
- 삭제된 파일 추적

## 설치

```bash
# Ubuntu/Debian
sudo apt-get install lsof

# CentOS/RHEL
sudo yum install lsof

# 버전 확인
lsof -v
```

## 기본 사용법

### 모든 열린 파일

```bash
# 모든 열린 파일 (매우 많음)
lsof

# 개수 제한
lsof | head -20
```

**출력 형식:**
```
COMMAND    PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
bash      1234   user  cwd    DIR    8,1     4096  123 /home/user
bash      1234   user  txt    REG    8,1   123456  456 /bin/bash
```

**컬럼 설명:**
- COMMAND: 프로세스 이름
- PID: 프로세스 ID
- USER: 사용자
- FD: 파일 디스크립터
- TYPE: 파일 타입
- NAME: 파일 경로

### 특정 파일

```bash
# 특정 파일을 연 프로세스
lsof /var/log/syslog

# 특정 디렉토리
lsof +D /var/log

# 재귀적 검색
lsof +D /home/user
```

### 특정 프로세스

```bash
# PID로 검색
lsof -p 1234

# 프로세스 이름으로
lsof -c nginx

# 여러 프로세스
lsof -p 1234,5678

# 사용자별
lsof -u username

# 사용자 제외
lsof -u ^root
```

## 네트워크 연결

### 포트 확인

```bash
# 모든 네트워크 연결
lsof -i

# 특정 포트
lsof -i :80
lsof -i :3306

# 포트 범위
lsof -i :1-1024

# TCP만
lsof -i TCP

# UDP만
lsof -i UDP

# 특정 프로토콜과 포트
lsof -i TCP:80
```

### 연결 상태

```bash
# LISTEN 상태만
lsof -i -s TCP:LISTEN

# ESTABLISHED 상태만
lsof -i -s TCP:ESTABLISHED

# 특정 IP
lsof -i @192.168.1.100

# 특정 호스트
lsof -i @google.com
```

## 실전 예제

### 예제 1: 포트 사용 프로세스 찾기

```bash
# 80 포트 사용 프로세스
lsof -i :80

# 출력:
# COMMAND  PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# nginx   1234   root    6u  IPv4  12345      0t0  TCP *:http (LISTEN)
```

### 예제 2: 삭제된 파일 찾기

```bash
# 삭제되었지만 여전히 열린 파일
lsof | grep deleted

# 또는
lsof +L1

# 출력:
# COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NLINK NODE NAME
# app     1234 user    3r   REG    8,1  1048576     0  123 /tmp/file (deleted)
```

**디스크 공간 회복:**
```bash
# 프로세스 재시작 또는 종료
kill -HUP 1234
```

### 예제 3: 특정 사용자의 파일

```bash
# 사용자가 연 모든 파일
lsof -u username

# 여러 사용자
lsof -u user1,user2

# root 제외
lsof -u ^root
```

### 예제 4: 네트워크 연결 모니터링

```bash
# 실시간 모니터링
watch -n 1 'lsof -i -s TCP:ESTABLISHED'

# 특정 포트 모니터링
watch -n 1 'lsof -i :80'
```

### 예제 5: 파일 시스템 언마운트 문제

```bash
# 언마운트 실패 시
umount /mnt/data
# umount: /mnt/data: target is busy

# 사용 중인 프로세스 확인
lsof +D /mnt/data

# 출력:
# COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# bash    1234 user  cwd    DIR    8,2     4096    2 /mnt/data

# 프로세스 종료 후 언마운트
kill 1234
umount /mnt/data
```

## 고급 사용법

### 조합 검색

```bash
# AND 조건 (기본)
lsof -u user -i :80

# OR 조건
lsof -u user -o -i :80

# 복잡한 조건
lsof -a -u user -i :80  # user AND port 80
```

### 출력 형식

```bash
# 간단한 출력
lsof -t -i :80  # PID만

# 특정 컬럼만
lsof -F pcn  # PID, Command, Name

# 반복 실행
lsof -r 1 -i :80  # 1초마다
```

### 파일 디스크립터

```bash
# 특정 FD
lsof -d 0-2  # stdin, stdout, stderr

# 특정 타입
lsof -d txt  # 실행 파일
lsof -d mem  # 메모리 매핑
lsof -d cwd  # 현재 디렉토리
```

## 실무 활용

### 1. 포트 충돌 해결

```bash
# 포트 사용 확인
lsof -i :8080

# 프로세스 종료
kill $(lsof -t -i :8080)
```

### 2. 메모리 누수 의심

```bash
# 삭제된 파일 확인
lsof +L1

# 큰 파일 찾기
lsof | awk '$7 ~ /^[0-9]+$/ && $7 > 1000000000'
```

### 3. 네트워크 디버깅

```bash
# 외부 연결 확인
lsof -i -s TCP:ESTABLISHED | grep -v localhost

# 특정 서비스 연결
lsof -i -a -c nginx
```

### 4. 보안 감사

```bash
# 의심스러운 연결
lsof -i -s TCP:ESTABLISHED | grep -v "known_ips"

# root가 연 파일
lsof -u root
```

### 5. 성능 모니터링

```bash
# 파일 디스크립터 개수
lsof -p <PID> | wc -l

# 프로세스별 FD 사용
for pid in $(pgrep myapp); do
    echo "PID $pid: $(lsof -p $pid | wc -l) FDs"
done
```

## 출력 필터링

### grep과 조합

```bash
# 특정 파일 타입
lsof | grep REG  # 일반 파일
lsof | grep DIR  # 디렉토리
lsof | grep IPv4 # IPv4 소켓

# 특정 경로
lsof | grep /var/log

# 특정 프로토콜
lsof -i | grep TCP
```

### awk로 가공

```bash
# PID와 파일명만
lsof | awk '{print $2, $9}'

# 큰 파일만
lsof | awk '$7 > 1000000 {print $2, $9, $7}'

# 포트별 개수
lsof -i | awk '{print $9}' | sort | uniq -c
```

## 트러블슈팅

### 문제 1: "Permission denied"

```bash
# 해결: sudo 사용
sudo lsof

# 또는 특정 프로세스만
sudo lsof -p <PID>
```

### 문제 2: 출력이 너무 많음

```bash
# 필터링
lsof -i :80

# 개수 제한
lsof | head -100

# 특정 프로세스만
lsof -c nginx
```

### 문제 3: 느린 실행

```bash
# DNS 조회 비활성화
lsof -n

# 포트 이름 변환 비활성화
lsof -P

# 둘 다
lsof -nP
```

## 유용한 조합

### 스크립트 예제

```bash
#!/bin/bash
# check_port.sh - 포트 사용 확인

PORT=$1

if [ -z "$PORT" ]; then
    echo "Usage: $0 <port>"
    exit 1
fi

PID=$(lsof -t -i :$PORT)

if [ -z "$PID" ]; then
    echo "Port $PORT is free"
else
    echo "Port $PORT is used by:"
    lsof -i :$PORT
fi
```

### 모니터링 스크립트

```bash
#!/bin/bash
# monitor_connections.sh

while true; do
    clear
    echo "=== Network Connections ==="
    lsof -i -s TCP:ESTABLISHED | grep -v COMMAND
    echo ""
    echo "=== Listening Ports ==="
    lsof -i -s TCP:LISTEN | grep -v COMMAND
    sleep 5
done
```

## 파일 타입

| 타입     | 설명             |
|----------|------------------|
| **REG**  | 일반 파일        |
| **DIR**  | 디렉토리         |
| **CHR**  | 문자 장치        |
| **BLK**  | 블록 장치        |
| **FIFO** | 파이프           |
| **LINK** | 심볼릭 링크      |
| **unix** | Unix 도메인 소켓 |
| **IPv4** | IPv4 소켓        |
| **IPv6** | IPv6 소켓        |

## 파일 디스크립터

| FD      | 설명                   |
|---------|------------------------|
| **cwd** | 현재 작업 디렉토리     |
| **txt** | 프로그램 텍스트 (코드) |
| **mem** | 메모리 매핑 파일       |
| **0u**  | stdin                  |
| **1u**  | stdout                 |
| **2u**  | stderr                 |
| **3r**  | FD 3 읽기              |
| **4w**  | FD 4 쓰기              |
| **5u**  | FD 5 읽기/쓰기         |

## 관련 도구

| 도구        | 용도                    |
|-------------|-------------------------|
| **lsof**    | 열린 파일               |
| **fuser**   | 파일 사용 프로세스      |
| **netstat** | 네트워크 통계           |
| **ss**      | 소켓 통계               |
| **pfiles**  | 프로세스 파일 (Solaris) |

## 요약

**lsof의 강점:**
- 열린 파일 추적
- 네트워크 연결 확인
- 포트 사용 확인
- 삭제된 파일 찾기

**주요 옵션:**
- `-i` - 네트워크
- `-p` - 프로세스
- `-u` - 사용자
- `-c` - 명령어
- `+D` - 디렉토리

**언제 사용?**
- 포트 충돌 해결
- 파일 시스템 언마운트 문제
- 네트워크 디버깅
- 메모리 누수 확인
