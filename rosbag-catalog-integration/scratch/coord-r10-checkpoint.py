import subprocess, json, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "hermes-cron-poll-14ae4556629a-20261011-135553"

claim = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                        "--role", "COORDINATOR", "--owner", OWNER],
                       capture_output=True, text=True)
print("CLAIM_RC", claim.returncode)
print(claim.stdout[-400:])
print(claim.stderr[-400:])
if claim.returncode != 0:
    sys.exit(1)

out = claim.stdout
token = None
for line in out.splitlines():
    s = line.strip()
    if s.startswith("token") or s.startswith("TOKEN"):
        token = s.split("=", 1)[-1].strip()
if not token:
    try:
        data = json.loads(out)
        token = data.get("token")
    except Exception:
        pass
if not token:
    import re
    m = re.search(r"\b([0-9a-f]{16,})\b", out)
    token = m.group(1) if m else None
print("TOKEN_FOUND", bool(token))

CP = """## 2026-10-11 13:57 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T13:55:53+08:00：13:50 后主会话回合处置 codex r10 最终态裁决）
- **13:50 后新事实（主会话回合 13:55–13:57 落盘，本侧核实）**：codex 第七轮（74ba3bf..65ca0be 最终态收口确认，13.3 万 token）裁决 `reviews/codex-r10-finalstate-20261011-verdict.md`（13:54）= **APPROVED_WITH_COMMENTS：A 节 10 条遗留意见全部落地无回退、代码零缺陷**，仅 2 条 info——B-01 仓库外文档连接语义误称残留（协调者 13:55 已直接处置：attempt-5 报告 3 处正文修正 + 4 份历史材料顶部纠错标注，复核 :12/:51 等指向为 r10 定位，标注已落 13:56:49）；B-02 `tests/test_scene_slice_scheduling.py:1163` docstring 无条件兼容声明 → **回派 2号 `attempt-1-r2-rework-9`（13:57 落盘，base main `65ca0be`，PENDING 未 ACK；B 13:54 心跳早于 13:57 派单，符合 5 分钟节奏）**，纯 docstring 零行为变更，交付后协调者 AST 验证直接验收合入、不再起 codex 第八轮。
- **main 不变**：HEAD `65ca0beb0111a2d45065206886d432bd20eb76d0`（= origin/main，rev-parse 双核一致，本轮无合入）；TODO:49/:50 已按 r10 口径记账（codex 七轮收口、强复审 target 待 rework-9 合入后更新）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**，维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型；pack target 现 `65ca0be`（pack_update_20261011_1231），**待 rework-9 合入后更新为合入 commit**（材料口径改为 codex 七份报告 + 两轮 TESTER MySQL + FOUND_ROWS 定论 + 测试 diff）。
- **角色占用**：2号待领 rework-9（PENDING）；A/C/TESTER 空闲（13:51–13:54 例行 ticks 心跳）；无在途 ocr/pytest 业务进程（ps 复核空）；leases 仅 C 05:19 / TESTER 12:46 零字节例行租约，无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/locks/ticks/事件复核，确认 13:50 后变化=主会话回合 r10 裁决处置+rework-9 派单，本侧仅补 checkpoint/事件，不重复派单）→prepend 检查点→event→release，**无新派单（沿用主会话身份）、无合入、无 OCR、无状态变更**。
- **下一步**：下轮巡检核 2号 rework-9 ACK/交付 → 交付后 AST 独立核验+定向 ruff → 直接验收合入（不再起 codex 第八轮）→ 强复审包 target 更新 → 等用户手动触发 → 03/05/06 聚合 DONE → TASK-08。
"""

with open(os.path.join(ROOT, "sessions/COORDINATOR.md"), encoding="utf-8") as f:
    content = f.read()
with open(os.path.join(ROOT, "sessions/COORDINATOR.md"), "w", encoding="utf-8") as f:
    f.write(CP + "\n" + content)
print("SESSION_PREPEND_OK")

event = subprocess.run([sys.executable, RUNTIME, "event", "--project", ROOT,
                        "--role", "COORDINATOR", "--token", token,
                        "--event-id", "coord-poll-20261011-135553-r10-handled-rework9-dispatched",
                        "--task", "TASK-06B", "--attempt", "1-r2",
                        "--status", "DISPATCHED",
                        "--summary", "核实主会话回合 13:55–13:57 处置 codex 第七轮 r10 最终态裁决（APPROVED_WITH_COMMENTS 2 info 代码零缺陷）：B-01 仓库外文档已协调者处置（attempt-5 报告 3 处正文修正+4 份历史材料顶部纠错标注）；B-02 回派 2号 attempt-1-r2-rework-9（13:57 PENDING 未 ACK，base main 65ca0be，纯 docstring，交付后协调者 AST 验证直接验收合入不再起 codex 第八轮）；main 65ca0be 不变；强复审 R2I-20261010-06 result 仍缺 READY_FOR_USER_TRIGGER，target 待 rework-9 合入后更新；本侧仅补 checkpoint/事件，不重复派单",
                        "--evidence", "reviews/codex-r10-finalstate-20261011-verdict.md; inbox/2号/TASK-06B/attempt-1-r2-rework-9.md",
                        "--next", "下轮巡检核 2号 rework-9 ACK/交付"],
                       capture_output=True, text=True)
print("EVENT_RC", event.returncode)
print(event.stdout[-300:])
print(event.stderr[-300:])

rel = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                      "--role", "COORDINATOR", "--token", token],
                     capture_output=True, text=True)
print("RELEASE_RC", rel.returncode)
print(rel.stdout[-200:])
print(rel.stderr[-200:])