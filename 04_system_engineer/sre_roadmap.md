# Site Reliability Engineer (SRE) 커리어 로드맵

> **내부 공유 자료**  
> 작성일: 2026-01-29  
> 버전: 1.0  
> 대상: SRE 지망생, Junior SRE

## 목차
- [전체 로드맵](#전체-로드맵)
- [Junior SRE (0-2년)](#junior-sre-0-2년)
- [Mid-level SRE (2-5년)](#mid-level-sre-2-5년)
- [Senior SRE (5-8년)](#senior-sre-5-8년)
- [Staff/Principal SRE (8년+)](#staffprincipal-sre-8년)
- [필수 기술 스택](#필수-기술-스택)
- [학습 자료](#학습-자료)

## 전체 로드맵

```
Junior SRE (0-2년)
    ↓
    Linux + 개발 기초 + 모니터링 + 자동화
    
Mid-level SRE (2-5년)
    ↓
    SLA 관리 + 고급 자동화 + 인시던트 대응 + IaC
    
Senior SRE (5-8년)
    ↓
    시스템 설계 + 성능 최적화 + 멘토링 + 아키텍처
    
Staff/Principal SRE (8년+)
    ↓
    기술 전략 + 조직 영향력 + 표준 수립
```

## SRE 핵심 원칙

### Google SRE 원칙

1. **SLI/SLO/SLA 관리**
   - Service Level Indicator (측정)
   - Service Level Objective (목표)
   - Service Level Agreement (약속)

2. **Error Budget (에러 예산)**
   - 100% - SLO = Error Budget
   - 예산 소진 시 배포 중단

3. **Toil 최소화**
   - 반복적 수동 작업 자동화
   - Toil < 50% 유지

4. **포스트모템 문화**
   - Blameless (비난 없는)
   - 근본 원인 분석
   - 재발 방지

## Junior SRE (0-2년)

### 1단계: 기초 다지기 (0-6개월)

#### Linux & 시스템 기초

**필수 명령어**
```bash
# 시스템 모니터링
top, htop, vmstat, iostat, sar
ps aux, pgrep, pkill

# 네트워크
ss, netstat, tcpdump, lsof
curl, wget, dig, nslookup

# 로그 분석
tail -f, grep, awk, sed
journalctl -f -u service

# 프로세스 관리
systemctl status/start/stop/restart
kill, nice, renice
```

**실습 과제:**
1. Linux 서버 설치 및 기본 설정
2. 시스템 리소스 모니터링 스크립트 작성
3. 로그 분석 및 패턴 찾기
4. 네트워크 트러블슈팅

#### 프로그래밍 기초 (Python)

**필수 스킬**
```python
# 1. 기본 문법
def check_disk_usage():
    """디스크 사용률 체크"""
    import shutil
    
    usage = shutil.disk_usage('/')
    percent = (usage.used / usage.total) * 100
    
    if percent > 80:
        send_alert(f"Disk usage: {percent:.1f}%")
    
    return percent

# 2. API 호출
import requests

def health_check(url):
    """서비스 헬스 체크"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

# 3. 파일 처리
def analyze_logs(log_file):
    """로그 분석"""
    errors = []
    with open(log_file) as f:
        for line in f:
            if 'ERROR' in line or '5xx' in line:
                errors.append(line.strip())
    return errors

# 4. 자동화
import schedule
import time

def job():
    print("Running scheduled task...")
    check_disk_usage()
    health_check("https://api.example.com/health")

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

**실습 과제:**
1. 헬스 체크 스크립트 작성
2. 로그 분석 도구 개발
3. 자동화 스크립트 작성
4. API 호출 및 데이터 처리

#### Git & 버전 관리

```bash
# 기본 워크플로우
git clone repo
git checkout -b feature/monitoring
git add .
git commit -m "Add monitoring script"
git push origin feature/monitoring

# 협업
git pull --rebase
git merge main
git rebase -i HEAD~3

# 히스토리 관리
git log --oneline --graph
git blame file.py
git bisect start
```

#### 모니터링 기초

**Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
  
  - job_name: 'app'
    static_configs:
      - targets: ['app1:8080', 'app2:8080']
```

**Grafana 대시보드**
```
- CPU 사용률
- 메모리 사용률
- 디스크 I/O
- 네트워크 트래픽
- 애플리케이션 메트릭
```

**알림 설정**
```yaml
# alertmanager.yml
route:
  receiver: 'team-slack'
  
receivers:
  - name: 'team-slack'
    slack_configs:
      - channel: '#alerts'
        text: '{{ .CommonAnnotations.summary }}'
```

### 2단계: 실무 기초 (6-12개월)

#### Docker 기초

**Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# 실행
CMD ["python", "app.py"]
```

**Docker Compose**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

#### CI/CD 기초

**GitLab CI**
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pytest tests/
    - pylint src/

build:
  stage: build
  script:
    - docker build -t myapp:$CI_COMMIT_SHA .
    - docker push myapp:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/myapp myapp=myapp:$CI_COMMIT_SHA
  only:
    - main
```

**GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build
        run: docker build -t myapp .
      
      - name: Deploy
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/myapp
```

#### 인시던트 대응 기초

**온콜 준비**
```
1. 알림 채널 확인
   - PagerDuty, Opsgenie
   - Slack, Email

2. 런북 숙지
   - 일반적인 장애 대응
   - 에스컬레이션 절차

3. 도구 접근 권한
   - 프로덕션 서버
   - 모니터링 대시보드
   - 로그 시스템
```

**기본 대응 절차**
```
1. 알림 확인
   - 무엇이 문제인가?
   - 영향 범위는?

2. 초기 대응
   - 로그 확인
   - 메트릭 확인
   - 최근 변경사항 확인

3. 완화 조치
   - 롤백
   - 트래픽 차단
   - 스케일 업

4. 복구 확인
   - 메트릭 정상화
   - 에러율 감소

5. 포스트모템
   - 타임라인 작성
   - 근본 원인 분석
   - 액션 아이템
```

### 3단계: 심화 학습 (12-24개월)

#### Kubernetes 기초

**기본 리소스**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**kubectl 명령어**
```bash
# 리소스 확인
kubectl get pods
kubectl get deployments
kubectl get services

# 상세 정보
kubectl describe pod myapp-xxx
kubectl logs -f myapp-xxx
kubectl exec -it myapp-xxx -- bash

# 디버깅
kubectl top pods
kubectl top nodes
kubectl get events --sort-by='.lastTimestamp'

# 배포
kubectl apply -f deployment.yaml
kubectl rollout status deployment/myapp
kubectl rollout undo deployment/myapp
```

#### Terraform (IaC)

**기본 구조**
```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket = "terraform-state"
    key    = "prod/terraform.tfstate"
    region = "ap-northeast-2"
  }
}

provider "aws" {
  region = var.region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main-vpc"
  }
}

# EC2 Auto Scaling
resource "aws_autoscaling_group" "web" {
  name                = "web-asg"
  min_size            = 2
  max_size            = 10
  desired_capacity    = 4
  vpc_zone_identifier = aws_subnet.private[*].id
  
  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "web-server"
    propagate_at_launch = true
  }
}

# RDS
resource "aws_db_instance" "main" {
  identifier        = "main-db"
  engine            = "postgres"
  engine_version    = "14.5"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  
  db_name  = "myapp"
  username = "admin"
  password = var.db_password
  
  multi_az               = true
  backup_retention_period = 7
  
  tags = {
    Name = "main-database"
  }
}
```

**변수 및 출력**
```hcl
# variables.tf
variable "region" {
  description = "AWS region"
  default     = "ap-northeast-2"
}

variable "db_password" {
  description = "Database password"
  sensitive   = true
}

# outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}
```

#### SLI/SLO 설정

**SLI 정의**
```python
# SLI 계산
def calculate_availability_sli():
    """가용성 SLI 계산"""
    total_requests = get_total_requests()
    successful_requests = get_successful_requests()
    
    sli = (successful_requests / total_requests) * 100
    return sli

def calculate_latency_sli():
    """지연 시간 SLI 계산"""
    p95_latency = get_p95_latency()
    return p95_latency

# SLO 체크
def check_slo():
    """SLO 달성 여부 확인"""
    availability_sli = calculate_availability_sli()
    latency_sli = calculate_latency_sli()
    
    availability_slo = 99.9  # 99.9%
    latency_slo = 200  # 200ms
    
    if availability_sli < availability_slo:
        alert("Availability SLO violated")
    
    if latency_sli > latency_slo:
        alert("Latency SLO violated")
```

**Error Budget 관리**
```python
def calculate_error_budget():
    """에러 예산 계산"""
    slo = 99.9  # 99.9%
    error_budget = 100 - slo  # 0.1%
    
    # 월간 허용 다운타임
    minutes_per_month = 30 * 24 * 60  # 43,200분
    allowed_downtime = minutes_per_month * (error_budget / 100)
    
    # 현재 사용량
    actual_downtime = get_actual_downtime()
    remaining_budget = allowed_downtime - actual_downtime
    
    return {
        'allowed': allowed_downtime,
        'used': actual_downtime,
        'remaining': remaining_budget,
        'percentage': (remaining_budget / allowed_downtime) * 100
    }

# 에러 예산 기반 의사결정
budget = calculate_error_budget()
if budget['percentage'] < 10:
    print("에러 예산 부족! 배포 중단")
    freeze_deployments()
else:
    print(f"에러 예산 {budget['percentage']:.1f}% 남음")
```


## Mid-level SRE (2-5년)

### 고급 자동화

#### 복잡한 자동화 시스템

**자동 복구 시스템**
```python
# auto_remediation.py
import boto3
import requests
from dataclasses import dataclass

@dataclass
class IncidentContext:
    service: str
    severity: str
    metrics: dict

class AutoRemediator:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.asg = boto3.client('autoscaling')
    
    def handle_incident(self, context: IncidentContext):
        """인시던트 자동 처리"""
        if context.severity == 'critical':
            self.escalate_immediately(context)
        
        # 자동 복구 시도
        if self.can_auto_fix(context):
            self.auto_fix(context)
        else:
            self.page_oncall(context)
    
    def auto_fix(self, context):
        """자동 복구"""
        if context.service == 'web':
            if context.metrics['cpu'] > 90:
                self.scale_up(context.service)
            elif context.metrics['error_rate'] > 5:
                self.restart_unhealthy_instances()
    
    def scale_up(self, service):
        """오토스케일링"""
        asg_name = f"{service}-asg"
        response = self.asg.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
        
        current = response['AutoScalingGroups'][0]['DesiredCapacity']
        new_capacity = min(current + 2, 10)
        
        self.asg.set_desired_capacity(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=new_capacity
        )
```

**카나리 배포**
```python
# canary_deployment.py
import time

class CanaryDeployer:
    def __init__(self, service_name):
        self.service = service_name
        self.slo_error_rate = 0.1  # 0.1%
    
    def deploy(self, new_version):
        """점진적 카나리 배포"""
        stages = [
            {'percentage': 10, 'duration': 300},   # 10% - 5분
            {'percentage': 25, 'duration': 600},   # 25% - 10분
            {'percentage': 50, 'duration': 900},   # 50% - 15분
            {'percentage': 100, 'duration': 0}     # 100%
        ]
        
        for stage in stages:
            print(f"Routing {stage['percentage']}% to {new_version}")
            self.route_traffic(new_version, stage['percentage'])
            
            if stage['duration'] > 0:
                time.sleep(stage['duration'])
                
                # 메트릭 확인
                metrics = self.get_metrics(new_version)
                
                if not self.is_healthy(metrics):
                    print("Canary failed! Rolling back...")
                    self.rollback(new_version)
                    return False
        
        print("Canary deployment successful!")
        return True
    
    def is_healthy(self, metrics):
        """헬스 체크"""
        if metrics['error_rate'] > self.slo_error_rate:
            return False
        if metrics['latency_p95'] > 500:  # 500ms
            return False
        return True
```

#### 고급 모니터링

**커스텀 메트릭**
```python
# metrics_exporter.py
from prometheus_client import start_http_server, Gauge, Counter
import time

# 메트릭 정의
cpu_usage = Gauge('system_cpu_usage', 'CPU usage percentage')
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
error_count = Counter('http_errors_total', 'Total HTTP errors', ['status_code'])

def collect_metrics():
    """메트릭 수집"""
    while True:
        # CPU 사용률
        cpu = get_cpu_usage()
        cpu_usage.set(cpu)
        
        # 요청 수
        request_count.labels(method='GET', endpoint='/api').inc()
        
        # 에러 수
        if has_error():
            error_count.labels(status_code='500').inc()
        
        time.sleep(10)

if __name__ == '__main__':
    start_http_server(8000)
    collect_metrics()
```

**PromQL 쿼리**
```promql
# CPU 사용률 (5분 평균)
avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100

# 에러율
sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m])) * 100

