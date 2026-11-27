# FluxCD
<!-- reference: _reference/fluxcd_official_notes.md -->

Kubernetes 클러스터 안에서 Git·OCI·Helm 저장소를 주기적으로 읽어 클러스터 상태를 맞추는 GitOps 도구입니다. 여러 컨트롤러와 CRD(GitRepository, Kustomization, HelmRelease 등)로 이루어져 있고, 화면 없이 `kubectl`·`flux` 명령으로 다룹니다. 이 문서만으로 CLI 설치 → 클러스터에 설치 → Git 소스와 Kustomization 배포 → HelmRelease → 드리프트 복구 확인 → 검증까지 따라 할 수 있게 썼고, 마지막에 Argo CD와 비교합니다.

- 기준 판: Flux v2.10.1 (2026-11-20, source-controller v1.10.2, kustomize-controller v1.10.2, helm-controller v1.7.2, notification-controller v1.10.1) (2026-11-27 확인)
- 예제 시험: 2026-11-27 2~7절을 kind v0.33.0(Kubernetes v1.37.0) 단일 노드 클러스터에서 실행해 사전 점검, `flux install`, 공개 저장소(podinfo)의 Git 소스·Kustomization·HelmRelease 배포, 삭제·수정한 리소스 복구, suspend·resume, 잘못된 경로 오류, `flux uninstall` 뒤 워크로드 유지를 확인. `flux bootstrap`(Git 호스팅 토큰 필요), 이미지 자동 갱신, 알림(Provider·Alert), SOPS 복호화, 여러 클러스터 구성은 미실행

## 목차

