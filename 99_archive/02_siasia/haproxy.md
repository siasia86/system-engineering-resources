# HAProxy 고가용성 구성 가이드

## 개요

HAProxy는 Active-Standby뿐만 아니라 다양한 고가용성 모드를 지원합니다. 각 모드의 특징과 구현 방법을 알아보겠습니다.

## HAProxy HA 모드 종류

### 1. Active-Standby (Keepalived + VRRP)

**현재 구현된 방식**

```
MASTER ↔ BACKUP (VIP 이동)
```

**특징:**
- 간단한 구성
- 빠른 장애조치 (7초 내)
- BACKUP 리소스 낭비
- 단일 서버 처리 능력 제한

**구성 예시:**
```bash
# Keepalived 설정
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    virtual_ipaddress {
        10.200.90.100/24
    }
}
```

### 2. Active-Active (DNS Round Robin)

**여러 HAProxy가 동시에 서비스**

```
Internet → DNS → HAProxy1 (10.200.90.172)
              → HAProxy2 (10.200.90.173)
              → HAProxy3 (10.200.90.174)
```

**특징:**
- 리소스 효율성
- 부하 분산
- 세션 유지 어려움
- DNS 캐시 지연

**DNS 설정:**
```dns
game.example.com.  IN  A  10.200.90.172
game.example.com.  IN  A  10.200.90.173
game.example.com.  IN  A  10.200.90.174
```

### 3. Active-Active (BGP Anycast)

**모든 HAProxy가 동일한 IP 광고**

```
Internet → Router → 가장 가까운 HAProxy
```

**특징:**
- 자동 장애조치
- 최적 경로 선택
- BGP 설정 복잡
- 라우터 지원 필요

**BGP 설정 (FRR):**
```bash
router bgp 65001
 neighbor 10.200.90.1 remote-as 65000
 network 10.200.90.100/32
```

### 4. Active-Active (상위 Load Balancer)

**클라우드 LB 뒤에 HAProxy 배치**

```
Internet → AWS NLB/ALB → HAProxy1
                      → HAProxy2
                      → HAProxy3
```

**특징:**
- Active-Active
- 관리 편의성
- 추가 비용
- 복잡성 증가

**AWS NLB 설정:**
```bash
aws elbv2 create-load-balancer \
  --name haproxy-nlb \
  --type network \
  --subnets subnet-12345
```

### 5. HAProxy Enterprise (클러스터 모드)

**상용 버전의 클러스터 기능**

```
HAProxy Cluster (설정 동기화 + 세션 공유)
```

**특징:**
- 진정한 Active-Active
- 세션 공유
- 라이선스 비용
- 복잡한 설정

## 백엔드 서버 로드밸런싱

HAProxy 내부에서 백엔드 서버들은 이미 Active-Active로 동작합니다.

```haproxy
backend game_servers
    balance roundrobin     # 순차 분배
    # balance leastconn    # 최소 연결
    # balance source       # 소스 IP 해시
    # balance uri          # URI 해시
    
    server game1 10.1.1.1:8080 check weight 100
    server game2 10.1.1.2:8080 check weight 100
    server game3 10.1.1.3:8080 check weight 50
```

## 모드별 비교표

| 모드            | 복잡도 | 비용 | 효율성 | 게임서버 적합도 |
|-----------------|--------|------|--------|-----------------|
| Active-Standby  | ⭐     | ⭐   | ⭐⭐   | ⭐⭐⭐          |
| DNS Round Robin | ⭐⭐   | ⭐   | ⭐⭐⭐ | ⭐⭐            |
| BGP Anycast     |        | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐          |
| 상위 LB         | ⭐⭐   |      | ⭐⭐⭐ | ⭐⭐⭐          |
| Enterprise      |        |      | ⭐⭐⭐ | ⭐⭐⭐          |

## 현재 구성 개선 방안

### 방안 1: DNS Round Robin 추가

```bash
# 현재 VIP 유지하면서 DNS 추가
game.siasiasoft.com.  IN  A  10.200.90.172
game.siasiasoft.com.  IN  A  10.200.90.173
```

### 방안 2: 세 번째 HAProxy 추가

```
3-way Active-Standby 구성
- 더 높은 가용성
- 부하 분산 효과
```

### 방안 3: 백엔드 확장

```haproxy
backend game_servers
    server game1 192.168.111.170:443 check
    server game2 192.168.111.171:443 check
    server game3 192.168.111.172:443 check
```

## 권장 하이브리드 구성

```
Internet → DNS (Round Robin) → HAProxy 클러스터 (Active-Standby)
                                      v
                              게임서버들 (Active-Active)
```

**레이어별 역할:**
- **DNS 레벨**: Round Robin (분산)
- **HAProxy 레벨**: Active-Standby (안정성)
- **백엔드 레벨**: Active-Active (성능)

## 실제 구현 예시

### DNS Round Robin + Active-Standby

```bash
# 1. DNS 설정
game.example.com.  IN  A  10.200.90.172  # MASTER
game.example.com.  IN  A  10.200.90.173  # BACKUP

# 2. 각 HAProxy에서 Keepalived 구성
# MASTER: priority 100
# BACKUP: priority 90

# 3. 클라이언트 접속
# 50% → 10.200.90.172 (MASTER 또는 BACKUP)
# 50% → 10.200.90.173 (BACKUP 또는 MASTER)
```

### AWS 환경에서의 구성

```bash
# NLB 생성
aws elbv2 create-load-balancer \
  --name game-haproxy-nlb \
  --type network \
  --scheme internet-facing

# Target Group에 HAProxy 인스턴스들 등록
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=i-haproxy1 Id=i-haproxy2
```

## 모니터링 및 관리

### 상태 확인 명령어

```bash
# VIP 소유자 확인
ip addr show eth0 | grep "10.200.90.100"

# HAProxy 통계
curl -u admin:haproxy123! http://localhost:8404/stats

# 클러스터 상태
systemctl status keepalived haproxy
```

### 장애조치 테스트

```bash
# MASTER에서 HAProxy 중지
systemctl stop haproxy

# BACKUP으로 VIP 이동 확인 (7초 내)
watch -n 1 'ip addr show eth0 | grep "10.200.90.100"'

# 서비스 복구
systemctl start haproxy
```

## 결론

HAProxy는 Active-Standby뿐만 아니라 다양한 Active-Active 모드를 지원합니다. 게임서버 환경에서는:

1. **안정성 우선**: Active-Standby (현재 구성)
2. **성능 우선**: DNS Round Robin + Active-Standby
3. **클라우드 환경**: NLB/ALB + HAProxy 클러스터

각 환경과 요구사항에 맞는 최적의 구성을 선택하여 구현할 수 있습니다.
