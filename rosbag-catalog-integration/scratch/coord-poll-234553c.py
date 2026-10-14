#!/usr/bin/env python3
import json
ROOT="/home/wang/work/doc/prd/rosbag-catalog-integration"
for role in ("A","B","C","TESTER","COORDINATOR"):
    try:
        d=json.load(open(f"{ROOT}/inbox/control/runtime/ticks/{role}.json"))
        print(role, json.dumps(d, ensure_ascii=False))
    except Exception as e:
        print(role, "ERR", e)
try:
    d=json.load(open(f"{ROOT}/inbox/control/runtime/leases/TESTER.json"))
    print("TESTER.lease", json.dumps(d, ensure_ascii=False))
except Exception as e:
    print("TESTER.lease ERR", e)