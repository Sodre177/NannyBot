#!/bin/bash

cd ~/projects/bot
echo "Resetting local branch:"
git checkout ${1:-master} -f 
echo "Pulling:"
git pull
echo "Resetting again in case the branch was just created:"
git checkout ${1:-master} -f 
echo "Replacing prefix bot:, changing to nanny:"
sed -i "s:\"bot\:\":\"nanny\:\":g" index.js
echo "Killing other nannybots:"
pkill -f "bot/index.js"
echo "Starting up:"
token=AaBb_01CcDdEeFfGgHhIiJjKk0123LlMmNnOoPpQqRrSsTtUuVvWw4567XxYyZz node ../bot/index.js >> nannybot.log 2>&1 &
echo "Redeployed NannyBot from branch ${1:-master} of Sodre177/bot! Check nannybot.log if there are any issues!"
