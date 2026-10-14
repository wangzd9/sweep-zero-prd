# 纠正补单：TESTER TASK-12S-AB 派单错误更正（口径修正，任务不变）

- status: DISPATCHED（更正）
- 时间：2026-10-13 14:5x +08:00（协调者）
- 背景：原派单 `inbox/TESTER/TASK-12S-AB/attempt-1-dispatch.md` 有两处事实错误，按原口径跑会白跑一轮。本单只纠错，**任务范围/验收标准不变**，已跑的有效结果保留复用。

## 更正 1：12S-A 的 worktree 与回执路径
- ❌ 原派单：A worktree `wt-01-t16a`、回执按 `receipts/TASK-12S-A/`
- ✅ 实际：A 的 12S-A 交付 worktree = **`wt-01-t12sa`**（`/home/wang/.local/state/rosbag-scene/wt-01-t12sa`，HEAD `77c395b`，已提交冻结、干净树）；交付回执 = **`inbox/1号/TASK-12S-A/attempt-1-receipt.md`**
- `wt-01-t16a` 是 16A 的旧树，与 12S-A 无关，不要在上面跑 12S-A 验证

## 更正 2：A 无新增 DDL/迁移
- ❌ 原派单：要求"A 涉新表/新列 → 隔离迁移实验"
- ✅ 实际：`77c395b` 的 5 文件（4 app + 904 行测试）**无任何 alembic 迁移文件**，无 schema 变更；`ingest_service.py +320` 是服务层字段绑定，`scene_config.py +49` 是配置 DTO
- 验证口径改为：**冻结元数据在 MySQL 的读写兼容 + 旧行为回归**（用现有真实库的 12S-A 相关表只读核验字段语义），**不为本单造任何迁移工作**；生产历史迁移链核验归 11S 发布门禁（强模型线 G4），不在本单

## 保持不变
- 12S-B 面（`f62a29c` 冻结快照功能验证 + 真实解码/渲染探针 + 7 图 hash）口径正确，继续
- 注意：B 的返修（S1-S9）在 `f62a29c` 之上**续 commit 未冻结**——你验证 12S-B 冻结快照用 `f62a29c` 只读 checkout（`git worktree add --detach` 或直接 `git -C wt-04a-t12sb show` 取文件），**不要在 B 的活树上跑**，避免读到半改代码；返修冻结后的受影响项复验由协调者另派
- 真实环境依赖：解码/渲染探针可复用强模型线已装好的独立 ROS2/PCL/Open3D 环境（`/home/wang/work/.local/spray-runtime/`，14:35 前已跑通真实小包），不要重复装环境
- 回执路径：`test-receipts/TEST-TASK12S-AB-independent/`（新建目录）

## 交付要求
- ACK 写 `inbox/TESTER/TASK-12S-AB/attempt-1-correction-ack.md`（确认两处更正 + 已跑结果哪些保留/哪些需复验）
- 15:15 前给第一份中期回执（12S-A MySQL 读写核验 + 12S-B 冻结快照功能面），完整回执随 B 返修冻结前的最后一轮