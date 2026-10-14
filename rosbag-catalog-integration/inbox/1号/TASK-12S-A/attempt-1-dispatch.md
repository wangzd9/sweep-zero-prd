# 派单：TASK-12S-A 原始信息绑定 attempt-1（协调者 r145 派发，2026-10-13 11:3x）

- **角色/owner**：执行者 A（1号）｜**attempt**：attempt-1｜**父任务**：TASK-12S（§9 v0.5 水雾优先）
- **固定 base**：`6fb42c4`（= origin/main，16A 已合入；领取时 `git fetch` 后双核一致才可开工）
- **worktree**：新建 `wt-01-t12sa`（分支 `a/task-12s-a-spray-intake`），.venv 软链主仓；不移动 16A 冻结 worktree
- **契约版本**：scene-input/v1（`RAW-DATA-REQUIREMENTS.md`）+ TODO §9.3/§9.4 + `SPRAY-INTEGRATION.md` §2/§4
- **最小阅读**：SESSION-START → TODO §9（9.2/9.3/9.4 卡）→ RAW-DATA-REQUIREMENTS.md → SPRAY-INTEGRATION.md §2/§4 → DESIGN §7.3.1（16A 双根/快照口径，已合入）

## 交付范围（仅这些，逐文件核 diff）

1. **DTO**（`app/schemas/scene_config.py`）：POST/PATCH ingest-submissions 新增**可选** `source_metadata` 块——有界 ≤64KiB、严格 `extra=forbid`、`schema_version="scene-input/v1"`、字段 `vehicle_code`（≤64 字符，spray 必填）/`collection_timezone`（必填，IANA 名校验）/`batch_id`（必填，非空字符串）/`sensor_profile`（必填，引用服务端已登记 sensor profile）；旧 profile/旧提交不携带该字段=行为零变化。
2. **API 面**（`app/api/ingest_submissions.py`）：接受/校验/错误码（未知车辆/缺信息 422、车辆冲突/已绑定改车 409 或明确待补状态，口径按 §9.4；`RAW-DATA-REQUIREMENTS.md` 明文「具体新提交可以拒绝422」）；未绑定阶段 row_version 修订、绑定后拒改。
3. **服务面**（`ingest_service.py`/`source_service.py`/`catalog_ingest.py`/`bootstrap.py` 允许范围内的接线）：Vehicle 解析成稳定 `vehicle_id`（用既有 Vehicle 模型 vehicle_code 唯一索引匹配，不建新表）；`intake_snapshot_json` 存 source_metadata **有界快照 + 独立 hash**（与旧 config_hash/EffectiveConfig 分离，旧 hash 不变）；绑定前验证/父子继承/恢复 upsert 重新应用同一冻结绑定（不被 rustdesk 名称匹配清空）；**新增 `scene-spray` profile 种子**（root=scene、incoming_prefix=`spray`、默认纯 scene_slice+spray、能力未接受时 profile 保持禁用、bootstrap 不崩）；原 `scene-isolated` 坡道 profile 的 ID/version/default/hash **零变化**。
4. **测试**：缺/未知车辆、车辆冲突、目录名无编号、两车同名包、重复登记、冻结后改车拒绝、未绑定 PATCH/row_version、hash 重放、旧 self_built/NVIDIA/坡道缺新字段仍工作（回归）。

## 验收（AC）

- **AC-18.1**：spray 入口 vehicle_code/时区/批次/sensor profile 有效且 purpose=scene_slice、scene=spray；不猜车，无资料/冲突拒绝或待补。
- **AC-18.2**：绑定前受 row_version 约束可修订、绑定后拒改；源/子包车辆一致；恢复不被 basename 匹配清空；独立 hash 与旧业务 hash 不混用。
- **AC-18.3**：旧 self_built/NVIDIA/slope 无需新增元数据；原 profile/version/default/hash 保留；scene-spray 窄前缀不抢坡道空前缀；无 spray 能力时 bootstrap 不崩。

## 硬边界（越界即停并回报协调者，不自行扩）

- **禁止新模型/迁移/DDL**（`app/models.py`、`alembic/versions/` 不动；如需先升级协调者）；复用 `intake_snapshot_json` 既有 Text 列。
- **不碰**：`scripts/`（16B 域）、`app/web/`+`app/services/bag_search_service.py`+`app/services/scene_result_query.py`+`app/templates/`（16C 冻结面）、`app/scene/spray/`（12S-B 域，未建）、ros2_slice 仓库、16A 已合入行为面（只可扩既有请求字段，不改双根语义）。
- 不改 `PURPOSES`/场景枚举全局语义；spray 窄前缀 `scene-spray`。
- 真实 1012 样本仅作**只读**探针（如 Vehicle 匹配语义），不复制/不写。

## 自测口径（回执必填）

- `./scripts/local_quality_gate.sh` 或等价：定向新用例 + 全仓 SQLite 复跑（base `6fb42c4` 既有失败集为对照口径）+ ruff；merge-tree 预核与 main 零冲突面。
- **真 MySQL 8.4 隔离库**：source_metadata 快照字段读写/hash 重放/旧提交对照（本单涉 intake_snapshot_json 写入路径，隔离库口径在案；用完即毁 0 残留）。
- 回执 `receipts/TASK-12S-A/attempt-1.md`：commit sha、文件集、逐 AC 证据、MySQL 命令/退出码、越界申报。

## 后续（协调者面）

机械核验 → 串行 OCR（尺寸预检拆批）→ TESTER 12S-A 独立验证 → 合入 main → 12S-A DONE → 重算 12S-C 依赖（仍需 16B 接受）。12S-B 待 16C 安全检查点交接（16C 暂停口径下协调者另行处理，不由你预占）。