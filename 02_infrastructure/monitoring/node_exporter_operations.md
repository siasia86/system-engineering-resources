# node_exporter 운영 가이드
<!-- reference: _reference/prometheus_official_notes.md -->

node_exporter는 Linux·Unix 호스트의 CPU·메모리·디스크·네트워크 같은 하드웨어·커널 지표를 Prometheus 형식으로 노출하는 exporter입니다. 설치는 [Prometheus·Grafana 설치](prometheus_grafana_install.md)에서 다루므로, 이 문서는 collector 선택, textfile collector, 핵심 지표와 PromQL, 알림 규칙, 보안·부하 관리를 운영 관점에서 정리합니다.

> 기준 판: node_exporter 1.13.1 (2026-11-19 릴리스, GitHub releases 기준, 확인일 2026-11-23). 2026-11-23 `prom/node-exporter:v1.13.1` 컨테이너에서 `--help`와 `/metrics`를 확인했습니다.

## 목차

| 목차                                                                                            |
|-------------------------------------------------------------------------------------------------|
| [1. 동작 구조](#1-동작-구조) / [2. collector 관리](#2-collector-관리)                           |
| [3. textfile collector](#3-textfile-collector) / [4. 핵심 지표와 PromQL](#4-핵심-지표와-promql) |
| [5. 알림 규칙 예](#5-알림-규칙-예) / [6. scrape 설정과 필터](#6-scrape-설정과-필터)             |
| [7. 보안](#7-보안) / [8. 트러블슈팅](#8-트러블슈팅) / [9. 운영 점검표](#9-운영-점검표)          |

---

## 1. 동작 구조

```text
+-------------------- host --------------------+
|  /proc  /sys  (kernel)                        |
|      |                                        |
|  node_exporter :9100/metrics                  |
|      |  collectors: cpu, meminfo, diskstats,  |
|      |  filesystem, netdev, textfile ...      |
|      |                                        |
|  /var/lib/node_exporter/textfile/*.prom  <----+-- cron / systemd timer scripts
+------|----------------------------------------+
       | HTTP pull (scrape)
       v
  Prometheus  --->  Alertmanager / Grafana
```

- node_exporter는 기본으로 HTTP 9100번 포트에서 `/metrics`를 제공합니다.
- 지표는 scrape 요청이 올 때마다 `/proc`·`/sys`를 읽어 만듭니다. 값을 저장하지 않으므로, 이력은 Prometheus에 있습니다.
- collector는 지표 묶음 단위의 수집 모듈입니다. 기본 활성 collector와 기본 비활성 collector가 나뉘어 있습니다.

컨테이너 지표(cAdvisor), 프로세스별 지표(process-exporter), 애플리케이션 지표는 node_exporter 범위가 아닙니다. 호스트 전체 자원만 다룬다고 보면 됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. collector 관리

collector는 플래그로 켜고 끕니다.

| 플래그                         | 의미                                             |
|--------------------------------|--------------------------------------------------|
| `--collector.<name>`           | 해당 collector 켜기                              |
| `--no-collector.<name>`        | 기본 활성 collector 끄기                         |
| `--collector.disable-defaults` | 기본 활성 collector를 모두 끄고 지정한 것만 사용 |

기본 활성 collector 중 운영에서 자주 보는 것입니다(공식 README 기준).

| collector      | 내용                                      |
|----------------|-------------------------------------------|
| `cpu`          | CPU 모드별 사용 시간                      |
| `meminfo`      | `/proc/meminfo` 메모리 통계               |
| `loadavg`      | load average                              |
| `diskstats`    | 디스크 I/O 횟수·바이트·시간               |
| `filesystem`   | 파일시스템 크기·여유·inode                |
| `netdev`       | 네트워크 인터페이스 송수신·오류·drop      |
| `pressure`     | PSI(Pressure Stall Information) 자원 대기 |
| `mdadm`        | md 소프트웨어 RAID 상태                   |
| `time`·`timex` | 시스템 시각과 NTP 동기화 상태             |
| `textfile`     | 디렉터리의 `*.prom` 파일 읽기             |

기본 비활성이지만 필요할 때 켜는 것입니다.

| collector    | 용도                             | 주의                               |
|--------------|----------------------------------|------------------------------------|
| `systemd`    | 유닛 상태(`active`/`failed`)     | 유닛 수가 많으면 지표 수 증가      |
| `processes`  | 프로세스·스레드 수와 상태별 개수 |                                    |
| `tcpstat`    | TCP 연결 상태별 개수             | 연결이 많은 서버는 수집 비용 증가  |
| `ethtool`    | NIC 드라이버 통계                | 지표 수가 많음                     |
| `interrupts` | 인터럽트별 횟수                  | CPU 수 × 인터럽트 수만큼 지표 생성 |

systemd collector를 켜되 필요한 유닛만 남기는 예입니다.

```bash
/usr/local/bin/node_exporter \
  --collector.systemd \
  --collector.systemd.unit-include='(sshd|nginx|docker)\.service' \
  --collector.textfile.directory=/var/lib/node_exporter/textfile \
  --collector.filesystem.mount-points-exclude='^/(dev|proc|run|sys|var/lib/docker/.+)($|/)'
```

플래그 이름과 기본값은 판마다 바뀔 수 있으므로 설치한 바이너리에서 `node_exporter --help`로 확인합니다.

1.13에서 달라진 점입니다.

| 항목                       | 내용                                                                                                                             |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `node_cpu_frequency_hertz` | cpu·cpufreq collector가 같은 이름을 쓰던 동작이 1.12 이전 방식으로 되돌아감. 대시보드·알림이 이 지표를 쓰면 판 올린 뒤 값을 확인 |
| 새 플래그                  | `--collector.cpufreq.enable-cpufreq-prefix`: cpufreq 지표를 `node_cpufreq_` 이름으로 분리 (v2에서 기본값이 될 예정)              |
| 새 collector               | `tainted`(커널 tainted 상태), `resctrl`. 둘 다 기본 꺼짐                                                                         |
| 폐지 예정 지표             | `nvme_namespace_capacity_bytes`                                                                                                  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. textfile collector

textfile collector는 지정한 디렉터리의 `*.prom` 파일을 읽어 그대로 노출합니다. 별도 exporter를 만들지 않고 배치 작업 결과, 백업 성공 시각, RAID 컨트롤러 상태, 패키지 업데이트 대기 수 같은 값을 지표로 만들 수 있습니다.

파일 형식은 Prometheus 텍스트 노출 형식입니다.

```text
# HELP backup_last_success_timestamp_seconds Unix time of last successful backup.
# TYPE backup_last_success_timestamp_seconds gauge
backup_last_success_timestamp_seconds{job="restic_daily"} 1.7633e+09
```

작성 규칙입니다.

- 쓰는 도중의 파일을 읽지 않도록 임시 파일에 쓰고 `mv`로 바꿉니다(같은 파일시스템 안의 rename은 원자적).
- 공식 README 기준으로 파일 안의 타임스탬프는 지원하지 않습니다. 시각은 위 예처럼 값으로 넣습니다.
- 같은 지표 이름을 여러 파일에서 쓰면 HELP 문구를 같게 맞춥니다. 다르면 scrape 오류가 납니다.

백업 스크립트 끝에서 성공 시각을 기록하는 예입니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

TEXTFILE_DIR="/var/lib/node_exporter/textfile"
OUT="${TEXTFILE_DIR}/backup.prom"

# ... 백업 명령 실행 (실패하면 set -e로 여기서 종료되어 시각이 갱신되지 않음) ...

cat > "${OUT}.$$" <<EOF
# HELP backup_last_success_timestamp_seconds Unix time of last successful backup.
# TYPE backup_last_success_timestamp_seconds gauge
backup_last_success_timestamp_seconds{job="restic_daily"} $(date +%s)
EOF
mv "${OUT}.$$" "${OUT}"
```

textfile collector 자체의 상태 지표입니다.

| 지표                          | 의미                                            |
|-------------------------------|-------------------------------------------------|
| `node_textfile_mtime_seconds` | 정상으로 읽은 각 파일의 수정 시각 (`file` 라벨) |
| `node_textfile_scrape_error`  | 파일을 열거나 읽다가 오류가 나면 1              |

`node_textfile_mtime_seconds`로 "스크립트가 멈춰 파일이 오래되었는지"를 감시할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 핵심 지표와 PromQL

카운터(`_total`, `_seconds_total`)는 누적값이므로 `rate()`나 `increase()`로 변화량을 봅니다.

| 영역          | 지표                                         | PromQL 예                                                                                                                  |
|---------------|----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| CPU           | `node_cpu_seconds_total{mode}`               | `1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))`                                                    |
| CPU 대기      | `node_cpu_seconds_total{mode="iowait"}`      | `avg by (instance) (rate(node_cpu_seconds_total{mode="iowait"}[5m]))`                                                      |
| 부하          | `node_load1`, `node_load5`                   | `node_load5 / count by (instance) (node_cpu_seconds_total{mode="idle"})`                                                   |
| 메모리        | `node_memory_MemAvailable_bytes`             | `1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes`                                                          |
| 디스크        | `node_filesystem_avail_bytes`                | `node_filesystem_avail_bytes{fstype!~"tmpfs                                      | overlay"} / node_filesystem_size_bytes` |
| inode         | `node_filesystem_files_free`                 | `node_filesystem_files_free / node_filesystem_files`                                                                       |
| 디스크 I/O    | `node_disk_io_time_seconds_total`            | `rate(node_disk_io_time_seconds_total[5m])` (1에 가까우면 장치가 거의 항상 바쁨)                                           |
| 네트워크      | `node_network_receive_bytes_total`           | `rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8` (bit/s)                                                     |
| 네트워크 오류 | `node_network_receive_errs_total`            | `increase(node_network_receive_errs_total[10m])`                                                                           |
| PSI           | `node_pressure_memory_waiting_seconds_total` | `rate(node_pressure_memory_waiting_seconds_total[5m])`                                                                     |
| 시간          | `node_timex_sync_status`                     | `node_timex_sync_status == 0` (동기화 안 됨)                                                                               |

메모리 사용률은 `MemFree`가 아니라 `MemAvailable`을 기준으로 봅니다. Linux는 남는 메모리를 페이지 캐시로 쓰므로 `MemFree`만 보면 늘 부족해 보입니다.

디스크가 가득 차는 시점을 미리 잡으려면 `predict_linear()`로 추세를 봅니다.

```promql
# 지난 6시간 추세로 24시간 뒤 여유 공간이 0 미만이 되는 파일시스템
predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}[6h], 24 * 3600) < 0
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 알림 규칙 예

