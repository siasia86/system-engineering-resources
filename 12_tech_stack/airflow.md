# Apache Airflow

## 목차

| 단계   | 섹션                                                                                                                                                              |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기본   | [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념)                                                                                   |
| 실전   | [4. DAG 작성](#4-dag-작성) / [5. Operator](#5-operator) / [6. 의존성 관리](#6-의존성-관리)                                                                       |
| 운영   | [7. 스케줄링](#7-스케줄링) / [8. 모니터링](#8-모니터링) / [9. 설치/설정](#9-설치설정) / [10. Tips](#10-tips)                                                     |
| 고급   | [11. 에러 처리/알림](#11-에러-처리--알림) / [12. XCom 상세](#12-xcom-상세) / [13. 보안](#13-보안) / [14. 성능 튜닝](#14-성능-튜닝)                               |

---

## 1. 개요

Apache Airflow는 **워크플로우를 코드로 정의, 스케줄링, 모니터링**하는 오픈소스 플랫폼.
데이터 파이프라인(ETL), 배치 작업, ML 파이프라인 오케스트레이션에 주로 사용됩니다.

```
┌─────────────────────────────────────────────────────────┐
│                   Airflow Execution Flow                │
│                                                         │
│  DAG File (Python) -> Scheduler -> Executor -> Worker   │
│                           │                             │
│                           v                             │
│                      Metadata DB                        │
└─────────────────────────────────────────────────────────┘
```

- DAG 파일(Python)을 Scheduler가 파싱하여 Executor → Worker로 실행
- Metadata DB에 상태를 저장

- DAG(Directed Acyclic Graph): 작업 흐름을 Python 코드로 정의
- Task: DAG 내 개별 작업 단위
- Operator: Task의 실행 방식 정의 (BashOperator, PythonOperator 등)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│  Web Server  │   │  Scheduler   │   │    Executor      │
│  (UI/API)    │   │  (DAG Parse, │   │  (LocalExecutor/ │
│              │   │   Schedule)  │   │   CeleryExecutor)│
└──────┬───────┘   └──────┬───────┘   └────────┬─────────┘
       │                  │                    │
       └──────────────────┼────────────────────┘
                          │
                 ┌────────┴────────┐
                 │  Metadata DB    │
                 │  (PostgreSQL/   │
                 │   MySQL)        │
                 └─────────────────┘
```

- Scheduler: DAG 파싱 및 스케줄링
- Executor: 실행 방식 결정 (Local, Celery, Kubernetes 등)

### Executor 유형

| Executor             | 특징                          | 적합 환경          |
|----------------------|-------------------------------|--------------------|
| SequentialExecutor   | 순차 실행, SQLite 사용        | 개발/테스트        |
| LocalExecutor        | 단일 머신 병렬 실행           | 소규모 운영        |
| CeleryExecutor       | 분산 Worker 풀                | 대규모 운영        |
| KubernetesExecutor   | Task별 Pod 생성               | 쿠버네티스 환경    |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념         | 설명                                                      |
|--------------|-----------------------------------------------------------|
| DAG          | 작업 흐름 전체 정의 (Python 파일)                         |
| Task         | DAG 내 개별 실행 단위                                     |
| Operator     | Task 실행 방식 (Bash, Python, HTTP 등)                    |
| TaskInstance | 특정 DAG Run에서의 Task 실행 인스턴스                     |
| DAG Run      | DAG의 1회 실행 (scheduled/manual/backfill)                |
| XCom         | Task 간 소량 데이터 공유 메커니즘                         |
| Connection   | 외부 시스템 연결 정보 (DB, S3, API 등)                    |
| Variable     | 전역 설정값 저장소                                        |
| Pool         | Task 동시 실행 수 제한                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 4. DAG 작성

### 기본 구조

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'infra',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['alert@example.com'],
}

with DAG(
    dag_id='example_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',   # 매일 02:00
    start_date=datetime(2026, 1, 1),
    catchup=False,                    # 과거 실행 건너뜀
    tags=['infra', 'backup'],
) as dag:

    def process():
        print("processing...")

    task_a = BashOperator(
        task_id='extract',
        bash_command='echo "extracting data"',
    )

    task_b = PythonOperator(
        task_id='transform',
        python_callable=process,
    )

    task_c = BashOperator(
        task_id='load',
        bash_command='echo "loading data"',
    )

    task_a >> task_b >> task_c   # 의존성 정의
```

### TaskFlow API (Airflow 2.0+, 권장)

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule_interval='@daily', start_date=datetime(2026, 1, 1), catchup=False)
def my_pipeline():

    @task
    def extract() -> dict:
        return {'data': [1, 2, 3]}

    @task
    def transform(raw: dict) -> dict:
        return {'result': [x * 2 for x in raw['data']]}

    @task
    def load(data: dict):
        print(data)

    raw = extract()
    transformed = transform(raw)
    load(transformed)

my_pipeline()
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Operator

### 주요 내장 Operator

| Operator                 | 용도                     | 패키지                     |
|--------------------------|--------------------------|----------------------------|
| `BashOperator`           | 쉘 명령 실행             | airflow.operators.bash     |
| `PythonOperator`         | Python 함수 실행         | airflow.operators.python   |
| `EmailOperator`          | 이메일 발송              | airflow.operators.email    |
| `HttpOperator`           | HTTP 요청                | airflow.providers.http     |
| `S3ToRedshiftOperator`   | S3 → Redshift 로드       | airflow.providers.amazon   |
| `PostgresOperator`       | PostgreSQL 쿼리 실행     | airflow.providers.postgres |
| `KubernetesPodOperator`  | K8s Pod 실행             | airflow.providers.cncf     |
| `SparkSubmitOperator`    | Spark Job 제출           | airflow.providers.apache   |

### Sensor (조건 대기)

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input/ready.flag',
    poke_interval=60,    # 60초마다 확인
    timeout=3600,        # 1시간 후 타임아웃
    mode='reschedule',   # Worker 슬롯 반환 (poke 대신 권장)
)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 의존성 관리

```python
# 순차
t1 >> t2 >> t3

# 병렬
t1 >> [t2, t3] >> t4

# 복잡한 의존성
t1 >> t2
t1 >> t3
[t2, t3] >> t4

# set_upstream / set_downstream
t2.set_upstream(t1)
t3.set_downstream(t4)
```

### TriggerRule (기본값: `all_success`)

| Rule            | 실행 조건                            |
|-----------------|--------------------------------------|
| `all_success`   | 모든 upstream 성공                   |
| `all_failed`    | 모든 upstream 실패                   |
| `all_done`      | 모든 upstream 완료 (성공/실패 무관)  |
| `one_success`   | upstream 중 하나라도 성공            |
| `one_failed`    | upstream 중 하나라도 실패            |
| `none_failed`   | 실패 없음 (skipped 허용)             |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 스케줄링

### Cron 표현식

```
┌─────── min (0-59)
│ ┌───── hour (0-23)
│ │ ┌─── day (1-31)
│ │ │ ┌─ month (1-12)
│ │ │ │ ┌ weekday (0-6, 0=Sun)
│ │ │ │ │
* * * * *
```

- 분(min), 시(hour), 일(day), 월(month), 요일(weekday) 순서

| 표현식         | 의미               |
|----------------|--------------------|
| `@hourly`      | 매시 정각          |
| `@daily`       | 매일 자정          |
| `@weekly`      | 매주 일요일 자정   |
| `@monthly`     | 매월 1일 자정      |
| `0 2 * * *`    | 매일 02:00         |
| `0 */6 * * *`  | 6시간마다          |

### execution_date vs data_interval

Airflow 2.2+에서 `execution_date` → `data_interval_start`/`data_interval_end` 로 변경.

```python
# 2.2+ 권장
@task
def process(**context):
    interval_start = context['data_interval_start']
    interval_end = context['data_interval_end']
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 모니터링

### 웹 UI 주요 뷰

| 뷰          | 용도                                   |
|-------------|----------------------------------------|
| Grid View   | DAG Run × Task 매트릭스, 상태 한눈에  |
| Graph View  | DAG 구조 시각화                        |
| Gantt View  | Task 실행 시간 분석                    |
| Log View    | Task 로그 실시간 확인                  |

### CLI

```bash
# DAG 목록
airflow dags list

# DAG 수동 트리거
airflow dags trigger my_dag

# Task 재실행
airflow tasks run my_dag my_task 2026-04-27

# 특정 날짜 범위 backfill
airflow dags backfill my_dag --start-date 2026-04-01 --end-date 2026-04-27

# DAG 파싱 에러 확인
airflow dags list-import-errors
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 설치/설정

### pip 설치

```bash
pip install "apache-airflow==2.9.0" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.0/constraints-3.11.txt"

# 프로바이더 추가
pip install apache-airflow-providers-amazon
pip install apache-airflow-providers-postgres
```

### 주요 환경변수

```bash
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://user:pass@localhost/airflow
export AIRFLOW__CORE__PARALLELISM=32
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=16
export AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key
```

### airflow.cfg 주요 설정

```ini
[core]
dags_folder = /opt/airflow/dags
parallelism = 32
max_active_tasks_per_dag = 16
max_active_runs_per_dag = 1

[scheduler]
dag_dir_list_interval = 30    # DAG 파일 스캔 주기 (초)
min_file_process_interval = 30

[webserver]
expose_config = False         # 운영 환경에서 False 필수
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Tips

### 설계

- `catchup=False` 기본 설정: 과거 미실행 DAG Run 자동 생성 방지.
- DAG 파일 파싱 시간 최소화: import 최상단에 무거운 라이브러리 로드 금지. DAG 파일은 Scheduler가 주기적으로 파싱함.
- XCom은 소량 데이터만: 대용량 데이터는 S3/DB에 저장하고 경로만 XCom으로 전달.
- `max_active_runs_per_dag = 1`: 동일 DAG 중복 실행 방지.

### 운영

- Pool 활용: 외부 시스템 부하 제어. DB 연결 수 제한 등에 필수.

```python
task = PythonOperator(
    task_id='db_task',
    python_callable=query_db,
    pool='database_pool',      # 최대 동시 실행 수 제한
    pool_slots=1,
)
```

- SLA Miss 알림 설정:

```python
with DAG(
    dag_id='critical_pipeline',
    sla_miss_callback=sla_callback,
    default_args={'sla': timedelta(hours=1)},
) as dag:
    ...
```

### 디버깅

```bash
# DAG 파싱 테스트 (에러 확인)
python /opt/airflow/dags/my_dag.py

# Task 단독 테스트 (DB 기록 없음)
airflow tasks test my_dag my_task 2026-04-27

# 의존성 확인
airflow tasks list my_dag --tree
```

⚠️ `airflow tasks test`는 실제 외부 시스템(DB, S3 등)에 영향을 줍니다. 테스트 환경에서 실행 권장.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 에러 처리 / 알림

### 콜백 함수

DAG 또는 Task 단위로 실패/재시도/성공 시 콜백을 등록합니다.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def on_failure(context):
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    execution_date = context['execution_date']
    log_url = context['task_instance'].log_url
    print(f"FAILED: {dag_id}.{task_id} at {execution_date}")
    print(f"Log: {log_url}")
    # Slack/PagerDuty 호출 가능

def on_retry(context):
    print(f"RETRY: attempt {context['task_instance'].try_number}")

with DAG(
    dag_id='my_pipeline',
    start_date=datetime(2026, 1, 1),
    on_failure_callback=on_failure,   # DAG 레벨 (모든 task에 적용)
) as dag:

    task = PythonOperator(
        task_id='my_task',
        python_callable=lambda: None,
        on_failure_callback=on_failure,   # Task 레벨 (개별 override)
        on_retry_callback=on_retry,
        on_success_callback=None,
    )
```

### Slack 알림 연동

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def slack_alert(context):
    ti = context['task_instance']
    SlackWebhookOperator(
        task_id='slack_alert',
        slack_webhook_conn_id='slack_webhook',
        message=f":red_circle: *{ti.dag_id}.{ti.task_id}* failed
"
                f"Execution: `{context['execution_date']}`
"
                f"<{ti.log_url}|Log>",
    ).execute(context)

# default_args에 등록하면 모든 task에 적용
default_args = {
    'on_failure_callback': slack_alert,
}
```

### SLA Miss 알림

```python
from datetime import timedelta

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    print(f"SLA missed: {task_list}")
    # 알림 발송

with DAG(
    dag_id='critical_pipeline',
    sla_miss_callback=sla_miss_callback,
    default_args={'sla': timedelta(hours=2)},
) as dag:
    ...
```

### 주요 콜백 비교

| 콜백                    | 트리거 시점              | 등록 위치          |
|-------------------------|--------------------------|--------------------|
| `on_failure_callback`   | Task/DAG 실패            | DAG, Task, default_args |
| `on_retry_callback`     | Task 재시도              | Task, default_args |
| `on_success_callback`   | Task 성공                | Task, default_args |
| `on_execute_callback`   | Task 실행 시작           | Task               |
| `sla_miss_callback`     | SLA 초과                 | DAG                |

[⬆ 목차로 돌아가기](#목차)

---

## 12. XCom 상세

Task 간 소량 데이터를 공유하는 메커니즘. Metadata DB에 저장됩니다.

### 기본 사용 (전통 방식)

```python
from airflow.operators.python import PythonOperator

def push_fn(**context):
    context['ti'].xcom_push(key='order_id', value='ORD-001')

def pull_fn(**context):
    order_id = context['ti'].xcom_pull(task_ids='push_task', key='order_id')
    print(order_id)

push_task = PythonOperator(task_id='push_task', python_callable=push_fn)
pull_task = PythonOperator(task_id='pull_task', python_callable=pull_fn)
push_task >> pull_task
```

### TaskFlow API (자동 XCom, 권장)

```python
from airflow.decorators import dag, task

@dag(schedule_interval='@daily', start_date=datetime(2026, 1, 1), catchup=False)
def pipeline():

    @task
    def extract() -> dict:
        return {'ids': [1, 2, 3]}   # 자동으로 XCom push

    @task
    def transform(data: dict) -> list:
        return [x * 2 for x in data['ids']]   # 자동으로 XCom pull/push

    @task
    def load(result: list):
        print(result)

    load(transform(extract()))

pipeline()
```

### 대용량 데이터 처리 패턴

XCom은 기본 48KB(SQLite), PostgreSQL은 1GB 제한이지만 **대용량은 S3 경로만 전달**하는 것이 원칙입니다.

```python
@task
def process_large_data() -> str:
    import boto3, json
    data = [i for i in range(100000)]
    s3 = boto3.client('s3')
    s3.put_object(Bucket='my-bucket', Key='tmp/result.json', Body=json.dumps(data))
    return 's3://my-bucket/tmp/result.json'   # 경로만 XCom으로 전달

@task
def consume(s3_path: str):
    import boto3, json
    s3 = boto3.client('s3')
    bucket, key = s3_path.replace('s3://', '').split('/', 1)
    data = json.loads(s3.get_object(Bucket=bucket, Key=key)['Body'].read())
    print(len(data))
```

### XCom 정리

XCom은 자동 삭제되지 않으므로 주기적 정리가 필요합니다.

```python
# DAG 완료 후 XCom 정리
from airflow.models import XCom
from airflow.utils.session import provide_session

@provide_session
def cleanup_xcom(context, session=None):
    dag_id = context['dag'].dag_id
    run_id = context['run_id']
    session.query(XCom).filter(
        XCom.dag_id == dag_id,
        XCom.run_id == run_id,
    ).delete()
```

```bash
# CLI로 XCom 삭제
airflow tasks clear my_dag --start-date 2026-01-01 --end-date 2026-04-01
```

| 항목              | 제한                                      |
|-------------------|-------------------------------------------|
| SQLite            | 2GB (개발용, 운영 비권장)                 |
| PostgreSQL        | 1GB per value                             |
| MySQL             | 64KB (MEDIUMBLOB 설정 시 16MB)            |
| 권장 최대 크기    | 48KB 이하 (경로/ID/상태값만 전달)         |

[⬆ 목차로 돌아가기](#목차)

---

## 13. 보안

### Fernet 키 (저장 데이터 암호화)

Connections, Variables의 민감 정보를 암호화합니다.

```bash
# Fernet 키 생성
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# airflow.cfg 또는 환경변수로 설정
export AIRFLOW__CORE__FERNET_KEY='your-generated-fernet-key'
```

⚠️ Fernet 키를 변경하면 기존 암호화된 Connections/Variables를 복호화할 수 없습니다. 키는 반드시 백업합니다.

### Secret Backend

Connections/Variables를 외부 시크릿 저장소에서 조회합니다.

```bash
# AWS Secrets Manager
pip install apache-airflow-providers-amazon
```

```ini
# airflow.cfg
[secrets]
backend = airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend
backend_kwargs = {"connections_prefix": "airflow/connections", "variables_prefix": "airflow/variables", "region_name": "ap-northeast-1"}
```

```bash
# AWS Secrets Manager에 Connection 등록
aws secretsmanager create-secret   --name "airflow/connections/my_postgres"   --secret-string "postgresql://user:pass@host:5432/db"
```

```python
# HashiCorp Vault
# airflow.cfg
# backend = airflow.providers.hashicorp.secrets.vault.VaultBackend
# backend_kwargs = {"connections_path": "airflow/connections", "variables_path": "airflow/variables", "url": "http://vault:8200", "token": "..."}
```

### Secret Backend 조회 순서

```
1. Secret Backend (AWS Secrets Manager / Vault)
2. 환경변수 (AIRFLOW_CONN_*, AIRFLOW_VAR_*)
3. Metadata DB (UI에서 등록한 Connections/Variables)
```

### 환경변수로 Connection 등록

```bash
# URI 형식
export AIRFLOW_CONN_MY_POSTGRES='postgresql://user:pass@host:5432/db'

# JSON 형식
export AIRFLOW_CONN_MY_S3='{"conn_type": "aws", "extra": {"region_name": "ap-northeast-1"}}'

# Variable
export AIRFLOW_VAR_API_KEY='SecureKey123'
```

### 웹서버 보안 설정

```python
# webserver_config.py
from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': 'YOUR_CLIENT_ID',
            'client_secret': 'YOUR_CLIENT_SECRET',
            'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
            'request_token_url': None,
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        },
    }
]
```

```ini
# airflow.cfg
[webserver]
expose_config = False          # 운영 환경 필수
expose_hostname = False
hide_sensitive_variable_fields = True
secret_key = your-random-secret-key   # 반드시 변경
```

[⬆ 목차로 돌아가기](#목차)

---

## 14. 성능 튜닝

### 핵심 파라미터

```ini
# airflow.cfg [core]
parallelism = 32                  # 전체 동시 실행 Task 수 (Airflow 전체)
max_active_tasks_per_dag = 16     # DAG당 동시 실행 Task 수
max_active_runs_per_dag = 1       # DAG당 동시 실행 DAG Run 수

