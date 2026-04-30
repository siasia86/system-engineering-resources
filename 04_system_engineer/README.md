# 시스템 엔지니어링

시스템 엔지니어 실무에 필요한 로드맵, 인프라 운영, 보안, AI 활용 자료 모음

[⬆ 목차로 돌아가기](#목차)

---

## 문서 목록

### 로드맵
- **[SE 로드맵](se_roadmap.md)** - 시스템 엔지니어 학습 경로
- **[SRE 로드맵](sre_roadmap.md)** - 사이트 신뢰성 엔지니어 학습 경로
- **[SE 로드맵 - 프로그래밍 언어](se_complete_roadmap_programming_languages.md)** - 언어별 학습 가이드

### 프로그래밍 언어
- **[언어 비교 (C, C++, C#, Go, Python, Bash)](c_cpp_csharp_go_python_bash_comparison.md)** - 6개 언어 상세 비교

### 인프라 운영
- **[게임 인프라 KPI](game-infra-kpi-presentation.md)** - 게임 서비스 인프라 운영 핵심 지표
- **[리소스 모니터링](resource_utilization_monitoring.md)** - Linux 서버 리소스 사용률 모니터링
- **[백업 도구 비교](backup_tools_comparison.md)** - 백업 도구 비교 가이드
- **[인프라 Monorepo](infra_monorepo_and_boilerplate.md)** - 인프라 Monorepo & 보일러플레이트 가이드
- **[S3 Gateway Endpoint 크로스 계정](s3_gateway_endpoint_cross_account.md)** - S3 Gateway Endpoint 크로스 계정 설정 가이드

### 네트워크 / 보안
- **[ASN 및 DDoS 대응](asn_and_cloudflare_ddos.md)** - ASN 운영 및 IDC DDoS 대응 가이드
- **[CDN, Proxy, Origin IP](cdn-proxy-origin-ip.md)** - CDN, Proxy, Origin IP 정리
- **[Inter-Region VPC Peering](vpc_peering_inter_region_guide.md)** - Inter-Region VPC Peering 가이드

### 설계 / 문서화
- **[ADR 가이드](adr_guide.md)** - Architecture Decision Record 가이드

### AI 활용
- **[AI 개발 요청 템플릿](ai_development_request_template.md)** - AI 개발 요청 통합 템플릿
- **[AI Markdown 디자인 패턴](ai_markdown_design_patterns.md)** - AI 에이전트용 Markdown 디자인 패턴
- **[Kiro CLI 레퍼런스](kiro_cli_command_reference.md)** - Kiro CLI Command Reference
- **[LSP 가이드](lsp-guide.md)** - Language Server Protocol 가이드
- **[DBA 로드맵](dba_roadmap.md)**
- **[DRM 가이드](drm_guide.md)** - DRM 개념, Tivoization, DMCA, GPL v3 관계 - DBA 역할, 학습 순서, 자격증, SE와의 차이
- **[Kiro 모델 가이드](kiro_model_guide.md)** - Kiro CLI 모델 선택 및 활용 가이드

[⬆ 목차로 돌아가기](#목차)

---

## 커리어 패스

### 시스템 엔지니어 (SE)

```
Junior SE (0-2년)
  ├─ Linux 기초
  ├─ 네트워크 기초
  └─ 스크립팅 (Bash, Python)

Mid-level SE (2-5년)
  ├─ 시스템 아키텍처
  ├─ 자동화 (Ansible, Terraform)
  └─ 컨테이너 (Docker, Kubernetes)

Senior SE (5년+)
  ├─ 인프라 설계
  ├─ 성능 최적화
  └─ 팀 리딩
```

### SRE (Site Reliability Engineer)

```
SRE 핵심 역량
  ├─ 모니터링 & 알림
  ├─ 인시던트 대응
  ├─ 자동화
  ├─ 성능 최적화
  └─ SLO/SLI/SLA 관리
```

[⬆ 목차로 돌아가기](#목차)

---

## 필수 기술 스택

### 운영체제
- Linux (Ubuntu, CentOS, RHEL)
- 시스템 관리 (systemd, cron)

### 프로그래밍
- **스크립팅**: Bash, Python
- **시스템**: Go, Rust
- 웹: JavaScript/TypeScript

### 인프라
- **컨테이너**: Docker, Kubernetes
- **IaC**: Terraform, Ansible
- **CI/CD**: Jenkins, GitLab CI, GitHub Actions

### 모니터링
- Prometheus, Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog, New Relic


---

[문서 전체 로드맵](../README.md)

---

## 참고 자료

### 로드맵 & 커리어

- roadmap.sh DevOps: [roadmap.sh/devops](https://roadmap.sh/devops) — ★★★☆☆
- roadmap.sh SRE: [roadmap.sh/sre](https://roadmap.sh/sre) — ★☆☆☆☆
- roadmap.sh System Design: [roadmap.sh/system-design](https://roadmap.sh/system-design) — ★★★☆☆
- roadmap.sh Linux: [roadmap.sh/linux](https://roadmap.sh/linux) — ★★★☆☆

### SRE & 운영

- Google SRE Book: [sre.google](https://sre.google/sre-book/table-of-contents/) — ★★★☆☆
- Google SRE Workbook: [sre.google/workbook](https://sre.google/workbook/table-of-contents/) — ★★★☆☆
- The Phoenix Project (책): Kim, Gene et al. "The Phoenix Project" — ★★☆☆☆
- The DevOps Handbook (책): Kim, Gene et al. "The DevOps Handbook" — ★★☆☆☆

### 인프라 & 클라우드

- AWS Architecture Center: [aws.amazon.com/architecture](https://aws.amazon.com/architecture/) — ★★☆☆☆
- AWS Well-Architected Framework: [docs.aws.amazon.com/wellarchitected](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) — ★★★☆☆
- Terraform Documentation: [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/docs) — ★★☆☆☆

### 시스템 설계

- System Design Primer: [github.com/donnemartin](https://github.com/donnemartin/system-design-primer) — ★★★☆☆
- High Scalability: [highscalability.com](http://highscalability.com/) — ★★☆☆☆

### 모니터링 & 성능

- Brendan Gregg - Linux Performance: [brendangregg.com](https://www.brendangregg.com/linuxperf.html) — ★★★☆☆
- USE Method: [brendangregg.com/usemethod](https://www.brendangregg.com/usemethod.html) — ★★★☆☆
- Prometheus Documentation: [prometheus.io/docs](https://prometheus.io/docs/introduction/overview/) — ★★☆☆☆


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-25

**마지막 업데이트**: 2026-04-18

© 2026 siasia86. Licensed under CC BY 4.0.
