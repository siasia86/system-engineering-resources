# Grafana — GitLab Contribution Heatmap

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 사전 준비](#2-사전-준비) / [3. Infinity Datasource 설정](#3-infinity-datasource-설정) |
| [4. 패널 쿼리 설정](#4-패널-쿼리-설정) / [5. Heatmap 패널 구성](#5-heatmap-패널-구성) / [6. 그룹별 분리](#6-그룹별-분리) |
| [7. Tips](#7-tips) |

---

## 1. 개요

Grafana OSS(무료)와 Infinity Datasource 플러그인을 사용하여 GitLab 커밋 기여도를 Heatmap(잔디)으로 시각화합니다. 별도 exporter나 중간 저장소 없이 GitLab API를 직접 조회합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  GitLab API ──> Infinity Datasource ──> Grafana Heatmap     │
│                                                             │
│  /groups/<id>/events       그룹 전체 커밋 이벤트            │
│  /projects/<id>/commits    프로젝트별 커밋                  │
└─────────────────────────────────────────────────────────────┘
```

| 항목       | 내용                                          |
|------------|-----------------------------------------------|
| Grafana    | OSS (무료)                                    |
| 플러그인   | yesoreyeram-infinity-datasource               |
| Enterprise | 불필요                                        |
| 인증       | GitLab Admin Personal Access Token (read_api) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사전 준비

### Infinity 플러그인 설치

```bash
grafana-cli plugins install yesoreyeram-infinity-datasource
sudo systemctl restart grafana-server
```

### GitLab Admin Access Token 발급

전체 사용자/프로젝트 이벤트 조회는 **admin 계정 토큰**이 필요합니다. 일반 토큰은 본인 이벤트만 반환합니다.

**웹 UI에서 발급:**
```
GitLab admin 계정으로 로그인
→ 우측 상단 프로필 아이콘 → Edit profile
→ Access Tokens → Add new token
  - Token name: grafana-readonly
  - Scopes: read_api
→ Create personal access token
→ 토큰 값 복사 (페이지 벗어나면 재확인 불가)
```

**Rails console에서 발급 (서버 직접 접근 시):**
```bash
sudo gitlab-rails console

# Rails console 내
user = User.find_by_username('root')
token = user.personal_access_tokens.create(
  name: 'grafana-readonly',
  scopes: ['read_api'],
  expires_at: 1.year.from_now
)
puts token.token
```

### API 동작 확인

```bash
# 토큰 유효성 확인
curl -s --header "PRIVATE-TOKEN: <token>" \
  https://gitlab.example.com/api/v4/user

# 그룹 목록 및 ID 확인
curl -s --header "PRIVATE-TOKEN: <token>" \
  https://gitlab.example.com/api/v4/groups

# 그룹 내 프로젝트 확인
curl -s --header "PRIVATE-TOKEN: <token>" \
  "https://gitlab.example.com/api/v4/groups/<group_id>/projects"
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Infinity Datasource 설정

`Configuration` → `Data Sources` → `Add` → `Infinity`

| 항목      | 값                                      |
|-----------|-----------------------------------------|
| Base URL  | `https://gitlab.example.com/api/v4`     |
| Auth Type | `API Key`                               |
| Key       | `PRIVATE-TOKEN`                         |
| Value     | `<your-token>`                          |
| Add to    | `Header`                                |

⚠️ Base URL은 회사 GitLab 도메인으로 변경합니다. `http://` → `https://` 확인 필수.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 패널 쿼리 설정

### 전체 사용자 커밋 이벤트 (admin 토큰 필요)

패널 추가 → Datasource: `Infinity` 선택

| 항목    | 값 |
|---------|----|
| Type    | `JSON` |
| Method  | `GET` |
| URL     | `https://gitlab.example.com/api/v4/events?action=pushed&per_page=100` |

Headers 탭:
```
Key:   PRIVATE-TOKEN
Value: <admin-token>
```

Columns 탭:
```
created_at      → string → date
author.name     → string → author
author.username → string → username
id              → string → event_id
project_id      → string → project_id
```

### 범위별 API 엔드포인트

| 범위           | 엔드포인트                                                    | 권한        |
|----------------|---------------------------------------------------------------|-------------|
| 전체 사용자    | `/api/v4/events?action=pushed`                                | admin 전용  |
| 특정 사용자    | `/api/v4/users/<user_id>/events?action=pushed`                | read_api    |
| 특정 그룹      | `/api/v4/groups/<group_id>/events?action=pushed`              | read_api    |
| 특정 프로젝트  | `/api/v4/projects/<project_id>/events?action=pushed`          | read_api    |

### Computed columns / Filter / Group by

| 기능              | 용도                                              | 잔디 필요 여부 |
|-------------------|---------------------------------------------------|----------------|
| Computed columns  | API 응답에 없는 컬럼을 수식으로 생성              | 선택 (날짜 파싱용) |
| Filter            | 특정 조건으로 데이터 필터링 (작성자, 날짜 등)     | 선택           |
| Group by          | 날짜별 커밋 수 집계 — **Heatmap 핵심 설정**       | ✅ 필수        |

**Group by 설정:**

```
Field: created_at   → Group by
Field: id           → Count
```

결과:
```
date        | count
2026-05-01  | 3
2026-05-02  | 7
2026-05-13  | 2
```

**Transform 탭 추가 설정:**

1. `Group by` → `created_at`: Group by / `id`: Count
2. `Convert field type` → `created_at` → Time

[⬆ 목차로 돌아가기](#목차)

---

## 5. Heatmap 패널 구성

패널 타입 → **Heatmap** 선택

| 항목      | 값                    |
|-----------|-----------------------|
| X축       | `date` (created_at)   |
| Y축       | `count` (커밋 수)     |
| Color     | 커밋 밀도 (자동)      |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 그룹별 분리

쿼리를 여러 개 추가하여 그룹/사용자별로 분리합니다.

```
# 그룹별
Query A: /api/v4/groups/10/events?action=pushed   → team-a
Query B: /api/v4/groups/20/events?action=pushed   → team-b

# 사용자별 (전체 이벤트에서 Filter 활용)
Query A: /api/v4/events?action=pushed + Filter: author.username == "user1"
Query B: /api/v4/events?action=pushed + Filter: author.username == "user2"
```

패널을 그룹별로 나누려면 Dashboard에 **Row** 추가:

```
Dashboard → Add → Row
├── Row: team-a
│   └── Heatmap 패널 (Query A)
└── Row: team-b
    └── Heatmap 패널 (Query B)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Tips

```bash
# 페이지네이션 — 커밋이 100개 초과 시
/api/v4/groups/<id>/events?action=pushed&per_page=100&page=2

# 기간 필터
/api/v4/groups/<id>/events?action=pushed&after=2026-01-01&before=2026-12-31
```

⚠️ GitLab API는 페이지당 최대 100개 제한입니다. 커밋이 많으면 Infinity 단독으로는 한계가 있으며, 이 경우 Prometheus exporter 방식으로 전환합니다.

⚠️ Datasource 레벨에 Auth 설정했더라도 패널 URL을 절대경로로 입력하면 Header가 누락될 수 있습니다. 패널 Headers 탭에 `PRIVATE-TOKEN`을 직접 추가합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Infinity Datasource: [grafana.com/plugins/yesoreyeram-infinity-datasource](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/) — ★★★☆☆
- GitLab Events API: [docs.gitlab.com/ee/api/events](https://docs.gitlab.com/ee/api/events.html) — ★★★☆☆
- GitLab Commits API: [docs.gitlab.com/ee/api/commits](https://docs.gitlab.com/ee/api/commits.html) — ★★★☆☆
- [prometheus_grafana.md](./prometheus_grafana.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-13

**마지막 업데이트**: 2026-05-13

© 2026 siasia86. Licensed under CC BY 4.0.
