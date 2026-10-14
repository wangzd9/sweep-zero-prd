# 派单：TASK-10 attempt-1 目录→坡道切片→数据库→API 获取真实工程闭环（P0 收尾单）

- status: DISPATCHED
- 派单时间：2026-10-11 21:5x +08:00（协调者 cron poll 回合）
- 任务：TASK-10（REQ-01～10、13 的 P0 部分 / 对应 AC 的 P0 部分），前置依赖 TASK-08 DONE ✅ + TASK-09 DONE ✅（21:5x 收口）
- owner：2号（B，wt-04a；TASK-09 原 owner，熟悉真实 NAS 切片+VLM 接线，交付冻结转空闲）
- base：main `ca8730d`（= origin/main，21:5x rev-parse 双核一致；TASK-08/09 全链已合入，无在途漂移）
- 性质：**P0 最后一张业务单**（真实工程闭环收敛），不是新建任务/扩需求；TODO §3 TASK-10 卡为准。

## 一、上游已就绪的事实（可直接引用，不重探）

1. **本地栈 8 容器 healthy**（backend/frontend/mysql/scanner/orchestrator/bag-cleanup-worker/双代理，Up 35h，21:5x 实测）——接收/调度/执行/回报链在本地可用。
2. **真实坡道样本**（只读）：`/mnt/nas_backup/data_slice/1165414093/slope/` 7 条 db3 在位（~239MB/15s，11279 消息/袋，参考 `/home/wang/work/ros2_slice/slice_message.csv`）；**row19 `1165414093_slope_20260818_105105_105120` 已在 TASK-09 实测 SUCCESS**（可发布区间非空），其余 row20/21 有外部 VLM 单帧确定性 500 缺陷（TASK-11 前置事实，不阻塞本单）。
3. **生产接线已合入 `ca8730d`**（TASK-09）：`vlm.py` 模型 ID 完整路径默认（`/home/sysadmin/data/disk02/jc/models/qwen3.8-27b-fp8`）+ max_tokens 2048 + enable_thinking 透传；`SLOPE_VLM_ENDPOINT` fail-closed（未配置=MODEL_UNAVAILABLE）。VLM 端点 `http://192.168.2.45:8002`（=18002 隧道，**不重启/不改配置**）。
4. **迁移链单头** `20261009_02_ingest_frozen`（TESTER 21:47 真 MySQL 复核 RC=0）；scene-config-v1 / scene-capability/v1 契约已合入。

## 二、闭环内容（端到端，全走正式服务链，不留测试旁路）

以 row19（或另选 1 条 slope 袋，**VLM 预算 ≤1 袋 ~15-16 帧**）为样本，跑通：

1. **目录上传/配置**：用正式 Backend API（03B 接收链）登记指定目录 + 场景/用途配置（scene-config-v1，slope 场景、PHASE0 用途）→ 冻结配置 hash（不得发 NULL-hash 事件）。
2. **真实坡道切片**：04B 适配器链（db3→抽帧→VLM→segment→writer 再切），真实 VLM 调用（预算内），断言 `SUCCESS` + 可发布区间非空 + 区间落在源袋时间范围内。
3. **NAS+数据库**：06B 正式回报/发布链（staging 校验→原子发布→子 Bag 登记→血缘/标签），数据库登记完整（父/子 uid ≤26 字符、当前版本/历史版本）。
4. **API 获取**：经正式 API 查回切片产物（区间证据/父子关系/标签/当前版），可打开、内容合理；**原包（源 db3/NAS 源目录）不变**（只读校验 mtime/大小或 hash 前后一致）。

输出=端到端实际回执：每步命令/exit code/关键响应字段 + 数据库登记证据 + API 获取证据 + 原包不变校验，落 `reports/TASK-10/`；必要风险（VLM 500 帧影响/时间映射边界/未覆盖场景）如实申报。

## 三、AC 核对（验收口径，TODO §3 TASK-10）

- 切片非空可打开 ✓（二.2/二.4）
- 区间内容合理 ✓（二.2 断言 + 二.4 查回）
- 父子/标签/当前版可查 ✓（二.3/二.4 API 证据）
- 获取有效 ✓（二.4 正式 API 响应）
- 原包不变 ✓（二.4 前后校验）
- P0 必要基础完整 ✓（全链走正式服务，不 mock）

## 四、边界与禁止

- **不写 NAS 业务目录**（`/mnt/nas_backup/data_slice` 只读）；产物/缓存只进 run 私有 work_dir 或 `/home/wang/.hermes/cache/scratch/`，用完清理；
- 不动 192.168.2.45 服务本身；VLM 调用 ≤1 袋抽帧口径（~15-16 帧）；
- **不等 UI/其他四类场景/插盘工具/可视化/规模压测**（TASK-07/12/13/14/15 范围）；工程通过 ≠ 生产就绪（质量门禁仍 TASK-11）；
- 发现模块缺陷：**定位+最小复现+记录回派，不跨模块自行改码**（TASK-08 先例口径）；
- 回归：SQLite 定向（scene 全族）+ 全量（`--ignore=tests/test_devflow.py`）+ ruff；涉数据库语义面真 MySQL 8.4.11 STRICT 隔离库文件级复跑（用完即毁 0 残留）；
- 交付 commit 在 `wt-04a` 新分支或 `wt-04a-t10`，单 commit 或最小集；回执 `receipts/TASK-10/attempt-1.md`（REVIEW_PENDING）。

## 五、停止条件

端到端四步全绿（每步有实际命令+exit code+证据落盘）+ 回归全绿 + 隔离资源 0 残留 + 回执/报告落盘。**VLM 500 帧若命中所选袋且无替代袋可用**：换袋一次；仍失败则 BLOCKED 回执（外部服务缺陷，记 TASK-11 前置事实），不无限重试。

## 六、下游

交付后：协调者机械核验（端到端证据逐项+越界核对）→ 串行 OCR（app 面如有改动）→ 验收合入 → **TASK-10 DONE → P0 停止派发**（协调者更新最终 HANDOFF/TODO，不自动转 TASK-11 或后续阶段）。
