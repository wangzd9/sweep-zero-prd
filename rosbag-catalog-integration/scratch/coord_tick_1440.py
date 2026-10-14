import json, os
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
ev = {
  "event_id": "coord-poll-20261011-144053-nochange",
  "occurred_at": "2026-10-11T14:40:53+08:00",
  "role": "COORDINATOR",
  "task": "NONE",
  "attempt": "0",
  "status": "POLL_NO_CHANGE",
  "summary": "14:30 后零业务变化：main 62a85bf=origin/main 双核一致；14:30:53 后新增仅 B 14:22 r9-accept-booked 记账+C 14:38 nochange 心跳+各角色 tick/lease 例行刷新，非业务交付；强复审 R2I-20261010-06 result 仍不存在（target 62a85bf，READY_FOR_USER_TRIGGER）；A/B/C/TESTER 全空闲、无在途 ocr/pytest 业务进程",
  "evidence": "sessions/COORDINATOR.md 14:40 检查点; git rev-parse main=origin/main=62a85bfb; ls reviews/strongmodel/; find -newermt 14:30:53; ps/leases 复核",
  "next": "等用户手动触发强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单",
}
os.makedirs(os.path.join(ROOT, "events/COORDINATOR"), exist_ok=True)
with open(os.path.join(ROOT, "events/COORDINATOR/coord-poll-20261011-144053-nochange.json"), "w") as f:
    json.dump(ev, f, ensure_ascii=False, indent=2)

cp = """## 2026-10-11 14:40 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T14:40:53+08:00）
- **14:30 后零业务变化**：main HEAD `62a85bfb6b3791ebfa706cce0125bb217635126f`（= origin/main，rev-parse 双核一致）；14:30:53 后共享根新增仅 B `b-poll-20261011-142253-r9-accept-booked` 记账心跳、C `C-poll-20261011-143853-nochange` 心跳及各角色 tick/lease 例行刷新（find -newermt 核实，无派单/返修/交付）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 14:10 pack，target `62a85bf`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，ticks 14:36–14:40 例行）；leases 仅 C/TESTER 例行短租约；无在途 ocr/pytest 业务进程（ps 复核仅桌面 code/wxocr）；`ocr.lock`/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/leases/事件复核）→append 检查点+event→release，**无新派单、无状态变更、无 OCR**。
"""
sf = os.path.join(ROOT, "sessions/COORDINATOR.md")
with open(sf) as f: s = f.read()
if "coord-poll-20261011-144053-nochange" not in s:
    with open(sf, "w") as f: f.write(cp + s)
hf = os.path.join(ROOT, "HANDOFF.md")
with open(hf) as f: h = f.read()
if "14:40 巡检检查点" not in h:
    with open(hf, "w") as f: f.write(cp + h)
print("ok")