# P95 레이턴시
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 가용성
(sum(up) / count(up)) * 100
```

#### 성능 최적화

**애플리케이션 프로파일링**
```bash
# Python 프로파일링
python -m cProfile -o profile.stats app.py
python -m pstats profile.stats

# Go 프로파일링
go tool pprof http://localhost:6060/debug/pprof/profile

# 시스템 프로파일링
perf record -g ./myapp
perf report
```

**데이터베이스 최적화**
```sql
-- 슬로우 쿼리 분석
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;

-- 인덱스 추가
CREATE INDEX idx_user_email ON users(email);

-- 쿼리 실행 계획
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
```

**캐싱 전략**
```python
# Redis 캐싱
import redis
import json

cache = redis.Redis(host='localhost', port=6379)

def get_user(user_id):
    """캐시 우선 조회"""
    # 캐시 확인
    cached = cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # DB 조회
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    
    # 캐시 저장 (1시간)
    cache.setex(f"user:{user_id}", 3600, json.dumps(user))
    
    return user
```

### Chaos Engineering

**카오스 실험**
```python
# chaos_experiment.py
import random
import time

class ChaosMonkey:
    def __init__(self):
        self.targets = get_non_critical_instances()
    
    def run_experiment(self):
        """카오스 실험 실행"""
        # 랜덤 인스턴스 선택
        target = random.choice(self.targets)
        
        print(f"Terminating instance: {target}")
        
        # 메트릭 기록 시작
        start_metrics = capture_metrics()
        
        # 인스턴스 종료
        terminate_instance(target)
        
        # 5분간 모니터링
        time.sleep(300)
        
        # 메트릭 비교
        end_metrics = capture_metrics()
        
        # 영향 분석
        impact = analyze_impact(start_metrics, end_metrics)
        
        if impact['availability'] < 99.9:
            print("System not resilient enough!")
        else:
            print("System handled failure gracefully")
