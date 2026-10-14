---
task: TASK-06B
attempt: 1-r2-rework
item: c67600d 机械核验证据（化身独立复跑，非采信自报）
status: VERIFIED_MERGE_HELD
output_commit: c67600d320fe3830e81c7210ef4349a679006953
base: eff047921ffbb02c107c1ec6145b30c4a2395de1
verified_at: 2026-10-10 13:2x（Asia/Shanghai）
---
# c67600d 机械核验证据（协调者机械验收化身，2026-10-10 13:18-13:25）

唤醒原因：monitor 指纹变化——wt-04a HEAD eff0479 → c67600d，对应 2号
`receipts/TASK-06B/attempt-1-r2-rework.md`（status=REVIEW_PENDING，13:05）。

## a) commit 范围（零越界，base 正确）

- 单 commit：`git log eff0479..c67600d` = 1；父链 = **eff0479**（当时 main HEAD，`git show` 证实 parent=eff047921…）；commit 时间 2026-10-10 13:07:32 +0800。
- 范围 5 文件 +741/-182（`git diff --stat eff0479..c67600d`）：
  `app/services/scene_publish_service.py`（+41）、`app/services/scene_result_report_service.py`（+628 主体）、`app/services/scene_result_service.py`（+89）、`tests/test_scene_result_report.py`（+123）、`tests/test_scene_result_storage.py`（+42）——全部在 06B 派单 scope（R2-03~11 + B8a 死锁 + R2-05 契约测试改写）。
- 零 .venv/环境产物：`git status` 仅 `?? .venv`（软链）与 `?? tests/test_r2_repro.py`（R2 复现锚，按派单**不进仓库**，确认 `git show c67600d --stat` 不含该文件）。
- merge-tree：`git merge-tree --write-tree --name-only main c67600d` = 干净树（69873b42…，0 冲突）。
- **一处跨任务文件（已申报）**：`tests/test_scene_result_storage.py`（06A 文件）2 个用例从 created_at 语义改写为 R2-05 分配 id 序号语义——回执已显式申报"可独立 revert"，属契约测试同步非产品行为变化。

## b) 独立复跑（化身在 wt-04a 自跑，真实退出码）

| 项 | 命令 | 化身实测 | 自报 |
|---|---|---|---|
| 核心两文件 | `pytest -q tests/test_scene_result_report.py tests/test_scene_result_storage.py` | **50 passed**（rc=0） | 50 passed ✓ |
| 全量 | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q --ignore=tests/test_r2_repro.py` | **805 passed, 3 failed, 10 skipped**（rc=1） | 806/3/10（自报含本地 repro 文件 1 用例，--ignore 后 805，差 1 即该文件）✓ |
| 3 failed 定性 | 同上 | 全为 `test_devflow.py` 沙箱环境性（worktree `.git` 是文件非目录，bubblewrap 无法构造沙箱）= 已知 3 个，**非回归** | 同（stash 基线同 3 failed）✓ |
| ruff | `ruff check app tests` | **All checks passed**（rc=0） | 同 ✓ |
| R2 repro 8 断言（隔离库） | `DATABASE_URL=sqlite:////tmp/r2-review-*.db DEMO_DATA=1 pytest -v tests/test_r2_repro.py` | **8 passed / 8 条全部反转**（rc=0，13:2x 化身跑） | 8 passed ✓ |
| MySQL 8.4.11 真实 5 场景 | `.venv/bin/python /home/wang/.hermes/cache/scratch/r2_switch_mysql.py`（独立隔离 schema+临时用户，跑完 DROP，化身自跑） | **5/5 PASS**：首切 1093 消除 / 重放 no-op 恰一 current / 并发恰一 current=3（一方 409）/ 旧版晚到 409 保 5 / 冲突 409 保 6；`mysql_version=8.4.11`、`cleanup_rc=0`（rc=0） | 5 场景 PASS ✓ |
| B8a 死锁回归 | 在 50 passed 内：`test_multi_scene_run_partial_complete_does_not_deadlock`（tests/test_scene_result_report.py:1033） | 通过 | 通过 ✓ |

注：化身首轮全量未 --ignore 本地 `tests/test_r2_repro.py`，出现 7 个 setup error（该文件 fixture 强制 `/tmp/r2-review-*` 隔离库、不进仓库）+ 806 passed；排除后干净数字 = **805 passed / 3 failed（devflow 环境性）/ 10 skipped**，该 3 failed 与基线 eff0479 同集。

## c) 合入判定（本轮不 merge——非验收失败）

机械核验 **PASS**，但两项硬门禁未满足，化身不代裁决：

1. **fresh 模块禁机械合入红线**：c67600d 是 R2 强模型返修新代码（+628 主体重写），**无 c67600d 范围 OCR 收口记录**（B8a 只覆盖 attempt-1-rework 的 6e6bb73 app 6 文件；c67600d 的 3 个 app 文件全部重写）。
   → 化身已按红线处置：13:21 flock ocr.lock 代跑 B8c `ocr review -c c67600d --audience agent`（后台，日志 ocr-c67600d-06b.log，B8a 先例 ~1h 量级），**收口后 findings 处置 + 合入与否交主会话**（high/critical 不得收口）。
2. **R2-05 跨任务契约合入时序**：回执显式申报 c67600d（switch 侧）与 1号 f088c2b（create 侧）契约互锁、"建议同批合入，协调者确认两侧 commit 时序"；而 f088c2b 现挂 `inbox/coordinator/TASK-03B/NEEDS_MAIN_REVIEW.md`（12:35）未合入——两侧合入顺序属**跨任务契约裁决**，化身禁项。

## d) high finding 核实与判定（主会话 14:01 裁决 + 化身证据补全）

- B8c r1 的 [security · high]（publish:155-156）**主会话 14:01 对照 c67600d 源码核实=真缺口（非误报）**：
  OCR 定位有偏差——`_SAFE_VEHICLE_KEY_RE` 常量在 c67600d 中**不存在**（OCR 把 publish:155-156
  的**内联正则** `re.fullmatch(r"[A-Za-z0-9._-]{1,128}", vehicle)` 误命名为常量）；
  该字符集放行 `..`/`.`/`..x`，`publish_root/".."/…` 解析到受控发布根之外，
  且 vehicle 段取 payload 自报值（`_effective_vehicle_key` 注释声称继承父包但路径口径仍自报）。
  与 B8a medium #3 同域、R2 漏网（与 R2-08 同域）。
- **主会话裁决=回派 2号小修（有界第 1 轮内并入 c67600d 返修）**：车辆段改继承父包受控记录
  （BagRecord.vehicle→Vehicle.vehicle_code 非空用 code，否则 unassigned），publish/report/reconcile
  三处同一口径，保留字符集校验+所有拼接点显式拒绝 `.`/`..` 段，回归四例+路径不逃逸断言。
  decision：`inbox/coordinator/TASK-06B/attempt-1-r2-rework-decision.md`；
  派单：`inbox/2号/TASK-06B/attempt-2-r2-rework-dispatch.md`（14:3x 化身代笔，修复方向以主会话裁决为准）。
- 化身不代改业务代码（v2 skill：代码问题回派 owner）；化身本轮补全的测试证据见上 a/b 节。

## 化身本轮未做

- 未 merge、未 push、未改任何业务代码；
- 未跑 B8b（仍待主会话裁决）；
- OCR 后台进程（pid 见 ocr-c67600d-06b.log 头部）持 ocr.lock 至收口，下轮 monitor 指纹变化时化身先查 `ps + 日志` 收口状态再动。