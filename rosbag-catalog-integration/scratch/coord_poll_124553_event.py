#!/usr/bin/env python3
import json, os, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

event = {
    "event_id": "coord-poll-20261011-124553-nochange",
    "occurred_at": "2026-10-11T12:45:53+08:00",
    "recorded_at": datetime.datetime.now().astimezone().isoformat(),
    "role": "COORDINATOR",
    "task": "TASK-06",
    "attempt": "0",
    "status": "NOCHANGE",
    "summary": "12:45 巡检：12:40 后零业务变化；main HEAD 65ca0be（= origin/main，rev-parse 三核一致）；12:40:53 后业务目录新增仅 B 12:44 例行 IDLE_WAITING 心跳（b-poll-20261011-124253-nochange）与 TESTER 12:42 例行 IDLE 心跳（tester-poll-20261011-123953-nochange），均报无新派单、强复审 result 仍缺，非业务交付；各角色 ticks 12:42-12:46 无在途忙碌，TESTER.lock 短租约 12:46 已释放在途。",
    "evidence": "git rev-parse HEAD=main=origin/main=65ca0beb0111a2d45065206886d432bd20eb76d0（三核一致）；find -newermt 2026-10-11 12:40:53 业务目录仅 events/B 094407ed…(b-poll-20261011-124253-nochange)+events/TESTER 76af9190…(tester-poll-20261011-123953-nochange)+各角色 runtime ticks/sessions（例行心跳）；reviews/strongmodel 仍无 R2I-20261010-06-result.md（目录最新 12:31 pack，target 65ca0be）；ps 无 ocr/pytest 业务进程（仅 wxocr 桌面）；ocr.lock 12:28 0 字节、coordinator.lock 0 字节、leases 仅 C.lock(05:19)/TESTER.lock(12:46 短租约) 无他角色在途",
    "next": "下轮核强复审 R2I-20261010-06 结果文件与 inbox 新派单/回执；空闲不扩需求",
}
path = os.path.join(ROOT, "events/COORDINATOR", "coord-poll-20261011-124553-nochange.json")
with open(path, "w") as f:
    json.dump(event, f, ensure_ascii=False, indent=2)
print("written", path)

cp = f"""## 2026-10-11 12:45 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T12:45:53+08:00：12:40 后零业务变化）
- **12:40 后零业务变化**：main HEAD `65ca0beb0111a2d45065206886d432bd20eb76d0`（= main = origin/main，rev-parse 三核一致）；12:40:53 后业务目录新增仅 B 12:44 例行 IDLE_WAITING 心跳（`b-poll-20261011-124253-nochange`，报 12:38 后 0 命中、强复审 result 仍缺、无新派单）与 TESTER 12:42 例行 IDLE 心跳（`tester-poll-20261011-123953-nochange`，报无新测试派单、attempt-5 证据不失效），均非业务交付。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 12:31 pack，target `65ca0be`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（ticks 12:42–12:46 例行，无在途忙碌；TESTER.lock 短租约 12:46 claim 已释放在途）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面）；`ocr.lock`(12:28)/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/locks/leases/ticks 复核）→append 检查点→event→release，**无新派单、无状态变更、无 OCR**。
"""

for target in ("sessions/COORDINATOR.md", "HANDOFF.md"):
    tp = os.path.join(ROOT, target)
    with open(tp) as f:
        content = f.read()
    with open(tp, "w") as f:
        f.write(cp + content)
    print("prepended", tp)