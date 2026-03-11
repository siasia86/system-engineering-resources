# iotop - I/O 모니터링 도구

## iotop이란?

**I/O Monitoring Tool** - 프로세스별 디스크 I/O 사용량을 실시간으로 모니터링하는 top과 유사한 도구입니다.

## 주요 기능

- 실시간 I/O 모니터링
- 프로세스별 읽기/쓰기 속도
- 누적 I/O 통계
- 스레드별 I/O 추적
- I/O 우선순위 표시

## 설치

```bash
# Ubuntu/Debian
sudo apt-get install iotop

# CentOS/RHEL
sudo yum install iotop

# Fedora
sudo dnf install iotop

# 버전 확인
iotop --version
```

## 기본 사용법

### 실행

```bash
# 기본 실행 (sudo 필요)
sudo iotop

# 배치 모드 (스크립트용)
sudo iotop -b

# 특정 횟수만
sudo iotop -b -n 5
```

**출력 예시:**
```
Total DISK READ:       2.50 M/s | Total DISK WRITE:       5.00 M/s
  TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN     IO>    COMMAND
 1234 be/4 root        0.00 B/s    2.50 M/s  0.00 %  5.00 % mysqld
 5678 be/4 user        2.50 M/s    0.00 B/s  0.00 %  2.00 % rsync
```

**컬럼 설명:**
- TID: 스레드 ID
- PRIO: I/O 우선순위
- USER: 사용자
- DISK READ: 읽기 속도
- DISK WRITE: 쓰기 속도
- SWAPIN: 스왑 사용률
- IO>: I/O 대기 비율
- COMMAND: 명령어

## 주요 옵션

### 표시 옵션

```bash
# 프로세스만 표시 (스레드 숨김)
sudo iotop -P

# 누적 I/O 표시
sudo iotop -a

# I/O 발생 프로세스만
sudo iotop -o

# 프로세스와 누적 I/O
sudo iotop -P -a
```

### 정렬 옵션

```bash
# 읽기 속도로 정렬
sudo iotop -o -k

# 쓰기 속도로 정렬
sudo iotop -o -k

# I/O 대기로 정렬 (기본값)
sudo iotop
```

### 업데이트 간격

```bash
# 1초마다 업데이트 (기본값)
sudo iotop

# 5초마다
sudo iotop -d 5

# 0.5초마다
sudo iotop -d 0.5
```

### 특정 프로세스

```bash
# 특정 PID만
sudo iotop -p 1234

# 여러 PID
sudo iotop -p 1234 -p 5678

# 특정 사용자
sudo iotop -u username
```

## 대화형 키

```
좌/우 화살표: 정렬 컬럼 변경
r: 정렬 순서 반전
o: I/O 발생 프로세스만 토글
p: 프로세스/스레드 토글
a: 누적 I/O 토글
q: 종료
```

## 실전 예제

### 예제 1: I/O 병목 찾기

```bash
# I/O 발생 프로세스만 표시
sudo iotop -o

# 누적 I/O로 정렬
sudo iotop -o -a

# 출력:
# Total DISK READ:       10.00 M/s | Total DISK WRITE:       50.00 M/s
#   TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN     IO>    COMMAND
#  1234 be/4 mysql       5.00 M/s   45.00 M/s  0.00 % 80.00 % mysqld
```

### 예제 2: 특정 프로세스 모니터링

```bash
# MySQL I/O 모니터링
sudo iotop -p $(pgrep mysqld)

# 여러 프로세스
for pid in $(pgrep nginx); do
    sudo iotop -p $pid -b -n 1
done
```

### 예제 3: 로그 기록

```bash
# 배치 모드로 로그 저장
sudo iotop -b -n 60 -d 1 > iotop.log

# 타임스탬프 포함
while true; do
    echo "=== $(date) ==="
    sudo iotop -b -n 1 -o
    sleep 5
done > iotop_timestamped.log
```

### 예제 4: 높은 I/O 프로세스 찾기

```bash
# I/O 대기가 높은 프로세스
sudo iotop -o -a | awk '$7 > 50 {print}'

# 쓰기가 많은 프로세스
sudo iotop -b -n 1 -o | sort -k6 -rn | head -10
```

### 예제 5: 실시간 알림

```bash
#!/bin/bash
# io_alert.sh

THRESHOLD=100  # MB/s

while true; do
    WRITE=$(sudo iotop -b -n 1 -o | awk 'NR==1 {print $7}' | sed 's/[^0-9.]//g')
    
    if (( $(echo "$WRITE > $THRESHOLD" | bc -l) )); then
        echo "High I/O detected: ${WRITE} MB/s"
        # 알림 전송
    fi
    
    sleep 5
done
```

## 배치 모드 활용

### CSV 형식 출력

```bash
# 헤더 포함
sudo iotop -b -n 1 -P | awk 'NR>1 {print $1","$3","$4","$5","$6","$7","$8}'

# 스크립트
#!/bin/bash
echo "Timestamp,TID,User,Read,Write,IO%,Command"
while true; do
    sudo iotop -b -n 1 -P -o | awk -v date="$(date +%s)" 'NR>1 {print date","$1","$3","$4","$5","$7","$8}'
    sleep 5
done > iotop.csv
```

### 통계 수집

