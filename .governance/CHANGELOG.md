# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

---

## [Unreleased]

- HL-01 하네스·루프 엔지니어링 보강 (2026-11-28, 사용자 직접 요청, 사용자 확인 "push 진행"): 1차 자료 12개(Hashimoto, OpenAI, Böckeler, LangChain, Anthropic 4편, Osmani 3편, Huntley)를 원문으로 대조해 [1차 자료 대조 노트](../_reference/harness_loop_engineering_sources_notes.md)를 쓰고, [Harness Engineering](../06_career/ai_tools/harness_engineering.md)에서 OpenAI 사례 인원(3명→7명)·6시간 문구를 정정하고 용어 기원·이름 구분·Böckeler 틀·Anthropic 장기 실행 패턴·걷어내기 원칙·통제 점검표·트러블슈팅을, [Loop Engineering](../06_career/ai_tools/loop_engineering.md)에 원문 날짜·Ralph 루프와 상한 있는 예제·정지 조건 작성 기준을 더함. 새 개념 문서는 기존 문서와 겹쳐 만들지 않음. Google Cloud 정의 페이지와 arXiv 정의는 미확인.

- DO-11 Windows sysprep 골든 이미지 (2026-11-28, 04 세션 직접 요청 DO-11, 이 세션 사용자 확인 "push 진행"): [Windows 골든 이미지와 sysprep](../02_infrastructure/windows_server/windows_golden_image_sysprep.md)(Packer hyperv-iso 흐름, autounattend·unattend 예제, WinRM 끊김을 피하는 예약 작업 방식, 비밀번호가 남는 곳, 결과물 보관과 검증 순서, 문제 해결)과 참조 노트 2개([sysprep](../_reference/windows_sysprep_official_notes.md), [무인 설치 응답 파일](../_reference/windows_unattend_answer_file_official_notes.md))를 쓰고 Packer·Hyper-V 문서를 연결함. 실제 빌드 결과는 04의 [보고]로만 적었고 이 저장소에서는 HCL·XML·PowerShell 구문 검사만 실행.

- DO-10 이미지 판 관리·승격 (2026-11-27, 00 세션 직접 요청 DO-10, 이 세션 사용자 확인 "진행하되 … 종속적인 내용이 있으면 안돼 … push 까지 진행"): [이미지 판 관리와 단계별 승격](../02_infrastructure/cicd/image_versioning_and_promotion.md)(불변 이미지, 판 번호 형식 제한, 출처 메타데이터, 한 번 빌드하고 승격, 보관·재빌드), [VM 이미지 판 관리](../02_infrastructure/iac/vm_image_versioning.md)(Vagrant 2.4.9 catalog 판 고정·조건 갱신·체크섬 거부, Packer 1.16.3 manifest·checksum 누적과 `-force`, catalog 갱신 스크립트), [컨테이너 이미지 승격](../02_infrastructure/containers/container_image_promotion.md)(registry 3.1.2 두 개로 digest 승격, 태그 덮어쓰기, `crane copy -n` 같은 digest 거부, cosign v3.1.6 signing config·서명 복사·SPDX 증명, GC), [이미지 관리 도구 비교](../02_infrastructure/cicd/image_management_tools_comparison.md)(HCP Packer, Harbor, AMI·Azure Compute Gallery·GCP, HCP Vagrant 2026-12-31 운영 종료)를 쓰고 참조 노트 5개와 Packer·Vagrant·Nexus·Dockerfile 문서 연결을 더함. 실제 VM 빌드, `vagrant up`, Harbor·ECR·HCP Packer는 미실행.

- DO-07 B24와 DO-07 완료 (2026-11-27, 00 세션 직접 요청 DO-07): [클라우드 설계 패턴](../03_engineering/reliability/cloud_design_patterns.md)에서 Azure Architecture Center 카탈로그 44개를 가용성·데이터 관리·설계와 구현·관리와 모니터링 4개 영역과 그 밖(메시징·보안)으로 정리하고, 현재 카탈로그의 Well-Architected 기둥 표기와 2014년판 8개 문제 영역을 대조했습니다. [Resilience Patterns](../03_engineering/reliability/resilience_patterns.md)와 서로 연결했고 참조 노트 1개를 추가했습니다. 이로써 roadmap.sh DevOps 108개 주제(1순위 37개, 2·3순위 71개)를 모두 마쳤습니다. B17~B24는 2026-11-27 사용자 지시("남은 작업도 사용자 승인 없이 계속 진행하여 마무리 할것")에 따라 묶음마다 묻지 않고 진행했습니다.

- DO-07 B23 프로그래밍 언어 (2026-11-27, 00 세션 직접 요청 DO-07): Python·Rust 기존 문서는 판 확인 결과 최신과 같아 보강하지 않았고, [Go 입문](../01_fundamentals/programming/go_for_se.md)·[Ruby 입문](../01_fundamentals/programming/ruby_for_se.md)·[Node.js 입문](../01_fundamentals/programming/nodejs_for_se.md)을 새로 썼습니다. 세 문서는 같은 호스트 목록 도구(인수 처리, JSON, 외부 명령, 제한 시간 있는 HTTP, 테스트)를 Go 1.27.4·Ruby 4.0.10·Node.js 26.13.1 공식 이미지에서 실행해 확인했고, 참조 노트 3개를 추가했습니다. 시험에서 Go 정적 빌드가 동적 링크 없이 7.2MB로 나오는 점, Ruby 4.0 기본 설치에 webrick이 없는 점, `npm init -y`가 `"type": "commonjs"`를 기록하는 점을 적었습니다.

- DO-07 B22 서버리스·PaaS (2026-11-27, 00 세션 직접 요청 DO-07): [서버리스 함수 비교](../02_infrastructure/cloud_aws/serverless_functions_comparison.md)에서 AWS Lambda·Azure Functions·Cloud Run functions의 무료 한도·실행 제한·콜드 스타트 대책을, [PaaS 비교](../02_infrastructure/cloud_aws/paas_comparison.md)에서 Cloudflare Workers·Vercel·Netlify·Render·Railway·Heroku의 무료 플랜 한도·잠듦·첫 유료 플랜을 공식 페이지로 대조했습니다. 참조 노트 2개를 추가했습니다. Lambda 표준 함수 최대 시간이 공식 문서에서 30분으로 표시된 점, Azure Linux Consumption 플랜이 2028-09-30 종료 예정인 점을 적었고, Google 요금·Azure 단가·무료 플랜 상업적 사용 조건은 읽지 못해 미확인으로 남겼습니다.

- DO-07 B21 클라우드와 AWS IaC (2026-11-27, 00 세션 직접 요청 DO-07): [AWS CDK와 CloudFormation](../02_infrastructure/iac/aws_cdk_cloudformation.md) 문서를 cfn-lint 1.61.0·CDK CLI 2.1149.0 컨테이너 시험(오류 코드 E3002·E3034·E6101, init·synth, 자격 증명 없는 diff 실패)과 함께 쓰고, 개요 문서가 없던 AWS에 [AWS 개요](../02_infrastructure/cloud_aws/aws_overview.md)를 새로 써 기존 AWS 문서 9개를 연결했으며, [클라우드 사업자 비교](../02_infrastructure/cloud_aws/cloud_provider_comparison.md)에서 Azure·Google Cloud·DigitalOcean·Alibaba Cloud·Hetzner를 공식 페이지로 대조했습니다. 참조 노트 3개를 추가했습니다. 시험에서 CDK CLI(`aws-cdk` 2.1xxx)와 라이브러리(`aws-cdk-lib` 2.2xx)의 판 번호가 달라 GitHub 릴리스 판으로 CLI를 설치하면 실패하는 점을 찾았고, 읽지 못한 가격 페이지는 미확인으로 남겼습니다.

- DO-07 B20 Kubernetes 비밀값 관리 (2026-11-27, 00 세션 직접 요청 DO-07): [Kubernetes 비밀값 관리](../04_security/cloud/kubernetes_secrets_management.md) 문서에서 Sealed Secrets·External Secrets Operator·Secrets Store CSI Driver와 클라우드별 도구(AWS ASCP, GKE Secret Manager 애드온, AKS Key Vault 애드온)를 비교했습니다. kind에서 Sealed Secrets v0.41.2(봉인·복원, strict 범위에서 다른 namespace 실패, 오프라인 봉인)와 ESO v2.15.0(Fake provider 동기화, 값 변경 갱신, 오류 시 마지막 값 유지, ExternalSecret 삭제 시 Secret 삭제)을 실행해 확인했고, 참조 노트 2개를 추가했습니다.

- DO-07 B19 프록시·서비스 메시 (2026-11-27, 00 세션 직접 요청 DO-07): [Envoy](../02_infrastructure/web_server/envoy.md) 문서를 v1.40.2 컨테이너 시험(설정 검증, 경로·80:20 가중치 라우팅, 능동 상태 검사, 처리율 제한, 관리 API)과 함께 쓰고, [서비스 메시 비교](../02_infrastructure/containers/service_mesh_comparison.md)에서 Istio·Linkerd·Consul의 데이터 플레인 구조, 배포·라이선스 조건, 판 지원을 공식 자료로 대조했습니다. 참조 노트 4개(envoy, istio, linkerd, consul)를 추가했습니다. 시험에서 상태 검사의 `no_traffic_interval`(기본 60초)을 정하지 않으면 멈춘 백엔드가 30초 동안 healthy로 남는 점을 찾아 적었고, Linkerd 안정 판이 2024-02부터 벤더 배포라는 점과 Consul이 BSL 1.1이라는 점을 비교 표에 넣었습니다.

- DO-07 B18 컨테이너 오케스트레이션 (2026-11-27, 00 세션 직접 요청 DO-07): [Docker Swarm](../02_infrastructure/containers/docker_swarm.md) 문서를 Engine 29.10.1 `docker:29-dind` 3노드 시험(routing mesh, 실패 시 자동 롤백, drain, secret·config, stack, manager 장애와 quorum 상실)과 함께 쓰고, [관리형 컨테이너 플랫폼 비교](../02_infrastructure/containers/managed_container_platforms.md)에서 EKS·GKE·AKS·ECS/Fargate·OpenShift의 요금과 Kubernetes 판 지원 정책을 공식 페이지로 대조했습니다. 참조 노트 2개를 추가했습니다. 시험에서 drain 뒤 active로 되돌려도 task가 돌아오지 않아 `service update --force`가 필요한 점, 자동 롤백 직후 수동 롤백이 `does not have a previous spec`로 실패하는 점을 찾았고, GKE 요금과 AKS Standard·Premium 금액은 페이지를 읽지 못해 미확인으로 남겼습니다.

- DO-07 B17 GitOps (2026-11-27, 00 세션 직접 요청 DO-07): [FluxCD](../02_infrastructure/cicd/fluxcd.md) 문서와 참조 노트를 새로 쓰고, [Argo CD](../02_infrastructure/cicd/argocd.md) 문서를 v3.6.3·Helm 차트 10.20.0으로 갱신해 server-side 매니페스트 설치, core 모드 조회, 판과 업그레이드 절(3.4→3.6), 함께 보기를 더했습니다. kind v0.33.0(Kubernetes v1.37.0) 단일 노드 클러스터에서 Flux v2.10.1(Git·Helm 배포, 드리프트 복구, suspend)과 Argo CD v3.6.3(자동 동기화, selfHeal)을 실행해 확인했고, [kind](../02_infrastructure/containers/kind.md) 문서의 시험 범위를 고쳤습니다. 시험에서 Argo CD를 일반 `kubectl apply`로 설치하면 CRD 주석 크기 제한으로 실패하는 점, `flux create helmrelease`에 `--wait`가 없는 점, `flux uninstall` 뒤에도 워크로드가 남는 점, metrics-server 없는 HPA 때문에 앱이 Degraded로 보이는 점을 찾아 적었습니다. 2026-11-27 사용자 지시("남은 작업도 사용자 승인 없이 계속 진행하여 마무리 할것")를 [인계](HANDOFF.md) 승인 범위에 기록했습니다.

- DO-07 B16 비밀값·IaC·설정 관리 (2026-11-27, 00 세션 직접 요청 DO-07): [SOPS](../02_infrastructure/iac/sops.md)와 [Pulumi](../02_infrastructure/iac/pulumi.md) 문서를 SOPS v3.13.3·age v1.3.2·Pulumi v3.278.0 컨테이너 시험(선택한 키만 암호화, updatekeys·rotate, MAC 불일치 탐지, 로컬 파일 backend, 패스프레이즈 비밀값, 상태 파일 구조)과 함께 쓰고, [설정 관리 도구 비교](../02_infrastructure/iac/config_management_comparison.md)에서 Ansible·Chef·Puppet·Salt를 비교했습니다. Puppet 예시는 OpenVox 8.34.0, Salt 예시는 3008.5 onedir로 실행했고 Chef는 라이선스 키가 필요해 미실행입니다. 참조 노트 5개(sops, pulumi, chef, puppet_openvox, salt)를 추가했습니다. 시험에서 `.sops.yaml`에 맞는 규칙이 없으면 `--age`를 줘도 실패하는 점, `SOPS_AGE_KEY_FILE`을 줘도 기본 위치의 키를 함께 읽는 점, Python 3.13에서 `pip install salt`가 실패하는 점을 찾아 적었습니다.

- Claude Code의 Code Mode·Projects 문서 (2026-11-26, 05 총괄 배정 D187: 사용자 지시 "32 repo (세션)에 요청 하는 방향으로 작업 진행 후 파일 생성까지"): 사용자가 말한 "claude code mode"를 공식 문서의 실험 기능 Code Mode로, "프로젝트 모드"를 Projects(beta)로 정하고 [Code Mode](../06_career/ai_tools/claude/claude_code_mode.md)와 [Projects](../06_career/ai_tools/claude/claude_code_projects.md) 문서를 새로 만들었습니다. Code Mode 문서 1절에 Code 탭·권한 모드·plan 모드·fast mode·Projects와의 이름 구분 표를 두었고, [데스크톱 앱](../06_career/ai_tools/claude/claude_code_desktop_guide.md) 8절에 링크를, [참조 노트](../_reference/claude_code_official_notes.md)에 Code Mode 항목과 Projects 추가 확인을 더했습니다. 두 기능 모두 실행 시험은 하지 않았습니다.

- gitleaks 대형 저장소 검사 보강 (2026-11-26, 30 세션 요청: 사용자 지시 "32 repo 에 있는 문서에 없다면, 추가 작성"): [gitleaks 가이드](../04_security/hardening/gitleaks_guide.md) 3절에 경로 인자 검사, 압축 포함 이력 전체 검사의 메모리 실측(다른 세션 보고 1건), 범위·깊이·파일 크기로 나눠 검사하는 방법, 종료 코드 137을 미검사로 다루는 기준, `--redact` 없는 보고서에 원문이 남는 점을 더했습니다. 가짜 토큰 저장소로 v8.30.1 옵션 동작을 시험해 `A..B`가 시작 커밋을 빼므로 첫 구간은 `<B>`만 써야 하는 점을 찾았습니다.

- ART-01 Blender 3순위 문서 (2026-11-26, 사용자 직접 요청): [Python 스크립트](../08_art/blender/blender_python_scripting.md)·[명령줄과 일괄 렌더](../08_art/blender/blender_cli_batch_render.md)·[애드온](../08_art/blender/blender_addons.md)·[트러블슈팅](../08_art/blender/blender_troubleshooting.md) 문서 4개를 추가해 ART-01 16개를 끝냈습니다. 공식 내려받기 폴더가 열려 Linux 압축판(sha256 확인)을 컨테이너에서 실행해 확인했고, [설치](../08_art/blender/blender_install.md) 문서와 [참조 노트](../_reference/blender_official_notes.md)의 미확인이던 파일 이름·체크섬을 채웠습니다. 시험에서 스크립트 예외가 종료 코드 0으로 끝나는 점, `-o`를 파일 앞에 두면 무시되는 점, `--addons`는 이번 실행에만 켜는 점, 자동 실행을 켜는 옵션이 대문자 `-Y`가 아니라 소문자 `-y`인 점을 찾아 적었습니다.

- DO-07 B15 관측 도구 (2026-11-26, 00 세션 직접 요청 DO-07): [OpenTelemetry](../02_infrastructure/monitoring/opentelemetry.md)와 [Jaeger](../02_infrastructure/monitoring/jaeger.md) 문서를 Collector v0.166.0·Jaeger v2.23.0·Python SDK 1.45.2 컨테이너 시험(OTLP/HTTP 수신, tail sampling으로 오류 트레이스만 남김, Badger 재시작 보존, v3 API)과 함께 쓰고, [모니터링 SaaS 비교](../02_infrastructure/monitoring/monitoring_saas_comparison.md)에 New Relic·Dynatrace 열과 비용, OpenTelemetry로 SaaS에 보내는 절을 더했습니다. 참조 노트 4개(opentelemetry, jaeger, new_relic, dynatrace)를 추가했습니다. 시험에서 Collector 0.166.0의 구성 요소 이름이 밑줄 형식(`otlp_grpc`, `host_metrics`)으로 바뀌어 예전 이름에 deprecated 경고가 나는 점과 Jaeger v2.21.0부터 v1 HTTP 경로(`/api/services`)가 404인 점을 찾아 적었습니다. New Relic CCU 단가와 Dynatrace 요청 제한·Managed URL은 미확인으로 남겼습니다.

- DO-07 B14 CI/CD 도구 (2026-11-26, 00 세션 직접 요청 DO-07): [Jenkins 설치](../02_infrastructure/cicd/jenkins_install.md)에 Docker·플러그인 미리 설치·JCasC·백업과 복원·업그레이드 절을 2.580.3 컨테이너 시험(REST 빌드, `master.key` 유무 복원 비교)과 함께 보강하고, [GitLab CI/CD](../02_infrastructure/cicd/gitlab_ci.md)에 Runner 19.6.1 컨테이너 확인(`exec` 없음, `lint`)과 컴포넌트·`auto_cancel`·CI lint API를 더했습니다. [CI/CD 도구 비교](../02_infrastructure/cicd/ci_tools_comparison.md)와 참조 노트 5개(jenkins, teamcity, circleci, buildkite, octopus_deploy)를 추가했습니다. JCasC가 Pipeline 스크립트의 `${...}`를 지우는 문제를 시험으로 찾아 `^${...}` 이스케이프를 적었습니다. TeamCity Enterprise 가격, CircleCI 추가 사용자 비용, CircleCI Server 판은 미확인으로 남겼습니다.

- ART-01 Blender 2순위 문서 (2026-11-26, 사용자 직접 요청): UV와 텍스처링·조명과 렌더·애니메이션과 리깅·[지오메트리 노드](../08_art/blender/blender_geometry_nodes.md)·스컬프팅·[파일 형식](../08_art/blender/blender_file_formats.md) 문서 6개를 추가하고 참조 노트에 확인 결과를 덧붙였습니다. 모두 `bpy` 5.3.0 컨테이너 실행으로 기본값·동작을 확인했고, 5.3에서 지오메트리 노드 모디파이어 입력 접근 방식이 바뀐 점, glTF 기본값이 모디파이어를 적용하지 않는 점을 시험으로 찾아 반영했습니다. 화면 조작·GPU 렌더·외부 프로그램에서 열기는 시험하지 않았습니다.

- ART-01 Art 섹션과 Blender 1순위 문서 (2026-11-26, 사용자 직접 요청): 새 최상위 폴더 `08_art/`와 [Blender 설치](../08_art/blender/blender_install.md)·화면 구성·단축키·모델링 기초·모디파이어·재질과 셰이딩 문서 6개, [참조 노트](../_reference/blender_official_notes.md)를 추가했습니다. blender.org 계열 사이트가 자동 조회에 403이라 판은 GitHub 미러 태그·판 정의 헤더와 PyPI `bpy`로, 기본값·키맵·모디파이어·재질은 `bpy` 5.3.0 컨테이너 실행으로 확인했고 시스템 요구사항·LTS 지원 기간은 검색 요약으로만 확인했습니다. 5.3에서 메뉴의 Array가 노드 에셋으로 바뀌고 내장 Array가 Legacy로 표시되는 점을 반영했습니다. DO-07 B14는 조사까지만 하고 보류했습니다.

- DO-07 B13 아티팩트 저장소 문서 (2026-11-24, 00 세션 직접 요청 DO-07): [Nexus Repository](../02_infrastructure/cicd/nexus.md) 문서를 3.98.3 CE 컨테이너 시험(H2·PostgreSQL 17, raw·PyPI·Docker 저장소, 백업·복원)과 함께 쓰고, [아티팩트 저장소 비교](../02_infrastructure/cicd/artifact_repository_comparison.md)와 참조 노트 3개를 추가했습니다. CE EULA 수락은 사용자 승인 뒤 시험 컨테이너에서만 했습니다. Artifactory·Cloudsmith는 상용이라 실행하지 않았고, Cloudsmith 가격 페이지는 직접 열지 못해 미확인으로 남겼습니다.

- DO-07 B12 메일 문서 (2026-11-24, 00 세션 직접 요청 DO-07): [메일 프로토콜](../01_fundamentals/networking/mail_protocols.md), [메일 인증](../04_security/hardening/email_authentication.md) 문서와 참조 노트 2개를 Debian 13 컨테이너(Postfix·Dovecot·OpenDKIM·OpenDMARC·postgrey) 시험과 함께 썼습니다. DMARC는 RFC 7489를 대체한 RFC 9989~9991 기준입니다. 시험 DNS 구성에서 opendkim-testkey가 레코드를 찾지 못한 원인은 미확인으로 기록했습니다.

- DO-07 B11 프로토콜 기초 문서 (2026-11-23, 00 세션 직접 요청 DO-07): [OSI 모델](../01_fundamentals/networking/osi_model.md), [HTTP와 HTTPS](../01_fundamentals/networking/http_https.md), [FTP와 SFTP](../01_fundamentals/networking/ftp_sftp.md), [SSH 사용](../01_fundamentals/networking/ssh.md) 문서와 참조 노트 4개를 컨테이너 시험과 함께 썼습니다. DNS·TLS 기존 문서는 보강 불필요로 판단했습니다. Alpine 3.22 vsftpd의 FTPS 세션 뒤 종료(139)는 원인 미확인으로 기록했습니다.

- DO-07 B10 로깅 문서와 1순위 완료 (2026-11-23, 00 세션 직접 요청 DO-07): [Elastic Stack 로그 수집](../02_infrastructure/data_pipeline/elastic_stack.md)(ES·Kibana·Filebeat 9.5.6), [Grafana Loki](../02_infrastructure/data_pipeline/loki.md)(Loki 3.7.10·Alloy), [Graylog](../02_infrastructure/data_pipeline/graylog.md)(7.2.2, Data Node preflight) 문서를 컨테이너 시험과 함께 쓰고, [로깅 도구 비교](../02_infrastructure/data_pipeline/logging_saas_comparison.md)(Splunk·Papertrail 참조 노트, 상용이라 비교만)를 더했습니다. 이로써 1순위 37개 주제(B1~B10)가 끝났고, 2·3순위는 PLAN 7절 B11~B24로 이어갑니다.

- DO-07 B9 모니터링 문서 (2026-11-23, 00 세션 직접 요청 DO-07): Prometheus·Grafana 문서는 나누지 않고 node_exporter 1.13.1로 판을 갱신했고, [Zabbix](../02_infrastructure/monitoring/zabbix.md) 8.0 LTS 문서(컨테이너 compose·agent2 설치 시험)와 [모니터링 SaaS 비교](../02_infrastructure/monitoring/monitoring_saas_comparison.md)(Datadog 참조 노트, 상용이라 비교만)를 새로 썼습니다. B9 묶음이 끝났습니다.

- DO-07 B8b 리버스 프록시·방화벽 문서 (2026-11-23, 00 세션 직접 요청 DO-07): [리버스 프록시 개념](../02_infrastructure/web_server/reverse_proxy.md)(RFC 9110·7239 기준)과 [ufw·firewalld](../04_security/hardening/ufw_firewalld.md) 문서·참조 노트를 새로 썼습니다. ufw는 `ubuntu:24.04` 컨테이너(NET_ADMIN)에서, firewalld는 `rockylinux/rockylinux:10`에서 `firewall-offline-cmd`로 설정을 확인했습니다. B8 묶음이 끝났습니다.