```

## Senior SRE (5-8년)

### 시스템 설계

**분산 시스템 설계**
```
요구사항:
- 초당 10만 요청 처리
- 99.99% 가용성
- 글로벌 서비스

아키텍처:
┌─────────────────────────────────────┐
│         Global Load Balancer        │
│         (Route 53 + CloudFront)     │
└─────────────────────────────────────┘
            ↓           ↓
    ┌───────────┐  ┌───────────┐
    │  Region 1 │  │  Region 2 │
    └───────────┘  └───────────┘
         ↓              ↓
    ┌─────────┐    ┌─────────┐
    │   ALB   │    │   ALB   │
    └─────────┘    └─────────┘
         ↓              ↓
    ┌─────────┐    ┌─────────┐
    │ ECS/EKS │    │ ECS/EKS │
    │ (10-50) │    │ (10-50) │
    └─────────┘    └─────────┘
         ↓              ↓
    ┌─────────┐    ┌─────────┐
    │   RDS   │    │   RDS   │
    │ Multi-AZ│    │ Multi-AZ│
    └─────────┘    └─────────┘
```

**용량 계획**
```python
# capacity_planning.py
import pandas as pd
from sklearn.linear_model import LinearRegression

class CapacityPlanner:
    def __init__(self):
        self.model = LinearRegression()
    
    def analyze_trend(self, days=90):
        """트렌드 분석"""
        # 과거 데이터 수집
        data = get_historical_metrics(days)
        df = pd.DataFrame(data)
        
        # 선형 회귀
        X = df[['day']].values
        y = df['cpu_usage'].values
        
        self.model.fit(X, y)
        
        return self.model
    
    def predict_usage(self, months=3):
        """미래 사용량 예측"""
        future_days = months * 30
        prediction = self.model.predict([[future_days]])
        
        return prediction[0]
    
    def recommend_scaling(self):
        """스케일링 권장사항"""
        prediction = self.predict_usage(3)
        
        if prediction > 80:
            return {
                'action': 'scale_up',
                'reason': f'Predicted usage: {prediction:.1f}%',
                'recommendation': 'Add 2 more instances'
            }
        
        return {'action': 'no_change'}