```bash
# 1분간 평균 I/O
sudo iotop -b -n 60 -d 1 | awk '
/Total DISK READ/ {
    read += $4;
    write += $10;
    count++;
}
END {
    print "Avg Read:", read/count, "MB/s";
    print "Avg Write:", write/count, "MB/s";
}'
```

## 실무 활용

### 1. 성능 문제 진단

```bash
# 디스크 I/O 병목 확인
sudo iotop -o -a

# 특정 시간대 모니터링
sudo iotop -b -n 3600 -d 1 > iotop_$(date +%Y%m%d_%H%M).log
```

### 2. 데이터베이스 최적화

```bash
# MySQL I/O 패턴 분석
sudo iotop -p $(pgrep mysqld) -b -n 600 -d 1 > mysql_io.log

# 분석
awk '/mysqld/ {read+=$4; write+=$5; count++} END {print "Avg Read:", read/count, "Avg Write:", write/count}' mysql_io.log
```

### 3. 백업 모니터링

```bash
# rsync I/O 모니터링
sudo iotop -p $(pgrep rsync) -o

# 백업 스크립트에 통합
#!/bin/bash
sudo iotop -b -p $$ > backup_io.log &
IOTOP_PID=$!

rsync -av /source /dest

kill $IOTOP_PID
```

### 4. 용량 계획

```bash
# 일일 I/O 통계
sudo iotop -b -n 86400 -d 1 | awk '
/Total DISK WRITE/ {
    total += $10;
}
END {
    print "Total written today:", total, "MB";
}'
```

### 5. 알림 시스템

```bash
#!/bin/bash
# io_monitor.sh

THRESHOLD=500  # MB/s
EMAIL="siasia.linux@gmail.com"

while true; do
    TOTAL_WRITE=$(sudo iotop -b -n 1 | awk '/Total DISK WRITE/ {print $10}')
    
    if (( $(echo "$TOTAL_WRITE > $THRESHOLD" | bc -l) )); then
        echo "High I/O: $TOTAL_WRITE MB/s" | mail -s "I/O Alert" $EMAIL
        sudo iotop -b -n 10 > /tmp/iotop_alert_$(date +%s).log
    fi
    
    sleep 60
done
```

## 대안 도구

### iotop-c (C 버전)

```bash
# 더 빠른 C 구현
sudo apt-get install iotop-c
sudo iotop-c
```

### iostat

```bash
# 디바이스별 I/O 통계
iostat -x 1

# 확장 통계
iostat -xz 1
```

### dstat

```bash
# 통합 시스템 통계
dstat -d  # 디스크만
dstat -D sda,sdb  # 특정 디스크
```

## 트러블슈팅

### 문제 1: "CONFIG_TASK_IO_ACCOUNTING not enabled"

```bash
# 원인: 커널 설정 미지원
# 해결: 커널 재컴파일 또는 다른 도구 사용

# 대안
iostat -x 1
```

### 문제 2: "Permission denied"

```bash
# 해결: sudo 사용
sudo iotop

# 또는 권한 부여
sudo setcap cap_net_admin=eip /usr/sbin/iotop
```

### 문제 3: 출력이 너무 빠름

```bash
# 업데이트 간격 증가
sudo iotop -d 5

# 또는 배치 모드
sudo iotop -b -n 10
```

## 성능 고려사항

```bash
# iotop 자체의 오버헤드
# - CPU: < 1%
# - 메모리: < 10MB
# - I/O: 거의 없음

# 프로덕션 환경에서 안전하게 사용 가능
```

## 스크립트 예제

### 자동 모니터링

```bash
#!/bin/bash
# auto_iotop.sh

LOG_DIR="/var/log/iotop"
DURATION=3600  # 1시간

mkdir -p $LOG_DIR

while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    LOG_FILE="$LOG_DIR/iotop_$TIMESTAMP.log"
    
    echo "Starting monitoring: $LOG_FILE"
    sudo iotop -b -n $DURATION -d 1 > $LOG_FILE
    
    # 7일 이상 된 로그 삭제
    find $LOG_DIR -name "iotop_*.log" -mtime +7 -delete
done
```

### 리포트 생성

```bash
#!/bin/bash
# iotop_report.sh

LOG_FILE=$1

echo "=== I/O Report ==="
echo ""
echo "Top I/O Processes:"
awk '/Total DISK/ {next} NR>1 {print $8, $4, $5}' $LOG_FILE | \
    sort -k2 -rn | head -10

echo ""
echo "Total I/O:"
awk '/Total DISK READ/ {read+=$4; write+=$10; count++} 
     END {print "Avg Read:", read/count, "MB/s"; 
          print "Avg Write:", write/count, "MB/s"}' $LOG_FILE
```

## 관련 도구

| 도구 | 용도 |
|------|------|
| **iotop** | 프로세스별 I/O |
| **iostat** | 디바이스별 I/O |
| **dstat** | 통합 시스템 통계 |
| **atop** | 고급 시스템 모니터 |
| **nmon** | 성능 모니터 |

## 요약

**iotop의 강점:**
- 실시간 I/O 모니터링
- 프로세스별 상세 정보
- 낮은 오버헤드
- 사용하기 쉬움

**주요 옵션:**
- `-o` - I/O 발생 프로세스만
- `-a` - 누적 I/O
- `-P` - 프로세스만
- `-b` - 배치 모드
- `-p` - 특정 PID

**언제 사용?**
- I/O 병목 찾기
- 디스크 성능 문제
- 프로세스 I/O 분석
- 용량 계획