아래 임계값은 시작점 예시입니다. 서비스 특성과 과거 지표를 보고 조정합니다.

```yaml
groups:
  - name: node
    rules:
      - alert: NodeExporterDown
        expr: up{job="node"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "node_exporter on {{ $labels.instance }} is not reachable"

      - alert: NodeFilesystemFillingUp
        expr: |
          (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes < 0.15)
          and predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}[6h], 24 * 3600) < 0
          and node_filesystem_readonly == 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.mountpoint }} on {{ $labels.instance }} may fill up within 24h"

      - alert: NodeMemoryLow
        expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.10
        for: 15m
        labels:
          severity: warning

      - alert: NodeClockNotSynced
        expr: node_timex_sync_status == 0
        for: 15m
        labels:
          severity: warning

      - alert: BackupTooOld
        expr: time() - backup_last_success_timestamp_seconds > 26 * 3600
        labels:
          severity: warning

      - alert: TextfileCollectorError
        expr: node_textfile_scrape_error == 1
        for: 10m
        labels:
          severity: warning
```

규칙 파일은 적용 전에 문법을 검사합니다.

```bash
promtool check rules /etc/prometheus/rules/node.yml
```

공식 저장소 하위의 `docs/node-mixin`에는 Prometheus 커뮤니티가 관리하는 node_exporter용 알림 규칙과 대시보드 묶음(mixin)이 있습니다. 처음 구성할 때 참고하기 좋습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. scrape 설정과 필터

