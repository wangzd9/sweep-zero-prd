import hashlib, json
from pathlib import Path

d = json.load(open("/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.json"))
before = d["source_hash_before"]
BAG_SRC = Path("/mnt/nas_backup/data_slice/1165414093/slope/1165414093_slope_20260818_105105_105120")

after = {}
for f in sorted(BAG_SRC.iterdir()):
    h = hashlib.sha256(f.read_bytes()).hexdigest() if f.stat().st_size < 60_000_000 else hashlib.sha256(open(f, 'rb').read(1 << 20)).hexdigest()
    after[f.name] = {"size": f.stat().st_size, "mtime": f.stat().st_mtime, "sha256_head1MB": h}

print("changed:")
for name in sorted(set(before) | set(after)):
    b, a = before.get(name), after.get(name)
    if b == a:
        continue
    if b is None:
        print(f"  NEW  {name} {a}")
    elif a is None:
        print(f"  GONE {name} was {b}")
    else:
        print(f"  DIFF {name}\n    before {b}\n    after  {a}")
print("total before", len(before), "after", len(after), "unchanged", after == before)