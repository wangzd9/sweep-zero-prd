---
task: TASK-06B
attempt: 1-r2-rework
owner: 2号
status: REVIEW_PENDING
base: eff0479
output_commit: c67600d
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
updated: 2026-10-10 13:05
---

# TASK-06B 回执（attempt-1-r2-rework，2026-10-10 13:05）

- owner：2号会话（前端功能开发群）
- status：REVIEW_PENDING
- 返修轮次：R2 强模型返修第 1 轮（有界 2 轮，11:31 裁决 REWORK_REQUIRED）
- 集成 base：main **eff0479**（含 2e674b2 本任务 06B 合入，11:31）
- 工作树：/home/wang/.local/state/rosbag-scene/wt-04a，分支 scene/task-06b-r2-rework（自 eff0479 新开）
- output_commit：**c67600d**（5 文件，纯 06B scope；.venv 与 R2 repro 文件均未入 commit）
- 已授权阶段：P0 本地（无生产、无处理机操作）
- OCR/强模型复审：未自跑，请协调者对 **c67600d** 串行代跑（flock inbox/ocr.lock）

## 交付文件（c67600d）

| 文件 | 变更 | 覆盖项 |
|---|---|---|
| `app/services/scene_result_report_service.py` | 大改（+628/-182 内主体） | R2-04/06/07/08/09/10/11、B8a 死锁 |
| `app/services/scene_result_service.py` | +89 | R2-03、R2-05 switch 侧 |
| `app/services/scene_publish_service.py` | +41 | R2-06 path traversal、R2-11 目标复用、B8a 同文件系统校验扩全 specs |
| `tests/test_scene_result_report.py` | +123 | R2-05 契约测试改写、reconcile R2-07 语义、B8a 多场景死锁回归（新增第 25 项） |
| `tests/test_scene_result_storage.py` | +42 | 06A 既有 2 用例从 created_at 语义改为分配 id 序号语义（R2-05 契约同步，非新增） |

## 逐条 R2 对应实现与测试数字

1. **R2-03（HIGH，MySQL 自引用 1093 + 并发双指针）**：`switch_current` 的
   NOT EXISTS 自引用 UPDATE（MySQL 8 报 1093，SQLite 容忍遮坑）改为**标量 COUNT 前置守卫**
   （两后端同义）；写入口（complete-scene 换版事务）锁父包 av 组行 `with_for_update` 实现串行化。
   测试：**MySQL 8.4.11 真实 5 场景 PASS**（独立隔离 schema，跑完 DROP）——
   首切（1093 消除，current=True）/ 同目标重放（no-op 恰一 current）/ 并发首切（双 worker，
   恰一 current=较大分配 id，一方 409）/ 旧版晚到（409 保旧）/ 冲突保旧（result 不一致 409 current 不动）。
   另 SQLite 并发 stale-read 用例（test_concurrent_first_switch_no_double_pointer）改写为 R2-05 语义后仍验证恰一 current。
2. **R2-04（HIGH，终态与换版非同一事务 → 永久非 current 被 200 掩盖）**：
   `complete_scene` 重写——终态 commit 前完成换版，同事务收敛；complete 重放核对原 manifest
   内容身份（digest 16 位，不再只比 outcome），回显真实 switch 状态；重放发现终态但换版未完成时
   实际重试补换版（`_replay_switch` 带收敛逻辑，"幂等重放"不得隐藏未完成步骤）。
   测试：R2 repro 反转 3 条（终态重放/内容身份核对相关）+ B8a crash-window 同域覆盖。
3. **R2-05（HIGH，switch 侧换版裁决字段）**：`switch_current` 版本先后裁决从 created_at 改为
   **av 行分配 id 序号**（与 1号 R2-05 create 侧契约逐字一致；契约注明"版本行在 run 创建事务
   提交时分配，id 序号与创建先后严格一致"）。测试：
   - test_late_old_version_no_rollback（改写为 id 序号语义：删旧行重建为更小编号占位 → complete 409 保新）PASS；
   - R2 repro 反转 test_late_old_event_run_keeps_new_current（旧事件 run 按契约预分配版本行 → 后 complete 409，新 current 不动）PASS；
   - 06A 存量 2 用例同步改写（见交付文件表）。
