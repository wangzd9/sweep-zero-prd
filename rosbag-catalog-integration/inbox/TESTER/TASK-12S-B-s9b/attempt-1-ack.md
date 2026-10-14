# ACK：TESTER TASK-12S-B S9b attempt-1 增量独立复验

- status: ACKED
- ACK 时间：2026-10-13T18:45+08:00
- owner：TESTER
- 派单：`inbox/TESTER/TASK-12S-B-s9b/attempt-1-dispatch.md`（2026-10-13 纠正轮，r2 短定向单之后按序接续）
- 固定快照：base=`0320a8e96c76e126de15c61d0671afb88ae8988f`，head=`f76e2a9b403577b791ca3688e0da5e574c4c272a`（完整 SHA 从对象解析）
- 源树核对：`wt-04a-t12sb` HEAD 实测=`f76e2a9b…`，porcelain 仅 `.venv` 未跟踪，冻结干净
- diff 范围：`git diff --stat 0320a8e..f76e2a9` = `app/scene/spray/decode.py` + `tests/test_spray_adapter.py`，2 文件 +369/-54，S9b 增量口径一致
- 独立隔离：新建 detach worktree @ `f76e2a9`，不动开发树
- 复用证据：TEST-TASK12S-BC-freeze 旧 16 条 40 用例 PASS（快照 `0320a8e` 匹配项）、真实小包探针锚（独立 rclpy 计数 1184 消息/44 scan 结束/44 PCD、源包 sha256、镜像 `rosbag-spray-runtime:20261013`）；不重复已通过旧 B 全仓
- 本单口径：镜像内真实调用 `decode_packet_route`，核 44 PCD 逐帧原始整数结束 storage_ns 与 DB3/message 范围一致、源包摘要不变、旧 DECODE_FAILED 已替换成功；新增矩阵（多 DB3/重复/缺帧/首尾不完整/映射歧义/取消）核实际断言；无真实模型/NAS 发布/生产写入
- 交付：`test-receipts/TEST-TASK12S-B-s9b/attempt-1.md`；FAIL 回 B 最小修复，不改业务实现，不批准合入