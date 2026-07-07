Review @${1} Vagrantfile and related inventory.
# ${1} 생략 시: 이 대화에서 가장 최근에 작업한 Vagrantfile 또는 관련 inventory 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 리뷰할까요?" 라고 물어볼 것.

Check: provider(hyperv/virtualbox/libvirt config validity) / box(exists on Vagrant Cloud,arch match) / network(private_network support per provider,DHCP vs static) / synced_folder(type match OS,disabled when unnecessary) / provision(ansible path valid,inventory reachable,limit scope) / resources(memory/cpu reasonable for test) / naming(vm name matches box,no misleading alias) / security(no hardcoded credentials,ssh key path valid) / unused(dead variables,unreachable code) / inventory(ansible_host resolvable,key path exists,group logic)

Output: Korean, ✅❌🟡 per item, fixes as code blocks
