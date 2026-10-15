# TASK-12S-F attempt-1 交付回执（执行者 B，2026-10-15 10:14 +08:00）

- **状态**：开发完成、自测全绿；**交付冻结暂挂**（按 supplement-s1 口径：F 冻结 base 后移至 E attempt-2 冻结 head，收到" E attempt-2 冻结 head=XXX"通知前不提前冻结正式交付；当前 commit 为工作点，届时机械 rebase）。
- **task/attempt**：TASK-12S-F / attempt-1（REQ-21 / AC-21）。owner=执行者 B。
- **base/head**：base `b39a3ec`（TASK-12S-E 冻结 head，原派单指定）→ 工作点 head **`6798059`**（分支 `b/task-12s-f-input-reject`，worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t12sf`）。diff 规模：10 文件 +939/-7。

## 文件清单（git diff b39a3ec 6798059）

| 文件 | 改动 |
|---|---|
| `alembic/versions/20261014_01_ingest_rejected.py` | 新增。单头迁移（down_revision=20261013_01_scene_intake）：ingest_submission 三列（rejection_reason_code String(32) nullable 带 index=True 自动名索引 / rejection_evidence_json Text nullable 无 server_default / stable_reject_rounds Integer nullable）+ 逐对象 gate（空库 create_all 已含新列时跳过 add，防 20260911_01 big-bang 重放 duplicate column）；downgrade 逆删 |
| `app/models.py` | IngestSubmission 加三列（+注释口径：INPUT_REJECTED 终态语义、TEXT 无默认、对账只扫 PENDING_INPUT） |
| `app/services/ingest_service.py` | `report_input_rejected`（受控根校验 409 越界、按 path_claim 定位唯一活动行：PENDING 复用 / 已拒绝幂等再确认不推代次 / 无行建系统拒绝行 scanner-reject、置 INPUT_REJECTED + 审计块）；`resume_input_rejected`（乐观锁 row_version：旧代次 409 ROW_VERSION_CONFLICT、非拒绝态 409 SUBMISSION_NOT_REJECTED、缺行 404；成功回 PENDING_INPUT、清稳定计数、保留拒绝历史、幂等键重放）；`_submission_response` 增 rejection 字段 + resume_hint |
| `app/api/ingest_submissions.py` | 两条路由：`POST /reject-input`（Scanner 内部上报，原始 body 限额口径复用 _raw_body+幂等依赖）；`POST /{id}/resume-input`（ResumeInputRequest DTO extra=forbid） |
| `app/scanner/metadata.py` | `classify_bag_input` 三分量（parsed/reason_code/detail）：BAD_METADATA/UNSUPPORTED_STORAGE/EMPTY_BAG/MISSING_DB3 稳定机器码 + 512 截断详情；`validate_bag_input` 保持原 raise 语义（既有调用方零改动） |
| `app/scanner/runner.py` | 稳定确认后（先落稳定证据再分类）无效输入不 raise：拒绝快照=mtime:file_count:total_bytes（**不含**递增 stable_rounds，保"相同快照抑制"口径）；相同快照已报→抑制不刷重复拒绝；Backend 上报不可达→计 failed 不写拒绝标记（下轮重试）；原包不 move 不删 |
| `app/scanner/backend.py` | `report_input_rejected` 上报封装（/reject-input，timeout 60） |
| `tests/test_ingest_input_rejected.py` | 新增 14 例：拒绝登记（有/无 submission、越界根 409、缺字段 422）、E 对账隔离（零事件零 run、不影响既有记录、不产生 source 行）、resume 全路径（成功/旧代次 409/非拒绝态 409/404/幂等重放/BOUND 防御 409）、迁移 upgrade/downgrade（独立空库，模拟旧库形态后单 revision 执行并核对列/索引/版本标记）；API 走自洽独立临时库夹具（test_web 同款配方，不污染共享库全局断言） |
| `tests/test_scanner_stability.py` | +5 例：空包两轮稳定后拒绝（不上报/不 move/不 register/不进指纹链）、相同快照抑制、内容变化重新计稳定可再报、上报失败计 failed 不持久化、classify 四原因码+与 validate 口径一致；FakeNasClient 加 metadata_text 参数 |
| `tests/test_scanner_structure.py` | 职责断言 +report_input_rejected/classify_bag_input |

## 行为（对应 REQ-21 / AC-21）

1. 稳定（≥scan_stability_rounds）后仍空/坏 metadata 的输入：Scanner 不再 raise 崩整轮，携稳定证据上报 → Backend 持久登记 INPUT_REJECTED；未绑定提交置拒绝态（ID/幂等键/path claim/资料保留），无提交建系统拒绝行（根+路径+观测身份留痕）；原包留 incoming 受控位置。
2. 可查询：rejection_reason_code 稳定机器码 + 索引；GET submission 回 rejection_evidence 审计块与 resume_hint。
3. 逻辑隔离：pending_binding 对账只扫 PENDING_INPUT——拒绝行零事件零 run，不产生 source/run/模型请求；既有 AVAILABLE/DERIVED 记录零触碰（有测试断言）。
4. 受控 resume：材料补齐后 `POST /{id}/resume-input`（row_version 乐观锁）回 PENDING_INPUT，可再走绑定/登记链；仍坏可再拒绝（可重复尝试、幂等）；旧代次/非拒绝态/已绑定拒绝 409。
5. 防线：incoming_path 越出声明 root 受控 scan 根 409；Backend 上报不可达计 failed 不假称已登记。

## 自测命令 / 退出码 / 环境

- 环境：worktree 软链主仓 venv（python3.10，.venv 提交前已删）；`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest`。
- `pytest tests/test_ingest_input_rejected.py -q` → **14 passed** (exit 0)。
- 组合回归 `pytest tests/test_ingest_input_rejected.py tests/test_ingest_config.py tests/test_ingest_config_api.py tests/test_scanner_stability.py tests/test_scanner_structure.py tests/test_scene_slice_scheduling.py -q` → **91 passed** (exit 0)。
- 全量 `pytest tests/ -q` → **1204 passed, 10 skipped, 5 failed**；5 失败归属核实均非本任务：3×test_devflow（worktree `.git` 文件非目录的环境固定项，skill 在案）；test_web 分页用例在 **base b39a3ec 独立 worktree 单跑同失败**（pre-existing 顺序依赖，已建 `wt-12sf-base` 对照取证后清理）；test_scene_slice 与"本套件在后"组合失败、反置顺序绿（其自身夹具顺序敏感，单独与本套件单独跑均绿）。
- 迁移核对：`alembic heads` 单头 `20261014_01_ingest_rejected`；upgrade/downgrade 由测试在独立空库实证（列/索引/版本标记断言）。
- `ruff check`（本仓 select E,F,I,UP）本任务 10 文件 → **0 error**（E501 非启用规则；I001 已 fix）。
- scanner 无 DB 直写结构红线（test_scanner_structure）通过：拒绝上报仍走 Backend API，`app/scanner/*` 无 sqlalchemy/app.models。

## 未执行项（如实申报）

- **真 MySQL 8.4.11 隔离探针未跑**：本迁移仅 nullable 列 + String(32) 索引（无 TEXT server_default、无宽列索引，不踩 1101/1071 已知情形），但 ACK 承诺"SQLite 绿不算数"——留待交付冻结时（E attempt-2 rebase 后）按 T-03/T-04 口径在隔离 MySQL 库实跑 `alembic upgrade head` + DML 探针，或由 TESTER 阶段统一取证；不提前声称已验证。
- **with_for_update / 真并发乐观锁互斥**：SQLite 静默忽略行锁，本地仅验用户可见契约（旧代次 409、不覆盖）；按仓库口径待隔离 MySQL 双会话竞争实证，未报已验证并发。
- **Scanner 真实 NAS 双轮稳定 E2E**：本地以 fake client 两轮驱动验证状态机；真实 A100/NAS 实测属 TESTER/生产口径，本单未授权不执行。
- OCR / 强审 / TESTER / 接受 / 合入：全部未执行，按门禁等 E attempt-2 收口后由协调者启动。

## 越界申报

- 无。`pending_binding.py` 只读消费未修改；`source_service.py` 未修改（E-R7/R8 点位归 A attempt-2）；未动 16C 界面文件；VLM/模型调用 0；未碰生产/迁移执行/算法。
- 工作区 `/home/wang/work/doc/prd/rosbag-catalog-integration` 仅写本回执 + sessions/B.md + 事件记录（角色允许面）。