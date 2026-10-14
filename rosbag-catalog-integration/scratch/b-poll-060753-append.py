import io, os, shutil

root = "/home/wang/work/doc/prd/rosbag-catalog-integration"
entry_src = os.path.join(root, "scratch/b-poll-060753-entry.txt")
sessions = os.path.join(root, "sessions/B.md")
event_src = os.path.join(root, "scratch/b-poll-060753-event.md")
event_dst = os.path.join(root, "inbox/events/B/b-poll-20261012-060753-nochange-task10-done-p0-idle.md")

# compute/verify FIRST, before touching shared file
entry = io.open(entry_src, encoding="utf-8").read().strip()
assert entry.startswith("- 巡检 2026-10-12 06:07"), "entry signature bad"
existing = io.open(sessions, encoding="utf-8").read()
assert "06:07 +08:00" not in existing, "entry already appended"
before_lines = existing.count("\n")
shutil.copyfile(event_src, event_dst)
new_content = existing.rstrip("\n") + "\n" + entry + "\n"
with io.open(sessions, "a", encoding="utf-8") as f:
    f.write("\n" + entry + "\n")
after = io.open(sessions, encoding="utf-8").read()
assert "06:07 +08:00" in after and after.count("\n") >= before_lines + 1
print("sessions append OK; event copied; lines %d -> %d" % (before_lines, after.count("\n")))