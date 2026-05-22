Review @${1}
# ${1} 생략 시: 이 대화에서 가장 최근에 수정/생성/읽은 코드 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 리뷰할까요?" 라고 물어볼 것.

Full code review.

Check: bugs(null ref,index,type,edge cases,race condition) / design(SRP,globals,circular dep,hardcode,magic number) / unintended behavior(side effects,order dependency,implicit state) / error handling(exception scope,bare except,return value check,resource release) / security(input validation,path traversal,injection,permissions,secret exposure) / performance(unnecessary IO,memory,nested loops) / doc mismatch(docstring,config keys,error codes)

Output: Korean, ✅❌⚠️ per item, fixes as code blocks
