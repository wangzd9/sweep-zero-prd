#!/usr/bin/env python3
"""coord 09:55 poll: claim -> append checkpoint -> event -> release (scripted per protocol)."""
import subprocess, sys, json

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-coord-20261011-095553"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    out = (p.stdout or "")
    if p.returncode != 0:
        print("FAIL", " ".join(args), "RC=", p.returncode)
        print("OUT:", out[:1500], "ERR:", p.stderr[:1500])
        sys.exit(1)
    return out

out = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR",
          "--owner", OWNER, "--ttl", "180"])
data = json.loads(out)
if not data.get("claimed"):
    print("CLAIM BUSY:", out)
    sys.exit(2)
token = data["token"]
print("claimed ok")

ckpt = """
## 2026-10-11 09:55 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T09:55:53+08:00）
- **09:35 后变化（上轮在途收口）**：R6-r1 增量 OCR 收口 **0 findings** → 2号 rework-6 `f4cd654` 已验收合入 main `4697be0`（09:44:51 --no-ff，推 origin 一致；sanity 全绿：alembic 单头 / ruff 3 文件 / SQLite 71 passed，裁决 `inbox/coordinator/TASK-06B/attempt-1-r2-rework-6-acceptance-decision.md`）。
- **TESTER attempt-5 在途**：09:52 ACK 开工（`inbox/TESTER/TASK-06/r2-final-mysql-e2e-attempt-5-ack.md`），口径=真 MySQL 8.4.11 新隔离库 + 生产默认 PyMySQL 连接（实测 flag 无 CLIENT_FOUND_ROWS 并注明）+ `tests/test_scene_result_report.py` 33 用例全文件 + R-01 秒末边界探针（ns末=999_999_999 不进位、二次重放无 StaleDataError）+ R-03 零 UPDATE 独立口径 + attempt-4 抽查 + `6d30a68..4697be0` 越界核对；等回执 `test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-5.md`，**不重复派单**。
- **强复审 R2I-20261010-06**：target 已更新 `4697be0`（增量 patch sha256 `b41a6b58…`，11 文件 +2024/-251），结果文件仍不存在，**READY_FOR_USER_TRIGGER，用户手动触发**，不自行调用付费模型。
- **门禁**：06 聚合放行剩余 = TESTER attempt-5 PASS + 强复审；03/05/06 聚合 DONE → TASK-08 路径不变。
- **角色占用**：TESTER=attempt-5 在途；A/B/C 空闲无新交付（events 最新 A 09:52/C 09:51 均非业务交付）；`ocr.lock`/`coordinator.lock` 无在途持有者，协调侧无在途 ocr/pytest 进程。
- 本轮控制动作：claim→巡检核查→append 检查点+event→release，**无新派单、无状态变更**。
"""
path = ROOT + "/sessions/COORDINATOR.md"
with open(path, "a", encoding="utf-8") as f:
    f.write(ckpt)
print("checkpoint appended")

out = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
          "--token", token,
          "--event-id", "coord-poll-095553-attempt5-inflight-20261011",
          "--task", "TASK-06", "--attempt", "5", "--status", "POLL_NOTED",
          "--summary", "09:55 巡检：f4cd654 已合入 main 4697be0（R6-r1 0 findings 收口，09:35 轮后完成，sanity 全绿）；TESTER attempt-5 09:52 ACK 在途（真 MySQL 新隔离库+生产默认连接口径）；强复审 target 4697be0 仍待用户手动触发",
          "--evidence", "inbox/coordinator/TASK-06B/attempt-1-r2-rework-6-acceptance-decision.md; inbox/TESTER/TASK-06/r2-final-mysql-e2e-attempt-5-ack.md",
          "--next", "等 TESTER attempt-5 回执后审核；无新派单"])
print("event ok:", out[:300])

out = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR",
          "--token", token])
print("release:", out[:300])
print("DONE")