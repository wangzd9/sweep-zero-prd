# 派单：TASK-07B 07B-post-r 合入后独立验证（07B 整链收口前最后一环）

- status: PENDING（待 ACK）
- 派单时间：2026-10-13 07:4x +08:00（协调者 coord poll 14ae4556629a，r133）
- owner：TESTER
- 任务：TASK-07B attempt-4-r4 交付收口后的 07B 整链独立验证（SR-05 既定口径 + R4 迁移面）
- 被测 target：**`62620a3ddc5cfa614c5e72681c852c96d60507b3`**（`scene/task-07b-manual-revision-withdraw` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07b`，R4 交付冻结 HEAD；base `4baf79f` 之上单 commit）
- 整链 origin base：`502bf8e`（未合入，待 TESTER PASS 后协调者 --no-ff 合入，07B 先于 16A rebase 双头）

## 一、验证范围（07B 合入门禁剩余证据）

1. **SR-05（R2 强审 `50c665e4…` 高 VERIFICATION_GAP，既定口径，target 已固定）**：真 MySQL 8.4.11 隔离库，**双连接同版本无关联子切片并发纠错**——初始 `bag_scene` 关联不存在、两请求读同一 `row_version`，发同代次请求核验：恰一方 200、另一方 409（不得 500/StaleDataError/唯一键异常），版本只 +1，审计行与 MANUAL evidence 各一行。SR-02 修复面（`_guarded_bump_row_version` 前置到关联 INSERT 之前）在此取证。
2. **R4 迁移面（R4-1/R4-2，target `62620a3`）**：
   - 正常态：真 MySQL 8.4.11 隔离库 fresh `upgrade head` → `downgrade -1` → `upgrade head` 往返 RC=0（SHOW COLUMNS 校验双表 corrected_label），容器 0 残留。
   - 表缺失态：SQLite 内存 + 真 MySQL 双库，`create_all` 后 DROP `scene_manual_revision` → 跑 downgrade **不抛异常**（R4-1 守卫生效断言）。
   - （范围说明：协调者 r133 裁决 `inbox/coordinator/TASK-07B/r4-01-adjudication-20261013.md` 已将「审计表缺失+evidence 列存在」合成态的 evidence 列 drop 判定为既定接受语义（docstring 已文档化，非本单验收项）——**无需**验证该合成态 evidence 列保留；本单只按上述正常态/表缺失态双库探针取证。）
3. **07B 定向回归不回归**：`pytest tests/test_task07b_manual_revision.py tests/test_task07b_r2_revision.py tests/test_task07b_r3_revision.py -q` 全绿（target 工作树口径）；页面实测（纠错/下架入口 + 详情「当前人工标签」+ 审计「修正为」列）07B 面不回归。

## 二、口径
- 真 MySQL = `docker.m.daocloud.io/mysql:8.4` 独占容器 + 独立 docker 网络（无宿主端口映射），用完即毁、0 残留；自包含 uvicorn 独立端口 + 临时 SQLite 夹具（DEMO_DATA=0），不触碰共享 real 栈/容器/宿主代理/生产。
- 独立取证（不复用 B 回执/协调者探针作为本单证据；可参考其命令形态）。
- 交付：`test-receipts/TEST-TASK07B-post-r/attempt-1.md`（PASS/FAIL + 逐条证据：命令/退出码/环境/断言/残留核）。

## 三、收口
- **PASS** → 协调者写 07B 整链合入（--no-ff，07B 先于 16A 迁移 rebase 双头）→ 07B DONE → 派 07C/16C。
- **FAIL** → 回派 B 定位（SR-05 并发面/迁移面，不跨模块）；同根因两轮失败升级用户。
- 本单不扩大 07B 需求面（冻结 AC=强审包 §2(1-6)+R4 派单 §二边界）。

- 已 ACK 前请落 ACK（`inbox/TESTER/TASK-07B/post-r-ack.md`）；独立验证中不催单。