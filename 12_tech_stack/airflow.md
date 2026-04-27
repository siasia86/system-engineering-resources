# Apache Airflow

## 목차

| 단계  | 섹션                                                                                                          |
|-------|---------------------------------------------------------------------------------------------------------------|
| 기본  | [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념)                               |
| 실전  | [4. DAG 작성](#4-dag-작성) / [5. Operator](#5-operator) / [6. 의존성 관리](#6-의존성-관리)                   |
| 운영  | [7. 스케줄링](#7-스케줄링) / [8. 모니터링](#8-모니터링) / [9. 설치/설정](#9-설치설정) / [10. Tips](#10-tips) |

---

## 1. 개요

Apache Airflow는 **워크플로우를 코드로 정의, 스케줄링, 모니터링**하는 오픈소스 플랫폼.
데이터 파이프라인(ETL), 배치 작업, ML 파이프라인 오케스트레이션에 주로 사용됩니다.

```
┌─────────────────────────────────────────────────────────┐
│                    Airflow 실행 흐름                     │
│                                                         │
│  DAG 파일 (Python) -> Scheduler -> Executor -> Worker   │
│                           │                             │
│                           v                             │
│                    Metadata DB (상태 저장)               │
└─────────────────────────────────────────────────────────┘
```

- DAG(Directed Acyclic Graph): 작업 흐름을 Python 코드로 정의
- Task: DAG 내 개별 작업 단위
- Operator: Task의 실행 방식 정의 (BashOperator, PythonOperator 등)

---

## 2. 아키텍처

```
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│  Web Server  │   │  Scheduler   │   │    Executor      │
│  (UI/API)    │   │  (DAG 파싱,  │   │  (LocalExecutor/ │
│              │   │   스케줄링)  │   │   CeleryExecutor)│
└──────┬───────┘   └──────┬───────┘   └────────┬─────────┘
       │                  │                    │
       └──────────────────┴────────────────────┘
                          │
                 ┌────────┴────────┐
                 │  Metadata DB    │
                 │  (PostgreSQL/   │
                 │   MySQL)        │
                 └─────────────────┘
```

### Executor 유형

| Executor          | 특징                                  | 적합 환경              |
|------------------|---------------------------------------|----------------------|
| SequentialExecutor| 순차 실행, SQLite 사용                | 개발/테스트           |
| LocalExecutor     | 단일 머신 병렬 실행                   | 소규모 운영           |
| CeleryExecutor    | 분산 Worker 풀                        | 대규모 운영           |
| KubernetesExecutor| Task별 Pod 생성                       | 쿠버네티스 환경       |

---

## 3. 핵심 개념

| 개념           | 설명                                                    |
|---------------|--------------------------------------------------------|
| DAG           | 작업 흐름 전체 정의 (Python 파일)                       |
| Task          | DAG 내 개별 실행 단위                                   |
| Operator      | Task 실행 방식 (Bash, Python, HTTP 등)                  |
| TaskInstance  | 특정 DAG Run에서의 Task 실행 인스턴스                   |
| DAG Run       | DAG의 1회 실행 (scheduled/manual/backfill)              |
| XCom          | Task 간 소량 데이터 공유 메커니즘                       |
| Connection    | 외부 시스템 연결 정보 (DB, S3, API 등)                  |
| Variable      | 전역 설정값 저장소                                      |
| Pool          | Task 동시 실행 수 제한                                  |

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

---

## 5. Operator

### 주요 내장 Operator

| Operator                | 용도                              | 패키지                        |
|------------------------|-----------------------------------|-------------------------------|
| `BashOperator`         | 쉘 명령 실행                      | airflow.operators.bash        |
| `PythonOperator`       | Python 함수 실행                  | airflow.operators.python      |
| `EmailOperator`        | 이메일 발송                       | airflow.operators.email       |
| `HttpOperator`         | HTTP 요청                         | airflow.providers.http        |
| `S3ToRedshiftOperator` | S3 → Redshift 로드                | airflow.providers.amazon      |
| `PostgresOperator`     | PostgreSQL 쿼리 실행              | airflow.providers.postgres    |
| `KubernetesPodOperator`| K8s Pod 실행                      | airflow.providers.cncf        |
| `SparkSubmitOperator`  | Spark Job 제출                    | airflow.providers.apache      |

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

| Rule                  | 실행 조건                              |
|----------------------|----------------------------------------|
| `all_success`        | 모든 upstream 성공                     |
| `all_failed`         | 모든 upstream 실패                     |
| `all_done`           | 모든 upstream 완료 (성공/실패 무관)    |
| `one_success`        | upstream 중 하나라도 성공              |
| `one_failed`         | upstream 중 하나라도 실패              |
| `none_failed`        | 실패 없음 (skipped 허용)               |

---

## 7. 스케줄링

### Cron 표현식

```
┌─────── 분 (0-59)
│ ┌───── 시 (0-23)
│ │ ┌─── 일 (1-31)
│ │ │ ┌─ 월 (1-12)
│ │ │ │ ┌ 요일 (0-6, 0=일)
│ │ │ │ │
* * * * *
```

| 표현식          | 의미              |
|----------------|------------------|
| `@hourly`      | 매시 정각         |
| `@daily`       | 매일 자정         |
| `@weekly`      | 매주 일요일 자정  |
| `@monthly`     | 매월 1일 자정     |
| `0 2 * * *`    | 매일 02:00        |
| `0 */6 * * *`  | 6시간마다         |

### execution_date vs data_interval

Airflow 2.2+에서 `execution_date` → `data_interval_start`/`data_interval_end` 로 변경.

```python
# 2.2+ 권장
@task
def process(**context):
    interval_start = context['data_interval_start']
    interval_end = context['data_interval_end']
```

---

## 8. 모니터링

### 웹 UI 주요 뷰

| 뷰           | 용도                                  |
|-------------|---------------------------------------|
| Grid View   | DAG Run × Task 매트릭스, 상태 한눈에  |
| Graph View  | DAG 구조 시각화                       |
| Gantt View  | Task 실행 시간 분석                   |
| Log View    | Task 로그 실시간 확인                 |

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

---

[⬆ 목차로 돌아가기](#목차)
