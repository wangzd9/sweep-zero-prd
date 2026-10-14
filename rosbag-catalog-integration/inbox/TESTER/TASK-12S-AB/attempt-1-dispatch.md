# 派单：TESTER 12S-A/B 独立验证（并行，不等 OCR）

- status: DISPATCHED
- 派单时间：2026-10-13 13:5x +08:00（用户群内授权"加速"——TESTER 快照已冻结，验证与 OCR 串行门解耦）
- 任务：对 12S-A（原始信息绑定）与 12S-B（水雾能力）的**已冻结交付快照**做独立验证（功能/回归/证据面），与 OCR 审查并行推进，不重复 OCR 的职责。
- owner：TESTER（独立测试槽，当前空闲）
- **固定快照（不可移动，以回执为准）**：
  - 12S-A：worktree `wt-01-t16a`，base `6fb42c4` → head `77c395b902f8b8b57276ac509e1c2dcc5ab26e90`（回执 `receipts/TASK-12S-A/attempt-1.md`）
  - 12S-B：worktree `wt-04a-t12sb`，base `6fb42c4` → head `f62a29c`（回执 `receipts/TASK-12S-B/attempt-1.md`）
- 依赖口径：本单验**已冻结产物**，不依赖 12S-C/16B 合入；OCR 出 CORRECTION 级返修后若 head 变动，本单结论失效、由协调者决定增量复验范围，不自动重跑。

## 一、验证范围（按 ACCEPTANCE v0.5 + 各卡 AC）

### 12S-A（source_metadata/API/快照/车辆绑定，新增 spray profile，不改坡道默认）
1. 独立复跑交付方申报的定向测试（`tests/test_scene_spray_intake.py` 904 行）+ 全仓 `pytest -q`（worktree 固定 3 个 test_devflow 环境性失败除外，申报归属）
2. 迁移面：`ingest_service.py +320`/`scene_config.py +49` 涉新表/新列 → 隔离 MySQL 8.4 实跑 `alembic upgrade head`（本单**有 DDL**，SQLite 绿不算数）；upgrade/downgrade/re-upgrade 往返
3. spray profile 注册：`scene-isolated` 既有坡道默认**不被改动**（对比 base 与 head 的 profile 快照 hash）
4. 车辆绑定/原始信息字段：API 返回 source_metadata 完整性、缺失字段 fail-closed 不猜
5. 旧坡道/自建/英伟达记录**零回归**（既有 /sources/register、/ingest-submissions 行为面）

### 12S-B（点云解码/渲染/整数 ns 分段 spray 适配器）
1. 独立复跑 `tests/test_spray_adapter.py`（952 行）+ 全仓 pytest
2. 整数 storage ns 映射：decode 输出可追溯输入消息 ID/DB3 文件/存储 ns（**不把 ms×1e6 冒充源 ns**——重复/歧义须拒绝）
3. PCD 解码：PointCloud 字段布局/型号/SDK/PointField 偏移/padding/row_step/字节序预检正确性（用 1012 只读小包做转换/渲染探针）
4. 双 pass 判定（SPRAY_SYSTEM/SPRAY_PROMPT_V18 + SIM）：pass1 明确异常直接判异常，否则 pass2 参考图编号
5. 7 参考图 hash 校验（`references.py`）：内容摘要+顺序与冻结清单一致
6. 异常归一：未知/空图/空模型→FAILED（非 NO_MATCH）；缺 topic→不适用；缺图/非零 converter 返回→明确错误
7. 合成已知命中 + 正常样本自洽

## 二、口径与边界
- 只读交付快照 + 隔离测试库/临时工作目录，**不碰生产/处理机/NAS 生产路径/业务库**
- 本地 real 栈如需，走测试根 `/test/scene/*`、`/home/wang/work/.local/rosbag-catalog/scene-work`
- 模型请求：12S-B 渲染/判定探针可用**只读本地短包 + 合成样本**；真实 VLM 付费调用留 12S-D（不从本单推导付费）
- 不重复 OCR 审查职责（findings 归属协调者裁决+owner 返修）；本单只产出"功能/回归/证据"维度的 PASS/FAIL + 证据
- 发现 CORRECTION 级缺陷：回执标 BLOCKED + 定位文件:行 + 复现命令，不代修

## 三、交付物
- 回执 `test-receipts/TEST-TASK12S-AB/attempt-1.md`（PASS/BLOCKED/FAIL 分 A/B 两段，含定向测试数、全仓 pytest 数、隔离 MySQL 往返证据、7 图 hash 比对、坡道默认不变对比、回归结论）
- 夹具 0 残留申报

## 四、与 OCR 的关系
- 本单与 12S-B/A 的 OCR 批次**并行**（不同执行者、不同槽），OCR findings 收口后若触发返修改 head，协调者再决定增量复验
- 本单 PASS 是 12S-C 接线 + 12S-D 的前置证据之一，不单独构成合入放行（合入仍需 OCR 零 CORRECTION + 协调者核验）