#!/usr/bin/env python3
# 修复事件文件名末尾多余 '+'（时间戳切片产物）
import json, os
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
bad = "coord-batch1012-0705-echoes-4acf-infer-continue-noaction-quiet-20261014070831+.json"
good = "coord-batch1012-0705-echoes-4acf-infer-continue-noaction-quiet-20261014070831.json"
for d in ("events/COORDINATOR", "inbox/events/COORDINATOR"):
    pb, pg = os.path.join(ROOT, d, bad), os.path.join(ROOT, d, good)
    if not os.path.exists(pb):
        print("missing", pb); continue
    e = json.load(open(pb, encoding="utf-8"))
    e["event_id"] = good[:-5]
    with open(pg, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.remove(pb)
    print("fixed", pg)