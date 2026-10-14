# 回执：TASK-07B attempt-4-r4 迁移 downgrade 最小返修

- status: REVIEW_PENDING（交付冻结）
- 派单：`inbox/2号/TASK-07B/attempt-4-r4-dispatch.md`（协调者 r130，2026-10-13 06:54:26）
- ACK：`inbox/2号/TASK-07B/attempt-4-r4-ack.md`（07:02）
- owner：B（前端功能开发群，cron poll `6f7471d8747c`）
- base/head：base `4baf79f`（attempt-3-r3 交付冻结 HEAD），head **`62620a3`**（单 commit，续 `scene/task-07b-manual-revision-withdraw` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07b`；原 base `502bf8e` 不变）
- 交付时间：2026-10-13 07:2x +08:00

## 一、文件清单（单文件 2 项，零 app 代码面）

`alembic/versions/20261012_01_scene_manual.py`（+31/−11）：

1. **R4-1（r3-1 medium CORRECTION）**：downgrade 的表存在性守卫从「仅包 drop_column/drop_table」提升为**覆盖整个表依赖块**（`_indexes_of` 调用+index 循环+corrected_label 列 drop+drop_table）。正常态行为与原口径逐语句一致；表缺失态 downgrade 全 no-op 不抛异常。
2. **R4-2（r3-1 low documentation）**：模块 docstring 补「downgrade→upgrade 往返风险」段（引用 `20261009_02` 的 `frozen_capability_hashes_json` 先例 + 07B 未合入迁移的处置边界：空库链起点不经过往返路径；已应用库往返=操作者重新纠错补记），不改列结构。

**越界申报（与派单 §一「最小修复」口径的差异，按验证口径实现）**：派单 §一要求仅把 `drop_column` 移回 `TABLE in get_table_names()` 判定内、index 循环维持现状（并断言原始口径 `68b5188` 对表不存在的库是 no-op 安全）。本侧双库实证发现**该断言不成立**（见 §三 取证 1）：原始口径与 R3 在表缺失态均在 `_indexes_of`（`get_indexes`）处抛 `NoSuchTableError`（SQLite `NoReferencedTableError` / MySQL 1146）。若仅按 §一 移动 drop_column，派单 §三 验证口径「表缺失态 SQLite 内存探针 downgrade 不抛异常」**必然失败**。故按 §三 验证口径（AC 面）实现守卫提升——§一 与 §三 冲突时以 §三 为准，差异在此申报，请协调者机械核验时重点核对；如协调者坚持 §一 字面口径，本 commit 可 1 行回退到中间形态（但该形态不满足 §三 探针）。

## 二、行为

- downgrade（表存在，正常态）：与 R3 交付同序——先 drop `bag_scene_label_evidence.corrected_label`（列存在时）→ drop 4 index（名存在时）→ drop `scene_manual_revision.corrected_label`（列存在时）→ drop 表。
- downgrade（表缺失，部分应用重入态）：evidence 列 drop 照旧（有独立 has_table+列守卫）；审计表相关全部操作跳过，**无异常**（双库实证）。
- upgrade 面零改动（R3 已审 0 findings 结构不动）。

## 三、自测命令 / 退出码 / 环境 / 关键断言 / 证据

环境：`wt-04a-t07b` HEAD `62620a3`，venv Python 3.10 + SQLAlchemy 2.0.41 + alembic 1.16.4 + pymysql；真 MySQL = `docker.m.daocloud.io/mysql:8.4`（8.4.11）独占容器+独立 docker 网络（无宿主端口映射），用完即毁。

1. **定向 pytest**：`pytest tests/test_task07b_r3_revision.py tests/test_task07b_manual_revision.py tests/test_task07b_r2_revision.py -q` → **12 passed** RC=0（2.37s）。
2. **真 MySQL 8.4.11 隔离库 fresh 往返**：`alembic upgrade head`（RC=0，SHOW COLUMNS 校验两表均含 `corrected_label varchar(16) nullable`）→ `downgrade -1`（RC=0，`SHOW TABLES LIKE 'scene_manual_revision'` 空 + evidence 列已移除）→ `upgrade head`（RC=0，两表列恢复）→ **MYSQL_ROUNDTRIP_OK**；容器 0 残留（`docker ps -a --filter label=rosbag.t07b=1` 空、网络已删）。证据 `scratch/b-r4-roundtrip.py` + `b-r4-colcheck.py`（终端输出在案）。
3. **表缺失态 downgrade 探针（R4-1 核心验收）**：SQLite 内存 + 真 MySQL 8.4 双库，`create_all` 后 DROP `scene_manual_revision`（模拟部分应用/已回滚态）→ 跑 downgrade：R4 工作树形态**双库 NO_EXCEPTION**；对照 R3 `4baf79f` 同态**双库 RAISED NoSuchTableError**（r3-1 medium 复现）。证据 `scratch/b-r4-evidence3.py`（终端输出在案）。
4. **原始口径取证（越界申报依据）**：`git show f4bfcf2:` 与 `68b5188:` 的 downgrade 在表缺失态双库**均 RAISED NoSuchTableError**（首个失败点=`_indexes_of`→`get_indexes`，`SHOW CREATE TABLE` 1146）——证伪派单 §一「原始口径 no-op 安全」断言。证据 `scratch/b-r4-evidence2.py` + `b-r4-evidence3.py`。
5. **ruff**：`ruff check alembic/versions/20261012_01_scene_manual.py` → **All checks passed** RC=0。
6. **alembic heads**：单头 `20261012_01_scene_manual (head)`，无多头。
7. **diff 边界**：`git show --stat HEAD` = 1 file changed, +31/−11，仅迁移文件（零 app/tests/新迁移文件/upgrade 面改动）。

未执行项：无新增用例（派单 §三明示迁移面无新增用例要求）；未跑全量 pytest（本单 0 app 代码改动，定向 3 文件+迁移面实证已覆盖改动面，R3 全量基线 840 passed 口径不变）。

## 四、后续（按派单 §四）

协调者机械核验（diff 限单文件+越界申报核对）→ R4 增量 OCR（单批迁移 `--from 4baf79f --to 62620a3`）→ 强审查增量复审（范围=R3-1~4+R4-1/R4-2，授权期 2026-10-13 11:33:12 内）→ TESTER 07B-post-r（SR-05 口径不变，target `62620a3`）→ 全绿合入（07B 整链先于 16A 迁移 rebase 双头）→ 07B DONE → 派 07C/16C。同根因两轮失败（R4 增量复审再出同位 CORRECTION）升级用户。