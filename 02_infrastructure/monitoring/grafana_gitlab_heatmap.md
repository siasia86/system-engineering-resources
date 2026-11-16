# Grafana — GitLab Contribution Heatmap

## 목차

| 섹션                                                                                                                             |
|----------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 사전 준비](#2-사전-준비) / [3. Infinity Datasource 설정](#3-infinity-datasource-설정)                   |
| [4. 패널 쿼리 설정](#4-패널-쿼리-설정) / [5. 유저별 Bar chart 패널](#5-유저별-bar-chart-패널) / [6. 그룹별 분리](#6-그룹별-분리) |
| [7. Tips](#7-tips)                                                                                                               |

---

## 1. 개요

Grafana OSS(무료)와 Infinity Datasource 플러그인을 사용하여 GitLab 커밋 기여도를 Heatmap(잔디)으로 시각화합니다. 별도 exporter나 중간 저장소 없이 GitLab API를 직접 조회합니다.

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  GitLab API ──> Infinity Datasource ──> Grafana Heatmap             │
│                                                                     │
│  /users/<id>/events                 per-user push events            │
│  /projects/<id>/events              per-project push events         │
│  /projects/<id>/repository/commits  per-project commits             │
└─────────────────────────────────────────────────────────────────────┘
```

| 항목       | 내용                                               |
|------------|----------------------------------------------------|
| Grafana    | OSS (무료)                                         |
| 플러그인   | yesoreyeram-infinity-datasource                    |
| Enterprise | 불필요                                             |
| 인증       | GitLab Personal Access Token (read_api, read_user) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사전 준비

### Infinity 플러그인 설치

```bash
grafana cli plugins install yesoreyeram-infinity-datasource
sudo systemctl restart grafana-server
```

### GitLab Access Token 발급

GitLab Events API에는 인스턴스 전체 사용자의 이벤트를 한 번에 돌려주는 엔드포인트가 없습니다. `GET /events`는 관리자 토큰이라도 **토큰 소유자 본인의 이벤트**만 반환하고, 그룹 단위 이벤트 엔드포인트도 없습니다. 따라서 사용자별(`/users/:id/events`) 또는 프로젝트별(`/projects/:id/events`)로 조회합니다.

- 이벤트는 토큰 소유자가 볼 수 있는 프로젝트 범위에서만 반환됩니다. 비공개 프로젝트까지 집계하려면 해당 프로젝트를 볼 수 있는 계정(멤버 또는 관리자)의 토큰을 사용합니다.
- 공식 문서는 `/events`·`/users/:id/events`에 `read_user` 또는 `api` scope를 요구하므로, 읽기 전용으로는 `read_api`와 `read_user`를 함께 부여합니다.

**웹 UI에서 발급:**
```
대상 프로젝트를 볼 수 있는 계정으로 로그인
→ 우측 상단 아바타 → Edit profile
→ 왼쪽 사이드바 Access → Personal access tokens
→ Generate token → Legacy token
  - Token name: grafana-readonly
  - Scopes: read_api, read_user
→ Generate token
→ 토큰 값 복사 (페이지 벗어나면 재확인 불가)
```

**Rails console에서 발급 (서버 직접 접근 시):**
```bash
sudo gitlab-rails console

# Rails console 내
user = User.find_by_username('root')
token = user.personal_access_tokens.create(
  name: 'grafana-readonly',
  scopes: ['read_api', 'read_user'],
  expires_at: 365.days.from_now
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

# 그룹 멤버(사용자 ID) 확인
curl -s --header "PRIVATE-TOKEN: <token>" \
  "https://gitlab.example.com/api/v4/groups/<group_id>/members"
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Infinity Datasource 설정

`Connections` → `Data sources` → `Add new data source` → `Infinity`

| 항목      | 값                                  |
|-----------|-------------------------------------|
| Base URL  | `https://gitlab.example.com/api/v4` |
| Auth Type | `API Key`                           |
| Key       | `PRIVATE-TOKEN`                     |
| Value     | `<your-token>`                      |
| Add to    | `Header`                            |

🟡 Base URL은 회사 GitLab 도메인으로 변경합니다. `http://` → `https://` 확인 필수.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 패널 쿼리 설정

### 사용자별 푸시 이벤트

패널 추가 → Datasource: `Infinity` 선택

| 항목   | 값                                                                                    |
|--------|---------------------------------------------------------------------------------------|
| Type   | `JSON`                                                                                |
| Method | `GET`                                                                                 |
| URL    | `https://gitlab.example.com/api/v4/users/<user_id>/events?action=pushed&per_page=100` |

Headers 탭:
```
Key:   PRIVATE-TOKEN
Value: <token>
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

| 범위          | 엔드포인트                                           | 반환 범위                           |
|---------------|------------------------------------------------------|-------------------------------------|
| 토큰 소유자   | `/api/v4/events?action=pushed`                       | 본인 이벤트만 (관리자 토큰도 같음)  |
| 특정 사용자   | `/api/v4/users/<user_id>/events?action=pushed`       | 토큰이 볼 수 있는 프로젝트의 이벤트 |
| 특정 프로젝트 | `/api/v4/projects/<project_id>/events?action=pushed` | 해당 프로젝트의 보이는 이벤트       |

🔵 그룹 단위 이벤트 엔드포인트는 공식 문서에 없습니다. 그룹 기준 집계는 그룹의 프로젝트별 또는 멤버별 쿼리를 합쳐서 만듭니다.

🔵 푸시 이벤트 1건에 커밋 여러 개가 들어 있을 수 있습니다. 커밋 수로 집계하려면 이벤트의 `push_data.commit_count`를 합산하거나 Commits API(`/projects/<id>/repository/commits`)를 사용합니다.

### Computed columns / Filter / Group by

| 기능             | 용도                                          | 잔디 필요 여부     |
|------------------|-----------------------------------------------|--------------------|
| Computed columns | API 응답에 없는 컬럼을 수식으로 생성          | 선택 (날짜 파싱용) |
| Filter           | 특정 조건으로 데이터 필터링 (작성자, 날짜 등) | 선택               |
| Group by         | 날짜별 커밋 수 집계 — **Heatmap 핵심 설정**   | ✅ 필수            |

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

## 5. 유저별 Bar chart 패널

Grafana 12 Heatmap은 table frame 입력 시 호환 문제가 있습니다. **Bar chart** 로 날짜별 커밋 수를 표현하는 것이 안정적입니다.

### Transform 설정 순서

```
1. filterByValue   → 특정 author_name만 필터링
2. convertFieldType → created_at → time
3. formatTime      → YYYY-MM-DD (하루 단위로 포맷)
4. groupBy         → created_at: groupby / commit_id: count
5. sortBy          → created_at 오름차순
```

🟡 Infinity 플러그인 내장 Filter는 `(intermediate value).map is not a function` 에러를 유발합니다. 반드시 **Grafana Transform 탭의 `filterByValue`** 를 사용합니다.

### filterByValue 설정

```
Transform → Add transformation → Filter by value
  Field name: author_name
  Filter:     Equals → <author_name>
  Match:      All
  Type:       Include
```

### formatTime 설정 (하루 단위)

```
Transform → Add transformation → Format time
  Time field:     created_at
  Output format:  YYYY-MM-DD
  Timezone:       Asia/Seoul
```

### 유저별 패널 구성 예시

프로젝트별로 `author_name`이 다를 수 있습니다 (한글/영문 혼재). API로 실제 값 확인 후 설정합니다.

```bash
# 프로젝트별 author_name 확인
curl -s --header "PRIVATE-TOKEN: <admin-token>" \
  "https://gitlab.example.com/api/v4/projects/<project_id>/repository/commits?per_page=20" \
  | python3 -c 'import sys,json; [print(c["author_name"]) for c in json.load(sys.stdin)]'
```

| username | author_name (git config) | 비고            |
|----------|--------------------------|-----------------|
| user1    | user1                    | 영문            |
| user2    | 홍길동                   | 한글 git config |

### Bar chart 패널 옵션

```
Panel type: Bar chart
X Field:    created_at
Bar width:  0.9
Fill:       80%
Color:      Fixed → Green
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 그룹별 분리

쿼리를 여러 개 추가하여 그룹/사용자별로 분리합니다. 그룹 이벤트 엔드포인트가 없으므로 그룹은 소속 프로젝트별 쿼리로, 사용자는 사용자 ID별 쿼리로 나눕니다. 프로젝트 ID는 `/groups/<group_id>/projects`, 사용자 ID는 `/groups/<group_id>/members`로 확인합니다.

```
# group (one query per project in the group)
Query A: /api/v4/projects/101/events?action=pushed   → team-a
Query B: /api/v4/projects/201/events?action=pushed   → team-b

# user (one query per user)
Query A: /api/v4/users/11/events?action=pushed       → user1
Query B: /api/v4/users/12/events?action=pushed       → user2
```

패널을 그룹별로 나누려면 Dashboard에 **Row** 추가:

```
Dashboard → Add → Row         
├── Row: team-a               
│   └── Heatmap panel (Query A)
└── Row: team-b               
    └── Heatmap panel (Query B)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Tips

```bash
# 페이지네이션 — 커밋이 100개 초과 시
/api/v4/users/<id>/events?action=pushed&per_page=100&page=2

# 기간 필터 (ISO 8601 날짜)
/api/v4/users/<id>/events?action=pushed&after=2026-01-01&before=2026-12-31
```

🟡 GitLab API는 페이지당 최대 100개 제한입니다. 커밋이 많으면 Infinity 단독으로는 한계가 있으며, 이 경우 Prometheus exporter 방식으로 전환합니다.

🟡 Datasource 레벨에 Auth 설정했더라도 패널 URL을 절대경로로 입력하면 Header가 누락될 수 있습니다. 패널 Headers 탭에 `PRIVATE-TOKEN`을 직접 추가합니다.

🟡 Infinity Datasource `Allowed hosts`에 GitLab 도메인을 반드시 등록합니다 (`https://` 포함). 미등록 시 `requested URL not allowed` 에러가 발생합니다.

🟡 `author_name`은 git config 기준이므로 GitLab username과 다를 수 있습니다. API로 실제 값을 확인 후 `filterByValue`에 입력합니다.

🟡 커밋이 없는 날짜는 API 응답에 포함되지 않아 Bar chart에 표시되지 않습니다. 빈 날짜까지 표시하려면 중간 저장소(InfluxDB/Prometheus) 수집 파이프라인이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Infinity Datasource: [grafana.com/plugins/yesoreyeram-infinity-datasource](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/) — ★★★☆☆
- GitLab Events API: [docs.gitlab.com/api/events](https://docs.gitlab.com/api/events/) — ★★★☆☆ (확인일 2026-11-16)
- GitLab Access token scopes: [docs.gitlab.com/security/tokens/access_token_scopes](https://docs.gitlab.com/security/tokens/access_token_scopes/) — ★★★☆☆ (확인일 2026-11-16)
- GitLab Commits API: [docs.gitlab.com/ee/api/commits](https://docs.gitlab.com/ee/api/commits.html) — ★★★☆☆
- GitLab Personal access tokens: [docs.gitlab.com/user/profile/personal_access_tokens](https://docs.gitlab.com/user/profile/personal_access_tokens/) — ★★★☆☆
- Grafana CLI: [grafana.com/docs/grafana/latest/administration/cli](https://grafana.com/docs/grafana/latest/administration/cli/) — ★★★☆☆
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

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
