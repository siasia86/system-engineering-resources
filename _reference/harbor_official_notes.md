---
name: harbor-official-notes
description: Harbor 2.15.5 태그 불변 규칙, 보존 규칙, 복제, Cosign·Notation 서명, garbage collection 정리.
tags:
  - harbor
  - registry
  - container
last_checked: 2026-11-27
sources:
  - https://github.com/goharbor/harbor/releases
  - https://goharbor.io/docs/main/working-with-projects/working-with-images/create-tag-immutability-rules/
  - https://goharbor.io/docs/main/working-with-projects/working-with-images/create-tag-retention-rules/
  - https://goharbor.io/docs/main/administration/configuring-replication/
  - https://goharbor.io/docs/main/working-with-projects/working-with-images/sign-images/
  - https://goharbor.io/docs/main/administration/garbage-collection/
---

# Harbor 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- GitHub 최신 릴리스 v2.15.5(2026-11-12). 문서 `main` 판은 2.16.0을 최신으로 표시.

## 2. 기능

- 태그 불변: 저장소·태그 각각 matching/excluding, 규칙은 OR, 프로젝트당 15개. 불변 태그는 삭제·다시 올리기·태그 변경·복제로 바꿀 수 없음.
- 보존 규칙: 최근 올린 N개, 최근 받은 N개, N일 안에 올린 것, N일 안에 받은 것, 항상 보존. 태그 필터, 태그 없는 artifact 선택, cron 일정, Dry Run·Run Now. 실행 뒤 되돌릴 수 없음. 태그가 여러 개인 artifact는 하나라도 보존 대상이면 모두 보존.
- 복제: Harbor와 다른 레지스트리 사이 push·pull 방식. 세부 필터는 미확인.
- 서명: v2.5부터 Cosign, Notation 지원. 서명은 accessory로 표시. `cosign clean` 미지원. 서명 복제는 Manual·Scheduled 실행만.
- GC: 삭제해도 공간이 바로 비지 않음. 태그 없는 artifact 함께 삭제 옵션, Dry Run, 일정. 최근 2시간 안에 올린 레이어는 남김. 서명된 artifact가 GC로 지워지면 서명도 함께 지워짐.

## 3. 시험

- 실행하지 않음. 공식 문서만 대조.
