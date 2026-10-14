#!/usr/bin/env bash
set -e
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
CP="$ROOT/scratch/coord_cp_1145.txt"
for F in "$ROOT/HANDOFF.md" "$ROOT/sessions/COORDINATOR.md"; do
  { cat "$CP"; echo; cat "$F"; } > "$F.new" && mv "$F.new" "$F"
  echo "PREPENDED $F"
done
head -3 "$ROOT/HANDOFF.md"
head -3 "$ROOT/sessions/COORDINATOR.md"