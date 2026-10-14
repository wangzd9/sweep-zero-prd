---
task: TASK-06A
attempt: 2
owner: 2号
status: ACCEPT_MERGED
decision_commit: 8bd5618
output_commit: e92ef17
updated: 2026-10-09 15:1x
---
# TASK-06A attempt-2 裁决：ACCEPT_MERGED

合入 main **8bd5618**（--no-ff，e92ef17 原样保留在历史），已推 origin（GitLab）与
github 镜像（2d4a6fa..8bd5618 成功）。

## 协调者独立验收证据（不信任自报，全部 wt-04a 独立执行）

1. **范围**：`git diff --name-only eaf632a e92ef17` = 3 文件
   （scene_result_query.py / scene_result_service.py / test_scene_result_storage.py），
   纯新增 1585 行，零 .venv 产物（worktree 内 .venv 是软链，git status untracked，
   未入 commit）；`merge-tree --write-tree e92ef17 b3280c9` 零冲突。
2. **定向**：`pytest -q tests/test_scene_result_storage.py` → **25 passed**（exit 0）。
3. **全量**：`pytest -q` → **697 passed / 10 skipped / 3 failed**；3 failed 全部
   `tests/test_devflow.py` 沙箱用例（worktree `.git` 文件态已知环境问题，
   attempt-1 验收时已同因判定非本任务回归）。
4. **ruff**：`check` + `format --check` 3 文件全绿。
5. **OCR（协调者代跑，flock ocr.lock 串行）**：`ocr review --from c4ce66c --to e92ef17
   --audience agent --timeout 120` → **0 findings**（2 文件，session 20cd817a，18m30s）。
   注：期间发现 wt-04a 下还有一个自跑 `ocr review -c e92ef17`（协调者 cron 早期
   B2 命令残留，非 2号发起——2号回执明确"未自跑"），按单实例串行规则已 kill 较新
   进程，保留持锁方；对交付物无影响。

## 5 项返修逐条对照代码核实（全在位）

| # | 级别 | 修复 | 核实证据（e92ef17 源码） |
|---|---|---|---|
| 1 | high | lineage 分页 NULL 分支 | `scene_result_query.py:344,354` 与 `search_scene_bags`（L149,158）同口径 `is_(None)` 分支；回归 `test_lineage_pagination_null_started_at` 在 25 项中 |
| 2 | medium | 段数同基数 | `scene_result_service.py:153,215-216` expected=registered=manifest 全部区间数（含 flat），docstring L23-24 写明语义；`_backfill_segments`→`_refresh_counts`（L200-201,236-241）重查实查行数；回归 `test_segment_counts_same_base_including_flat` |
| 3 | medium | 幂等 IntegrityError 兜底 | begin_nested+IntegrityError 15 处，`_scene_row` 补 except 无裸 500；回归 `test_concurrent_replay_no_500` |
| 4 | medium | current 双指针并发 | NOT EXISTS guarded UPDATE（L389,443）单条原子置指针，rowcount==0 重读有界 3 次；回归 `test_concurrent_first_switch_no_double_pointer` |
| 5-8 | low | N+1 批量 IN / +1 探测复用 / 死参数 db / 死常量 | `child_by_uid` 循环前一次 IN（L364-403）；`truncated` 复用探测；`_bag_summary` 无 db 参数；`_SEARCH_PROJECTION` 已删 |

## 契约选择确认（06B 派单引用）

- **#2 段数基数**：采纳"expected = registered = manifest 全部区间数（含 flat）"，
  06B 完整性门禁按**等值比较**（全部区间落库即完整）；可发布子集另走
  `list_segments(publish_only=True)` 与 manifest `expected_slice_keys` 核对，不混入段数基数。
- **switch_current 3 次有界重试**：持续高竞争下 409 收尾（重放语义），与 06B 路由
  409 映射兼容。
- **零 schema 变更**：guarded UPDATE / NOT EXISTS 均为 DML，两后端同义，无 MySQL DDL 风险。

DESIGN §11.2 契约表以 e92ef17（合入 8bd5618）为 06A 数据层事实来源。

## 执行者状态

2号 slot 释放；TASK-06B 依赖（05/04B/06A）全部 DONE，已生成 attempt-1 dispatch
（`inbox/2号/TASK-06B/attempt-1-dispatch.md`，PENDING，10min cron 自动领取）。