```

### 고급 인시던트 관리

**포스트모템 템플릿**
```markdown
# 포스트모템: [서비스명] 장애

## 요약
- 발생 시간: 2026-01-29 14:30 KST
- 종료 시간: 2026-01-29 15:45 KST
- 지속 시간: 1시간 15분
- 영향: 전체 사용자의 30%
- 근본 원인: DB 연결 풀 고갈

## 타임라인
- 14:30 - 알림 발생 (높은 에러율)
- 14:35 - 온콜 엔지니어 확인 시작
- 14:40 - DB 연결 문제 확인
- 14:50 - 연결 풀 크기 증가 (50 → 200)
- 15:00 - 부분 복구
- 15:45 - 완전 복구

## 근본 원인
트래픽 급증으로 DB 연결 풀 고갈
- 평소 트래픽: 1000 req/s
- 장애 시: 5000 req/s
- 연결 풀: 50 (부족)

## 해결 방법
1. 즉시: 연결 풀 크기 증가
2. 단기: Auto Scaling 설정
3. 장기: 연결 풀 동적 조정

## 액션 아이템
- [ ] 연결 풀 모니터링 추가 (@john, 2026-02-05)
- [ ] Auto Scaling 정책 수정 (@jane, 2026-02-10)
- [ ] 부하 테스트 실시 (@team, 2026-02-15)
- [ ] 런북 업데이트 (@alice, 2026-02-01)

## 교훈
- 연결 풀 크기를 트래픽에 맞게 설정
- 부하 테스트 정기 실시
- 모니터링 강화
```

**인시던트 자동화**
```python
# incident_manager.py
from enum import Enum

class Severity(Enum):
    P0 = "critical"      # 전체 서비스 다운
    P1 = "high"          # 주요 기능 장애
    P2 = "medium"        # 부분 장애
    P3 = "low"           # 경미한 문제

class IncidentManager:
    def __init__(self):
        self.pagerduty = PagerDutyClient()
        self.slack = SlackClient()
    
    def create_incident(self, title, severity, details):
        """인시던트 생성"""
        incident = {
            'title': title,
            'severity': severity,
            'created_at': datetime.now(),
            'status': 'investigating'
        }
        
        # PagerDuty 알림
        if severity in [Severity.P0, Severity.P1]:
            self.pagerduty.trigger_incident(incident)
        
        # Slack 알림
        self.slack.post_message(
            channel='#incidents',
            text=f"{severity.value.upper()}: {title}"
        )
        
        # 자동 대응 시도
        if severity == Severity.P0:
            self.auto_respond(incident)
        
        return incident
    
    def auto_respond(self, incident):
        """자동 대응"""
        # 1. 로그 수집
        logs = collect_logs(minutes=10)
        
        # 2. 메트릭 수집
        metrics = collect_metrics(minutes=10)
        
        # 3. 최근 배포 확인
        recent_deploys = get_recent_deployments(hours=2)
        
        # 4. 자동 롤백 시도
        if recent_deploys:
            self.rollback(recent_deploys[0])
```

### 고급 Kubernetes

**커스텀 오퍼레이터**
```python
# custom_operator.py
import kopf
import kubernetes

@kopf.on.create('apps', 'v1', 'deployments')
def deployment_created(spec, name, namespace, **kwargs):
    """Deployment 생성 시 자동 설정"""
    # HPA 자동 생성
    create_hpa(name, namespace)
    
    # PDB 자동 생성
    create_pdb(name, namespace)
    
    # ServiceMonitor 생성 (Prometheus)
    create_service_monitor(name, namespace)

@kopf.on.update('apps', 'v1', 'deployments')
def deployment_updated(spec, name, namespace, **kwargs):
    """Deployment 업데이트 시 검증"""
    # 리소스 제한 확인
    if not has_resource_limits(spec):
        raise kopf.PermanentError("Resource limits required")
    
    # 헬스 체크 확인
    if not has_health_checks(spec):
        raise kopf.PermanentError("Health checks required")