4. **R2-06（HIGH，空文件+空哈希过校验）**：`_verify_published_files` 实际打开 db3 校验
   非空 + sqlite3 可读 + 消息数 >0 + topic 集合与 per-slice manifest 记录一致 + 区间身份
   （消息 MIN/MAX(timestamp) 落在记录存储域窗口内）；vehicle_key 限定安全字符集
   `_SAFE_VEHICLE_KEY_RE`（拒绝 `..`/`/` 等，防 path traversal——B8a OCR 新增 high 同域合并）。
   publish 侧 `_target_matches` 复用目标同样要求 digest 完整一致。
   测试：R2 repro 反转 test_empty_published_db3_rejected（空包 0 字节 + 空哈希 → 409 INCOMPLETE，
   complete 事务整体回滚、子包不进 AVAILABLE）PASS；topic 不一致/消息数不符用例 PASS。
5. **R2-07（HIGH，reconcile 按父包前缀扫全部版本 → 历史合法切片 409 混合版本）**：
   `reconcile_scene` 读取记录前按本 run 筛选——`BagDerivation.run_id == 本 run` 为主锚，
   无 derivation（首次 reconcile 尚无登记）时退化为记录内嵌 run 身份过滤；历史记录保留不参与
   digest 等值判断。测试：R2 repro 反转 test_reconcile_ignores_historical_versions
   （两代 reanalysis 切片共存目录 → 本 run 正常补登记，历史不误对）PASS。
6. **R2-08（HIGH，manifest 身份被 run_id/source_id 静默覆盖 → 比较恒真）**：
   `parse_report_manifest` 不再覆盖原始身份字段；新增 `_verify_source_identity`——
   外层请求代次 == 冻结 run 快照代次 == manifest 代次 == 父包当前代次**四方相等** +
   按源身份契约核对指纹；不覆盖不猜测。reconcile 恢复路径同样走身份校验。
   测试：R2 repro 反转 test_stale_run_rejected_by_generation_check（旧代次 run 200/current 复现路径 → 409）PASS。
7. **R2-09（HIGH，未领取 run 无 token 直接过租约校验）**：场景写边界改为——非终态 run 必须处于
   允许执行状态 + `require_valid_task_lease` 真实 token 验证（`lease_token_hash` 为空直接 409，
   不再 `return` 放行）；终态 run 只允许已验证内容身份的只读幂等回显；reconcile 恢复入口
   （无租约）加独立可信身份/范围约束（源围栏 + 四方代次 + run 类型），不改共用函数历史语义。
   测试：R2 repro 反转 test_unclaimed_run_rejected_and_genuine_worker_ok（未领取 409、
   错 token 409、合法执行者 200）PASS。
8. **R2-10（HIGH，AVAILABLE 子包 relative_path 仍 06A 占位、无 BagFile/BagTopic 索引）**：
   `_mark_children_available` 与 `_slice_records_of` 幂等回填——真实发布逻辑路径
   `{publish_root}/{vehicle_key or "unassigned"}/{scene_code}/{slice_key}/`（与发布层逐字同口径，
   保证指向实际发布目录）、BagFile（sequence_no/file_name/file_size_bytes，存在则更新不重复建）、
   BagTopic（name/message_count）、child.message_count/total_size_bytes、derivation 产物关联；
   回填与 AVAILABLE 推进同一事务（不得先 AVAILABLE 后补索引）；车辆元数据继承分离到
   `child.vehicle_id`（父包 vehicle 非空时）。重放幂等（索引按 bag_id+file_name/topic 名 upsert）。
   测试：R2 repro 反转 test_available_child_has_published_file_index（complete 后 child 有
   BagFile/BagTopic、message_count>0、路径存在且指向同一 db3、重放无重复索引）PASS。
9. **R2-11（MEDIUM，move 成功后重试原 specs 先 stat staging → FileNotFoundError）**：
   `publish_scene_slices` 优先核验已存在目标——digest + 完整身份一致则**复用**（不要求 staging 在），
   目标内容不一致 → PUBLISH_CONFLICT（不覆盖不清掉）；真正需要 move 时才要求 staging；
   缺 staging 且缺目标 → PUBLISH_BLOCKED；同文件系统校验从 specs[0] 扩到**全部 specs 切片**。
   测试：R2 repro 反转 test_publish_retry_after_move_reuses_target_or_blocks（move 后重放 200 复用、
   内容不一致 CONFLICT、缺 staging 缺 target BLOCKED 不抛 FileNotFoundError）PASS。
