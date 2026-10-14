import sys, pathlib
ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
cp = (ROOT / "scratch/_coord_cp_045553.md").read_text()
# ensure cp ends with newline
if not cp.endswith("\n"):
    cp += "\n"
for name in ["sessions/COORDINATOR.md", "HANDOFF.md"]:
    p = ROOT / name
    old = p.read_text()
    # prepend checkpoint then a blank line, keep original
    new = cp + "\n" + old
    p.write_text(new)
    print("prepended", name, "old_len", len(old), "new_len", len(new))
print("OK")