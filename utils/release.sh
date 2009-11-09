#!/bin/sh
set -e

hg out
hg push
./utils/archive.sh

cd app
./deploy.sh
wget -S -O /dev/null http://www.linotify.com