- DO-07 B8a 프록시·캐시 문서 (2026-11-23, 00 세션 직접 요청 DO-07): [Varnish](../02_infrastructure/web_server/varnish.md)와 [Squid](../02_infrastructure/web_server/squid.md) 문서·참조 노트를 새로 썼습니다. 두 제품 모두 컨테이너로 실행해 Varnish 캐시 적중과 Squid 전달 요청(200)을 확인했습니다. HAProxy는 기존 문서 6개로 충분해 보강 불필요로 판단하고 공통 참조 노트의 판(3.4.8·3.3.18·3.2.27)만 갱신했습니다.

- DO-07 B7b 웹 서버 문서 (2026-11-23, 00 세션 직접 요청 DO-07): [Tomcat](../02_infrastructure/web_server/tomcat.md), [Caddy](../02_infrastructure/web_server/caddy.md), [IIS](../02_infrastructure/windows_server/iis.md)와 참조 노트 3개를 새로 썼습니다. Tomcat 11.0.29와 Caddy v2.11.9는 공식 컨테이너로 실행해 확인했고(Caddy 설정 예 3개 `validate` 통과), IIS는 작성 환경이 Linux라 Microsoft Learn 문서와 대조만 했습니다.

- DO-07 B7a Nginx·Apache 검토 (2026-11-23, 00 세션 직접 요청 DO-07): 기존 [Nginx](../02_infrastructure/web_server/nginx_install.md)·[Apache](../02_infrastructure/web_server/apache_install.md) 문서가 설치부터 TLS·트러블슈팅까지 다뤄 새 문서 없이 보강 불필요로 판단했습니다. 공통 [웹 서버 참조 노트](../_reference/web_server_official_notes.md)의 판을 nginx.org·httpd.apache.org 기준으로 갱신(Nginx 1.31.9·1.30.7, Apache 2.4.71)하고, Apache 문서에 빠져 있던 참조 주석을 더했습니다.

- DO-07 B6 Git 호스팅 문서 (2026-11-23, 00 세션 직접 요청 DO-07): [GitHub](../02_infrastructure/cicd/github.md), [GitLab](../02_infrastructure/cicd/gitlab.md), [Git 호스팅 비교](../02_infrastructure/cicd/git_hosting_comparison.md)를 새로 쓰고 [Git 명령 참조](../02_infrastructure/cicd/git_command_reference.md)에 설치·판 확인을 보강했습니다. 참조 노트 3개(GitHub, GitLab, Bitbucket)를 새로 썼습니다. GitHub·Bitbucket은 계정이 필요하고 GitLab은 권장 메모리(16 GB)에 못 미쳐 실행 시험은 하지 않았으며, 명령은 공식 문서 원문과 대조했습니다. 저장소 이전 절차(mirror)는 로컬 저장소로 시험했습니다.

- DO-07 B5 셸·편집기 문서 (2026-11-23, 00 세션 직접 요청 DO-07): [Bash 스크립트](../01_fundamentals/linux/bash_scripting.md), [PowerShell](../01_fundamentals/windows/powershell.md), [nano](../01_fundamentals/linux/nano.md)를 새로 쓰고 [Vim](../01_fundamentals/linux/vim.md)에 설치·설정 파일·검증 절을 보강했습니다. 참조 노트는 PowerShell·nano를 새로 쓰고 Bash(엄격 모드·ShellCheck)·Vim(설정 파일 위치)을 보강했습니다. PowerShell은 Microsoft 수명 주기 문서가 7.7.0 정식판 이전 갱신본이라 판 번호를 GitHub release 기준으로 적고, `ubuntu:24.04` 컨테이너에 7.7.0을 설치해 시험했습니다. Bash 예제는 ShellCheck 경고 0건, nano는 7.2와 최신 판의 단축키 차이를 실제 화면과 공식 단축키표로 확인했습니다.

- DO-07 B4 관측 도구 문서 추가 (2026-11-23, 00 세션 직접 요청 DO-07): [프로세스 모니터링](../01_fundamentals/linux/process_monitoring.md), [sysstat](../01_fundamentals/linux/sysstat.md), [Linux 네트워크 점검 도구](../01_fundamentals/linux/linux_network_tools.md) 문서와 참조 노트 3개(procps, sysstat, 네트워크 도구)를 새로 썼습니다. 판은 각 프로젝트 배포처로 1차 확인하고, Ubuntu 24.04의 설치 판과 Rocky 10 컨테이너에서 명령·단위 파일·기록 위치·보관 기간을 실행해 2차 대조했습니다. sysstat 보관 기간이 배포판마다 다른 점(Ubuntu 7일, Rocky 28일)과 Debian `ENABLED`가 cron 방식에만 쓰이는 점을 확인해 적었습니다. 형제 문서 간 링크는 해당 문서가 들어오는 commit에서 더해 중간 commit에도 깨진 링크가 없게 했습니다.

- DO-07 B3 BSD 계열 문서 추가 (2026-11-23, 00 세션 직접 요청 DO-07): [BSD 계열](../01_fundamentals/linux/bsd_family.md) 개념 문서(Linux와 다른 점, 세 OS 비교, 판과 지원, 기본 명령 대응표, 고르는 기준, 확인 방법)와 FreeBSD·OpenBSD·NetBSD 참조 노트 3개를 새로 썼습니다. 판·지원 정책은 각 공식 사이트로, 명령은 공식 Handbook·man 페이지로 확인했습니다. BSD는 Linux 컨테이너로 실행할 수 없어 실행 시험은 하지 않았습니다.

- DO-07 B2 Linux 배포판 문서 추가 (2026-11-23, 00 세션 직접 요청 DO-07): [Ubuntu·Debian](../01_fundamentals/linux/ubuntu_debian.md), [RHEL 계열](../01_fundamentals/linux/rhel_family.md), [SUSE Linux](../01_fundamentals/linux/suse_linux.md) 문서와 참조 노트 3개를 새로 썼습니다. 판·지원 기간은 각 배포판 공식 출처(ubuntu.com·changelogs.ubuntu.com, debian.org·Debian LTS wiki, access.redhat.com, suse.com lifecycle, get.opensuse.org)로 1차 확인하고, `ubuntu:24.04`·`debian:13`·`rockylinux/rockylinux:10`·`opensuse/leap:16.0` 컨테이너에서 패키지 명령을 실행해 2차 대조했습니다. 일부 날짜는 endoflife.date를 보조로 쓰고 표시했습니다. Windows는 기존 문서 4개가 범위를 다뤄 보강 불필요로 판단했습니다. HANDOFF에 DO-07 묶음의 조건부 상시 승인을 기록했습니다.

- DO-07 B1 텍스트 처리 문서 추가 (2026-11-23, 00 세션 직접 요청 DO-07): [텍스트 처리](../01_fundamentals/linux/text_processing.md)(설치 확인, grep·sed·awk·cut·sort·uniq·tr·wc, 파이프 조합, jq, 검증, 트러블슈팅)와 [참조 노트](../_reference/text_processing_official_notes.md)를 새로 썼습니다. 참조 노트는 설치된 GNU 도구의 `--help`와 man 페이지로 2회 검증했고, 예제는 GNU grep 3.11·sed 4.9·gawk 5.2.1·coreutils 9.4에서 실행해 확인했습니다. 같은 날 gawk·coreutils 매뉴얼 페이지는 응답이 없어 주소 응답은 다음에 다시 봅니다. README·Linux 목차·_reference INDEX에 등록했습니다.

- DO-07 계획 등록 (2026-11-23, 00 세션 직접 요청 DO-07, 사용자 착수 승인): roadmap.sh DevOps 하위 주제 108개 문서 요청 가운데 1순위 37개를 [PLAN](PLAN.md) 7절에 묶음 B1~B10, 문서 계획, 제외 사유와 함께 등록했습니다. 요청의 개념·가이드·설정·설치 유형은 기술별 독립 문서 하나로 합치고, 상용 도구는 `_reference`와 비교 문서만 씁니다. [TODO](TODO.md)에 진행 1줄과 2·3순위 대기 1줄을 더했습니다.

- Docker 문서 2개 파일 이름 변경 (2026-11-23, 사용자 결정): DO-03 정리 뒤 Compose 내용이 빠져 이름과 내용이 어긋난 `docker_install_and_compose.md`를 [docker_install.md](../02_infrastructure/containers/docker_install.md)로, `docker_compose_cheatsheet.md`를 [docker_cheatsheet.md](../02_infrastructure/containers/docker_cheatsheet.md)로 `git mv` 했습니다. 이 저장소 안 링크 5곳(README, Docker Compose, Docker 네트워크, Podman, CHANGELOG의 링크 주소)을 같은 commit에서 고쳤고, 과거 기록의 본문 표기는 당시 이름 그대로 두었습니다. 다른 저장소 17개의 모든 branch에서 깨지는 링크는 0건이라 옛 자리 안내는 두지 않았고, [옮김 기록](MOVED.md)에 2행과 확인 범위를 더해 관찰 유예를 2026-12-23까지 둡니다.

- `.security_check.toml` 중복 예외 정리 (2026-11-23, 사용자 요청): 30 PR 9(`!vault`·`.local` 파일 이름 오탐 제외)가 고정 판 v0.7.0에 들어 있어, 저장소 설정의 `!vault` 값 예외 1개와 `.local` 파일 이름 때문에 둔 internal-host 허용 9개를 지웠습니다(문서용 예시 호스트 허용 5개는 유지). v0.7.0 `security_check.py`로 지우기 전과 후를 비교해 탐지 404건이 같고 새 탐지 0건임을 확인했습니다. 같은 검사에서 나온 high 1건(DO-03 [Docker Compose](../02_infrastructure/containers/docker_compose.md) `.env` 예시의 `POSTGRES_PASSWORD` 값)은 저장소 규칙대로 `<PASSWORD>` 자리표시자로 바꿨고, 줄 끝 주석이 값에 섞이지 않는 것을 `docker compose config`로 확인했습니다. 재검사 결과 high 0건, 실패 파일 0개입니다.

- DevOps 문서 후속 정리와 TODO·PLAN 현행화 (2026-11-23, 사용자 요청): 기존 문서 11개(yaml_syntax, Ansible 설치·팀 운영, Molecule, Vagrant, Packer, Kubernetes 기본·설치, k3s, Podman, SCVMM, Windows Server 핵심 개념)에 `함께 보기`를 두어 DO-03 새 문서로 연결했습니다. [Docker 명령 치트시트](../02_infrastructure/containers/docker_cheatsheet.md)는 제목을 바꾸고 안내만 남은 2~4장을 "옮긴 내용" 표로 합쳤고, [Docker 설치와 초기 설정](../02_infrastructure/containers/docker_install.md)은 안내만 남은 6·7·9장을 "옮긴 내용" 표로 합쳐 트러블슈팅을 6장으로 올렸습니다(두 문서의 장 앵커로 들어오는 링크 0건 확인). [TODO](TODO.md)에 대기 3건(DO-03 실기 확인, 조건이 충족된 `.security_check.toml` 중복 예외 정리, 파일 이름 변경 결정)을 적었고, [PLAN](PLAN.md) 5절에 기술 문서 작성 원칙 3줄(한 문서 한 기술, 옮긴 자리 안내, 범용 본문)을 더했습니다.

- DevOps 문서 범용 표현 정리 (2026-11-23, 사용자 요청): 오늘 쓴 DO-03 문서 가운데 특정 시험 환경에 묶인 본문 표현을 범용으로 바꿨습니다. [systemd 포함 컨테이너](../02_infrastructure/containers/systemd_container.md)는 시험 PC 상황과 보고 출처 문장을 본문에서 빼고 머리말 확인 범위로 모았으며 inotify 사용량 확인 명령을 더했습니다. [Hyper-V](../02_infrastructure/windows_server/hyper_v.md) 8절 제목을 "VM 안에서 가상화·컨테이너 쓰기"로 바꿨고, [Jinja2](../02_infrastructure/iac/jinja2.md)·[ansible-lint](../02_infrastructure/iac/ansible_lint.md)·[Docker Compose](../02_infrastructure/containers/docker_compose.md)·[Docker 네트워크](../02_infrastructure/containers/docker_network.md)의 날짜·환경 표현을 한두 곳씩 고쳤습니다.

- HANDOFF 현행화 (2026-11-23, 05 30분 단위 업무 1차, 05 D122): [HANDOFF](HANDOFF.md) 2절의 기준 줄을 main `90fad96`으로, "진행 중" 행을 DO-03 R1~R9와 D169 완료 상태로 고쳤습니다. 11-17 완료 목록은 이력에 있어 행에서 뺐습니다.

- Hyper-V 독립 문서 추가 (2026-11-23, 05 DO-03 R6 배정, 05 D122): [Hyper-V](../02_infrastructure/windows_server/hyper_v.md)(요구 사항, 설치, 가상 스위치, Linux VM 만들기, 운영 명령, 체크포인트, MAC 스푸핑과 중첩 가상화, 검증, 트러블슈팅)를 새로 썼습니다. 작성 환경이 Linux라 실행 시험은 하지 않았고, 명령과 요구 사항은 Microsoft Learn 문서와 Microsoft 공식 저장소 스크립트와 대조했습니다. Vagrant 10장·Packer 4장의 Hyper-V 내용은 도구별 사용법이라 옮기지 않고 함께 보기로 연결했습니다.

- kind 독립 문서 추가 (2026-11-23, 05 DO-03 R7 배정, 05 D122): [kind](../02_infrastructure/containers/kind.md)(설치, 첫 클러스터, 설정 파일, 앱 배포와 접속, 로컬 이미지, 여러 클러스터, 검증, 트러블슈팅)를 새로 썼습니다. 기준 판은 v0.33.0(기본 노드 이미지 v1.37.0)이며, 설치와 시험 PC inotify 한도 변경이 필요해 실행 시험은 하지 않고 kind 공식 문서 원본과 대조했습니다. 옮긴 기존 본문은 없습니다.

- systemd 포함 컨테이너 문서 보완 (2026-11-23, 00 세션 직접 요청 DO-03 R9 보완): [systemd 포함 컨테이너](../02_infrastructure/containers/systemd_container.md)에 4-3절 "공개 이미지를 쓸 때"(이미지의 `VOLUME /sys/fs/cgroup` 때문에 구성 A에서 멈추는 문제와 진입 스크립트, getty@tty1·systemd-modules-load mask, systemd 219 제약), 구성 B의 호스트 cgroup 빈 디렉터리 주의, inotify 실측 수치, 트러블슈팅 2행을 더했습니다. 수치와 현상은 00 세션의 실측 보고를 출처로 밝혀 적었고, 공개 이미지 Dockerfile의 `VOLUME` 선언은 이 세션에서 대조했습니다.

- yamllint 독립 문서 추가 (2026-11-23, 05 DO-03 R8 배정, 05 D122): [yamllint](../02_infrastructure/iac/yamllint.md)(설치, 첫 검사, 주요 규칙, 설정 파일, 예외 처리, 종료 코드와 출력 형식, ansible-lint와 함께 쓰기, CI 연결, 검증, 트러블슈팅)를 새로 썼습니다. 예제는 yamllint 1.38.0으로 실행해 출력과 종료 코드(error 1, strict에서 warning 2)를 확인했고, ansible-lint 호환 설정은 ansible-lint 원본 설정 파일과 대조했습니다. 옮긴 기존 본문은 없습니다.

- systemd 포함 컨테이너 독립 문서 추가 (2026-11-23, 05 DO-03 R9 배정, 05 D122): [systemd 포함 컨테이너](../02_infrastructure/containers/systemd_container.md)(준비, 이미지 만들기, 실행 구성, Compose, 서비스 다루기, Ansible 접속, 보안 주의, 검증, 트러블슈팅)를 새로 썼습니다. Docker Engine 29.8.1에서 구성 네 가지를 시험해 `--privileged --cgroupns=private`가 동작하면서 호스트 cgroup 트리를 숨기는 것을 확인했고, 이를 권장 구성으로 적었습니다. Compose 기동과 Ansible 접속은 시험 PC의 inotify 한도에 걸려 확인하지 못했고 문서에 그렇게 적었습니다. docker 11장의 systemd 전용 부분과 치트시트 4장 cgroup 설정은 새 문서로 옮기고 안내만 남겼습니다.

- Docker 네트워크 독립 문서 추가 (2026-11-23, 05 DO-03 R5 배정, 05 D122): [Docker 네트워크](../02_infrastructure/containers/docker_network.md)(드라이버 비교, bridge, 네트워크 명령, 포트 공개, Compose에서 쓰기, macvlan, 그 밖의 드라이버, 검증, 트러블슈팅)를 새로 썼습니다. bridge 이름 해석, 내부 전용 네트워크, 포트 공개 범위, host·none은 Docker Engine 29.8.1에서 실행해 확인했고, macvlan은 호스트 인터페이스를 바꾸므로 시험하지 않고 공식 문서와 대조했습니다. docker 8장, 설치 문서 9장 macvlan, 치트시트 3장 본문은 새 문서로 옮기고 안내만 남겼습니다.

- Jinja2 독립 문서 추가 (2026-11-23, 05 DO-03 R4 배정, 05 D122): [Jinja2](../02_infrastructure/iac/jinja2.md)(설치, 기본 문법, 조건과 반복, 필터와 테스트, 공백 제어, 재사용, Ansible에서 쓰기, 검증, 트러블슈팅)를 새로 썼습니다. 예제는 Jinja2 3.1.6과 ansible-core 2.20.5로 렌더링해 확인했고, template 모듈 두 번째 실행 `changed=0`까지 보았습니다. [Ansible 기초 가이드](../02_infrastructure/iac/ansible_basic_guide.md) 9장 본문은 새 문서로 옮기고 안내만 남겼습니다.

- ansible-lint 독립 문서 추가 (2026-11-23, 05 DO-03 R3 배정, 05 D122): [ansible-lint](../02_infrastructure/iac/ansible_lint.md)(설치, 첫 검사, profile 6단계, 자주 만나는 규칙, 설정 파일, 예외 처리, 자동 수정, CI 연결, 검증, 트러블슈팅)를 새로 썼습니다. 기준 판은 v26.11.0입니다. 사용자 승인으로 scratchpad 가상환경에 ansible-lint 26.11.0을 시험 설치해 3·7·8절 예제를 실행했고, 결과로 위반 표(`command-instead-of-shell` 추가), 요약 문구와 종료 코드, `--fix`가 고치는 규칙, 검증 2단계를 바로잡았습니다. [Ansible 기초 가이드](../02_infrastructure/iac/ansible_basic_guide.md) 19장 본문은 새 문서로 옮기고 안내만 남겼습니다.

- 직접 요청 경로 추가 (2026-11-23, 사용자 결정 05 D169, 05 `2e6a6a7` 기록 대조): [HANDOFF](HANDOFF.md) 2절 세션 역할을 "05 총괄 배정과 다른 Claude 세션의 문서 요청을 받음"으로 바꾸고, 3절에 직접 요청 조건(형식 B, TODO 기록, 공개 저장소의 비공개 정보 금지, commit·push 사용자 확인, 여러 저장소·사용자 결정 건은 05로, 05 배정 우선, Codex 제외, 05 비대조)을 더했습니다. 지침 개정으로 보고 이 세션 사용자 확인 뒤 반영했습니다.

- Ansible 기초 문서를 혼자 읽는 문서로 보강 (2026-11-23, 05 DO-03 R2 배정, 05 D122): [Ansible 기초 가이드](../02_infrastructure/iac/ansible_basic_guide.md) 1절에 설치(가상환경 pip, 배포판 패키지)와 설치 확인을 더하고, ansible-core 판별 제어 노드 Python 요구 판(2.22는 3.13 이상, PyPI 확인 2026-11-23)을 표로 적었습니다. 20절 검증(설정 → 인벤토리 → 접속 → 문법 → 미리 보기 → 실행 → 멱등성)과 함께 보기를 새로 두었습니다. 18절 Vault 본문은 [Ansible Vault](../02_infrastructure/iac/ansible_vault.md)와 겹쳐 그 문서 안내로 줄였습니다. 9절 Jinja2와 19절 ansible-lint는 R4·R3 문서를 쓸 때 옮깁니다. 검증 순서는 ansible-core 2.20.5에서 로컬 대상으로 실행해 두 번째 실행 `changed=0`까지 확인했습니다.

- Docker Compose 독립 문서 추가 (2026-11-23, 05 DO-03 R1 배정, 05 D122): [Docker Compose](../02_infrastructure/containers/docker_compose.md)(설치, 첫 프로젝트, compose.yaml 구조, 명령, 변수와 .env, 여러 환경, 운영 설정, 검증, 트러블슈팅)를 새로 썼습니다. 기준 판은 Compose v5.8.0이고, 3절 예제와 9절 검증 명령은 Docker Engine 29.8.1·Compose v5.5.1에서 실행해 확인했습니다. 흩어져 있던 Compose 본문(docker 7장, 설치 문서 6·7장과 트러블슈팅 2행, 치트시트 2장과 4장의 리소스·헬스체크·환경 변수·프로파일)은 새 문서로 옮기고 그 자리에는 안내만 남겼습니다. 치트시트 3장 네트워크와 4장 cgroup은 R5·R9 문서를 쓸 때 옮깁니다. 파일 경로는 바뀌지 않아 [옮김 기록](MOVED.md) 대상이 아닙니다.

- ISS-02 검사 예외 재검토 (2026-11-22, 05 AX-HUB-24 마무리 계획 A2·N2, 05 D158 C2): 재검토일 2026-11-30을 앞당겨 검사 도구 0.7.0으로 두 예외를 빼고 검사했고, 두 파일 모두 다시 걸렸습니다(box-chars 2건, diagram-width 4건). [network_headers](../01_fundamentals/networking/network_headers.md)는 Ethernet·TLS 그림에서 앞 필드가 끝나고 Payload가 같은 줄 오른쪽에서 시작하는 칸에 `Payload (continues)` 이름을 붙이고 경계를 `├───┴───┤`로 바꿔 예외를 없앴습니다. 한글 이름은 diagram-kr 검사에 걸려 영문으로 썼습니다. [ddos 방어 구조](../04_security/cloud/ddos_defense_architecture.md)는 사유를 "인접 박스 연결선 오탐"에서 실제 원인(오른쪽 연결선이 끝난 아래 행의 폭 차이, 공백으로 채우면 줄 끝 공백 검사와 충돌, 다시 그리면 화살표 뜻이 바뀜)으로 고치고 재검토일을 2027-02-28로 연장했습니다. 두 설정 파일, [검증 기준](verification.md), [TODO](TODO.md) 예외 표, [ISSUE](ISSUE.md) ISS-02, [HANDOFF](HANDOFF.md) 다음 기한을 함께 맞췄습니다.

- TODO 대기 줄 2개 닫음 (2026-11-21, 05 AX-HUB-24, 사용자 결정 05 D156 ②): [TODO](TODO.md) 1절의 "대기 — AX-HUB-19 후속"과 "대기 — MAIN-20261113-01 / AX-HUB-20 후속"을 닫았습니다. "기존 갱신" 후보 13건(6~11·13·14·16·20·21·23·28)은 [후보 기록](tracks/MAIN-20261113-01_ax-reference-docs/40_results/CANDIDATES.md)에 그대로 보존하며, 사용자가 요청하면 TODO에 새 줄로 엽니다. 후보 파일과 `07_ai_transformation` 문서는 바꾸지 않았습니다.

- 검사 도구 고정 판 0.7.0 (2026-11-21, 05 AX-HUB-24, 사용자 결정 05 D155 ①): [검사 workflow](../.github/workflows/update-date.yml)의 sia_scripts 판을 0.6.0에서 0.7.0으로 바꿨습니다(tag v0.7.0 → 30 `aa43731`). 첨부 archive를 직접 내려받아 계산한 SHA-256이 05가 release asset에서 확인한 값과 같았습니다. [검증 기준](verification.md)과 [PLAN](PLAN.md) 4절의 판 표기도 함께 고쳤습니다. 커밋 사본에 0.7.0 도구로 link·style(설정과 기본)·heading·inventory 검사를 돌려 모두 0건이었고, 예외 목록은 총 5건이었습니다.

