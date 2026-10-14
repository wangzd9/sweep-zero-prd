
import pathlib
root = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
sp = root / "sessions/C.md"
line = (root / "scratch/c_poll_0308_new_line.txt").read_text(encoding="utf-8")
old = sp.read_text(encoding="utf-8")
assert old.startswith("- 最后更新："), "sessions head changed between read and write, abort"
sp.write_text(line + "\n" + old, encoding="utf-8")
print("sessions prepended ok")
