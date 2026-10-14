# 回执：TEST-TASK07B-post-r attempt-1（07B 整链收口前最后一环独立验证）

- 时间：2026-10-13 08:3x +08:00（TESTER cron poll 167580c0500b，会话 `cron-tester-poll-167580c0500b-20261013-075953`）
- 派单：`inbox/TESTER/TASK-07B/post-r-dispatch.md`（协调者 r133）；ACK `inbox/TESTER/TASK-07B/post-r-ack.md`
- 被测 target：**`62620a3ddc5cfa614c5e72681c852c96d60507b3`**（`scene/task-07b-manual-revision-withdraw` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07b`；开工前 `git rev-parse HEAD` 实测一致，工作树仅 `.venv`/`scratch` untracked，0 业务改动）
- 整链 origin base：`502bf8e`（fetch 实测 `origin/main`=`502bf8ec79690cf01e130cb0591121eb10e96af5`，未合入）
- 环境（独立取证，不复用 B 回执/协调者探针作证据）：
  - 真 MySQL = 独占容器 `tester-postr-mysql`（镜像 `6ea90827b110` = `docker.m.daocloud.io/mysql:8.4` 本地缓存，容器内 `SELECT VERSION()` 实测 **8.4.11**），独立 docker 网络 `tester-postr-net`（172.22.0.2，无宿主端口映射），隔离库 `t_postr`/`t_postr_mig`/`t_postr_mig_drop`；用完即毁（0 残留实测）
  - 工作树 `.venv` Python 3.10（SQLAlchemy 2.0.41 / PyMySQL 1.4.6 / alembic 1.16.4）
  - 页面实测：自包含 uvicorn `127.0.0.1:18793` + 临时 SQLite（DEMO_DATA=0），结束即毁
- 结果：**PASS（4/4 全项）**

## 一、SR-05 双连接同版本无关联并发（R2 强审 50c665e4… 高 VERIFICATION_GAP，既定口径）

- 探针 `~/.hermes/cache/scratch/tester_postr_sr05_probe.py`（日志 `tester_postr_sr05.log`），**RC=0 PASS**。
- 前置实测：子切片 `SCENE_SLICE`/AVAILABLE，`ver0=1`，**初始 `bag_scene` 关联不存在**（断言 linked=None）；两 worker 各自独立 SQLAlchemy session（双连接），barrier 同步起跑，同 body（row_version=1）并发调 `revise_scene_labels`。
- 断言全过：**恰一方 200（B）、另一方 409（A）**，409 detail=`ROW_VERSION_CONFLICT: bag changed concurrently`（守卫拒绝语义，非 500）；全程无 StaleDataError/IntegrityError（异常捕获面实测为空）；SR-02 修复面（`_guarded_bump_row_version` 先行于关联 INSERT）取证成立——输家在守卫处回滚，`bag_scene` 关联由赢家单条建立（linked=True）。
- 终态断言：`row_version`=2（**只 +1**）；`scene_manual_revision` 审计行**恰 1 条**（action=REVISE, corrected_label=flat, operator=wang-sr05, 原值引用=`slope#sr05-run-…#sr05`）；MANUAL evidence **恰 1 行**（corrected_label=flat, revised_by=wang-sr05）。

## 二、R4 迁移面（target `62620a3`，真 MySQL 8.4.11）

- **正常态**（探针 `tester_postr_mig_normal.py`，日志 `tester_postr_mig_normal.log`，**RC=0 PASS**，库 `t_postr_mig`）：
  - `alembic heads` 单头 `20261012_01_scene_manual`；fresh 隔离库 `upgrade head` → `downgrade -1` → `upgrade head` **三次 RC=0 往返**；
  - SHOW COLUMNS（Inspector 等价口径）：upgrade 后双表 `scene_manual_revision.corrected_label` 与 `bag_scene_label_evidence.corrected_label` **均在**；downgrade 后审计表 drop、evidence 列 drop（对称逆操作）；再 upgrade 双列恢复；
  - 新库数据可写抽查：REVISE 行 INSERT/DELETE RC=0（既有迁移链 20260911_01 起点在真 MySQL 8.4 全链通）。
- **表缺失态**（探针 `tester_postr_mig_drop.py`，日志 `tester_postr_mig_drop.log`，**RC=0 PASS**）：
  - 真 MySQL 隔离库 `t_postr_mig_drop`：fresh `upgrade head` 后 `DROP TABLE scene_manual_revision`（alembic_version 保持 head）→ `alembic downgrade -1` **RC=0 不抛异常**（R4-1 守卫生效断言；对照 R3/原始口径同态 NoSuchTableError=已被修复对象）；
  - SQLite（临时文件库）同路径 fresh `upgrade head` → DROP 表 → `downgrade -1` **RC=0 不抛异常**；双库断言审计表不存在 + evidence corrected_label 已 drop；
  - MySQL 侧 downgrade 后 `upgrade head` 恢复 RC=0；
  - 合成态（审计表缺失+evidence 列存在）按 r133 裁决 `r4-01-adjudication-20261013.md` 不属本单验收项，未执行。

## 三、07B 定向回归（target 工作树口径）

- `pytest tests/test_task07b_manual_revision.py tests/test_task07b_r2_revision.py tests/test_task07b_r3_revision.py -q` → **12 passed, RC=0**（2.26s，日志 `tester_postr_pytest.log`）。
- 页面实测（探针 `tester_postr_page_probe.py`，日志 `tester_postr_page.log` + `postr_uvicorn.log`，**RC=0 PASS**，真实 HTTP urllib 非 TestClient）：
  1. 切片详情 `/bags/{uid}`：`scene-revise`/`scene-withdraw` 表单入口均在；
  2. 未纠错详情**不出现**「当前人工标签」；
  3. 表单纠错 POST → 303 `revision_flash=REVISE`；
  4. 纠错后详情渲染 `当前人工标签：<strong>flat</strong>` + 审计表「修正为」列 + 行（人工纠错/场景/wang-postr/flat/row_version=1）；
  5. 表单下架 POST（row_version=2）→ 303 `revision_flash=WITHDRAW`；
  6. 详情显示「已下架」；默认 `/bags` 视图**不含**该切片，`/bags?view=all` **仍可见**。

## 四、清理与残留核

- 容器 `tester-postr-mysql` 已 `docker rm -f`、网络 `tester-postr-net` 已删：`docker ps -a --filter name=tester-postr` **0 残留**、`docker network ls --filter name=tester-postr` **0 残留**；
- 临时 SQLite（postr_page.db/postr_mig_drop.sqlite）**已删**；SR-05 探针自建夹具行自清；宿主无 18793 监听（uvicorn 退出确认）；
- target worktree `git status` **0 tracked 改动**，HEAD 仍 `62620a3`——零业务代码改动，测试材料仅在 `~/.hermes/cache/scratch/`。

## 五、结论与未执行项

- **结论：PASS**——07B 合入门禁剩余证据（SR-05 真 MySQL 并发口径 + R4 迁移面双库探针 + 定向回归 + 页面实测）全部独立取证成立；按派单收口链，请协调者执行 07B 整链 `--no-ff` 合入（先于 16A rebase 双头）→ 07B DONE。
- 未执行项：合成态 evidence 列探针（r133 裁决出单）、16A/16B/16C 面（非本单范围）、生产启用（TASK-11 门禁仍 PRODUCTION BLOCKED 待用户授权）。
- 普通测试 PASS ≠ OCR/强审查/生产门禁通过；OCR 与强审由协调者面收口，本回执不覆盖。