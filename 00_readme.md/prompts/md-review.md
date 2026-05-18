Review markdown @${1}

Check: structure(toc-section match,heading level,flow) / content(tech error,typo,example mismatch,duplication) / code block(lang tag,runnable,output accuracy) / link(anchor,external,image) / table(alignment,format) / footer(badge,date,license) / ref-stars(★☆=tool,★★☆=blog/3rdparty,★★★☆=official-doc,★★★★☆=rfc/seminal,★★★★★=canonical/rare) / internal-doc(remove: 내부 공유 자료 header, 문서 변경 이력, 문서 관리자, 피드백 email, 실명 @mention, 작성자 노트)

Output: Korean, ✅❌⚠️ per item, diff for fixes

Loop (max 3 iterations):
1. Review → list all ❌/⚠️ issues
2. Fix all issues found
3. Re-review the same file(s)
4. Repeat until no ❌/⚠️ remain or 3 iterations completed
5. Final summary: iterations run, issues fixed, remaining issues
