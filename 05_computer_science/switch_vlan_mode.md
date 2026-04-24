# Switch VLAN Mode (Access / Trunk / Dynamic)

스위치 포트의 VLAN 모드는 프레임이 포트를 통과할 때 VLAN 태그를 어떻게 처리하는지를 결정합니다.

## 목차

| 단계       | 섹션                                                                                              |
|------------|---------------------------------------------------------------------------------------------------|
| 기본       | [1. Access Mode](#1-access-mode) / [2. Trunk Mode](#2-trunk-mode)                                 |
| 고급       | [3. Dynamic Mode](#3-dynamic-mode) / [4. Voice VLAN](#4-voice-vlan)                               |
| 보안       | [5. Private VLAN](#5-private-vlan) / [6. VLAN Hopping 공격과 방어](#6-vlan-hopping-공격과-방어)    |
| 비교       | [7. ISL vs 802.1Q](#7-isl-vs-8021q) / [8. 모드 비교 요약](#8-모드-비교-요약)                      |
| 운영       | [9. 트러블슈팅 명령어](#9-트러블슈팅-명령어) / [10. 실무 Tip](#10-실무-tip)                        |
| 권장       | [11. 운영 권장 사항](#11-운영-권장-사항)                                                           |

---

## 1. Access Mode

### 개요

하나의 VLAN에만 소속되는 포트 모드. 주로 PC, 프린터 등 엔드 디바이스를 연결할 때 사용합니다.

### 동작 방식

```
[PC] --(untagged)--> [Switch Port (Access VLAN 10)]
                          |
                          +-- RX: untagged frame --> classify to VLAN 10
                          +-- TX: strip VLAN 10 tag --> send untagged
```

- 수신 시: 태그가 없는 프레임을 해당 포트에 설정된 VLAN으로 분류
- 송신 시: VLAN 태그를 제거(untag)하여 전송
- 해당 포트는 하나의 VLAN 트래픽만 전달

### 설정 — Cisco IOS

```
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
```

### 특징

| 항목        | 설명                                |
|-------------|-------------------------------------|
| VLAN 수     | 1개                                 |
| 태그 처리   | 수신: 태그 추가 / 송신: 태그 제거   |
| 연결 대상   | PC, 서버, 프린터 등 엔드 디바이스   |
| DTP 협상    | 비활성                              |
| 보안        | 단일 VLAN이므로 상대적으로 안전     |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Trunk Mode

### 개요

여러 VLAN의 트래픽을 하나의 링크로 전달하는 포트 모드. 스위치 간 연결, 스위치-라우터 간 연결에 사용합니다.

### 동작 방식

```
[Switch A] --(tagged: VLAN 10,20,30)--> [Switch B]
                |
                +-- VLAN 10 frame --> 802.1Q tag (VID: 10)
                +-- VLAN 20 frame --> 802.1Q tag (VID: 20)
                +-- Native VLAN frame --> send untagged
```

- 802.1Q 태그를 사용하여 VLAN 식별
- Native VLAN 트래픽은 태그 없이(untagged) 전송
- 허용된 VLAN만 통과 가능 (`allowed vlan` 설정)

### 802.1Q 프레임 구조

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────────────────────────────────────┐
│                     Destination MAC (48bit)                   │
├───────────────────────────────────────────────────────────────┤
│                       Source MAC (48bit)                      │
├───────────────────────────────┬───────────────────────────────┤
│     TPID (0x8100, 16bit)      │     TCI (16bit)               │
│                               │  PCP(3) + DEI(1) + VID(12)    │
├───────────────────────────────┴───────────────────────────────┤
│                     EtherType / Length                        │
├───────────────────────────────────────────────────────────────┤
│                          Payload                              │
└───────────────────────────────────────────────────────────────┘
```

| 필드   | 크기    | 설명                                       |
|--------|---------|--------------------------------------------| 
| TPID   | 2byte   | `0x8100` (802.1Q 식별자)                   |
| TCI    | 2byte   | PCP(3bit) + DEI(1bit) + VID(12bit)         |
| VID    | 12bit   | VLAN ID (0~4095, 유효: 1~4094)             |

### 설정 — Cisco IOS

```
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30
```

### 특징

| 항목        | 설명                                              |
|-------------|---------------------------------------------------|
| VLAN 수     | 여러 개 (최대 4094)                               |
| 태그 처리   | 802.1Q 태그 추가/제거                             |
| Native VLAN | 태그 없이 전송되는 VLAN (기본: VLAN 1)            |
| 연결 대상   | 스위치 간, 스위치-라우터, 스위치-가상화 호스트    |
| DTP 협상    | 기본 활성 (desirable)                             |

### Native VLAN 주의사항

⚠️ 양쪽 스위치의 Native VLAN이 불일치하면 트래픽이 잘못된 VLAN으로 전달될 수 있습니다.

```
Switch A (native vlan 1) ---- Switch B (native vlan 99)
  --> VLAN mismatch --> security risk (VLAN Hopping attack)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Dynamic Mode

### 개요

DTP(Dynamic Trunking Protocol)를 사용하여 상대 포트와 자동 협상으로 Access 또는 Trunk를 결정하는 모드.

### `dynamic desirable` — 적극적 Trunk 협상

- 적극적으로 Trunk 협상을 시도
- 상대가 Trunk, Desirable, Auto이면 Trunk 성립

```
interface FastEthernet0/1
 switchport mode dynamic desirable
```

### `dynamic auto` — 수동 대기

- 수동적으로 대기, 상대가 요청하면 Trunk 수락
- 상대가 Trunk 또는 Desirable이면 Trunk 성립
- 상대가 Auto이면 양쪽 다 수동이므로 Access로 동작

```
interface FastEthernet0/1
 switchport mode dynamic auto
```

### DTP 협상 결과 매트릭스

| 구분            | Access   | Trunk    | Desirable | Auto     |
|-----------------|:--------:|:--------:|:---------:|:--------:|
| **Access**      | Access   | ❌       | Access    | Access   |
| **Trunk**       | ❌       | Trunk    | Trunk     | Trunk    |
| **Desirable**   | Access   | Trunk    | Trunk     | Trunk    |
| **Auto**        | Access   | Trunk    | Trunk     | Access   |

- ❌ = 불일치로 인한 오류 발생 가능

### DTP 비활성화

보안상 DTP를 비활성화하는 것이 권장됩니다.

Access 고정:

```
interface FastEthernet0/1
 switchport mode access
 switchport nonegotiate
```

Trunk 고정:

```
interface GigabitEthernet0/1
 switchport mode trunk
 switchport nonegotiate
```

### 특징

| 항목            | 설명                                        |
|-----------------|---------------------------------------------|
| 프로토콜        | DTP (Dynamic Trunking Protocol)             |
| 보안            | ⚠️ DTP 악용 가능 → 비활성화 권장             |
| 사용 환경       | 소규모 네트워크, 테스트 환경                 |
| 운영 환경 권장  | ❌ 명시적으로 Access/Trunk 지정 권장          |

[⬆ 목차로 돌아가기](#목차)

---

## 4. Voice VLAN

### 개요

IP 전화기(IP Phone)를 연결할 때 데이터 VLAN과 음성 VLAN을 분리하는 기능. Access 포트에서 추가로 설정합니다.

### 동작 방식

```
                          +-- Data VLAN 10 (untagged) --> PC traffic
[PC] -- [IP Phone] -- [Switch Port]
                          +-- Voice VLAN 50 (tagged)  --> voice traffic (802.1Q, CoS)
```

- PC 트래픽: Data VLAN (untagged)
- 음성 트래픽: Voice VLAN (802.1Q 태그 + CoS 값 부여)
- IP Phone이 미니 스위치 역할을 하여 PC와 스위치 사이에 위치

### 설정 — Cisco IOS

```
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 50
```

### Voice VLAN 옵션

| 설정                        | 동작                                          |
|-----------------------------|-----------------------------------------------|
| `switchport voice vlan 50`  | VLAN 50을 음성 VLAN으로 지정 (802.1Q 태그)    |
| `switchport voice vlan dot1p` | 태그는 하지만 VLAN 0 사용 (우선순위만 부여)  |
| `switchport voice vlan untagged` | 음성도 태그 없이 전송                     |
| `switchport voice vlan none` | Voice VLAN 비활성화                           |

### 특징

| 항목        | 설명                                              |
|-------------|---------------------------------------------------|
| QoS         | CoS(Class of Service) 값으로 음성 트래픽 우선 처리 |
| 보안        | 데이터/음성 트래픽 분리로 보안 강화                |
| 전제 조건   | IP Phone이 CDP/LLDP를 지원해야 VLAN 정보 수신     |

[⬆ 목차로 돌아가기](#목차)

---

## 5. Private VLAN

### 개요

하나의 VLAN 내에서 포트 간 통신을 제한하는 기능. 같은 서브넷에 있지만 호스트 간 직접 통신을 차단할 때 사용합니다.

### 구조

```
┌─────────────────────────────────────────────┐
│              Primary VLAN 100               │
│                                             │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Isolated     │  │ Community            │ │
│  │ VLAN 101     │  │ VLAN 102             │ │
│  │              │  │                      │ │
│  │ Host A  X    │  │ Host C <---> Host D  │ │
│  │ Host B  X    │  │ (same community OK)  │ │
│  │ (no L2 talk) │  │                      │ │
│  └──────────────┘  └──────────────────────┘ │
│                      |                      │
│              ┌───────────────┐              │
│              │  Promiscuous  │              │
│              │  (Gateway)    │              │
│              │  all can talk │              │
│              └───────────────┘              │
└─────────────────────────────────────────────┘
```

### 포트 유형

| 유형          | 통신 가능 대상                                |
|---------------|-----------------------------------------------|
| Promiscuous   | 모든 포트와 통신 가능 (게이트웨이, 라우터)    |
| Isolated      | Promiscuous 포트만 통신 가능 (호스트 간 차단) |
| Community     | 같은 Community + Promiscuous 포트와 통신 가능 |

### 설정 — Cisco IOS

```
! Primary VLAN
vlan 100
 private-vlan primary

! Secondary VLAN (Isolated)
vlan 101
 private-vlan isolated

! Secondary VLAN (Community)
vlan 102
 private-vlan community

! Primary-Secondary 매핑
vlan 100
 private-vlan association 101,102

! Promiscuous 포트 (게이트웨이)
interface GigabitEthernet0/1
 switchport mode private-vlan promiscuous
 switchport private-vlan mapping 100 101,102

! Isolated 포트
interface FastEthernet0/10
 switchport mode private-vlan host
 switchport private-vlan host-association 100 101

! Community 포트
interface FastEthernet0/20
 switchport mode private-vlan host
 switchport private-vlan host-association 100 102
```

### 사용 사례

| 환경                  | 용도                                          |
|-----------------------|-----------------------------------------------|
| IDC / 호스팅          | 고객 간 L2 격리 (같은 서브넷 공유)            |
| DMZ                   | 서버 간 불필요한 통신 차단                    |
| 호텔/공용 Wi-Fi       | 사용자 간 직접 통신 방지                      |

[⬆ 목차로 돌아가기](#목차)

---

## 6. VLAN Hopping 공격과 방어

### 공격 기법 1 — Switch Spoofing

공격자가 DTP 패킷을 전송하여 스위치와 Trunk를 형성, 모든 VLAN 트래픽을 수신합니다.

```
[Attacker] --(DTP desirable)--> [Switch]
                                    |
                              Trunk formed!
                              All VLANs exposed
```

방어:

```
interface FastEthernet0/1
 switchport mode access
 switchport nonegotiate
```

### 공격 기법 2 — Double Tagging

Native VLAN이 기본값(VLAN 1)일 때, 이중 802.1Q 태그를 삽입하여 다른 VLAN으로 프레임을 전달합니다.

```
[Attacker VLAN 1]
    |
    +-- Frame: [Outer Tag: VLAN 1][Inner Tag: VLAN 20][Data]
    |
[Switch A] strips outer tag (native VLAN, untagged)
    |
    +-- Frame: [Tag: VLAN 20][Data]  --> forwarded as VLAN 20
    |
[Switch B] delivers to VLAN 20
```

- 단방향 공격 (응답은 돌아오지 않음)
- Native VLAN이 VLAN 1일 때만 가능

방어:

```
! Native VLAN을 사용하지 않는 VLAN으로 변경
switchport trunk native vlan 999

! Native VLAN에도 태그 강제
vlan dot1q tag native
```

### 방어 체크리스트

| 방어 항목                                  | 명령어                                |
|--------------------------------------------|---------------------------------------|
| DTP 비활성화                               | `switchport nonegotiate`              |
| 미사용 포트 Access 고정                    | `switchport mode access`              |
| Native VLAN 변경                           | `switchport trunk native vlan 999`    |
| Native VLAN 태그 강제                      | `vlan dot1q tag native`               |
| 허용 VLAN 제한                             | `switchport trunk allowed vlan ...`   |
| 미사용 포트 shutdown                       | `shutdown`                            |

[⬆ 목차로 돌아가기](#목차)

---

## 7. ISL vs 802.1Q

### 비교

| 항목            | ISL (Inter-Switch Link)        | 802.1Q                         |
|-----------------|--------------------------------|--------------------------------|
| 표준            | Cisco 독자 규격                | IEEE 표준                      |
| 캡슐화          | 전체 프레임을 새 헤더로 감싸기 | 기존 프레임에 4byte 태그 삽입  |
| 오버헤드         | 26byte (헤더) + 4byte (FCS)   | 4byte                          |
| Native VLAN     | 지원하지 않음                  | 지원 (untagged 전송)           |
| 현재 상태       | ❌ 단종 (EOL)                  | ✅ 업계 표준                    |
| 지원 장비       | 구형 Cisco 장비만              | 모든 벤더                      |

### ISL 프레임 구조

```
+------------+------------------+----------+
| ISL Header | Original Frame   | ISL FCS  |
| (26 byte)  | (encapsulated)   | (4 byte) |
+------------+------------------+----------+
```

### 결론

ISL은 현재 거의 사용하지 않으며, 신규 환경에서는 802.1Q만 사용합니다. 구형 장비 마이그레이션 시에만 참고.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 모드 비교 요약

| 항목            | Access          | Trunk                | Dynamic              |
|-----------------|:---------------:|:--------------------:|:--------------------:|
| VLAN 수         | 1개             | 여러 개              | 협상 결과에 따름     |
| 태그            | Untagged        | Tagged (802.1Q)      | 협상 결과에 따름     |
| 연결 대상       | 엔드 디바이스   | 스위치/라우터        | 자동 판단            |
| DTP             | 비활성          | 기본 활성            | 활성                 |
| 보안            | 🟢              | 🟡 Native VLAN 주의  | 🔴 DTP 악용 가능     |
| 운영 환경 권장  | ✅              | ✅                   | ❌                   |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅 명령어

### 기본 확인

| 명령어                                    | 용도                                    |
|-------------------------------------------|-----------------------------------------|
| `show vlan brief`                         | 전체 VLAN 목록 및 포트 할당 확인        |
| `show interfaces trunk`                   | Trunk 포트 상태, 허용 VLAN, Native VLAN |
| `show interfaces switchport`              | 특정 포트의 모드, VLAN 설정 상세        |
| `show interfaces fa0/1 switchport`        | 특정 포트 지정 확인                     |
| `show dtp interface fa0/1`                | DTP 협상 상태 확인                      |

### VLAN 통신 문제

| 명령어                                    | 용도                                    |
|-------------------------------------------|-----------------------------------------|
| `show mac address-table vlan 10`          | 특정 VLAN의 MAC 테이블 확인             |
| `show spanning-tree vlan 10`              | STP 상태 확인 (포트 blocking 여부)      |
| `show interfaces status`                  | 포트 상태 (up/down, speed, duplex)      |
| `show vlan id 10`                         | 특정 VLAN 상세 정보                     |

### Private VLAN 확인

| 명령어                                    | 용도                                    |
|-------------------------------------------|-----------------------------------------|
| `show vlan private-vlan`                  | PVLAN 매핑 확인                         |
| `show interfaces private-vlan mapping`    | 포트별 PVLAN 매핑 상태                  |

### 실행 예시

```
Switch# show interfaces fa0/1 switchport
Name: Fa0/1
Switchport: Enabled
Administrative Mode: access
Operational Mode: access
Administrative Trunking Encapsulation: negotiate
Negotiation of Trunking: Off
Access Mode VLAN: 10 (DATA)
Trunking Native Mode VLAN: 1 (default)
Voice VLAN: 50 (VOICE)
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 실무 Tip

### Tip 1 — Trunk 허용 VLAN은 최소한으로

```
! BAD: 모든 VLAN 허용 (기본값)
switchport trunk allowed vlan all

! GOOD: 필요한 VLAN만 명시
switchport trunk allowed vlan 10,20,30
```

불필요한 VLAN 트래픽이 Trunk를 통과하면 대역폭 낭비 + 보안 위험.

### Tip 2 — Native VLAN은 반드시 변경

```
! 양쪽 스위치 모두 동일하게 설정
switchport trunk native vlan 999
```

VLAN 1을 Native VLAN으로 사용하면 Double Tagging 공격에 취약합니다.

### Tip 3 — 미사용 포트는 반드시 shutdown

```
interface range FastEthernet0/20-24
 switchport mode access
 switchport access vlan 999
 switchport nonegotiate
 shutdown
```

미사용 포트를 열어두면 물리적 접근만으로 네트워크 침입이 가능합니다.

### Tip 4 — VLAN 설계 시 번호 체계를 정해두기

| 범위        | 용도                    |
|-------------|-------------------------|
| 1           | 사용하지 않음 (기본값)  |
| 10~99       | 데이터 VLAN             |
| 100~199     | 서버 VLAN               |
| 200~299     | 음성 VLAN               |
| 900~999     | 관리/미사용 VLAN        |

### Tip 5 — Trunk 설정 후 반드시 양쪽 확인

```
! 양쪽 스위치에서 각각 실행
show interfaces trunk
```

한쪽만 Trunk이고 반대쪽이 Access이면 통신 장애가 발생합니다. Native VLAN 불일치도 CDP/로그에서 경고가 나오므로 확인할 것.

### Tip 6 — VTP 모드를 Transparent로 설정

```
vtp mode transparent
```

VTP Server/Client 모드에서 실수로 VLAN DB가 전파되어 전체 네트워크 VLAN이 삭제되는 사고를 방지합니다. 대규모 환경에서는 VTP를 사용하지 않거나 Transparent 모드를 권장.

### Tip 7 — 변경 전 현재 설정 백업

```
show running-config | section interface
```

VLAN/포트 변경 전 현재 설정을 저장해두면 롤백이 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 운영 권장 사항

1. 모든 포트에 명시적으로 Access 또는 Trunk 설정
2. 사용하지 않는 포트는 shutdown + Access 모드로 설정
3. `switchport nonegotiate`로 DTP 비활성화
4. Native VLAN은 기본 VLAN 1이 아닌 별도 VLAN 사용
5. Trunk에서 `allowed vlan`으로 필요한 VLAN만 허용
6. VTP는 Transparent 모드 또는 비활성화
7. VLAN 번호 체계를 사전에 정의하고 문서화

```
! unused port security example
interface range FastEthernet0/20-24
 switchport mode access
 switchport access vlan 999
 switchport nonegotiate
 shutdown
```

[⬆ 목차로 돌아가기](#목차)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---
**작성일**: 2026-04-24

**마지막 업데이트**: 2026-04-24

© 2026 siasia86. Licensed under CC BY 4.0.
