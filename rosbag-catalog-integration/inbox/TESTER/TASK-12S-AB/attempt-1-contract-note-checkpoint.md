# 检查点：12S-B 契约变更通知已消费（S9 帧映射）

- 时间：2026-10-13T15:00:15+08:00（TESTER cron `167580c0500b`，owner `cron-tester-poll-167580c0500b-20261013-145453`）
- 关联：`inbox/TESTER/TASK-12S-AB/frame-mapping-contract-note.md`（协调者 r159，14:5x）
- **消费确认**：
  1. 12S-A 侧不变，已交付 PASS（A=`77c395b`）口径维持，不受影响。
  2. 12S-B 侧已交付结论仅对冻结 `f62a29c` 有效；**S9 packet 路线帧映射（`decode.py` len 断言）不按 `f62a29c` 判定 FAIL 收口**——缺陷已由环境面确认（1184 packet→44 PCD，is_last_scan 边界）且 B 返修单 `attempt-1-rework-s9-dispatch.md` 在途。等协调者发 B 新 head 快照后，按新 head 复验 S9 映射矩阵（多 DB3/重复/缺帧/首尾不完整 + 真实包 1184→44）。
  3. 环境升级已知悉：镜像 `rosbag-spray-runtime:20261013`（本地实测在库 e3fe73534ad8），12S-B 后续真实 decode/渲染复验可用该镜像实跑（只读 bag，输出写 scratch/work），不再按缺依赖 NOT_RUN。
  4. 15:15 目标口径已知悉：TESTER 只取证不判水雾阳性/正常段识别质量（算法 owner 面）。
- 本轮实测佐证：`wt-04a-t12sb` HEAD 仍 `f62a29c`、返修脏工作区在途（adapter/decode/precheck/render/references/pcd_io/time_map 未提交 + `tests/test_spray_rework_16s.py` 未跟踪），**TESTER 未触碰**；`decode.py:267` len 断言在冻结 commit 确认在位（与 S9 描述一致）。
- 结论：已交付 `test-receipts/TEST-TASK12S-AB/attempt-1.md`（14:51，TEST_REPORT_PENDING）维持有效；B 面增量复验**未派单不预占不启动**，等协调者新快照 dispatch。
