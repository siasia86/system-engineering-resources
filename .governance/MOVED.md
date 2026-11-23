# 옮김 기록

Git에서 추적하던 문서를 다른 경로로 옮긴 기록입니다. 옛 경로는 대상이 없을 수 있어 코드로 표기하고, 현행 경로는 이 파일 자리에서 본 상대 링크로 적습니다. 행은 정리 조건이 차도 지우지 않고 "정리됨 — 날짜·승인"으로 닫습니다.

| 옛 경로                                                      | 현행 경로                                                                                         | 옮긴 commit            | 외부 참조 확인                                                                                                                                                                               | 정리 조건                                                                                                                    |
|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `PLAN.md`                                                    | [PLAN.md](PLAN.md)                                                                                | 32 `63a7b22`           | 32 소유 담당 · 아래 1절 범위·검색어 · 32 `439be13` · 2026-11-14 · main 기준 branch 주소 0건, commit 고정 주소 3건(영향 없음), 다른 branch 주소 1건(1절)                                      | 정리됨 — 2026-11-17·사용자 직접 결정(관찰 유예 끝 전에 앞당김), [삭제 기록](REMOVED.md)                                      |
| `TODO.md`                                                    | [TODO.md](TODO.md)                                                                                | 32 `63a7b22`           | 32 소유 담당 · 아래 1절 범위·검색어 · 32 `439be13` · 2026-11-14 · main 기준 branch 주소 0건, commit 고정 주소 1건(영향 없음)                                                                 | 정리됨 — 2026-11-17·사용자 직접 결정(관찰 유예 끝 전에 앞당김), [삭제 기록](REMOVED.md)                                      |
| `CHANGELOG.md`                                               | [CHANGELOG.md](CHANGELOG.md)                                                                      | 32 `63a7b22`           | 32 소유 담당 · 아래 1절 범위·검색어 · 32 `439be13` · 2026-11-14 · branch 주소 0건, commit 고정 주소 0건                                                                                      | 정리됨 — 2026-11-17·사용자 직접 결정(관찰 유예 끝 전에 앞당김), [삭제 기록](REMOVED.md)                                      |
| `02_infrastructure/cloud_aws/backup_tools_comparison.md`     | [cloud_backup_cost_comparison.md](../02_infrastructure/cloud_aws/cloud_backup_cost_comparison.md) | 32 `3de9397`           | 32 소유 담당 · 아래 1절 둘째 범위 · 32 `8ba9371` · 2026-11-16 · 이 저장소 안 링크 1건(루트 README, 같은 commit에서 고침), 다른 저장소 0건                                                    | 외부 참조 0건이라 옛 자리 안내 없음. 관찰 유예 2026-11-16~2026-12-16. 유예 중 참조가 나오면 고치거나 안내를 둠               |
| `01_fundamentals/networking/tcpdump_examples.md`             | [packet_analysis.md](../01_fundamentals/networking/packet_analysis.md)(통합)                      | 32 `4211bf5`           | 32 소유 담당 · 2026-11-17 · 이 저장소 안 링크 3건과 루트 README 1행(같은 commit에서 고침) · 05 검토가 02·03·05·30·31·33·35·41 원격 main을 검색해 05 기록 문서 1곳뿐 · 04·42·DOCS-PRIV 미확인 | 통합으로 파일 삭제(05 D132 M4), 옛 자리 안내 없음. 관찰 유예 2026-11-17~2026-12-17. 유예 중 참조가 나오면 고치거나 안내를 둠 |
| `02_infrastructure/containers/docker_install_and_compose.md` | [docker_install.md](../02_infrastructure/containers/docker_install.md)                            | 32 이 행과 같은 commit | 32 소유 담당 · 아래 1절 셋째 범위 · 2026-11-23 · 이 저장소 안 링크 5건(README·Docker Compose·Docker 네트워크·Podman·CHANGELOG, 같은 commit에서 고침), 다른 저장소의 깨지는 링크 0건          | 외부 참조 0건이라 옛 자리 안내 없음. 관찰 유예 2026-11-23~2026-12-23. 유예 중 참조가 나오면 고치거나 안내를 둠               |
| `02_infrastructure/containers/docker_compose_cheatsheet.md`  | [docker_cheatsheet.md](../02_infrastructure/containers/docker_cheatsheet.md)                      | 32 이 행과 같은 commit | 32 소유 담당 · 아래 1절 셋째 범위 · 2026-11-23 · 이 저장소 안 링크 5건(README·Docker Compose·Docker 네트워크·Podman·CHANGELOG, 같은 commit에서 고침), 다른 저장소의 깨지는 링크 0건          | 외부 참조 0건이라 옛 자리 안내 없음. 관찰 유예 2026-11-23~2026-12-23. 유예 중 참조가 나오면 고치거나 안내를 둠               |

