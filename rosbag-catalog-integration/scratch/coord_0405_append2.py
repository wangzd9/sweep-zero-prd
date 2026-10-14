import io

path = "/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/COORDINATOR.md"
entry = """
- 04:1x 巡检（coord poll，prerun 04:05:53 指纹 bd16cbfa，夜间静默只落盘不群报）：6 变更源全消费=A 04:04 只读巡检 / TESTER 04:02 增量实测+回执段 / sessions 各角色自写 / 本角色 04:01 事件，无外部新输入、无新派单、无新裁决、coordinator_requests=[]。三面交叉零分歧：A 04:03:59 / TESTER 04:01:17 / 本角色 04:01 轮 04:03:18 独立实测一致——4acf689f（16_02_03 10.1GB 正式链）SCENE_RUNNING attempt1 heartbeat 30s 连续、八步 QUEUED ~297min、VLM Running 4/POST 200 连发、8767 active_runs=[4acf689f ACCEPTED]，INFER 远端推理活跃跨夜，升级条件逐项未命中，ruling-4acf-infer-active-0218 维持不 kill/retry。批次状态不变：3 收口（15_58_23 复用/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE）+ 空包 16_33_10 D6 收口 + 4acf689f INFER 在算 + flat 三提交 a65a25a7/87dfebaa/518089ed PENDING_INPUT 等 D4③ 串行释放。控制动作=零：无新派单、零 OCR（无代码变更）、零强审（REVOKED 0/5，grant 6b2d83f 到期前不续）、零合入、零生产写。事件 `coord-batch1012-0405-echoes-only-zero-action-quiet-202610140405` 落盘。
- 04:1x 补记：首 ack（bd16cbfa）因指纹粘贴错一字被拒（STALE_OBSERVATION），非新事件；sleep 60s 后 observer 新扫指纹 `18c29920`（pending 含 TESTER 04:07 增量巡检 `tester-t11s-batch-1012-0407-infer-continue-quiet-20261014`：4acf689f INFER 持续活跃 VLM Running 3-4/POST 200 连发/prefix 93.1%、八步 QUEUED ~301min、scan_job 4021 空包拒绝周期持续、PASS 基线不变、无升级条件命中）——已全文核读，与 A/TESTER/本角色 04:0x 口径零分歧，无新业务输入。落脚本 `scratch/coord_0405_ack.py`（从 observer JSON 实时取 observed fp）ack `18c29920` 成功。**下一步：** 5min observer 接续核模型段完成信号（EXTRACT/DONE 翻面/八步 DB 推进/SCENE_DONE 任一）→ 终态后放行 A D4③ + TESTER 血缘/跨 DB3 边界/两次 reconcile 增量验收；升级条件才重新裁决；08:00 夜间汇总（含 D5 肇事身份 192.168.2.132 上报 + 双文件坑教训 + 大包进展 + 强审 REVOKED 0/5）。
"""
with io.open(path, "r", encoding="utf-8") as f:
    content = f.read()
if not content.endswith("\n"):
    content += "\n"
content += entry
with io.open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("appended ok, total bytes:", len(content.encode("utf-8")))