| 섹션                                                                                              |
|---------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. CLI 설치](#2-cli-설치) / [3. 클러스터에 설치](#3-클러스터에-설치)        |
| [4. Git 소스와 Kustomization](#4-git-소스와-kustomization) / [5. HelmRelease](#5-helmrelease)     |
| [6. 드리프트와 일시 중지](#6-드리프트와-일시-중지) / [7. 상태 확인 명령](#7-상태-확인-명령)       |
| [8. bootstrap으로 운영 구성](#8-bootstrap으로-운영-구성) / [9. Argo CD와 비교](#9-argo-cd와-비교) |
| [10. 검증](#10-검증) / [11. 트러블슈팅](#11-트러블슈팅) / [함께 보기](#함께-보기)                 |

---

## 1. 개요

```text
[Git / OCI / Helm repo] <--poll-- [source-controller] --artifact--> [kustomize-controller] --apply--> cluster
                                                       \-----------> [helm-controller] ------helm---> cluster
                                    [notification-controller] --> Slack, Teams, webhook ...
```

| 컨트롤러                    | CRD                                                                | 기본 설치 |
|-----------------------------|--------------------------------------------------------------------|-----------|
| source-controller           | GitRepository, OCIRepository, HelmRepository, HelmChart, Bucket 등 | 예        |
| kustomize-controller        | Kustomization                                                      | 예        |
| helm-controller             | HelmRelease                                                        | 예        |
| notification-controller     | Provider, Alert, Receiver                                          | 예        |
| image-reflector-controller  | ImageRepository, ImagePolicy                                       | 아니오    |
| image-automation-controller | ImageUpdateAutomation                                              | 아니오    |

- API 판: `source.toolkit.fluxcd.io/v1`, `kustomize.toolkit.fluxcd.io/v1`, `helm.toolkit.fluxcd.io/v2`, `notification.toolkit.fluxcd.io/v1`(시험한 v2.10.1의 `flux check` 출력 기준).
- Flux의 Kustomization(`kustomize.toolkit.fluxcd.io`)은 kustomize 도구의 `kustomization.yaml`과 다른 객체입니다. Flux Kustomization이 저장소의 경로를 가리키고, 그 경로 안에 `kustomization.yaml`이 있으면 kustomize로 빌드합니다.
- Flux 프로젝트는 자체 웹 화면을 제공하지 않습니다. 화면이 필요하면 Flux Operator, Headlamp 플러그인, Capacitor 같은 생태계 도구를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. CLI 설치

```bash
FV=2.10.1
curl -sSLO https://github.com/fluxcd/flux2/releases/download/v${FV}/flux_${FV}_linux_amd64.tar.gz
curl -sSLO https://github.com/fluxcd/flux2/releases/download/v${FV}/flux_${FV}_checksums.txt
grep " flux_${FV}_linux_amd64.tar.gz\$" flux_${FV}_checksums.txt | sha256sum -c -
sudo tar xzf flux_${FV}_linux_amd64.tar.gz -C /usr/local/bin flux
flux version --client
```

- 시험한 압축판은 체크섬 파일과 일치했습니다.
- macOS는 `brew install fluxcd/tap/flux`도 있습니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 3. 클러스터에 설치

```bash
flux check --pre        # Kubernetes 판 점검
flux install            # 기본 컨트롤러 4개
flux check
```

- v2.10.1의 사전 점검은 `Kubernetes 1.37.0 >=1.35.0-0`처럼 최소 판을 보여 줍니다. Flux는 최근 Kubernetes minor 판 세 개만 지원합니다.
- 이미지 자동 갱신까지 쓰려면 `flux install --components-extra=image-reflector-controller,image-automation-controller`로 설치합니다(시험에서 컨트롤러 6개가 뜸).
- `flux install`은 시험·개발용입니다. 운영은 설치 매니페스트를 Git에 두고 Flux가 자신을 관리하게 하는 `flux bootstrap`을 씁니다(8절).

[⬆ 목차로 돌아가기](#목차)

---

## 4. Git 소스와 Kustomization

공개 예제 저장소 podinfo의 `kustomize/` 경로를 배포합니다.

```bash
flux create source git podinfo \
  --url=https://github.com/stefanprodan/podinfo \
  --branch=master \
  --interval=1m

flux create kustomization podinfo \
  --source=GitRepository/podinfo \
  --path=./kustomize \
  --prune=true \
  --interval=5m \
  --target-namespace=default \
  --wait=true --timeout=3m
```

같은 내용을 YAML로 Git에 둘 때의 모양입니다(`flux export`로 뽑을 수 있음).

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 1m0s
  ref:
    branch: master
  url: https://github.com/stefanprodan/podinfo
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 5m0s
  path: ./kustomize
  prune: true
  sourceRef:
    kind: GitRepository
    name: podinfo
  targetNamespace: default
  wait: true
  timeout: 3m0s
```

| 필드                   | 뜻                                                                           |
|------------------------|------------------------------------------------------------------------------|
| `interval`             | 다시 맞추는 주기(필수). 문서는 최소 60초를 권함                              |
| `prune`                | 저장소에서 빠진 리소스를 클러스터에서도 지움(필수)                           |
| `wait`                 | 적용한 리소스가 모두 준비될 때까지 확인                                      |
| `timeout`              | 빌드·적용·상태 확인 제한 시간                                                |
| `dependsOn`            | 먼저 준비돼야 하는 다른 Kustomization                                        |
| `decryption`           | `provider: sops`와 키 Secret으로 SOPS 파일 복호화(age 키는 `.agekey` 접미사) |
| `postBuild.substitute` | 빌드 뒤 `${VAR}` 치환 값                                                     |

- 시험에서 Deployment 2개 replica, Service, HPA가 만들어졌고 `flux tree kustomization podinfo`에 세 리소스가 보였습니다.
- 비밀값 파일은 [SOPS](../iac/sops.md)로 암호화해 커밋하고 `decryption`으로 풉니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 5. HelmRelease

```bash
flux create source helm podinfo \
  --url=https://stefanprodan.github.io/podinfo \
  --interval=10m

flux create helmrelease podinfo \
  --source=HelmRepository/podinfo \
  --chart=podinfo \
  --chart-version=">=6.0.0" \
  --target-namespace=helmdemo \
  --create-target-namespace \
  --interval=10m

kubectl -n flux-system wait helmrelease/podinfo --for=condition=Ready --timeout=180s
```

- `flux create helmrelease`에는 `--wait` 옵션이 없습니다(시험에서 `unknown flag: --wait`). 준비 확인은 `kubectl wait`나 `flux get helmreleases`로 합니다.
- Helm 릴리스 이름은 따로 정하지 않으면 `<대상 namespace>-<HelmRelease 이름>`입니다. 시험에서는 `helmdemo-podinfo`로 설치돼 Deployment 이름도 `helmdemo-podinfo`였습니다. 이름을 고정하려면 `--release-name`을 줍니다.
- 값 바꾸기는 HelmRelease의 `spec.values`나 `valuesFrom`(ConfigMap·Secret)에 둡니다. `--chart-version`의 범위는 Helm 저장소 차트에만 적용되고 Git 소스 차트에는 무시됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 드리프트와 일시 중지

```bash
# 즉시 다시 맞추기 (--with-source: 소스도 먼저 새로 받음)
flux reconcile kustomization podinfo --with-source

# 장애 대응 중 자동 적용 멈추기 / 다시 켜기
flux suspend kustomization podinfo
flux resume kustomization podinfo
```

- 시험에서 Deployment를 지운 뒤 reconcile하면 다시 만들어졌고, 이미지를 손으로 `6.0.0`으로 바꾼 뒤 reconcile하면 저장소의 `6.17.0`으로 돌아갔습니다.
- 손으로 고친 내용은 다음 주기(`interval`)나 reconcile에서 덮어씁니다. 장애 대응으로 클러스터를 직접 고쳐야 하면 먼저 `suspend`하고, 고친 내용을 Git에 반영한 뒤 `resume`합니다.
- `flux uninstall`은 Flux 컨트롤러와 CRD만 지우고, Flux가 배포한 워크로드는 남깁니다(시험에서 podinfo Deployment 유지).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 상태 확인 명령

| 명령                           | 보는 것                                       |
|--------------------------------|-----------------------------------------------|
| `flux get all -A`              | 모든 소스·Kustomization·HelmRelease 준비 상태 |
| `flux get kustomizations`      | 적용한 revision, SUSPENDED, READY, 메시지     |
| `flux tree kustomization 이름` | 그 Kustomization이 만든 리소스 목록           |
| `flux events -A`               | 최근 이벤트(성공·실패 원인)                   |
| `flux logs --level=error`      | 컨트롤러 오류 로그                            |
| `flux export source git 이름`  | 현재 객체를 YAML로 출력                       |

[⬆ 목차로 돌아가기](#목차)

---

## 8. bootstrap으로 운영 구성

공식 문서가 권하는 설치 방법입니다. Flux 매니페스트를 Git 저장소에 커밋하고, Flux가 그 저장소에서 자신까지 갱신하게 만듭니다.

```bash
export GITHUB_TOKEN='<GITHUB_TOKEN>'
flux bootstrap github \
  --token-auth \
  --owner=<GITHUB_USER> \
  --repository=<REPOSITORY> \
  --branch=main \
  --path=clusters/<CLUSTER_NAME> \
  --personal
```

- 조직 저장소는 `--personal`을 빼고 `--owner`에 조직 이름을 줍니다. `GITHUB_TOKEN`이 없으면 명령이 토큰을 묻습니다.
- 토큰은 클러스터의 `flux-system` namespace에 `flux-system` Secret으로 저장됩니다. 권한이 넓은 토큰이므로 저장소 하나로 범위를 줄인 토큰을 씁니다.
- GitLab·Gitea 등 다른 Git 호스팅, Terraform provider, Flux Operator(FluxInstance CR)로도 설치할 수 있습니다.
- 이번 시험에서는 Git 호스팅 토큰이 필요해 bootstrap을 실행하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. Argo CD와 비교

| 항목             | FluxCD                                                      | [Argo CD](./argocd.md)                                       |
|------------------|-------------------------------------------------------------|--------------------------------------------------------------|
| 구성             | 역할별 컨트롤러 + CRD. 필요한 것만 설치                     | API 서버, repo-server, application-controller, Redis, Dex 등 |
| 화면             | 없음(생태계 도구)                                           | 웹 UI 기본 포함                                              |
| 배포 단위        | Kustomization, HelmRelease                                  | Application, ApplicationSet                                  |
| Helm             | helm-controller가 실제 Helm 릴리스로 설치(`helm ls`에 보임) | 차트를 렌더링해 매니페스트로 적용                            |
| 권한 모델        | Kubernetes RBAC, 서비스 계정 지정(impersonation)            | 자체 RBAC·프로젝트(AppProject)·SSO                           |
| 여러 클러스터    | 클러스터마다 Flux 설치가 일반적                             | Argo CD 하나에서 여러 클러스터 관리                          |
| 이미지 자동 갱신 | 기본 컴포넌트(선택 설치)                                    | 별도 프로젝트 Argo CD Image Updater                          |
| 설치 시험(kind)  | 컨트롤러 4개, `flux install` 한 번                          | 일반 `kubectl apply`는 CRD 크기로 실패, server-side 필요     |

- 고르는 기준: 화면으로 여러 팀이 상태를 보고 수동 동기화·되돌리기를 자주 한다면 Argo CD, 클러스터마다 가볍게 두고 Git과 Kubernetes RBAC만으로 운영한다면 Flux가 맞습니다. 둘 다 CNCF 졸업 프로젝트입니다.
- Flux 공식 문서에서 Argo CD와의 비교 문장은 찾지 못했습니다. 위 표는 두 도구의 공식 문서와 이번 시험을 대조해 정리한 것입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용 | 방법                                              | 기대 결과                                  |
|------|-----------|---------------------------------------------------|--------------------------------------------|
| 1    | 사전 점검 | `flux check --pre`                                | `prerequisites checks passed`              |
| 2    | 설치      | `flux check`                                      | `all checks passed`                        |
| 3    | 소스      | `flux get sources git`                            | READY True, `stored artifact for revision` |
| 4    | 적용      | `flux get kustomizations`                         | READY True, `Applied revision: ...`        |
| 5    | 리소스    | `flux tree kustomization 이름`                    | 저장소의 리소스 목록                       |
| 6    | 드리프트  | 리소스 삭제 뒤 `flux reconcile ... --with-source` | 다시 생성                                  |
| 7    | Helm      | `flux get helmreleases`                           | `Helm install succeeded ...`               |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

| 증상                                                   | 원인                                          | 조치                                                  |
|--------------------------------------------------------|-----------------------------------------------|-------------------------------------------------------|
| `kustomization path not found: stat ...: no such file` | `--path`가 저장소에 없음                      | 경로 확인(저장소 루트 기준 `./경로`)                  |
| `✗ context deadline exceeded` (`--wait` 사용 시)       | 제한 시간 안에 준비되지 않음, 위 경로 오류 등 | `flux get`·`flux events`로 실제 원인 확인             |
| `unknown flag: --wait` (`create helmrelease`)          | helmrelease 생성 명령에는 없는 옵션           | `kubectl wait helmrelease/이름 --for=condition=Ready` |
| 손으로 고친 값이 되돌아감                              | 정상 동작(드리프트 복구)                      | Git에 반영, 급하면 `flux suspend`                     |
| 이미지 자동 갱신 CRD가 없음                            | 기본 설치에 image 컨트롤러 없음               | `--components-extra`로 다시 설치                      |
| `flux uninstall` 뒤에도 앱이 남음                      | 워크로드는 지우지 않음                        | 앱을 지우려면 먼저 Kustomization을 삭제(prune)        |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Argo CD](./argocd.md) — 웹 UI가 있는 GitOps 도구
- [Helm](../containers/helm.md) — 차트와 릴리스
- [SOPS](../iac/sops.md) — Git에 두는 비밀값 암호화
- [kind](../containers/kind.md) — 시험용 로컬 클러스터

---

## 참고 자료

- Flux Docs: [Installation](https://fluxcd.io/flux/installation/) · [Bootstrap for GitHub](https://fluxcd.io/flux/installation/bootstrap/github/) · [Components](https://fluxcd.io/flux/components/) · [Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/) · [FAQ](https://fluxcd.io/flux/faq/) — ★★★☆☆
- GitHub: [fluxcd/flux2 releases](https://github.com/fluxcd/flux2/releases) — ★★★☆☆
- 예제 저장소: [stefanprodan/podinfo](https://github.com/stefanprodan/podinfo) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
