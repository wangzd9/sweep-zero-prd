---
task: TASK-06A
attempt: 2
owner: 2号
status: REVIEW_PENDING
base: c4ce66c（attempt-1 交付；dispatch 声明 base main 1946718 以 attempt-1 为续作基点）
output_commit: e92ef17
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
updated: 2026-10-09 12:55
---
# TASK-06A attempt-2 返修交付

恢复自中断的 attempt-2 返修（resume-note）：在途改动（query 层 #1/#5-#8 与
service 层 #2/#3 主体）已保留并补齐，未丢弃任何在途工作；本轮新增修复 3 处
在途缺陷 + 5 项回归测试。

## 交付内容（3 文件，零越界，零新迁移）

- `app/services/scene_result_service.py`
- `app/services/scene_result_query.py`
- `tests/test_scene_result_storage.py`（+5 回归测试，共 25 项）

## 逐条返修对照（dispatch/OCR b29b4ae2 8 条）

### 必修 1-4
1. **high-1 分页 NULL 分支** ✅：`lineage` 续查条件补
   `started_at.is_(None)` 分支，与 `search_scene_bags` 同口径（注释写明原因）。
   回归：`test_lineage_pagination_null_started_at`（A ts=00:01 / B ts=00:00:50 /
   C ts=NULL，limit=2，锚定非 NULL 行翻页，C 必须在第二页）。
2. **high-2 段数语义** ✅：选定 **expected = manifest 全部区间数（含 flat）**，
   registered 同基数（语义选择说明见下）。重放补齐路径改为 `_backfill_segments`
   完成后 `_refresh_counts` 重查 `scene_segment` 实际行数（修复前补齐路径存过期值）。
   回归：`test_segment_counts_same_base_including_flat`（含 flat 的 manifest
   expected==registered==2；删区间行后重放，registered 重查刷新）。
3. **medium IntegrityError 兜底** ✅：`register_manifest` 的 av insert、
   `_register_derivation` 的 bag_record/derivation insert、evidence insert、
   `_scene_row` 的 scene insert 全部 `begin_nested` + `except IntegrityError`
   重查：同 run 内容一致 → 200 语义重放；内容不同 → 409 DUPLICATE_CONFLICT；
   非本模块唯一键冲突 → re-raise 留痕。在途缺陷修复：`_scene_row` 原 begin_nested
   无 except（会裸 500），已补。回归：`test_concurrent_replay_no_500`
   （monkeypatch stale read 模拟 check-then-act 间隙，撞唯一键后重放而非 500）。
4. **medium switch_current 双指针** ✅：在途改动只有清旧指针的 guarded UPDATE，
   未堵"无 current 行的并发首切"双置 True 洞（两方都读到 current=None，
   `current is not None` 分支不进）。本轮补**置新指针的 NOT EXISTS guarded
   UPDATE**：`SET current=1 WHERE id=? AND NOT EXISTS(同 parent+scene 其他
   current 行)`，rowcount==0 → 重读（同目标幂等重放 / 他版本胜出错退 409），
   有界 3 次。两后端通用，不依赖行锁强度。回归：
   `test_concurrent_first_switch_no_double_pointer`（stale SELECT 返回空，
   断言同 parent+scene 恰一行 current=true）。

### 建议 5-8（顺手全修）
5. **lineage N+1** ✅：循环前一次 IN 批量取子包行建 `child_by_uid`，
   next_cursor 锚点复用批量结果。回归：`test_lineage_no_n_plus_1`
   （engine 级 before_cursor_execute 计数，6 子包页查询数 ≤7；修复前 10）。
6. **list_segments 冗余二次查询** ✅：`truncated` 复用首次 +1 探测。
7. **_bag_summary 死参数 db** ✅：移除（含调用点）。
8. **_SEARCH_PROJECTION 死常量** ✅：删除。

### 可选 low
- #7 性能注释：`+1 探测` 处补"超大量数据代价有界、DESIGN §7.1 已接受"注释。
- 死代码清理：#8 已含；无其他。

## #2 契约选择说明（06B 派单需带上）

**expected_segment_count = registered_segment_count 基数 = manifest 全部区间数
（含 flat 等非发布）**。06B 完整性门禁做 `expected == registered` 等值比较
（全部区间落库即完整）。可发布子集由 06B 另走
`list_segments(publish_only=True)` 与 manifest `expected_slice_keys` 核对，
不混入段数基数。理由：flat 区间同样是 manifest 声明的落库义务
（DESIGN §4.1"包含 flat"）；若 expected 只计可发布而 registered 计全部，
含 flat 的 SUCCESS manifest 两值恒不等，门禁要么永不开通要么漏检 flat 缺失。

## 验证（worktree 内，.venv 软链主仓；真实退出码）

| 命令 | 结果 |
|---|---|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_result_storage.py` | 25 passed（exit 0） |
| 同上，源文件 stash 回 c4ce66c 跑新增 5 项（验证 RED） | 5 failed（exit 1）——撤修复必红 |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`（全量） | 697 passed, 10 skipped, 3 failed |
| 3 个失败 | 全部 `tests/test_devflow.py` 沙箱用例；**已验证 base c4ce66c 下同样 3 failed, 21 passed**（stash 全部改动后单跑该文件），worktree `.git` 文件/目录环境差异，与本任务无关 |
| `.venv/bin/python -m ruff check app tests` | All checks passed!（exit 0） |
| `.venv/bin/python -m ruff format --check app tests` | 151 files already formatted（exit 0） |
| `git diff c4ce66c e92ef17 --stat` | 3 文件 +457/-127，零越界、无 .venv 产物 |

## 待协调者验收的要点

- OCR 请代跑 e92ef17（flock inbox/ocr.lock）；未自跑。
- MySQL 隔离库 DDL 实测：本任务零 schema 变更（guarded UPDATE / NOT EXISTS
  子查询均为 DML，两后端同义），无新增 DDL 风险。
- SQLite 下 `begin_nested` 退化为 SAVEPOINT（有效）；MySQL 下行锁 + SAVEPOINT
  全量生效，兜底路径在后端无关语义下成立。
- `switch_current` 的 3 次有界重试在持续高竞争下会 409 收尾（重放语义），
  与 06B 路由层 409 映射兼容。
- 恢复说明：attempt-2 上一执行会话被中断（stale claim），本轮为 resume-note
  要求的续作；在途改动全部保留并审查补齐，无 checkout/reset。