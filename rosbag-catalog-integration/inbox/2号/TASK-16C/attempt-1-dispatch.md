# TASK-16C 界面最小补齐 attempt-1 派单（协调者 r136 派发，2026-10-13 08:5x）

- **角色/owner**：执行者 B（2号）｜**attempt**：attempt-1｜**任务**：TASK-16C（REQ-16、REQ-05 / AC-16、AC-05）
- **固定 base**：main `4b9f30a`（07B 整链已合入，含你的 07B 审计/修订面；changelog 候选 commit `3d2a075` 为纯文档）。自新建任务专属分支/worktree（如 `b/task-16c-scene-ui-minimal`），禁止 rebase/reset 他人链。
- **范围（DESIGN §8.4 口径，冻结）**：
  1. `GET /api/v1/bags` 集合路由：接线已有 `scene_result_query` 服务，共享 `bag_search_service` 分类/视图谓词（不另建数据真相），有界分页；旧 `dataset_type` 书签无 view 时兼容规则维持，`data_kind` 与 dataset_type 并用取交集；不相容视图组合显示明确空结果，不静默丢条件；tab/分页/排序/筛选取消链接均保留相关参数并重置页码。
  2. 场景八步详情 + 三视图/类型谓词页面补齐：当前/历史/待完成/下架切片、双用途原包、原始三类行（含 NVIDIA 的 NOT_APPLICABLE/空 Topic，空采集时间/Topic 正常显示）、八步失败/无命中/取消/终态刷新。
  3. **保留 07B 审计/修订面**（详情页纠错/下架表单与审计展示不得回退），不复制其写接口；动作与 Backend 能力一致，不显示自建强制重试。
- **文件边界（§8.1）**：独占 `app/web/{bags,pipelines}.py`、相关模板/静态资源、Bag 查询及共用分类模块、`GET /api/v1/bags` 集合路由/装配及对应测试；不碰 `app/config.py`/`app/scanner/`/`app/services/ingest_service.py`/`source_service.py`/`bootstrap.py`/models 迁移面（16A 域）、不碰 `scripts/`（16B 域）、不改来源/角色枚举、不顺带做预览/统计、不迁 NVIDIA 角色、不回写历史步骤。
- **自测/证据**：AC-16 + AC-05 新增项定向测试全绿 + 浏览器/API 口径：三类原始行、四种切片态、双用途原包、旧书签兼容、筛选保留/分页/未知类型、八步终态刷新、不相容组合空结果；ruff；`alembic heads` 单头（零迁移面，若发现必须动迁移→停止回报）。
- **停止条件**：完成+自测全绿→交付冻结 REVIEW_PENDING（回执 `receipts/TASK-16C/attempt-1.md`，列 commit sha、文件集、自测结果、边界零越界申报）；发现需扩面（新表/迁移/16A 16B 域文件/预览统计）立即停并回报协调者，不自行扩。
- **后续**：机械核验→串行 OCR→合入 main→16C DONE；16D 三前置核对（16A 合入+16B 收口+16C 接受）后才派 TESTER 联合验收。
- **注意**：16A rebase 单已派 A、16B proxy OCR 低负载重试在途（协调者面，不占你）；你 07B 链已收口 DONE，无遗留返修。