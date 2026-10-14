# TASK-12S-A attempt-1 交付回执

- **task/attempt：** TASK-12S-A / attempt-1（v0.5 水雾原始信息绑定，scene-input/v1 source_metadata）
- **owner：** 执行者 A
- **分支 / worktree：** `a/task-12s-a-spray-intake` @ `/home/wang/.local/state/rosbag-scene/wt-01-t12sa`
- **base / head：** `6fb42c4` → `77c395b902f8b8b57276ac509e1c2dcc5ab26e90`
- **状态：** REVIEW_PENDING（开发自测完成，待 OCR/强审 + 测试者独立验证；**未合入**）

## 文件清单（5 改/新增，1272 增 / 32 删）

- `app/schemas/scene_config.py`（+49）：新增 `SourceMetadataSchema`（scene-input/v1，extra=forbid，IANA 时区 `ZoneInfo` 校验）；`IngestSubmissionRequest` 增可选 `source_metadata`；`__all__` 导出。
- `app/api/ingest_submissions.py`（±18）：POST 透传 metadata；PATCH body 增可选 `source_metadata`（None=显式删块），空更新提示含 source_metadata。
- `app/services/ingest_service.py`（+320）：核心实现（见下）。
- `app/services/bootstrap.py`（±13）：`seed_default_ingest_profile` 幂等调用 `seed_scene_spray_profile`，能力未接受不崩。
- `tests/test_scene_spray_intake.py`（新增 904 行，25 测试）。

## 行为（对应 AC）

- **AC-18.1** 接受时 `resolve_source_metadata_vehicle`：spray 入口（`incoming_prefix=="spray"` 语义判定，不绑 profile_id 字面量）必填，vehicle_code/sensor_profile 必须可解析；不猜车、不自动建 Vehicle；未知车辆/未知 sensor/缺字段 → 422。旧入口 metadata=None 恒零变化，携带块同样校验块内引用。
- **AC-18.2** intake_snapshot 增 `source_metadata` + 独立 `source_metadata_hash`，与 16A config_hash 分离（旧提交无块时与既有快照逐字节一致）；绑定/恢复登记 `_apply_frozen_vehicle_binding` 按冻结快照覆盖车辆，MANUAL 不篡改，目录名 basename 与冻结矛盾 → 409 回滚 fail-closed。
- **AC-18.3** `seed_scene_spray_profile` 幂等种子 scene-spray（root=scene、prefix=spray、默认 scene_slice+spray），能力未接受 enabled=False，bootstrap 不崩。窄前缀隔离沿用既有两遍匹配（非空优先于同根空兜底）。

## 关键裁决（开发中纠正的两处越界，均已在提交前回退/收窄）

1. **`_disabled_prefix_claims_path` 回退**：初版为"disabled spray 前缀认领 spray/ 路径停待处理"，破坏了 base 既有 `test_ingest_config.py::test_disabled_profile_not_matched`（disabled 窄前缀应回退同根 default 兜底）。AC-18.3"窄前缀不抢坡道"本由 active 两遍匹配天然保证，disabled 不进活动集、回退口径不变。已删该函数、恢复 base 语义，测试改为验证 disabled 回退口径。
2. **spray 必填判定口径**：初版 `profile_id=="scene-spray"` 魔法字面量，测试用独立 profile_id 时失效。改为 `incoming_prefix=="spray"` 语义判定（生产 profile_id 即 scene-spray，测试可复用同入口行为）。

## 自测证据

- 命令：`.venv/bin/python -m pytest tests/test_scene_spray_intake.py -q`
  - 退出码 0，**25 passed**（独立跑与全量套件顺序跑均绿）。
- 既有回归：`pytest tests/test_ingest_config_api.py tests/test_ingest_config.py tests/test_ingest_frozen_hash.py tests/test_scene_config_schemas.py tests/test_scene_intake_isolation.py` → **78 passed**，无回归。
- ruff：`python -m ruff check app/ tests/test_scene_spray_intake.py` → **All checks passed**。
- 全量套件：`pytest tests/` → **908 passed, 10 skipped**；仅剩 4 个**既有**失败：`test_devflow.py`×3 + `test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`×1，均在干净 base（`git stash` 后）复现，与本单无关。
- 测试隔离要点：TestClient 走 get_db 独立 session，seed/vehicle 需 commit 可见；teardown 删 Vehicle 前须先删引用它的 bag（bind 测试 bag name 为 rosbag2 时间戳 leaf，单 name 前缀删不净）——否则全量顺序下跨测试 FK 约束报错。

## 未执行项

- 未跑 OCR / 付费强审查（执行者边界）。
- 未合入主分支（门禁关闭，待协调者调度）。
- 未做真实 MySQL / A100 生产验证（本单 P0 本地 SQLite 口径；TESTER 独立验证另跑）。
- sensor_profile 批准名单当前为单一占位值 `seyond-front-mid-approved-v1`（env `SPRAY_SENSOR_PROFILES` 可覆盖）——真实名单待数据方/协调者给，非本单阻塞。

## 越界申报

- 无生产写、无主分支合入、未改 TODO/HANDOFF/DESIGN/decision/其他角色目录。
- 仅写本任务 4 个 app 文件 + 1 个新测试文件。