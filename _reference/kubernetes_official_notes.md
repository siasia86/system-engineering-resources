---
name: kubernetes-official-notes
description: Kubernetes 공식 문서 기반 핵심 개념, 버전, 아키텍처 정리.
last_checked: 2026-05-26
sources:
  - https://kubernetes.io/docs/concepts/overview/
  - https://kubernetes.io/docs/concepts/architecture/
---

# Kubernetes 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-26)

| 항목            | 버전    |
|-----------------|---------|
| Kubernetes      | v1.36.1 |
| 지원 정책       | 최신 3개 마이너 버전 |

## 2. 공식 정의

> "Kubernetes is a portable, extensible, open source platform for managing
> containerized workloads and services, that facilitates both declarative
> configuration and automation."
> — kubernetes.io

## 3. 핵심 오브젝트

| 오브젝트      | 설명                                                   |
|---------------|--------------------------------------------------------|
| Pod           | 최소 배포 단위, 1개 이상의 컨테이너 묶음               |
| Deployment    | Pod 복제·롤링 업데이트 관리                            |
| Service       | Pod 집합에 대한 네트워크 엔드포인트                    |
| ConfigMap     | 설정 데이터 저장 (비민감)                              |
| Secret        | 민감 데이터 저장 (base64 인코딩)                       |
| Namespace     | 클러스터 내 논리적 격리 단위                           |
| Node          | 컨테이너를 실행하는 워커 머신                          |
| PersistentVolume | 스토리지 추상화 레이어                              |

## 4. 클러스터 아키텍처

```
Control Plane                    Worker Node
─────────────                    ───────────
kube-apiserver                   kubelet
etcd                             kube-proxy
kube-scheduler                   Container Runtime
kube-controller-manager          (containerd / CRI-O)
```

## 5. 주요 특징

- **Self-healing**: 컨테이너 장애 시 자동 재시작·재배치
- **Horizontal scaling**: `kubectl scale` 또는 HPA로 자동 스케일
- **Rolling update / Rollback**: 무중단 배포, 이전 버전 복구
- **Service discovery**: 내부 DNS (CoreDNS)로 서비스 간 통신
- **Declarative**: YAML로 원하는 상태 정의, 컨트롤러가 실현

## 6. CRI 요구사항

- v1.24+: dockershim 제거, CRI 표준 런타임 필수
- v1.26+: CRI API v1 필수
- v1.37: containerd 1.x 호환 불가 예정 (RuntimeConfig CRI RPC 미지원)

## 7. 주의사항

- etcd 백업 필수 (클러스터 상태 전체 저장)
- `kubectl apply` vs `kubectl create`: apply는 선언적(권장), create는 명령적
- Resource Requests/Limits 미설정 시 노드 자원 고갈 위험
- RBAC 기본 활성화 (v1.6+)
