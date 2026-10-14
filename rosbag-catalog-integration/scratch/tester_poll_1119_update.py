#!/usr/bin/env python3
"""TESTER poll 11:19 heartbeat: record rework-7 merge (main 4697be0->b7cee07), maintain IDLE."""
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
sess = ROOT / "sessions" / "TESTER.md"
text = sess.read_text(encoding="utf-8")

new_line = (
    "- 心跳：2026-10-11 11:21 CST（本轮唤醒=v2 5分钟巡检 preflight checked_at 2026-10-11T11:19:53+08:00 "
    "control=ACTIVE、legacy_busy 空、无存活旧 owner；TESTER.lock claim cron-tester-poll-1119（token 946c0913…）短写即释放。"
    "11:16 后实质变化=**2号 rework-7 已合入 main**（11:18 commit `b7cee07` --no-ff merge，git 独立复核 = origin/main；"
    "OCR R7-r1 0 findings session 084ce079；`git diff 4697be0..b7cee07`=2 文件 +15/-9：app `scene_result_report_service.py` "
    "仅 2 行注释精确化（:582 赋值行未动，**零代码/零行为变更**）、`tests/test_scene_result_report.py` 时钟固定重构"
    "（首放/同秒重放共用 T0、跨秒显式 T0+1s，纯测试基建，业务断言未弱化））→ **被测快照 4697be0→b7cee07**；"
    "attempt-5（target `4697be0`）行为面结论对本变动持续有效，复用依据=上述 diff 逐行核对（app 面零行为），TESTER 复测口径无变化，不自行开新 attempt。"
    "inbox/TESTER/ 无新 PENDING（grep status: PENDING rc=1）；强复审 `R2I-20261010-06-result.md` 仍不存在"
    "（reviews/strongmodel 最新仍为 pack），**pack target 待协调者由 `4697be0` 更新为 `b7cee07`**，维持 READY_FOR_USER_TRIGGER（用户手动触发）；"
    "docker ps -a 无 tester 容器残留（grep rc=1）→ **维持 IDLE**，不重复启动已完成测试。"
    "下一步=等协调者更新强复审 pack target + 用户手动触发 → 03/05/06 聚合 DONE → TASK-08 联调派单届时 ACK 后开工）\n"
)
# 顶部第一个非空行前插入（新心跳置顶，与既有文件惯例一致）
idx = text.index("- 心跳：")
text = text[:idx] + new_line + text[idx:]
sess.write_text(text, encoding="utf-8")
print("updated sessions/TESTER.md")