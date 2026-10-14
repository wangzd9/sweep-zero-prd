# -*- coding: utf-8 -*-
"""14:08 巡检检查点写入：HANDOFF + sessions/COORDINATOR prepend，TIMELINE append，event 落盘。"""
import json
import pathlib
import sys
import time

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
NOW = "2026-10-11 14:08"
NOW_ISO = "2026-10-11T14:08:00+08:00"

CHECKPOINT = f"""## 2026-10-11 14:08 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T14:05:53+08:00：2号 rework-9 交付→验收合入收口）
- **2号 rework-9 交付并验收合入**：`c2cee73452299b8029c899ac491dba3263fa2b26`（14:01 交付，base `65ca0be`，1 file +3/-1 纯 docstring 零行为变更：`tests/test_scene_slice_scheduling.py:1163` 删"无库成功应用过，改短零兼容风险"无条件兼容声明、改与迁移文件 `alembic/versions/20261009_02_ingest_frozen.py:40` 限定边界一致口径）→ 独立机械核验全绿（全 SHA/HEAD~1=`65ca0be`=合入前 origin/零越界/**AST 全量比对独立复跑**：865 常量仅该 docstring 1 条差异+6604 非常量节点前后一致+新口径断言通过且"无条件/零兼容风险"零残留/定向 **36 passed RC=0** + ruff 绿，wt-04a-r9 独立复跑）→ 串行 OCR R9-r1：diff 唯一文件被 default_path 排除，**纯测试交付 0 入选=预期口径**（coverage 0/0，OCR_EXIT=0，7ms，与 R8-r1 session `b012b488`/18:59 夹具单 `c2dbe91` 先例一致，非漏审非故障）→ **--no-ff 合入 main `62a85bf`（14:08，推 origin 65ca0be..62a85bf）**+ 合入后 sanity 全绿（alembic 单头 `20261009_02_ingest_frozen`/ruff 绿/SQLite 定向 36 passed RC=0 主仓独立复跑）。decision `inbox/coordinator/TASK-06B/attempt-1-r2-rework-9-acceptance-decision.md`（ACCEPT_MERGED）+ OCR 账 `reviews/TASK-06B/attempt-1-r2-rework-9/ocr-batches.md`。
- **codex 审查链（七轮）全部收口**：r10 最终态（13:54）仅余的 B-02 已随 rework-9 合入落地，B-01 协调者 13:55 已处置，**不再起第八轮**；06B 开发/测试/OCR 面全闭环。
- **强复审 R2I-20261010-06**：**target 已更新 `62a85bf`**（pack_update_20261011_1415：增量 patch `git diff eff0479..62a85bf` = 11 文件 +2032/-251，sha256 `76ff031dc95e6051efae3fc90938430b5b1404210a177d2d35d77975a6e5e8b2`）；结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` 仍不存在，**READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。rework-9 为 test-only docstring（零行为变更），不触发 TESTER 复测（先例=rework-7 R-03）。
- **main**：HEAD `62a85bfb6b3791ebfa706cce0125bb217635126f`（= origin/main，rev-parse 双核一致）；13:57 后业务目录新增=2号 rework-9 派单+ACK（14:00）+回执（14:02）+ B 交付事件，均已本轮处置。
- **角色占用**：A/C/TESTER 全空闲（无新交付）；B rework-9 交付冻结（`c2cee73` 已入 main，wt-04a-r9 冻结）；无在途 ocr/pytest 业务进程（ps 复核）；`ocr.lock`/`coordinator.lock` 本轮自持已释放。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps 复核，发现 2号 14:01 rework-9 交付回执 REVIEW_PENDING）→机械核验+AST 独立复跑+定向/ruff 复跑→尺寸预检（微批纯测试）→串行 OCR R9-r1（预期 0 入选收口）→合入+push+sanity→decision+OCR 账+TODO（06/06B 行/进度行/主线收口注记）+强复审包 target 更新+TIMELINE（coord-poll-1405-r9-merged-62a85bf-20261011）→event→release。**有合入，06B 开发面全闭环（codex 七轮全收口），门禁推进至仅强复审一项**。
- **下一步**：巡检核强复审结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` 是否出现（用户手动触发）→ PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
"""

