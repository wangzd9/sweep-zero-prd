import io, sys, os
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
TARGET = os.path.join(ROOT, "sessions/C.md")
TMP = os.path.join(ROOT, "scratch/c_entry_0918.md")
TOKEN = sys.argv[1]

entry = io.open(TMP, "r", encoding="utf-8").read()
assert entry.startswith("- 最后更新：2026-10-12 09:18 +08:00"), "entry signature bad"
assert entry.rstrip().endswith("见下"), "entry tail bad"

orig = io.open(TARGET, "r", encoding="utf-8").read()
lines = orig.splitlines(keepends=True)
print("orig_lines:", len(lines))
# 校验前两条签名仍在（首行=09:15 条目，次行=09:08 条目）
assert lines[0].startswith("- 最后更新：2026-10-12 09:15 +08:00"), "line1 not 09:15 entry"
assert lines[1].startswith("- 最后更新：2026-10-12 09:08 +08:00"), "line2 not 09:08 entry"
# 防止重复写入
assert "C-cron-poll-20261012-091853" not in orig, "091853 already present"

new_content = entry.rstrip("\n") + "\n" + orig

# 干跑：写到临时 TARGET 并核验
dry = TMP + ".dry"
io.open(dry, "w", encoding="utf-8").write(new_content)
dl = io.open(dry, "r", encoding="utf-8").read().splitlines(keepends=True)
assert len(dl) == len(lines) + 1, "dry line count"
assert dl[0].startswith("- 最后更新：2026-10-12 09:18 +08:00"), "dry line1"
assert dl[1].startswith("- 最后更新：2026-10-12 09:15 +08:00"), "dry line2"
assert dl[-1] == lines[-1], "dry last line preserved"
assert sum("C-poll-20261012-091353" in l for l in dl) >= 1, "prev entry preserved"
os.remove(dry)

# 校验全部通过后才写真实文件（最后一步 open）
io.open(TARGET, "w", encoding="utf-8").write(new_content)
# 写后验证
after = io.open(TARGET, "r", encoding="utf-8").read().splitlines(keepends=True)
print("after_lines:", len(after))
assert after[0].startswith("- 最后更新：2026-10-12 09:18 +08:00"), "write verify line1"
assert after[1].startswith("- 最后更新：2026-10-12 09:15 +08:00"), "write verify line2"
assert after[-1] == lines[-1], "write verify last"
assert "C-cron-poll-20261012-091853" in after[0], "owner in line1"
print("WRITTEN OK token_present=%s" % ("C-cron-poll-20261012-091853" in new_content))