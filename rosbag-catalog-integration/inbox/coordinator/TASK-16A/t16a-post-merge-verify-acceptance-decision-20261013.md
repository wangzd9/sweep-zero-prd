# 裁决：TASK-16A DONE（rebase 链合入后独立验证 PASS，2026-10-13 09:4x，协调者 r139）

## 收口条件核对

1. **开发交付**：A attempt-3-rebase `da304e2`（rebase 到 `3d2a075`，16A 域内容=旧链逐字节同一+迁移接线 8 行）已冻结交付（r138 在案）。
2. **机械核验**：r138 协调者独立核全绿（祖先核/零越界/迁移单头/定向 56 独立复跑/ruff 绿）。
3. **OCR**：16A v2 14/14 + attempt-2-r1 增量 3 批 + 接线批（session `8073ac31`）全收口，无 CORRECTION 级遗留。
4. **合入**：--no-ff 合入 main `6fb42c4`（r138，双推 origin/github 一致，合入后 sanity 全绿）。
5. **TESTER 独立验证 PASS**（本裁决输入）：`test-receipts/TEST-TASK16A-post-merge/attempt-1.md`（09:32 交付，事件 `tester-t16a-post-merge-verify-pass-20261013`）：
   - 真 MySQL 8.4.11 隔离容器全链迁移三趟 RC=0（fresh upgrade head → downgrade 至 `20261012_01_scene_manual` → 再 upgrade head），单头 `20261013_01_scene_intake`（25 字符，无 1406）。
   - AC-14/08 迁移承载字段 MySQL 取证：`intake_root_id varchar(16) NOT NULL DEFAULT 'self_built'`+索引 `ix_ingest_profile_root_enabled` 在列；历史行回填 `self_built`（IS NULL 计数=0），行身份不变。
   - SQLite 定向 7 文件 68 passed（16A 56 + 07B 12）RC=0；`test_web` 单跑失败按派单口径申报=基线 `502bf8e` 既有顺序依赖，非 16A 回归，不阻塞。
   - 容器/网络 0 残留、被测 worktree 零改动（协调者 09:3x 独立复核 docker ps -a 与 network ls 均 0，main HEAD `6fb42c4` 未动）。
6. **已知观察项**：应用层 AC-14/08 语义面（双根同名/跨盘 rename/快照绑定/异常不回退）= A 链 56 测试 + OCR 闭环范围，本单口径不越界。

## 结论

**TASK-16A 判定 DONE**（main `6fb42c4`）。强审查 NOT_REQUIRED：16A 链自 attempt-1 起已含 16A v2 14 批 OCR + 增量 3 批 + 接线批 0 findings，且 16A 属本轮 v0.4 新规划内低风险接线面（双根配置/Scanner 隔离/身份防线），未触发 REVIEW_NOW 条件；07B 域两轮强审（`50c665e4`/`a8febf1a`）已独立闭环在案。

## 接续

- 16D 三前置：16A **已接受**；16B 维持 NEEDS_REVIEW 冻结（proxy OCR 4/4 连败，r137 已升级用户裁决：a 再试/b 换审查方式/c 已裁 findings 先行返修/d 搁置——**等用户答复，不第 5 次自动重试**）；16C B 开发中（ACK 08:3x，`wt-04a-t16c` base `4b9f30a`）。三项全接受且合入固定快照后才派 16D。
- A 槽释放：当前无满足条件的可派叶任务（16B 冻结等用户、16C 属 B、07C/11/12-15 未授权），A 转空闲待命，不扩需求。
- 16A 接受后 real 栈全链冒烟（16B 留项）仍待 16B 收口后、16D 前执行，owner=C。