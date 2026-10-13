#!/usr/bin/env bash
# Stops all three BLACKGATE sites.  ./stop.sh
cd "$(dirname "$0")"
for d in box portal submission; do (cd "$d" && docker compose down); done
