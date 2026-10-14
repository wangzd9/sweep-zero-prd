# 独立验证派单：TASK-16B r2（与OCR并行）

status: DISPATCHED
时间：2026-10-13T17:45:32+08:00；owner=TESTER；本轮用户直接要求纠正执行，原16B验证范围内补齐独立证据，不新增需求。

- 固定base=40ab818，head=e152465；源树`/home/wang/.local/state/rosbag-scene/wt-03b-t16b`。独立干净隔离快照验证，禁止移动原开发树。diff只有scripts/scene_host_proxy.py及tests/test_scene_host_proxy.py。
- 先读`inbox/control/SPRAY-CORRECTION-20261013.md`、`receipts/TASK-16B/attempt-2-r2.md`与所需实现/测试；不要读整个历史。ACK后运行对应代理/编排定向验证，独立核R1-01迟到重复不二次执行、R1-02终态响应丢失/未提交对账、R1-03失败台账保留及恢复、R1-04 unlink异常释放ACTIVE、R1-05 replace后父目录fsync。注入结果必须证明状态/次数/台账，不只抄执行者PASS。
- 只验证固定r2，无真实模型调用、无NAS发布、无生产写入。不重跑整仓；未改模块的匹配SHA旧PASS直接复用。
- 交付`test-receipts/TEST-TASK16B-r2/attempt-1.md`，含被测完整SHA、命令/rc、逐项PASS/FAIL与证据。代码失败返原C，不改实现，不启动OCR或批准合入。
- 后续S9固定head到达再按其增量单复验；12S-C最终proxy接线在最终固定集成SHA另做受影响验证，不能把本单等同12S-D正式全链。
