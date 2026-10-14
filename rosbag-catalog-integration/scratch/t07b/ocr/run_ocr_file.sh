#!/usr/bin/env bash
# 串行单文件 OCR（cron 化身短路径：单文件 <420s，flock 持 ocr.lock）
# 用法: run_ocr_file.sh <入选文件>
set -u
WT=/home/wang/.local/state/rosbag-scene/wt-04a-t07b
BASE=502bf8ec79690cf01e130cb0591121eb10e96af5
HEAD=f4bfcf2aad48877c3a3add55a02eed44c055a115
LOCK=/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/ocr.lock
LOGDIR=/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr
FILE="$1"
SAFE=$(echo "$FILE" | tr '/' '_')
LOG="$LOGDIR/ocr_${SAFE}.log"

# 排除其余 9 个入选文件 + tests
ALL="alembic/versions/20261012_01_scene_manual.py,app/api/__init__.py,app/api/scene_manual_revision.py,app/models.py,app/services/scene_manual_revision_service.py,app/static/bag-detail.css,app/static/bag-search.css,app/templates/bags.html,app/templates/detail.html,app/web/bags.py,tests/*"
EXCL=$(echo "$ALL" | tr ',' '\n' | grep -vxF "$FILE" | paste -sd, -)

cd "$WT" || exit 9
python3 - "$FILE" <<'PYEOF'
import fcntl, subprocess, sys, time
file = sys.argv[1]
lock = open("/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/ocr.lock", "a+")
fcntl.flock(lock, fcntl.LOCK_EX)
logdir = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr"
log = open(f"{logdir}/ocr_{file.replace('/','_')}.log", "w")
base = "502bf8ec79690cf01e130cb0591121eb10e96af5"
head = "f4bfcf2aad48877c3a3add55a02eed44c055a115"
allf = ["alembic/versions/20261012_01_scene_manual.py","app/api/__init__.py","app/api/scene_manual_revision.py","app/models.py","app/services/scene_manual_revision_service.py","app/static/bag-detail.css","app/static/bag-search.css","app/templates/bags.html","app/templates/detail.html","app/web/bags.py","tests/*"]
excl = ",".join(f for f in allf if f != file)
t0 = time.time()
rc = subprocess.run(
    ["ocr","review","--from",base,"--to",head,"--audience","agent","--max-tokens","60000","--exclude",excl],
    cwd="/home/wang/.local/state/rosbag-scene/wt-04a-t07b",
    stdout=log, stderr=subprocess.STDOUT,
).returncode
dt = int(time.time()-t0)
log.flush()
tail = [l.rstrip() for l in open(f"{logdir}/ocr_{file.replace('/','_')}.log") if l.strip()]
print(f"FILE={file} RC={rc} SECONDS={dt}")
for l in tail[-12:]:
    print(l)
PYEOF