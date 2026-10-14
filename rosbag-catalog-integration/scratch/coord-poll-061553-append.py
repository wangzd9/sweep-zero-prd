import pathlib, shutil

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
scratch = ROOT / "scratch"
checkpoint = (scratch / "coord-poll-061553-checkpoint.txt").read_text().rstrip("\n")
event_md = (scratch / "coord-poll-061553-event.md").read_text()

# 1) move event into inbox/events/COORDINATOR/
dst = ROOT / "inbox/events/COORDINATOR/coord-poll-20261012-061553-p0-idle-r41.md"
shutil.move(str(scratch / "coord-poll-061553-event.md"), str(dst))

# 2) prepend checkpoint to sessions/COORDINATOR.md
sf = ROOT / "sessions/COORDINATOR.md"
old = sf.read_text()
sf.write_text(checkpoint + "\n" + old)

# 3) prepend checkpoint to HANDOFF.md
hf = ROOT / "HANDOFF.md"
oldh = hf.read_text()
hf.write_text(checkpoint + "\n" + oldh)

print("event:", dst)
print("sessions prepend ok, first line:", sf.read_text().splitlines()[0][:80])
print("handoff prepend ok, first line:", hf.read_text().splitlines()[0][:80])