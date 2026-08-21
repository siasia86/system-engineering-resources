# 게임 서버 아키텍처 유형

게임 서비스의 서버 운영 방식을 유형별로 분류합니다.
각 방식의 구조, 장단점, 대표 게임 사례를 정리합니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Dedicated Server](#2-dedicated-server) / [3. Listen Server](#3-listen-server) |
| [4. P2P](#4-p2p) / [5. Hybrid](#5-hybrid) / [6. 유형 비교](#6-유형-비교)                               |
| [7. 핵심 지표](#7-핵심-지표) / [8. 클라우드 인프라](#8-클라우드-인프라)                                |

---

## 1. 개요

### 서버 유형 분류 기준

게임 서버 운영 방식은 **게임 로직을 어디서 처리하느냐**에 따라 분류합니다.

```
Dedicated Server   — 별도 서버 머신이 게임 로직 전담
Listen Server      — 플레이어 중 한 명의 PC가 서버 역할
P2P                — 모든 플레이어가 동등하게 연결, 서버 없음
Hybrid             — 위 방식을 혼합
```

### 서버 유형 선택 기준

| 요소           | 영향                                             |
|----------------|--------------------------------------------------|
| 플레이어 수    | 대규모(50명+)는 Dedicated 필수                   |
| 경쟁/랭크 여부 | 핵 방지 필요 시 Dedicated 필수                   |
| 비용           | Dedicated가 가장 비쌈, P2P가 가장 저렴           |
| 지연시간 (핑)  | Dedicated 서버 위치가 핑에 직접 영향             |
| 개발 복잡도    | P2P가 구현 복잡, Dedicated가 서버 측에 로직 집중 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Dedicated Server

### 개념

게임사 또는 커뮤니티가 **독립된 서버 머신**을 운영합니다.
플레이어 PC는 입력만 전송하고 게임 로직은 서버에서 처리합니다.

```
플레이어 A ─┐
플레이어 B ─┤──→ Dedicated Server
플레이어 C ─┤       └─→ 게임 로직 처리
플레이어 D ─┤       └─→ 충돌/판정
플레이어 E ─┘       └─→ 전체 동기화

플레이어 PC = 입력 전송 + 화면 렌더링만 담당
```

### 장단점

| 항목 | 내용                                             |
|------|--------------------------------------------------|
| 장점 | 핵/치트 방지 용이, 안정적 판정, 대규모 동시 접속 |
| 장점 | 특정 플레이어 이탈 시에도 서버 유지              |
| 단점 | 서버 운영 비용 발생                              |
| 단점 | 서버 위치에 따른 핑 불균형                       |
| 단점 | 서버 장애 시 전체 서비스 영향                    |

### 틱레이트 (Tick Rate)

서버가 초당 게임 상태를 업데이트하는 횟수입니다.

| 게임     | 틱레이트 | 특징                              |
|----------|----------|-----------------------------------|
| Valorant | 128 tick | FPS 중 높은 수준                  |
| CS2      | Subtick  | CS2 전용 방식, 64/128 개념과 다름 |
| PUBG     | 30 tick  | 배틀로얄 기준 일반적              |
| Fortnite | 30 tick  | 배틀로얄 기준 일반적              |
| LoL      | 30 tick  | MOBA 장르 기준 충분               |

> 틱레이트가 높을수록 서버가 초당 더 자주 상태를 동기화합니다. 빠른 교전이 많은 FPS에서 중요하며, 높을수록 서버 부하와 비용이 증가합니다.

### 대표 게임

| 게임        | 장르         | 서버 인프라           |
|-------------|--------------|-----------------------|
| LoL         | MOBA         | AWS (지역별 서버)     |
| PUBG        | 배틀로얄 FPS | Microsoft Azure       |
| Fortnite    | 배틀로얄     | AWS                   |
| Valorant    | 전술 FPS     | Riot 직접 운영        |
| CS2         | FPS          | Valve + 커뮤니티 병행 |
| Overwatch 2 | FPS          | Blizzard 운영         |
| FIFA Online | 스포츠       | EA 서버               |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Listen Server

### 개념

플레이어 중 **한 명이 호스트(서버) 역할**을 겸합니다.
해당 PC가 서버이자 클라이언트로 동작합니다.

```
호스트 PC (서버 + 플레이어 A)
     │
     ├──→ 플레이어 B
     ├──→ 플레이어 C
     └──→ 플레이어 D

호스트가 방을 닫으면 서버도 종료
```

### 장단점

| 항목 | 내용                                     |
|------|------------------------------------------|
| 장점 | 별도 서버 비용 없음, 구성 간단           |
| 장점 | 호스트가 방을 만들면 즉시 플레이 가능    |
| 단점 | 호스트 이탈 시 게임 종료                 |
| 단점 | 호스트에게 유리한 핑 (Host Advantage)    |
| 단점 | 호스트 PC 성능/네트워크에 게임 품질 종속 |
| 단점 | 경쟁 환경에 부적합 (공정성 문제)         |

### 대표 게임

| 게임           | 장르      | 비고                            |
|----------------|-----------|---------------------------------|
| Minecraft      | 샌드박스  | 서버 앱 별도 실행 또는 Listen   |
| Terraria       | 샌드박스  | 호스트 PC가 서버                |
| 초기 Diablo II | 액션 RPG  | Battle.net 로비 + Listen Server |
| Left 4 Dead 2  | Co-op FPS | Listen Server 기본              |
| 초기 Halo      | FPS       | Xbox LAN / Listen Server        |

[⬆ 목차로 돌아가기](#목차)

---

## 4. P2P

### 개념

중앙 서버 없이 **모든 플레이어가 직접 연결**합니다.
각 클라이언트가 게임 상태를 서로에게 전달합니다.

```
플레이어 A ←──→ 플레이어 B
     ↑                ↑
     └────→ 플레이어 C ┘

중앙 서버 없음 — 플레이어끼리 직접 통신
```

### P2P 동기화 방식

| 방식                      | 설명                                           |
|---------------------------|------------------------------------------------|
| **State Synchronization** | 전체 게임 상태를 주기적으로 모든 피어에 전송   |
| **Lockstep**              | 모든 피어가 동일한 입력을 동일한 프레임에 실행 |

> Lockstep: 모든 클라이언트가 동일한 시뮬레이션을 돌리고, 입력값만 교환합니다. 한 명이 지연되면 전체가 대기하는 구조입니다. 스타크래프트 초기 구조가 대표적입니다.

### 장단점

| 항목 | 내용                                          |
|------|-----------------------------------------------|
| 장점 | 서버 운영 비용 없음                           |
| 장점 | 서버 없이 즉시 플레이 가능                    |
| 단점 | 핵/치트 방지 매우 어려움                      |
| 단점 | 플레이어 수 증가 시 연결 복잡도 급증          |
| 단점 | 한 명의 높은 핑이 전체에 영향 (Lockstep 방식) |
| 단점 | 공정한 판정 보장 어려움                       |

### 대표 게임

| 게임                 | 장르   | 비고              |
|----------------------|--------|-------------------|
| 스타크래프트 1       | RTS    | Lockstep P2P      |
| 워크래프트 3         | RTS    | Lockstep P2P      |
| 초기 FIFA (오프라인) | 스포츠 | 콘솔 로컬 P2P     |
| 철권 시리즈 (온라인) | 격투   | P2P + 롤백 넷코드 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. Hybrid

### 개념

Dedicated Server + P2P 또는 Listen Server를 **상황에 따라 혼합**합니다.

### 대표 패턴

```
패턴 A — 로비는 Dedicated, 게임 중은 P2P
  Dedicated Server (로그인, 매칭, 랭킹)
         │
         └─→ 게임 시작 후 P2P로 전환

패턴 B — 중요 데이터는 Dedicated, 부가 데이터는 P2P
  Dedicated Server (점수, 아이템, 인증)
  P2P (음성 채팅, 부가 데이터)

패턴 C — 롤백 넷코드 + P2P (격투 게임)
  P2P 연결 + 예측/롤백으로 지연 보완
```

### 롤백 넷코드 (Rollback Netcode)

격투 게임 등 소수 인원 P2P에서 핑 문제를 해결하는 기술입니다.

| 항목      | 내용                                                  |
|-----------|-------------------------------------------------------|
| 원리      | 상대 입력을 예측 실행 → 실제 입력 수신 시 불일치 롤백 |
| 장점      | 높은 핑에서도 반응성 유지                             |
| 단점      | 롤백 순간 화면 끊김 현상 발생 가능                    |
| 대표 게임 | 길티기어 스트라이브, 킹오파 XV, 스트리트파이터 6      |

### 대표 게임

| 게임                | 방식                                 |
|---------------------|--------------------------------------|
| GTA Online          | P2P 기반 + Rockstar 서버 (인증/DB)   |
| 다크소울 시리즈     | P2P 침입/협력 + Fromsoft 서버 (매칭) |
| 길티기어 스트라이브 | P2P + 롤백 넷코드                    |
| 초기 COD 시리즈     | Dedicated + Listen Server 혼용       |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 유형 비교

### 전체 비교표

| 항목             | Dedicated      | Listen Server  | P2P           | Hybrid         |
|------------------|----------------|----------------|---------------|----------------|
| 게임 로직 처리   | 전용 서버      | 호스트 PC      | 각 클라이언트 | 혼합           |
| 서버 비용        | 높음           | 없음           | 없음          | 중간           |
| 핵 방지          | ✅ 용이        | 🟡 제한적      | ❌ 어려움     | 🟡 부분적      |
| 대규모 동시접속  | ✅ 가능        | ❌ 어려움      | ❌ 어려움     | 🟡 제한적      |
| 공정성           | ✅ 높음        | 🟡 호스트 유리 | ❌ 낮음       | 🟡 부분적      |
| 호스트 이탈 영향 | 없음           | 서버 종료      | 재연결 필요   | 상황별 상이    |
| 개발 복잡도      | 중간           | 낮음           | 높음          | 높음           |
| 대표 장르        | FPS, MOBA, MMO | 협동/인디      | RTS, 격투     | 오픈월드, 격투 |

### 장르별 권장 방식

| 장르       | 권장 방식         | 이유                              |
|------------|-------------------|-----------------------------------|
| 경쟁 FPS   | Dedicated         | 핵 방지, 높은 틱레이트 필요       |
| 배틀로얄   | Dedicated         | 100명+ 동시 처리                  |
| MOBA       | Dedicated         | 랭크 환경, 공정한 판정            |
| MMO        | Dedicated         | 수천 명 동시 접속, 영속적 세계    |
| Co-op 인디 | Listen Server     | 소수 인원, 비용 절감              |
| 격투 게임  | P2P + 롤백 넷코드 | 소수 인원, 저지연 반응성          |
| RTS        | P2P Lockstep      | 동일 시뮬레이션 보장              |
| 오픈월드   | Hybrid            | 인증/DB는 서버, 일부 동기화는 P2P |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 핵심 지표

### 지연시간 관련 개념

| 용어                      | 설명                                     |
|---------------------------|------------------------------------------|
| **RTT (Round Trip Time)** | 클라이언트 → 서버 → 클라이언트 왕복 시간 |
| **핑 (Ping)**             | RTT의 절반 (단방향 지연시간 추정값)      |
| **틱레이트**              | 서버가 초당 상태를 업데이트하는 횟수     |
| **지터 (Jitter)**         | 패킷 지연시간의 변동폭                   |
| **패킷 로스**             | 전송 중 손실된 패킷 비율                 |

### 핑 기준 체감 품질

| 핑 범위   | 체감                            |
|-----------|---------------------------------|
| 0~30ms    | 매우 쾌적                       |
| 30~60ms   | 쾌적 (대부분 장르 지장 없음)    |
| 60~100ms  | 보통 (FPS에서 불리함 체감 시작) |
| 100~150ms | 불편 (격투/FPS에서 명확히 불리) |
| 150ms+    | 심각 (경쟁 게임 사실상 불가)    |

### Host Migration

Listen Server에서 호스트가 이탈했을 때 다른 플레이어가 서버를 이어받는 기능입니다.

```
호스트 이탈 감지
      │
      v
  후보 선정 (핑·안정성 기준)
      │
      v
  게임 상태 전달 → 새 호스트 지정
      │
      v
  나머지 플레이어 재연결
```

COD 시리즈, Halo 시리즈 등에서 구현된 기술입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 클라우드 인프라

### 주요 게임사 클라우드 현황

| 게임사     | 클라우드        | 주요 게임                 |
|------------|-----------------|---------------------------|
| Riot Games | AWS             | LoL, Valorant             |
| PUBG Corp  | Microsoft Azure | PUBG                      |
| Epic Games | AWS             | Fortnite                  |
| Blizzard   | 자체 + AWS      | Overwatch 2, WoW          |
| EA         | AWS + Azure     | FIFA Online, Apex Legends |
| Rockstar   | 자체 서버       | GTA Online                |

### 게임 서버 전용 클라우드 서비스

| 서비스                        | 제공사    | 특징                              |
|-------------------------------|-----------|-----------------------------------|
| **GameLift**                  | AWS       | Dedicated Server 관리형 서비스    |
| **PlayFab**                   | Microsoft | 게임 백엔드 통합 (매칭, 랭킹, DB) |
| **Game Servers (GKE/Agones)** | GCP       | Agones 기반 컨테이너 게임 서버    |
| **Multiplay**                 | Unity     | Dedicated Server 호스팅           |

### AWS GameLift 구조

```
Player Client
      │
      v
  GameLift FlexMatch (matching)
      │
      v
  GameLift Fleet (EC2 instances)
      │
      ├─→ Game Session (per room)
      └─→ Player Session (per player)
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Valve Developer Community: [developer.valvesoftware.com](https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking) — ★★★☆☆
- AWS GameLift: [docs.aws.amazon.com/gamelift](https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-intro.html) — ★★★☆☆
- Riot Engineering Blog: [technology.riotgames.com](https://technology.riotgames.com/) — ★★☆☆☆
- Gabriel Gambetta. "Fast-Paced Multiplayer" — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-21

**마지막 업데이트**: 2026-08-21

© 2026 siasia86. Licensed under CC BY 4.0.
