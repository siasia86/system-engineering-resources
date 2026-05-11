#!/usr/bin/env bash

echo "rsync --dry-run"
rsync -av /home/sjyun/.kiro/ /root/sj_del/00_default/.kiro/ --exclude .cli_bash_history --exclude sessions --exclude *.swp  -n
sleep 5
rsync -av /home/sjyun/.kiro/ /root/sj_del/00_default/.kiro/ --exclude .cli_bash_history --exclude sessions --exclude *.swp 


