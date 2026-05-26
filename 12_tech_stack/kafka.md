# Apache Kafka

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 설치 & 설정](#4-설치--설정) / [5. 주요 명령어](#5-주요-명령어) / [6. Producer & Consumer](#6-producer--consumer) |
| [7. 파티션 & 복제](#7-파티션--복제) / [8. Consumer Group](#8-consumer-group) / [9. 운영](#9-운영) |
| [10. Tips](#10-tips) |

---

## 1. 개요

Apache Kafka는 분산 이벤트 스트리밍 플랫폼. 대용량 실시간 데이터 파이프라인, 이벤트 드리븐 아키텍처, 로그 집계에 사용됩니다.

```
┌──────────────────────────────────────────────────────────────┐
│                    Kafka Data Flow                           │
│                                                              │
│  Producers ──> Topics (Partitions) ──> Consumers             │
│                      │                                       │
│                  Brokers (Cluster)                           │
│                  ZooKeeper / KRaft                           │
└──────────────────────────────────────────────────────────────┘
```

- **고처리량**: 초당 수백만 건의 메시지를 처리합니다.
- **내구성**: 디스크에 메시지를 저장하여 장애 후 재처리가 가능합니다.
- **확장성**: 파티션 추가로 수평 확장합니다.
- **재생 가능**: 오프셋 기반으로 과거 메시지를 재처리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                       Kafka Cluster                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Broker 1    │  │  Broker 2    │  │  Broker 3    │           │
│  │              │  │              │  │              │           │
│  │  Topic A     │  │  Topic A     │  │  Topic A     │           │
│  │  Partition 0 │  │  Partition 1 │  │  Partition 2 │           │
│  │  (Leader)    │  │  (Leader)    │  │  (Leader)    │           │
│  │  Partition 1 │  │  Partition 2 │  │  Partition 0 │           │
│  │  (Follower)  │  │  (Follower)  │  │  (Follower)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                              │                                  │
│                    ZooKeeper / KRaft                            │
│                    (metadata management)                        │
└─────────────────────────────────────────────────────────────────┘
         ^                                        |
         │ produce                         consume │
┌────────────────┐                    ┌────────────────────────┐
│   Producers    │                    │   Consumer Groups      │
│  - App Server  │                    │  - Group A (Service 1) │
│  - Log Agent   │                    │  - Group B (Service 2) │
└────────────────┘                    └────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념            | 설명                                                          |
|-----------------|---------------------------------------------------------------|
| Topic           | 메시지를 분류하는 논리적 채널 (DB 테이블과 유사)              |
| Partition       | Topic의 물리적 분할 단위. 병렬 처리와 확장성 제공             |
| Offset          | 파티션 내 메시지의 순서 번호 (0부터 시작, 단조 증가)          |
| Broker          | Kafka 서버 인스턴스. 파티션 데이터 저장 및 서빙               |
| Leader          | 파티션의 읽기/쓰기를 담당하는 브로커                          |
| Follower        | Leader 파티션을 복제하는 브로커 (ISR)                         |
| ISR             | In-Sync Replicas. Leader와 동기화된 복제본 집합               |
| Producer        | Topic에 메시지를 발행하는 클라이언트                          |
| Consumer        | Topic에서 메시지를 구독하는 클라이언트                        |
| Consumer Group  | 동일 Topic을 분산 처리하는 Consumer 집합                      |
| Retention       | 메시지 보존 기간/크기 (기본 7일)                              |
| ZooKeeper/KRaft | 클러스터 메타데이터 관리 (KRaft는 ZooKeeper 없이 동작)        |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치 & 설정

### Docker Compose (KRaft 모드, ZooKeeper 불필요)

```yaml
# docker-compose.yml
# version: '3.8'  # Docker Compose v2에서 deprecated (생략 가능)

services:
  kafka:
    image: confluentinc/cp-kafka:8.1.3
    hostname: kafka
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_LOG_DIRS: /var/lib/kafka/data
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    depends_on:
      - kafka
```

### 주요 Broker 설정 (server.properties)

```properties
# 기본 설정
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://192.0.2.1:9092
log.dirs=/var/lib/kafka/data
num.partitions=3
default.replication.factor=3

# 메시지 보존
log.retention.hours=168          # 7일
log.retention.bytes=107374182400 # 100GB
log.segment.bytes=1073741824     # 1GB (세그먼트 크기)

# 성능
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# 복제
min.insync.replicas=2
unclean.leader.election.enable=false   # 데이터 손실 방지
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령어

### Topic 관리

```bash
# Topic 생성
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create \
  --topic my-topic \
  --partitions 3 \
  --replication-factor 3

# Topic 목록
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Topic 상세 정보
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe \
  --topic my-topic

# Topic 설정 변경 (보존 기간 1일로 변경)
kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter \
  --entity-type topics \
  --entity-name my-topic \
  --add-config retention.ms=86400000

# Topic 삭제
kafka-topics.sh --bootstrap-server localhost:9092 \
  --delete \
  --topic my-topic
```

### 메시지 테스트

```bash
# 메시지 발행 (콘솔 Producer)
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic my-topic

# 키-값 형식으로 발행
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic my-topic \
  --property "key.separator=:" \
  --property "parse.key=true"

# 메시지 소비 (처음부터)
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic my-topic \
  --from-beginning

# Consumer Group으로 소비
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic my-topic \
  --group my-consumer-group
```

### Consumer Group 관리

```bash
# Consumer Group 목록
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Consumer Group 상태 (lag 확인)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe \
  --group my-consumer-group

# 오프셋 리셋 (처음부터 재처리)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-consumer-group \
  --topic my-topic \
  --reset-offsets \
  --to-earliest \
  --execute

# 특정 오프셋으로 리셋
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-consumer-group \
  --topic my-topic:0 \
  --reset-offsets \
  --to-offset 1000 \
  --execute
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Producer & Consumer

### Python Producer (confluent-kafka)

```python
from confluent_kafka import Producer
import json

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',                    # 모든 ISR 확인 후 응답
    'retries': 3,
    'retry.backoff.ms': 1000,
    'compression.type': 'snappy',
    'batch.size': 16384,
    'linger.ms': 5,                   # 배치 대기 시간
})

def delivery_report(err, msg):
    if err is not None:
        print(f'Delivery failed: {err}')
    else:
        print(f'Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}')

# 메시지 발행
event = {
    'user_id': 12345,
    'action': 'purchase',
    'amount': 99.99
}

producer.produce(
    topic='user-events',
    key=str(event['user_id']),
    value=json.dumps(event).encode('utf-8'),
    callback=delivery_report
)

producer.flush()   # 버퍼 비우기
```

### Python Consumer (confluent-kafka)

```python
from confluent_kafka import Consumer, KafkaError
import json

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest',   # earliest | latest
    'enable.auto.commit': False,        # 수동 커밋 (정확한 처리 보장)
    'max.poll.interval.ms': 300000,
})

consumer.subscribe(['user-events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            raise Exception(msg.error())

        # 메시지 처리
        event = json.loads(msg.value().decode('utf-8'))
        print(f'Received: {event}')

        # 처리 완료 후 수동 커밋
        consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Producer 설정 비교

| 설정                  | 값          | 특성                              |
|-----------------------|-------------|-----------------------------------|
| `acks=0`              | 0           | 응답 없음. 최고 처리량, 데이터 손실 가능 |
| `acks=1`              | 1           | Leader 확인. 균형                 |
| `acks=all` (`acks=-1`)| all         | 모든 ISR 확인. 최고 내구성        |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 파티션 & 복제

### 파티션 수 결정

```
파티션 수 = max(처리량 목표 / 단일 파티션 처리량, Consumer 수)
```

- 파티션 수는 늘릴 수 있지만 줄일 수 없습니다.
- 파티션 수 > Consumer 수이면 일부 Consumer가 여러 파티션을 처리합니다.
- 파티션 수 < Consumer 수이면 일부 Consumer가 유휴 상태가 됩니다.

### 복제 설정

```
replication.factor=3   # 브로커 3개 이상 필요
min.insync.replicas=2  # 최소 2개 ISR에 쓰기 성공 시 확인
```

```
acks=all + min.insync.replicas=2 + replication.factor=3
→ 브로커 1개 장애 시에도 데이터 손실 없음
```

### 파티션 키 전략

```python
# 키 없음: 라운드 로빈 (순서 보장 없음)
producer.produce(topic='events', value=message)

# 키 있음: 동일 키 → 동일 파티션 (키 단위 순서 보장)
producer.produce(topic='events', key='user-123', value=message)

# 커스텀 파티셔너
from confluent_kafka import Producer

def custom_partitioner(key, all_partitions, available_partitions):
    # 특정 로직으로 파티션 선택
    return hash(key) % len(all_partitions)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. Consumer Group

### 파티션 할당

```
Topic: my-topic (파티션 6개)
Consumer Group: my-group (Consumer 3개)

Consumer 1 → Partition 0, 1
Consumer 2 → Partition 2, 3
Consumer 3 → Partition 4, 5
```

### Lag 모니터링

```bash
# Consumer Lag 확인 (CURRENT-OFFSET vs LOG-END-OFFSET)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe \
  --group my-consumer-group

# 출력 예시
# TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# my-topic    0          1000            1050            50
# my-topic    1          980             1050            70
```

### 오프셋 커밋 전략

| 전략              | 설명                                      | 위험                        |
|-------------------|-------------------------------------------|-----------------------------|
| Auto Commit       | 주기적으로 자동 커밋                      | 처리 전 커밋 시 메시지 손실 |
| Manual Sync       | 처리 완료 후 동기 커밋                    | 처리량 감소                 |
| Manual Async      | 처리 완료 후 비동기 커밋                  | 실패 시 재처리 필요         |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영

### 모니터링 지표

| 지표                              | 설명                          | 임계값 기준          |
|-----------------------------------|-------------------------------|----------------------|
| `kafka.consumer.lag`              | Consumer 처리 지연             | 지속 증가 시 경보    |
| `kafka.broker.BytesInPerSec`      | 초당 수신 바이트               | 용량 계획 기준       |
| `kafka.broker.UnderReplicatedPartitions` | 복제 지연 파티션 수      | 0이어야 정상         |
| `kafka.broker.ActiveControllerCount` | 활성 Controller 수          | 클러스터당 1이어야 함 |
| `kafka.broker.OfflinePartitionsCount` | 오프라인 파티션 수          | 0이어야 정상         |

### Prometheus + JMX Exporter

```yaml
# docker-compose.yml에 추가
kafka:
  environment:
    KAFKA_JMX_PORT: 9999
    KAFKA_JMX_HOSTNAME: kafka

jmx-exporter:
  image: bitnami/jmx-exporter:0.19.0
  ports:
    - "5556:5556"
  volumes:
    - ./jmx-kafka.yml:/opt/bitnami/jmx-exporter/config.yml
  command: ["5556", "/opt/bitnami/jmx-exporter/config.yml"]
```

### 토픽 보존 정책 조정

```bash
# 특정 토픽 보존 기간 변경 (1일)
kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter \
  --entity-type topics \
  --entity-name my-topic \
  --add-config retention.ms=86400000

# 크기 기반 보존 (10GB)
kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter \
  --entity-type topics \
  --entity-name my-topic \
  --add-config retention.bytes=10737418240
```

### 파티션 재분배

```bash
# 파티션 재분배 계획 생성
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --topics-to-move-json-file topics.json \
  --broker-list "1,2,3" \
  --generate

# 재분배 실행
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file reassignment.json \
  --execute

# 진행 상태 확인
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file reassignment.json \
  --verify
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Tips

### 메시지 전달 보장 수준

| 수준                | 설명                                      | 설정                                    |
|---------------------|-------------------------------------------|-----------------------------------------|
| At-most-once        | 최대 1회 전달 (손실 가능)                 | `acks=0`, auto commit                   |
| At-least-once       | 최소 1회 전달 (중복 가능)                 | `acks=all`, 수동 커밋, 재시도           |
| Exactly-once        | 정확히 1회 전달                           | Idempotent Producer + Transactional API |

### Exactly-once Producer

```python
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'enable.idempotence': True,   # 중복 방지
    'acks': 'all',
    'retries': 2147483647,
    'max.in.flight.requests.per.connection': 5,
    'transactional.id': 'my-transactional-producer',
})

producer.init_transactions()
producer.begin_transaction()
try:
    producer.produce('topic-a', key='k1', value='v1')
    producer.produce('topic-b', key='k2', value='v2')
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
    raise
```

### 주의사항

🟡 파티션 수는 생성 후 늘릴 수 있지만 줄일 수 없습니다. 초기 설계 시 충분한 파티션 수를 설정합니다.

🟡 `unclean.leader.election.enable=false`를 설정합니다. `true`이면 ISR에 없는 브로커가 Leader가 되어 데이터 손실이 발생할 수 있습니다.

🟡 Consumer Lag이 지속적으로 증가하면 Consumer 처리 속도가 Producer 발행 속도를 따라가지 못하는 것입니다. Consumer 수를 늘리거나 처리 로직을 최적화합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Apache Kafka Documentation: [kafka.apache.org/documentation](https://kafka.apache.org/documentation/) — ★★★☆☆
- Confluent Developer: [developer.confluent.io](https://developer.confluent.io/) — ★★★☆☆
- Kafka: The Definitive Guide: Narkhede, Shapira, Palino. "Kafka: The Definitive Guide" — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-10

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.
