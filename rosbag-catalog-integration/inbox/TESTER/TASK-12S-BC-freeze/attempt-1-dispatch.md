# 派单：TESTER 12S-B(0320a8e)+12S-C(92dcb52) 冻结产物前置验证（与 OCR 并行，用户 16:02 加速指令②）

- status: DELIVERED（TESTER 16:5x 交付，TEST_REPORT_PENDING，test-receipts/TEST-TASK12S-BC-freeze/attempt-1.md）
- 派单时间：2026-10-13 16:1x +08:00（协调者）
- 任务：对**已冻结**的 B `0320a8e`（12S-B 16 条返修，不含 S9）与 C `92dcb52`（12S-C 接线前置）**并行**独立验证，不等各自 OCR 收口。正式 12S-D 联调仍等 16B+12S-B 最终接受合入（本单≠联调 PASS）。

## A 面：12S-B `0320a8e`（wt-04a-t12sb，8 文件 +980/−77）
1. **16 条受影响项复验**（S1-S8+T1-T8，B 已修，`0320a8e` 相对冻结 `f62a29c`）：抽 c01/c02 各 HIGH/medium 关键项（S1 valid_frames 模型面、S3 截断 PointCloud2 归一、S4 intensity ROI mask 上色、T1 fail-closed ldd、T7 ASCII off-by-one、T8 tie 唯一最近）独立复跑/断言
2. **真实解码/渲染探针**：用已装镜像 `rosbag-spray-runtime:20261013`（本地在库 `e3fe73534ad8`），对真实只读包跑 `0320a8e` 的 decode+render，记录有效帧数（500KiB 过滤后）、时间覆盖、强度上色是否生效（S4 验证关键）——**这是把 B 面真实算法执行从 NOT_RUN 转 PASS 的第一步**
3. **S9 不预占**：`decode.py:270` 的 `len(pc_ds)!=len(src_msgs)` 在 `0320a8e` 仍在（真实 packet 包会误拒），本单**不判 S9 FAIL**，packet 血缘/帧映射矩阵等 S9 新 head 后补验（口径 `frame-mapping-contract-note.md` 在案）
4. 回归口径：spray 域 + 全仓 base 既有失败集对照，零新增

## B 面：12S-C `92dcb52`（wt-03b-t12sc，27 行业务增量 orchestrator+18/proxy+9 + 470 行测试）
1. **接线模块验证**（前置，非联调）：spray 适配器注册/能力启用、八步派发接线、`scene_capabilities.yaml` spray 段、`incoming/spray` 路由——在 `92dcb52` 冻结面上独立跑接线测试（`test_scene_spray_wiring.py`）+ 断言 spray 接线不破坏 slope 默认（12S-A 已合入的坡道面零回归）
2. **disabled spray 回退风险**（REPORT 点名）：关闭 spray 时 `incoming/spray` 不得被错误调度为坡道；本面给出独立证据
3. 正式联调（真链冒烟+发布+入库）归 12S-D，本单只到模块级
4. 与 C 的 16B-r2 的关系：接线 `92dcb52` 消费 `40ab818`（16B-r1），r2 若改 proxy 则接线核验在 r2 合入后复验受影响项（本单证据对 `92dcb52` 快照有效，head 变动则增量）

## 交付
- 回执 `test-receipts/TEST-TASK12S-BC-freeze/attempt-1.md`（A 面/B 面分段，真实探针证据 commit/只读包 sha256 在案）
- 16:45 前给 A 面（12S-B 真实渲染）中期回执——这是 17:30 停止点判断"真实首包预算"的输入之一
- 环境复用镜像，不重装；只读包不动