TIMELINE_EVENT = f"""
<!-- role-event:coord-poll-1405-r9-merged-62a85bf-20261011 -->
- {NOW_ISO} COORDINATOR TASK-06B/attempt-1-r2-rework-9 MERGED：2号 rework-9 `c2cee73`（codex 第七轮最终态 r10 B-02 **最后一条意见**，14:01 交付，1 file +3/-1 纯 docstring 零行为变更：tests:1163 删无条件兼容声明改迁移文件限定边界口径）→ 独立机械核验全绿（全 SHA/HEAD~1=65ca0be/零越界/AST 全量比对独立复跑：865 常量仅该 docstring 1 条差异+6604 非常量节点一致+新口径断言通过且旧声明零残留/定向 36 passed RC=0+ruff 绿独立复跑）→ 串行 OCR R9-r1 纯测试交付预期 0 入选（coverage 0/0，OCR_EXIT=0，R8-r1/c2dbe91 先例同口径）→ --no-ff 合入 main **62a85bf**（14:08，推 origin 65ca0be..62a85bf）+ 合入后 sanity 全绿（alembic 单头 20261009_02_ingest_frozen/ruff 绿/SQLite 定向 36 passed RC=0 独立复跑）→ **codex 审查链（七轮）全部收口，不再起第八轮**；强复审包 R2I-20261010-06 target 更新 62a85bf（pack_update_20261011_1415，增量 patch eff0479..62a85bf 11 文件 +2032/-251 sha256 76ff031d…）仍等**用户手动触发**；rework-9 test-only 不触发 TESTER 复测；证据：inbox/coordinator/TASK-06B/attempt-1-r2-rework-9-acceptance-decision.md; reviews/TASK-06B/attempt-1-r2-rework-9/ocr-batches.md；下一步：巡检核强复审结果文件→PASS 收口即 03/05/06 聚合 DONE→TASK-08；补录：{NOW_ISO}
"""

def prepend(path: pathlib.Path, block: str):
    p = ROOT / path
    old = p.read_text(encoding="utf-8")
    p.write_text(block + old, encoding="utf-8")
    print("prepended", path, "len", len(block))

def append(path: pathlib.Path, block: str):
    p = ROOT / path
    old = p.read_text(encoding="utf-8")
    p.write_text(old + block, encoding="utf-8")
    print("appended", path, "len", len(block))

prepend("HANDOFF.md", CHECKPOINT)
prepend("sessions/COORDINATOR.md", CHECKPOINT)
append("TIMELINE.md", TIMELINE_EVENT)

# event 落盘
ev = {
    "event_id": "coord-poll-1405-r9-merged-62a85bf-20261011",
    "role": "COORDINATOR",
    "task": "TASK-06B",
    "attempt": "attempt-1-r2-rework-9",
    "status": "MERGED",
    "occurred_at": NOW_ISO,
    "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "summary": "2号 rework-9 c2cee73（codex 第七轮最终态 B-02 最后一条意见，纯 docstring 零行为变更）独立 AST 核验+定向 36 passed+ruff 绿全绿 → OCR R9-r1 预期 0 入选收口 → --no-ff 合入 main 62a85bf 推 origin，sanity 全绿；codex 审查链七轮全部收口不再起第八轮；强复审 R2I-20261010-06 target 更新 62a85bf（pack_update_20261011_1415）仍等用户手动触发",
    "evidence": "inbox/coordinator/TASK-06B/attempt-1-r2-rework-9-acceptance-decision.md; reviews/TASK-06B/attempt-1-r2-rework-9/ocr-batches.md",
    "next": "巡检核强复审结果文件 reviews/strongmodel/R2I-20261010-06-result.md 是否出现→PASS 收口即 03/05/06 聚合 DONE→TASK-08",
}
ep = ROOT / "events" / "COORDINATOR" / f"coord-poll-1405-r9-merged-62a85bf-20261011.json"
ep.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
print("event written", ep)
print("DONE")