- TODO·PLAN 끝난 항목 정리 (2026-11-21, 05 AX-HUB-24 배정, 05 D122): TODO 머리 규칙("완료된 항목은 `CHANGELOG.md`로 이동")에 따라 [TODO](TODO.md) 1절의 끝난 문단 3개(2026-09-15 테스트 문서 `[5.0.2]` 안내, 웹 서버 테스트 `MAIN-20261027-01`·`-02` 완료 문장, "수신 완료 — MAIN-20261027-06" 문단)를 지우고, 대기 줄 2개(AX-HUB-19 후속, MAIN-20261113-01 / AX-HUB-20 후속)에 쌓인 끝난 경과를 줄여 다음 행동만 남겼습니다. [PLAN](PLAN.md) 4절의 v0.6.0 전환 경과 두 문장은 이력 안내 한 문장으로 바꾸고 다음 갱신 규칙은 그대로 두었습니다. 지운 내용은 모두 이 파일의 `[5.0.2]`, 2026-10-27·2026-11-01·2026-11-12·2026-11-13·2026-11-16·2026-11-17 항목에 이미 있어 새로 옮긴 원문은 없습니다. 열린 줄은 대기 2개와 검사 예외 표(ISS-02)로 전후 같습니다.

- Claude Code 설정 파일 가이드 추가 (2026-11-19, 31 Claude 세션 요청, 사용자 지시로 보낸 요청과 같은 날 변경 2건): [설정 파일 가이드](../06_career/ai_tools/claude/claude_code_settings_guide.md)(설정 파일 층, 우선순위와 병합·신뢰, 공유와 개인 구분, 권한 규칙 문법, deny·ask·allow 후보, 안전 설정, hook 실패 시 동작, hook 배포 방식 세 가지, Codex 대응, 적용과 확인)를 범용 학습 문서로 만들었습니다. 변경 요청에 따라 위험 명령 deny와 자격증명 읽기 차단은 저장소 공유안이 아니라 개인 설정의 선택 예시로 쓰고, 위험 작업이 잦은 사용자는 ask나 개인 프로젝트 파일로 조절하는 방법을 함께 적었습니다. code.claude.com의 settings·settings-reference·permissions·hooks 원문과 Codex rules 공식 문서로 대조했습니다. 요청 목록의 `push origin :*`는 규칙으로 쓰면 끝의 `:*`가 와일드카드로 읽혀 모든 push에 일치하므로 hook 검사로 안내했습니다. 규칙 예시는 세션에서 실제 일치를 시험하지 않았습니다. [참조 노트](../_reference/claude_code_official_notes.md) 7절·12절·출처, [확장 기능 가이드](../06_career/ai_tools/claude/claude_code_extensions_guide.md) 연결 1줄, 루트 README 행, `06_career` README(ai_tools 31→32)·`_reference` INDEX를 맞췄습니다.

- `security_check.py` internal-host 오탐 허용 (2026-11-19, 사용자 요청): 남은 high 20건이 모두 internal-host 규칙이었습니다. `.local`로 끝나는 설정 파일 이름(Claude 개인 지침 파일, `/etc` 아래 파일)과 내부 도메인 접미사를 붙인 문서용 예시 호스트라서, 30 문서 12절의 방식대로 [`.security_check.toml`](../.security_check.toml)에 14개 파일의 `[[allow]]`(rule `internal-host` + path)를 넣었습니다. 그 파일들의 다른 규칙은 계속 검사합니다. 저장소 전체 재검사 결과 high 0건, 종료 코드 0(경고 356·낮음 41은 차단 기준 미만)입니다. 정정(2026-11-19): 이 결과는 이 항목을 쓰기 전에 잰 값이며, 처음 쓴 이 항목이 예시 호스트 이름을 그대로 인용해 high 1건이 생겼습니다. 파일·호스트 이름을 빼고 다시 잰 결과는 high 0건, 종료 코드 0입니다.

- `security_check.py` 저장소 설정 추가 (2026-11-19, 사용자 요청): 루트 [`.security_check.toml`](../.security_check.toml)에 `[placeholder] values` 예외 목록을 두어 비밀번호 규칙이 값으로 잘못 읽은 36건(`!vault`, `...`, 비밀 이름 `prod/app/db`, NOPASSWD 뒤 `ALL`, 출력 서식 `.3f`, 정책 이름 등)을 제외했습니다. 값 전체가 같을 때만 제외하고, 넓은 접미사 규칙(`_id` 등)은 실제 키까지 가릴 수 있어 쓰지 않았습니다. 저장소 전체 재검사에서 비밀번호·토큰 항목은 0건이 되었고, 실제 값 형태의 시험 줄은 계속 탐지되는 것을 확인했습니다. 검사기 공통 설정(30)은 바꾸지 않았습니다.

- 문서 예시 비밀값 자리표시자 치환 (2026-11-19, 사용자 요청): 30 `security_check.py`(26.11.16, 30 main `450973d`)를 저장소 전체에 실행해 비밀번호·토큰 항목에서 실제 값처럼 보인 예시를 자리표시자로 바꿨습니다. 대상은 10개 문서입니다: http_methods(`securePassword123!`·JWT 조각·`secret123` → `<PASSWORD>`·`<NEW_PASSWORD>`·`<ACCESS_TOKEN>`·`<REFRESH_TOKEN>`), SoftEther 클라이언트 가이드·Linux 작업 가이드(`SecurePassword123456789` → `<PASSWORD><OTP>`, 같은 파일의 고정 패스워드도 `<PASSWORD>`), graphql(`<TOKEN>`), airflow(`user:pass@`·`your-secret-key`·`SecureKey123` → `<PASSWORD>`·`<SECRET_KEY>`·`<API_KEY>`), kubernetes_basic(base64 값 → `<BASE64_PASSWORD>`), ansible_vault(`sk-…` → `<API_KEY>`), mysql_install·percona_xtrabackup(`SecurePassword123!`·`NewPassword123!`). 셸에서 따옴표 없이 쓰인 자리는 `<`가 리디렉션으로 해석되지 않게 따옴표를 넣었습니다. windows_openssh_install은 평문 변환 대신 `Read-Host -AsSecureString` 입력으로 바꿨습니다. 비밀번호·토큰 항목 탐지는 73건에서 36건으로 줄었고 남은 것은 오탐(코드 표현 `secret['password']`, 예시 계정 `123456789012` ARN, `token_policies`, `NOPASSWD`, `pass@k`, `=...` 등)입니다. 저장소 규약의 자리표시자 `SecurePassword123`·`Secureuser123`(`.gitleaks.toml`·검사기 예외 등록)은 그대로 두었고, git 이력은 바꾸지 않았습니다.

- SoftEther VPN 경유 Linux 서버 작업 가이드 실기 반영 (2026-11-19, 사용자 요청): Ubuntu 24.04 서버에 vpnclient 4.44 Build 9807을 설치하고 RADIUS+OTP 계정으로 실제 연결해 통신 시험까지 마친 결과로 [가이드](../01_fundamentals/networking/softether_vpn_linux_server_ops.md)를 고쳤습니다. 4절에 계정 생성(`AccountCreate`·`RemoteDisable`), 서버 인증서 검증(`AccountServerCertSet`·`Enable`, 새 계정은 검증 꺼짐), 설정 확인 표를 넣었습니다. 5절에는 주소만 받는 `dhcpcd` 옵션(`-G`·`-C`), SecureNAT가 option 121·249로 함께 보내는 경로(하나만 막으면 다른 형식으로 들어옴), 실행 중인 dhcpcd에 `-T`를 쓰면 주소가 지워지는 문제와 복구 방법을 더했습니다. 8절에 `vpn_vpn0`의 `arp_ignore`·`arp_announce`와 UDP 가속 설명을, 10절 스크립트에 DHCP 방식과 ARP 설정을, 트러블슈팅에 동시 세션 code 20 등 3행을 추가했습니다. Ubuntu 24.04 Server의 DHCP 클라이언트(`dhcpcd` 있음, `dhclient` 없음)를 확인값으로 바꿨습니다. 실제 서버 주소·계정·대역은 문서에 넣지 않았습니다. 이어서 문서를 범용 기준으로 다시 점검해, 시험 환경 하나에서만 본 내용(포트 예시, 두 경로 형식 동시 수신, UDP 가속 대상 주소)과 추정(Windows도 같은 경로를 받음)을 일반 표현으로 고쳤습니다.

- uv 설명 문서 추가 (2026-11-19, 30 전담 세션 요청 30-REQ-20261119-UV, 사용자 지시로 보낸 요청): [uv 문서](../01_fundamentals/programming/python/python_uv.md)(uv 소개, 대체하는 도구 표, 시스템 Python 보호 원칙과 `--no-bin`, PEP 668·deadsnakes PPA를 쓰지 않는 이유, sha256 대조 설치, 기본 사용 예, 프로젝트·도구 관리)와 [참조 노트](../_reference/python_uv_official_notes.md)를 만들었습니다. 최신 판 0.13.9(2026-11-17), `--no-bin` 설명, 저장 위치, 대체 대상은 Astral 공식 문서·GitHub Releases와 대조했습니다. 문서의 명령 예제는 `ubuntu:24.04` 컨테이너의 일반 사용자 계정에서 실행해 출력을 확인했습니다. 이 이미지에는 시스템 Python이 없어 시스템 Python 불변은 30 devenv README 6절의 실기 시험 결과를 인용했습니다. 설치 스크립트 예는 30 저장소(비공개) 링크로 대신했습니다. Python README 목록·학습 순서, [가상환경](../01_fundamentals/programming/python/python_virtual_env.md) uv 절 연결 1줄, 루트 README(Python 30→31개, uv 행), `01_fundamentals` README 문서 수(58→59), `_reference` INDEX를 맞췄습니다.

- TODO2 문장 4곳 현장 병합 (2026-11-18, 05 AX-HUB-24 N7 배정, 사용자 요청으로 배정 요청): `AGENTS.md` 17행, `GOVERNANCE.md` 15행, `INDEX.md` 7행, `.governance/README.md` 5행의 "이전 루트 상태·이력을 실제 적용에서 보존·병합하고 TODO2 상세 설계 과제를 일반 작업에 일괄 적용하지 않습니다." 문장만 31 `5cc4a68` profile 원문 "실제 적용에서는 현장의 기존 상태와 이력을 보존하고 필요한 내용만 병합합니다."로 바꿨습니다. 바꾼 4줄은 31 해당 줄과 글자까지 같고, 네 파일의 `TODO2`는 0곳입니다. 같은 줄의 다른 문장과 각 파일 날짜는 그대로 두었고, [HANDOFF](HANDOFF.md) 보류 칸의 후속 안내를 완료로 고쳤습니다.

- Rust 기초 문법 문서 추가 (2026-11-18, 사용자 요청): 개념 문서 앞 단계가 비어 있어 [Rust 기초 문법](../01_fundamentals/programming/rust/rust_basics.md)(프로그램 구조, 변수와 가변성, 기본 타입, 문자열, 제어문, 함수, 구조체, 열거형과 match·Option, 컬렉션, 모듈, 출력과 포맷, 종합 예제)을 bash·python 비교 형식으로 만들었습니다. Rust 예제 14개를 공식 `rust:1.100-slim` 이미지에서 컴파일·실행해 문서의 출력과 실제 출력을 자동 대조했고(처음 적은 출력 2곳을 실제 값으로 정정), clippy 경고 1건을 고쳐 `-D warnings` 0건을 확인했습니다. rust/ README 목록·학습 순서, 로드맵 Phase 1 표, 전환 가이드 도입부·첫 주 계획, 루트 README, `01_fundamentals` README 문서 수(57→58)를 맞췄습니다.

- AI 코딩 도구 비교 최신화와 ai_tools 폴더 양식 정비 (2026-11-18, 사용자 요청): [AI 코딩 도구 비교](../06_career/ai_tools/ai_coding_tools_comparison.md)의 요금·모델·벤치마크를 각 공식 페이지에서 다시 확인해 반영했습니다. Windsurf는 Devin Desktop으로 이름이 바뀌어(`windsurf.com` 308 이동, 공식 페이지 문구) Devin 항목으로 합쳤고, OpenAI 주력 모델을 GPT-6 계열로, Claude Team 좌석 요금·Copilot AI Credits·Amp Hobby 플랜·BenchLM 순위(2026-11-18)를 바꿨습니다. 기준일을 하나로 맞추고 reference 주석·절별 목차 돌아가기·통계 절을 넣었습니다. [참조 노트](../_reference/ai_coding_tools_official_notes.md)에 "최신 재확인" 절을 추가했습니다. 같은 폴더(하위 폴더 포함) 점검에서 양식이 어긋난 10개 문서를 정비했습니다: harness_engineering(절 끝 링크·구분선·통계), mcp_protocol_guide·ai_generated_infra_code_review(통계), ai_markdown_design_patterns(도입부 위치, 표 안 돌아가기 링크 제거), ai_development_request_template(목차 뒤 불필요한 링크 제거, 11절 링크), codex/codex_skills_catalog(목록형 목차를 표로), codex/asd_ste100_codex_communication·kiro/kiro_agent_lock·codex/codex_skills_setup_guide·codex/codex_cli_linux_guide(절 끝 링크), kiro/kiro_setup_guide(번호 붙은 참고 자료 절 정리, 통계). 근거 노트가 내용과 맞는 3개 문서에만 reference 주석을 넣었고, 본문 내용은 바꾸지 않았습니다.

- Windows 코드 서명 참조 노트·가이드 추가 (2026-11-18, 사용자 요청): [참조 노트](../_reference/windows_code_signing_official_notes.md)에 SmartScreen 평판(EV의 즉시 통과 효과는 2024년에 없어짐), 서명 방식 비교, Azure Artifact Signing(인증서 3일, 타임스탬프 필수, SignTool dlib·GitHub Action v2 입력), CA/B Forum 기본 요구사항 3.11.0(2023-06 하드웨어 키 보관, 2026-03-01부터 유효 기간 최대 460일), SignTool·타임스탬프, UAC 색(서명 회색·미서명 노란색), 드라이버 제출 계정의 EV 요건, 오탐 제출 주소를 Microsoft Learn·CA/B Forum 원문과 대조해 정리했습니다. Artifact Signing의 법인 대상 지역은 Azure Quickstart(한국 포함 12개)와 Windows 앱 문서(4개 지역)가 달라 둘 다 적었습니다. 이를 근거로 게임 배포용 [코드 서명 가이드](../04_security/hardening/windows_code_signing_guide.md)(서명 대상, 빌드·패치 순서, 명령, CI, 키 운영, 평판 쌓기, 오탐 대응, 점검표)를 만들었습니다. 서명 명령과 CI 예시는 실제 인증서로 실행하지 않았습니다. 앞서 만든 SoftEther 작업 가이드와 Rust 전환 가이드에 빠졌던 `reference` 주석을 넣었고, 루트 README·`04_security` README(hardening 19→20)·`_reference` INDEX를 맞췄습니다.

- Rust 학습 자료 보강 (2026-11-18, 사용자 요청): 로드맵·개념 문서·참조 노트가 이미 있어 새로 만들지 않고 빈 곳을 채웠습니다. [bash·python 사용자를 위한 Rust 전환 가이드](../01_fundamentals/programming/rust/rust_for_bash_python_se.md)(사용 판단, 도구·작업 대응표, 세 언어 비교 예제 3개, 처음 막히는 지점, 첫 4주 계획)와 [rust/ README](../01_fundamentals/programming/rust/README.md)를 새로 만들고, [로드맵](../01_fundamentals/programming/rust_roadmap_for_se.md)에 단계별 저장소 문서 표와 전환 가이드 안내를 넣었습니다. 예제 3개는 공식 `rust:1.100-slim` 이미지에서 컴파일·실행하고 clippy 경고 0건을 확인했습니다. [참조 노트](../_reference/rust_official_notes.md)는 Stable을 1.100.0(2026-11-12 공지, 공식 배포 manifest 대조)으로, clap·regex·nix 판을 crates.io 값으로 바꾸고 1.100 주요 변경을 더했습니다(nix 0.32 변경 내용은 미확인). 루트 README·`01_fundamentals` README 문서 수(56→57)·`_reference` INDEX를 맞췄습니다.

- SoftEther VPN 경유 Linux 서버 작업 가이드 추가 (2026-11-18, 사용자 요청): [softether_vpn_linux_server_ops.md](../01_fundamentals/networking/softether_vpn_linux_server_ops.md)를 새로 만들었습니다. Ubuntu·Rocky Linux 서버가 vpnclient로 접속한 뒤의 작업(작업 전 점검과 자동 원복 타이머, RADIUS+OTP 계정의 재연결·자동 연결 제약, 고정 IP·DHCP, Split Tunnel, DNS, ufw·firewalld·SELinux·rp_filter, SSH·rsync·MTU, 작업 스크립트, 종료 점검)을 다룹니다. vpncmd 명령과 RHEL 10 `dhclient` 제거는 공식 문서로 대조했고, Ubuntu의 `dhclient` 기본 설치 여부는 미확인으로 적었습니다. 실제 서버에서 명령을 실행해 보지는 않았습니다. 루트 README Networking 표에 1행을 넣고(표 정렬), [클라이언트 가이드](../01_fundamentals/networking/softether_vpn_client_guide.md) 개요에 연결 1줄을 추가했습니다.

- 루트 `TODO2.md` 삭제 (2026-11-17, 사용자 직접 결정): 31·00·30·51 저장소 구조와 governance 공급을 다룬 별도 설계 과제 문서를 지웠습니다. 저장소 안에서 이 파일을 링크하거나 입력으로 쓰는 곳은 없었고, 다른 저장소(03·31)의 언급은 이름만 적은 관찰 기록입니다. [INDEX](INDEX.md)의 트리 1행과 읽기 조건 표 1행을 지우고 [삭제 기록](REMOVED.md)에 복원 명령을 남겼습니다. AGENTS·GOVERNANCE·INDEX·`.governance/README.md`의 "TODO2 상세 설계 과제를 일반 작업에 일괄 적용하지 않습니다" 문장은 31 profile 원문이라 이 저장소에서 고치지 않았습니다.

- 루트 연결 안내 삭제 (2026-11-17, 사용자 직접 결정): 2026-10-27 `.governance/`로 옮긴 뒤 루트에 두었던 `TODO.md`·`PLAN.md`·`CHANGELOG.md` 연결 안내를 지웠습니다. 저장소 안 링크·도구 입력은 0건이었고, 현행 AGENTS의 "옛 자리 안내는 외부 참조가 있을 때 둡니다"에 따라 관찰 유예 끝(11-26) 전에 앞당겼습니다. [옮김 기록](MOVED.md) 세 행을 닫고 [삭제 기록](REMOVED.md)에 복원 명령을 남겼으며, [INDEX](INDEX.md) 트리 1행과 TODO·HANDOFF의 대기 줄을 정리했습니다. 05 총괄에 미리 알렸습니다. `TODO2.md`는 그대로 둡니다.

- 문서 세 건 정리 (2026-11-17, 05 D132 M4, 사용자 "모두 권장안"): `04_security/web_cwe/README.md`의 개인 playbook 경로 3곳을 자리표시자로 바꿨습니다(이력은 그대로). [gstack](../02_infrastructure/monitoring/gstack.md)을 공식 저장소 README(`VERSION` 1.99.5.0, commit `5b4fa9e`, 2026-11-17 확인) 기준으로 다시 썼고, 공식 자료에 없는 `.gstack/memory.md`·`/memory`·70% 임계 설명을 지웠습니다. `01_fundamentals/networking/tcpdump_examples.md`는 코드 블록이 [packet_analysis.md](../01_fundamentals/networking/packet_analysis.md) 1~4절과 같아 통합·삭제했고, 통합 대상에 없던 Python 출력 1줄(`print(f"Payload: …")`)은 packet_analysis.md의 같은 자리로 옮겼습니다. 링크 3곳과 루트 README 행을 고쳤습니다([옮김 기록](MOVED.md)).

- 출처 미확인 commit 되돌림 (2026-11-17, 05 D133, 사용자 승인): 16:58에 main에 들어온 `fc60899`("docs: docs modified")가 루트 `CHANGELOG.md`·`README.md`, `06_career/README.md`, `_reference/INDEX.md`에 stash 충돌 표시를 남겨 CI가 실패했습니다. `git revert`로 되돌려(`5cfb780`) 트리를 `8655aae`와 같게 맞췄습니다. 10-13 stash는 그대로 두었고, commit을 만든 주체는 미확인입니다.

- 단독 업무 점검 (2026-11-17, 05 D122 배정): 고정 판 sia_scripts 0.6.0(archive SHA-256과 manifest 38개 파일 대조)으로 커밋 사본(`f12a3f9`)에 [검증 기준](verification.md)의 현장 검사 여섯 가지를 돌려 모두 이슈 0건이었습니다(링크 1715개, 문체 455개 파일, 헤딩 552개 파일, 예외 목록 총 5건·사유 미확인 0건). 고칠 문서가 없어 문서는 바꾸지 않았고, [ISSUE](ISSUE.md)에 ISS-03 재확인 결과를 덧붙였습니다.

- 검사 도구 고정 판 0.6.0 (2026-11-17, 05 D130 U9-1, 사용자 허용): [검사 workflow](../.github/workflows/update-date.yml)의 sia_scripts 판을 0.5.0에서 0.6.0으로 바꾸고(0.5.1은 건너뜀), 첨부 archive의 SHA-256을 직접 계산해 05 검토 값과 대조한 뒤 고정했습니다. [검증 기준](verification.md)과 [PLAN](PLAN.md) 4절의 판 표기도 함께 고쳤습니다. 바꾸기 전 커밋 사본에 0.6.0으로 workflow 검사 다섯 단계를 돌려 모두 0건이었고, 예외 목록은 총 5건이었습니다. PR 3의 CI(예외 목록 총 5건)가 성공한 뒤 사용자 지시로 병합했고(`04939d4`), 병합 commit의 main CI도 성공했습니다.

- 계정 표기 6곳 일반화 (2026-11-17, 05 D128 B1, 사용자 허용): `96_scripts/windows/win_hosts_manager.py`의 로그 폴더 이름을 스크립트 이름 기반으로, `02_infrastructure/web_server/nginx_geoip2_install.sh` 머리 주석의 작성자를 저장소 표기 `siasia86`으로 바꿨습니다. 이 파일의 옛 항목 2곳은 `<옛 표기>`로 가리고, 계정 홈 경로 1곳은 `~/.kiro/...` 꼴로 일반화했습니다. Git 이력은 다시 쓰지 않았습니다.

- 보고만 항목 2차 정정 (2026-11-16): 사용자 결정(권장안 모두 승인)으로 1차 검토에서 남긴 항목을 11묶음으로 다시 처리해 171개 파일을 고쳤습니다. 위험·모순(strace 권한, trivy 실행 순서, docker·compose cgroup 권장 통일, OCSP stapling 예시, AWS MFA·Network Firewall 그림), 지난 날짜 표(PostgreSQL 14·.NET 8/9 지원 종료, Windows Server ESU, 현행 Claude 모델, AI 도구 비교표, 최신 판), 절 재작성(GitLab 이벤트 API 전제, dbtrail 저장 구조, Kiro 도구 매핑, 빈 절)과 다이어그램 안 한글의 영문화를 반영했고, `_reference` 노트를 다시 확인한 곳은 확인일과 INDEX를 맞췄습니다. 근거를 끝내 찾지 못한 값, 파일 통합·삭제가 필요한 항목(gstack 문서 전제, tcpdump 예시 중복), 공개 문서의 실습 경로는 고치지 않았습니다.

- 폴더별 새 문서 추가 (2026-11-16): 사용자 지시(승인 없이 추가)로 11개 폴더 묶음의 빠진 주제를 분석해 새 문서 42개를 더하고, 폴더 README 9개와 루트 README에 목록·문서 수를 반영했습니다. 주요 주제는 systemd·journald·sysctl, Python 동시성·HTTP·날짜·디버깅, DNS·MTU, 분산 시스템·수 표현·확률적 자료구조·일관된 해싱, GitLab CI·Dockerfile·Podman·Kubernetes 장애 진단, LVM·mdadm·node_exporter·CloudWatch, 점진 배포·Feature Flag·Toil·Resilience, AIDE·auditd·SELinux·침해 초동 점검, PostgreSQL 백업·VACUUM·PgBouncer·MySQL 논리 백업, MCP·AI 작성 코드 검토·기술 면접·기술 문서 작성, 에이전트 평가·MCP 서버 점검·실행 관측입니다. 같은 LVM 주제가 두 폴더에 나와 `02_infrastructure/storage/lvm_operations.md` 하나만 남겼습니다.

