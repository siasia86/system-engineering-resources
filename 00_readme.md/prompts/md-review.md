Review markdown @${1}
# ${1} 생략 시: 이 대화에서 가장 최근에 수정/생성/읽은 .md 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 리뷰할까요?" 라고 물어볼 것.

Check: structure(toc-section match,heading level,flow) / content(typo,example mismatch,duplication,broken sentence) / code block(lang tag,runnable,output accuracy) / link(anchor,external,image) / table(alignment,format,display-width: Korean=2 ASCII=1) / diagram(box chars │┌└ detected → all │...│ rows must have equal display width, pad spaces before closing │; ┌─┐/└─┘ horizontal lines match content width; diagram interior use English only, add Korean explanation below diagram; arrow flow direction logical) / footer(badge,date,license) / ref-stars(★☆=tool,★★☆=blog/3rdparty,★★★☆=official-doc,★★★★☆=rfc/seminal,★★★★★=canonical/rare) / internal-doc(remove: 내부 공유 자료 header, 문서 변경 이력, 문서 관리자, 피드백 email, 실명 @mention, 작성자 노트)

# 기술 내용의 사실 정확성(RFC 대조, 할루시네이션 탐지, 비검증 수치)은 @fact-check 에서 별도 수행.
# 이 프롬프트는 형식/구조/스타일만 검사.

# _reference/ 파일 추가 검증 항목 (경로에 _reference/ 포함 시 적용)
# source-coverage: frontmatter에 sources: URL 존재 여부 / 본문 내용이 해당 URL로 추적 가능한지
# unverified: 공식 문서에서 확인 불가한 내용에 "# 미확인 — 검증 필요" 표시 누락 여부
# version-accuracy: 버전 정보가 GitHub API / PyPI API / 공식 릴리즈 페이지 기준인지 (기억·추론 기반 금지)
# no-inference: 공식 문서에 없는 기능명·파라미터명·동작 설명 혼입 여부 (블로그·Stack Overflow·추론 내용 금지)
# last-checked: frontmatter last_checked 날짜 존재 여부

Output: Korean, ✅❌🟡 per item, diff for fixes

Loop (max 3 iterations):
1. Review → list all ❌/🟡 issues
2. Fix all issues found
3. Re-review the same file(s)
4. Repeat until no ❌/🟡 remain or 3 iterations completed
5. Final summary: iterations run, issues fixed, remaining issues