# [scheduler]
dag_dir_list_interval = 30        # DAG 파일 스캔 주기 (초) — 줄이면 CPU 증가
min_file_process_interval = 30    # DAG 파일 재파싱 최소 간격
max_dagruns_to_create_per_loop = 10
```

### Executor별 튜닝

| Executor           | 튜닝 포인트                                                    |
|--------------------|----------------------------------------------------------------|
| LocalExecutor      | `parallelism` = CPU 코어 수 × 2                               |
| CeleryExecutor     | Worker 수 × Worker concurrency = 전체 처리량                  |
| KubernetesExecutor | Pod 생성 오버헤드 있음 — 짧은 Task에 비효율                   |

```bash
# CeleryExecutor Worker 설정
airflow celery worker --concurrency 16   # Worker당 동시 Task 수
```

### DAG 파싱 최적화

DAG 파일은 Scheduler가 주기적으로 파싱합니다. 파싱 시간이 길면 스케줄링 지연이 발생합니다.

```python
# 나쁜 예: DAG 파일 최상단에서 무거운 작업
import pandas as pd          # 느린 import
df = pd.read_csv('data.csv') # 파싱 시마다 실행됨

# 좋은 예: Task 내부로 이동
@task
def process():
    import pandas as pd      # Task 실행 시에만 import
    df = pd.read_csv('data.csv')
