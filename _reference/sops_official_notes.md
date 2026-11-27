---
name: sops-official-notes
description: SOPS v3.13.3·age v1.3.2 판, .sops.yaml 설정 키, age 키 위치, updatekeys·rotate, 컨테이너 시험 결과 정리.
tags:
  - sops
  - age
  - secrets
last_checked: 2026-11-27
sources:
  - https://github.com/getsops/sops/releases
  - https://github.com/FiloSottile/age/releases
  - https://getsops.io/docs/
  - https://getsops.io/docs/usage/identities/age/
  - https://getsops.io/docs/usage/identities/config-file/
  - https://getsops.io/docs/usage/key-management/
---

# SOPS 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- SOPS 최신 v3.13.3(2026-07-23). 이전 v3.13.2(06-30), v3.13.1(05-16), v3.13.0(05-08).
- age 최신 v1.3.2(2026-08-29). 이전 v1.3.1(2025-12-28), v1.3.0(2025-12-27).
- SOPS 릴리스에는 `sops-v<판>.checksums.txt`가 있고, age 릴리스에는 체크섬 파일 대신 자산별 `.proof` 파일과 GitHub 자산 digest가 있음.
- 시험한 체크섬: `sops-v3.13.3.linux.amd64` 체크섬 파일과 일치. `age-v1.3.2-linux-amd64.tar.gz` sha256 `cbe24006683f8eb669266162894b9a522a1af52f2665fbc63a4bb032ed26ac10`(GitHub digest와 일치).
- 라이선스 MPL 2.0, CNCF Sandbox(2023~).

## 2. 키 방식과 설정

- 소개 문서: "encrypts with AWS KMS, GCP KMS, Azure Key Vault, HuaweiCloud KMS, age, and PGP". 메뉴에 HashiCorp Vault / OpenBao.
- `.sops.yaml`: 이름이 정확히 `.sops.yaml`이어야 함("Other names (i.e. .sops.yml) won't be automatically discovered"). creation rule은 위에서부터 보고 처음 맞는 규칙을 씀.
- v3.13.3 `config/config.go`의 설정 키: `path_regex`, `age`, `pgp`, `kms`, `gcp_kms`, `azure_keyvault`, `hckms`, `hc_vault_transit_uri`, `key_groups`, `shamir_threshold`, `encrypted_regex`, `unencrypted_regex`, `encrypted_suffix`, `unencrypted_suffix`, `encrypted_comment_regex`, `unencrypted_comment_regex`, `mac_only_encrypted`, `destination_rules`, `stores` 등.
- `sops.go`: `DefaultUnencryptedSuffix = "_unencrypted"`.
- age 키 기본 위치(Linux): `$XDG_CONFIG_HOME/sops/age/keys.txt`, 없으면 `$HOME/.config/sops/age/keys.txt`. 문서는 `SOPS_AGE_KEY_FILE`이 기본 위치를 대신한다고 설명하나, 3절 시험에서는 함께 읽혔음.
- `updatekeys`: `.sops.yaml`에 맞춰 받는 사람을 추가·삭제. `rotate`: 새 데이터 키로 모든 값을 다시 암호화, `-i`로 제자리 저장.
- 공식 문서의 common operations 페이지에서 `exec-env`·`exec-file` 설명은 찾지 못함. 실행 파일 도움말(`sops exec-env --help`)로 확인.

## 3. 컨테이너 시험 (2026-11-27, Debian 13)

- `encrypted_regex: ^(password|token)$`: 해당 키만 `ENC[AES256_GCM,...]`, 나머지 평문.
- `decrypt --extract`, `set`, `EDITOR`를 바꾼 `edit`, `filestatus`, `--output-type json` 동작.
- `.sops.yaml`이 있고 맞는 규칙이 없으면 `--age`를 줘도 `error loading config: no matching creation rules found`(종료 코드 1). `--config /dev/null`이면 성공.
- `exec-env`에 중첩 YAML: `cannot use complex value in environment; offending key db`(종료 코드 1). dotenv 파일은 동작.
- `updatekeys -y`: recipient 2개, 두 번째 키로 복호화 성공. `rotate -i`: 값 암호문과 감싼 키 모두 바뀜.
- 기본 위치에 맞는 키가 있으면 `SOPS_AGE_KEY_FILE`에 틀린 키를 줘도 복호화 성공(종료 코드 0). 기본 키를 치우면 `Recovery failed because no master key was able to decrypt the file`(종료 코드 128).
- `SOPS_AGE_KEY`에 비밀키 문자열: 복호화 성공.
- 평문 값을 손으로 바꾸면 `MAC mismatch`(종료 코드 51), `--ignore-mac`은 종료 코드 0.
- 미실행: PGP, 클라우드 KMS, Vault, key_groups·shamir_threshold, textconv.
