"""T10 reverify AC-3 独立复核：源袋前后 hash/mtime/size 一致性。
before 值取自驱动证据 scratch/t10/t10-e2e.json (source_hash_before)，
after 为本次独立重算（sha256 head 1MB + size + mtime）。"""
import hashlib
import json
import sys
from pathlib import Path

BAG = Path("/mnt/nas_backup/data_slice/1165414093/slope/1165414093_slope_20260818_105105_105120")
EV = json.loads(Path("/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.json").read_text())
before = EV["source_hash_before"]

ok = True
for f in sorted(BAG.iterdir()):
    st = f.stat()
    h = hashlib.sha256(f.read_bytes() if st.st_size < 60_000_000 else open(f, "rb").read(1 << 20)).hexdigest()
    b = before.get(f.name)
    match = b is not None and b["sha256_head1MB"] == h and b["size"] == st.st_size and abs(b["mtime"] - st.st_mtime) < 0.001
    ok = ok and match
    print(f"{f.name}: size={st.st_size} mtime={st.st_mtime:.6f} sha1MB={h[:16]}.. match_before={match}")

print("ALL_UNCHANGED" if ok else "CHANGED_DETECTED")
sys.exit(0 if ok else 1)