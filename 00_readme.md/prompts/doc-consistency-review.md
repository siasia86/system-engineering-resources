Cross-file consistency review for project @${1:directory}
# ${1} 생략 시: 현재 작업 중인 프로젝트 루트 디렉토리를 대상으로 삼을 것.
# 최근 작업 디렉토리가 불명확하면 "어떤 프로젝트를 검증할까요?" 라고 물어볼 것.

Verify cross-file consistency across README.md, PLAN.md, CHANGELOG.md, and source code.

Check items:
1. version-consistency: code `VERSION = "..."` vs CHANGELOG vs docs
2. path-existence: file paths in docs (outside code blocks / quote blocks) exist on filesystem
   - resolve relative paths from project root
3. date-freshness: footer `마지막 업데이트` date vs actual file mtime (warn if mtime > footer date)
4. cross-doc-duplication: same info in multiple docs must not contradict
5. status-table-accuracy: status tables (✅/⬜) vs actual artifacts on filesystem
6. link-validity: internal doc links (#anchor, relative paths) resolve correctly

Edge case handling:
- PLAN.md / CHANGELOG.md 없으면 해당 체크 skip
- VERSION 상수 없는 파일 skip
- 코드블록(```) / 인용구(>) 내부 경로·값은 검증 제외

Method:
- Read all .md files + source code in target directory
- For path-existence: `test -f` or `ls` from project root
- For date-freshness: `stat -c %Y` vs parsed footer date

Output: Korean, ✅❌🟡 per item, show specific mismatches with file:line

Loop (max 3 iterations):
1. Review → list all ❌/🟡 issues
2. Fix all issues found
3. Re-review
4. Repeat until no ❌/🟡 remain or 3 iterations completed
5. Final summary: iterations run, issues fixed, remaining issues
