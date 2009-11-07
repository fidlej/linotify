#!/bin/sh
set -e

rm -rf release/linotify
mkdir -p release/linotify
hg archive release/linotify
tar czf release/linotify-agent.tar.gz release/linotify/agent
mv release/linotify-agent.tar.gz app/static/download/
tar czf release/linotify.tar.gz release/linotify
mv release/linotify.tar.gz app/static/download/
