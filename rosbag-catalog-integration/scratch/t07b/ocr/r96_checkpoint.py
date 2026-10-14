import json, subprocess, time
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "a706bedf4cf6488b8214b5f99d2a437f"
OWNER = "cron-coord-poll-14ae4556629a-20261012-201553-r96"
NOW = time.strftime("%Y-%m-%d %H:%M")

cp = f"""## 2026-10-12 {NOW} 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T20:15:53+08:00，第 96 轮；r95 detached OCR 在途正常，零业务变化）

- **r95 detached 串行 OCR 在途核（20:1x 实测）**：pid 464164（PGID=464164 Ss，20:02:16 起）存活，`fuser` 核 `inbox/ocr.lock` 由其 flock 持有；子进程 node `ocr review`（pid 464166）正在跑 **b5 `scene_manual_revision_service.py`**（`--max-tokens 30000`，`--from 502bf8e --to f4bfcf2`），b5 日志 0 字节 20:02 起=首文件在途未收口（已约 14 分钟，r92 同尺寸单文件 329-415s 口径内正常）。
- **队列实况（20:1x vllm metrics 实测）**：`18002` num_requests_running=**4**（较 r95 20:01 的 2 回升=其他 worker 抢占窗口），b5 若在 4 并发下再空转超 400s 收口则 r97+ 核 `remaining_progress.txt` 记账，detached 无 420s 外层上限，不 reap；脚本逐文件续跑 b6-b10 直至 `== r95 detached done ==` 标记。
- 交付冻结 REVIEW_PENDING 不变：`f4bfcf2`（base `502bf8e`，main 未合入）；OCR 已收口 4/10（b1 0 / b2 0 / b3 **1 medium CORRECTION 待裁决** / b4 0）。
- **角色占用**：B=交付冻结 REVIEW_PENDING；A/C/TESTER 空闲（preflight legacy_busy 空）；pid 464164/464166 为唯一在途业务进程。
- **强审查**：授权在案 grant `31dcbabe…` 至 2026-10-13 11:33:12 +08:00，滚动 60 分钟 0/5，累计 0，在途 0，token/费用未知；07B 预判 REVIEW_NOW 待 OCR 收口。
- **门禁**：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；changelog F-035~039 等用户审批不催。
- 本轮控制动作：claim（`{OWNER}`，20:17:47，token 自 lease JSON）→巡检核查（ps+fuser 核 detached OCR 存活与锁持有/vllm metrics 队列实测/remaining_progress 复读）→checkpoint+event→release。**无新派单、无合入、无门禁变更**。
- **下一步：** r97+ 核 `remaining_progress.txt`（FILE=b5 RC=0+Review complete=记账续 b6-b10；pid 464164 已退且无 done 标记=异常如实记账，按 r95 预案不无限重启，挂 NEEDS_MAIN_REVIEW 交长寿命会话）→全收口后裁决 b3 medium→强审查 pack 起跑（授权 0/5，期限 2026-10-13 11:33:12）→合入→TESTER 独立验证→07B DONE→派 07C。
"""

sess = f"{ROOT}/sessions/COORDINATOR.md"
with open(sess, "r", encoding="utf-8") as f:
    old = f.read()
with open(sess, "w", encoding="utf-8") as f:
    f.write(cp + "\n" + old)
print("sessions written", len(old), "->", len(cp) + len(old))

ev = f"""---
event_id: coord-poll-20261012-201553-r96-ocr-inflight
role: COORDINATOR
time: {time.strftime('%F %T %z')}
task: TASK-07B
attempt: 1
status: OCR_IN_FLIGHT
summary: r96 巡检：r95 detached OCR pid 464164 存活、flock 持 ocr.lock、b5 首文件在途（~14min，vllm 4 并发）；零业务变化
evidence: scratch/t07b/ocr/remaining_progress.txt
next: r97 核 b5 收口（RC/Review complete）续 b6-b10
"""
with open(f"{ROOT}/inbox/events/COORDINATOR/coord-poll-20261012-201553-r96-ocr-inflight.md", "w", encoding="utf-8") as f:
    f.write(ev)
print("event written")

out = subprocess.run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN], capture_output=True, text=True)
print("RELEASE RC", out.returncode, out.stdout.strip()[:200], out.stderr.strip()[:200])