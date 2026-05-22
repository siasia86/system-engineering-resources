Review markdown @${1}
# ${1} 생략 시: 이 대화에서 가장 최근에 수정/생성/읽은 .md 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 리뷰할까요?" 라고 물어볼 것.

Check: structure(toc-section match,heading level,flow) / content(tech error,typo,example mismatch,duplication) / code block(lang tag,runnable,output accuracy) / link(anchor,external,image) / table(alignment,format,display-width: Korean=2 ASCII=1) / diagram(box chars │┌└ detected → all │...│ rows must have equal display width, pad spaces before closing │; ┌─┐/└─┘ horizontal lines match content width; diagram interior use English only, add Korean explanation below diagram) / footer(badge,date,license) / ref-stars(★☆=tool,★★☆=blog/3rdparty,★★★☆=official-doc,★★★★☆=rfc/seminal,★★★★★=canonical/rare) / internal-doc(remove: 내부 공유 자료 header, 문서 변경 이력, 문서 관리자, 피드백 email, 실명 @mention, 작성자 노트)

Output: Korean, ✅❌⚠️ per item, diff for fixes

Loop (max 3 iterations):
1. Review → list all ❌/⚠️ issues
2. Fix all issues found
3. Re-review the same file(s)
4. Repeat until no ❌/⚠️ remain or 3 iterations completed
5. Final summary: iterations run, issues fixed, remaining issues
