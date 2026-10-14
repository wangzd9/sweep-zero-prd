# 派单：t10-defect1-source-ready —— 03B 域 source_status DISCOVERED→READY 生产路径（TASK-10 缺口 #1 最小返修）

- status: DISPATCHED
- 派单时间：2026-10-12 00:0x +08:00（协调者 cron poll 00:00:53 回合）
- 任务：TASK-10 端到端闭环缺口 #1（2号取证单 `receipts/TASK-10/attempt-1.md` 定位，协调者独立核验属实）
- owner：1号（A；03B 接收链原 owner，熟悉 source_service/登记/Scanner 身份透传）
- base：main `ca8730d`（= origin/main，2026-10-12 00:0x rev-parse 双核）
- worktree：按先例新建任务专属 worktree（如 `wt-01-t10def1`，.venv 软链主仓）

## 一、缺陷事实（协调者已核，不重查）

- 正式接收链登记的真实源 `source_status` 初始=`DISCOVERED`（`app/models.py:83` 默认；`source_service.py:215` 登记置 DISCOVERED；:459 仅置错误态）。
- `scene_schedule_consumer.py:208` 与 `scene_slice_service.py:167` 均要求 `source_status == "READY"` 才建/认领 SCENE_SLICE run。
- **app+scripts+alembic 全仓 grep `source_status` READY setter 0 命中**（协调者 00:0x 实测）→ 正式登记的真实源永远到不了 scene 链（P0 真实闭环断点，2号 E2E 靠 ORM 手动置 READY 的 harness 前置才驱动到下游）。

## 二、范围（最小修复，不扩）

1. **先核既有隐式路径**：确认是否已有 scanner 确认/指纹稳定等既有机制可置 READY（有→接入；无→补最小生产置位路径）。
2. 在 **03B 登记成功路径**补 `DISCOVERED→READY` 置位：登记 matched+指纹/元数据完整后由正式服务链置 READY（口径按 DESIGN §3/7 接收链语义，**单 commit 最小面**，只动 source_service/登记链相关文件+测试，不碰 05/06B/04B）。
3. 幂等与竞争：重复登记/Scanner 重扫不得把 READY 回退 DISCOVERED；与错误态（:459）语义不冲突。
4. 测试：SQLite 定向（登记→READY 自动置位 + outbox 消费建 run 不再被 :208 拦截 + 幂等不回退 + 错误态不受影响）；涉并发语义真 MySQL 8.4.11 STRICT 隔离库文件级复跑（用完即毁 0 残留）。

## 三、AC（验收口径）

- 正式登记真实源后**无 harness 手动置位**即可建 SCENE_SLICE run（E2E `scratch/t10_e2e.py` 1c2 前置可去掉复验，协调者合入后安排）。
- 定向+全量 SQLite（`--ignore=tests/test_devflow.py`）+ruff 全绿；零越界（diff 范围=登记链+测试）。
- 回执 `receipts/TASK-03B/t10-defect1-source-ready.md`（REVIEW_PENDING）。

## 四、边界

- 不改 06B/05/04B 代码（#2 由 2号并行）；不重启共享栈/不动 NAS 业务目录；发现跨模块依赖→记录回派不自行扩。

## 五、停止条件

交付 commit（单 commit 或最小集）+ 自测证据 + 回执落盘 → REVIEW_PENDING 冻结等协调者核验+OCR+合入。
