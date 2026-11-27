---
name: docker-swarm-official-notes
description: Docker Engine v29.10.1 Swarm 모드의 포트, Raft 장애 허용, secret 저장, 업데이트 기본값과 dind 3노드 시험 결과 정리.
tags:
  - docker
  - swarm
  - orchestration
last_checked: 2026-11-27
sources:
  - https://github.com/moby/moby/releases
  - https://docs.docker.com/engine/swarm/
  - https://docs.docker.com/engine/swarm/admin_guide/
  - https://docs.docker.com/engine/swarm/secrets/
  - https://github.com/docker/cli/blob/master/docs/reference/commandline/service_create.md
---

# Docker Swarm 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- Docker Engine 최신 v29.10.1(moby 태그 `docker-v29.10.1`, 2026-11-24), 이전 v29.10.0(11-16). `docker:29-dind` 이미지의 서버 판 29.10.1.
- Swarm 모드는 Engine에 포함(별도 설치 없음).

## 2. 공식 문서 (docker/docs 저장소 원본)

- 포트: "Port `2377` TCP for communication with and between manager nodes", "Port `7946` TCP/UDP for overlay network node discovery", "Port `4789` UDP (configurable) for overlay network traffic".
- Raft: N개 manager는 "(N-1)/2" 영구 장애까지 견딤. 과반을 잃으면 `docker swarm init --force-new-cluster`로 복구(남은 manager 하나로 새 클러스터).
- secret 문서: 전송과 저장 모두 암호화("encrypted during transit and at rest"), 값은 암호화된 Raft 로그에 저장, 컨테이너 안 경로는 `/run/secrets/<secret_name>`.
- 참가 토큰: "If you subsequently rotate the token, it doesn't affect existing swarm nodes."
- `docker service create` 기본값: `--update-failure-action` pause, `--update-order` stop-first, `--rollback-failure-action` pause, `--rollback-order` stop-first. 기본 병렬 1개.

## 3. dind 시험 (2026-11-27, docker:29-dind 3개)

- manager 1 + worker 2: init·join, `node ls`에 Leader 1. manager에서 TCP 2377·7946 listen.
- `--publish 8080:80` 3 replica: worker IP:8080에서 nginx 응답(routing mesh). scale 5/5.
- update parallelism 2·delay 2s 성공. 없는 이미지 + `--update-failure-action rollback`: `rollback_completed`, 직전 이미지 복귀. 직후 `service rollback`: `service ... does not have a previous spec`.
- drain w1 → task가 m1·w2로 이동. active로 되돌려도 재분배 없음, `service update --force` 뒤 노드마다 1개.
- secret: `/run/secrets/db_pw`가 ro tmpfs, `secret inspect`에 값 없음, 사용 중 삭제 거부(`is in use by the following service`). config는 지정 경로 파일.
- stack: overlay 네트워크에서 서비스 이름 DNS 동작, `build:`만 있으면 `invalid image reference for service b: no image specified`.
- worker에서 `service ls`: `This node is not a swarm manager`.
- manager 1개 정지: worker 컨테이너 유지, `control=false`. 재시작 약 20초 뒤 모두 Ready.
- manager 3개: 리더 정지 시 다른 manager가 Leader, 서비스 3/3. 2개 정지 뒤 약 45초 시점 조회·scale 모두 `The swarm does not have a leader ...`(15초 시점에는 조회 성공). 떠 있던 컨테이너 유지.
- autolock 켜면 `SWMKEY-1-...` 키 출력.
- 미실행: 실제 서버, 방화벽, 인증서 교체, 백업·복구, `--force-new-cluster`.
