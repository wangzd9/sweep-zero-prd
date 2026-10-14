# 回执：TASK-16C attempt-1 界面最小补齐

- status: REVIEW_PENDING
- task/attempt: TASK-16C / attempt-1
- owner: B（执行者B·前端功能开发群）
- 派单：`inbox/2号/TASK-16C/attempt-1-dispatch.md`（协调者 r136，§8.4 口径）
- base: main `4b9f30a`（07B 冻结合入点，派单指定）
- 分支/worktree: `b/task-16c-scene-ui-minimal` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t16c`
- 交付 commit: **`ad37ae1`**（8 files, +957/−33）
- 交付时间: 2026-10-13 09:59 +08:00
- 范围声明: 只改本单指定文件边界（§8.1：bags 检索/展示、集合 API、pipeline 详情 scene 分支）；**不碰 07B 冻结面（审计/修订/withdraw API）、不改 scene_slice_service 行为面、不部署生产、不加 DB 列**（data_kind 为计算谓词）。

## 一、交付物清单
| 文件 | 类型 | 说明 |
|---|---|---|
| `app/services/bag_search_service.py` | 改 | `DATA_KINDS`/`DATA_KIND_LABELS` + `data_kind_case()`（SQL CASE 单值分类，独立标量子查询+`in_` 表达存在性，规避 outerjoin/API 两入口 auto-correlation 丢 FROM）+ `originals_view_condition()`（三类原始共享谓词：含英伟达输入记录 NOT_APPLICABLE 角色、排除场景子切片）+ `data_kind_context()`（本页行多标签，一次有界批量查询，双用途原包双标、未知历史不猜类型）；`BagSearchState.data_kind` 全链路（normalize/query_items/_apply_filters/active filters），不相容组合明确空结果不静默丢条件 |
| `app/services/scene_result_query.py` | 改 | `search_scene_bags` 接共享谓词 + data_kind/dataset_type/purpose/时间边界过滤；`_bag_summary` 加 data_kind 字段；行级单一规范分类（优先级 slice→nvidia→scene_original→self_built_original，与 CASE 同口径）；cursor 上下文一致性（历史 cursor 兼容、不一致 422）；修既有 `vehicle.name`→`vehicle_code`（集合路由首触真实车辆行的潜在崩溃） |
| `app/api/sources.py` | 改 | 新增 `GET /api/v1/bags` 集合路由（置于静态 `/bags/{bag_uid}` 之前，路由顺序已验证）：view=slices/originals/all、data_kind、dataset_type、purpose、vehicle_id、时间边界、cursor、limit（clamp 50..200，超限收敛非 422） |
| `app/web/bags.py` | 改 | `bag_list` 加 `data_kind` 参数接线；模板上下文加 `data_kind_ctx`/`data_kind_labels`（双用途双标） |
| `app/templates/bags.html` | 改 | 视图 tab 文案恢复 PRD DEC-06 口径（当前可用切片/原始包/全部/历史）；「数据分类」筛选下拉（四类）；「数据来源」td 多标签 badge（未分类兜底，替换原单标签 sc._role 逻辑） |
| `app/web/pipelines.py` | 改 | 场景八步详情：`_scene_phase_summary`（SCENE_STEP_NAMES 真实 StepRun 构建中文总览；未开始/已跳过（无需）/失败/执行中按真实状态，**不伪标完成**）；`_scene_outcome` 以快照 `scene_outcomes` 为第一真相（SCENE_DONE≠SUCCESS，NO_MATCH/NOT_APPLICABLE 区分），run 状态/事件 payload 兜底；`_scene_environment_paths`（模型端点/处理机输入/场景 NAS 路径，**无 A100 面**）；scene 血缘 `bag_lineage_view` 降级不阻断（源 bag 行缺失时）；场景 run 动作面（取消/重试按场景队列真实支持） |
| `app/templates/pipeline_detail.html` | 改 | 按 `pipeline_type` 分支（**不用 source_id 前缀/dataset_type 推断**）：场景运行环境区 + 数据血缘区（切片→父包/父→子切片，复用 07A lineage envelope）；非场景面板（A100 运行环境/文件与日志）scene 不渲染；八步终态（SCENE_DONE/SCENE_FAILED/SCENE_PARTIAL_FAILED）停止 10s 自动刷新，非终态沿用 |
| `tests/test_task16c_ui_minimal.py` | 新增 | 15 用例（详见下） |

## 二、场景八步详情口径（§7.3.3 关键行为）
- 八步中文名固定：输入检查/解码/抽帧/模型识别/区间生成/切包/产物校验/NAS 发布/登记/完成（PRECHECK→REGISTER）。
- 未启动后继步骤=「未开始」，run 终态 SUCCESS 不回填伪完成（断言：阶段总览 status 计数=真实完成步数）。
- NO_MATCH/NOT_APPLICABLE：区间生成及之后无需步骤=「已跳过（无需）」，运行级结果展示 NO_MATCH（不标 SUCCESS）。
- 失败步骤保持真实错误文本（`model timeout: connection refused` 原样透出）。
- 终态页无 `location.reload` 自动刷新；非场景页面行为不变。

## 三、自测证据（命令/退出码/环境）
环境：wt-04a-t16c，`.venv`（Python 3.10，符号链接主仓 venv），SQLite 临时库（conftest 统一 DATABASE_URL），DEMO_DATA=1。
| 命令 | 退出码 | 结果 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_task16c_ui_minimal.py -q` | 0 | **15 passed**（集合路由 7：默认 slices 视图/双用途 data_kind 过滤/交集与不相容空结果/422/limit clamp/cursor 不一致 422/cursor 历史兼容 + 谓词与双标 4：四类 CASE/originals 含英伟达 NOT_APPLICABLE/双用途双标/未知历史不猜 + 八步详情 4：SUCCESS 全步/部分完成不伪标/NO_MATCH 跳过/FAILED 真实错误） |
| `.venv/bin/python -m pytest tests/ -q`（全仓） | 1 | **876 passed, 4 failed, 10 skipped**；4 failed 全部为 base 既有：`tests/test_devflow.py`×3（**git stash 基座复跑同样 3 failed**，与本变更零关联）+ `tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`（**git stash 基座单跑同样 failed**：共享库缺表/时序，REVIEW-T09 既有顺序污染族）。本单 15 用例在全量顺序跑中全绿 |
| `.venv/bin/python -m ruff check app/… 6 文件` | 0 | **All checks passed** |
| `.venv/bin/python -c "from app.main import app"` | 0 | IMPORT_OK；路由顺序 `/api/v1/bags` 先于 `/api/v1/bags/{bag_uid}` |

## 四、关键断言与契约点
- Web 与 API 两入口**同一谓词**（`data_kind_case`/`originals_view_condition` 同源），分类口径不分裂。
- 双用途原包：筛选走单值 CASE（scene_original 优先），行展示走多标签 context（两标并置）。
- `data_kind` × `dataset_type` 不相容组合（如 self_built+nvidia_original）→ 200 `items=[]`，不 500 不丢条件。
- 未执行项：独立 MySQL 8.4 实测（SQLite 测试不覆盖 MySQL DDL；本单无迁移/DDL 变更，仅 SELECT 谓词，风险低）；页面浏览器人工走查（测试者独立验证范围）。
- 越界申报：无。`vehicle.name`→`vehicle_code` 属集合路由首触路径的潜在崩溃修复（既有 `_bag_summary` 缺陷，非本单引入），如协调者认为越界可单独摘除。