```yaml
# prometheus.yml
scrape_configs:
  - job_name: node
    scrape_interval: 30s
    static_configs:
      - targets:
          - 192.0.2.10:9100
          - 192.0.2.11:9100
        labels:
          env: prod
```

수집 범위를 줄이는 방법은 두 가지입니다.

| 방법                                   | 위치            | 특징                                            |
|----------------------------------------|-----------------|-------------------------------------------------|
| `--no-collector.*`, `disable-defaults` | node_exporter   | 모든 scrape에 적용                              |
| `params: collect[]` / `exclude[]`      | Prometheus 설정 | scrape job별로 다르게 적용. 둘을 함께 쓰지 못함 |

```yaml
  - job_name: node_minimal
    params:
      collect[]:
        - cpu
        - meminfo
        - filesystem
    static_configs:
      - targets: ['192.0.2.12:9100']
```

지표 수(cardinality)가 늘어나는 주요 원인은 컨테이너 호스트의 수많은 veth 인터페이스와 overlay 마운트입니다. `--collector.netdev.device-exclude`, `--collector.filesystem.mount-points-exclude`로 걸러 냅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 보안

node_exporter의 `/metrics`에는 호스트 이름, 커널 판, 마운트 경로, 네트워크 인터페이스 같은 구성 정보가 들어 있습니다. 인터넷에 그대로 노출하지 않습니다.