- 문서 내용 검토와 정정 (2026-11-16): 사용자 지시로 추적 문서 491개를 11묶음으로 나눠 병렬 검토하고, 공식 문서·같은 문서 안 근거로 확인된 정정만 61개 파일에 반영했습니다. 위험한 예시(호스트 전체 볼륨 삭제, 정확히 일치하지 않는 사용자 허용 검사, 값으로 읽히는 sysctl 줄 끝 주석, ICMPv6 차단, 경고 없는 policy drop)를 고쳤고, 명령·옵션 오류(unshare 순서, mc retention, restic key remove, Vault capability·dev 수신 주소, Kiro CI 도구 권한), 문서 안 모순(DNS 헤더 비트 순서, LINQ 지연 실행 예시, 복사된 Filebeat 표, View 생성 순서), 연결 노트와 어긋난 값(Zabbix 8.0 LTS, Unicode 문자 수, GRAID 명령), 패치 판(MetalLB·Longhorn·Grafana·kube-prometheus-stack)과 `_reference` 노트 14개의 정의·판 표기를 바로잡았습니다. 절 재작성·주 판 전환·날짜가 박힌 표·근거 부족 항목은 고치지 않고 따로 모았습니다.

- 운영 기준 제목과 적용 문구 정정 (2026-11-16): 중앙 profile 31 `a08c206`에 맞춰 [GOVERNANCE](GOVERNANCE.md) 제목을 "운영 기준"으로 바꾸고 6절 끝 문장을 현장에서도 참인 문장으로 고쳤습니다. [적용 기록](APPLICATION.md) 7절에 남겼습니다.

- 클라우드 백업 비교 문서 이름 변경과 INDEX 칸 삭제 (2026-11-16): 사용자 결정으로 `02_infrastructure/cloud_aws/backup_tools_comparison.md`를 [cloud_backup_cost_comparison.md](../02_infrastructure/cloud_aws/cloud_backup_cost_comparison.md)로 옮겼습니다(`3de9397`). `storage/`의 같은 이름 문서와 구분하려는 것이며, 제목과 루트 README 설명(옛 "AWS Backup vs 직접 구현")을 실제 내용인 도구 리소스·비용 비교에 맞췄습니다. 외부 참조 확인과 관찰 유예는 [옮김 기록](MOVED.md)에 적었습니다. [_reference INDEX](../_reference/INDEX.md) 표에서 뜻이 정해지지 않았던 "참조" 칸을 지웠습니다.

- 저장소 분석과 모순 정정 (2026-11-16): 저장소 전체 검사(추적 파일 style·heading·link·inventory·gitleaks 0건) 뒤 자동 검사가 잡지 못하는 모순을 고쳤습니다. [_reference INDEX](../_reference/INDEX.md)에 빠진 노트 4개(SoftEther·Hyper-V 3개)를 더하고 Vault 확인일을 노트와 맞췄습니다. 노트 9개(eBPF·GDB·iotop·iperf3·Lean·rsync·strace·tcpdump·Valgrind)의 표에 남은 옛 최신 판을 같은 노트의 2026-11-09 확인 값으로 바꿨습니다. `vim_airline.md`의 작성일이 마지막 업데이트보다 늦던 것을 첫 commit 날짜로 고쳤고, 2026-11-09·11-15에 내용을 바꾸고도 날짜를 두었던 노트 7개와 관리 문서 4개(AGENTS 포함)의 마지막 업데이트를 실제 수정일로 맞췄습니다. Python 문서 2개의 `reference` 주석이 노트가 아닌 URL을 가리켜 지웠고(같은 URL은 참고 자료에 있음), [적용 기록](APPLICATION.md) 6절에 2026-11-14·15 profile 병합을 더했습니다.

- 관리 문서 현행화 (2026-11-16): [PLAN](PLAN.md) 4절의 검사 도구 기준을 옛 v0.3.3에서 workflow 고정 값 v0.5.0·checksum으로 바로잡고 다음 고정 판 갱신 조건을 적었습니다. [HANDOFF](HANDOFF.md) 재개 지점과 [TODO](TODO.md) 대기 줄에 고정 판 갱신·루트 연결 안내 관찰 유예(2026-11-26)를 반영했습니다.

- AX-HUB-17 옛 자리 안내의 옮김 기록 전환 (2026-11-14): 33 기준 v1.5(`307863d`) 5절·6절에 따라 [옮김 기록](MOVED.md)을 새로 만들고, 2026-10-27에 `.governance/`로 옮긴 루트 `PLAN.md`·`TODO.md`·`CHANGELOG.md` 3행에 외부 참조 확인과 정리 조건을 적었습니다. [INDEX](INDEX.md) 1절 tree에 한 줄을 더했습니다. 중앙 profile 31 `bc68358`에 맞춰 AGENTS·[GOVERNANCE](GOVERNANCE.md)·INDEX·[관리 진입](README.md)의 3행 공통 기준 문장을 옮김 기록 기준으로 바꿨습니다. HANDOFF와 루트 README에는 대응 문장이 없어 그대로 두었습니다. 루트 연결 안내 3개는 지우지 않았습니다.

- 운영 규칙 반복 문장 정정 (2026-11-14): 중앙 profile 31 `ffd7052`에 맞춰 [GOVERNANCE](GOVERNANCE.md) 3절에서 같은 뜻으로 두 번 적힌 비공개 원문 보존 문장 가운데 뒤 문장을 지웠습니다. 다른 문장은 바꾸지 않았습니다.

- 중앙 profile 기준 틀 병합 (2026-11-14): 31 `633dd64`의 32 profile 변경분을 수동 병합했습니다. [INDEX](INDEX.md) 1절에 현장 실제 경로에 맞춘 관리 공간 tree와 배치 안내 연결을 더하고 4절 결과물 문장을 배치 기준으로 바꿨습니다. PLAN 문장 교체는 현장 PLAN에 바꿀 문장이 없어 병합하지 않았고 이유를 [적용 기록](APPLICATION.md) 5절에 남겼습니다.

- MAIN-20261113-01 후보 기록 이동 (2026-11-14): AX 참고 문서 후보 기록을 새 결과물 규칙(GOVERNANCE 3절)에 맞춰 `.governance/outputs/`에서 [트랙](tracks/MAIN-20261113-01_ax-reference-docs/README.md)의 `40_results/`로 내용 변경 없이 옮기고, TODO·CHANGELOG의 링크 2개를 새 자리로 고쳤습니다.

- AX-HUB-21 옛 결과물 삭제 (2026-11-13): 사용자 결정으로 `.governance/outputs/MAIN-20261004-01_스킬목록병합/`(2개 파일)을 사본 없이 지웠습니다. 이 폴더를 가리키던 링크 1개는 삭제 직전 원격 commit 기준 고정 주소로 바꿨고, 경로·삭제 직전 SHA·복원 명령은 [삭제 기록](REMOVED.md)에 남겼습니다. `outputs/MAIN-20261113-01_AX참고문서후보/`는 TODO 대기 항목이 쓰므로 남겼습니다.

- MAIN-20261113-01 / AX-HUB-20 사후 대조 정정 (2026-11-13): 보안 위협 문서의 ASI04 이름을 대조 문서 제목 표기로 고치고, 최종 원문 표기 미확인 항목에 ASI05를 더했습니다. 지침 파일 노트에 Claude Code가 `AGENTS.md`를 직접 읽지 않는 경우와 가져오기 구성을 권하는 이유를, 설계 원칙 문서에 2.2절 표 일부가 Claude Code 문서의 권고라는 출처를 적었습니다. TODO의 "기존 갱신" 후보 수를 13건으로 바로잡았습니다.

- MAIN-20261113-01 / AX-HUB-20 단계 1 (2026-11-13): 사용자가 고른 권장 묶음 문서 4개를 썼습니다. `_reference/`에 [지침 파일 비교 노트](../_reference/agent_instruction_files_official_notes.md)와 [Agent Skills 규격 노트](../_reference/agent_skills_spec_official_notes.md), `07_ai_transformation/`에 [에이전트 설계 원칙](../07_ai_transformation/agent_design_principles.md)과 [에이전트 보안 위협 점검](../07_ai_transformation/agent_security_risks.md)입니다. 07 README 문서 목록, 루트 README 7절, `_reference/INDEX.md`에 연결했습니다. 새 노트에는 도구 간 비교와 규격만 두고 도구별 세부는 기존 노트를 가리킵니다. OWASP 항목은 이름과 자체 한 줄 설명만 두었고 원문 PDF는 접근 제한으로 열람하지 못해 OWASP 조직 저장소 두 곳에서 이름을 대조했습니다. 후보 기록의 자리 열과 넘어가는 주소를 정정했습니다.

- MAIN-20261113-01 / AX-HUB-20 단계 0 (2026-11-13): AX 환경 구축 참고 문서 후보 28건과 먼저 쓸 묶음(문서 4개), 문서 양식 예시를 [후보 기록](tracks/MAIN-20261113-01_ax-reference-docs/40_results/CANDIDATES.md)에 정리했습니다. 공식 주소와 게시일·버전은 2026-11-13에 직접 확인했고 미확인 항목은 기록 5절에 남겼습니다. `07_ai_transformation/`·`_reference/`·`06_career/` 본문은 쓰지 않았습니다.

- AX-HUB-19 (2026-11-12): 새 최상위 [07_ai_transformation](../07_ai_transformation/README.md)의 첫 골격을 만들었습니다. README에 목적(AX 환경 구축 참고 자료)과 나누는 기준(특정 도구 사용법은 `06_career/ai_tools/`, 도구와 무관한 AX 환경 구축 방법은 07, 공식 원문 정리는 `_reference/`), 관련 06 문서 5개 연결을 두고 문서 목록은 아직 없음으로 표시했습니다. 루트 README 목차와 `7. AI Transformation` 절, `06_career/README.md` 관련 섹션에 07 연결을 더했습니다. 내용 문서 작성과 기존 06 문서 이동은 하지 않았습니다.

- AX-HUB-17 / CL2CX-20261112-01 (2026-11-12): 중앙 원본 31 `22f92ad324a8e96d0ed3b2ce8f9c405fed23794d`의 문서 형식 경로 정정을 운영 규칙에 수동 반영했습니다. 검사 범위는 변경 문서 두 개의 문체·헤딩·링크·교차 앵커와 diff입니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 E(사용자 승인, 문체·형식). 별점은 [운영 규칙](GOVERNANCE.md)의 자료 유형 기준(블로그·튜토리얼 ★2, 공식 문서 ★3)을 그대로 적용해, 개인·커뮤니티 사이트와 사례 글·제3자 재게시·집계 자료 11줄을 ★3에서 ★2로 바꿨습니다(Brendan Gregg Linux Performance 3줄, roadmap.sh 4줄, AWS의 Riot 이전 사례 1줄, Cornell LII §1201 1줄, BenchLM 2줄). 공급사 발표·지원 종료 공지와 도서 공식 페이지는 ★3을 유지했습니다. `01_fundamentals/README.md`의 cs 행 설명에 빠져 있던 알고리즘·압축·게임 테스트를 넣고, `06_career/README.md`의 `ip_ownership_guide.md` 설명을 문서 내용(업무 외 저작물 귀속, 저작권법 제9조, 근로계약서 귀속 조항)에 맞췄습니다. 기존 설명의 "직무 발명"은 문서에 없는 내용이었습니다. 코드 블록 그림 속 한글(디렉토리 트리 포함 225개 블록)과 `절대`·`완전히`·`무조건`이 쓰인 44줄(부정문·용어·안전 경고·사실 진술)은 고치지 않았고, 리디렉션되는 ISTQB·Codex 문서 링크는 다음 정기 검사로 미뤘습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 D7-3(사용자 승인). ingress-nginx가 2026-03에 은퇴(저장소 2026-03-24 보관)해 [Kubernetes 기초](../02_infrastructure/containers/kubernetes_basic.md)의 Ingress 예시에서 nginx 전용 annotation을 빼고 `ingressClassName`을 자리표시로 바꿨습니다. Ingress API 동결·Gateway 권장 안내와 `### Gateway API` 소절(v1.7.0 CRD, Gateway·HTTPRoute·HTTPS 전환 예시)을 추가했습니다. [k3s](../02_infrastructure/containers/k3s.md)의 Traefik 비활성화 주석과 [Helm](../02_infrastructure/containers/helm.md) values 예시의 `className`(`helm create` 기본값 `""`)도 맞췄습니다. YAML은 PyYAML 파싱과 Gateway API v1.7.0 CRD 스키마 대조만 했고 클러스터 적용은 하지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 D7-2(사용자 승인). [n8n Docker 치트시트](../02_infrastructure/containers/n8n_docker_cheatsheet.md)를 n8n 2.x + PostgreSQL 기준으로 다시 썼습니다. n8n 2.0에서 MySQL·MariaDB 저장소 지원이 끝나 `DB_MYSQLDB_*` 예시를 공식 `DB_POSTGRESDB_*`와 postgres 서비스를 넣은 compose 예시로 바꾸고, 1.0에서 제거된 `N8N_BASIC_AUTH_*`를 지웠습니다. 연결 확인은 n8n 이미지에 DB 클라이언트가 없으므로 postgres 컨테이너의 `pg_isready`·`psql`로, 전체 초기화는 `docker compose down -v --remove-orphans`로 바꿨습니다. 1.x MySQL·MariaDB 사용자를 위한 이전 절(`export:entities`·`import:entities`)을 추가했습니다. compose 예시는 `docker compose config`로 구문만 확인했고 실행하지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 D7-1(사용자 승인, 문서 요구 유지·비용 재계산). [100TB/일 로그 설계](../02_infrastructure/data_pipeline/log_aggregation_100tb.md)와 [100GB/일 로그 설계](../02_infrastructure/data_pipeline/log_aggregation_100gb.md)의 `1. 요구사항` 자리에 중복돼 있던 비용 표를 문서 자체 조건에서 뽑은 요구사항 표로 바꿨습니다. 100TB의 MSK 절 표(Snowflake 표 사본)를 MSK 내용으로 바꾸고, 비용 표를 AWS Price List API 서울 온디맨드 단가와 산식으로 다시 계산했습니다. 100TB는 ~$63,000/월에서 ~$1,640,000/월(금액을 정한 8개 항목, Glue·Snowflake·Direct Connect는 사용량·계약별이라 산식만)이 됐고, 누적 용량은 4절 용량 표와 맞춘 180PB 기준이며 MSK 브로커 36대·OpenSearch 48대는 문서 요구에서 산식으로 정했습니다. 100GB는 빠졌던 OpenSearch EBS와 VPN 연결 요금을 넣어 ~$850/월에서 ~$1,159/월이 됐습니다. 그림·구성 요소·저장 등급·보관 기간은 바꾸지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): D8 후속(사용자 승인, A안)으로 `01_fundamentals/cs/game_testing/` 8개 문서의 Unity Test Framework 참고 자료를 `com.unity.test-framework@1.3` 패키지 문서에서 Unity 6.3 LTS 매뉴얼로 바꾸고, 편집기에 포함된 core 패키지라 Package Manager에서 판을 따로 고를 수 없다는 안내를 한 줄씩 더했습니다. 패키지 문서의 최신 판(1.9.0)은 Unity 6.2 이상의 사용 안내를 Unity Manual로 연결하고, 6.7은 2026-11-10 현재 Beta입니다. [Game Testing 노트](../_reference/game_testing_official_notes.md)의 출처·확인일과 Firebase Game Loop 실행 기기 설명(Test Lab에서 선택한 기기, 로컬은 시뮬레이터)을 공식 문장에 맞췄고 `_reference/INDEX.md` 확인일을 맞췄습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 D8(사용자 승인, 판 전환 정책 R1~R4). R1 패치 판: Trivy 예시 고정판을 v0.76.2로, nginx GeoIP2 문서·스크립트의 기본 nginx 판을 1.30.6으로 바꿨습니다. R2 주 판: `nginx_install.md`의 Mozilla 설정을 6.0 intermediate로 바꿔 DHE 암호 3개를 빼고(`apache_install.md`와 같은 목록) 5.7과의 차이를 짧게 남겼습니다. Elasticsearch 설치를 9.x(저장소 `9.x`, 이미지 9.5.6, JDK 21)로, MongoDB 설치를 9.0(저장소 `mongodb-org/9.0`, 키 `server-9.asc`)으로 바꾸고 각각 구판(8.x·8.0) 차이 절에 지원 종료일을 적었습니다. OpenVPN 설명은 2.7 문서 기준으로 바꾸고 2.6 old stable 지원 일정을 적었습니다. Rust 예시는 edition 2024·`rust-version = "1.85"`로 바꿨습니다. 짝인 출처 노트 4개와 `_reference/INDEX.md` 확인일을 2026-11-10으로 맞췄습니다. Unity Test Framework 링크는 현행 판(1.9)이 다른 주 판이고 1.6 이상 매뉴얼이 안내 쪽으로 바뀌어 고치지 않았습니다. .NET 11(정식 출시 전)과 AI 도구 비교 표(기준일 전면 갱신 필요)는 정책대로 보류했습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 D6(사용자 승인). `06_career/legal/_reference/`에 남아 있던 법령 본문·발췌 텍스트 8개(국가법령정보센터 6개, 미국 연방 법령 2개)를 비공개 저장소 `37_law`의 `moleg/`·`us/`로 옮기고(`37_law` `750fac0`, Git blob 해시 일치 확인), 이 저장소에서는 추적을 해제했습니다(로컬 파일 유지, `.gitignore`에 `*.txt` 추가). 2026-10-27에 hwp·hwpx·pdf만 옮기고 txt는 남았던 것을 같은 원칙으로 마무리한 것입니다. `privacy_law_guide.md`·`reverse_engineering_legal_guide.md`의 `reference` 주석을 지우고, 참고 자료의 txt 링크 4개를 공식 출처 주소로 바꿨습니다(정보통신망법 `law.go.kr` 추가). 기존 commit 이력의 사본은 그대로 남습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): D4 후속(사용자 승인)으로 다른 저장소의 `yunli` branch를 가리키던 링크 4개를 정리했습니다. 31 저장소의 `agent_skill_improvement_workflow.md`는 2026-10-03에 삭제됐습니다. 현행 `theorems/skill-maintenance.md`는 skill·저장소 지침 수정 절차만 다루고 32→41→35 흐름과 공용·개인 범위는 다루지 않아 후속 문서로 보지 않았습니다. 그래서 `harness_engineering.md`·`loop_engineering.md`·`_reference/github_references.md`의 링크 3개는 빼고 문장만 남겼습니다. 41 저장소의 참고 기록 링크는 같은 파일이 있는 `main`으로 바꿨습니다. `github_references.md`는 출처를 다시 확인하지 않아 `last_checked`를 유지했습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-10): 검증 후속 D3·D4(사용자 승인). D3: `02_infrastructure/iac/packer.md` 권리 고지의 `<옛 표기>`를 저장소 표기 `siasia86`으로 맞췄습니다. D4: 예시 브랜치로 쓰인 계정 이름 `yunli`를 바꿨습니다. `git_guide.md` fast-forward 그림은 앞 그림과 같은 `feature`로 바꾸고 `C---D` 열 위치를 유지했습니다. `gh_command_reference.md`는 명령 예시를 `feature/login`으로, `gh run list` 출력 예시의 branch 열을 `main`으로 바꿨습니다. 다른 저장소의 `yunli` 브랜치를 가리키는 실제 링크와 스크립트 안의 이름은 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 검증 후속 D9(사용자 승인, 공식 근거나 재현으로 확인된 문장 수준 정정만)으로 작은 정정 후보 약 90건 중 대부분을 90개 문서에서 고쳤습니다. 예: Python 내장 예외를 가리는 클래스 이름, Rust `should_panic` 메시지·axum `State` 추출자, C# 중복 선언, HTB 기본 class·conntrack 기본값·overcommit 권장 단서, bash `((frame++))`·`set -E`, SoftEther Raw L2TP·기본 리스너, Cloudflare Magic Transit의 ASN·계층, Kafka 리스너 분리·JMX 이미지·파티셔너, Harness YAML 이름, systemd 드롭인, Chaos Monkey 2010·성숙도 모델 출처, SSH ssh.socket·PQ 키 교환, Windows OpenSSH 인코딩, mod_php 전용 지시어 단서, XtraBackup `--defaults-extra-file`, 라이선스 가이드 법률 단정 완화, 출처 노트 5개(`_reference/INDEX.md` 확인일 반영). 판단이 필요하거나 절·표를 새로 짜야 하는 항목은 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 검증 후속 D2·D5(사용자 승인). D2: CVE-2026-43284 문서에서 이름이 바뀐 공개 PoC 저장소 링크 2곳을 지웠습니다. 같은 완화 방법(esp4·esp6·rxrpc 모듈 차단)은 탐지 도구 저장소의 "Fixing it" 절과 발견자 원본 저장소가 출처로 남아 있습니다. 두 CVE 문서의 PoC 빌드 명령 블록은 재현 시험 기록이라는 안내 문장으로 바꿨습니다. D5: 문서·예시 19개 파일의 내부망처럼 보이는 주소를 문서용 주소로 바꿨습니다(`10.200.101.0/24` → `192.0.2.0/24`, `10.200.90.155` → `198.51.100.155`, 마지막 자리와 서브넷 관계 유지). 상자 그림은 행 폭을 유지했고, AWS CLI 프로필 이름 예시는 `<profile>`로 바꿨습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 검증 후속 D1(사용자 승인, 문서 의도를 유지한 경고·안전 옵션만)으로 그대로 따라 하면 데이터 손실·보안 약화가 생기는 예시 14건을 16개 문서에서 정정했습니다. XtraBackup 백업 전 hook은 대상 스키마 명시·`\_`·`-N`·기본 dry run으로, PITR은 binlog 별도 복사·연속 적용과 기존 datadir `mv` 보존으로, `mysqld --initialize` 재실행 안내는 빈 datadir 한정·`--init-file` 재설정으로 바꿨습니다. PAM `pam_permit` 교체에는 원인 확인·백업·원복과 시험 컨테이너 한정 경고를, WinRM 운영 예시에는 인증서 검증과 CA 경로를, Terraform 정책에는 "최소 권한 아님" 제목과 좁히는 방법을 넣었습니다. CVE 문서의 제3자 스크립트는 커밋 해시 고정·실행 전 확인으로, AF_RXRPC·XFRM 소켓 시험은 모듈 자동 로드 경고와 "참고용" 판정으로, Vault 인증서는 SAN 재생성 절차로 고쳤습니다. ssh `accept-new`, bpftrace setcap 경고·capability 목록, gdb `ptrace_scope` 원복, iotop setcap 무효(Python 판), git hook의 stash 전후 비교, `@contextmanager` 재시도 예제 교체를 반영했습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 마지막 단계로 `_reference/` 출처 노트 92개를 4개 묶음으로 나눠 확인하고 66개를 정정했습니다. 앞 단계에서 본문 검증 중 수집한 노트 불일치 28건을 공식 자료로 다시 확인해 반영했고(오보 2건은 유지), 판·지원 종료·릴리스 날짜를 2026-11-09 기준으로 덧붙였습니다. 고친 노트만 `last_checked`를 2026-11-09로 바꾸고 확인만 한 노트는 날짜를 유지했으며, `_reference/INDEX.md`의 확인일과 최신 버전 열을 노트에 맞췄습니다. 도메인이 없어진 `isms.kisa.or.kr`(KISA 하위 도메인)을 `isms-p.or.kr`로, 404 주소(restic·vim man page·Windows 성능 문서)를 현행 주소로 바꿨습니다. 본문 `tls_https_testing.md`의 TLS 1.3 근거도 RFC 9846으로 맞췄습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 7단계로 `97_misc` 6개 문서와 루트 `license_guide.md`를 확인하고 7개 모두 정정했습니다. Apache(광고 조항 제거는 v1.1)·BSD(1999년 3-Clause) 연혁, GPL v2/v3 호환 조건, 폐기된 SPDX 식별자(3.29.0 목록 대조), pip-licenses·Maven license 플러그인 명령을 고쳤습니다. Kiro 요금·credit pooling·모델 배율과 Amazon Q 전환 정책, GameLift Servers·Multiplay 운영사 변경, Ubuntu 24.04의 `adb` 패키지 이름, 404였던 Samsung Knox 백서 주소를 반영했습니다. 법률 단정 표현, 비공개 저장소 링크, 재작성이 필요한 권고는 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 5단계로 `05_database` 28개 문서를 4개 묶음으로 나눠 확인하고 28개 모두 정정했습니다(06단계보다 늦게 끝나 순서가 바뀜). MySQL 설치 안내의 저장소 패키지(mysql-apt-config 0.8.33, el9-1)에 든 GPG 키가 2025-10-23에 만료되어 유효한 판(0.8.40, el9-4·el8-3·el10-3)으로 바꿨습니다. MySQL 8.4 기준으로 제거·이름 변경된 명령과 변수(`SHOW BINARY LOG STATUS`, `--source-data`, `innodb_redo_log_capacity`, `GET_SOURCE_PUBLIC_KEY`)를 반영하고, 격리·잠금·EXPLAIN·Performance Schema 단위·PostgreSQL 통계 열 이름을 공식 문서와 대조해 고쳤습니다. XtraBackup 증분 LSN 체인·없는 옵션·`set -e` 오류, PostgreSQL 18·ICU 기본값·`pg_promote()`, Redis 줄 끝 주석·`ZRANGE REV`, MongoDB 지원 일정·제거된 설정, Elasticsearch 8.19 설정, dbtrail 명령 옵션과 코어에서 제거된 who-changed 기능 안내를 반영했습니다. 위험한 백업 hook 예시와 PITR 절차, dbtrail 구조 문서 재작성은 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 6단계로 `06_career` 42개 문서를 5개 묶음으로 나눠 확인하고 35개 문서를 정정했습니다. 2026-10-01 시행된 정보통신망법·시행령 개정(침해사고 신고 24시간 이내, CISO 임원 지정)과 확정된 과징금 고시·유출 대응 안내서를 개인정보 해설에 반영했고, 도메인이 없어진 `www.privacy-i.kr` 링크를 제조사 공식 페이지로 바꿨습니다. Kiro CLI 3.0.0(V3 기본) 기준판 안내, Claude Ultra 플랜, Codex `ultra` effort, v0·Bolt 무료 조건, `gh copilot` 확장 종료, AWS 자격증 폐지·개명, PromQL CPU 식, f-string SQL 예시를 고쳤습니다. 예시의 실제 이메일·계정 이름·개인 경로를 자리표시자로 바꾸고, 06 README에 누락 문서 12개를 연결했으며, 출처 별점을 GOVERNANCE 5절 기준으로 맞췄습니다. Kiro V3 전면 개정, 법령 원문 txt 추적 해제 여부 등은 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 4단계로 `04_security` 35개 문서를 확인하고 35개 모두 정정했습니다. `tls_ssl_guide.md`의 testssl.sh clone 주소가 원본 이전 뒤 2026-11-05에 제3자가 새로 만든 빈 저장소(`drwetter/testssl.sh`)를 가리키고 있어 원본 `testssl/testssl.sh`로 바꿨습니다(저장소 내 다른 참조 0건). CVE 문서는 NVD·cve.org·CISA KEV·Ubuntu·Debian·Red Hat·ALAS 추적기와 대조해 CVSS·KEV 등재·수정 버전·패치 커밋과 탐지 스크립트 오류(AF_RXRPC 번호 등)를 고쳤고, PoC 코드는 열거나 실행하지 않았습니다. pam_faillock 배치 순서, sudo 리다이렉트, gitleaks 기본 디코딩 깊이, auditd openat, fail2ban 줄 끝 주석, AWS Network Firewall 기본 동작·로깅 호출, GuardDuty finding 이름, OWASP Top 10:2025 매핑, RFC 9846, 인증서 최대 200일을 반영했습니다. 출처 별점을 GOVERNANCE 5절 기준으로 맞추고 옛 디렉터리 이름(`01_cve`·`02_web_cwe`) 표기를 정리했습니다. PoC 링크 유지 여부, 제3자 스크립트 직접 실행 예시 등은 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 3단계로 `03_engineering` 20개 문서를 확인하고 14개 문서를 정정했습니다. Google SRE Book·Workbook 원문에 없는 인용을 원문 문장으로 바꾸고, 온콜 인원 기준(primary·secondary, 단일 사이트 최소 8명)과 N+2 예시를 원문대로 고쳤습니다. DORA 현행 5개 지표, MySQL online DDL의 INSTANT 범위, AWS 7 Rs·Savings Plans 4종·Spot price-capacity-optimized, LitmusChaos·OpenCost의 CNCF 단계, OpsGenie·Grafana OnCall OSS 지원 종료를 반영했습니다. ADR 템플릿 코드 블록에 자동 삽입된 목차 링크를 지우고 출처 별점을 GOVERNANCE 5절 기준으로 맞췄습니다. 내용이 빈 헤딩 2개와 출처 없는 수치는 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 2단계로 `02_infrastructure` 76개 문서를 6개 묶음으로 나눠 확인하고 71개 문서를 정정했습니다. ansible-core·molecule·PyYAML·promtool·amtool·git·`docker compose config` 등으로 설정과 명령을 재현했고, Airflow 3.0·Helm 4·Kafka 4(KRaft 전용)·Kubernetes 1.37·Prometheus 3.16 기준으로 제거·폐기된 문법과 버전을 갱신했습니다. MinIO 커뮤니티판 보관(archived), Terraform BSL, Zabbix AGPLv3처럼 상태가 바뀐 사실을 반영했고, HAProxy 문서의 ACME 인증서 이름·통계 유지 버전·Prometheus 접근 제한 순서 오류를 바로잡았습니다. 출처 별점을 GOVERNANCE 5절 기준으로 맞추고, 예시의 실제 계정 이름과 개인 경로를 자리표시자로 바꿨으며, root README Web Server 표에 누락 문서 1개를 연결했습니다. 재작성이 필요한 문서(100TB 로그 집계 비용, n8n MySQL 전제, ingress-nginx 예시 등)는 고치지 않았습니다.

