# 回执：TEST-TASK06-r2-final-mysql-e2e attempt-5
> **连接语义纠错（2026-10-11 13:55 协调者，据 codex 第七轮 B-01）**：本文件所称
> "PyMySQL 生产默认连接/生产默认语义"均指**无 CLIENT_FOUND_ROWS 隔离连接**（裸 pymysql.connect 无 client_flag，changed-rows 语义）；生产实际默认建连
> （SQLAlchemy 2.0.41 + PyMySQL 1.1.1）默认 client_flag=2 带 FOUND_ROWS，同值 UPDATE 返回
> matched rows=1。本文件证据只验证 changed-rows 连接下的修复行为，**不外推生产默认连接**。
> 详见 reviews/codex-r10-finalstate-20261011-verdict.md。


- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e-attempt-5.md`（协调者 09:44 下达，TESTER 09:52 ACK）
- 状态：**TEST_REPORT_PENDING**（待协调者验收）
- 被测 base：main `4697be0`（= origin/main，09:44:51 推送，开工前 git 复核 HEAD 一致，工作树无 app/tests 未提交改动）
- 环境：真实 MySQL 8.4.11 隔离容器（镜像 `6ea90827b110`，net `tester-r2net5` 172.22.0.2，宿主 33072，
  隔离库 `t_r2app5`/`t_r5dbg`/`t_r5ac2`），主仓 `.venv` Python 3.10.12，PyMySQL 生产默认连接语义
  （`ssl={"ca": None}` 无 flag 参数，实测裸连接 flag `0x3AAA0D`，**无 CLIENT_FOUND_ROWS**）
- 结果：**PASS 4/4**
  - AC1（R-01 秒末边界，核心新增）：`tests/test_scene_result_report.py` 全文件真 MySQL **35 passed RC=0**
    （含 `test_reconcile_start_ns_truncates_toward_zero_at_second_boundary` ns末=0/500_000_000/999_999_999 三参数）；
    探针 ns末=999_999_999 走真实 reconcile 链 → 落库 `started_at=22:13:22`（完整值=BASE_S+2 整秒，
    **向下截断不进位到 +3**，旧码 `/1e9` 进位错口径已消除）→ 二次同 body 重放 200 无 StaleDataError，
    `started_at`/`updated_at`/`row_version` 三元组不推进
  - AC2（R-03 零 UPDATE 直接断言）：独立口径=连接层 general_log（非 ORM 监听）；
    initial 后 `TRUNCATE mysql.general_log`，同秒重放（total=36 行）+ 跨秒重放（local_now+1s，total=72 行）
    **`UPDATE bag_record`=0**、无任何 UPDATE 语句、三元组不推进 → 幂等重放零 UPDATE，no-op 与墙钟无关
  - AC3（不回归）：微秒回归用例 + 整秒口径探针（defect3 原形状）各 1 例真 MySQL **PASS**
  - AC4（口径核对）：`git diff 6d30a68..4697be0` = 3 文件 +156/-8，app 行为面**仅 :582 一行赋值**
    `start_ns // 1_000_000_000`，tests 两文件为断言强化——无越界
- 报告：`reports/TASK-06/r2-final-mysql-e2e-attempt-5.md`
- 证据：`~/.hermes/cache/scratch/tester_r5_suite.log`（pytest 全量 35 passed）、`tester_r5_probe.log` +
  `tester_r5_probe.py`（AC1 三探针源码与输出）、`tester_r5_ac2b.log` + `tester_r5_ac2b.py`（AC2 general_log 计数）、
  `tester_r5_mysql.py`（pytest 插件，DATABASE_URL 指向隔离库）
- 清理：容器/网络已毁，宿主 33072 无监听，`docker ps -a` 无 tester 残留（0 残留核实）
- 未执行项：S1/S2/S3/S4/B8c/B8a/r6 与 attempt-3/4 已收口项按派单不重跑；强模型增量复审 R2I-20261010-06
  维持 READY_FOR_USER_TRIGGER（target 随合入更新为 `4697be0`，用户手动触发，不代跑）
- 零业务代码改动；测试材料仅在 `~/.hermes/cache/scratch/`