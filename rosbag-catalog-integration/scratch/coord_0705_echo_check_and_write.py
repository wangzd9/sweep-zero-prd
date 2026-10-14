#!/usr/bin/env python3
# 07:05 巡检：核 pending 变更源=自回声 → 落 checkpoint + event
import json, os, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
FP = "a11f5a2fafbef8ee1e8c129d7716056ba31df1c37a57e687eee25ac8e57de584"

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")

# 1) 变更源核验：本轮 pending 7 项（07:05:10 起观测，07:05:53 快照）
#    07:00 起 find 各派发目录零新文件（terminal 已核），coordinator_requests 最新 10-13 22:33 HANDLED
#    → 全部为 07:03 轮已消费口径的回声：本角色 07:03 事件双副本 + TESTER 07:01 事件双副本
#      + sessions C/TESTER/COORDINATOR 自写 + test-receipts TESTER 07:0x 段
checkpoint = f"""
- 07:05 巡检（coord poll，prerun 07:05:53 指纹 {FP}，quiet_hours 夜间只落盘不群报）：7 变更源全核读=上轮 07:03 口径的增量回声（本角色 07:03 事件 canonical+inbox 双副本 + TESTER 07:01 增量只读实测事件双副本 + sessions C/TESTER/COORDINATOR 自写 + test-receipts TESTER 07:0x 回执段），零外部新输入、零新派单/裁决/群请求（coordinator_requests=[]，最新 10-13 22:33 已 HANDLED；find 07:00 后核 inbox/1号/2号/3号/TESTER/coordinator/SPRAY-BATCH-1012-20261013 零新文件）。批次维持 07:03 口径：4acf689f（16_02_03 大包）SCENE_RUNNING attempt1 INFER 远端推理持续活跃跨夜（TESTER 07:01 实测 heartbeat 06:58→07:0x 30s 续租、八步 QUEUED ~490min、volcsw 92988→93002 递增；升级条件逐项未命中，ruling-4acf-infer-active-0218 维持不 kill/cancel/retry）+ flat 三提交 a65a25a7/87dfebaa/518089ed PENDING_INPUT source_id=NULL 等 A D4③ 串行释放（14_42_48 正式全链 NOT_RUN）+ 空包 16_33_10 D6 拒绝可追溯 + run 7=6DONE+1RUNNING + 8767 health=ok + PASS 基线不变。强审 REVOKED used_60m=0/5 不续旧 grant。控制动作=零：无新派单、零 OCR（无代码变更）、零强审、零合入、零生产写；本轮全程只读文档核读，未触生产。**下一步：** 5min observer 接续核模型段完成信号（checkpoint 翻 EXTRACT/DONE / 八步 DB 推进 / SCENE_DONE 任一）→ 终态后放行 A D4③ + TESTER 血缘/跨 DB3 边界/两次 reconcile 增量验收；升级条件命中才重新裁决；08:00 夜间汇总（含 D5 肇事身份 192.168.2.132 上报 + 强审 REVOKED 0/5）。夜间静默不群报，final [SILENT]。
"""

# 2) 读 sessions/COORDINATOR.md 尾部（先读后写，防截断）
sp = os.path.join(ROOT, "sessions", "COORDINATOR.md")
with open(sp, "r", encoding="utf-8") as f:
    content = f.read()
if not content.endswith("\n"):
    content += "\n"
content += checkpoint
with open(sp, "w", encoding="utf-8") as f:
    f.write(content)

# 3) 落实质事件（canonical + inbox 双副本，与既有事件链一致）
event = {
    "event_id": f"coord-batch1012-0705-echoes-4acf-infer-continue-noaction-quiet-{now.replace('-','').replace(':','').replace('T','')[:15]}",
    "occurred_at": now,
    "recorded_at": now,
    "role": "COORDINATOR",
    "task": "TASK-11S-BATCH-1012",
    "attempt": "1",
    "status": "OBSERVING",
    "supersedes_context": "prerun 07:05:53 指纹 " + FP + "，7 变更源=07:03 口径增量回声（本角色 07:03 事件双副本 + TESTER 07:01 事件双副本 + sessions C/TESTER/COORDINATOR 自写 + test-receipts 07:0x 段），零外部新输入",
    "summary": "07:05 静默巡检：7 变更源全核读=在途角色自产回声，零新派单/零新裁决/零群请求。批次维持 07:03 口径：4acf689f（16_02_03 大包）SCENE_RUNNING attempt1 INFER 远端推理持续活跃跨夜（升级条件逐项未命中，ruling-4acf-infer-active-0218 维持不 kill/cancel/retry）+ flat 三提交 PENDING_INPUT 等 A D4③ 串行释放（14_42_48 NOT_RUN）+ 空包 D6 拒绝可追溯 + PASS 基线不变。控制动作=零：无新派单、零 OCR（无代码变更）、零强审（REVOKED 0/5 不续）、零合入、零生产写；本轮只读文档核读。",
    "evidence": "terminal find 07:00 后核 inbox/1号/2号/3号/TESTER/coordinator/SPRAY-BATCH-1012-20261013/requests 零新文件；coordinator_requests 最新 10-13 22:33 HANDLED；TESTER 07:01 事件全文核读（heartbeat 06:58→30s、八步 QUEUED ~490min、volcsw 递增、scan 幂等 failed:2）与本角色 07:03 口径零分歧",
    "next": "5min observer 接续核模型段完成信号（checkpoint 翻 EXTRACT/DONE / 八步 DB 推进 / SCENE_DONE 任一）→ 终态后放行 A D4③ + TESTER 增量验收；升级条件才重新裁决；08:00 夜间汇总",
    "quiet_hours_note": "夜间静默 21:00-08:00：工作落盘照常，不主动群报；final [SILENT]",
    "source_fingerprint": FP,
}
for d in ("events/COORDINATOR", "inbox/events/COORDINATOR"):
    p = os.path.join(ROOT, d, event["event_id"] + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", p)
print("checkpoint appended to", sp)
print("event_id:", event["event_id"])