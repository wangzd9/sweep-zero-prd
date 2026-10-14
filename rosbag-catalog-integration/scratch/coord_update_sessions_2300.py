import sys

root = "/home/wang/work/doc/prd/rosbag-catalog-integration"
with open(root + "/scratch/coord_ckpt_2300.md", "r", encoding="utf-8") as f:
    ckpt = f.read()

p = root + "/sessions/COORDINATOR.md"
with open(p, "r", encoding="utf-8") as f:
    content = f.read()

old_head = "## 2026-10-10 22:57 \u5de1\u68c0\u68c0\u67e5\u70b9\uff08cron poll 14ae4556629a\uff0c\u771f\u5b9e checked_at 22:55:53\uff09"
new_head = "## \u5386\u53f2\u68c0\u67e5\u70b9\uff082026-10-10 22:57\uff0ccron poll 14ae4556629a\uff0c\u771f\u5b9e checked_at 22:55:53\uff09"
assert old_head in content, "current head not found"
content = content.replace(old_head, new_head, 1)
content = ckpt + content
with open(p, "w", encoding="utf-8") as f:
    f.write(content)
print("sessions/COORDINATOR.md updated")