#!/bin/sh
# Archives the HEAD version of linotify-agent.
set -e

hgversion=`hg log --limit 1 agent | head -1 | cut -d: -f3`

rm -rf release
mkdir -p release/linotify

# Export the agent source code
hg archive release/linotify
mv release/linotify/agent release/linotify-agent
rm -rf 'release/linotify-agent/test'
sed -i -e 's/${HGVERSION}/'"$hgversion/" release/linotify-agent/agent.py

# Package it
find release/linotify-agent/ -type f -exec sha1sum {} \; | sed 's@  release/linotify-agent/@  @' >release/files.sha1sum
mv release/files.sha1sum release/linotify-agent
tar czf release/linotify-agent.tar.gz -C release linotify-agent

# Publish it
mv release/linotify-agent.tar.gz app/static/download/

rm -rf release

