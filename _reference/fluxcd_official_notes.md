---
name: fluxcd-official-notes
description: Flux v2.10.1 판과 컨트롤러 판, 지원 Kubernetes 판, 설치 방법, Kustomization 필드, kind 시험 결과 정리.
tags:
  - flux
  - gitops
  - kubernetes
last_checked: 2026-11-27
sources:
  - https://github.com/fluxcd/flux2/releases/tag/v2.10.0
  - https://github.com/fluxcd/flux2/releases/tag/v2.10.1
  - https://fluxcd.io/flux/installation/
  - https://fluxcd.io/flux/installation/bootstrap/github/
  - https://fluxcd.io/flux/components/
  - https://fluxcd.io/flux/components/kustomize/kustomizations/
  - https://fluxcd.io/flux/faq/
---

# FluxCD 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- v2.10.1(2026-11-20): "a patch release that fixes credential caching across the controllers". source-controller v1.10.2, kustomize-controller v1.10.2, notification-controller v1.10.1, helm-controller v1.7.2, image-reflector-controller v1.3.1, image-automation-controller v1.3.1.
- v2.10.0(2026-10-26, feature release): source-watcher v2.3.1 포함. 이전 v2.9.6(10-01), v2.9.5(08-31).
- v2.10.0 주요 변경: object identity GA(`ObjectLevelWorkloadIdentity` feature gate 폐지), 기본 RBAC에서 `serviceaccounts/token` create 권한 제거, notification `Alert`·`Provider` v1 승격(v1beta3의 `Alert.spec.summary`, `Provider.spec.interval` 제거), ImageRepository 태그 저장소 기본값이 Flux artifact storage(`--feature-gates=FluxStorage=false`로 BadgerDB 유지), OCIRepository를 HelmRelease 차트 소스로 사용, ArtifactGenerator.
- 지원: "Flux project offers support only for the latest three minor versions of Kubernetes." CLI·컨트롤러는 최근 minor 세 개 지원(FAQ).
- 지원 Kubernetes 표: 릴리스 노트는 v1.35 `>= 1.35.2`, v1.36 `>= 1.36.1`, v1.37 `>= 1.37.0`, 설치 문서는 `>= 1.35.0`·`>= 1.36.0`·`>= 1.37.0`으로 서로 다름. v2.10.1 `flux check --pre`는 `>=1.35.0-0`.

## 2. 설치

- "The recommended way of installing Flux on Kubernetes clusters is by using the bootstrap procedure." 그 밖에 Terraform(`flux_bootstrap_git`), Flux Operator(FluxInstance), 개발용 `flux install`·install.yaml·Helm.
- GitHub bootstrap: `flux bootstrap github --token-auth --owner --repository --branch --path --personal`. `GITHUB_TOKEN`이 없으면 입력을 물음. 토큰은 `flux-system` namespace의 `flux-system` Secret에 저장.
- bootstrap이 커밋하는 파일 이름(`gotk-components.yaml` 등)은 읽은 두 쪽에서 찾지 못함.

## 3. 구성 요소·필드

- CRD: Source(GitRepository, OCIRepository, HelmRepository, HelmChart, Bucket, ExternalArtifact, ArtifactGenerator), Kustomization, HelmRelease, Notification(Provider, Alert, Receiver), Image(ImageRepository, ImagePolicy, ImageUpdateAutomation). ExternalArtifact 사용은 `--feature-gates=ExternalArtifact=true` 필요.
- Kustomization: `interval` 필수("The minimum value should be 60 seconds."), `retryInterval`, `prune` 필수, `wait`(true면 `healthChecks` 무시), `timeout`, `dependsOn`, `decryption.provider: sops`(유일한 값)·`secretRef`(age 키는 `.agekey` 접미사), `postBuild.substitute`·`substituteFrom`.
- UI: "The Flux project does not provide a UI of its own". 생태계: Flux Operator, Capacitor, Radar, Headlamp 플러그인, Freelens, VS Code GitOps Tools, Weave GitOps.
- FAQ에서 Argo CD 비교 문장은 찾지 못함.

## 4. kind 시험 (2026-11-27, kind v0.33.0, Kubernetes v1.37.0)

- CLI 압축판 체크섬 일치, `flux version --client` v2.10.1.
- `flux install`: 컨트롤러 4개(helm, kustomize, notification, source). `flux check`에 CRD 판 `source.toolkit.fluxcd.io/v1`, `kustomize.toolkit.fluxcd.io/v1`, `helm.toolkit.fluxcd.io/v2`, `notification.toolkit.fluxcd.io/v1`. `--components-extra=image-reflector-controller,image-automation-controller`로 6개.
- podinfo `./kustomize`: Deployment 2/2, Service, HPA. Deployment 삭제 뒤 `reconcile --with-source`로 재생성, 이미지를 손으로 6.0.0으로 바꾸면 reconcile 뒤 6.17.0으로 복귀.
- suspend 상태가 `flux get`의 SUSPENDED True로 보임, resume 정상.
- 잘못된 경로: `kustomization path not found: stat ...: no such file or directory`, `--wait`는 `context deadline exceeded`.
- `flux create helmrelease`에 `--wait` 없음(`unknown flag: --wait`). HelmRelease 정상 설치, 릴리스 이름 `helmdemo-podinfo`(`<target-namespace>-<name>`).
- `flux uninstall`: flux-system 삭제, podinfo Deployment는 남음.
- 미실행: bootstrap, 이미지 자동 갱신 동작, 알림, SOPS 복호화.
