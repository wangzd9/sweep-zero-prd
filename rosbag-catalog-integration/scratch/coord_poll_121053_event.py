#!/usr/bin/env python3
import json, os, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

event = {
    "event_id": "coord-poll-20261011-121053-nochange",
    "occurred_at": "2026-10-11T12:10:53+08:00",
    "recorded_at": datetime.datetime.now().astimezone().isoformat(),
    "role": "COORDINATOR",
    "task": "TASK-06",
    "attempt": "0",
    "status": "NOCHANGE",
    "summary": "12:10 巡检：12:00 后零业务变化；main b7cee07=origin/main 复核一致；12:00:53 后业务目录新增仅 B 12:08 例行 IDLE 心跳（b-poll-20261011-120753-nochange，报无新派单、强复审 result 仍缺，非业务交付）；强复审 R2I-20261010-06 result 文件仍不存在（pack target b7cee07 在案），保持 READY_FOR_USER_TRIGGER 等用户手动触发；06 聚合放行门禁唯一剩余不变。",
    "evidence": "git rev-parse HEAD=main=origin/main=b7cee07c71adf8fcfec5465247170f45f9c648e9（三核一致）；find -newermt 2026-10-11 12:00:53 业务目录仅 events/B a9c41b75…(b-poll-20261011-120753-nochange IDLE 心跳)+自身 12:00 tick；reviews/strongmodel 无 R2I-20261010-06-result.md（目录最新 11:22 pack）；ps 无 ocr/pytest 业务进程（仅 wxocr 桌面）；ocr.lock/coordinator.lock 0 字节无他角色在途持有者",
    "next": "下轮核强复审结果文件与 inbox 新派单/回执；空闲不扩需求",
}
path = os.path.join(ROOT, "events/COORDINATOR", "coord-poll-20261011-121053-nochange.json")
with open(path, "w") as f:
    json.dump(event, f, ensure_ascii=False, indent=2)
print("written", path)

cp = f"""## 2026-10-11 12:10 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T12:10:53+08:00：12:00 后零业务变化）
- **12:00 后零业务变化**：main HEAD `b7cee07c71adf8fcfec5465247170f45f9c648e9`（= main = origin/main，rev-parse 三核一致）；12:00:53 后业务目录新增仅 B 12:08 例行 IDLE 心跳（`b-poll-20261011-120753-nochange`，报无新派单、强复审 result 仍缺，非业务交付）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 11:22 仅 pack，target `b7cee07`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B 12:08 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/lock/event 复核）→event 落盘（`coord-poll-20261011-121053-nochange`）→prepend 检查点（sessions+HANDOFF）→release，**无新派单、无合入、无状态变更**。
"""

for target in ("sessions/COORDINATOR.md", "HANDOFF.md"):
    tp = os.path.join(ROOT, target)
    with open(tp) as f:
        content = f.read()
    with open(tp, "w") as f:
        f.write(cp + content)
    print("prepended", tp)