# 12S-B 帧映射（S9）契约补充通知（r159）
> 有效派单以 `inbox/2号/TASK-12S-B/attempt-1-rework-s9-dispatch.md`（r160）为准；本通知补充 C 口径：前置模块级编码继续（API 面不变），接线核验单等 17 条返修合入后按 12S-B 新 head 执行，禁正式联调 PASS 口径不变。

# 契约变更通知：12S-B decode.py 帧映射（S9）纳入返修

- 时间：2026-10-13 14:5x +08:00（协调者 r159）
- 关联：`inbox/3号/TASK-12S-C/attempt-1-ack.md`（14:1x ACK，消费基线 `40ab818`+12S-A `77c395b`+12S-B `f62a29c` 固定 SHA import）

## 变更

- 独立环境真实解码发现：packet 路线 scan 消息数≠PCD 帧数（小包 1184→44，`is_last_scan` 边界），`f62a29c` `decode.py` 长度断言对真实有效包必 DECODE_FAILED。**S9 [HIGH] 帧映射契约已补入 B 返修单**（`attempt-1-rework-addendum-S9.md`）：以 scan 结束消息建可追溯帧映射（DB3/message id/源 storage_ns 整数直用，禁 ms×1e6 伪造），跨 DB3/重复/缺帧/首尾不完整显式拒绝。
- 运行环境已就位：`rosbag-spray-runtime:20261013`（本机+处理机 cross-host PASS），真实 decode/渲染不再 NOT_RUN。

## 对 C 前置开发的影响

1. **模块级编码可继续**：C 当前 import 级集成口径不变（`f62a29c` 的 API 面/adapter 注册/manifest 结构本期不随 S9 变，S9 改的是 decode 内部帧边界语义）。
2. **接线核验单（依赖全部合入后）按 12S-B 新 head 执行**：S9 合入后协调者发快照更新；C 的受影响核验面=packet 路线真实包端到端（44 帧映射、storage ns 分段输入），不重写八步。
3. **禁正式联调 PASS 口径不变**（三依赖未合入）；本通知不改变 C 的 §9.2 文件边界。
4. 若 C 在编码中发现 S9 映射契约与 16B dispatch_payload/租约面有接线冲突，按 ACK 口径申报协调者，不单方面改 decode 域。