- MAIN-20261109-01 / DOCS-32 (2026-11-09): 전체 문서 일회성 검증 1단계로 `01_fundamentals` 183개 문서를 9개 묶음으로 나눠 사실·최신성·일관성·출처·별점·보안을 확인하고 120개 문서를 정정했습니다. 명령·코드 예시는 python3 3.14·gcc·go·bash와 서버의 ltrace·strace·perf·tcpdump 등으로 실행해 대조했고, 폐기된 RFC(793·7231·7540·8446·5575 등)를 현행 번호로 바꿨습니다. 출처 별점은 [GOVERNANCE](GOVERNANCE.md) 5절 기준(공식 문서 3, RFC·PEP·주요 도서 4, 블로그·제3자 2)으로 맞췄습니다. 깨진 외부 링크 5건을 고치고, 예시의 실제 계정 이름을 자리표시자로 바꿨으며, root README Programming 표에 누락 문서 5개, linux·python README에 누락 문서 6개를 연결했습니다. Rust·C#은 컴파일 환경이 없어 공식 문서·소스 대조만 했고, 재작성이 필요한 예제 등 판단 항목은 고치지 않았습니다.

- MAIN-20261027-06 / DOCS-32 (2026-11-01): ISS-06을 종료했습니다. POLICY-31 CL2CX-20261027-04에 대한 Codex 반환 CX2CL-20261027-03(권장안 1~2)이 31 `8558b03`에서 수용 판정되어, 적용 계층을 common 단독으로 유지하기로 확정했습니다. 근거는 AGENTS 2절이 common만 선택한 경우 Codex 안내를 필수로 요구하지 않는다는 점과, 중앙 Codex 안내가 skill 선택표·개인 skill 수정 경로 중심이라 개인 지침과 겹친다는 점입니다. 확정 문장을 [적용 기록](APPLICATION.md) 4절에 원문 그대로 넣었습니다. `.codex/repository-guidance.md`·설정 4개·개인 skill은 변경하지 않았습니다.

- MAIN-20261027-07 / DOCS-32 (2026-10-27): ISS-07을 종료했습니다. 사용자 지시로 법령 원문은 비공개 저장소 `37_law`, 민감 자료는 `system-engineering-resources_private`에 두도록 나눴습니다. `06_career/legal/_reference`의 원문 17개(hwp·hwpx 16개, PDF 1개)를 추적 해제하고(로컬 파일 유지), `.gitignore`의 허용 예외를 없애고 보관 위치 안내로 바꿨습니다. [개인정보 보호법 가이드](../06_career/legal/privacy_law_guide.md)의 원문 다운로드 링크 12개를 개인정보보호위원회 출처 게시물 주소로 바꿨으며, 각 파일이 게시물 첨부와 일치함을 확인했습니다. 원문 19개는 `37_law` `d96a7da`, 개인정보가 담긴 PDF 1개는 `system-engineering-resources_private` `9bc806b`에 commit했습니다. 비공개 저장소 이름 변경(`34_system-engineering-resources_private` → `system-engineering-resources_private`)에 맞춰 S3 문서 2개의 안내를 고치고 참고 파일의 실제 경로(`99_archive/03_aws_jobs/01_AWS_jobs/`)를 덧붙였습니다. 기존 commit 이력의 원문 사본은 그대로 남습니다.

- MAIN-20261027-06 / DOCS-32 (2026-10-27): ISS-05를 종료했습니다. 중앙 profile common 계층에 맞춰 AGENTS·GOVERNANCE·INDEX를 중앙 원문으로 바꾸고 `.governance/README.md`에 공통 첫 문단을 추가했습니다. 설정 4개(`.gitignore`·검사 TOML 2개·`.gitleaks.toml`)는 중앙 공통 구간에 현장 예외·패턴·탐지 규칙을 CONSUMER LOCAL 구간으로 보존해 합쳤고, 추적 파일 무시 목록과 gitleaks 탐지 결과가 이전과 같음을 확인했습니다. Codex 계층 안내는 ISS-06, 원문 제외 대상 법령 파일 16개의 추적 상태는 ISS-07로 등록했습니다. [적용 기록](APPLICATION.md).

- MAIN-20261027-05 / DOCS-32 (2026-10-27): ISS-01을 종료했습니다. 중앙 profile 기준에 따라 루트 `TODO.md`·`PLAN.md`·`CHANGELOG.md`를 `.governance/`로 옮기고(`git mv`), 이동 문서의 상대 링크 42개와 `.governance` 관리 문서 링크 18개, `TODO2.md` 링크 2개, `asd_ste100_codex_communication.md` 링크 1개, INDEX 읽기 조건 표 2행, GOVERNANCE·INDEX·README의 위치 문구를 고쳤습니다. 루트에는 연결 안내 문서를 별도 commit으로 두었습니다. 나머지 중앙 병합은 ISS-05로 등록했으며 31은 변경하지 않았습니다. [적용 기록](APPLICATION.md).

- MAIN-20261027-04 / DOCS-32 (2026-10-27): ISS-04를 종료했습니다. [테스트 기법 README](../01_fundamentals/cs/testing/README.md) 구조 tree의 옛 이름 `02_testing/`을 `testing/`으로 고치고, 루트 README CS 표에 [게임 테스트](../01_fundamentals/cs/game_testing/README.md) 연결을 추가했습니다. TODO 검사 예외 표를 설정 파일의 예외 5건(heading 예외 포함)과 맞추고 원본을 verification으로 연결했습니다. HANDOFF 사전 결정 규칙(문서 정정)에 따라 수행했습니다.

- MAIN-20261027-03 / DOCS-32 (2026-10-27): `.governance`의 [HANDOFF](HANDOFF.md)·[ISSUE](ISSUE.md)·[verification](verification.md) 초기 후보 문구를 현장 상태에 맞게 정리했습니다. HANDOFF에 재개 지점 표와 사전 결정 규칙을 두고 10-04 현장 적용 사실을 바로잡았습니다. ISSUE에 열린 이슈 ISS-01~04(중앙 profile 위치 차이, 검사 예외 재검토, 적용 복구 자료 부재, 작은 색인 불일치)를 등록했습니다. verification의 일회성 CL09 작업 기록(`be2d024`, 검사 도구 0.5.0 고정과 기본 설정 예외 5개 반영)을 현재 상태 설명과 현장 검사 명령으로 바꿨습니다. 공통 규칙 문장과 중앙 profile 10-26 개정 적용은 변경하지 않았습니다.

- MAIN-20261027-02 / DOCS-32 (2026-10-27): [웹 서버 테스트](../01_fundamentals/cs/web_testing/README.md) 2차 묶음으로 Graceful Reload·Load Balancer·Cache/CDN·요청 보안·웹 관측성 테스트 문서 5개를 추가하고, [web_testing_official_notes](../_reference/web_testing_official_notes.md)에 reload·LB·HTTP 캐시·요청 보안·관측성 기준 절 5개를 더했습니다. nginx 제어 신호·upstream·limit_req·headers 모듈, HAProxy 3.2 설정·관리 문서, RFC 9111·5861, W3C Trace Context, OWASP Secure Headers ci 목록(2026-10-18 갱신본), MDN CORS와 대조했습니다. 요청 보안 문서는 방어 설정 확인만 다루고 공격 재현 입력값은 넣지 않았습니다. 1차에서 빠진 `04_security/hardening/tls_ssl_guide.md` 연결을 TLS 문서와 README 경계 표에 보완했고, 웹 서버 테스트 항목을 TODO에서 제거했습니다. 명령은 실제 호스트에 실행하지 않았습니다.

- MAIN-20261027-01 / DOCS-32 (2026-10-27): [웹 서버 테스트](../01_fundamentals/cs/web_testing/README.md) 1차 묶음으로 README와 HTTP 프로토콜·Reverse Proxy·TLS/HTTPS·웹 성능·Timeout 테스트 문서 4개, 공통 출처 노트 [web_testing_official_notes](../_reference/web_testing_official_notes.md)를 추가하고 root·Fundamentals·테스트 README와 `_reference/INDEX.md`에 연결했습니다. RFC 9110·nginx·HAProxy 3.2·k6·h2load·testssl.sh 공식 문서와 대조했으며, `curl`·`openssl` 옵션은 로컬 도움말로 확인했습니다. 명령은 외부 호스트에 실행하지 않았고 2차 묶음 5개 주제는 TODO에 남겼습니다. Fundamentals README의 cs 문서 수를 실제 추적 파일 수 52개로 정정했습니다.

- GWS-03 / DOCS-32 (2026-10-19): [SSD 마모 분산과 fio 성능 검수](../02_infrastructure/storage/ssd_wear_performance_validation.md)를 추가하고 README Storage 목록에 연결했습니다. FTL·마모 분산, fio 설정과 실쓰기량, SSS-PTS의 판정 범위를 공식 근거로 요약했습니다. 장비 시험·환경 변경은 수행하지 않았습니다.

- DOCS-32 / CL2CX-16 (2026-10-14): `.github/workflows/update-date.yml`에서 README 날짜 자동화 작업을 제거하고 검증 실행 조건을 `main`으로 한정했습니다.
### ASD-STE100 소통 적용 조사 — 2026-10-09

- `STE-20261009-01`: [사용 방안](../06_career/ai_tools/codex/asd_ste100_codex_communication.md)과 [출처 노트](../_reference/asd_ste100_official_notes.md)를 추가하고 root·Career·reference 색인에 연결했습니다. 공식 소개·FAQ와 OpenAI 문서, GitHub 후보 5개의 기준 커밋·파일·라이선스·설치 부작용을 대조했습니다.
- 한국어에는 명확한 대상·행동·조건·의미 보존 원칙부터 참고하는 방안을 제안했습니다. 표준 PDF 전체·AI 백서·한국어 개선 효과는 미검증이며 skill 설치·clone·설정 변경·31 정책 작업은 미실행입니다.
- 검증: 고정된 sia_scripts v0.3.3 태그 소스와 일치하는 검사기로 Markdown 6개의 style·heading·내부 링크 258개, 교차 앵커 2개, root README 문서 수 표기를 확인했습니다. Career의 표 형식은 검사기 지원 밖이므로 별도 대조해 AI 도구 문서 수 19개와 일치함을 확인했습니다. 담당 파일 Gitleaks와 git diff --check도 통과했습니다. CI release archive 실행과 원격 CI는 이 로컬 검증에 포함하지 않습니다.
- 첫 검사에서 새 출처 표 행의 정렬 오류를 보정했습니다. 하위 README 검사 실패는 검사기가 (N개) 표기만 인식한 데서 발생했으며, 실제 표와 파일 수를 대조해 보완했습니다. 원본 실패 로그는 로컬 기록에 보존했습니다.
- 커밋 필수 검사에서 기존 출처 색인의 푸터 누락을 발견했습니다. Git의 최초 추가일 2026-05-22를 확인해 푸터를 보완했습니다. 필수 검사 설정과 hook은 변경하지 않았습니다.


### main 병합 검토 — 2026-10-04

