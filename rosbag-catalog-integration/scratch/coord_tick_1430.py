#!/usr/bin/env python3
# 协调者 14:30 巡检：补记 codex r11 终审收口（TIMELINE 事件 + sessions 检查点）
import json, pathlib

R = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")

# 1) TIMELINE 追加 r11 收口事件（幂等：已有 r11 则跳过）
tl = R / "TIMELINE.md"
tl_text = tl.read_text(encoding="utf-8")
if "codex-r11-final-20261011" not in tl_text:
    entry = (
        "\n<!-- role-event:coord-poll-1430-codex-r11-final-20261011 -->\n"
        "- 2026-10-11T14:29:00+08:00 COORDINATOR TASK-06B codex R11_FINAL：codex 第八轮收尾确认（65ca0be..62a85bf，rework-9/B-02 落库后终态）裁决 **APPROVED 零 comment**"
        "（reviews/codex-r11-final-20261011-verdict.md，14:29 落盘）：B-02 tests:1163 与迁移文件 20261009_02_ingest_frozen.py:40 口径一致、"
        "`零兼容/无库/没有库` 测试文件 0 命中、AST 双复核（codex 独立 + 协调者合入前）确认零行为变更、无增量新问题 → "
        "**codex 审查链八轮全部收口，零遗留意见**；main 现 `62a85bf`（= origin/main，rev-parse 双核一致）。"
        "06B 开发/测试/OCR 面全闭环不变，06 聚合放行唯一剩余门禁=强模型增量复审 R2I-20261010-06（target `62a85bf`，pack_update_20261011_1415，"
        "result 文件 reviews/strongmodel/R2I-20261010-06-result.md 仍不存在，**用户手动触发**）→ PASS 后 03/05/06 聚合 DONE → TASK-08。\n"
    )
    tl.write_text(tl_text + entry, encoding="utf-8")
    print("TIMELINE: appended r11 event")
else:
    print("TIMELINE: r11 already present, skip")

# 2) sessions/COORDINATOR.md 检查点（插入文件首部下一行前=最新在上）
sf = R / "sessions/COORDINATOR.md"
s = sf.read_text(encoding="utf-8")
if "14:30 巡检检查点" not in s:
    cp = (
        "## 2026-10-11 14:30 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T14:30:53+08:00）\n"
        "- **14:25 后唯一新事实=codex r11 终审收口**（14:29 主会话回合落盘 `reviews/codex-r11-final-20261011-verdict.md`）：65ca0be..62a85bf 裁决 **APPROVED 零 comment**（B-02 与迁移文件 :40 口径一致/`零兼容/无库/没有库` 0 命中/AST 双复核零行为变更）→ **codex 审查链八轮全部收口、零遗留意见**；本侧核实 main HEAD `62a85bfb…`（= origin/main rev-parse 双核一致），TIMELINE 补记 r11 事件（coord-poll-1430-codex-r11-final-20261011）。\n"
        "- **强复审 R2I-20261010-06**：result 文件 `reviews/strongmodel/R2I-20261010-06-result.md` 仍不存在（pack 14:10 更新 target `62a85bf`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。\n"
        "- **门禁**：06 聚合放行唯一剩余=强复审（06B 开发/测试/OCR 面全闭环，TESTER attempt-5 10:07 ACCEPT、rework-9 14:08 合入 sanity 全绿）；PASS 后 03/05/06 聚合 DONE → TASK-08 联调派单，路径不变。\n"
        "- **角色占用**：A/B/C/TESTER 全空闲（preflight legacy_busy 空；TESTER 14:15 心跳维持 IDLE、无容器残留；leases 无他角色在途）；无在途 ocr/pytest 业务进程（ps 核实 rc=1）；`ocr.lock`/`coordinator.lock` 无在途持有者。\n"
        "- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/leases/events 复核）→TIMELINE 补记+本检查点→release，**无新派单、无合入、无 OCR、无状态变更**。\n"
    )
    # 最新在上：插到文件第一个 checkpoint 标题前
    import re
    m = re.search(r"^## 2026", s, re.M)
    if m:
        s = s[: m.start()] + cp + "\n" + s[m.start():]
    else:
        s = cp + "\n" + s
    sf.write_text(s, encoding="utf-8")
    print("sessions: checkpoint prepended")
else:
    print("sessions: 14:30 checkpoint already present, skip")

# 3) 事件文件
ev_dir = R / "events/COORDINATOR"
ev = {
    "event_id": "coord-poll-1430-codex-r11-final-20261011",
    "role": "COORDINATOR",
    "task": "TASK-06B",
    "attempt": "attempt-1-r2-rework-9",
    "status": "REVIEW_CHAIN_CLOSED",
    "occurred_at": "2026-10-11T14:29:00+08:00",
    "recorded_at": "2026-10-11T14:30:53+08:00",
    "summary": "codex r11（65ca0be..62a85bf 终审确认）APPROVED 零 comment，codex 审查链八轮全部收口零遗留；main 62a85bf=origin 双核一致；06 聚合放行唯一剩余=强复审 R2I-20261010-06（result 仍不存在，用户手动触发，target 62a85bf）",
    "evidence": "reviews/codex-r11-final-20261011-verdict.md; reviews/strongmodel/R2I-20261010-06-pack.md",
    "next": "巡检核强复审 result 文件出现→PASS 收口即 03/05/06 聚合 DONE→TASK-08 联调派单",
}
ev_path = ev_dir / (ev["event_id"] + ".json")
if not ev_path.exists():
    ev_path.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("event: written")
else:
    print("event: already exists, skip")
print("OK")