```

**고급 배포 전략**
```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 25
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 15m}
      - setWeight: 100
      
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 1
        
      trafficRouting:
        istio:
          virtualService:
            name: myapp-vsvc
```

### 멀티 클라우드 & 하이브리드

**Terraform 멀티 클라우드**
```hcl
# AWS
provider "aws" {
  region = "ap-northeast-2"
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"
}

# GCP
provider "google" {
  project = "my-project"
  region  = "asia-northeast3"
}

resource "google_compute_instance" "web" {
  name         = "web-server"
  machine_type = "e2-medium"
}

# Azure
provider "azurerm" {
  features {}
}

resource "azurerm_virtual_machine" "web" {
  name     = "web-vm"
  vm_size  = "Standard_B2s"
}
```

### 보안 & 컴플라이언스

**시크릿 관리**
```python
# secrets_manager.py
import boto3
from cryptography.fernet import Fernet

class SecretsManager:
    def __init__(self):
        self.ssm = boto3.client('ssm')
        self.secrets = boto3.client('secretsmanager')
    
    def get_secret(self, name):
        """시크릿 조회"""
        try:
            response = self.secrets.get_secret_value(SecretId=name)
            return response['SecretString']
        except Exception as e:
            print(f"Failed to get secret: {e}")
            return None
    
    def rotate_secret(self, name):
        """시크릿 로테이션"""
        # 새 시크릿 생성
        new_secret = generate_secure_password()
        
        # 업데이트
        self.secrets.update_secret(
            SecretId=name,
            SecretString=new_secret
        )
        
        # 애플리케이션 재시작
        restart_applications_using_secret(name)
```

**보안 스캔 자동화**
```bash
#!/bin/bash
# security_scan.sh

# 컨테이너 이미지 스캔
trivy image myapp:latest

# 인프라 스캔
checkov -d terraform/

# 의존성 스캔
safety check -r requirements.txt

# 시크릿 스캔
gitleaks detect --source .
```

## Staff/Principal SRE (8년+)

### 기술 전략

**SRE 플랫폼 구축**
```
목표: 모든 팀이 사용할 수 있는 SRE 플랫폼

구성 요소:
1. 자동화 프레임워크
   - 배포 자동화
   - 인시던트 자동 대응
   - 용량 자동 조정

2. 관찰성 플랫폼
   - 통합 모니터링
   - 분산 추적
   - 로그 집계

3. 신뢰성 도구
   - SLO 대시보드
   - Error Budget 추적
   - Chaos Engineering

4. 개발자 도구
   - Self-service 배포
   - 환경 프로비저닝
   - 디버깅 도구
```

**표준 및 베스트 프랙티스**
```markdown
# SRE 표준

## 배포 표준
- 모든 배포는 카나리 배포
- 자동 롤백 설정 필수
- 배포 전 부하 테스트

## 모니터링 표준
- 모든 서비스는 SLO 정의
- Golden Signals 모니터링 (Latency, Traffic, Errors, Saturation)
- 알림은 actionable해야 함

## 인시던트 표준
- P0/P1은 30분 내 대응
- 모든 인시던트는 포스트모템
- 액션 아이템 추적
```

### 고급 Go 프로그래밍

**고성능 모니터링 에이전트**
```go
// agent.go
package main

import (
    "context"
    "time"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

type MetricsCollector struct {
    cpuGauge    prometheus.Gauge
    memGauge    prometheus.Gauge
    diskGauge   prometheus.Gauge
}

func NewMetricsCollector() *MetricsCollector {
    return &MetricsCollector{
        cpuGauge: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "system_cpu_usage",
            Help: "Current CPU usage percentage",
        }),
        memGauge: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "system_memory_usage",
            Help: "Current memory usage percentage",
        }),
    }
}

func (m *MetricsCollector) Collect(ctx context.Context) {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()
    
    for {
        select {
        case <-ticker.C:
            cpu := getCPUUsage()
            mem := getMemoryUsage()
            
            m.cpuGauge.Set(cpu)
            m.memGauge.Set(mem)
            
            if cpu > 80 {
                sendAlert("High CPU usage", cpu)
            }
        case <-ctx.Done():
            return
        }
    }
}

func main() {
    collector := NewMetricsCollector()
    
    prometheus.MustRegister(collector.cpuGauge)
    prometheus.MustRegister(collector.memGauge)
    
    ctx := context.Background()
    go collector.Collect(ctx)
    
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9090", nil)
}
```

### 멘토링 & 리더십

**주니어 멘토링 계획**
```
1개월차:
- 온보딩
- 도구 및 시스템 소개
- 첫 온콜 준비

3개월차:
- 자동화 프로젝트 할당
- 코드 리뷰
- 인시던트 대응 참여

6개월차:
- 독립적 프로젝트
- 온콜 로테이션 참여
- 포스트모템 작성

12개월차:
- 복잡한 프로젝트 리드
- 멘토링 시작
- 기술 발표
```

**기술 리뷰**
```
주간 리뷰:
- 아키텍처 리뷰
- 코드 리뷰
- 인시던트 리뷰

월간 리뷰:
- SLO 달성률
- Error Budget 사용량
- Toil 분석
- 개선 과제
```


## 필수 기술 스택

### 프로그래밍 언어

**Python (필수)**
```
우선순위: ★★★★★
용도: 자동화, 스크립팅, 데이터 분석