## 1. 외부 참조 확인 범위

- 범위: 이 저장소 원격 main(`439be13`)과, 이 저장소 소유자의 다른 저장소 13개(공개·비공개)를 2026-11-14에 가져온 원격 branch 전부입니다. branch마다 따로 검색했습니다.
- 저장소 이름 접두가 있는 검색어: `system-engineering-resources/(blob|tree|raw|edit)/<branch>/(PLAN|TODO|CHANGELOG).md`, `system-engineering-resources/<branch>/(PLAN|TODO|CHANGELOG).md`(raw 주소), `32_system-engineering-resources/(PLAN|TODO|CHANGELOG).md`(로컬 경로).
- 접두가 없는 검색어: 이 저장소 안 `.governance` 밖과 안에서 `](PLAN.md)`·`](../TODO.md)` 같은 상대 링크, 그리고 workflow·설정·스크립트(`.github`, `*.toml`, `*.yml`, `*.json`, `*.py`, `*.sh`)의 파일 이름입니다.
- 결과: 이 저장소 안 상대 링크와 도구 입력은 0건입니다. 다른 저장소의 commit 고정 주소 4건은 고정된 commit을 가리켜 영향이 없습니다. 다른 저장소의 `yunli` branch에 이 저장소 `yunli` branch의 `PLAN.md`를 가리키는 주소가 1건 있습니다. 이 저장소의 `yunli` branch는 이미 지워졌고, main의 옛 경로와는 관계가 없습니다.
- 둘째 범위(`backup_tools_comparison.md`): 이 저장소 원격 main(`8ba9371`)과 같은 13개 저장소의 원격 branch 전부를 2026-11-16에 검색했습니다. 검색어는 접두 있는 `cloud_aws/backup_tools_comparison`(주소·로컬 경로 모두 포함)과 접두 없는 `backup_tools_comparison`입니다. 접두 없는 결과 가운데 `02_infrastructure/storage/` 문서 2개의 `./backup_tools_comparison.md`는 같은 이름의 다른 문서를 가리켜 해당이 없습니다.
- 셋째 범위(`docker_install_and_compose.md`·`docker_compose_cheatsheet.md`, 2026-11-23): 이 PC에 clone된 다른 저장소 17개의 로컬·원격 branch 전부를 `git fetch --all` 뒤 검색했습니다. 검색어는 접두 없는 `docker_install_and_compose`·`docker_compose_cheatsheet`입니다. 두 곳이 나왔으나 링크가 아닙니다. 한 곳은 다른 저장소 조사 기록 안의 코드 표기(과거 상태 설명)이고, 다른 한 곳은 이름이 비슷한 다른 파일(`01_docker_docker_compose_cheatsheet.md`)이 부분 문자열로 걸린 것입니다. 이 저장소 workflow·설정·스크립트의 참조는 0건입니다.
- 미확인: 이 저장소는 공개 저장소입니다. 검색 범위 밖(다른 사람의 저장소·북마크, Git 제외 자료, 도구 메모리·설정)에서 들어오는 참조는 확인하지 않았습니다. "0건"은 위 범위 안의 결과입니다.

## 2. 정리 조건

- 관찰 유예 30일: 옮긴 날(2026-10-27, 루트 안내 `ab553ad`도 같은 날)부터 세며 2026-11-26에 끝납니다. 유예 중 참조가 나오면 그 참조를 고치거나 옛 자리 안내를 유지합니다.
- 정리 후보 30일: 이 저장소가 구조 변경 완료 표에서 끝난 날부터 따로 셉니다. 2026-11-14 현재 시작하지 않았습니다.
- 두 기간은 목적과 기산점이 달라 합치지 않습니다. 어느 쪽이든 지나는 것만으로 지우지 않습니다.
- 루트 `PLAN.md`·`TODO.md`·`CHANGELOG.md` 연결 안내는 이 기록과 함께 남아 있습니다. 행 닫기와 루트 안내 삭제는 외부 참조 결과와 두 기간을 본 뒤 정리 묶음에서 사용자 묶음 승인으로 합니다. 지우면 이 행을 닫고 [삭제 기록](REMOVED.md)에 행을 더해 서로 가리키게 합니다. 2026-11-17 사용자 직접 결정으로 관찰 유예 끝(11-26) 전에 세 안내를 지우고 행을 닫았습니다. 저장소 안 참조는 0건이었고 외부 참조는 1절 결과(commit 고정 주소 4건, 지워진 branch 주소 1건)에서 바뀐 것을 다시 찾지 않았습니다.

---

**작성일**: 2026-11-14

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
