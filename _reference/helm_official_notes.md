---
name: helm-official-notes
description: Helm 공식 문서 기반 핵심 개념, 버전, Chart 구조 정리.
last_checked: 2026-05-26
sources:
  - https://helm.sh/docs/intro/using_helm/
  - https://helm.sh/docs/chart_template_guide/
---

# Helm 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-26)

| 항목  | 버전   | 비고                        |
|-------|--------|-----------------------------|
| Helm  | v4.2.0 | v4부터 OCI 레지스트리 기본  |

## 2. 공식 정의

> "Helm helps you manage Kubernetes applications — Helm Charts help you
> define, install, and upgrade even the most complex Kubernetes application."
> — helm.sh

## 3. 핵심 개념

| 용어        | 설명                                                        |
|-------------|-------------------------------------------------------------|
| Chart       | Kubernetes 리소스 묶음 패키지 (tgz)                         |
| Release     | 클러스터에 설치된 Chart의 인스턴스                          |
| Repository  | Chart를 저장·공유하는 저장소                                |
| Values      | Chart 동작을 커스터마이징하는 변수 (`values.yaml`)          |
| Template    | Go 템플릿으로 작성된 K8s YAML                               |

## 4. Chart 디렉토리 구조

```
mychart/
├── Chart.yaml          # 차트 메타데이터 (이름, 버전, 설명)
├── values.yaml         # 기본 변수값
├── templates/          # Go 템플릿 YAML
│   ├── deployment.yaml
│   ├── service.yaml
│   └── _helpers.tpl    # 재사용 템플릿 함수
└── charts/             # 의존 차트 (서브차트)
```

## 5. 주요 명령어

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm search repo nginx
helm install my-release bitnami/nginx
helm upgrade my-release bitnami/nginx --set replicaCount=3
helm rollback my-release 1
helm uninstall my-release
helm list
```

## 6. v4 주요 변경사항 (helm.sh/docs/overview 기준)

- **Wasm 기반 플러그인 시스템**: WebAssembly 런타임으로 플러그인 재설계 (CLI / getter / post-renderer 타입)
- **OCI digest 지원**: `oci://registry/chart@sha256:...` 형식으로 digest 지정 설치
- **Multi-Document Values**: 여러 YAML 파일로 values 분리 가능
- **kstatus 통합**: 배포 상태 상세 모니터링
- **Server-Side Apply**: 여러 도구가 동일 리소스 관리 시 충돌 해결 개선
- **Breaking**: post-renderer는 플러그인 이름으로만 지정 (직접 실행 파일 불가)
- **Breaking**: `helm registry login`은 도메인명만 허용 (전체 URL 불가)

## 7. 주의사항

- `helm upgrade --install`: 없으면 설치, 있으면 업그레이드 (CI/CD 권장)
- `--atomic`: 업그레이드 실패 시 자동 롤백
- `helm template`: 실제 설치 없이 렌더링 결과 확인 (디버깅)
- values 우선순위: `--set` > `-f values.yaml` > `values.yaml` (기본)
