# 回执：TEST-TASK06-r2-final-mysql-e2e attempt-4
> **连接语义纠错（2026-10-11 13:55 协调者，据 codex 第七轮 B-01）**：本文件所称
> "PyMySQL 生产默认连接/生产默认语义"均指**无 CLIENT_FOUND_ROWS 隔离连接**（裸 pymysql.connect 无 client_flag，changed-rows 语义）；生产实际默认建连
> （SQLAlchemy 2.0.41 + PyMySQL 1.1.1）默认 client_flag=2 带 FOUND_ROWS，同值 UPDATE 返回
> matched rows=1。本文件证据只验证 changed-rows 连接下的修复行为，**不外推生产默认连接**。
> 详见 reviews/codex-r10-finalstate-20261011-verdict.md。


- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e-attempt-4.md`（协调者 22:50 下达，TESTER 22:51 ACK）
- 状态：**TEST_REPORT_PENDING**（待协调者验收）
- 被测 base：main `6d30a68`（= origin/main，22:46:03 推送，开工前 git 复核一致）
- 环境：真实 MySQL 8.4.11 隔离容器（镜像 `6ea90827b110`，net `tester-r2net4` 172.22.0.2，宿主 33072，
  隔离库 `t_r4app`/`t_r4dbg`），主仓 `.venv`，PyMySQL 生产默认连接语义（实测 flag `0x3AAA0D`，
  **无 CLIENT_FOUND_ROWS**）
- 结果：**PASS 3/3**
  - AC1：`tests/test_scene_result_report.py` 全文件真 MySQL **32 passed RC=0**（含微秒回归用例）+
    探针 reconcile-1（小数秒 start_ns）落库整秒 microsecond=0 / reconcile-2 幂等重放 200 无
    StaleDataError / `started_at`·`updated_at`·`row_version` 均未推进
  - AC2：整秒口径（缺陷3 原形状）抽查 1 例同流程 **PASS**（M-1 未碰坏整秒路径）
  - AC3：`git diff 5f0124b..6d30a68` = 3 文件 +72/-5，app 行为面**仅 M-1 一行赋值**，alembic 仅
    docstring，tests 为用例+注释——无越界
- 报告：`reports/TASK-06/r2-final-mysql-e2e-attempt-4.md`
- 证据：`~/.hermes/cache/scratch/tester_r4_suite.log`（pytest 全量）、`tester_r4_probe.log` +
  `tester_r4_probe.py`（探针源码与输出）
- 清理：容器/网络已毁，宿主 33072 无监听，`docker ps -a` 无 tester-r2 残留（0 残留核实）
- 未执行项：S1/S2/S3/S4/B8c/B8a/r6 按派单不重跑（前序 attempt 已 PASS，AC3 确认 6d30a68 对其无
  行为面变更）；强模型增量复审 R2I-20261010-06 维持 READY_FOR_USER_TRIGGER（用户手动触发，不代跑）
- 零业务代码改动；测试材料仅在 `~/.hermes/cache/scratch/`