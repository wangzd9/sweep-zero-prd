import json

p = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.json"
d = json.load(open(p))
print("TOP KEYS:", list(d.keys()))
print()
for k, v in d.items():
    if isinstance(v, dict):
        print("==", k)
        print(json.dumps(v, indent=1, ensure_ascii=False)[:3000])
    else:
        s = str(v)
        print(k, "=", s[:300])
    print()