#!/usr/bin/env python3
# coordinator 23:40:53 poll: read t10 run log + evidence json + git heads with cwd
import subprocess, json, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
CAT = "/home/wang/work/rosbag-catalog"

def sh(cmd, cwd=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"

out = {}
rc, h1, e1 = sh("git rev-parse main", cwd=CAT)
rc2, h2, e2 = sh("git rev-parse origin/main", cwd=CAT)
out["main"] = h1 or e1
out["origin_main"] = h2 or e2

rc, runlog, _ = sh("cat /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-run.log")
out["run_log"] = runlog

rc, ev, _ = sh("python3 -c \"import json;d=json.load(open('/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.json'));print(json.dumps(d,ensure_ascii=False,indent=1)[:6000])\"")
out["e2e_json_head"] = ev

rc, pub, _ = sh("find /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/publish /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/work -type f -exec ls -la {} \\; 2>/dev/null | head -30")
out["publish_work_ls"] = pub

# db quick check
rc, db, _ = sh("python3 -c \"import sqlite3;c=sqlite3.connect('/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.db');print([r for r in c.execute('select name from sqlite_master where type=\\\"table\\\"')])\"")
out["db_tables"] = db

print(json.dumps(out, ensure_ascii=False, indent=1))