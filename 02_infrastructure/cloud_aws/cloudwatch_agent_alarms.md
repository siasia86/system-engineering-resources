# CloudWatch Agent와 경보 운영 가이드

Amazon CloudWatch는 AWS 리소스와 애플리케이션의 지표·로그를 모으고 경보를 보내는 관측 서비스입니다. EC2 기본 지표에는 메모리·디스크 사용률이 없으므로, 운영에서는 CloudWatch Agent로 OS 내부 지표와 로그를 보내고 경보(Alarm)로 이상을 알립니다. 이 문서는 기본 지표와 Agent의 경계, Agent 설치·설정, 경보 평가 방식, 누락 데이터 처리, 경보 설계 기준을 정리합니다.

> 기준: AWS CloudWatch User Guide와 EC2 User Guide (확인일 2026-11-16). 요금은 [CloudWatch 요금 페이지](https://aws.amazon.com/cloudwatch/pricing/)에서 확인합니다.

## 목차

| 목차                                                                                                  |
|-------------------------------------------------------------------------------------------------------|
| [1. 기본 지표와 Agent 지표](#1-기본-지표와-agent-지표) / [2. Agent 설치와 권한](#2-agent-설치와-권한) |
| [3. Agent 설정 파일](#3-agent-설정-파일) / [4. 경보 평가 방식](#4-경보-평가-방식)                     |
| [5. 누락 데이터 처리](#5-누락-데이터-처리) / [6. 경보 만들기](#6-경보-만들기)                         |
| [7. 경보 설계 기준](#7-경보-설계-기준) / [8. 트러블슈팅](#8-트러블슈팅)                               |
| [9. 운영 점검표](#9-운영-점검표)                                                                      |

---

## 1. 기본 지표와 Agent 지표

```text
+------------------- EC2 instance --------------------+
|  hypervisor view          guest OS view             |
|  CPUUtilization           mem_used_percent          |
|  NetworkIn/Out            disk_used_percent         |
|  StatusCheckFailed        swap_used_percent, logs   |
|        |                        |                   |
|        | (no agent needed)      | CloudWatch Agent  |
+--------|------------------------|-------------------+
         v                        v
   namespace AWS/EC2        namespace CWAgent (default)
         \                        /
          +---> CloudWatch Metrics / Logs ---> Alarms ---> SNS / Auto Scaling / EC2 action
```

| 구분      | EC2 기본 지표 (`AWS/EC2`)                            | CloudWatch Agent 지표 (`CWAgent`)                            |
|-----------|------------------------------------------------------|--------------------------------------------------------------|
| 수집 위치 | 하이퍼바이저에서 관찰                                | 게스트 OS 안에서 수집                                        |
| 대표 지표 | `CPUUtilization`, `NetworkIn`, `StatusCheckFailed`   | `mem_used_percent`, `disk_used_percent`, `swap_used_percent` |
| 설치      | 필요 없음                                            | Agent 설치와 IAM 권한 필요                                   |
| 주기      | 기본(basic) 5분, 상태 검사는 1분. 세부(detailed) 1분 | `metrics_collection_interval`로 지정 (기본 60초)             |
| 요금      | 기본 모니터링 무료, 세부 모니터링 유료               | 사용자 지정 지표(custom metric)로 과금                       |

메모리와 디스크 사용률은 하이퍼바이저가 볼 수 없는 게스트 OS 내부 정보라서 Agent가 필요합니다. 세부 모니터링은 `aws ec2 monitor-instances --instance-ids <INSTANCE_ID>`로 켭니다.

Agent 지표는 지표 이름 × 차원(dimension) 조합마다 별도 사용자 지정 지표로 과금됩니다. 차원을 많이 붙이거나 모든 마운트·모든 CPU 코어를 수집하면 비용이 빠르게 늘어납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Agent 설치와 권한

### IAM 역할

EC2 인스턴스에 IAM 역할(인스턴스 프로파일)을 연결하고 AWS 관리형 정책 `CloudWatchAgentServerPolicy`를 붙입니다. Systems Manager로 Agent를 배포·설정하려면 `AmazonSSMManagedInstanceCore`도 함께 붙입니다. Agent가 로그 그룹 보존 기간을 설정하게 하려면 `logs:PutRetentionPolicy` 권한이 추가로 필요합니다.

정적 액세스 키를 서버에 두는 방식은 키 유출과 교체 부담이 있으므로, EC2에서는 인스턴스 역할을 씁니다. 온프레미스 서버는 별도 자격증명 구성이 필요합니다([sts_assume_role.md](sts_assume_role.md) 참고).

### 설치

Amazon Linux 2023과 Amazon Linux 2는 패키지 저장소에서 설치할 수 있고, 다른 배포판은 AWS가 제공하는 RPM·DEB 패키지를 내려받아 설치합니다. 설치 방식은 OS마다 다르므로 [설치 문서](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-on-EC2-Instance.html)를 확인합니다.

```bash
# Amazon Linux 2023 / Amazon Linux 2
sudo yum install amazon-cloudwatch-agent

# 그 밖의 배포판 (DEB 예): 공식 문서의 다운로드 링크로 받은 뒤
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

### 시작과 상태 확인

```bash
# 설정 파일을 읽어 적용하고 시작 (-a fetch-config, -m 실행 환경, -s 시작)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
     -a fetch-config -m ec2 -s \
     -c file:/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-agent.json

# 온프레미스 서버
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
     -a fetch-config -m onPremise -s -c file:<CONFIG_PATH>

# 설정을 SSM Parameter Store에 둔 경우
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
     -a fetch-config -m ec2 -s -c ssm:AmazonCloudWatch-linux

# 상태 확인
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status
```

Agent는 시작할 때 설정 파일을 `/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/`에 `file_` 또는 `ssm_` 접두사를 붙여 복사합니다. Agent 자체 로그는 기본으로 `/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log`에 남습니다.

여러 서버에 같은 설정을 쓰려면 설정 JSON을 Parameter Store(이름이 `AmazonCloudWatch-`로 시작)에 두고 Systems Manager Run Command의 `AmazonCloudWatch-ManageAgent` 문서로 배포하는 방식이 관리하기 쉽습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Agent 설정 파일

설정 파일은 `agent`, `metrics`, `logs` 세 절로 나뉩니다. 직접 작성하거나 `amazon-cloudwatch-agent-config-wizard`로 만들 수 있습니다.

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "cwagent"
  },
  "metrics": {
    "namespace": "CWAgent",
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}",
      "AutoScalingGroupName": "${aws:AutoScalingGroupName}"
    },
    "metrics_collected": {
      "mem": {
        "measurement": ["used_percent"]
      },
      "disk": {
        "measurement": ["used_percent", "inodes_free"],
        "resources": ["/", "/data"],
        "ignore_file_system_types": ["sysfs", "devtmpfs", "tmpfs", "overlay"],
        "drop_device": true
      },
      "swap": {
        "measurement": ["used_percent"]
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/ec2/prod/messages",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/ec2/prod/nginx-error",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          }
        ]
      }
    }
  }
}
```

| 키                            | 설명                                                                    |
|-------------------------------|-------------------------------------------------------------------------|
| `metrics_collection_interval` | 수집 주기(초). 기본 60. 짧게 하면 비용과 API 호출이 늘어남              |
| `run_as_user`                 | Agent 실행 계정(Linux). 지정하지 않으면 root                            |
| `append_dimensions`           | 모든 지표에 붙일 차원. `${aws:InstanceId}` 같은 변수 사용               |
| `resources`                   | 디스크 마운트 지점 목록. `*`는 모든 마운트                              |
| `drop_device`                 | 디스크 지표에서 장치 이름 차원을 뺌. 장치 이름이 바뀌어도 경보가 유지됨 |
| `log_stream_name`             | `{instance_id}`, `{hostname}`, `{ip_address}` 등 변수 사용 가능         |
| `retention_in_days`           | 로그 그룹 보존 기간. 지정하지 않은 새 로그 그룹은 만료 없음             |

🟡 이미 있는 로그 그룹에 `retention_in_days`를 지정하면 지정한 일수보다 오래된 로그가 삭제됩니다. 기존 로그 그룹에 적용하기 전에 보존 요구사항을 확인합니다.

경보는 지표 이름과 모든 차원이 정확히 일치해야 연결됩니다. `append_dimensions`를 바꾸면 기존 경보가 데이터를 받지 못해 `INSUFFICIENT_DATA`가 되므로, 차원 구성은 처음에 정해 두고 바꿀 때는 경보도 함께 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 경보 평가 방식

지표 경보(metric alarm)는 세 상태 중 하나입니다.

| 상태                | 의미                                                      |
|---------------------|-----------------------------------------------------------|
| `OK`                | 지표가 임계값 안에 있음                                   |
| `ALARM`             | 지표가 임계값을 벗어남                                    |
| `INSUFFICIENT_DATA` | 경보가 막 시작했거나 지표가 없거나 판단할 데이터가 부족함 |

경보 평가는 세 설정으로 정해집니다.

| 설정                    | 의미                                                 |
|-------------------------|------------------------------------------------------|
| Period                  | 데이터 포인트 하나를 만드는 시간 길이(초)            |
| Evaluation Periods (N)  | 상태 판단에 쓰는 최근 데이터 포인트 수               |
| Datapoints to Alarm (M) | N개 중 임계값을 넘어야 하는 개수. 연속일 필요는 없음 |

M과 N을 다르게 두면 "M out of N" 경보가 됩니다. 예를 들어 Period 60초, 5개 중 3개는 "최근 5분 중 3분 이상 임계값 초과"를 뜻합니다. 일시적인 튐에는 반응하지 않고 지속되는 문제만 잡을 때 씁니다.

```text
threshold = 80%     period = 60s     M/N = 3/5

minute :  1   2   3   4   5
value  : 85  70  90  60  88      breaching = 3 of last 5  -> ALARM
```

알아 둘 동작입니다.

- Period가 1분 이상이면 경보는 매분 평가합니다. 고해상도 지표에는 Period 10초·20초·30초의 고해상도 경보를 만들 수 있고(추가 요금), 10초마다 평가합니다.
- Period × Evaluation Periods가 하루를 넘으면 한 시간에 한 번 평가합니다.
- 경보 동작(SNS 알림 등)은 상태가 바뀔 때만 실행됩니다. Auto Scaling 동작은 예외로, 새 상태가 유지되는 동안 1분마다 다시 실행됩니다.
- 경보 이력은 30일 동안 보관됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 누락 데이터 처리

서버가 멈추거나 Agent가 죽으면 데이터 포인트가 비어 들어옵니다. `TreatMissingData`로 빈 데이터를 어떻게 볼지 정합니다.

| 값               | 동작                                                 | 맞는 경우                                       |
|------------------|------------------------------------------------------|-------------------------------------------------|
| `missing` (기본) | 평가 범위의 데이터가 모두 없으면 `INSUFFICIENT_DATA` | 일반 지표                                       |
| `breaching`      | 빈 데이터를 임계값 초과로 봄                         | 꾸준히 들어와야 하는 지표(하트비트, Agent 지표) |
| `notBreaching`   | 빈 데이터를 정상으로 봄                              | 오류가 날 때만 기록되는 지표                    |
| `ignore`         | 현재 상태 유지                                       | 간헐적으로만 들어오는 지표                      |

판단 기준입니다.

- Agent가 보내는 `mem_used_percent`에 `missing`을 쓰면 Agent가 멈췄을 때 `INSUFFICIENT_DATA`로만 바뀌고 SNS 알림이 가지 않을 수 있습니다. 데이터가 끊긴 것 자체를 알리려면 `breaching`을 쓰거나 `INSUFFICIENT_DATA` 상태에도 알림 동작을 붙입니다.
- AWS 문서는 EC2 지표에 정지·종료·재부팅·복구 동작을 붙인 경보에는 `missing`을 쓰고 `ALARM` 상태에서만 동작하게 하라고 권고합니다. EC2 지표는 인스턴스가 정상이어도 드물게 데이터가 빠질 수 있기 때문입니다.
- `AWS/DynamoDB` 네임스페이스 경보는 기본값이 `ignore`입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 경보 만들기

SNS 주제를 만들고 구독을 확인한 뒤 경보를 만듭니다.

```bash
# 1. 알림용 SNS 주제와 메일 구독 (메일로 온 확인 링크를 눌러야 활성화)
aws sns create-topic --name ops-alerts
aws sns subscribe --topic-arn arn:aws:sns:<REGION>:<ACCOUNT_ID>:ops-alerts \
    --protocol email --notification-endpoint ops@example.com

# 2. 메모리 경보: 1분 주기, 5개 중 3개가 90% 초과면 ALARM
aws cloudwatch put-metric-alarm \
    --alarm-name "prod-web01-mem-high" \
    --namespace CWAgent \
    --metric-name mem_used_percent \
    --dimensions Name=InstanceId,Value=<INSTANCE_ID> \
    --statistic Average \
    --period 60 \
    --evaluation-periods 5 \
    --datapoints-to-alarm 3 \
    --threshold 90 \
    --comparison-operator GreaterThanThreshold \
    --treat-missing-data breaching \
    --alarm-actions arn:aws:sns:<REGION>:<ACCOUNT_ID>:ops-alerts \
    --ok-actions arn:aws:sns:<REGION>:<ACCOUNT_ID>:ops-alerts

# 3. 상태 검사 실패 시 인스턴스 복구 (EC2 동작은 missing 권고)
aws cloudwatch put-metric-alarm \
    --alarm-name "prod-web01-status-recover" \
    --namespace AWS/EC2 \
    --metric-name StatusCheckFailed_System \
    --dimensions Name=InstanceId,Value=<INSTANCE_ID> \
    --statistic Maximum --period 60 --evaluation-periods 2 \
    --threshold 0 --comparison-operator GreaterThanThreshold \
    --treat-missing-data missing \
    --alarm-actions arn:aws:automate:<REGION>:ec2:recover
```

디스크 경보는 `append_dimensions`와 `drop_device` 설정에 따라 차원이 달라집니다. 먼저 실제 차원을 확인하고 그대로 지정합니다.

```bash
aws cloudwatch list-metrics --namespace CWAgent --metric-name disk_used_percent \
    --dimensions Name=InstanceId,Value=<INSTANCE_ID>
```

경보 동작을 시험할 때는 `set-alarm-state`로 상태를 잠시 바꿉니다. 바뀐 상태는 다음 평가 때 원래대로 돌아갑니다.

```bash
aws cloudwatch set-alarm-state --alarm-name "prod-web01-mem-high" \
    --state-value ALARM --state-reason "notification test"
```

여러 경보를 묶는 복합 경보(composite alarm)는 다른 경보들의 상태를 규칙식으로 조합합니다. 예를 들어 "CPU 높음 AND 응답 지연 높음"일 때만 알림을 보내 알림 소음을 줄일 수 있습니다. 복합 경보는 SNS 알림은 보낼 수 있지만 EC2 동작이나 Auto Scaling 동작은 할 수 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 경보 설계 기준

| 기준                     | 설명                                                                              |
|--------------------------|-----------------------------------------------------------------------------------|
| 행동할 수 있는 경보만 둠 | 받은 사람이 할 일이 없는 경보는 대시보드로 옮김                                   |
| 지속 시간 조건           | 순간 튐은 M out of N이나 긴 Period로 거름                                         |
| 데이터 끊김도 장애로 봄  | Agent 지표는 `breaching` 또는 `INSUFFICIENT_DATA` 알림                            |
| 심각도 분리              | 즉시 대응(페이징)과 업무 시간 처리(티켓)를 다른 SNS 주제로 나눔                   |
| 복구 알림                | `--ok-actions`로 해소도 알려 대응 종료 시점을 남김                                |
| 이름 규칙                | `<환경>-<대상>-<지표>-<조건>`처럼 정해 두면 검색·필터가 쉬움                      |
| 코드로 관리              | 콘솔에서 만든 경보는 누락·불일치가 생기기 쉬움. Terraform·CloudFormation으로 관리 |

처음 운영할 때 갖출 최소 경보 예입니다.

| 대상          | 지표                               | 조건 예            |
|---------------|------------------------------------|--------------------|
| 인스턴스 상태 | `StatusCheckFailed`                | 2분 연속 > 0       |
| CPU           | `CPUUtilization`                   | 15분 중 10분 > 85% |
| 메모리        | `mem_used_percent` (CWAgent)       | 5분 중 3분 > 90%   |
| 디스크        | `disk_used_percent` (CWAgent)      | 5분 연속 > 85%     |
| 로그 오류     | 로그 지표 필터로 만든 `ErrorCount` | 5분 합계 > 0       |

임계값은 시작점입니다. 2~4주 운영하면서 과거 지표와 오탐 이력을 보고 조정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                            | 확인                                                | 대응                                                    |
|---------------------------------|-----------------------------------------------------|---------------------------------------------------------|
| `CWAgent` 지표가 안 보임        | `amazon-cloudwatch-agent-ctl -a status`, Agent 로그 | 인스턴스 역할과 `CloudWatchAgentServerPolicy` 연결 확인 |
| Agent 로그에 `AccessDenied`     | 인스턴스 프로파일, 정책                             | 역할 연결 후 Agent 재시작                               |
| 경보가 계속 `INSUFFICIENT_DATA` | `list-metrics`로 실제 차원 확인                     | 경보 차원을 지표와 정확히 맞춤                          |
| 로그가 안 올라감                | 파일 경로·권한, `run_as_user` 계정의 읽기 권한      | 로그 파일 권한 조정 또는 실행 계정 변경                 |
| 비용이 갑자기 늘어남            | 지표 수(차원 조합), 수집 주기, `resources: ["*"]`   | 필요한 마운트·차원만 남기고 주기 조정                   |
| 메일 알림이 오지 않음           | SNS 구독 상태가 `PendingConfirmation`인지           | 확인 메일의 링크로 구독 확인                            |

VPC에 인터넷 경로가 없는 사설 서브넷 인스턴스는 CloudWatch(`monitoring`)·CloudWatch Logs(`logs`) 인터페이스 VPC 엔드포인트가 있어야 Agent가 데이터를 보낼 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 점검표

| 항목                                              | 주기    |
|---------------------------------------------------|---------|
| 모든 운영 인스턴스에서 Agent 상태 `running`       | 주 1회  |
| 경보 중 `INSUFFICIENT_DATA`로 오래 머무는 것 정리 | 주 1회  |
| SNS 구독 확인 상태와 수신자 목록                  | 분기    |
| `set-alarm-state`로 주요 경보 알림 경로 시험      | 분기    |
| 로그 그룹 보존 기간과 보존 요구사항 일치          | 분기    |
| 사용자 지정 지표 수와 CloudWatch 비용 추이        | 월 1회  |
| 경보 정의가 IaC 코드와 일치                       | 변경 때 |

관련 문서:

- AWS 보안 점검(CloudTrail·GuardDuty): [aws_security.md](../../04_security/cloud/aws_security.md)
- 온프레미스 모니터링 비교: [zabbix_vs_prometheus.md](../monitoring/zabbix_vs_prometheus.md)
- 호스트 지표 수집(Prometheus): [node_exporter_operations.md](../monitoring/node_exporter_operations.md)

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Using Amazon CloudWatch alarms: [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html) — ★★★☆☆ (확인일 2026-11-16)
- Alarm evaluation: [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarm-evaluation.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarm-evaluation.html) — ★★★☆☆ (확인일 2026-11-16)
- Configuring how CloudWatch alarms treat missing data: [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html) — ★★★☆☆ (확인일 2026-11-16)
- Starting the CloudWatch agent: [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/start-CloudWatch-Agent-on-premise-SSM-onprem.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/start-CloudWatch-Agent-on-premise-SSM-onprem.html) — ★★★☆☆ (확인일 2026-11-16)
- CloudWatch agent configuration file details: [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html) — ★★★☆☆ (확인일 2026-11-16)
- Metrics collected by the CloudWatch agent: [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-collected-by-CloudWatch-agent.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-collected-by-CloudWatch-agent.html) — ★★★☆☆ (확인일 2026-11-16)
- CloudWatch agent prerequisites (IAM): [docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/prerequisites.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/prerequisites.html) — ★★★☆☆ (확인일 2026-11-16)
- Manage detailed monitoring for your EC2 instances: [docs.aws.amazon.com/AWSEC2/latest/UserGuide/manage-detailed-monitoring.html](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/manage-detailed-monitoring.html) — ★★★☆☆ (확인일 2026-11-16)
- Amazon CloudWatch 요금: [aws.amazon.com/cloudwatch/pricing](https://aws.amazon.com/cloudwatch/pricing/) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