10. **B8a OCR [high]（R2 未覆盖真新增）：多场景 run 永远无法 complete（死锁）**：
    `complete_scene` 改为——仅当本 run snapshot 的**所有预期场景都已回报 outcome** 才触发
    `finish_scene_run`（+换版）；部分场景回报时 run 保持非终态（SCENE_RUNNING）、已回报场景
    正常换版，租约不清。测试：test_scene_result_report.py 新增
    `test_multi_scene_run_partial_complete_does_not_deadlock`（2 场景 run：complete A（NO_MATCH）→
    断言 run_finalized=False、run_status=SCENE_RUNNING、A 已切 current；complete B →
    断言 run 终态 + 两场景 current 正确收敛）PASS；单场景路径不回归（既有 25 项全过）。

## 验证（worktree，.venv 软链主仓；真实退出码）

| 命令 | 结果 |
|---|---|
| `.venv/bin/python -m pytest -q tests/test_scene_result_report.py tests/test_scene_result_storage.py`（核心两文件，25+25） | **50 passed**（exit 0） |
| `.venv/bin/python -m pytest -q tests/` 场景套件 7 文件（report/storage/scheduling/lineage/config_resolution/capability_contract/config_schemas） | **168 passed**（exit 0） |
| R2-20261010 evidence 8 断言（worktree 内 `tests/test_r2_repro.py`，**按派单要求不进仓库**，`DATABASE_URL=sqlite:////tmp/r2-review-*.db DEMO_DATA=1` 隔离库路径引用跑） | **8 passed / 8 条全部反转**（exit 0） |
| MySQL 8.4.11 真实（rosbag-catalog-local-mysql-1，独立隔离 schema+临时用户，跑完 DROP，凭据不落盘不回显） | **5 场景 PASS**：首切 1093 消除 / 重放 no-op / 并发恰一 current / 旧版晚到 409 / 冲突保旧；脚本 /home/wang/.hermes/cache/scratch/r2_switch_mysql.py（可复跑） |
| `.venv/bin/python -m pytest -q`（全量） | **806 passed, 10 skipped, 3 failed**——3 个全部 `tests/test_devflow.py` 沙箱环境性用例，**stash 本返修全部改动后基线 eff0479 上同 3 failed**（既有，非本返修引入） |
| `.venv/bin/ruff check app tests` | All checks passed（exit 0） |
| `.venv/bin/ruff format --check app/ services 改动文件` | 全 formatted（exit 0） |
| `git diff --name-only eff0479..HEAD` | 5 文件全在 06B scope，零 .venv/环境产物 |

## 越界/契约交汇申报（需协调者重点核）

- `tests/test_scene_result_storage.py`（06A 文件）改 2 个用例：其断言建立在"created_at 排序"
  旧契约上，R2-05 裁决已把排序键改为分配 id 序号——测试改写为同语义新契约（非产品行为变化；
  服务层 `switch_current` 改动本身在 06B 返修清单内）。若协调者认为 06A 测试应回派 1号改，
  本 commit 内两 hunk 可独立 revert（不 revert 则 06A 回归基线会红）。
- R2-05 契约的 **create 侧（版本行在 run 创建事务内分配并绑定）由 1号落地**（派单修复链 1）；
  本返修 switch 侧按契约 id 序号裁决。当前 main 上事件消费路径若 1号 R2-05 create 侧尚未合入，
  `switch_current` 对"同事务秒级 created_at 并列、id 未随创建先后"的边界依赖 av 行分配序——
  1号合入后需协调者确认两侧 commit 时序（c67600d 与其 create 侧 commit 同批验收）。
- R2 repro 翻转文件里 test_late_old_event_run_keeps_new_current 按契约**预分配**了旧事件 run 的
  版本行（模拟 1号 create 侧落地后的形态）；1号 create 侧合入后该预分配代码可删，断言不变。

## 未执行项（如实）

- **OCR：未自跑**——请协调者对 c67600d 代跑（5 文件，单批安全）。
- local_stack.sh test / 页面实测：未执行——P0 本地授权，无路由/页面改动（3 个 POST 路由为
  执行面专用，语义只增严）。
- 处理机/生产：未执行（未授权）。
- TASK-08 联调：未执行——聚合任务范围。

## 建议可解锁

- 协调者验收 c67600d（含 R2 逐条核对 + MySQL 复跑）后，R2 有界第 2 轮强模型复审；
- 1号 R2-05 create 侧 commit 与本 commit 同批合入 main（两侧契约互锁，建议协调者确认合入顺序）。