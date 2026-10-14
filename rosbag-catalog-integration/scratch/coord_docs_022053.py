import sys
root = "/home/wang/work/doc/prd/rosbag-catalog-integration"
cp = open(root + "/scratch/coord_cp_022053.md").read().rstrip() + "\n"
p = root + "/sessions/COORDINATOR.md"
cur = open(p).read()
open(p, "w").write(cp + cur)
line = "| 2026-10-12 02:20:53 | COORDINATOR | coord-poll-20261012-022053-nochange | 巡检 | POLL_NO_CHANGE | P0 收口后空转第3轮：main 453da0c 双核一致、02:15 后零业务事件、五角色全空闲、无在途进程；TASK-11 生产门禁维持未放行 | |\n"
with open(root + "/TIMELINE.md", "a") as f:
    f.write(line)
print("docs updated")