# 派单：TASK-16B attempt-2-r2（强审 SR-16B-R1 5 项阻塞最小返修）

- status: DISPATCHED
- 派单时间：2026-10-13 15:2x +08:00（协调者 r162）
- owner：C（3号，16B 原 owner）｜attempt：attempt-2-r2（base `40ab818` 续 commit，不新开分支）
- base：`40ab818`（wt-03b-t16b，attempt-2-r1 交付冻结，机械核验全绿+增量 OCR 0 findings 在案）
- 触发：强审 `SR-16B-R1-20261013`（call `e7d6b921`，授权 grant `6b2d83fb9` 内）**REWORK_REQUIRED**：5 项阻塞全 CORRECTION（R1-01/02/03 高、R1-04/05 中）。结果全文 `reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/result.md`（逐条含代码位置/触发/最小修复边界/解除条件，先读它）。
- 与 12S-C 前置的关系：本单优先于 12S-C 编码推进——12S-C 接线核验本就依赖 16B 接受；12S-C 前置可暂停等待（worktree `wt-03b-t12sc` @ `22ffb71` 冻结不动），r2 交付后再续，不另派单。

## 一、返修项（5 条，逐项按强审 result.md 的最小修复边界）

- **R1-01 [高] H1 单写者**：首个 worker 结束移除 ACTIVE 后，迟到重复 /run 可再 try_reserve 启动第二线程（=同 attempt 重烧模型）。修复=保留后执行资格与 Backend 当前 run/attempt 及已接受身份对账，**已终态 run 不得重执行**。注意：强审已核「try_reserve 失败后重读 ACTIVE 返回错误 200」无独立反例（释放后读空→409），不要扩该面。
- **R1-02 [高] H2 终态必达**：RUNNING 落库后终态 post() 失败只打印不重试，随后清 recovery=步骤永久卡 RUNNING。修复=**清理可恢复状态前**对失败终态写入按本 attempt 对账补报，覆盖「已提交但响应丢失」与「未提交」两种注入。
- **R1-03 [高] H4 失败恢复**：_finish_failure 吞 SCENE_FAILED 上报异常仍删 recovery+移 ACTIVE，Backend 短时不可用时 run 停 SCENE_RUNNING 且重启失恢复入口。修复=区分已确认终态与状态不确定，**先对账再决定是否清恢复台账**，两分支（上报未提交/响应丢失）注入。
- **R1-04 [中] H4 收尾恒执行**：clear_recovery_state 的 unlink 非 FileNotFoundError 异常中断收尾→ACTIVE 幽灵残留挡后续 /run。修复=活动位释放在清理异常下仍执行+保留清理失败恢复依据，注入 unlink 抛错验证。（except Exception 范围强审已认可，不扩不改。）
- **R1-05 [中] H6 台账耐久**：_write_json_atomic fsync 了 tmp 未在 os.replace 后同步**父目录**，首次创建台账掉电可丢目录项=已 202 的 run 不可恢复。修复=replace 后 fsync 目录+调用顺序测试（文件及目录 fsync 次序），掉电语义 docstring 限受支持文件系统。（同 PID tmp 名冲突强审未立阻塞项，不扩。）

## 二、自测/证据
- 5 项各带故障注入回归（按强审解除条件：R1-01 快速完成后重发+释放边界交错证明只执行一次；R1-02/03 两分支注入收敛；R1-04 unlink 注入 ACTIVE 不残留；R1-05 fsync 顺序断言）。
- 既有 20 passed 零回归 + 全仓口径同 r1（base 既有失败集对照）+ ruff 全过。
- 零越界：只动 `scripts/scene_host_proxy.py` + `tests/test_scene_host_proxy.py`，不碰 orchestrator/fake_vlm/app 面/迁移/12S-C 文件。

## 三、交付物
- 冻结 commit（续 `c/task-16b-scene-host-proxy` @ `wt-03b-t16b`）+ 回执 `receipts/TASK-16B/attempt-2-r2.md`（R1-01~05 逐项：修复说明+注入证据表）。
- 收口链：机械核验→**返修增量 OCR 固定入口**（`--from 40ab818 --to <新head>`，单业务文件小增量）→**强审增量复审**（只看 R1-01~05 问题 ID+修复 diff+注入证据，授权期限内 60min 剩 4/5）→TESTER 收口（r1 口径）→合入 main→16B DONE→**重算 12S-C 依赖**。

## 四、ACK 时限
- 30min 内 ACK（`inbox/3号/TASK-16B/attempt-2-r2-ack.md`）；12S-C 前置暂停期间无第二单，直接接。