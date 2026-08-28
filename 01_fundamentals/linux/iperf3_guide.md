# iperf3 네트워크 성능·loss 측정 가이드
<!-- reference: _reference/iperf3_official_notes.md -->

`iperf3`는 두 호스트 사이의 TCP·UDP throughput, latency 변동, UDP packet loss, jitter를 측정하는 네트워크 테스트 도구입니다. ICMP `ping`이 차단된 환경에서도 실제 TCP·UDP 포트를 사용해 통신 품질을 확인할 수 있습니다.

`iperf3`는 운영 트래픽을 대체하지 않습니다. 테스트 bandwidth를 과도하게 설정하면 네트워크 congestion을 만들 수 있으므로, 관리망 또는 승인된 테스트 시간에 제한된 source·destination으로 수행합니다.

## 목차

| 섹션                                                                                    |
|-----------------------------------------------------------------------------------------|
| [1. 구조와 사전 확인](#1-구조와-사전-확인) / [2. 설치](#2-설치)                         |
| [3. TCP 측정](#3-tcp-측정) / [4. UDP loss·jitter 측정](#4-udp-lossjitter-측정)          |
| [5. 방향·병렬·JSON 옵션](#5-방향병렬json-옵션) / [6. Windows 방화벽](#6-windows-방화벽) |
| [7. 결과 해석](#7-결과-해석) / [8. 안전한 종료와 정리](#8-안전한-종료와-정리)           |

---

## 1. 구조와 사전 확인

`iperf3`는 한쪽을 server, 다른 쪽을 client로 실행합니다.

```text
iperf3 server                         iperf3 client
192.0.2.10:5201  <=================>  192.0.2.20
```

- server: `iperf3 -s`로 수신 대기합니다.
- client: `iperf3 -c <server>`로 테스트를 시작합니다.
- 기본 port: TCP·UDP `5201`
- 테스트 방향: 기본적으로 client가 server로 전송합니다.

### 사전 확인

서버에서 iperf3 버전을 확인합니다.

```bash
iperf3 --version
```

Windows client에서 TCP port만 사전 확인할 수 있습니다.

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 5201
```

`Test-NetConnection`은 TCP 연결만 확인합니다. UDP 통신 여부와 packet loss는 iperf3 UDP 테스트로 확인해야 합니다.

테스트 전에 다음 정보를 확정합니다.

- server·client의 실제 IP와 interface
- TCP 또는 UDP 측정 여부
- 허용된 테스트 bandwidth
- 테스트 시간과 최대 실행 시간
- 방화벽에 허용할 source IP
- 결과 파일 보관 위치와 민감정보 처리 기준

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### Ubuntu·Debian

```bash
sudo apt-get update
sudo apt-get install iperf3
```

### Fedora·RHEL 계열

```bash
sudo dnf install iperf3
```

### Arch Linux

```bash
sudo pacman -S iperf3
```

### Windows

Windows에서는 조직에서 승인한 `iperf3.exe` binary 또는 package source를 사용합니다. 설치 전 package source와 binary hash를 확인합니다.

```powershell
winget search iperf3
iperf3.exe --version
```

`winget search` 결과의 package ID가 조직 정책에 맞는지 확인한 뒤 설치합니다. 출처가 불명확한 실행 파일이나 임의의 다운로드 script를 사용하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. TCP 측정

TCP 측정은 실제 TCP 서비스의 throughput과 sender 측 retransmission을 확인하는 데 적합합니다.

### Server 시작

Linux:

```bash
iperf3 -s -p 5201
```

Windows PowerShell:

```powershell
iperf3.exe -s -p 5201
```

### 기본 TCP 측정

Client에서 실행합니다.

```bash
iperf3 -c 192.0.2.10 -p 5201 -t 60 -i 1
```

- `-c`: server 주소
- `-p`: server port
- `-t 60`: 60초 실행
- `-i 1`: 1초 간격 결과 출력

Windows:

```powershell
iperf3.exe -c 192.0.2.10 -p 5201 -t 60 -i 1
```

TCP 결과의 `sender`와 `receiver` throughput 차이가 크거나 `Retr` 값이 증가하면 경로·NIC·receiver 처리 상태를 추가로 확인합니다.

### 짧은 반복 측정

간헐적인 문제를 관찰할 때 여러 번 실행합니다.

```powershell
1..10 | ForEach-Object {
    $Start = Get-Date
    iperf3.exe -c 192.0.2.10 -p 5201 -t 10 -i 1
    Write-Host "finished: $Start"
    Start-Sleep -Seconds 5
}
```

동일한 시간대의 서버 log와 client 결과를 함께 보관해야 원인 비교가 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. UDP loss·jitter 측정

UDP는 재전송이 없으므로 `Lost/Total Datagrams`, loss percentage, jitter를 직접 확인할 수 있습니다. 테스트 bandwidth를 낮은 값부터 시작합니다.

### UDP 기본 측정

```bash
iperf3 -c 192.0.2.10 -u -b 10M -t 60 -i 1
```

Windows:

```powershell
iperf3.exe -c 192.0.2.10 -u -b 10M -t 60 -i 1
```

- `-u`: UDP mode
- `-b 10M`: 목표 bandwidth 10 Mbps
- `-t 60`: 60초 실행
- `-i 1`: 1초 간격 출력

### 단계적으로 bandwidth 증가

처음부터 회선 최대 bandwidth를 사용하지 않습니다.

```powershell
iperf3.exe -c 192.0.2.10 -u -b 1M  -t 30 -i 1
iperf3.exe -c 192.0.2.10 -u -b 10M -t 30 -i 1
iperf3.exe -c 192.0.2.10 -u -b 50M -t 30 -i 1
```

각 결과에서 loss와 jitter가 급증하는 구간을 비교합니다.

UDP loss가 발생했다고 해서 항상 중간 네트워크 장비의 packet loss로 단정하지 않습니다. receiver CPU, NIC ring buffer, firewall inspection, socket buffer 부족도 원인이 될 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 방향·병렬·JSON 옵션

### Reverse 방향

기본 테스트는 client에서 server로 전송합니다. 반대 방향은 `-R`을 사용합니다.

```bash
iperf3 -c 192.0.2.10 -R -t 60 -i 1
iperf3 -c 192.0.2.10 -u -b 10M -R -t 60 -i 1
```

한 방향에서만 문제가 발생하면 routing, QoS, asymmetric path, 송신·수신 NIC 상태를 비교합니다.

### Parallel stream

단일 TCP stream이 회선 성능을 충분히 사용하지 못할 때 여러 stream을 사용합니다.

```bash
iperf3 -c 192.0.2.10 -P 4 -t 60 -i 1
```

`-P` 값이 클수록 host CPU와 네트워크 부하가 증가하므로 작은 값부터 사용합니다.

### JSON 결과

자동 분석과 보관에는 JSON 출력을 사용합니다.

```bash
iperf3 -c 192.0.2.10 -u -b 10M -t 60 -i 1 --json > iperf3-udp-result.json
```

Windows:

```powershell
iperf3.exe -c 192.0.2.10 -u -b 10M -t 60 -i 1 --json `
    | Out-File -Encoding utf8 .\iperf3-udp-result.json
```

결과 파일에는 IP 주소, port, throughput, jitter, loss 정보가 포함될 수 있으므로 외부 공유 전에 대상 정보와 운영 환경 정보를 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Windows 방화벽

Windows server에서 iperf3를 실행할 때는 테스트 protocol과 port에 맞는 inbound rule이 필요합니다.

### TCP 5201 임시 허용

```powershell
New-NetFirewallRule `
    -DisplayName "iperf3 temporary TCP 5201" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5201 `
    -RemoteAddress 192.0.2.20 `
    -Action Allow
```

### UDP 5201 임시 허용

```powershell
New-NetFirewallRule `
    -DisplayName "iperf3 temporary UDP 5201" `
    -Direction Inbound `
    -Protocol UDP `
    -LocalPort 5201 `
    -RemoteAddress 192.0.2.20 `
    -Action Allow
```

`RemoteAddress`는 실제 client IP 또는 제한된 관리망으로 지정합니다. `Any`로 공개하지 않습니다.

현재 rule 확인:

```powershell
Get-NetFirewallRule -DisplayName "iperf3 temporary *" |
    Get-NetFirewallPortFilter
```

테스트가 끝나면 rule을 제거합니다.

```powershell
Remove-NetFirewallRule -DisplayName "iperf3 temporary TCP 5201"
Remove-NetFirewallRule -DisplayName "iperf3 temporary UDP 5201"
```

방화벽 변경은 운영 정책과 승인 범위를 확인한 뒤 수행합니다. 테스트 port를 인터넷에 장시간 노출하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 결과 해석

### TCP 결과

```text
Throughput 감소 + Retr 증가
→ TCP retransmission 또는 경로 품질 저하 가능성

TCP 연결 실패
→ port 정책·방화벽·server process·경로 문제 가능성

Reverse 방향만 성능 저하
→ 비대칭 routing·QoS·수신 경로 가능성

Parallel stream에서만 성능 증가
→ 단일 stream window·호스트 처리 한계 가능성
```

TCP의 `Retr` 값은 iperf3가 관찰한 sender 측 retransmission입니다. 이것만으로 특정 장비의 packet loss 위치를 확정할 수 없습니다.

### UDP 결과

```text
Lost/Total Datagrams 증가
→ UDP loss 가능성

Jitter 증가
→ packet delivery 시간 변동 가능성

Throughput 목표 대비 실제 수신량 감소
→ congestion·receiver 처리 한계·rate shaping 가능성
```

UDP 테스트 결과는 다음 조건과 함께 기록합니다.

- 송신 bandwidth
- packet length
- 테스트 방향
- 테스트 시간
- server·client CPU와 NIC 상태
- firewall·QoS·traffic shaping 정책

### ICMP 차단 환경에서의 판단

`ping`이 차단된 경우 ICMP loss를 측정할 수 없습니다. 대신 애플리케이션이 실제 사용하는 TCP port와 controlled UDP test를 각각 확인합니다.

```text
TCP 443 실패 + TCP 5201 실패
→ 공통 경로·방화벽·routing 가능성

TCP 443 성공 + TCP 5201 실패
→ iperf3 port 방화벽 또는 server 설정 가능성

TCP 성공 + UDP loss 발생
→ UDP 정책·rate·receiver 처리·경로 품질 추가 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 안전한 종료와 정리

### Server 종료

iperf3 server가 foreground로 실행 중이면 다음으로 종료합니다.

```text
Ctrl-c
```

Windows PowerShell에서도 동일합니다.

```powershell
Stop-Process -Name iperf3
```

`Stop-Process`는 다른 테스트가 실행 중인지 확인한 뒤 사용합니다.

### 테스트 결과 보관

```bash
iperf3 -c 192.0.2.10 -u -b 10M -t 60 --json > iperf3-20260828-udp.json
```

결과 파일의 IP 주소와 운영 정보가 외부로 유출되지 않도록 접근 권한과 보관 기간을 정합니다.

### 테스트 종료 checklist

- iperf3 server 종료
- Windows Firewall 임시 rule 제거
- Linux firewall 임시 rule 제거
- 테스트 bandwidth와 시간을 기록
- client·server 결과를 함께 보관
- 운영 트래픽 영향이 없었는지 확인

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- iperf3 공식 저장소: [github.com/esnet/iperf](https://github.com/esnet/iperf) — ★★★☆☆
- iperf3 Manual: [software.es.net/iperf](https://software.es.net/iperf/) — ★★★☆☆
- Windows Firewall cmdlets: [learn.microsoft.com/powershell/module/netsecurity](https://learn.microsoft.com/powershell/module/netsecurity/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-28

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.