| 방법             | 설명                                                                  |
|------------------|-----------------------------------------------------------------------|
| 방화벽           | 9100 포트를 Prometheus 서버 주소에서만 허용                           |
| 바인드 주소 제한 | `--web.listen-address=192.0.2.10:9100`처럼 내부 주소에만 바인드       |
| TLS·기본 인증    | `--web.config.file=web-config.yml` (공식 README는 실험 기능으로 표시) |
| 전용 계정        | root가 아닌 시스템 계정으로 실행                                      |

```yaml
# web-config.yml 예 (bcrypt 해시는 htpasswd -nBC 10 "" 등으로 생성)
tls_server_config:
  cert_file: /etc/node_exporter/node.crt
  key_file: /etc/node_exporter/node.key
basic_auth_users:
  prometheus: <BCRYPT_HASH>
```

```bash
# 방화벽 예 (firewalld): Prometheus 서버 192.0.2.5만 허용
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.0.2.5/32" port port="9100" protocol="tcp" accept'
sudo firewall-cmd --reload
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                 | 확인                                                                | 대응                                            |
|--------------------------------------|---------------------------------------------------------------------|-------------------------------------------------|
| `up == 0`                            | `curl -s http://192.0.2.10:9100/metrics \| head`                    | 서비스 상태, 방화벽, 바인드 주소 확인           |
| scrape 시간이 길다                   | `scrape_duration_seconds`, `node_scrape_collector_duration_seconds` | 느린 collector를 찾아 끄거나 범위 축소          |
| 특정 collector 실패                  | `node_scrape_collector_success == 0`                                | 로그(`journalctl -u node_exporter`)와 권한 확인 |
| 디스크 지표에 컨테이너 마운트가 섞임 | `node_filesystem_size_bytes` 라벨 확인                              | `mount-points-exclude`, `fs-types-exclude` 조정 |
| textfile 지표가 안 보임              | `node_textfile_scrape_error`, 파일 확장자·권한                      | `*.prom` 확장자, 읽기 권한, HELP 충돌 확인      |

`node_scrape_collector_duration_seconds`와 `node_scrape_collector_success`는 node_exporter가 collector마다 내보내는 자기 진단 지표입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 점검표

| 항목                                                   | 주기         |
|--------------------------------------------------------|--------------|
| 모든 대상의 `up` 지표와 `NodeExporterDown` 알림 동작   | 상시 감시    |
| node_exporter 판 확인과 릴리스 노트의 변경·제거 플래그 | 분기         |
| 켜 둔 비활성 collector와 지표 수(cardinality) 점검     | 분기         |
| textfile 스크립트의 `mtime` 갱신과 `scrape_error`      | 상시 감시    |
| 9100 포트 접근 제한(방화벽·바인드 주소)                | 구성 변경 때 |
| 알림 규칙 `promtool check rules` 통과                  | 변경 때      |

관련 문서:

- 설치와 Docker Compose 구성: [prometheus_grafana_install.md](prometheus_grafana_install.md)
- Prometheus·Alertmanager 구조와 PromQL: [prometheus_grafana.md](prometheus_grafana.md)
- 자원 사용률 해석: [resource_utilization_monitoring.md](resource_utilization_monitoring.md)
- md RAID 지표: [mdadm_software_raid.md](../storage/mdadm_software_raid.md)

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- node_exporter 공식 저장소 README: [github.com/prometheus/node_exporter](https://github.com/prometheus/node_exporter) — ★★★☆☆ (확인일 2026-11-16)
- node_exporter Releases: [github.com/prometheus/node_exporter/releases](https://github.com/prometheus/node_exporter/releases) — ★★★☆☆ (확인일 2026-11-16)
- textfile collector 소스: [collector/textfile.go](https://github.com/prometheus/node_exporter/blob/master/collector/textfile.go) — ★★★☆☆ (확인일 2026-11-16)
- Monitoring Linux host metrics with the Node Exporter: [prometheus.io/docs/guides/node-exporter](https://prometheus.io/docs/guides/node-exporter/) — ★★★☆☆ (확인일 2026-11-16)
- Prometheus Alerting rules: [prometheus.io/docs/prometheus/latest/configuration/alerting_rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) — ★★★☆☆ (확인일 2026-11-16)
- Exporter TLS·인증 설정: [github.com/prometheus/exporter-toolkit/blob/master/docs/web-configuration.md](https://github.com/prometheus/exporter-toolkit/blob/master/docs/web-configuration.md) — ★★★☆☆ (확인일 2026-11-16)
- [Prometheus 공식 참조 노트](../../_reference/prometheus_official_notes.md)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
