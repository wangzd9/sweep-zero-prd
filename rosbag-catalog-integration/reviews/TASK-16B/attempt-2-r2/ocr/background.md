# TASK-16B attempt-2-r2 OCR 背景

## 交付
base `40ab818`（r1 冻结，已机械核验+OCR 0 findings）→ head `e152465`（r2，C 16:45 交付）：`scripts/scene_host_proxy.py`（+171/−43 业务面）+ `tests/test_scene_host_proxy.py`（+378 故障注入，排除挂 TESTER/协调者复跑已 39 passed）。

## 触发
强审 `SR-16B-R1-20261013`（call `e7d6b921`）结论 REWORK_REQUIRED，5 项 CORRECTION 全部指向 r1 修复面的**边界情形**（r1 修对了主路径但收尾/对账语义有缝隙）：

- **R1-01 [高] H1 单写者**：首个 worker 结束移除 ACTIVE 后，迟到重复 /run 可再次 try_reserve→202+二次 spawn（=同 attempt 重烧模型）。修复=终态对账：已终态 run 的迟到请求不得重执行
- **R1-02 [高] H2 终态必达**：终态 post() 失败只打日志，随后清 recovery=步骤永久卡 RUNNING。修复=清理可恢复状态前对失败终态写入按 attempt 对账补报（覆盖"已提交但响应丢失"+"未提交"两分支）
- **R1-03 [高] H4 失败恢复**：_finish_failure 吞 SCENE_FAILED 上报异常仍删 recovery+移 ACTIVE。修复=区分已确认终态与状态不确定，先对账再决定是否清台账
- **R1-04 [中] H4 收尾顺序**：clear_recovery_state 的 unlink 非 FileNotFoundError 异常中断收尾→ACTIVE 幽灵残留。修复=活动位释放在清理异常下仍执行
- **R1-05 [中] H6 台账耐久**：_write_json_atomic fsync 了 tmp 未同步父目录，首次创建台账掉电可丢目录项。修复=replace 后 fsync 目录

## 审查重点（增量）
1. R1-01~05 各修复是否引入**新的**状态缝隙（对账补报本身失败怎么办、终态判断的竞态窗口、fsync 目录在不可支持文件系统的降级路径）
2. r1 已修 6 处（H1-H6/L1）语义不得回退
3. 单写者/恢复/recovery 真相源三者在 r2 后的组合闭环
4. 强审明确不扩的面：try_reserve 失败后重读 ACTIVE 返回 200 无独立反例（不审）、except Exception 范围已认可（不扩）

## 验证证据
协调者独立复跑：proxy+orchestrator 定向 **39 passed**（28.52s）+ ruff 绿。

## 非本次范围
orchestrator 本批零改动（diff 确认）、算法面、12S-C 接线面（C 另一交付 `92dcb52` 已独立 OCR 双零 findings）。