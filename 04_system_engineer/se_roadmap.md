# System Engineer (SE) 커리어 로드맵

> **내부 공유 자료**  
> 작성일: 2026-01-29  
> 버전: 1.0  
> 대상: SE 지망생, Junior SE

## 목차
- [전체 로드맵](#전체-로드맵)
- [Junior SE (0-2년)](#junior-se-0-2년)
- [Mid-level SE (2-5년)](#mid-level-se-2-5년)
- [Senior SE (5-8년)](#senior-se-5-8년)
- [Lead SE (8년+)](#lead-se-8년)
- [자격증](#자격증-가이드)
- [학습 자료](#학습-자료)

## 전체 로드맵

```
Junior SE (0-2년)
    ↓
    Linux 기초 + 네트워킹 + 스크립팅
    
Mid-level SE (2-5년)
    ↓
    고급 시스템 관리 + 클라우드 + 자동화
    
Senior SE (5-8년)
    ↓
    아키텍처 설계 + 멘토링 + 전문화
    
Lead SE / Architect (8년+)
    ↓
    전략 수립 + 팀 관리 + 기술 리더십
```

## Junior SE (0-2년)

### 1단계: 기초 다지기 (0-6개월)

#### Linux 기본

**필수 명령어**
```bash
# 파일 시스템
ls, cd, pwd, cp, mv, rm, mkdir, touch
cat, less, head, tail, grep, find

# 권한 관리
chmod 755 file.sh
chown user:group file.txt
ls -la

# 프로세스 관리
ps aux
top, htop
kill, pkill
systemctl start/stop/restart service
```

**파일 시스템 구조**
```
/           # 루트
/etc        # 설정 파일
/var        # 가변 데이터 (로그)
/home       # 사용자 홈
/usr        # 프로그램
/tmp        # 임시 파일
/opt        # 추가 소프트웨어
```

**실습 과제:**
1. Linux 서버 설치 (Ubuntu 22.04 LTS)
2. SSH 접속 설정
3. 사용자 계정 생성 및 sudo 권한 부여
4. 기본 명령어 100번씩 연습

#### 네트워킹 기초

**핵심 개념**
```
IP 주소: 192.168.1.100
서브넷 마스크: 255.255.255.0 (/24)
게이트웨이: 192.168.1.1
DNS: 8.8.8.8, 1.1.1.1
포트: 22(SSH), 80(HTTP), 443(HTTPS), 3306(MySQL)
```

**필수 명령어**
```bash
# 네트워크 확인
ip addr show
ip route show
ping google.com
traceroute google.com
nslookup google.com

# 연결 확인
netstat -tuln
ss -tuln
lsof -i :80

# 방화벽
iptables -L
firewall-cmd --list-all
ufw status
```

**실습 과제:**
1. 고정 IP 설정
2. DNS 서버 변경
3. 방화벽 규칙 추가 (포트 80, 443 허용)
4. 네트워크 문제 진단 연습

#### 웹 서버 기초

**Apache**
```bash
# 설치
sudo apt-get install apache2

# 관리
sudo systemctl start apache2
sudo systemctl enable apache2
sudo systemctl status apache2

# 설정
/etc/apache2/apache2.conf
/etc/apache2/sites-available/
/var/www/html/
```

**Nginx**
```bash
# 설치
sudo apt-get install nginx

# 관리
sudo systemctl start nginx
sudo systemctl enable nginx

# 설정
/etc/nginx/nginx.conf
/etc/nginx/sites-available/
/usr/share/nginx/html/
```

**실습 과제:**
1. Apache 설치 및 기본 페이지 확인
2. Nginx 설치 및 설정
3. 가상 호스트 설정
4. SSL 인증서 설정 (Let's Encrypt)

### 2단계: 실무 기초 (6-12개월)

#### 사용자 및 권한 관리

```bash
# 사용자 관리
useradd -m -s /bin/bash username
passwd username
usermod -aG sudo username
userdel -r username

# 그룹 관리
groupadd developers
usermod -aG developers username
groups username

# sudo 설정
visudo
# username ALL=(ALL:ALL) ALL
```

#### 패키지 관리

**Ubuntu/Debian (apt)**
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install package
sudo apt-get remove package
sudo apt-cache search keyword
```

**CentOS/RHEL (yum/dnf)**
```bash
sudo yum update
sudo yum install package
sudo yum remove package
sudo yum search keyword
```

#### 로그 관리

```bash
# 주요 로그 위치
/var/log/syslog          # 시스템 로그 (Ubuntu)
/var/log/messages        # 시스템 로그 (CentOS)
/var/log/auth.log        # 인증 로그
/var/log/apache2/        # Apache 로그
/var/log/nginx/          # Nginx 로그

# 로그 확인
tail -f /var/log/syslog
journalctl -f
journalctl -u nginx.service

# 로그 로테이션
/etc/logrotate.conf
/etc/logrotate.d/
```

#### 백업 및 복구

**tar 백업**
```bash
# 압축 백업
tar -czf backup_$(date +%Y%m%d).tar.gz /data

# 압축 해제
tar -xzf backup.tar.gz

# 증분 백업
tar -czf backup.tar.gz --listed-incremental=snapshot.file /data
```

**rsync 백업**
```bash
# 로컬 백업
rsync -av /source/ /backup/

# 원격 백업
rsync -av /source/ user@remote:/backup/

# 삭제된 파일도 동기화
rsync -av --delete /source/ /backup/
```

**자동 백업 스크립트**
```bash
#!/bin/bash
# /usr/local/bin/backup.sh

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE="/var/www"

# 백업 실행
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $SOURCE

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

# 로그
echo "Backup completed: $DATE" >> /var/log/backup.log
```

**cron 설정**
```bash
# crontab 편집
crontab -e

# 매일 새벽 2시 백업
0 2 * * * /usr/local/bin/backup.sh
```

### 3단계: 심화 학습 (12-24개월)

#### Bash 스크립팅

**기본 문법**
```bash
#!/bin/bash

# 변수
NAME="Server01"
COUNT=10

# 조건문
if [ $COUNT -gt 5 ]; then
    echo "Count is greater than 5"
fi

# 반복문
for i in {1..5}; do
    echo "Number: $i"
done

# 함수
check_service() {
    systemctl is-active $1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "$1 is running"
    else
        echo "$1 is not running"
    fi
}

check_service nginx
```

**실용 스크립트 예제**
```bash
#!/bin/bash
# 서버 헬스 체크

# CPU 사용률
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# 메모리 사용률
MEM=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')

# 디스크 사용률
DISK=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')

# 알림
if [ $(echo "$CPU > 80" | bc) -eq 1 ]; then
    echo "High CPU: $CPU%" | mail -s "Alert" siasia.linux@gmail.com
fi

if [ $MEM -gt 80 ]; then
    echo "High Memory: $MEM%" | mail -s "Alert" siasia.linux@gmail.com
fi

if [ $DISK -gt 80 ]; then
    echo "High Disk: $DISK%" | mail -s "Alert" siasia.linux@gmail.com
fi
```

#### 가상화

**VMware ESXi**
```
- vSphere Client 사용
- VM 생성 및 관리
- 스냅샷 관리
- 리소스 할당
- 네트워크 설정
```

**KVM/QEMU**
```bash
# 설치
sudo apt-get install qemu-kvm libvirt-daemon-system

# VM 생성
virt-install --name vm01 \
  --ram 2048 \
  --disk path=/var/lib/libvirt/images/vm01.qcow2,size=20 \
  --vcpus 2 \
  --os-type linux \
  --network bridge=virbr0 \
  --cdrom /path/to/ubuntu.iso

# 관리
virsh list --all
virsh start vm01
virsh shutdown vm01
```

#### 스토리지 관리

**LVM (Logical Volume Manager)**
```bash
# 물리 볼륨 생성
pvcreate /dev/sdb

# 볼륨 그룹 생성
vgcreate vg_data /dev/sdb

# 논리 볼륨 생성
lvcreate -L 50G -n lv_data vg_data

# 파일시스템 생성
mkfs.ext4 /dev/vg_data/lv_data

# 마운트
mount /dev/vg_data/lv_data /data

# 용량 확장
lvextend -L +10G /dev/vg_data/lv_data
resize2fs /dev/vg_data/lv_data
```

**RAID**
```bash
# RAID 1 생성
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# 상태 확인
cat /proc/mdstat
mdadm --detail /dev/md0

# 설정 저장
mdadm --detail --scan >> /etc/mdadm/mdadm.conf
```

**NFS 서버**
```bash
# 설치
sudo apt-get install nfs-kernel-server

# 공유 설정
echo "/data 192.168.1.0/24(rw,sync,no_subtree_check)" >> /etc/exports

# 적용
exportfs -a
systemctl restart nfs-kernel-server

# 클라이언트 마운트
mount -t nfs server:/data /mnt/data
```


## Mid-level SE (2-5년)

### 고급 시스템 관리

#### 성능 튜닝

**커널 파라미터**
```bash
# 현재 설정 확인
sysctl -a

# 설정 변경
sysctl -w net.ipv4.tcp_max_syn_backlog=4096

# 영구 설정
echo "net.ipv4.tcp_max_syn_backlog = 4096" >> /etc/sysctl.conf
sysctl -p
```

**주요 튜닝 파라미터**
```bash
# 네트워크
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535

# 파일 디스크립터
fs.file-max = 2097152

# 메모리
vm.swappiness = 10
vm.dirty_ratio = 15
```

#### 고가용성 (HA)

**Keepalived (VRRP)**
```bash
# /etc/keepalived/keepalived.conf
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    
    virtual_ipaddress {
        192.168.1.100
    }
}
```

**HAProxy 로드 밸런싱**
```bash
# /etc/haproxy/haproxy.cfg
frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    server web1 192.168.1.10:80 check
    server web2 192.168.1.11:80 check
```

#### 보안 강화

**방화벽 (iptables)**
```bash
# 기본 정책
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# SSH 허용
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# HTTP/HTTPS 허용
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 저장
iptables-save > /etc/iptables/rules.v4
```

**SSH 보안**
```bash
# /etc/ssh/sshd_config
Port 2222                    # 기본 포트 변경
PermitRootLogin no           # root 로그인 금지
PasswordAuthentication no    # 패스워드 인증 금지
PubkeyAuthentication yes     # 키 인증만 허용
```

**fail2ban**
```bash
# 설치
sudo apt-get install fail2ban

# 설정
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 2222
maxretry = 3
bantime = 3600
```

#### 클라우드 (AWS 기초)

**EC2 관리**
```bash
# AWS CLI 설치
sudo apt-get install awscli

# 설정
aws configure

# 인스턴스 목록
aws ec2 describe-instances

# 인스턴스 시작/중지
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

**S3 백업**
```bash
# 파일 업로드
aws s3 cp backup.tar.gz s3://my-bucket/

# 동기화
aws s3 sync /data s3://my-bucket/data/

# 다운로드
aws s3 cp s3://my-bucket/backup.tar.gz ./
```

**VPC 기본**
```
- VPC 생성
- 서브넷 구성 (Public/Private)
- 인터넷 게이트웨이
- 라우팅 테이블
- 보안 그룹
- NACL
```

### 모니터링 & 알림

**Zabbix**
```bash
# 서버 설치
sudo apt-get install zabbix-server-mysql zabbix-frontend-php

# 에이전트 설치
sudo apt-get install zabbix-agent

# 설정
# /etc/zabbix/zabbix_agentd.conf
Server=zabbix-server-ip
ServerActive=zabbix-server-ip
Hostname=web01
```

**Prometheus + Grafana**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### 자동화 기초

**Ansible**
```yaml
# inventory
[webservers]
web01 ansible_host=192.168.1.10
web02 ansible_host=192.168.1.11

# playbook.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
    
    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: yes
```

**실행**
```bash
ansible-playbook -i inventory playbook.yml
```

## Senior SE (5-8년)

### 아키텍처 설계

**3-Tier 아키텍처**
```
[Load Balancer]
    ↓
[Web Servers] (Apache/Nginx)
    ↓
[Application Servers] (Tomcat/Node.js)
    ↓
[Database Servers] (MySQL/PostgreSQL)
```

**고가용성 설계**
```
Region: ap-northeast-2
├─ AZ-A
│  ├─ Web Server 1
│  ├─ App Server 1
│  └─ DB Master
└─ AZ-C
   ├─ Web Server 2
   ├─ App Server 2
   └─ DB Slave
```

### 용량 계획

**리소스 모니터링**
```bash
# CPU 트렌드
sar -u 1 10

# 메모리 트렌드
sar -r 1 10

# 디스크 I/O
sar -d 1 10

# 네트워크
sar -n DEV 1 10
```

**예측 및 계획**
```
현재 사용량 분석
    ↓
성장률 계산
    ↓
3-6개월 후 예측
    ↓
용량 증설 계획
```

### 데이터베이스 관리

**MySQL 복제**
```sql
-- Master 설정
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-do-db = mydb

-- Slave 설정
[mysqld]
server-id = 2
relay-log = mysql-relay-bin
```

**백업 전략**
```bash
# Full 백업
mysqldump --all-databases > full_backup.sql

# 증분 백업 (바이너리 로그)
mysqlbinlog mysql-bin.000001 > incremental.sql

# 자동화
0 2 * * * /usr/local/bin/mysql_backup.sh
```

### 재해 복구 (DR)

**DR 계획**
```
1. RPO (Recovery Point Objective)
   - 데이터 손실 허용 시간: 1시간

2. RTO (Recovery Time Objective)
   - 복구 목표 시간: 4시간

3. 백업 전략
   - 일일 전체 백업
   - 시간별 증분 백업
   - 원격지 백업

4. 복구 절차
   - 백업 확인
   - 서버 복구
   - 데이터 복구
   - 서비스 재개
```

### 컨테이너 기초

**Docker**
```bash
# 이미지 빌드
docker build -t myapp:1.0 .

# 컨테이너 실행
docker run -d -p 80:80 --name web myapp:1.0

# 관리
docker ps
docker logs web
docker exec -it web bash
```

**Docker Compose**
```yaml
version: '3'
services:
  web:
    image: nginx
    ports:
      - "80:80"
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
```

## Lead SE / Architect (8년+)

### 기술 리더십

**팀 관리**
```
- 주니어 멘토링
- 기술 표준 수립
- 코드 리뷰
- 아키텍처 리뷰
- 기술 문서화
```

**프로세스 개선**
```
- 장애 대응 프로세스
- 변경 관리 프로세스
- 백업/복구 절차
- 보안 체크리스트
```

### 전략 수립

**인프라 로드맵**
```
현재 상태 분석
    ↓
문제점 파악
    ↓
개선 방안 수립
    ↓
우선순위 결정
    ↓
실행 계획
```

**비용 최적화**
```
- 리소스 사용률 분석
- 불필요한 리소스 제거
- 예약 인스턴스 활용
- 스팟 인스턴스 활용
- 자동 스케일링
```

### 고급 기술

**Kubernetes 기초**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

**Terraform**
```hcl
# main.tf
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"
  
  tags = {
    Name = "web-server"
  }
}
```


## 자격증 가이드

### Junior → Mid Level

**Linux+** (CompTIA)
- 난이도: ⭐⭐
- 비용: $300
- 유효기간: 3년
- 추천: Linux 기초 확인용

**LPIC-1** (Linux Professional Institute)
- 난이도: ⭐⭐
- 비용: $200 × 2 (101, 102)
- 유효기간: 평생
- 추천: 실무 기초 검증

**CompTIA Network+**
- 난이도: ⭐⭐
- 비용: $300
- 유효기간: 3년
- 추천: 네트워킹 기초

### Mid → Senior Level

**RHCSA** (Red Hat Certified System Administrator)
- 난이도: ⭐⭐⭐
- 비용: $400
- 유효기간: 3년
- 추천: 실무 능력 증명

**RHCE** (Red Hat Certified Engineer)
- 난이도: ⭐⭐⭐⭐
- 비용: $400
- 유효기간: 3년
- 추천: 고급 기술 증명

**AWS Solutions Architect Associate**
- 난이도: ⭐⭐⭐
- 비용: $150
- 유효기간: 3년
- 추천: 클라우드 필수

**LPIC-2**
- 난이도: ⭐⭐⭐
- 비용: $200 × 2 (201, 202)
- 유효기간: 평생
- 추천: Linux 고급

### Senior → Lead Level

**AWS Solutions Architect Professional**
- 난이도: ⭐⭐⭐⭐⭐
- 비용: $300
- 유효기간: 3년
- 추천: 클라우드 전문가

**RHCA** (Red Hat Certified Architect)
- 난이도: ⭐⭐⭐⭐⭐
- 비용: $2,000+
- 유효기간: 3년
- 추천: 최고 수준 증명

**CCIE** (Cisco Certified Internetwork Expert)
- 난이도: ⭐⭐⭐⭐⭐
- 비용: $1,600 (Lab)
- 유효기간: 3년
- 추천: 네트워크 전문가

## 기술 스택 체크리스트

### 필수 (Must Have)

**운영체제**
- [ ] Ubuntu/Debian
- [ ] CentOS/RHEL
- [ ] Linux 커널 기초

**네트워킹**
- [ ] TCP/IP
- [ ] DNS
- [ ] 방화벽 (iptables, firewalld)
- [ ] 로드 밸런싱

**서버**
- [ ] Apache
- [ ] Nginx
- [ ] Tomcat (선택)

**데이터베이스**
- [ ] MySQL/MariaDB
- [ ] PostgreSQL (선택)

**스크립팅**
- [ ] Bash
- [ ] Python (기초)

**가상화**
- [ ] VMware ESXi
- [ ] KVM/QEMU

**모니터링**
- [ ] Zabbix 또는 Nagios
- [ ] 로그 분석

**백업**
- [ ] tar, rsync
- [ ] 백업 전략

### 권장 (Should Have)

**클라우드**
- [ ] AWS (EC2, S3, VPC)
- [ ] Azure 또는 GCP (선택)

**자동화**
- [ ] Ansible
- [ ] Shell 스크립팅 고급

**컨테이너**
- [ ] Docker 기초
- [ ] Docker Compose

**보안**
- [ ] SSL/TLS
- [ ] VPN
- [ ] 보안 강화

**고가용성**
- [ ] Keepalived
- [ ] HAProxy
- [ ] 클러스터링

### 선택 (Nice to Have)

**고급 기술**
- [ ] Kubernetes
- [ ] Terraform
- [ ] CI/CD (Jenkins)
- [ ] Python 고급
- [ ] Go (선택)

**전문 분야**
- [ ] 네트워크 전문 (CCNA/CCNP)
- [ ] 보안 전문 (Security+)
- [ ] 클라우드 전문 (AWS Pro)

## 학습 자료

### 온라인 강의

**무료**
- Linux Journey (linuxjourney.com)
- YouTube - LearnLinuxTV
- YouTube - NetworkChuck
- AWS Free Tier 실습

**유료**
- Linux Academy / A Cloud Guru
- Udemy - Linux Administration
- Coursera - System Administration
- Pluralsight

### 책

**초급**
- "Linux Bible" - Christopher Negus
- "UNIX and Linux System Administration Handbook"

**중급**
- "The Practice of System and Network Administration"
- "Site Reliability Engineering" (Google)

**고급**
- "Systems Performance" - Brendan Gregg
- "TCP/IP Illustrated"

### 실습 환경

**로컬**
```
VirtualBox + Ubuntu VM (무료)
VMware Workstation Player (무료)
```

**클라우드**
```
AWS Free Tier (12개월 무료)
DigitalOcean ($5/month)
Linode ($5/month)
```

**홈랩**
```
중고 서버 구매 (Dell R720 등)
라즈베리 파이 클러스터
미니 PC (Intel NUC)
```

### 커뮤니티

**한국**
- KLDP (kldp.org)
- 생활코딩
- 44BITS
- AWS 한국 사용자 모임

**글로벌**
- Reddit - r/sysadmin, r/linuxadmin
- Server Fault (serverfault.com)
- Linux Questions (linuxquestions.org)

## 연봉 가이드

### 한국 (서울 기준, 2026년)

| 레벨 | 경력 | 연봉 범위 |
|------|------|----------|
| Junior SE | 0-2년 | 3,000만 - 4,500만원 |
| Mid-level SE | 2-5년 | 4,500만 - 6,500만원 |
| Senior SE | 5-8년 | 6,500만 - 9,000만원 |
| Lead SE | 8년+ | 9,000만 - 1억 2천만원+ |

**변수:**
- 회사 규모 (스타트업 vs 대기업)
- 기술 스택 (클라우드, 자동화)
- 자격증
- 영어 능력

### 글로벌 (미국 기준)

| 레벨 | 경력 | 연봉 범위 (USD) |
|------|------|----------------|
| Junior SE | 0-2년 | $60k - $80k |
| Mid-level SE | 2-5년 | $80k - $120k |
| Senior SE | 5-8년 | $120k - $160k |
| Lead SE | 8년+ | $160k - $220k+ |

## 커리어 전환 옵션

### SE에서 다른 역할로

```
SE → DevOps Engineer
    - 자동화 관심
    - 개발 능력 추가
    - CI/CD 경험

SE → Cloud Engineer
    - AWS/Azure/GCP 전문
    - 클라우드 아키텍처
    - 비용 최적화

SE → Security Engineer
    - 보안 전문화
    - 침투 테스트
    - 보안 감사

SE → Network Engineer
    - 네트워킹 전문화
    - CCNA/CCNP
    - SDN, NFV

SE → SRE
    - 개발 능력 강화
    - 자동화 고도화
    - SLA 관리

SE → IT Manager
    - 팀 관리
    - 프로젝트 관리
    - 예산 관리
```

## 실무 프로젝트 아이디어

### Junior Level

1. **홈랩 구축**
   - VirtualBox에 3대 서버 구성
   - 웹 서버, DB 서버, 백업 서버
   - 네트워크 설정 및 방화벽

2. **자동 백업 시스템**
   - Bash 스크립트 작성
   - cron 스케줄링
   - 이메일 알림

3. **모니터링 대시보드**
   - Zabbix 설치
   - 서버 모니터링 설정
   - 알림 규칙 설정

### Mid Level

1. **HA 웹 서비스**
   - Keepalived + HAProxy
   - 2대 웹 서버
   - 자동 failover

2. **AWS 3-Tier 아키텍처**
   - VPC 설계
   - ELB + EC2 + RDS
   - Auto Scaling

3. **Ansible 자동화**
   - 100대 서버 설정 자동화
   - 롤링 업데이트
   - 설정 관리

### Senior Level

1. **DR 시스템 구축**
   - 멀티 리전 구성
   - 자동 백업 및 복제
   - 복구 절차 문서화

2. **컨테이너 플랫폼**
   - Docker Swarm 또는 Kubernetes
   - CI/CD 파이프라인
   - 모니터링 통합

3. **인프라 코드화**
   - Terraform으로 전체 인프라 관리
   - GitOps 워크플로우
   - 자동 배포

## 성공을 위한 팁

### 학습 전략

1. **실습 중심**
   - 이론 20% : 실습 80%
   - 매일 최소 1시간 실습
   - 실패를 두려워하지 말기

2. **문서화 습관**
   - 배운 내용 정리
   - 트러블슈팅 기록
   - 개인 위키 운영

3. **커뮤니티 참여**
   - 질문하고 답변하기
   - 오픈소스 기여
   - 블로그 운영

### 면접 준비

**기술 면접 주제**
```
- Linux 기본 명령어
- 네트워킹 (TCP/IP, DNS)
- 트러블슈팅 경험
- 백업/복구 전략
- 보안 베스트 프랙티스
- 클라우드 경험
- 자동화 경험
```

**예상 질문**
```
1. 서버가 느려졌을 때 어떻게 진단하나요?
2. 백업 전략을 설명해주세요.
3. HA 구성 경험이 있나요?
4. 가장 어려웠던 장애 경험은?
5. 자동화 경험이 있나요?
```

### 지속적 성장

**매일**
- 새로운 명령어 1개 학습
- 기술 블로그 1개 읽기
- 실습 1시간

**매주**
- 새로운 기술 1개 학습
- 개인 프로젝트 진행
- 커뮤니티 참여

**매월**
- 학습 내용 정리
- 포트폴리오 업데이트
- 자격증 준비

**매년**
- 자격증 1개 취득
- 컨퍼런스 참석
- 커리어 목표 재설정

---

## 문서 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-01-29 | 초기 작성 |

---

**문서 관리자:** SRE Team  
**피드백:** siasia.linux@gmail.com  
**다음 리뷰:** 2026-04-29


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-11

© 2026 siasia86. Licensed under CC BY 4.0.
