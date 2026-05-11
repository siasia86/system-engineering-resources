Review @${1}

Full code review.

Check: bugs(null ref,index,type,edge cases,race condition) / design(SRP,globals,circular dep,hardcode,magic number) / unintended behavior(side effects,order dependency,implicit state) / error handling(exception scope,bare except,return value check,resource release) / security(input validation,path traversal,injection,permissions,secret exposure) / performance(unnecessary IO,memory,nested loops) / doc mismatch(docstring,config keys,error codes)

Output: Korean, ✅❌⚠️ per item, fixes as code blocks