학습 순서:
1. 기본 문법 (2주)
2. 파일/네트워크 처리 (1주)
3. API 호출 (1주)
4. 자동화 스크립트 (2주)
```

**Go (권장)**
```
우선순위: ★★★★☆
용도: 고성능 도구, 에이전트, CLI

학습 순서:
1. 기본 문법 (2주)
2. 동시성 (goroutine, channel) (2주)
3. 네트워크 프로그래밍 (1주)
4. CLI 도구 개발 (2주)
```

**Bash (필수)**
```
우선순위: ★★★★★
용도: 시스템 관리, 자동화

핵심 스킬:
- 변수, 조건문, 반복문
- 파이프, 리다이렉션
- 텍스트 처리 (grep, awk, sed)
- 프로세스 관리
```

### 인프라 & 클라우드

**AWS (필수)**
```
핵심 서비스:
- EC2, Auto Scaling
- ELB (ALB, NLB)
- RDS, DynamoDB
- S3, CloudFront
- CloudWatch, X-Ray
- IAM, VPC
- ECS, EKS

자격증:
- AWS Solutions Architect Associate
- AWS SysOps Administrator
```

**Kubernetes (필수)**
```
핵심 개념:
- Pod, Deployment, Service
- ConfigMap, Secret
- Ingress, NetworkPolicy
- HPA, VPA
- StatefulSet, DaemonSet
- Helm, Kustomize

자격증:
- CKA (Certified Kubernetes Administrator)
- CKAD (Certified Kubernetes Application Developer)
```

**Terraform (필수)**
```
핵심 스킬:
- 리소스 정의
- 모듈 작성
- State 관리
- 워크스페이스
- 변수 및 출력

자격증:
- HashiCorp Certified: Terraform Associate
```

### 모니터링 & 관찰성

**Prometheus + Grafana (필수)**
```
Prometheus:
- 메트릭 수집
- PromQL 쿼리
- 알림 규칙
- Service Discovery

Grafana:
- 대시보드 작성
- 알림 설정
- 데이터 소스 통합
```

**ELK Stack (권장)**
```
Elasticsearch:
- 로그 저장 및 검색
- 인덱스 관리

Logstash:
- 로그 파싱
- 필터링

Kibana:
- 로그 시각화
- 대시보드
```

**분산 추적 (권장)**
```
Jaeger / Zipkin:
- 트레이스 수집
- 성능 분석
- 병목 지점 파악
```

### CI/CD

**GitLab CI / GitHub Actions (필수)**
```
핵심 스킬:
- 파이프라인 작성
- 자동 테스트
- 자동 배포
- 시크릿 관리
```

**ArgoCD (권장)**
```
GitOps:
- 선언적 배포
- 자동 동기화
- 롤백
```

### 데이터베이스

**PostgreSQL / MySQL (필수)**
```
핵심 스킬:
- 쿼리 최적화
- 인덱스 설계
- 복제 설정
- 백업/복구
- 슬로우 쿼리 분석
```

**Redis (권장)**
```
용도:
- 캐싱
- 세션 저장
- 메시지 큐
```

### 네트워킹

**필수 지식**
```
- TCP/IP, HTTP/HTTPS
- DNS, CDN
- Load Balancing
- SSL/TLS
- VPN, VPC
```

**도구**
```
- tcpdump, wireshark
- curl, wget
- dig, nslookup
- netstat, ss
```

## 학습 자료

### 책

**SRE 기초**
- "Site Reliability Engineering" (Google)
- "The Site Reliability Workbook" (Google)
- "Seeking SRE" (O'Reilly)

**시스템 & 네트워크**
- "UNIX and Linux System Administration Handbook"
- "TCP/IP Illustrated"
- "Computer Networking: A Top-Down Approach"

**클라우드 & 인프라**
- "Kubernetes in Action"
- "Terraform: Up & Running"
- "AWS Certified Solutions Architect Study Guide"

**프로그래밍**
- "Fluent Python"
- "The Go Programming Language"
- "Learning the bash Shell"

### 온라인 강의

**Coursera**
- Google Cloud Platform Fundamentals
- Site Reliability Engineering: Measuring and Managing Reliability

**Udemy**
- AWS Certified Solutions Architect
- Kubernetes for Absolute Beginners
- Terraform for Beginners

**A Cloud Guru**
- AWS Certified SysOps Administrator
- Kubernetes Deep Dive

### 실습 플랫폼

**Hands-on Labs**
- AWS Free Tier
- Google Cloud Free Tier
- Katacoda (Kubernetes)
- Play with Docker
- Terraform Cloud

**CTF & Challenges**
- OverTheWire (Linux)
- HackerRank (Python)
- LeetCode (알고리즘)

### 커뮤니티

**온라인 커뮤니티**
- SRE Weekly Newsletter
- r/sre (Reddit)
- SRE Slack Communities
- DevOps Korea

**컨퍼런스**
- SREcon
- KubeCon
- AWS re:Invent
- DevOps Days

## 실전 프로젝트

### Junior 레벨

**프로젝트 1: 모니터링 시스템**
```
목표: Prometheus + Grafana 구축

단계:
1. Prometheus 설치 및 설정
2. Node Exporter 설치
3. 메트릭 수집 설정
4. Grafana 대시보드 작성
5. 알림 규칙 설정