- MAIN-20261004-01에서 CAT-20261004-01 스킬 목록의 faa6574를 main에 fast-forward·일반 push하고 원격 SHA를 확인했습니다. 후보 문서 5개·링크 259개·교차 앵커 8개·inventory·Gitleaks를 재검사했고 확인된 모순·의도 불일치는 없었습니다. [병합 결과와 미실행](https://github.com/siasia86/system-engineering-resources/blob/167744a19d578d71e921b4a918b2b12c1fc800e8/.governance/outputs/MAIN-20261004-01_%EC%8A%A4%ED%82%AC%EB%AA%A9%EB%A1%9D%EB%B3%91%ED%95%A9/20261004_markdown/REVIEW.md).


- 기존 날짜 CI의 UTC 기준으로 한국 날짜의 작성일보다 갱신일이 하루 앞서지는 문제를 확인해 날짜 계산만 KST(UTC+9, POSIX TZ=KST-9)로 지정했습니다. 날짜 갱신은 기존처럼 yunli에서만 수행하며 Windows Git Bash에서도 자정 경계 두 사례를 확인했습니다.

- M12-MAIN-20261004-01에서 yunli의 Codex·harness·loop 자료와 현장 .governance 적용 문서를 검토했습니다. main 고유 commit은 없으며 변경 Markdown 15개와 파일 링크·교차 fragment·diff·Gitleaks를 확인했습니다.
- 외부 자료의 최신 사실 재조사나 도구 설치는 이번 Git 통합 검사에 포함하지 않습니다. [여섯 저장소 게시 확인](https://github.com/siasia86/12_github-main/blob/main/.governance/outputs/M12-MAIN-20261004-01/20261004_markdown/REVIEW.md)에서 최종 원격 상태를 확인합니다.

### Added

- 2026-10-15: 같은 문서의 "결론" 절을 상세 항목 우선순위에 맞춤. "SE라면"에 Bash(1순위 필수)와 JavaScript(3순위 권장)를 넣고 Go를 "강력 권장"으로, Ruby vs Rust의 "둘 다 우선순위 낮음"을 "Rust 4순위(권장), Ruby 낮음"으로, 추천 학습 경로를 "Python·Bash 깊게 학습 + Go 시작"으로 고침.
- 2026-10-15: [언어별 학습 가이드](../06_career/roadmap/se_complete_roadmap_programming_languages.md)의 "SE에게 추천하는 언어 우선순위" 요약을 언어별 상세 항목의 우선순위에 맞춰 다시 씀(Python·Bash 1순위, Go 2순위, JavaScript 3순위, Rust 4순위, PowerShell 조건부, C·Ruby 낮음). 우선순위 "낮음"인 C를 시스템 언어의 "권장"에서 "선택" 묶음으로 옮김.
- 2026-10-15: [언어별 학습 가이드](../06_career/roadmap/se_complete_roadmap_programming_languages.md)의 언어 이름 뒤 별 표시 10개를 제거(묶음·우선순위·학습 난이도에 같은 정보가 있음). [SE 로드맵](../06_career/roadmap/se_roadmap.md) 자격증 가이드의 `난이도: ★★` 10줄을 `난이도: 2/5`처럼 숫자로 바꿔 출처 별점과 구분.
- 2026-10-15: 출처 목록 별점 9줄을 `— ★★★☆☆` 형식(대시와 빈 별 포함)으로 맞춤. [KPI 발표 자료](../02_infrastructure/monitoring/game_infra_kpi_presentation.md) 8줄, [ASN·DDoS 가이드](../01_fundamentals/networking/asn_and_cloudflare_ddos.md) 1줄. 별 개수는 바꾸지 않았고, 로드맵의 언어 평가·난이도 표시는 출처 별점이 아니어서 그대로 둠.
- 2026-10-15: [게임 인프라 KPI 발표 자료](../02_infrastructure/monitoring/game_infra_kpi_presentation.md)의 깨진 내부 링크 2개(`./asn_and_cloudflare_ddos.md` → `01_fundamentals/networking/`)를 고치고 별점을 `— ★★★☆☆` 형식으로 맞춤. 링크 글자에 대괄호가 겹쳐 고정 검사 도구(0.3.3)가 놓치던 링크로, 다른 판의 검사기 대조에서 발견.
- 2026-10-15: Claude [데스크톱 앱 가이드](../06_career/ai_tools/claude/claude_code_desktop_guide.md) 8절에 Projects(beta)와 Code 세션의 차이를 추가. 스레드의 실행 위치(기본 클라우드), 로컬·SSH 세션은 프로젝트에 넣을 수 없음, Remote Control로 연결한 폴더의 Work locally 스레드, 미commit 변경 손실 위험, 사용 가능 위치와 공유 제한을 정리하고 [참조 노트](../_reference/claude_code_official_notes.md)에 claude-projects 근거를 기록.
- 2026-10-15: Claude 문서 3개를 `06_career/ai_tools/claude/`에 추가. [기본 사용법](../06_career/ai_tools/claude/claude_code_basics_guide.md)에 요청 작성·plan 모드·`@`·`!` 입력·컨텍스트 관리·세션 재개·되돌리기 한계·diff 검토를, [데스크톱 앱 가이드](../06_career/ai_tools/claude/claude_code_desktop_guide.md)에 Code 탭·SSH 원격 세션 요구 사항·연결 끊김·세션과 사이드바 정리·Remote Control·CLI 차이를, [스킬 목록](../06_career/ai_tools/claude/claude_skills_catalog.md)에 개인 스킬 14개와 기본 제공·계정 스킬·같은 이름 우선순위를 정리. root·Career README(문서 수 28) 색인에 연결.
- 2026-10-15: [리버스 엔지니어링 법적 기준 가이드](../06_career/legal/reverse_engineering_legal_guide.md) 추가. AI 기반 역분석 도구(morluto/rea) 확산을 계기로 도구 라이선스·대상 약관·법률을 구분하고, 저작권법 제101조의3·제101조의4·제104조의2·제136조, 정보통신망법 제48조·제71조, 17 U.S.C. §1201(f)(g)(j), 37 CFR §201.40(b)(18)을 정리. 원문 발췌 3개를 `06_career/legal/_reference/`에 저장하고 root·Career README, DRM·IP 가이드에 연결.
- 2026-10-14: [Claude 참조 노트](../_reference/claude_code_official_notes.md)와 Claude 문서 4개를 `06_career/ai_tools/claude/`에 추가. [공통 개념](../06_career/ai_tools/claude/claude_code_concepts.md), [Linux CLI 가이드](../06_career/ai_tools/claude/claude_code_cli_linux_guide.md), [확장 기능 가이드](../06_career/ai_tools/claude/claude_code_extensions_guide.md), [모델 가이드](../06_career/ai_tools/claude/claude_models_guide.md)에 설치·인증·권한 모드·설정·Skills·Hooks·Subagents·MCP·모델 라인업과 가격을 정리하고 root·Career README와 reference INDEX에 연결.
- 2026-10-13: [Aside AI 브라우저 가이드](../06_career/ai_tools/aside_browser_guide.md)와 [공식 참조 노트](../_reference/aside_browser_official_notes.md)를 추가. 지원 플랫폼·기능·요금·권한·데이터 처리·CLI/MCP·제작사 벤치마크를 조사하고 공식 자료의 Max 사용량·데이터 전송 설명 차이를 기록. root·Career README와 reference INDEX에 연결.
- 2026-10-13: Boris Cherny의 다섯 업무 원형 조사 [본문](../06_career/ai_tools/ai_work_archetypes.md)과 [참조 노트](../_reference/ai_work_archetypes_notes.md)를 추가. 원형 정의·제품 단계별 조합·AI 활용과 인프라 적용 예시를 구분하고 root·Career README 및 reference INDEX에 연결. X 원문 직접 열람 제한과 출처별 확인 상태를 기록.
- `CAT-20261004-01`: `codex_skills_catalog.md`에 세션 제공 스킬 31개의 한 줄 설명, 업무별 선택과 명시적 호출 예시를 추가. 개인 7개·기본 4개·플러그인 20개를 구분하고 root·Career 목차와 설정 가이드에 연결. 스킬 설치·설정 변경은 포함하지 않음.
- Jev 공식 참조 노트와 개념·사용 가이드 3개를 추가. TypeSafe AI 공식 문서에 따라 질문 유형, 확률·신뢰도, 모델 제한, HTTP API·Python SDK와 결과 분기를 정리하고 root·Career README 및 reference INDEX에 연결.
- `04_security/hardening/ai_agent_sandbox_concepts.md`에 샌드박스·OS 권한·실행 승인·원격 실행기의 역할과 한계, 저장소별 책임, 환경별 권한 및 검증 기준을 개념 문서로 추가하고 root·Security README에서 연결. 운영 설정 변경은 포함하지 않음.
- `codex_concepts.md`, `codex_gui_guide.md`, `codex_ide_guide.md`, `codex_api_guide.md`를 추가해 Codex 공통 개념과 GUI·IDE·API 사용 경로를 분리.

### Changed

- 2026-10-15: Claude [Linux CLI 가이드](../06_career/ai_tools/claude/claude_code_cli_linux_guide.md)와 [참조 노트](../_reference/claude_code_official_notes.md)의 "작성 서버에 CLI 미설치" 문구를 데스크톱 앱 SSH 세션이 설치한 2.1.295 확인 결과로 정정하고, 그 설치본이 `PATH`에 없다는 점을 추가. [공통 개념](../06_career/ai_tools/claude/claude_code_concepts.md)의 도입 링크와 학습 순서에 새 문서 3개를 연결.
- 2026-10-15: Career README의 legal 문서 수를 실제 파일 수 5개로 정정하고 색인에서 빠져 있던 개인정보 문서 2개를 root·Career README에 추가. DRM·IP 가이드의 "라이선스 가이드 (작성 예정)"를 실제 문서 링크로 교체.
- 2026-10-14: `06_career/ai_tools/`를 공통 문서와 도구별 하위 폴더(`claude/`·`codex/`·`kiro/`·`jev/`)로 재구성. Codex 8개·Kiro 4개·Jev 2개를 `git mv`로 옮기고 저장소 전체 상대 링크, 검사 예외 설정(`.md-style-check.sia_scripts.toml`), TODO 예외 표를 새 경로로 갱신.
- 2026-10-14: 기존 Claude 관련 내용 검토. `ai_coding_tools_comparison.md`의 Claude Code 플랫폼·플랜(모든 유료 플랜, Max $100부터), 권한 모드 6종, 클라우드 제공자 표현, 커스텀 에이전트(`.claude/agents/`), 2026-07 벤치마크 시점 안내를 정정. `harness_engineering.md`의 `CLAUDE.md`·`.cursorrules` 예시, 요청 템플릿의 Anthropic 문서 주소, AI 도구 참조 노트의 Claude Code 항목을 갱신.
- 2026-10-13: `.gitignore`에 Claude Code 세션 worktree 위치 `/.claude/worktrees/`를 추가. 31 공통 ignore 원본(31_governances 012569e)의 같은 규칙을 이 한 줄만 병합했고 `.claude/`의 프로젝트 설정·skill은 Git 추적 대상으로 남김.
- 2026-10-13: CI workflow의 Node.js 20 지원 종료·runner 전환 경고 대응. `actions/checkout` v4→v7, `actions/setup-python` v5→v7(모두 Node 24 런타임)로 올리고 `runs-on`을 `ubuntu-latest`에서 `ubuntu-26.04`로 고정. `ubuntu-latest`의 26.04 순차 전환(2026-10-19~11-19) 동안 OS가 섞이지 않게 함.
- 2026-10-13: [`git_command_reference.md`](../02_infrastructure/cicd/git_command_reference.md)의 사실 오류 정정. `git restore file_name`이 마지막 커밋이 아니라 Staging Area 기준임을 바로잡고 마지막 커밋 복원 명령을 추가, `git config --list`가 전체 범위 설정을 출력함을 명시, `store` helper의 저장 파일 범위, 기존 문법 블록의 `switch --detach` 위치, push 예시 주석, `master`·개인 브랜치명 예시를 정리. root README CI/CD 표에 연결하고 gh 문서와 상호 링크, gh 문서에 `gh run list --commit`의 전체 SHA 조건 보충.
- 2026-10-13: `github_cli.md`를 [`gh_command_reference.md`](../02_infrastructure/cicd/gh_command_reference.md)로 이름을 바꾸고 gh 문서를 하나로 통합. `gh run` 조회·대기·종료 코드 판정과 기본 저장소 지정, PR 체크 대기·`--match-head-commit`, 환경 변수·텔레메트리, Linux 패키지 서명 키 교체를 추가하고, 존재하지 않는 `repo (read)` scope, SSL 오류 해결책, 보관된 `gh-copilot` 확장, `--body` secret 입력을 바로잡음. root README 링크 갱신.
- `codex_concepts.md`를 사람의 학습을 위한 입문 문서로 개편. 모델·에이전트·도구의 역할, 사용 화면과 실행 위치, 파일 경로 오류 수정 예시, 설정·권한 비교표와 추천 학습 순서를 추가하고 root·Career README 설명을 갱신.
- root의 중복 `codex_cli.md`를 제거하고 `06_career/ai_tools/codex_cli_linux_guide.md`를 Codex CLI 사용자 가이드 canonical 문서로 유지.
- `_reference/codex_cli_official_notes.md`를 공식 사실·버전·인증·권한 검증 source로 유지.
- 기존 CLI 문서를 TUI·로컬 작업·비대화형 실행 중심으로 연결하고, root·Career README inventory에 Codex 문서군을 등록.

### Fixed

- Codex 설정 문서의 `exec` 승인 옵션 오류, 사용자·프로젝트·profile 설정 범위와 우선순위 누락을 수정. `CODEX_HOME`, `AGENTS.override.md`, HTTP MCP·OAuth 적용 조건과 Skills 기본 제공·선택 로드를 명시.
- Codex 문서의 승인 생략·샌드박스 해제 혼동, `/status` 확인 범위, 추론 수준·비용 고정 배수·목표 반복·메모리 자동 로드와 GUI 승인 범위의 모호한 표현을 정리. `project_doc_max_bytes`는 공식 문서 간 표현 차이와 보수적인 운영 권장을 함께 기록.
- `codex_cli_linux_guide.md`의 인증·TUI 표 정렬을 CI의 한글 표시 폭 규칙에 맞게 수정.
- Codex 공통 개념·GUI·IDE·API 문서의 목차, 목차 복귀 링크, 참고 자료, 통계 영역을 저장소 공통 양식에 맞게 보정.

### Verified

- 2026-10-15: Claude 참조 노트 3차 대조로 code.claude.com의 quickstart·interactive-mode·common-workflows·best-practices·checkpointing·commands·desktop·skills 원문을 내려받아 새 문서의 명령·단축키·제약을 확인. 사이드바 섹션 구성은 공식 문서에 없어 데스크톱 앱에서 관찰한 결과로 기록. 개인 스킬 설치본 79개 파일이 SKILL-35 원본과 SHA-256 일치. 로컬 sia_scripts 0.4.0으로 전체 Markdown 473개의 링크 1127개·heading, style 383개, root README inventory, 담당 파일 Gitleaks와 `git diff --check` 통과. 단축키 동작·`--version` 외 CLI 실행은 미검증.
- 2026-10-15: 저작권법(법률 제21336호, 2026-08-11 시행)을 law.go.kr에서, §1201은 law.cornell.edu에서, 37 CFR §201.40은 eCFR(최종 개정 2024-10-28)에서 받아 조문 번호·요건·벌칙을 대조. 2026-02-10 개정으로 무력화 금지 벌칙이 제136조 제3항 제3호의3으로 이동한 것을 확인. EU Directive 2009/24/EC는 EUR-Lex 자동 요청 차단으로 원문 미대조.
- 2026-10-14: Claude 참조 노트는 code.claude.com 문서 13종을 1차, platform.claude.com 모델·가격·폐기 일정과 claude.com/pricing·GitHub 릴리스(v2.1.299)를 2차로 대조. `loop_engineering.md`의 `/goal`·`/loop` 설명은 공식 문서와 일치. 로컬 `claude` CLI 미설치로 실행 대조는 미실시, Kiro 모델 목록은 kiro-cli 로그인이 필요해 미확인.
- 2026-10-13: Git 문서 정정 후 대상 Markdown 4개의 style·heading, 전체 Markdown 464개의 링크 1045개, root README inventory와 `git diff --check`를 확인. `git restore --source=HEAD --staged --worktree`와 `git config --local --list` 동작을 로컬 Git 2.43.0 임시 저장소에서 확인.
- 2026-10-13: gh 문서 통합 후 대상 Markdown 2개의 style·heading, 전체 Markdown 464개의 링크 1042개, root README inventory와 `git diff --check`를 확인. 새 예시 명령은 로컬 gh 2.45.0으로 실행·도움말 대조했으며 최신 v2.102.0 전용 옵션(`--worktree`, `clipboard`)은 릴리스 노트로만 확인.
- 2026-10-13 main 게시 준비: 기존 ASD-STE100 변경을 보존하면서 두 조사 문서를 병합. `sia_scripts` v0.3.3 태그 소스로 담당 Markdown 8개의 style·heading·내부 링크 271개와 root README inventory를 확인했고, Career AI 도구 실제 문서 수 21개를 대조. 로컬 검사와 원격 CI 실행은 구분하며 원문 접근·제품 실행의 기존 미검증 범위는 유지.
- 2026-10-13: Aside 관련 Markdown 6개의 style·heading·파일 링크, root README inventory와 Career `ai_tools` 실제 문서 수 20개를 확인. 공식 제품·도움말 및 다운로드·변경 이력·요금·정책을 두 차례 대조. 로컬 문서 검사는 설치된 `sia_scripts` 0.3.0을 사용하며 CI 0.3.3·Aside 설치와 실제 동작·벤치마크 재현은 미실행.
- 2026-10-13: 다섯 업무 원형 관련 Markdown 6개의 style·heading·파일 링크 258개와 root README inventory, Career `ai_tools` 실제 문서 수 19개, 담당 파일의 Gitleaks v8.30.1·공백 검사를 통과. 설치된 `sia_scripts` 0.3.0 도구를 사용했으며 CI 고정 버전 0.3.3 실행은 미실행. 원형 명칭·복수 역할·제품 단계별 조합은 전재·보도·해설로 두 차례 대조했고 X 원문 직접 검증은 미완료로 기록.
- `CAT-20261004-01`: `sia_scripts` v0.3.3 태그 소스로 변경 Markdown 5개의 style·heading·파일 링크 259개, 교차 fragment 8개와 root README inventory를 확인. Luna의 스킬 목록 31개 대조에서도 누락·중복 없음. 스킬 설치·실제 동작 검증은 미실행.
- 2026-10-01 Codex 입문 문서 개편 후 기존 수정분을 포함한 변경 문서 10개의 Markdown style·heading·link, root README inventory, gitleaks와 `git diff --check`를 검증. 파일 경로 예시의 공백 포함·미포함·없는 파일 동작을 임시 디렉토리에서 확인. 실제 Codex 모델 호출은 실행하지 않음.
- 2026-10-01 Codex 설정 관련 변경 문서 8개의 Markdown style·heading·link, root README inventory, gitleaks와 `git diff --check`를 검증. CI 체크섬·manifest를 대조한 `sia_scripts` v0.3.3을 사용하고, 로컬 Codex CLI 0.159.3의 `--help`로 `exec` 예제 12개의 인수 문법과 TOML 예제 3개의 구문을 확인. 실제 모델 호출·OAuth 로그인·설정 적용은 실행하지 않음.
- Jev 추가 문서와 관련 인덱스의 Markdown style·heading·link 및 root README inventory를 CI 체크섬과 동일한 `sia_scripts` v0.3.3으로 검증. Python·Bash·JSON 구문과 큐 분기 경계값을 로컬에서 확인하고 gitleaks 검사를 통과. 인증된 API 호출과 SDK 실행은 수행하지 않음.
- 고정된 `sia_scripts` v0.3.3으로 변경 Codex 문서의 Markdown style·heading·link 검사와 root README inventory 검사를 통과.

---

## [5.0.2] - 2026-09-15

### Added

- 범용 테스트 개념 문서 11개 추가: 테스트 케이스 설계, 테스트 오라클, 시나리오 기반 테스트, 위험 기반 테스트, 테스트 추적성, 테스트 데이터 관리, 동시성 테스트, 장애 주입 테스트, 탐색적 테스트, Property-based Testing, Mutation Testing.
- 게임 도메인 테스트 문서 8개 추가: 게임 테스트 케이스 설계, 상태, 플레이 시나리오, 저장·불러오기, 매칭, 게임 경제, 게임 성능 및 디렉토리 README.
- `software_testing_official_notes.md`, `game_testing_official_notes.md`, `load_testing_official_notes.md`, `advanced_testing_official_notes.md` 공통 reference note 추가.
- 게임 서비스 실행 계획 디렉토리 README 추가.

### Changed

- 테스트 문서 README inventory에 범용 테스트 개념 문서를 등록.
- 게임 테스트 README inventory에 게임 도메인 문서를 등록.
- `_reference/INDEX.md`를 문서별 1:1 reference가 아닌 문서군별 공통 reference note 재사용 구조로 갱신.
- `mobile_game_load_testing_plan.md`를 `03_engineering/delivery/game_service_testing/`로 이관.
- 모바일 게임 디바이스 솔루션 비교 문서는 `97_misc/`에 유지하고 이관된 부하 계획 링크를 갱신.
- root README의 모바일 게임 부하 테스트 inventory 경로를 갱신.

### Verified

- Batch 1~7 및 보조 Batch 8-1·8-2의 문서 작성·README inventory·공통 reference 연결을 완료.
- 공통 reference note별 공식 출처 대조와 `@fact-check` 2회, 본문 문서 fact-check를 완료.
- 변경 문서의 `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check`, `git diff --check`, `gitleaks` 검증을 완료.
- 완료 항목을 `TODO.md`에서 제거하고, 활성 잔여 이슈만 유지하도록 정리.

---

## [5.0.1] - 2026-09-14

### Changed

- 개인정보 보호법 가이드의 제34조 유출 통지 기한을 2026-09-11 시행 현행 법령 기준으로 확인하고, 시행령 제39조의 72시간 이내 기준과 법 제34조 제1항의 "지체 없이" 표현을 함께 명시.
- 개인정보 보호법 제34조 제1항의 통지 항목 6호·7호가 현행 법령에 포함됨을 확인하고 fact-check TODO를 정리.

### Verified

- 국가법령정보센터 현행 개인정보 보호법·시행령 원문과 가이드의 관련 조문·출처·내부 링크를 대조.
- README inventory, Markdown style·heading·link 검사와 gitleaks 검증을 완료.

---

## [5.0.0] - 2026-08-31

### Added

- 계정·repository·운영 도구에 종속되지 않는 공용 `skill-review` prompt를 추가하고 agent skill 탐색 대상에서 제외.

### Changed

- 32 root `README.md`와 `PLAN.md`에 31 `governances` 공통 정책 원본 및 35 `agent-skill` 공개 mirror 역할을 명시.
- `97_misc/similar_repos.md`의 checker 참조를 30 `sia-*` release wrapper 기준으로 갱신.

### Verified

- 32 문서 repository의 system engineering 학습 영역·하위 README·문서 inventory·Markdown 품질 검증 기준 유지 상태를 확인.

### Removed

- `00_governance/01_repository_governance/` 제거 (14개 파일). 공통 governance policy·template·TODO·분리 계획은 [31 `governances`](https://github.com/siasia86/31_governances) `v0.1.0`으로 이관하고 rollback 대상으로 32 commit `71fe059`를 보존합니다.
- `00_governance/02_kiro/skills/repo-governance/SKILL.md`, `00_governance/03_claude/README.md`, `00_governance/README.md`, 루트 `README.md`의 `01_repository_governance` 참조를 31 `governances` 링크로 갱신.
- `00_governance/` 전체 제거 (57개 파일). Kiro·Claude agent skill 공개 mirror는 [35 `agent-skill`](https://github.com/siasia86/35_agent-skill)로 이관하고 rollback 대상으로 32 commit `22b4608`을 보존합니다. `.md-style-check.sia_scripts.toml`과 workflow의 `00_governance/02_kiro` 관련 예외·조건도 함께 정리했습니다.

---

## [4.0.0] - 2026-08-31

### Changed

- 30 checker source·test·release 전환과 32 consumer 검증을 완료하고, 상세 migration 기록을 30 `docs/migration/`으로 통합했습니다. 32 `PLAN.md`는 system engineering 문서 repository 운영 항목만 유지합니다.
- 32 active 문서·hook·skill과 전역 Kiro hook의 checker 실행 참조를 설치된 `sia-*` wrapper 기준으로 갱신.
- 32 consumer workflow run `33154491505`에서 `v0.3.3` release download·checksum·manifest·style·heading·link·inventory 검증 전체 성공.
- 30 consumer pin을 `v0.3.3`과 SHA-256 `0b293d76e8efb55e93ad6bb21c0b00bf4362e60aa7a3a4ea5e6d752a012bb4ad`로 갱신.
- 30 consumer pin을 `v0.3.2`와 SHA-256 `9f9b74a0b21926a55a72fc11fbb59cd049da176413e5617249af3ecf68dabcc4`로 갱신.
- `iperf3` 공식 reference와 네트워크 통신 품질 측정 가이드 추가.
- `PLAN.md`에 2026-08-28 local baseline, 외부 의존성, 원격 적용 순서를 정리.
- 첫 test target에 root SSH와 임시 HTTPS artifact를 사용해 `0.3.0 install → 0.3.1 update → 0.3.0 rollback`을 검증. 운영 artifact repository와 일반 사용자 Controller `become`은 미완료로 유지.
- `30_sia-scripts`에 GitHub Actions 검증 workflow와 `v*.*.*` tag 전용 versioned artifact 생성을 추가.
- `30_sia-scripts` release manifest에 source commit provenance와 파일별 SHA-256 검증을 추가.
- `01_fundamentals/linux/neovim_guide.md` 추가 및 Neovim 고유 운영 기능·window 분할·LSP·Tree-sitter·headless 사용법 기록.
- `01_fundamentals/linux/tmux_guide.md` 추가 및 session·window·pane 운영과 Neovim window 분할 차이 기록.
- `01_fundamentals/linux/zoxide_guide.md` 추가 및 설치·shell 초기화·query·database 관리·rollback 절차 기록.
- 30 저장소 CI slice commit `e69bcfb`를 `origin/main`에 push하고 로컬 검증을 완료.
- localhost 임시 HTTPS artifact endpoint에서 `0.3.0 install → 0.3.1 update → 0.3.0 rollback`을 실제 로컬 경로에 적용.
- 로컬 `current -> 0.3.0` baseline, root ownership·permission, 비권한 사용자 쓰기 차단을 확인.
- `30_sia-scripts` 공용 검사기·release artifact·Ansible 배포 구조의 migration 상태를 갱신.
- 오류 fixture 4종과 legacy/common 검사기 반환 코드 대조를 완료.
- 일반 계정 Controller의 사용자 소유 `.venv`에서 Ansible syntax check를 완료.
- 최종 검증이 끝난 30 저장소(`30_sia-scripts`) 검증 clone을 사용자 승인으로 삭제. 원격 `main`과 사용자 clone을 기준 상태로 사용.
- `ansible-lint==26.8.0`과 `ansible-core==2.20.5` 조합의 lint 통과를 확인.
- 임시 target에서 release install·update·rollback과 root 소유자·권한·entrypoint 동작을 확인.
- 32 저장소 자체 Markdown style·heading·link 검사, gitleaks, `git diff --check`를 재검증해 통과.
- 일반 계정 Controller의 local `become` probe가 password-required sudoers 정책으로 실패함을 확인하고, root harness 적용과 운영 검증 미완료 상태를 기록.

### Removed

- root legacy checker 4개(`md-style-check.py`, `md-heading-check.py`, `md-link-check.py`, `readme_inventory_check.py`)를 cleanup commit `fe4a9d6d48aba374645542cec812eda583487057`에서 삭제.
- 삭제 후에도 `strip-footer-md.py`, `.md-style-check.toml`, `.md-heading-check.toml`, `.md-style-check.sia_scripts.toml`은 유지.

### Verified

- cleanup 문서 hash 정정 push 후 30 CI run `33156553757`와 32 consumer CI run `33156558662`가 성공했으며, 30·32 working tree와 원격 branch 동기화를 확인.
- cleanup 후 32 consumer workflow run `33154800657`에서 private release download·checksum·manifest·embedded file hash·style·heading·link·inventory 검증 전체 성공.
- cleanup rollback은 `git revert fe4a9d6d48aba374645542cec812eda583487057`로 수행할 수 있도록 분리.

## [3.11.0] - 2026-08-27

### Added

- 32 Markdown CI를 30 `0.3.1` release asset·SHA-256·manifest 검증 후 `sia-*` wrapper를 실행하도록 전환.
- 30 generic checker의 `file_skip`·`path_skip` contract와 32 policy profile을 추가하고 style·heading·link·inventory parity를 확인.
- 30·32 검증 script 이관 workflow를 시작하고, parity·config·CI consumer 검증 전까지 32 root script 삭제를 보류.
- 저장소별 규칙 체계 `.governance/`와 저장소 규칙 우선순위 정책(`00_governance/01_repository_governance/governance_precedence.md`, 2026-08-31 [31 governances](https://github.com/siasia86/31_governances)로 이관) 추가.
- governance 개선 항목 관리 문서 `governance_todo.md` 추가.
- 작업 템플릿 6종 추가: TODO, CHANGELOG, README, RUNBOOK, GOVERNANCE, VERIFICATION. 기존 PLAN·ISSUE 템플릿을 포함해 8종이 됩니다.
- 헤딩 구조·목차 앵커 검사기 `md-heading-check.py` 추가 (anchor / number / level / duplicate).
- `md-heading-check.py` 예외 설정 `.md-heading-check.toml` 추가 (파일별 검사 항목 제외 지원).
- `md-heading-check.py` 에 목차 완결성 검사(`toc`) 추가. 본문 H2가 목차에 없으면 검출합니다.
- `md-style-check.py --list-skips` 옵션 추가. 파일별 제외 항목과 사유를 출력하고, 사유가 없는 항목이 있으면 종료 코드 1을 반환합니다.
- 검사 도구 작업의 후속 항목을 정리한 임시 문서 `TODO2.md` 추가.
- 압축 알고리즘 문서 `01_fundamentals/cs/compression_algorithms.md` 추가.
- Zircon Windows 빌드 저장소에 `.governance/GOVERNANCE.md` 적용. `.governance/` 체계의 첫 적용 사례입니다.
- Zircon Windows 빌드 저장소에 구성 README와 DevExpress 의존성 문서 작성.
- Ansible 학습·자동화 저장소에 `.governance/GOVERNANCE.md` 와 `.governance/verification.md` 적용.
- `documentation_policy.md` §3.1 경로·식별자 기록 기준 신설. 환경 종속성을 판단 기준으로 정의.

### Changed

- 헤딩 구조 검사를 CI 필수 검사로 등록.
- 스타일 검사 대상에 `02_kiro/` 미러와 저장소 메타 문서(`CHANGELOG.md`, `LICENSE.md`, `TODO.md`, `license_guide.md`)를 포함 (323개 → 367개).
- `md-style-check.py` 의 파일별 제외 항목을 `(검사 집합, 사유, 재검토 시점)` 구조로 변경. 사유 없는 제외를 남기지 않도록 했습니다.
- 검사 제외 항목 전수 점검. 근거가 사라진 2건 제거, 범위가 과도한 1건 축소, 사유 미확인 6건 해소 (11건 → 9건).
- PLAN·ISSUE 템플릿에 비가역 작업, 임시 조치, 재발 방지 섹션 추가.
- 템플릿 8종의 목차·번호 체계와 민감정보 기록 금지 항목을 통일.
- `README.md` 저장소 profile 설명을 `.governance/` 체계 기준으로 갱신.
- 날짜 갱신 workflow의 커밋 생성 job을 단일 branch로 제한.
- 날짜 갱신 workflow에서 `02_kiro/` 미러를 제외. 봇 커밋과 동기화가 서로 덮어쓰던 문제 해결.
- Kiro 미러 allowlist에서 원문 보존본과 미러 전용 파일을 제외.
- `documentation_policy.md`와 `governance_precedence.md`의 역할을 상호 참조로 명확히 함.
- `skip_checks`를 저장소 전체 검사 예외의 실행 설정으로 정의하고, `.governance/`에 사유·범위·재검토 시점을 기록하도록 정리.
- `03_claude/`는 원본·allowlist·검증 절차를 확정하기 전까지 예약 영역으로 유지하도록 활성화 조건을 정의.
- 도구 중립 규칙은 `01_repository_governance/`, 도구 종속 자료는 각 도구 영역에 배치하는 분리 기준을 정의.
- 이관 저장소의 템플릿 사용 실태를 측정하고, 현재 사용 형식과 미사용 문서의 재검토 조건을 기록.
- Zircon Windows 후속 작업을 `12_zircon_win` 저장소의 `TODO.md`로 이관하고 `TODO2.md`에서 관련 블록을 정리.
- Ansible 저장소의 `.governance/` 병행 검증을 완료하고 중앙 `chobo_ansible` profile과 관련 활성 참조를 제거.
- `TODO2.md`의 Ansible profile 정리 항목을 완료하고 임시 TODO 문서를 삭제.
- `TODO.md`에서 완료된 작업과 해소된 검사 예외를 제거하고, 실제 미완료 fact-check와 유효한 검사 예외만 유지.
- `kiro_cli_command_reference.md`의 frontmatter TODO를 종료. 일반 문서에는 `_reference/` 전용 frontmatter 규칙을 적용하지 않음.
- 신규 저장소의 기본 작업 문서 위치를 `.governance/ISSUE.md`, `.governance/TODO.md`, `.governance/PLAN.md`로 정의하고, 기존 루트 문서는 legacy로 허용. 관련 템플릿과 작업 skill 탐색 경로를 갱신.
- `md-style-check.py --list-skips`를 CI에 등록하여 사유 없는 검사 예외를 차단.
- `TODO2.md`에 분산되어 있던 완료 기록을 CHANGELOG의 Added·Changed·Fixed 항목으로 통합하고, TODO2에는 미완료 작업만 남김.
- Ansible 저장소 후속 검증에서 `terraform fmt` 2건, 헤딩 레벨 건너뜀 4건, 목차 앵커 불일치 1건과 목차 누락 1건을 수정.

### Fixed

- `CHANGELOG.md`와 `LICENSE.md`에서 존재하지 않는 `#목차`를 참조하던 복귀 링크 11건 제거.
- `STYLE.md`의 중첩 코드블록 오류 수정. §5~§7, §10, §11 이 코드블록으로 렌더링되던 문제 해결.
- `STYLE.md`의 중복된 `## 14.` 섹션 번호를 14/15/16 으로 재정렬.
- 헤딩 레벨 건너뜀 1건, 중복 앵커 2건 수정.
- `git_concepts.md` 의 목차가 존재하지 않는 섹션을 링크하던 문제 수정 (섹션 번호 재부여).
- 목차 앵커 불일치 7건 수정. em dash·슬래시·`+` 가 앵커에서 제거되며 발생한 불일치.
- `license_guide.md` 표 정렬 26건 수정.
- `md-heading-check.py` 앵커 생성 규칙을 github-slugger 문자 집합으로 교체.
- `md-heading-check.py` 펜스 판정을 CommonMark 규칙으로 교체하고 범위·하위 절 번호 표기 지원.
- `md-heading-check.py` 의 H2 번호 패턴이 이중 이스케이프로 작성되어 `number` 검사가 동작하지 않던 문제 수정.
- `md-heading-check.py` 의 앵커 링크 패턴이 링크 텍스트의 중첩 대괄호를 처리하지 못하던 문제 수정.
- 목차에서 빠져 있던 섹션 5건 추가.
- `git_official_notes.md`, `git_guide.md`, `git_concepts.md`의 사실 오류 12건 수정.
- `privacy_law_guide.md` 개요 표의 소관 기관을 풀네임 병기로 정정.
- 추적되던 구버전 백업 파일 제거 및 `.gitignore` 패턴 보강.
- Kiro 동기화 스크립트가 존재하지 않는 파일을 allowlist에서 요구해 검증 단계에서 중단되던 문제 수정.
- Kiro 미러의 계정·내부 IP·사용자 홈 경로 기록 3건 제거.
- 원본 에이전트 JSON 8개의 파일 끝 개행 누락 수정.

---

## [3.10.0] - 2026-08-20

### Added

- `00_governance/`를 저장소 운영 정책과 AI 도구 미러의 공통 상위 디렉토리로 추가.
- 향후 Claude 자료를 위한 `00_governance/03_claude/` 예약 영역 추가.
- 도구별 동기화를 위한 `manifests/kiro_files.txt` 구조 추가.
- 민감정보와 환경 정보를 제외한 `profiles/chobo_ansible.md` 저장소 profile 추가.
- Kiro 동기화 스크립트와 `.gitignore`에 로컬 전용 `.local/` 제외 규칙 추가.

### Changed

- `00_repository_governance/`를 `00_governance/01_repository_governance/`로 이동.
- `00_kiro/`를 `00_governance/02_kiro/`로 이동.
- README, 검사 설정, 유사 레포 비교 문서의 활성 경로를 새 구조로 갱신.

---

## [3.9.0] - 2026-08-20

### Added

- `00_readme.md/`를 Kiro 실행 자료 미러임을 명시하는 `00_kiro/`로 rename.
- `00_repository_governance/` 추가.
- 문서 운영 정책, Kiro 동기화 정책, `PLAN.md`·`ISSUE.md` 템플릿 추가.
- `sync_files.txt`로 Kiro 공개 동기화 허용 목록 추가.
- 루트 `README.md`에 Kiro 운영 문서와 저장소 운영 정책 링크 추가.

### Changed

- `md-style-check.py`, `.md-style-check.toml`, 유사 레포 비교 문서의 Kiro 디렉토리 경로를 `00_kiro/`로 갱신.
- `CHANGELOG.md`의 마지막 업데이트 날짜를 `2026-08-20`으로 갱신.

---

## [3.8.0] - 2026-08-20

### Added

- `.md-style-check.toml`로 Markdown 검사 제외 디렉토리·파일 설정을 분리.
- GitHub Actions에 `main`·`yunli` push와 Pull Request 대상 Markdown 검증 추가.
- CI에서 `md-link-check.py`, `md-style-check.py`, `readme_inventory_check.py` 실행.

### Fixed

- `md-style-check.py`의 4-backtick·인용구 코드 fence 처리를 fence 길이 기준으로 정정.
- 코드블록 반복 제거 결과를 캐시하고, 중첩 박스 다이어그램을 depth 기준으로 검사.
- 출력 패턴·skip 옵션 매핑을 목록과 사전으로 분리.
- 날짜 자동화 workflow의 staged 상태 검사 순서를 수정하여 실제 commit·push가 실행되도록 보강.

---

## [3.7.0] - 2026-08-20

### Fixed

#### `_reference/web_server_official_notes.md` fact-check

- Nginx `ssl_protocols` TLSv1.3 기본 활성화 시점을 `1.19.0`에서 `1.23.4`로 정정.
- Nginx stream 모듈 도입 시점을 `1.9.5`에서 `1.9.0`으로 정정.
- Nginx `ssl_certificate` 설명을 `ssl` 디렉티브 deprecated 및 `listen ... ssl` 사용 기준으로 정정.
- Apache 2.4.58 `mod_http2` 기능을 TLS 1.3 early data가 아닌 HTTP 103 Early Hints로 정정.
- 공식 출처: [Nginx CHANGES](https://nginx.org/en/CHANGES), [Nginx SSL module](https://nginx.org/en/docs/http/ngx_http_ssl_module.html), [Apache mod_http2](https://httpd.apache.org/docs/2.4/mod/mod_http2.html), [Apache 2.4.58 CHANGES](https://archive.apache.org/dist/httpd/CHANGES_2.4.58).

---

## [3.6.0] - 2026-08-05

### Added

#### VPN 문서 3종 신규 추가

| 파일                                                       | 내용                                                                                           |
|------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `01_fundamentals/networking/softether_vpn_server_guide.md` | SoftEther VPN Server 설치·초기설정·L2TP/IPsec·OpenVPN·방화벽·systemd·명령어·트러블슈팅         |
| `01_fundamentals/networking/vpn_comparison_blog.md`        | VPN 프로토콜 선택 가이드 — 보안·성능·방화벽 통과·시나리오별 선택·플로우차트                    |
| `_reference/softether_official_notes.md`                   | SoftEther 공식 스펙 및 소스코드 기반 참조 노트 (GlobalConst.h, Server.h, softether.org/3-spec) |

#### fact-check 수정

- `01_fundamentals/networking/vpn_comparison_blog.md` — WireGuard 연도 2018 → 2016 (ePrint 2016/914 기준)

### Removed

- `TODO2.md` — T1/T2 작업 완료 확인 후 삭제

---

## [3.5.0] - 2026-08-05

### Changed

#### 파일명 변경 — 개념 문서 _concepts 접미어 통일 (8개)

| 구 파일명                    | 신 파일명                             |
|------------------------------|---------------------------------------|
| `linux/ipc.md`               | `linux/ipc_concepts.md`               |
| `linux/virtual_memory.md`    | `linux/virtual_memory_concepts.md`    |
| `linux/scheduler.md`         | `linux/scheduler_concepts.md`         |
| `linux/namespace.md`         | `linux/namespace_concepts.md`         |
| `linux/cgroup.md`            | `linux/cgroup_concepts.md`            |
| `networking/TCP_state.md`    | `networking/tcp_state_concepts.md`    |
| `networking/vpn_protocol.md` | `networking/vpn_protocol_concepts.md` |
| `cs/cpu_cisc_risc.md`        | `cs/cpu_cisc_risc_concepts.md`        |

- 내부 참조 링크 12개 파일 일괄 수정 (README.md, CHANGELOG.md, TODO2.md, STYLE.md 등)
- `TODO2.md` 작업 전체 완료 (Batch 1~4 ✅ ) → 파일 삭제

### Fixed

#### fact-check 수정 (02_infrastructure)
- `devops_toolchain.md` — Terraform/Ansible/Docker/Compose/K8s/Helm/ArgoCD/Prometheus/Grafana 버전 갱신
- `container_runtime.md` — containerd 1.x 비호환 시점 v1.37 → v1.38
- `zabbix_vs_prometheus.md` — Prometheus v3.13.0 → v3.13.2
- `prometheus_grafana.md` — Prometheus/Alertmanager/Grafana/node-exporter 이미지 버전 갱신
- `airflow.md` — Airflow 3.2.1 → 3.3.0

#### fact-check 수정 (01_fundamentals)
- `softether_vpn_client_guide.md` — v4.43-9799-beta → v4.44-9807-rtm (2026-08 기준)
- `crates_ecosystem.md` — tokio version 1.40 → 1.53
- `TCP_state.md` (→ tcp_state_concepts.md) — tcp_fin_timeout이 FIN_WAIT_2 타이머임을 명확히 수정, tcp_tw_recycle 제거 커널 버전(4.12) 명시

---

## [3.4.0] - 2026-08-02

### Added

#### _reference — 신규 참조 파일 1개
- `csharp_official_notes.md` — .NET 10 LTS/C# 14, LTS/STS/EOL 버전 대응표, 타입 시스템, async/await, 언어 기능 (C# 3~14), dotnet CLI/NuGet/msbuild-props, deprecated (releases-index.json/Language-Version-History.md 기반, fact-check 완료)

#### 01_fundamentals/programming/csharp — 신규 디렉토리 및 문서 5개
- `README.md` — 학습 순서, 빠른 참조, 주요 개념 요약
- `csharp_key_concepts.md` — 타입 시스템, 값/참조 형식, struct vs class, record, nullable, NRT, null 연산자, pattern matching, primary constructor, required, global using, .NET 버전 대응표
- `csharp_oop.md` — 클래스 구성 요소, 접근 제한자, 상속, 인터페이스(default members C# 8+), 추상 클래스, 다형성, 제네릭 제약
- `csharp_async.md` — async/await 기초, 반환 타입(Task/ValueTask/void), 병렬 실행, ConfigureAwait, async 스트림(C# 8+), CancellationToken, 안티패턴
- `csharp_linq.md` — 람다, Func/Action/Predicate, 쿼리/메서드 문법, 연산자(필터/변환/집계/정렬/그룹화/조인), 지연/즉시 실행, ToLookup/Zip
- `csharp_dotnet_cli.md` — dotnet new/build/run/test/publish, .csproj PropertyGroup, NuGet 관리, self-contained/AOT 게시, xUnit/NUnit/MSTest 구조

---

## [3.3.0] - 2026-08-01

### Added

#### _reference — 신규 참조 파일 8개 (Batch 1~4)
- `gdb_official_notes.md` — GDB 17.2, break/run/bt/step/next, -p attach, --batch, 약어 규칙 (gdb.1/GNU FTP)
- `strace_official_notes.md` — strace v7.1, syscall/signal 추적, -e trace 필터, --seccomp-bpf (strace.1/GitHub)
- `ltrace_official_notes.md` — ltrace 0.8.1, 동적 라이브러리 함수 추적, -e/-l/-x 필터, --demangle (ltrace.1/GitLab)
- `valgrind_official_notes.md` — Valgrind 3.27.1, Memcheck(definitely/indirectly/possibly lost), Callgrind/Helgrind/Massif (valgrind.org)
- `perf_official_notes.md` — perf stat/record/report/top/trace/probe 서브커맨드, --list-cmds/-vv (perf.1/kernel wiki)
- `lsof_official_notes.md` — lsof 4.99.7, FD/TYPE 필드, -p/-i/-u/-a/-n/-P/-t 옵션 (lsof.8/GitHub)
- `iotop_official_notes.md` — iotop v1.31, Linux 2.6.20+, --only/--batch/--processes, Total vs Current (iotop.8/GitHub)
- `tcpdump_official_notes.md` — tcpdump 4.99.6, BPF 필터 문법, -w pcap/-r/-n/-nn/-X/-Q (tcpdump.1)
- `bash_shell_official_notes.md` — Bash 5.3, interactive/non-interactive §6.3, PS1/BASH_ENV, 리다이렉션 §3.6 (bash manual)
- `vim_official_notes.md` — Vim 9.2, Normal/Insert/Visual/Command/Replace 모드, 주요 명령어 (vimhelp.org/vim.1)

#### _reference/INDEX.md — 항목 추가
- Batch 1~4 신규 10개 항목 등록

### Fixed

#### 01_fundamentals/linux — `<!-- reference:` 연결 추가
- `gdb.md` → `gdb_official_notes.md`
- `strace.md` → `strace_official_notes.md`
- `ltrace.md` → `ltrace_official_notes.md`
- `valgrind.md` → `valgrind_official_notes.md`
- `perf.md` → `perf_official_notes.md`
- `lsof.md` → `lsof_official_notes.md`
- `iotop.md` → `iotop_official_notes.md`
- `tcpdump.md` → `tcpdump_official_notes.md`
- `shell_interactive_mode.md` → `bash_shell_official_notes.md`
- `vim.md` → `vim_official_notes.md`
- `vim_airline.md` → `vim_official_notes.md`
- `bash_file_redirection.md` — reference 병기 추가 (kernel + bash_shell)
- `bash_math.md` — reference 병기 추가 (kernel + bash_shell)
- `bash_trap_complete_guide.md` — reference 병기 추가 (kernel + bash_shell)
- `vim_airline.md` — H1 12개 → H2로 변환 (문서 구조 정규화)
- `root_password_recovery.md` — 절차 문서 확인 (_reference 불필요)

---

## [3.2.0] - 2026-08-01

### Added

#### _reference — 신규 참조 파일 2개
- `ebpf_bpftrace_official_notes.md` — eBPF 개요, BPF Map 타입(bpf.2 기반), bpftrace 프로브 타입, 활용 도구(Cilium/Falco/Katran), CAP_BPF(Linux 5.8+), libbpf v1.7.0, bpftrace v0.26.1
- `linux_process_official_notes.md` — Process Lifecycle(fork/execve/wait man page 기반), Virtual Memory(mmap.2/MM concepts), OOM killer(oom_score_adj, overcommit_memory), IPC(pipe/shmget/mq_overview), 시스템 프로세스(PID0/1/2)

#### _reference/INDEX.md — 항목 추가
- eBPF / bpftrace — libbpf v1.7.0, bpftrace v0.26.1
- Linux Process / Memory / IPC — fork/exec/wait, mmap, OOM, pipe/shm/mq

### Fixed

#### 01_fundamentals/linux — `<!-- reference:` 연결 15개 추가
- `linux_filesystem.md`, `linux_virtual_fs.md` → `linux_filesystem_official_notes.md`
- `scheduler_concepts.md`, `netfilter_tc.md`, `seccomp_capabilities.md` → `linux_kernel_official_notes.md`
- `bash_file_redirection.md`, `bash_math.md`, `bash_trap_complete_guide.md` → `linux_kernel_official_notes.md`
- `ebpf.md`, `bpftrace.md` → `ebpf_bpftrace_official_notes.md` (기존 kernel_notes에서 교체)
- `process_lifecycle.md`, `linux_system_processes.md` → `linux_process_official_notes.md` (기존 kernel_notes에서 교체)
- `virtual_memory_concepts.md` → `linux_process_official_notes.md` (기존 kernel_notes에서 교체)
- `ipc_concepts.md`, `oom_hang.md` → `linux_kernel_official_notes.md` + `linux_process_official_notes.md` (병기)

#### _reference — fact-check 수정
- `linux_process_official_notes.md` — `overcommit_memory` 출처 `MM concepts` → `proc_sys_vm.5` 교체 (직접 접근 가능한 man page 기반)

---

## [3.1.0] - 2026-07-29

### Added

> 3.0.0 구조 개편(git mv) 이후 mtime 초기화로 인해
> 이번 세션 신규 작성 파일만 기재. 이전(migrated) 파일은 제외.

#### 01_fundamentals/cs — 신규 문서 2개
- `version_control_concepts.md` — VCS 3세대 분류, 중앙집중형 vs 분산형 아키텍처, SVN 저장소/Working Copy 구조, 리비전 모델, 브랜치 전략, 병합 원리, 잠금 모델, 인프라 활용(hooks/백업)
- `git_concepts.md` — Git 객체 모델(blob/tree/commit/tag), DAG 구조, 참조 시스템(HEAD/branch/tag), 작업 영역 3단계, reset 3종류, 브랜치 전략(Trunk-based/GitHub Flow/GitFlow), merge vs rebase, 원격 저장소, 훅 자동화, GitOps + IaC 활용

#### 02_infrastructure/cicd — 신규 문서 1개
- `svn_guide.md` — SVN CLI 실무 가이드 (checkout/update/commit/diff/log/branch/merge/충돌해결/속성/잠금/externals/서버설정/실무팁 전 명령어)

#### _reference — 신규 참조 파일 2개
- `svn_official_notes.md` — Apache Subversion 1.14.5 버전 현황, FSFS 포맷, 프로토콜, 잠금 모델, svn:* 속성, svnadmin 명령어, Git 비교
- `git_official_notes.md` — Git 2.55.0 버전 현황, 4가지 객체 모델, SHA-1/SHA-256, HEAD/branch/tag 참조 구조, merge 전략(ort 2.34+ 기본), reflog, packfile, 주요 설정값

#### _reference/INDEX.md — 항목 추가
- SVN (Subversion) 1.14.5 (LTS)
- Git 2.55.0

### Fixed

#### _reference — 팩트체크 수정
- `rust_official_notes.md` — `last_checked` 2026-07-29 갱신, "fully enabling" 직역 → "전체 활성화" (과장 표현 검사 통과)
- `git_official_notes.md` — merge 기본 전략 `Recursive` → `ort (Git 2.34+)` 수정
- `git_concepts.md` — §7 merge vs rebase 다이어그램에 ort 관련 주석 추가
- `ai_coding_tools_official_notes.md` — "최고" 표현 → "1위" / "속도 1위(Fastest measured)" 수정
- `charset_encoding_official_notes.md` — "ASCII 하위 호환 (U+0000~U+007F는 1바이트, 값 동일)"으로 수정 (RFC 3629 원문 기반, 과장 표현 제거)
- `svn_official_notes.md` — 다이어그램 내부 한글(`개발자`) → 영문(`Dev A/B/C`) 수정

#### _reference — 표 정렬 일괄 수정 (14개 파일)
- `INDEX.md`, `android_adb_official_notes.md`, `chaos_finops_official_notes.md`
- `charset_encoding_official_notes.md`, `e4fsprogs_centos5_notes.md`, `github_references.md`
- `hyperv_centos5_io_contention_notes.md`, `hyperv_version_comparison_notes.md`
- `linux_filesystem_official_notes.md`, `linux_kernel_official_notes.md`
- `platform_engineering_official_notes.md`, `sre_operations_official_notes.md`
- `web_server_official_notes.md`, `ai_coding_tools_official_notes.md`
- md-style-check `_reference/` 37개 파일 0건 통과

### Removed

- `01_fundamentals/programming/rust/temp_factcheck_20260729.md` — 임시 팩트체크 메모 파일 삭제

---

## [3.0.3] - 2026-07-28

### Added

#### 01_fundamentals/programming/rust — 신규 문서 11개
- `01_ownership_borrowing.md`, `02_error_handling.md`, `03_traits_generics.md`
- `04_concurrency.md`, `05_system_programming.md`, `06_networking.md`
- `07_cli_tools.md`, `08_crates_ecosystem.md`, `09_testing.md`
- `10_practical_examples.md`, `rust_roadmap_for_se.md`

### Fixed

#### 표 정렬 일괄 수정 (~90개 파일)
- `01_fundamentals/` (linux, networking, cs, programming/python) — 표 display width 기준 재정렬
- `02_infrastructure/` (cicd, containers, iac, monitoring, web_server)
- `04_security/` (cloud, cve, hardening)
- `05_database/nosql`, `05_database/operations`, `97_misc/`

### Removed

#### 97_misc → 99_archive/05_centos5_legacy 이동 (6개 파일)
- `centos5_aws_migration_assessment.md`, `centos5_ext4_fsck_guide.md`
- `centos5_gamedb_hyperv_host_compatibility.md`, `hyperv_io_contention_legacy_vm.md`
- `hyperv_myisam_io_timeout_incident_20260715.md`, `hyperv_version_centos5_compatibility.md`

---

## [3.0.2] - 2026-07-27

### Changed

- `06_career/ai_tools/ai_coding_tools_comparison.md` — AI 코딩 도구 비교 내용 갱신
- `97_misc/similar_repos.md` — 유사 저장소 목록 갱신

---

## [3.0.0] - 2026-07-07

### Changed

#### 레포 구조 전면 개편 (BREAKING CHANGE)

기존 13개 최상위 디렉토리 → 6개 섹션 기반 구조로 전환.

| 신규 디렉토리        | 내용                                                                    | 통합 출처           |
|----------------------|-------------------------------------------------------------------------|---------------------|
| `01_fundamentals/`   | linux, networking, cs, programming                                      | 02, 03, 05, 08, 11  |
| `02_infrastructure/` | containers, cicd, iac, monitoring, cloud_aws, data_pipeline, web_server | 01, 07, 12, 13      |
| `03_engineering/`    | reliability, delivery, organization, cost                               | 04/02_operations    |
| `04_security/`       | hardening, cloud, cve, web_cwe                                          | 06                  |
| `05_database/`       | rdbms, operations, nosql, forensics                                     | 09, 10              |
| `06_career/`         | roadmap, legal, ai_tools                                                | 04/01, 04/04, 04/05 |

- git mv 200+ 파일 (history 보존)
- README.md 전면 재작성 (6섹션 레벨 기반 탐색)
- 내부 링크 전수 수정 (md-link-check 0건)
- md-style-check.py FILE_SKIP + EXCLUDE_DIRS 경로 갱신
- md-style-check.py 박스 상/하단 공백 혼입 검출 규칙 추가
- .gitignore: `99_archive/` 통합 (기존 51_siasia, 33_<옛 표기>, 99_ETC 제거)
- 기존 디렉토리 README.md 12개 삭제
- `00_readme.md/`, `90_DELETE/` 삭제

### Fixed

- `02_infrastructure/cloud_aws/vpc_peering_inter_region_guide.md` — 다이어그램 좌우 박스 비대칭 수정, fence 홀수 수정, 한글→영문
- `02_infrastructure/cicd/infra_monorepo_and_boilerplate.md` — 중첩 코드블록 4-backtick 전환

### Removed

- `00_readme.md/` — Kiro 설정 복사본 (불필요)
- `90_DELETE/` — deprecated 파일 2개 (CONTRIBUTING, GITHUB_UPLOAD_GUIDE)
- 기존 디렉토리 README.md 12개 (01_install ~ 12_tech_stack)

## [2.3.0] - 2026-07-07

### Added

#### 12_tech_stack — 신규 문서 3개
- `harness_engineering.md` — AI Harness Engineering (에이전트 환경 설계)
- `vpn_protocol_concepts.md` (05_computer_science) — VPN 프로토콜 비교 (PPTP~WireGuard, RFC 대조 검증)
- `zabbix_vs_prometheus.md` — 모니터링 도구 비교 (아키텍처, 수집, 알림, 확장성)

#### _reference — 신규 참조 파일
- `vpn_protocol_official_notes.md` — VPN RFC 기반 참조 노트
- INDEX.md 갱신 (VPN Protocol 항목 추가, 알파벳순 정렬)

#### 03_advanced_linux — 신규 문서 6개
- `ipc_concepts.md` — 프로세스 간 통신 (Pipe, Socket, Shared Memory, Message Queue)
- `linux_virtual_fs.md` — VFS 추상화 계층, inode, dentry, superblock
- `namespace_concepts.md` — Linux Namespace 7종 (pid, net, mnt, uts, ipc, user, cgroup)
- `netfilter_tc.md` — Netfilter 훅 체인, iptables/nftables, TC 트래픽 제어
- `scheduler_concepts.md` — CFS, RT, Deadline 스케줄러, nice, cgroup CPU
- `virtual_memory_concepts.md` — 페이지 테이블, TLB, Swap, OOM Killer, NUMA

#### 04_system_engineer/04_ai — 신규 문서 3개
- `kiro_agent_lock.md` — Kiro 에이전트 동시 실행 방지
- `kiro_model_guide.md` — Kiro 모델 선택 가이드
- `kiro_setup_guide.md` — Kiro CLI 초기 설정

#### 05_computer_science — 신규 문서 1개
- `switch_vlan_mode.md` — Access/Trunk/Hybrid 모드, 802.1Q 태깅

#### 06_security — 신규 문서 11개
- `network_attack_glossary.md` — 네트워크 공격 용어 사전 (DDoS, MITM, ARP Spoofing 등)
- `01_cve/` 서브디렉토리 생성 — CVE 5건 + LPE 공격 시나리오
  - `cve_2026_31431_copy_fail.md`, `cve_2026_43284_dirty_frag.md`
  - `cve_2026_43500_dirty_frag.md`, `cve_2026_43503_dirty_clone.md`
  - `cve_2026_46300_fragnesia.md`, `cve_2026_lpe_attack_scenarios.md`
- `02_web_cwe/` 서브디렉토리 생성 — CWE 4건
  - `cwe_022_path_traversal.md`, `cwe_078_command_injection.md`
  - `cwe_200_info_disclosure.md`, `cwe_434_file_upload.md`

#### 08_debugging_linux — 신규 문서 1개
- `oom_hang.md` — OOM Killer 분석, 행 진단, kdump, sysrq

#### 09_database — 신규 문서 7개
- `dbtrail/` 서브디렉토리 생성 — DB 포렌식/복구
  - `architecture.md`, `forensics.md`, `recovery_guide.md`
- `rdbms_index.md`, `rdbms_server_config.md`, `rdbms_slow_query.md`, `rdbms_tuning.md`

#### 11_python — 신규 문서 2개
- `python_file_io.md` — 파일 읽기/쓰기, encoding, pathlib, atomic write
- `python_generators.md` — yield, send, generator expression, itertools

#### 12_tech_stack — 신규 문서 4개
- `01_data_pipeline/` 서브디렉토리 생성
  - `game_log_pipeline.md`, `log_aggregation_100gb.md`, `log_aggregation_100tb.md`
- `github_cli.md` — gh CLI 명령어, PR/Issue 자동화
- `gstack.md` — 게임 인프라 기술 스택 조합
- `loop_engineering.md` — AI 에이전트 루프 설계

#### 13_iac — 신규 문서 1개
- `01_ansible/molecule.md` — Ansible 역할 테스트 프레임워크

#### _reference — 신규 참조 파일 4개
- `cve_security_official_notes.md` — CVE/CWE 공식 출처 참조
- `linux_kernel_official_notes.md` — 커널 릴리즈/기능 참조
- `networking_official_notes.md` — 네트워크 프로토콜 RFC 참조
- `postgresql_official_notes.md` — PostgreSQL 공식 문서 참조

#### 04_system_engineer/02_operations — 시니어급 문서 8개 (신규)
- `incident_management.md` — 장애 등급 분류, IC 역할, 에스컬레이션, State Document
- `slo_error_budget.md` — SLI/SLO/SLA 정의, Error Budget 운영, Burn Rate Alert, OpenSLO
- `capacity_planning.md` — 트래픽 예측, 리소스 산정, Headroom 설계, Load Testing
- `zero_downtime_migration.md` — Expand-Contract, Dual Write, CDC, Canary 전환, 롤백 전략
- `change_management.md` — Standard/Normal/Emergency 변경 등급, CAB, 배포 윈도우
- `postmortem_framework.md` — 5 Whys, Blameless Culture, Action Items 추적, 리뷰 프로세스
- `chaos_engineering.md` — 가설 기반 실험, 폭발 반경 제어, Game Day, 성숙도 모델
- `multi_region_architecture.md` — Active-Active/Passive, RPO/RTO 설계, Failover/Failback
- `platform_engineering.md` — IDP 설계, Golden Path, CNCF Platform WP 기반 성숙도 모델
- `oncall_design.md` — 로테이션, 25% 규칙, 런북, 에스컬레이션, 번아웃 방지
- `team_topology.md` — 4가지 팀 유형, 3가지 상호작용 모드, Conway 법칙 역전
- `tech_debt_management.md` — Fowler Quadrant, 측정 지표, 상환 우선순위 매트릭스
- `vendor_evaluation.md` — PoC 설계, TCO 3년 산정, Lock-in 평가, Weighted Scoring
- `legacy_modernization.md` — Strangler Fig, 6R 전략, 데이터 이중 쓰기, Shadow Mode

#### 12_tech_stack — 신규 문서 1개
- `cloud_cost_optimization.md` — FinOps 6 Principles, RI/SP 전략, Spot 활용, Right-sizing

#### _reference — platform_engineering_official_notes.md 신규
- CNCF Platforms White Paper + Platform Maturity Model 공식 출처 통합

#### _reference — sre_operations_official_notes.md 신규
- Google SRE Book/Workbook, PagerDuty, OpenSLO, ITIL v4, gh-ost, pt-osc 공식 출처 통합

#### .kiro/prompts — fact-check.md 신규
- 기술 사실 검증 전용 프롬프트 (RFC 대조, 할루시네이션 탐지, 비검증 수치 제거)
- md-review.md에서 사실 검증 역할 분리

#### 04_system_engineer/02_operations — 신규 문서 2개
- `s3_object_lock.md` — S3 Object Lock (WORM, Governance/Compliance, 운영)
- `s3_backup_tips.md` — EC2→S3 백업 운영 팁 (비용, 성능, 무결성, DB 백업)

#### 99_ETC/01_AWS_jobs — 신규 문서 1개
- `s3_cross_account_backup.md` — STS AssumeRole Cross-account 백업 (웹+CLI)

#### 01_install — 업데이트
- `postgresql_install.md` — PG18 추가, ICU provider 상세 설명, 최신 마이너 버전 반영

### Changed

#### 12_tech_stack
- `aws_network_firewall.md` — Resource ID placeholder 표준화 (보안 검사 통과)

#### 12_tech_stack
- `harness.md` → `harness_inc.md` 이름 변경 (CI/CD 플랫폼 명시)

#### md-style-check.py
- `_reference` 디렉토리 검사 제외 추가
- `kiro_cli_command_reference.md` FILE_SKIP diagram-kr 예외 추가

#### .kiro/prompts/md-review.md
- `content(tech error)` 제거 → `content(typo,example mismatch,duplication,broken sentence)`
- `@fact-check` 분리 안내 주석 추가
- diagram 항목에 `arrow flow direction logical` 추가

#### 스크립트
- `md-style-check.py` — `_reference` 제외, FILE_SKIP diagram-kr 추가, `--no-*` 옵션 11개
- `md-link-check.py` — 코드블록 파싱 수정 (라인 토글 방식)
- `strip-footer-md.py` — 신규 유틸리티 (푸터 일괄 제거 스크립트)

#### .kiro/skills/work-rules/SKILL.md
- §15 Storage targets에 추론/기억 기반 작성 금지 규칙 상단 배치

### Fixed

#### 다이어그램 한글→영문 (8개 파일 완료)
- `asn_and_cloudflare_ddos.md`, `infra_monorepo_and_boilerplate.md`
- `s3_gateway_endpoint_cross_account.md`, `vpc_peering_inter_region_guide.md`
- `devops_toolchain.md`, `sre_roadmap.md`
- `ai_development_request_template.md`, `ai_markdown_design_patterns.md`

#### 다이어그램 화살표 수정
- `ai_development_request_template.md` — `------->` → `──────>` (Box Drawing 문자)
- `vpn_protocol_concepts.md` — 다이어그램 `│`/`v` 위치, 박스 `┐`/`┘` 닫힘, Transport/Tunnel Mode 박스 수정

#### vpn_protocol_concepts.md 사실 검증 수정
- 세대 타임라인: OpenVPN 2012→2001, IKEv2 순서 교체
- IPsec AES-GCM-16: SHOULD+ → MUST (RFC 8221)
- OpenVPN TLS: "1.3 기본" → "1.2/1.3 (최상위 지원 버전 자동 선택)"
- L2TP/IPsec 오버헤드: "~20% 증가" → 출처 없는 수치 제거

---

## [2.2.1] - 2026-06-21

### Fixed

#### 01_install — 표 정렬 수정 (5개 파일)
- `nginx_install.md`, `apache_install.md`, `docker_install_and_compose.md`, `ansible_install_and_team_operation.md`, `elasticsearch_install.md`
- 표 내부 파이프(`|`) 미이스케이프로 인한 열 깨짐 수정 (`\|` 이스케이프 적용)
- 불필요한 빈 열 제거 및 display width 기준 패딩 재정렬

#### 02_basic_linux — 표 정렬 + 다이어그램 수정 (4개 파일)
- `bash_file_redirection.md` — 표 패딩 수정, 다이어그램 행 폭 통일, 다이어그램 내부 한글→영문
- `bash_math.md` — 표 열 너비 재정렬 (`\|\|` 이스케이프 포함)
- `root_password_recovery.md` — 표 열 너비 재정렬
- `shell_interactive_mode.md` — 표 전체 자동 정렬

#### 04_system_engineer — 표 정렬 + 구조 수정 (22개 파일)
- 전체 표 display width 기준 자동 정렬
- `kiro_cli_command_reference.md` — 파이프 이스케이프 (`--wrap <always \| never>`)
- `game_infra_kpi_presentation.md` — H1 중복 수정 (`# ubuntu-24.04` → `## ubuntu-24.04`)
- `infra_monorepo_and_boilerplate.md` — 코드블록 시작 태그 누락 수정
- `ai_markdown_design_patterns.md` — 이모지 뒤 공백 추가
- `vpc_peering_inter_region_guide.md` — 반말체→합니다체 수정 (2건)
- 다이어그램 행 폭 패딩 통일

#### 05_computer_science — 표 정렬 + 다이어그램 수정 (19개 파일)
- 전체 표 display width 기준 자동 정렬
- `equivalence_partitioning.md` — 코드블록 닫힘 누락 수정
- `ipv4_addressing_guide.md`, `array.md`, `linked_list.md`, `queue.md`, `integration_testing.md` — 다이어그램 내부 한글→영문
- 다이어그램 행 폭 패딩 통일

---

## [2.2.0] - 2026-05-04

### Added

#### 01_install — 신규 설치 가이드 13개
- `mysql_install.md` — Ubuntu/RHEL 설치, 초기 보안 설정, my.cnf, 복제 계정, 기본 사용법
- `postgresql_install.md` — Ubuntu/RHEL 설치, pg_hba.conf, LOCALE 'C.UTF-8' 이슈 대응, 기본 사용법
- `docker_install_and_compose.md` — Ubuntu/RHEL 설치, daemon.json, Compose 운영, 실무 팁 7가지
- `kubernetes_install.md` — k3s(단일 명령), kubeadm(멀티 노드), kubectl, Deployment/Service YAML
- `nginx_install.md` — 설치, 가상 호스트, 리버스 프록시, upstream LB, SSL/Let's Encrypt
- `apache_install.md` — 설치, MPM(prefork/worker/event) 상세 비교 및 튜닝, SSL
- `redis_install.md` — 설치, requirepass, 위험 명령 비활성화, 자료형 CRUD, Slow Log
- `prometheus_grafana_install.md` — 바이너리/APT 설치, Node Exporter, PromQL, 알림 규칙, Compose
- `elasticsearch_install.md` — ELK 구조, 8.x 보안 설정, ILM, Compose
- `haproxy_install.md` — L4/L7 LB, upstream 알고리즘, SSL 터미네이션, 소켓 런타임 제어
- `vault_install.md` — KV/Database 시크릿 엔진, AppRole, Auto Unseal(AWS KMS), 감사 로그
- `mongodb_install.md` — 8.0 설치, 인증 활성화, CRUD, 인덱스, 프로파일링, 백업
- `jenkins_install.md` — JDK 21, Declarative Pipeline, Shared Library, Compose

#### 09_database — rdbms_replication.md 개선
- MySQL 복제 전체 설정 절차 추가 (Primary 계정 생성, mysqldump 초기 동기화, binlog position 기반 설정)
- 반동기 복제 섹션 추가 (플러그인 설치, ACK 흐름, 상태 확인)
- Failover 섹션 추가 (전통/GTID 수동 Failover, MHA·Orchestrator 자동화 도구 비교)
- 복제 필터링 섹션 추가 (binlog_do_db, replicate_do_table 등)
- PostgreSQL Streaming Replication 전체 설정 추가 (pg_basebackup, pg_stat_replication, 동기 복제, Failover)
- MySQL RDS vs Aurora 비교표 추가

### Changed

- `01_install/README.md` 신규 생성 — 14개 문서 목차
- `09_database/README.md` 목차에 설치 문서 링크 추가 (mysql_install, postgresql_install)
- `README.md` `01_install` 섹션 표에 신규 13개 파일 추가, 문서 트리 업데이트, 마지막 업데이트 갱신
- `README.md` 문서 트리 링크 텍스트 오류 6건 수정 (하이픈 → 언더스코어)
- `~/.kiro/markdown/STYLE.md` 규칙 10 보강 — 반말체 종결어미 금지 패턴 명시 (`~이다.` `~한다.` 등)

### Fixed

- `mysql_install.md` `mysqldump` 명령에 `sudo` 누락 수정 (Ubuntu auth_socket 환경)
- `postgresql_install.md` DB 생성 구문 수정 (`LC_COLLATE 'en_US.UTF-8'` → `LOCALE 'C.UTF-8'`, PostgreSQL 17 + Ubuntu 24.04 ICU 환경)
- `postgresql_install.md` 계정명 대소문자 수정 (`Secureuser123` → `secureuser123`, PostgreSQL 소문자 저장 규칙)
- 전체 `.md` 반말체 종결어미 수정 — `01_install` 8개 파일 19건, `09_database` 8개 파일 30건, 기타 12개 파일 33건 (총 82건)
  - `~이다.` `~한다.` `~된다.` `~있다.` `~없다.` `~않는다.` `~아니다.` → 합니다체 통일

---

## [2.1.0] - 2026-05-01

### Added

- `12_tech_stack/README.md` 신규 생성 — 6개 문서 링크 표, 참고 자료, 푸터
- `10_nosql/README.md` 문서 목록 섹션 추가 (Redis, MongoDB, Elasticsearch 링크 표)
- `11_python/README.md` 목차 섹션 추가
- `06_security/README.md` 목차 섹션 추가
- `02_basic_linux/README.md` 목차 섹션 추가, `shell_interactive_mode.md` 문서 목록 추가
- `09_database/rdbms_partition.md` PostgreSQL Hash 파티셔닝 예제 추가

### Changed

- `07_opensource/` 파일명 앞 숫자 접두사 제거 (`01_docker_...` → `docker_...` 등 4개)
- `08_debugging_linux/` 내부 공유 자료 헤더 제거 (strace, ltrace), 문서 변경 이력/관리자 섹션 제거
- `04_system_engineer/01_roadmap/sre_roadmap.md` 내부 공유 자료 헤더, 실명, 작성자 노트 제거
- 전체 참고 자료 별점 STYLE.md 기준 재적용
  - 공식 문서: ★★★☆☆, 서드파티/블로그: ★★☆☆☆, seminal 도서/PEP: ★★★★☆
  - Use The Index Luke: ★★☆☆☆ (서드파티)
- `09_database/` 다이어그램 내 한글 영문화 (4개 파일)
- `07_opensource/container_architecture.md` 다이어그램 내 한글 영문화, 중복 참고 자료 제거
- `06_security/01_ddos_defense_architecture.md` 다이어그램 내 한글 영문화, 참고 자료 형식 수정
- `02_basic_linux/` 다이어그램 내 한글 영문화 (redirection, vim, shell_interactive_mode)
- `10_nosql/nosql_elasticsearch.md` REST API 코드블록 `bash` 태그 제거, JSON 내 `#` 주석 → `//`
- `n8n_docker_cheatsheet.md` 자격증명 실제값 → 표준 플레이스홀더 적용
- `12_tech_stack/git_guide.md` bare URL → 마크다운 형식 + 별점 추가
- `README.md` `07_opensource` 링크 파일명 수정 (접두사 제거 반영), 마지막 업데이트 갱신

### Fixed

- `09_database/rdbms_lock.md` `information_schema.innodb_lock_waits` MySQL 8.0 제거 반영 (8.0+ 쿼리 우선)
- `09_database/rdbms_join.md` INNER JOIN 다이어그램 값 오류 수정 (`│2│3│` → `│1│3│`)
- `09_database/rdbms_replication.md` RDS MySQL Read Replica 최대 수 수정 (5개 → 15개)
- `09_database/rdbms_partition.md` 이벤트 스케줄러 파티션 이름 충돌 수정 (동적 이름 생성으로 변경)
- `09_database/rdbms_procedure.md` `SQL_CALC_FOUND_ROWS` deprecated 주석 추가
- `09_database/rdbms_transaction.md` `FOR UPDATE` 설명 정정 (일반 SELECT는 MVCC로 허용)
- `08_debugging_linux/strace.md` `strace -b` 오류 수정 (strace에 없는 옵션)
- `02_basic_linux/README.md` 리소스 모니터링 링크 경로 수정 (`04_system_engineer/02_operations/` 누락)
- 전체 README.md 링크 유효성 검증 완료 (12개 파일 전체 OK)

---

## [2.0.0] - 2026-04-30

### Added

- `09_database/` 신규 디렉토리 — RDBMS 11개 문서
  (normalization, join, index, explain, transaction, lock, view, procedure, replication, partition, schema_migration)
- `10_nosql/` 신규 디렉토리 — MongoDB, Redis, Elasticsearch
- `04_system_engineer/01_roadmap/` 서브디렉토리 분리 (SE/SRE/DBA 로드맵)
- `04_system_engineer/02_operations/` ~ `05_legal/` 서브디렉토리 분리
- `license_guide.md` 전면 재작성 (라이선스 역사, 이슈, 법적 근거 추가)
- `12_tech_stack/git_guide.md` 신규 — diff/log/fetch/stash/rebase/safe.directory
- `04_system_engineer/05_legal/drm_guide.md` 신규
- `04_system_engineer/05_legal/ip_ownership_guide.md` 신규
- `04_system_engineer/01_roadmap/dba_roadmap.md` 신규
- 루트 README.md 문서 트리 섹션 추가

### Changed

- 전체 .md 푸터 통일 — stars/forks/watchers 배지, 작성일/마지막업데이트 빈줄 규칙
- 전체 참고 자료 별점 추가 (★★☆☆☆ 기본값 기준)
- 전체 목차 표 형식 통일 — H2만 포함, H3 혼입 제거
- `[⬆ 목차로 돌아가기]` 전체 파일 추가
- `05_computer_science/` 참고 자료 목록 형태 변환 (표 → 목록)
- `se_complete_roadmap_programming_languages.md` 제목 수정 ("완전" 제거)

### Fixed

- `packet_analysis.md` 중복 H2 섹션 제거
- `license_guide.md` `## License` H2 20개+ 중복 제거 (코드블록으로 이동)
- 전체 과장 표현 수정 ("최고 성능" → "높은 성능" 등)

---

## [1.1.0] - 2026-03-25

### Added

- `01_install/` 디렉토리 README.md 목차에 추가 (Ansible 기초, 설치 및 팀 운영 가이드)
- GitHub Actions workflow 추가 (`.github/workflows/update-date.yml`)
  - `main` 브랜치 push 시 변경된 README.md의 마지막 업데이트 날짜 자동 갱신

### Changed

- `07_system_engineer/` → `04_system_engineer/`로 번호 변경 (자주 사용하는 디렉토리 우선 배치)
- `04_opensource/` → `07_opensource/`로 번호 변경 (swap)
- `08_debuggin_linux/` → `08_debugging_linux/`로 오타 수정
- README.md 목차 순서를 디렉토리 번호 순으로 재정렬 (1~10번)
- 모든 하위 디렉토리 README.md 푸터 통일 (통계 배지, 마지막 업데이트, 저작권)

### Fixed

- 문서 내 `debuggin_linux` → `debugging_linux` 오타 수정 (6개 파일)
- 문서 내 `07_system_enginner` → `04_system_engineer` 오타 및 경로 수정 (6개 파일)
- 문서 내 `01_debuggin_linux` → `08_debugging_linux` 잘못된 번호 참조 수정

---

## [1.0.0] - 2026-03-11

### Added

- 초기 릴리스
- Linux 디버깅 도구 가이드 (strace, ltrace, gdb, perf, valgrind, lsof, iotop, tcpdump)
- 기본 Linux 명령어 및 스크립팅 가이드
- Bash trap 가이드
- IP 주소 체계 가이드
- 고급 Linux (bpftrace)
- 오픈소스 도구 (Docker, n8n, 컨테이너 아키텍처)
- 컴퓨터 과학 (TCP, 패킷 분석, 네트워크 헤더, HTTP)
- 보안 (DDoS 방어)
- 시스템 엔지니어 로드맵
- 프로그래밍 언어 비교 (C, C++, C#, Go, Python, Bash)
- Python 가이드 (클래스, 로깅, Magic Attributes)
- 라이선스 가이드
- 각 디렉토리별 README.md
- LICENSE.md
- CC BY 4.0 라이선스 적용 (문서)
- MIT License 적용 (코드 예제)

---

## 변경 사항 기록 방법

### 카테고리

- `Added` - 새로운 기능 추가
- `Changed` - 기존 기능 변경
- `Deprecated` - 곧 제거될 기능
- `Removed` - 제거된 기능
- `Fixed` - 버그 수정
- `Security` - 보안 관련 변경

위 6종 외의 카테고리는 사용하지 않습니다.

### 버전 번호

| 자리  | 올리는 기준                                 | 예                  |
|-------|---------------------------------------------|---------------------|
| major | 저장소 구조 개편, 최상위 디렉토리 체계 변경 | `2.0.0`, `3.0.0`    |
| minor | 문서 추가, 검사 도구 기능 추가, 정책 도입   | `3.10.0` → `3.11.0` |
| patch | 오류 수정과 서식 정정만 포함                | `3.0.2`, `3.0.3`    |

문서 저장소이므로 Semantic Versioning 의 하위 호환 개념은 그대로 적용되지 않습니다. 위 기준으로 해석합니다.

- 릴리스는 날짜 단위가 아니라 작업 단위입니다. 같은 날 여러 버전이 올라갈 수 있습니다.
- 항목은 최신 버전이 위로 오도록 내림차순으로 배치합니다.
- 한 릴리스 안에서 중간 상태는 기록하지 않습니다. 최종 결과만 남깁니다.

🟡 `3.0.1` 은 존재하지 않습니다. 번호를 건너뛴 것으로, 누락된 변경 내역은 없습니다.

## 참고 자료

- Keep a Changelog: [keepachangelog.com](https://keepachangelog.com/) — ★★☆☆☆
- Semantic Versioning: [semver.org](https://semver.org/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-11

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
