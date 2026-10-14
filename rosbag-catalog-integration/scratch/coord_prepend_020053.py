import pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
cp = (ROOT / "scratch/coord_cp_020053.md").read_text(encoding="utf-8")

for rel in ("sessions/COORDINATOR.md", "HANDOFF.md"):
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    if "2026-10-12 02:0x 巡检检查点" in text[:2000]:
        print(rel, "already has checkpoint, skip")
        continue
    p.write_text(cp + "\n" + text, encoding="utf-8")
    print(rel, "prepended ok")