기간: 1주
```

**프로젝트 2: 자동화 스크립트**
```
목표: 시스템 헬스 체크 자동화

기능:
- CPU, 메모리, 디스크 체크
- 서비스 상태 확인
- 로그 분석
- Slack 알림

기술: Python, Bash
기간: 1주
```

**프로젝트 3: CI/CD 파이프라인**
```
목표: 간단한 웹 앱 배포 자동화

단계:
1. GitHub Actions 설정
2. 자동 테스트
3. Docker 이미지 빌드
4. AWS ECS 배포

기간: 2주
```

### Mid-level 레벨

**프로젝트 1: Kubernetes 클러스터**
```
목표: 프로덕션급 K8s 클러스터 구축

구성:
- EKS 클러스터
- Ingress Controller
- Cert Manager (SSL)
- Prometheus + Grafana
- EFK Stack
- ArgoCD

기간: 3주
```

**프로젝트 2: IaC로 인프라 구축**
```
목표: Terraform으로 전체 인프라 관리

리소스:
- VPC, Subnet
- EC2, Auto Scaling
- RDS, ElastiCache
- ALB, CloudFront
- S3, IAM

기간: 3주
```

**프로젝트 3: 자동 복구 시스템**
```
목표: 장애 자동 감지 및 복구

기능:
- 헬스 체크
- 자동 재시작
- 자동 스케일링
- 알림 및 로깅

기술: Python, AWS Lambda, CloudWatch
기간: 2주
```

### Senior 레벨

**프로젝트 1: SRE 플랫폼**
```
목표: 통합 SRE 플랫폼 구축

기능:
- Self-service 배포
- SLO 대시보드
- Error Budget 추적
- 인시던트 관리
- Chaos Engineering

기간: 2개월
```

**프로젝트 2: 멀티 리전 아키텍처**
```
목표: 글로벌 고가용성 시스템

구성:
- 멀티 리전 배포
- Global Load Balancing
- 데이터 복제
- Disaster Recovery

기간: 2개월
```

**프로젝트 3: 성능 최적화**
```
목표: 시스템 성능 10배 향상

작업:
- 프로파일링
- 병목 지점 파악
- 캐싱 전략
- DB 최적화
- 아키텍처 개선

기간: 1개월
```

## 커리어 팁

### 이력서 작성

**강조할 내용**
```
1. 정량적 성과
   "시스템 안정성 개선"
   "가용성 99.9% → 99.99% 향상 (다운타임 90% 감소)"

2. 기술 스택
   - 사용한 도구 및 기술
   - 프로젝트 규모
   - 담당 역할

3. 문제 해결
   - 어떤 문제를 해결했는가
   - 어떻게 해결했는가
   - 결과는 무엇인가

4. 자동화
   - 자동화한 작업
   - 절감한 시간
   - 개선 효과
```

**예시**
```
Site Reliability Engineer | ABC Company | 2023-2025

• Kubernetes 기반 마이크로서비스 인프라 구축 및 운영 (50+ 서비스)
  - EKS 클러스터 설계 및 구축
  - ArgoCD를 통한 GitOps 배포 자동화
  - 배포 시간 60분 → 5분 단축 (92% 개선)

• SLO 기반 신뢰성 관리 체계 수립
  - 핵심 서비스 SLO 정의 (가용성 99.9%, 레이턴시 P95 < 200ms)
  - Error Budget 추적 시스템 구축
  - 가용성 99.5% → 99.95% 향상

• 인시던트 대응 시간 70% 단축
  - 자동 복구 시스템 개발 (Python, AWS Lambda)
  - 런북 자동화 (Ansible)
  - MTTR 30분 → 9분 단축

• 모니터링 및 관찰성 플랫폼 구축
  - Prometheus + Grafana 기반 메트릭 수집
  - EFK Stack 로그 집계 (일 10TB)
  - Jaeger 분산 추적 시스템

기술 스택: Kubernetes, AWS, Terraform, Python, Go, Prometheus, Grafana
```

### 면접 준비

**기술 면접 주제**
```
1. Linux & 시스템
   - 프로세스 관리
   - 메모리 관리
   - 파일 시스템
   - 네트워킹

2. 클라우드 & 인프라
   - AWS 서비스
   - Kubernetes
   - IaC (Terraform)

3. 모니터링
   - 메트릭 수집
   - 로그 분석
   - 알림 설정

4. 프로그래밍
   - Python/Go 코딩
   - 알고리즘
   - 시스템 설계

5. SRE 원칙
   - SLI/SLO/SLA
   - Error Budget
   - Toil
   - 포스트모템
```

**예상 질문**
```
1. "99.9% 가용성을 달성하기 위한 전략은?"
   → Multi-AZ, Auto Scaling, Health Check, 모니터링

2. "대규모 장애 발생 시 대응 절차는?"
   → 영향 파악 → 완화 조치 → 근본 원인 분석 → 포스트모템

3. "Kubernetes에서 Pod가 재시작되는 이유는?"
   → OOMKilled, CrashLoopBackOff, Liveness Probe 실패

4. "데이터베이스 성능 최적화 방법은?"
   → 인덱스, 쿼리 최적화, 캐싱, 복제, 샤딩