```

```bash
# DAG 파싱 시간 측정
airflow dags report
```

### Pool 설계

외부 시스템 부하 제어에 사용합니다.

```bash
# Pool 생성
airflow pools set database_pool 5 "DB connection limit"
airflow pools set api_pool 3 "External API rate limit"
```

```python
# Task에 Pool 할당
task = PythonOperator(
    task_id='db_query',
    python_callable=query_db,
    pool='database_pool',
    pool_slots=1,           # 이 Task가 점유하는 슬롯 수
)
```

### 메모리/CPU 모니터링

```bash
# Scheduler 상태 확인
airflow jobs check --job-type SchedulerJob --hostname $(hostname)

# Task 실행 통계
airflow tasks states-for-dag-run my_dag manual__2026-04-27T00:00:00+00:00
```

### 성능 체크리스트

| 항목                          | 권장값/방법                                      |
|-------------------------------|--------------------------------------------------|
| DAG 파싱 시간                 | 1초 미만 (`airflow dags report` 로 확인)         |
| `catchup`                     | `False` (불필요한 과거 Run 방지)                 |
| `max_active_runs_per_dag`     | `1` (중복 실행 방지)                             |
| XCom 크기                     | 48KB 이하 (대용량은 S3 경로 전달)                |
| Sensor `mode`                 | `reschedule` (Worker 슬롯 점유 방지)             |
| Pool                          | 외부 시스템 연동 Task에 반드시 설정              |
| `min_file_process_interval`   | DAG 수가 많으면 60~120초로 증가                  |

[⬆ 목차로 돌아가기](#목차)
