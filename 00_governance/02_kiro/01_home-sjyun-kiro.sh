#!/usr/bin/env bash
WHO01="${WHO01:-${SUDO_USER:-$(id -un)}}"

case "$WHO01" in
    siasia|yunli|sjyun)
        ;;
    *)
        echo "unsupported WHO01: ${WHO01}" >&2
        exit 1
        ;;
esac

echo "rsync -av /home/${WHO01}/.kiro/ /root/sj_del/00_default/.kiro/${WHO01}/ --exclude .cli_bash_history --exclude sessions --exclude .local --exclude *.swp  -n"
echo "============================================="
echo "# rsync --dry-run mode #"
echo "rsync -av /home/${WHO01}/.kiro/ /root/sj_del/00_default/.kiro/${WHO01}/ --exclude .cli_bash_history --exclude sessions --exclude .local --exclude *.swp  -n"

rsync -av /home/${WHO01}/.kiro/ /root/sj_del/00_default/.kiro/${WHO01}/ --exclude .cli_bash_history --exclude sessions --exclude *.swp  -n
for ((i=1;i<=10;i++)) ; do echo "#####  ${i}  #####" ; sleep 1 ; done
rsync -av /home/${WHO01}/.kiro/ /root/sj_del/00_default/.kiro/${WHO01}/ --exclude .cli_bash_history --exclude sessions --exclude *.swp

echo "rsync --dry-run"
rsync -av /home/${WHO01}/.kiro/ /root/32_system-engineering-resources/00_governance/02_kiro/  --exclude .cli_bash_history --exclude sessions --exclude .local --exclude *.swp --exclude 01_home-sjyun-kiro.sh -n
for ((i=1;i<=5;i++)) ; do echo "#####  ${i}  #####" ; sleep 1 ; done
rsync -av /home/${WHO01}/.kiro/ /root/32_system-engineering-resources/00_governance/02_kiro/  --exclude .cli_bash_history --exclude sessions --exclude .local --exclude *.swp --exclude 01_home-sjyun-kiro.sh



##################################################
#rsync -av  /root/sj_del/00_default/.kiro/${WHO01}/ /home/${WHO01}/.kiro/ --exclude .cli_bash_history --exclude sessions --exclude .local --exclude *.swp  -n && chown -R ${WHO01}:${WHO01} /home/${WHO01}/.kiro

## diff -r /home/sjyun/.kiro/ /home/yunli/.kiro/  --exclude='.cli_bash_history' --exclude='sessions'
