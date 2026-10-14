import io

path = "/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/COORDINATOR.md"
entry = """
- 04:05 唤醒检查点（coord poll，prerun 04:05:53 指纹 bd16cbfa，夜间静默只落盘不群报）：6 变更源全消费=在途角色只读轮次+自产物回声（A 04:04 巡检 / TESTER 04:02 增量实测+回执 04:03 段 / sessions A·C·COORDINATOR·TESTER 自写 / 本角色 04:01 事件），无外部新输入、无新派单、无新裁决、coordinator_requests=[]。三面交叉零分歧：A 04:03:59 / TESTER 04:01:17 / 本角色 04:01 轮 04:03:18 独立实测一致——4acf689f（16_02_03 10.1GB 正式链）SCENE_RUNNING attempt1 heartbeat 30s 连续、八步 QUEUED ~297min、VLM Running 4/POST 200 连发、8767 active_runs=[4acf689f ACCEPTED]，INFER 远端推理活跃跨夜，升级条件逐项未命中，ruling-4acf-infer-active-0218 维持不 kill/retry。批次状态不变：3 收口（15_58_23 复用/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE）+ 空包 16_33_10 D6 收口 + 4acf689f INFER 在算 + flat 三提交 a65a25a7/87dfebaa/518089ed PENDING_INPUT 等 D4③ 串行释放。控制动作=零：无新派单、零 OCR（无代码变更）、零强审（REVOKED 0/5，grant 6b2d83f 到期前不续）、零合入、零生产写。**下一步：** 5min observer 接续核模型段完成信号（EXTRACT/DONE 翻面/八步 DB 推进/SCENE_DONE 任一）→ 终态后放行 A D4③ + TESTER 血缘/跨 DB3 边界/两次 reconcile 增量验收；升级条件才重新裁决；08:00 夜间汇总（含 D5 肇事身份 192.168.2.132 上报 + 双文件坑教训 + 大包进展 + 强审 REVOKED 0/5）。事件 `coord-batch1012-0405-echoes-only-zero-action-quiet-202610140405` 落盘。
"""
with io.open(path, "r", encoding="utf-8") as f:
    content = f.read()
if not content.endswith("\n"):
    content += "\n"
content += entry
with io.open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("appended ok, total bytes:", len(content.encode("utf-8")))