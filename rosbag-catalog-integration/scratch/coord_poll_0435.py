#!/usr/bin/env python3
import subprocess, sys, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "coordinator-cron-14ae4556629a-20261011043553"

def sh(*args):
    p = subprocess.run(list(args), capture_output=True, text=True)
    print(f"$ {' '.join(str(a) for a in args)}")
    if p.stdout: print(p.stdout)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(p.returncode)
    return p.stdout

out = sh("python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER)
import re
m = re.search(r"token[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9_-]+)", out) or re.search(r"\b([A-Za-z0-9]{16,})\b", out)
token = m.group(1) if m else None
print("TOKEN:", token)
if not token:
    sys.exit(1)

ckpt = """## 2026-10-11 04:35 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T04:35:53+08:00）
- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main，rev-parse 双核一致）；04:30:53 后业务目录唯一新增为 B 04:34 例行 IDLE 心跳 `b-poll-20261011-043253-nochange`（task=NONE，非业务）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新仍为 pack `R2I-20261010-06-pack.md`，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 项 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B 04:34 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核仅既有 alembic/uvicorn 服务与 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 无他角色在途持有者。
- 本轮控制动作：claim→巡检核查→prepend 检查点→release，**无新派单、无状态变更**。
"""
sess = ROOT + "/sessions/COORDINATOR.md"
with open(sess) as f:
    old = f.read()
with open(sess, "w") as f:
    f.write(ckpt + old)
print("checkpoint written")

sh("python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token)
print("released")