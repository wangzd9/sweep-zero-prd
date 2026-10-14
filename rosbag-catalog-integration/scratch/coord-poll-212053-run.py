import subprocess, sys, json, datetime

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
TOKEN = "6278ddd5ed1a49818bd7fcbd4ab6b3d5"
OWNER = "cron-coord-poll-212053"
NOW = "2026-10-11T21:25:00+08:00"

def run_cmd(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print("CMD:", " ".join(cmd[:8]), "... rc=", p.returncode)
    if p.returncode != 0:
        print("STDERR:", p.stderr[:2000])
        sys.exit(1)
    return p

# 1) prepend checkpoint to sessions/COORDINATOR.md
ckpt = """## 2026-10-11 21:20 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T21:20:53+08:00：2号 TASK-09 commit `a60bb81` 已落地，交付回执未到）

- **实质变化=2号 TASK-09 commit 落地（commit≠交付，不启动核验/OCR）**：`wt-04a-t09`（branch `scene/task-09-slope-real-verify`）21:22:58 commit `a60bb81`，diff `0a8ca8a..a60bb81`=**3 文件 +187/-3**（`app/scene/slope/adapter.py` +10 / `app/scene/slope/vlm.py` +17 / 新增 `tests/test_slope_vlm_wiring.py` 163 行）；commit 口径=模型 ID 完整路径默认 + max_tokens 2048 + enable_thinking 透传（真实样本核验 2026-10-11）。`receipts/TASK-09/` 与 `reports/TASK-09/` **均不存在** → 交付回执未到，本轮不机械核验、不 OCR、不合入。
- **2.3 回归已完成一轮 + 附加证据推进中（长测试，不重复启动不接管）**：21:21 B 起跑 pytest 全量（`pytest tests/ -q -x --ignore=tests/test_devflow.py`，pid 2860867，含 alembic upgrade head 前置，21:25 前进程已退出）；`scratch/t09-real/` 证据链：主 runner `t09-real-verify.json`（21:04，EXIT=0：row19 阳性 **SUCCESS** 非空可发布区间 / row22-23 阴性 NO_MATCH / 边界 MODEL_UNAVAILABLE 如实报出，五键齐全）；row20/21 **500 帧确定性复现**（`t09-real-verify-retry.json` 21:16：帧 `1787021491199936487` 第 13 帧 `HTTP 500 Internal Server Error @ http://192.168.2.45:8002/v1/chat/completions` → MODEL_UNAVAILABLE，与 21:11 探针口径一致，**非接线故障**）；阳性补足 row32/33（`t09-real-verify-extra.json` 21:20：row32 **NO_MATCH**（flat 11/slope 3，publish_target=false）+ row33 产物目录 21:20 仍在写，结论待定）。
- **main 不变**：HEAD `0a8ca8a`（= origin/main，rev-parse 双核一致）；20:55:53 后共享根业务面新增仅 TASK-09 相关（wt-04a-t09 编码/commit + scratch 证据 + 各角色 ticks/心跳 + 本侧记账），**无新派单/合入/OCR/decision**。
- **角色占用**：B=RUNNING（t09 交付整理中：commit 已落、回归+附加证据推进，等回执）；A/C/TESTER 空闲（C 最新 20:13 nochange 心跳+例行 tick，均报无新派单）；`ocr.lock` 0 字节无在途 OCR；ps 复核 21:25 无协调侧 ocr/pytest 业务进程。
- **门禁**：TASK-10 维持 WAITING（前置=08 DONE ✅ + 09 未交付）；TASK-11 生产启用门禁维持未放行；真实样本门禁已按 19:55 用户授权解除（09 本体在途）。
- 本轮控制动作：claim（`cron-coord-poll-212053`）→巡检核查（rev-parse 双核/find -newermt/wt-04a-t09 log+diff --stat/scratch 证据 json 复核/ps/locks）→HANDOFF+sessions 检查点+TIMELINE+event→release。**有状态变更（t09 commit 落地+回归完成一轮），无新派单、无合入、无 OCR**。
- **下一步**：下轮核 2号 `receipts/TASK-09/attempt-1.md` 交付回执（含 500 帧根因口径 + row33 结论 + 回归/ruff 证据 + 隔离资源声明）；交付即机械核验（diff vs 派单 AC 逐点、图像 content 非空、阳性/阴性/边界断言、500 帧归因）→串行 OCR（app 2 文件 + test，§3.6 尺寸预检）→合入→TASK-09 DONE→TASK-10 候选重算派单。
"""
with open(ROOT + "/sessions/COORDINATOR.md") as f:
    sessions = f.read()
with open(ROOT + "/sessions/COORDINATOR.md", "w") as f:
    f.write(ckpt + "\n" + sessions)
print("sessions/COORDINATOR.md prepended")

# 2) prepend checkpoint to HANDOFF.md
handoff_ckpt = """## 2026-10-11 21:25 巡检检查点（cron poll 14ae4556629a，checked_at 2026-10-11T21:20:53+08:00：TASK-09 2号 commit `a60bb81` 落地，交付回执未到）
- **TASK-09 2号 交付仍在途，commit 已落**：`wt-04a-t09` 21:22:58 commit `a60bb81`（`0a8ca8a..a60bb81` 3 文件 +187/-3：`app/scene/slope/adapter.py` + `app/scene/slope/vlm.py` + 新增 `tests/test_slope_vlm_wiring.py` 163 行；口径=模型 ID 完整路径默认 + max_tokens 2048 + enable_thinking 透传）；**commit≠交付**，`receipts/TASK-09/` 仍不存在 → 不核验不 OCR 不合入。21:21 B 已跑 pytest 全量回归（`--ignore=tests/test_devflow.py`，21:25 前进程退出）+ 附加证据推进：row20/21 500 帧确定性复现（retry 21:16，`帧 1787021491199936487` HTTP 500 @ `192.168.2.45:8002` → MODEL_UNAVAILABLE 如实报出，非接线故障）；阳性补足 row32 NO_MATCH（flat 11/slope 3）/ row33 21:20 仍在写。主 runner `t09-real-verify.json`（21:04 EXIT=0：row19 阳性 SUCCESS + 阴性 NO_MATCH + 边界 MODEL_UNAVAILABLE）证据链在案。
- main `0a8ca8a`=origin 未动；无 OCR 在途；TASK-10 维持 WAITING（前置 09 未交付）；生产启用 TASK-11 门禁维持未放行。
- **下一步**：等 2号 `receipts/TASK-09/attempt-1.md` 交付回执（含 500 帧根因口径 + row33 结论 + 回归/ruff 证据）→ 机械核验 → 串行 OCR → 合入 → 09 DONE → 派 TASK-10。

"""
with open(ROOT + "/HANDOFF.md") as f:
    handoff = f.read()
with open(ROOT + "/HANDOFF.md", "w") as f:
    f.write(handoff_ckpt + handoff)
print("HANDOFF.md prepended")

# 3) append TIMELINE row
timeline_row = "| 2026-10-11 21:22 | 2026-10-11 21:25 | 2号 / 协调者 cron | TASK-09 / attempt-1 | 2号 commit `a60bb81` 落地（21:22:58，`wt-04a-t09`，3 文件 +187/-3：slope VLM 接线=模型 ID 完整路径默认 + max_tokens 2048 + enable_thinking 透传 + 新增 `tests/test_slope_vlm_wiring.py` 163 行）；21:21 pytest 全量回归跑完（`--ignore=tests/test_devflow.py`）；真实样本附加证据：row20/21 500 帧确定性复现（`帧 1787021491199936487` HTTP 500 → MODEL_UNAVAILABLE 如实报出，非接线故障）+ 阳性补足 row32 NO_MATCH / row33 在途；**交付回执 `receipts/TASK-09/` 未到（commit≠交付，不核验不 OCR 不合入）**；main `0a8ca8a`=origin 不变；TASK-10 维持 WAITING | COMMIT_LANDED | wt-04a-t09 log a60bb81；scratch/t09-real/t09-real-verify{,-retry,-extra}.json | 等 2号交付回执→机械核验→串行 OCR→合入→09 DONE→派 TASK-10 |\n"
with open(ROOT + "/TIMELINE.md") as f:
    tl = f.read()
with open(ROOT + "/TIMELINE.md", "w") as f:
    f.write(tl + timeline_row)
print("TIMELINE.md appended")

# 4) event
run_cmd(["python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
         "--token", TOKEN,
         "--event-id", "coord-poll-20261011212053-task09-commit-a60bb81",
         "--task", "TASK-09", "--attempt", "1", "--status", "RUNNING",
         "--summary", "2号 t09 commit a60bb81 落地（3 文件 +187/-3 接线+test）+pytest 全量回归完成一轮+500 帧确定性复现（MODEL_UNAVAILABLE 如实报出）+row32/33 阳性补足在途；交付回执未到不核验不 OCR 不合入；main 0a8ca8a 不变；TASK-10 维持 WAITING",
         "--evidence", "wt-04a-t09 a60bb81；scratch/t09-real/*.json",
         "--next", "下轮核 receipts/TASK-09/attempt-1.md 交付回执→机械核验→串行 OCR→合入→09 DONE→派 TASK-10"])
print("event done")

# 5) release
run_cmd(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN])
print("released")