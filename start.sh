#!/usr/bin/env bash
# Starts all three BLACKGATE sites. Run from the blackgate-split folder:  ./start.sh
set -e
cd "$(dirname "$0")"

for d in box portal submission; do
  [ -f "$d/docker-compose.yml" ] || { echo "ERROR: folder '$d' not found here. You are probably in an OLD copy (it should contain box, portal, submission)."; exit 1; }
done
docker info >/dev/null 2>&1 || { echo "ERROR: Docker is not running or you lack permission. Try: sudo ./start.sh"; exit 1; }

for d in box portal submission; do
  echo "=== Starting $d ==="
  (cd "$d" && docker compose up -d --build)
done

echo
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'NAMES|blackgate'
echo
echo "Challenge files : http://localhost:8080"
echo "Flag submission : http://localhost:8090"
echo "Stage 6 box     : http://localhost:9000"
