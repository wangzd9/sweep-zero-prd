---
task: TASK-06B
item: attempt-1-defect3-reconcile-replay
owner: 2号
status: REVIEW_PENDING
commit: 4e2158e（单 commit）
base: main 0f6aa87
branch: scene/task-06b-defect3-reconcile-replay（wt-04a）
delivered: 2026-10-10 21:05 +08:00
---
# 回执：缺陷3 reconcile 幂等二次 MySQL StaleDataError

## 文件清单（零越界）

- `app/services/scene_result_report_service.py`（+27/-3，单文件，app 代码面）
- 未改任何测试断言、未删用例、未动 complete 路径。

## 根因（已实证闭环）

`bag_record.updated_at` 为 **DATETIME(0) 秒精度**（`SHOW COLUMNS` 实测 + 迁移 DDL 无
fractional），MySQL 写入四舍五入落库。reconcile 幂等二次（reconcile-2）时 6 个业务字段
（availability/relative_path/started_at/duration_ns/message_count/total_size_bytes）已全部
收敛，旧代码仍无条件 `child.updated_at = local_now()` → flush 只剩**单列 updated_at 的
UPDATE**；同秒内两次 reconcile 的 `local_now()` 微秒不同但 round 后落库同值 →
MySQL `affected rows=0`（无 CLIENT_FOUND_ROWS）→ ORM `check_rowcount`（单行 UPDATE 恒
True，`persistence.py:871/946`）抛 `StaleDataError: UPDATE statement on table 'bag_record'
expected to update 1 row(s); 0 were matched`。SQLite 对同值 UPDATE 恒返回 1 → 本地全绿遮坑
（与 R2-02 双引号方言同类教训）。

与 TESTER 取证吻合：echo `1801`（reconcile-1 多列 UPDATE，`updated_at=20.566585`）/
`1908`（reconcile-2 单列 `UPDATE bag_record SET updated_at WHERE id=2`，`20.584041`，
同秒 `:20`）+ 探针（新连接同语句 affected=1 因跨秒/行存在）。

## 修复（派单方向 1+2 结合，最小）

`_mark_children_available` 在赋值前捕获 6 个业务字段原值 `old`；赋值后比较，**仅当确有
业务字段变化时才推进 `updated_at`**。已收敛的幂等重放 → no-op 零 UPDATE，reconcile-2 收敛
成功返回 200（REQ-06 幂等登记契约）；有变化时正常多列/单列 UPDATE 且 affected rows=1，
不受本修复影响。选择依据：方向 3（CLIENT_FOUND_ROWS）影响全仓 rowcount 语义，派单明确
"慎用"，且本缺陷因果范围仅限 06B reconcile 幂等重放，最小面即方向 1 的收敛检测。

同文件 `complete` 重放路径自查：complete 终态分支不调用 `_mark_children_available`（仅
reconcile 走该函数），无同类 no-op 风险，未扩改。

## 命令 / 退出码 / 环境 / 关键断言 / 证据

环境：wt-04a（`/home/wang/.local/state/rosbag-scene/wt-04a`），branch
`scene/task-06b-defect3-reconcile-replay`，HEAD `4e2158e`，base `0f6aa87`；venv
`/home/wang/work/rosbag-catalog/.venv`（sqlalchemy 2.0.41 / pymysql 1.4.6 / pytest 8.4.1 /
python 3.10.12）。真实 MySQL 8.4.11 = 本机 docker `rosbag-catalog-local-mysql-1`
（172.20.0.6，隔离库 `b_defect3_verify`，root 直连）。

1. **真实 MySQL A/B（AC1 核心证据）**——脚本 `/home/wang/.hermes/cache/scratch/b_ab.py`
   （剥离 CLIENT_FOUND_ROWS 引擎 `client_flag=0x3aa20d`，匹配 TESTER 实际条件；FK 检查会话级
   关=TESTER 同款 teardown 兼容，不改仓库测试）：
   - 旧代码（git stash 回 0f6aa87 文件）：`test_reconcile_backfills_after_publish_without_report`
     **FAILED**，`persistence.py:948 StaleDataError: expected to update 1 row(s); 0 were matched`
     （RC=1）——缺陷复现。
   - 修复代码（4e2158e）：同用例 **1 passed**（RC=0）——reconcile 幂等二次收敛返回 200。
2. **单列 no-op 直接探针**（b_ab.py 内置）：stored `19:57:20` 写 `19:57:20.400000`（round 回
   :20 同值）→ 剥离 flag 后 `StaleDataError`（rowcount=0）；默认 flag（含 FOUND_ROWS）下
   rowcount=1 不抛——证实差异源=CLIENT_FOUND_ROWS。
3. **SQLite 定向**：`.venv/bin/python -m pytest tests/test_scene_result_report.py -q` →
   **31 passed**（AC2）。
4. **全量**：`.venv/bin/python -m pytest -q` → **822 passed**，3 failed（`test_devflow.py`
   沙箱环境性=main 基线同集，独立复跑 3 failed/21 passed 确认与本改动无关），10 skipped
   （`test_bag_cleanup_mysql.py` 独占容器验收），7 errors（`test_r2_repro.py` 需
   `/tmp/r2-review-*` 隔离库，wt-04a untracked 既有，非本次产出）。
5. **ruff**：`.venv/bin/ruff check app/services/scene_result_report_service.py` →
   **All checks passed**（AC2）。
6. **零越界**：`git diff 0f6aa87..HEAD --stat` → `1 file changed, 27 insertions(+), 3 deletions(-)`
   （AC3）。

## 未执行项 / 越界申报

- 未跑 OCR（协调者串行）、未合入 main、未自标 DONE。
- AC1 的 TESTER 独立复测（本用例真 MySQL 8.4 新 attempt）未跑——待协调者合入后派 TESTER。
- 无越界；隔离库 `b_defect3_verify` 与探针表为临时材料，用完即毁（隔离库 b_defect3_verify+用户 bdef3v 已清理，宿主机 0 残留）。