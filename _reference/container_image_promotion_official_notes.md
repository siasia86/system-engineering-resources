---
name: container-image-promotion-official-notes
description: crane·skopeo 복사, cosign v3 서명·증명, Syft SBOM, ECR 태그 불변·수명 주기 규칙과 로컬 레지스트리 시험 결과 정리.
tags:
  - container
  - registry
  - cosign
  - sbom
last_checked: 2026-11-27
sources:
  - https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane_copy.md
  - https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane_tag.md
  - https://github.com/containers/skopeo/blob/main/docs/skopeo-copy.1.md
  - https://github.com/containers/skopeo/blob/main/docs/skopeo-sync.1.md
  - https://docs.sigstore.dev/cosign/signing/signing_with_containers/
  - https://docs.sigstore.dev/cosign/verifying/verify/
  - https://github.com/anchore/syft
  - https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html
  - https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html
  - https://distribution.github.io/distribution/about/garbage-collection/
---

# 컨테이너 이미지 승격 공식 자료 참조 노트

## 1. 판 (2026-11-27 GitHub API 확인)

- crane v0.22.1(2026-09-04), skopeo v1.25.2(2026-11-16), cosign v3.1.6(2026-11-25), syft v1.57.2(2026-11-16), distribution(registry) v3.1.2(2026-09-24), oras v1.4.0(2026-11-17).
- 내려받은 crane·cosign·syft는 각 릴리스의 checksums 파일과 sha256 일치.

## 2. 복사 도구

- `crane copy SRC DST`: "retaining the digest value". `-a/--all-tags`, `-n/--no-clobber`.
- `crane tag IMG TAG`: "Tag remote image without downloading it."
- `skopeo copy --all`(목록과 모든 이미지), `--preserve-digests`(유지 못 하면 실패), `--multi-arch`. `skopeo sync`는 태그를 지정하지 않으면 모든 태그 복사, `--dry-run`, `--digestfile`.

## 3. cosign v3.1.6 (도움말과 시험)

- 서명은 OCI 1.1 referrer 방식. 키 방식(`--key cosign.key`)은 계속 지원.
- `--tlog-upload` deprecated. 기본 signing config와 함께 쓰면 "--tlog-upload=false is not supported with --signing-config or --use-signing-config" 오류.
- `cosign signing-config create --out no-tlog.json`(서비스 지정 없음)으로 만든 설정을 `--signing-config`로 주면 투명성 로그 없이 서명됨.
- 검증 때 `--insecure-ignore-tlog`가 없으면 "not enough verified log entries from transparency log: 0 < 1"로 실패.
- `cosign copy`는 deprecated, 대안으로 `oras copy -r`, `cosign save`/`cosign load`, `cosign download`/`cosign attach` 안내.
- `cosign attest --type`: slsaprovenance, slsaprovenance02, slsaprovenance1, link, spdx, spdxjson, cyclonedx, vuln, openvex, custom 또는 URI.

## 4. Syft

- `syft <image> -o spdx-json=./spdx.json -o cyclonedx-json=./cdx.json`. 시험에서 `registry:` 접두사와 `SYFT_REGISTRY_INSECURE_USE_HTTP=true`로 HTTP 레지스트리 이미지를 직접 읽음(SPDX-2.3).

## 5. ECR

- 저장소 단위 `MUTABLE`/`IMMUTABLE`, 예외 필터(`IMMUTABLE_WITH_EXCLUSION` 등, 와일드카드). 덮어쓰기 시 `ImageTagAlreadyExistsException`.
- 수명 주기 규칙: `tagPatternList`나 `tagPrefixList`(둘 중 하나) 사용 시 `tagStatus`는 `tagged`. countType `imageCountMoreThan`, `sinceImagePushed`, `sinceImagePulled`, `sinceImageTransitioned`. 처리는 24시간 안. 만료(expire)와 보관(archive)이 있음. JSON 전체 형식은 미확인.

## 6. 시험 (registry:3.1.2 두 개, python:3.13-slim 도구 컨테이너)

- Docker Hub `busybox:1.37` 목록(index)을 `crane copy`로 복사해 digest 같음.
- `crane mutate --label`로 OCI 라벨(version, revision, created, base.name)을 넣은 이미지를 만들고, `crane tag`로 같은 digest에 태그 2개 추가, `crane copy`로 다른 레지스트리에 같은 digest로 승격.
- 같은 태그에 다른 이미지를 올리면 registry는 덮어씀. digest 조회는 원래 이미지.
- `crane copy -n`은 대상 태그가 같은 digest를 가리켜도 "refusing to clobber existing tag"로 rc=1.
- 서명·증명은 registry 3.1.2에 referrers API가 없어(404) `sha256-<digest>` 태그로 저장됨. `crane copy`로 이미지만 옮기면 대상에서 "no signatures found". 이 태그도 `crane copy`하면 대상에서 서명·SPDX 증명 검증 통과.
- 다른 공개 키로 검증하면 "accepted signatures do not match threshold".
- 태그 삭제 뒤 `registry garbage-collect --delete-untagged` 실행, 서명 태그는 남고 검증 통과.
- distribution GC 문서: GC 동안 레지스트리를 "read-only mode or not running" 상태로 둠(stop-the-world), `--delete-untagged`는 태그가 참조하지 않는 manifest 삭제.
