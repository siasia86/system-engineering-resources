# 컨테이너 이미지 태그·digest와 단계별 승격
<!-- reference: _reference/container_image_promotion_official_notes.md -->

컨테이너 이미지를 한 번 빌드해 digest로 식별하고, 다시 빌드하지 않고 단계별 레지스트리(또는 태그)로 올리며, 서명·SBOM을 함께 옮기고 오래된 이미지를 정리하는 방법을 정리합니다. 원칙은 [이미지 판 관리와 단계별 승격](../cicd/image_versioning_and_promotion.md)에 있고, 이 문서는 명령과 설정을 다룹니다.

- 기준 판: crane v0.22.1, cosign v3.1.6, syft v1.57.2, distribution(registry) v3.1.2, skopeo v1.25.2 (2026-11-27 확인)
- 예제 시험: 2026-11-27 레지스트리 컨테이너 두 개(`registry:3.1.2`, 단계 예시 dev·prod)와 도구 컨테이너에서 2~9절을 실행. 공개 이미지 미러 복사, 라벨 추가, 태그 추가, 레지스트리 간 digest 승격, 태그 덮어쓰기, `crane copy -n`, cosign 키 서명·검증·SPDX 증명, 서명 복사, garbage collection을 확인. skopeo, Harbor·ECR·Nexus의 불변·정리 기능, 키 없는 서명(OIDC)은 미시험(공식 문서만 대조)

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 구성 개요](#1-구성-개요) / [2. 태그와 digest](#2-태그와-digest) / [3. 태그 규칙](#3-태그-규칙)               |
| [4. 출처 라벨](#4-출처-라벨) / [5. 승격 방법](#5-승격-방법) / [6. 배포에서 digest 고정](#6-배포에서-digest-고정) |
| [7. 서명과 SBOM](#7-서명과-sbom) / [8. 덮어쓰기 막기](#8-덮어쓰기-막기) / [9. 정리](#9-정리)                     |
| [10. 검증](#10-검증) / [11. 트러블슈팅](#11-트러블슈팅) / [함께 보기](#함께-보기)                                |

---

## 1. 구성 개요

```text
CI 빌드 1회 → dev 레지스트리   app:1.4.0-3f2a9c1  (digest A)
                                 + 서명, SBOM 증명
     |  시험 통과
     |  같은 저장소: 단계 태그 추가   app:qa → A
     |  다른 저장소: digest A 복사    prod 레지스트리 app:1.4.0 → A
     v
배포 설정: registry.example.com/app:1.4.0@sha256:A
```

- 예제의 단계 이름과 레지스트리 수는 설명용입니다. 레지스트리 하나에 단계 태그만 쓰는 조직도, 단계마다 레지스트리를 두는 조직도 있습니다.
- 명령의 `reg-dev:5000`, `reg-prod:5000`은 시험용 이름이며 `registry.example.com` 같은 실제 주소로 바꿔 씁니다. 시험 레지스트리는 HTTP라 `--insecure`·`--allow-http-registry`를 붙였고, HTTPS 레지스트리에서는 빼야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 태그와 digest

| 구분   | 예                       | 바뀌는가                            | 용도                        |
|--------|--------------------------|-------------------------------------|-----------------------------|
| 태그   | `app:1.4.0`, `app:qa`    | 레지스트리 설정에 따라 바뀔 수 있음 | 사람이 읽는 이름, 단계 표시 |
| digest | `app@sha256:9deaef37...` | 내용이 같으면 항상 같음             | 배포·승격·서명의 기준       |

시험(registry 3.1.2 기본 설정)에서 같은 태그에 다른 이미지를 올렸을 때:

```text
dev 1.4.0 now   sha256:b8c4baaa...   ← 태그는 새 이미지로 바뀜
by digest still sha256:9deaef37...   ← digest로 받으면 원래 이미지
```

- 여러 아키텍처 이미지는 목록(index) digest와 아키텍처별 digest가 따로 있습니다. 승격과 배포에는 목록 digest를 씁니다. 시험에서 `crane copy`로 `busybox:1.37` 목록을 복사하자 원본과 같은 목록 digest가 나왔습니다.

```bash
crane digest registry.example.com/app:1.4.0          # sha256:...
crane digest --full-ref registry.example.com/app:1.4.0
docker buildx imagetools inspect registry.example.com/app:1.4.0
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 태그 규칙

| 태그 종류    | 예              | 바꿔도 되는가 | 설명                                         |
|--------------|-----------------|---------------|----------------------------------------------|
| 불변 판 태그 | `1.4.0-3f2a9c1` | 아니오        | 빌드마다 하나, commit까지 포함해 겹치지 않음 |
| 판 태그      | `1.4.0`         | 아니오        | 릴리스 판                                    |
| 단계 태그    | `qa`, `prod`    | 예            | 지금 그 단계에 있는 판 표시                  |
| 이동 태그    | `latest`, `1.4` | 예            | 편의용, 운영 배포에는 쓰지 않음              |

- 태그는 영문·숫자·`_`·`.`·`-`로 최대 128자이며 `+`를 쓸 수 없습니다. SemVer build metadata(`1.4.0+3f2a9c1`) 대신 `-`를 씁니다.
- 바꾸지 않을 태그와 바꿔도 되는 태그를 이름 규칙으로 나누면, 레지스트리의 불변 규칙에서 예외 패턴을 쉽게 정할 수 있습니다(8절).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 출처 라벨

OCI 표준 라벨(annotation 키)에 판, commit, 빌드 시각, 기반 이미지를 넣습니다.

```bash
docker buildx build \
  --label org.opencontainers.image.version=1.4.0 \
  --label org.opencontainers.image.revision=$(git rev-parse --short HEAD) \
  --label org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --label org.opencontainers.image.source=https://git.example.com/team/app \
  --label org.opencontainers.image.base.name=docker.io/library/busybox:1.37 \
  -t registry.example.com/app:1.4.0-$(git rev-parse --short HEAD) --push .
```

| 키                                                 | 내용                |
|----------------------------------------------------|---------------------|
| `org.opencontainers.image.version`                 | 판 번호             |
| `org.opencontainers.image.revision`                | 빌드 commit         |
| `org.opencontainers.image.created`                 | 빌드 시각(RFC 3339) |
| `org.opencontainers.image.source`                  | 소스 저장소 주소    |
| `org.opencontainers.image.base.name`·`base.digest` | 기반 이미지         |

시험은 빌드 대신 `crane mutate`로 라벨을 붙였습니다.

```bash
crane mutate reg-dev:5000/base/busybox:1.37 --platform linux/amd64 \
  --label org.opencontainers.image.version=1.4.0 \
  --label org.opencontainers.image.revision=3f2a9c1 \
  -t reg-dev:5000/app:1.4.0-3f2a9c1
crane config reg-dev:5000/app:1.4.0-3f2a9c1      # config.Labels에 값 확인
```

- 라벨은 이미지를 받는 누구나 볼 수 있습니다. 비공개 저장소 주소나 내부 이름을 넣어야 한다면 공개 레지스트리에 올리지 않는지 확인합니다.
- BuildKit의 `--provenance`·`--sbom` 빌드 증명 기능도 있으나 이 문서에서는 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 승격 방법

### 5.1 같은 레지스트리에서 단계 태그 추가

```bash
D=$(crane digest reg-dev:5000/app:1.4.0-3f2a9c1)
crane tag reg-dev:5000/app@$D qa       # 레이어를 받지 않고 태그만 추가
crane ls reg-dev:5000/app              # 1.4.0-3f2a9c1, qa
```

### 5.2 다른 레지스트리로 digest 복사

```bash
crane copy reg-dev:5000/app@$D reg-prod:5000/app:1.4.0
crane digest reg-prod:5000/app:1.4.0   # $D와 같아야 함
```

```text
reg-prod:5000/app:1.4.0: digest: sha256:9deaef37...  size: 546
prod 1.4.0 sha256:9deaef37...
```

| 도구          | 명령 예                                                          | 특징                                  |
|---------------|------------------------------------------------------------------|---------------------------------------|
| crane         | `crane copy SRC@DIGEST DST:TAG`                                  | digest 유지, `-n`으로 기존 태그 보호  |
| skopeo        | `skopeo copy --all --preserve-digests docker://SRC docker://DST` | 유지 못 하면 실패, `sync`로 여러 태그 |
| docker buildx | `docker buildx imagetools create -t DST SRC@DIGEST`              | Docker만 있는 환경                    |
| oras          | `oras copy -r SRC DST`                                           | 서명 등 연결된 artifact까지 복사      |

- 승격 원본은 태그가 아니라 digest로 지정합니다. 승격 도중 원본 태그가 바뀌어도 시험한 이미지가 올라갑니다.
- `crane copy -n`은 대상 태그가 이미 있으면 거부합니다. 시험에서는 대상 태그가 같은 digest를 가리킬 때도 "refusing to clobber existing tag"로 rc=1이었습니다. 승격 작업을 다시 실행할 수 있게 하려면 먼저 대상 digest를 비교해 같으면 건너뜁니다.

```bash
if [ "$(crane digest reg-prod:5000/app:1.4.0 2>/dev/null)" = "$D" ]; then
  echo "already promoted"
else
  crane copy -n reg-dev:5000/app@$D reg-prod:5000/app:1.4.0
fi
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 배포에서 digest 고정

```yaml
# Kubernetes: 태그와 digest를 함께 쓰면 digest로 받음
containers:
  - name: app
    image: registry.example.com/app:1.4.0@sha256:9deaef37429b6c901ba7bd8d210642f4f86982a61bb52262955c5864d34b91e4
```

```yaml
# kustomization.yaml
images:
  - name: registry.example.com/app
    digest: sha256:9deaef37429b6c901ba7bd8d210642f4f86982a61bb52262955c5864d34b91e4
```

- 태그를 함께 적으면 사람이 판을 알아보기 쉽고, 실제로 받는 이미지는 digest가 정합니다.
- GitOps라면 승격 단계에서 배포 저장소의 digest 값을 바꾸는 commit을 만듭니다([Argo CD](../cicd/argocd.md), [FluxCD](../cicd/fluxcd.md)).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 서명과 SBOM

### 7.1 키 만들기와 서명

```bash
cosign generate-key-pair                         # cosign.key(비밀번호로 암호화), cosign.pub
cosign signing-config create --out no-tlog.json  # 공개 투명성 로그를 쓰지 않는 설정
cosign sign --key cosign.key --signing-config no-tlog.json -y reg-dev:5000/app@$D
cosign verify --key cosign.pub --insecure-ignore-tlog reg-dev:5000/app@$D
```

- cosign v3.1.6에서 `--tlog-upload=false`는 deprecated이고, 그대로 쓰면 "--tlog-upload=false is not supported with --signing-config or --use-signing-config" 오류로 서명하지 않았습니다. 공개 투명성 로그(Rekor)에 올리지 않으려면 서비스를 비운 signing config를 `--signing-config`로 줍니다.
- 투명성 로그 없이 서명한 이미지는 검증할 때 `--insecure-ignore-tlog`가 필요합니다. 빼면 "not enough verified log entries from transparency log: 0 < 1"로 실패합니다.
- 공개 이미지라면 기본 설정(Rekor 기록, 키 없는 OIDC 서명)이 일반적입니다. 사내 이미지를 공개 로그에 남겨도 되는지는 조직 규칙에 따라 정합니다.
- `cosign.key`는 비밀값입니다. 저장소에 넣지 않고 CI 비밀 저장소나 KMS(`--key awskms://...` 등)를 씁니다. 키 비밀번호는 `COSIGN_PASSWORD` 환경 변수로 주며 로그에 남기지 않습니다.
- 태그로 서명해도 cosign은 태그가 가리키는 digest에 서명을 붙였습니다(시험에서 태그 서명과 digest 서명이 같은 digest 아래 두 개로 보임). 태그가 바뀌는 사이의 혼동을 피하려면 digest로 서명합니다.

### 7.2 서명이 저장되는 곳

```text
$ crane ls reg-dev:5000/app
1.4.0-3f2a9c1
qa
sha256-9deaef37429b6c901ba7bd8d210642f4f86982a61bb52262955c5864d34b91e4   ← 서명·증명 목록
```

- cosign v3은 OCI 1.1 referrer 방식으로 서명을 붙입니다. 시험한 registry 3.1.2는 referrers API가 없어(`/v2/<repo>/referrers/<digest>` 404) `sha256-<digest>` 태그로 대신 저장됐습니다. referrers API를 지원하는 레지스트리는 이 태그 없이 연결됩니다.
- `cosign tree <image>@<digest>`로 붙은 서명과 증명을 볼 수 있습니다.

### 7.3 SBOM 만들고 증명으로 붙이기

```bash
syft registry:reg-dev:5000/app@$D -o spdx-json=sbom.spdx.json
cosign attest --key cosign.key --signing-config no-tlog.json -y \
  --type spdxjson --predicate sbom.spdx.json reg-dev:5000/app@$D
cosign verify-attestation --key cosign.pub --insecure-ignore-tlog --type spdxjson reg-dev:5000/app@$D
```

- 시험에서 SPDX-2.3 SBOM이 만들어졌고, 증명 payload의 subject digest가 이미지 digest와 같았습니다.
- `--type`은 spdx, spdxjson, cyclonedx, slsaprovenance, openvex 등을 받습니다.

### 7.4 승격할 때 서명도 옮기기

| 방법                                  | 결과(시험)                                               |
|---------------------------------------|----------------------------------------------------------|
| `crane copy`로 이미지만 복사          | 운영 쪽 `cosign verify`가 "no signatures found"          |
| `sha256-<digest>` 태그도 `crane copy` | 운영 쪽 서명·SPDX 증명 검증 통과                         |
| `oras copy -r`                        | cosign이 안내하는 대안, 연결된 artifact까지 복사(미시험) |
| `cosign copy`                         | v3에서 deprecated                                        |

- 서명은 digest에 붙으므로 레지스트리를 옮겨도 같은 공개 키로 검증됩니다. 다른 키로 검증하면 "accepted signatures do not match threshold"로 실패했습니다.
- 운영 배포 직전 단계(또는 클러스터의 admission 정책)에서 서명 검증을 실패 조건으로 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 덮어쓰기 막기

| 레지스트리             | 설정                                                          | 예외                                         |
|------------------------|---------------------------------------------------------------|----------------------------------------------|
| distribution(registry) | 태그 불변 기능 없음                                           | 도구에서 `crane copy -n` 등으로 막기         |
| Harbor                 | 프로젝트별 태그 불변 규칙(저장소·태그 패턴, 최대 15개)        | excluding 패턴(예: `latest`, `qa`)           |
| AWS ECR                | 저장소 `IMMUTABLE`, 예외 필터 있는 `IMMUTABLE_WITH_EXCLUSION` | 와일드카드 필터                              |
| Nexus Docker hosted    | `writePolicy: allow_once`                                     | `latestPolicy`로 `latest`만 다시 올리기 허용 |

- 단계 태그(`qa`, `prod`)를 쓰는 방식이라면 불변 규칙에서 단계 태그를 예외로 둡니다. 판 태그(`1.4.0`, `1.4.0-<commit>`)는 불변으로 둡니다.
- Harbor 불변 태그는 삭제, 다시 올리기, 태그 변경, 복제로도 바뀌지 않습니다. ECR은 덮어쓰려 하면 `ImageTagAlreadyExistsException`을 냅니다. 두 기능은 시험하지 않았습니다.
- Nexus의 `allow_once` 재배포 거부(409)는 [Nexus 문서](../cicd/nexus.md#7-검증)에서 시험했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 정리

```bash
crane delete reg-dev:5000/app@<지울 digest>        # manifest 삭제(태그도 사라짐)
# 레지스트리 컨테이너 안에서: 먼저 dry run
registry garbage-collect --dry-run --delete-untagged /etc/distribution/config.yml
registry garbage-collect --delete-untagged /etc/distribution/config.yml
```

- distribution 레지스트리는 삭제를 켜야(`REGISTRY_STORAGE_DELETE_ENABLED=true`) manifest를 지울 수 있고, 공간은 garbage collection을 실행해야 비워집니다. 공식 문서는 GC 동안 레지스트리를 읽기 전용 모드로 두거나 멈추라고 안내합니다(stop-the-world 방식).
- 시험에서 태그 하나를 지운 뒤 GC를 실행해도 `sha256-<digest>` 태그로 저장된 서명은 남았고 검증이 통과했습니다. referrers API로만 연결된(태그 없는) 서명은 `--delete-untagged`의 대상이 될 수 있으니, 그런 레지스트리에서는 dry run 목록에서 서명 manifest가 지워지는지 먼저 봅니다.

| 레지스트리 | 정리 기능                                                                                                                                                 |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Harbor     | 보존 규칙(최근 N개, N일 안에 올림·받음, 태그 패턴, 태그 없는 artifact), Dry Run, 실행 뒤 되돌릴 수 없음. GC 따로, GC로 지운 artifact의 서명도 함께 지워짐 |
| AWS ECR    | 수명 주기 규칙(`imageCountMoreThan`, `sinceImagePushed`, `sinceImagePulled`, 태그 패턴), 24시간 안 처리, 만료·보관                                        |
| Nexus      | 정리 정책 + `Docker - Delete unused manifests and images` 작업([Nexus 문서](../cicd/nexus.md#6-운영))                                                     |

- 정리 규칙에서 운영 배포 중인 판을 보호합니다. 패턴으로 보호하려면 3절의 태그 규칙이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용           | 방법                                              | 기대 결과             |
|------|---------------------|---------------------------------------------------|-----------------------|
| 1    | 승격 전후 같은 파일 | `crane digest` 원본·대상                          | 같은 digest           |
| 2    | 출처 라벨           | `crane config <image>`의 `config.Labels`          | 판·commit·시각        |
| 3    | 서명                | `cosign verify --key cosign.pub <image>@<digest>` | 종료 코드 0           |
| 4    | 다른 키 거부        | 다른 공개 키로 검증                               | 실패                  |
| 5    | SBOM 증명           | `cosign verify-attestation --type spdxjson ...`   | 종료 코드 0           |
| 6    | 배포 설정           | 매니페스트의 `image:`                             | `@sha256:` 포함       |
| 7    | 정리 미리 보기      | GC·보존 규칙 dry run                              | 운영 판이 목록에 없음 |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

| 증상                                              | 원인                                             | 조치                                                     |
|---------------------------------------------------|--------------------------------------------------|----------------------------------------------------------|
| 운영 레지스트리에서 `no signatures found`         | 이미지만 복사, 서명 artifact 미복사              | `sha256-<digest>` 태그나 referrer도 복사(`oras copy -r`) |
| `--tlog-upload=false is not supported ...`        | cosign v3 기본 signing config                    | 서비스를 비운 signing config를 `--signing-config`로      |
| `not enough verified log entries ... 0 < 1`       | 투명성 로그 없이 서명한 이미지                   | `--insecure-ignore-tlog`(조직 규칙 확인)                 |
| `refusing to clobber existing tag`                | `crane copy -n`, 대상 태그 있음(같은 digest여도) | 먼저 digest 비교, 같으면 건너뜀                          |
| 같은 태그인데 서버마다 다른 이미지                | 태그 덮어쓰기                                    | digest 고정 배포, 레지스트리 불변 규칙                   |
| 삭제했는데 디스크가 그대로                        | GC 미실행                                        | dry run 뒤 GC                                            |
| `http: server gave HTTP response to HTTPS client` | HTTP 레지스트리                                  | 시험 환경만 `--insecure`, 운영은 HTTPS                   |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [이미지 판 관리와 단계별 승격](../cicd/image_versioning_and_promotion.md) — 원칙
- [VM 이미지 판 관리](../iac/vm_image_versioning.md) — 같은 원칙의 VM판
- [이미지 관리 도구 비교](../cicd/image_management_tools_comparison.md) — Harbor, 클라우드 레지스트리
- [Dockerfile 작성과 빌드](./dockerfile_best_practices.md) — 기반 이미지 digest 고정
- [Nexus Repository](../cicd/nexus.md) · [Kubernetes 비밀값 관리](../../04_security/cloud/kubernetes_secrets_management.md)

---

## 참고 자료

- go-containerregistry: [crane copy](https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane_copy.md) · [crane tag](https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane_tag.md) — ★★★☆☆
- skopeo: [skopeo-copy](https://github.com/containers/skopeo/blob/main/docs/skopeo-copy.1.md) · [skopeo-sync](https://github.com/containers/skopeo/blob/main/docs/skopeo-sync.1.md) — ★★★☆☆
- Sigstore: [Signing containers](https://docs.sigstore.dev/cosign/signing/signing_with_containers/) · [Verifying](https://docs.sigstore.dev/cosign/verifying/verify/) · [cosign releases](https://github.com/sigstore/cosign/releases) — ★★★☆☆
- [Syft](https://github.com/anchore/syft) · [OCI image annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md) · [distribution garbage collection](https://distribution.github.io/distribution/about/garbage-collection/) — ★★★☆☆
- AWS ECR: [Tag mutability](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html) · [Lifecycle policies](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html) — ★★★☆☆

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
