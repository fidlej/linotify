#!/bin/sh
# Archives the HEAD version of linotify-agent.
set -e

rm -rf release
mkdir -p release/linotify
hg archive release/linotify
mv release/linotify/agent release/linotify-agent
rm -rf 'release/linotify-agent/test'
find release/linotify-agent/ -type f -exec sha1sum {} \; | sed 's@  release/linotify-agent/@  @' >release/files.sha1
mv release/files.sha1 release/linotify-agent
tar czf release/linotify-agent.tar.gz -C release linotify-agent

mv release/linotify-agent.tar.gz app/static/download/
#rm -rf release