5. "CI/CD 파이프라인 설계 시 고려사항은?"
   → 자동 테스트, 단계별 배포, 롤백, 모니터링
```

**시스템 설계 문제**
```
"초당 10만 요청을 처리하는 URL 단축 서비스를 설계하시오"

고려사항:
- 확장성 (Scale)
- 가용성 (Availability)
- 성능 (Performance)
- 비용 (Cost)

답변 구조:
1. 요구사항 명확화
2. 용량 계산
3. 아키텍처 설계
4. 데이터베이스 설계
5. API 설계
6. 확장 전략
7. 모니터링
```

### 연봉 협상

**한국 SRE 연봉 (2026 기준)**
```
Junior (0-2년):
- 대기업: 4,000만원 - 5,500만원
- 스타트업: 3,500만원 - 5,000만원
- 외국계: 5,000만원 - 7,000만원

Mid-level (2-5년):
- 대기업: 5,500만원 - 8,000만원
- 스타트업: 5,000만원 - 7,500만원
- 외국계: 7,000만원 - 10,000만원

Senior (5-8년):
- 대기업: 8,000만원 - 12,000만원
- 스타트업: 7,500만원 - 11,000만원
- 외국계: 10,000만원 - 15,000만원

Staff/Principal (8년+):
- 대기업: 12,000만원 - 18,000만원
- 스타트업: 11,000만원 - 16,000만원
- 외국계: 15,000만원 - 25,000만원+
```

**협상 팁**
```
1. 시장 조사
   - 동일 직급 연봉 범위 파악
   - 회사 규모별 차이 이해

2. 본인 가치 입증
   - 정량적 성과
   - 기술 스택
   - 프로젝트 경험

3. 전체 패키지 고려
   - 기본급
   - 스톡옵션
   - 보너스
   - 복지

4. 협상 전략
   - 희망 연봉보다 10-20% 높게 제시
   - 유연성 유지
   - 대안 제시 (스톡옵션, 승진 일정)
```

## SRE vs DevOps vs SE

### 역할 비교

| 항목 | SRE | DevOps | SE |
|------|-----|--------|-----|
| **주요 목표** | 신뢰성, 가용성 | 배포 속도, 협업 | 인프라 안정성 |
| **코딩 비중** | 60-70% | 40-50% | 20-30% |
| **운영 비중** | 30-40% | 50-60% | 70-80% |
| **핵심 메트릭** | SLO, Error Budget | 배포 빈도, MTTR | 가동률, 성능 |
| **자동화** | 매우 높음 | 높음 | 중간 |
| **온콜** | 있음 | 있음 (팀에 따라) | 있음 |

### 커리어 전환

**SE → SRE**
```
강화할 스킬:
- 프로그래밍 (Python, Go)
- 자동화
- 클라우드 네이티브 (K8s)
- SLO/SLA 관리

기간: 6-12개월
```

**DevOps → SRE**
```
강화할 스킬:
- 신뢰성 엔지니어링
- 성능 최적화
- 인시던트 관리
- 용량 계획

기간: 3-6개월
```

**개발자 → SRE**
```
강화할 스킬:
- 인프라 (AWS, K8s)
- 시스템 관리 (Linux)
- 모니터링
- 네트워킹

기간: 6-12개월
```

## 마무리

### SRE 성공을 위한 핵심

**1. 기술적 깊이**
- 단순히 도구 사용이 아닌 원리 이해
- 문제의 근본 원인 파악 능력
- 시스템 전체를 보는 시야

**2. 자동화 마인드**
- 반복 작업은 자동화
- Toil 최소화
- 효율성 추구

**3. 데이터 기반 의사결정**
- 메트릭 기반 판단
- SLO/Error Budget 활용
- 정량적 분석

**4. 협업 능력**
- 개발팀과 협업
- 명확한 커뮤니케이션
- 포스트모템 문화

**5. 지속적 학습**
- 새로운 기술 습득
- 커뮤니티 참여
- 지식 공유

### 다음 단계

**지금 바로 시작하기**
```
1. Linux 서버 설치 (VM 또는 클라우드)
2. Python 기초 학습 시작
3. AWS Free Tier 계정 생성
4. 첫 자동화 스크립트 작성
5. GitHub에 코드 업로드
```

**3개월 목표**
```
- Linux 명령어 숙달
- Python 기본 프로그래밍
- AWS 기초 서비스 사용
- 간단한 모니터링 시스템 구축
```

**6개월 목표**
```
- Docker/Kubernetes 기초
- Terraform으로 인프라 관리
- CI/CD 파이프라인 구축
- 포트폴리오 프로젝트 3개
```

**1년 목표**
```
- Junior SRE 취업
- 온콜 로테이션 참여
- 자동화 프로젝트 완료
- 커뮤니티 활동 시작
```

---

**작성자 노트:**
이 로드맵은 실제 SRE 현업 경험을 바탕으로 작성되었습니다. 각자의 상황에 맞게 조정하여 사용하시기 바랍니다.

**참고 자료:**
- Google SRE Book: https://sre.google/books/
- SRE Weekly: https://sreweekly.com/
- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/

**업데이트:**
- 2026-01-29: 초안 작성
- 정기 업데이트 예정 (분기별)

**피드백:**
이 문서에 대한 피드백이나 제안사항이 있으시면 언제든지 공유해주세요.


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
