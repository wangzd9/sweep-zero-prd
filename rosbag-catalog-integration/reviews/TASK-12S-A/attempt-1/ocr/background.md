# TASK-12S-A attempt-1 OCR 背景

## 交付
base `6fb42c4`（main，07B DONE+16A 合入后）→ head `77c395b902f8b8b57276ac509e1c2dcc5ab26e90`，5 文件 +1272/−32：`app/api/ingest_submissions.py`、`app/schemas/scene_config.py`（+49 新）、`app/services/bootstrap.py`、`app/services/ingest_service.py`（+320）、`tests/test_scene_spray_intake.py`（+904，测试面）。

## 任务内容（REQ-18、14、08 / AC-18、14、08）
source_metadata 原始信息绑定 + 车辆绑定 + 新增 spray profile（不改坡道默认 `scene-isolated`）+ 提交/登记快照扩展。

## 关键不变量（审查重点）
1. 既有坡道/自建/英伟达行为零回归：`scene-isolated` 默认仍仅 scene_slice+slope；旧客户端缺新字段的兼容
2. fail-closed：车辆映射/原始信息缺失不得猜值入库；矛盾输入明确 4xx
3. 幂等：ingest-submission 既有幂等键语义不被新字段破坏（payload hash 面变化需核对已接受提交的重放行为）
4. 迁移面：本卡 diff 无 alembic 文件（协调者核 diff 确认）——若 models 变 schema 而迁移缺失=缺陷
5. 场景接收快照 `intake_snapshot_json`（16A 产物）扩展不重算已接受业务 hash

## 测试证据
开发方申报：定向全绿 + 全仓 pytest 仅 base 既有失败；协调者 TESTER 独立验证并行在途（不同槽）。

## 非本次范围
水雾识别/切片逻辑（12S-B）、正式接线（12S-C）、界面（16C 暂停）、生产部署。