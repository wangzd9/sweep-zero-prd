#!/usr/bin/env python3
"""08:00 coordinator night-summary: append sessions/COORDINATOR.md entry + event JSON.
Read-first (r mode), then append; no truncate. Verifies trailing newline before append."""
import json, hashlib, os, sys, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
NOW = "2026-10-14T08:06:00+08:00"
EVENT_ID = "coord-batch1012-0800-night-summary-quiet-end-20261014"

entry = (
    "- 最后更新：2026-10-14 08:06 +08:00（TASK-11S-BATCH-1012 / COORDINATOR / 08:00 夜间汇总，prerun 08:00:53 指纹 d1514a48；"
    "静默窗口 21:00–08:00 结束，本条随 final 投递 08:00 全角色汇总）：夜间 11 小时本批零代码变更、零控制状态翻转、零新派单/新裁决/新返修"
    "（coordinator_requests=[] 全程）。变更源 8 项逐核全部=各角色自产事件/会话回声（COORDINATOR 07:45+07:56、TESTER 07:50+07:55、C 07:58 obs59、sessions×3、"
    "test-receipts TESTER 07:5x 段），无外部新输入。**夜间核心事实（07:52–08:00 只读实测汇总）**：① 大包 scene-4acf689f（16_02_03 正式链）SCENE_RUNNING "
    "attempt1 heartbeat 08:02:03 续租活跃、八步全 QUEUED（模型段 INFER 持续约 545min，跨夜不 kill/cancel/retry 口径，ruling-4acf-infer-active-0218 有效）；"
    "VLM 远端 07:59:38–08:00:28 采样 Running 2-3/Waiting 0/prefix 93.1-93.3%（C obs59）+TESTER 07:56 volcsw 99639→99663 同节奏，升级条件逐项未命中。"
    "② flat 三提交 a65a25a7(14_42_48)/87dfebaa(16_37_47)/518089ed(16_58_28) 仍 PENDING_INPUT source_id=NULL 等 SCENE_EXEC_HOST 串行释放，"
    "14_42_48 正式全链维持 NOT_RUN；scan 4067/4066（07:55:51）incoming SUCCESS 空包拒绝可追溯、self_built 全绿；8 包终态 6 DONE+1 RUNNING+空包拒绝面，无新终态。"
    "③ 资源面 NAS 71% 不变、生产栈 8 容器全 Up、8767 health ok；C obs59 记 load 2.18 单点上抬（5/15min 仍低位，非 C 进程，事实记录不升级）。"
    "**08:00 汇总上报两项**：A1=22:53:02 三 dup RETRY 肇事身份——开发机 192.168.2.132 外部人工手动 /retry API 三发+bind_vehicle 绑 vehicle_id=1『运营授权』，"
    "非 A/C/TESTER/COORDINATOR 留痕（C obs12 D5 交付），**肇事人身份待用户核实，不新开任务**；A2=C 记账缺口——obs56 轮 event JSON 未落 inbox/events/C"
    "（仅 canonical sessions 行在案，obs57 已申报），抽查后维持『canonical 行为准、事件落盘缺失不补造』口径，**不返修不升级**。"
    "强审查：REVOKED（grant 6b2d83fb 已于 10-13 撤销，expires_at 10-14 13:27 不续）；近 60min 0/5、在途 0；末次 SR-SPRAY-FINAL-R4 已 SUCCEEDED 收口，本批无代码变更不起 OCR/强审。"
    "**白天动作**：A 续 D4 第③步（4acf689f 终态后核 flat 409 释放/绑定推进并回执）；C 续只读观察+模型段完成信号申报；TESTER 续独立验收"
    "（终态后 14_42_48 全链+八步/reconcile+TEST_REPORT_PENDING）；B IDLE；恢复交接 21:07:41 ACK 在案不重复。零控制动作，5min observer 接续。"
)

# 1) append session (read-first, verify trailing newline)
s_path = os.path.join(ROOT, "sessions", "COORDINATOR.md")
with open(s_path, "r", encoding="utf-8") as f:
    content = f.read()
if not content.endswith("\n"):
    content += "\n"
new = content + entry + "\n"
with open(s_path, "w", encoding="utf-8") as f:
    f.write(new)
lines_before = content.count("\n")
lines_after = new.count("\n")
assert lines_after == lines_before + 1, f"append line check failed: {lines_before} -> {lines_after}"

# 2) event JSON (canonical inbox/events/COORDINATOR + mirrored events/COORDINATOR)
event = {
    "event_id": EVENT_ID,
    "occurred_at": NOW,
    "recorded_at": NOW,
    "role": "COORDINATOR",
    "task": "TASK-11S-BATCH-1012",
    "attempt": "1",
    "status": "NIGHT_SUMMARY",
    "supersedes_context": "prerun 08:00:53 指纹 d1514a48（8 变更源全自产回声，零外部新输入）；静默窗口 21:00-08:00 结束",
    "summary": "08:00 夜间汇总（11h）：本批零代码变更/零控制翻转/零新派单。大包 4acf689f INFER 模型段持续约545min 升级条件未命中不 kill/retry；flat 三提交 PENDING_INPUT 等串行释放 14_42_48 维持 NOT_RUN；8 包 6 DONE+1 RUNNING+空包拒绝面；NAS 71%/8 容器 Up/health ok。上报两项：dup RETRY 肇事身份=开发机 192.168.2.132 外部人工（待用户核实不新开任务）；C obs56 event JSON 落盘缺失（canonical 行为准不补造不返修）。强审 REVOKED 近60min 0/5 在途0。",
    "evidence": "sessions/COORDINATOR.md 08:06 条目（%d -> %d 行）；C obs59 08:0x、TESTER 07:5x、coord 07:56 事件；strong_review.py status：authorization=REVOKED used_last_60_minutes=0 active_calls=[] last_call SUCCEEDED" % (lines_before, lines_after),
    "next": "A 续 D4③（终态后 409 核+绑定+回执）；C 续观察+完成信号申报；TESTER 续独立验收+TEST_REPORT_PENDING；B IDLE；5min observer 接续，白天 20 分钟报告。",
    "quiet_hours_note": "08:00 静默窗口结束，本事件随 final 投递 08:00 全角色汇总。",
}
canon = os.path.join(ROOT, "inbox", "events", "COORDINATOR", EVENT_ID.split("-", 3)[-1].replace("20261014", "20261014080600").rsplit("-", 1)[0] + "-summary-20261014080600.json")
# simpler stable filename:
canon = os.path.join(ROOT, "inbox", "events", "COORDINATOR", "coord-batch1012-0800-night-summary-20261014080600.json")
mirr = os.path.join(ROOT, "events", "COORDINATOR", "coord-batch1012-0800-night-summary-20261014080600.json")
os.makedirs(os.path.dirname(mirr), exist_ok=True)
for p in (canon, mirr):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)

print("OK session_lines %d->%d canon=%s mirr=%s" % (lines_before, lines_after, canon, mirr))