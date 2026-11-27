---
name: chef-official-notes
description: Chef Infra Client 19.5.19 판, 19의 라이선스 키 조건, Habitat 패키지 전환과 18과의 차이 정리.
tags:
  - chef
  - configuration-management
last_checked: 2026-11-27
sources:
  - https://github.com/chef/chef/tags
  - https://docs.chef.io/client/19/license/
  - https://docs.chef.io/client/19/reference/ctl_chef_client/
  - https://www.chef.io/blog/what-s-the-difference-between-progress-chef-infra-client-18-and-19
---

# Chef 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- GitHub `chef/chef` 최신 태그 v19.5.19(태그 날짜 2026-11-24). GitHub 릴리스 목록은 v15.8.23(2020)에서 멈춰 판 확인에 쓰지 않음.
- 저장소 라이선스 Apache-2.0.

## 2. Infra Client 19 라이선스 (docs.chef.io/client/19/license/)

- 공식 배포판을 받아 실행할 때는 키 검사가 없음. 비공식 경로(공개 Ruby gem)와 실행 중 설치 방식은 키 필요.
- 블로그(2026-04-21): "All downloads of Chef Infra Client 19 official distributions require authentication using a Chef License Key."
- 키 지정: `CHEF_LICENSE_KEY` 환경 변수, `chef-client --chef-license-key=<LICENSE_KEY>`, 대화형 입력. "After setting a license key, Chef Infra Client validates it with Progress Chef's licensing service."
- EULA 동의는 별개: `--chef-license accept|accept-silent|accept-no-persist`, `CHEF_LICENSE`, `client.rb`의 `chef_license`.
- 무료·체험 키의 노드 수 제한은 공식 문서에서 찾지 못함(미확인).

## 3. 18과 19 차이 (블로그 2026-04-21)

- 패키지 이름 `chef`(18) → `chef-ice`(19). omnibus → Habitat 기반.
- 설치 경로 `/opt/chef`(18) → `/hab/pkgs/chef/chef-infra-client`, `/hab/bin`에 링크.
- 디스크 Linux 600MB, Windows 2.1GB. 이전 도구 `migrate-ice`.
- Ruby 3.1.x → 3.4.8. AIX·Solaris 로컬 설치 중단(target mode만), Intel macOS 미지원.
- Workstation 26 이상 필요. 19.1 기준 Linux ARM·SELinux는 19.2, FIPS는 19.3 예정.
- 18의 지원 종료일은 이 글에서 찾지 못함.

## 4. 명령

- `chef-client --local-mode`(`-z`)와 chef-zero가 19 참조 문서에 있음(요약 근거). `--why-run`은 라이선스 문서 예시(`chef-client --local-mode --why-run`)에 있음.
- 19 참조 메뉴: chef-client, chef-solo, ohai, supermarket-ctl. `chef-apply`는 메뉴에 없음.

## 5. 시험

- 미실행. 내려받기에 라이선스 키가 필요해 컨테이너 시험을 하지 않음.
