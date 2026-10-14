# 回执：TASK-07A attempt-1 统一界面·可见性与检索（P1 提前，用户授权）

- status: **REVIEW_PENDING**
- task/attempt：TASK-07A / attempt-1
- owner：cron-b-poll-6f7471d8747c-20261012-094753（执行者 B，前端功能开发群）
- base：`453da0c`（= origin/main，ACK 时双核一致）
- head：`f94d006`（`f94d0062acb7b5431e386d9cfd99ed8d9c3a85ba`，单 commit，11 文件 +905/-30）
- 分支/worktree：`scene/task-07a-visibility-lineage` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07a`
- 交付时间：2026-10-12 11:17 +08:00（cron 巡检回合，preflight checked_at 2026-10-12T09:47:53+08:00，本回合 11:14 续做）
- 详细报告：`reports/TASK-07A/attempt-1.md`（页面实测证据 + 回归 + 越界申报）

## 一、文件清单（逐文件行为）

1. `app/services/scene_result_query.py`（+100）
   - 新增 `bag_lineage_view(db, bag_uid) -> dict`：恒定 envelope `{bag_uid, lineage, children}`。
   - 切片视角 lineage：parent_bag_uid/parent_name/parent 摘要（名称/路径/状态/时长）、slice_key、scene_code、run_id、analysis_version、config_hash、label（SceneSegment）、duration_ns、created_at。
   - 原始包视角 children：每个 child 的 bag_uid、scene_code、slice_key、duration_ns、availability、current（SceneAnalysisVersion.current）、analysis_version。
   - 非场景包：`{lineage: None, children: []}` 200（不 404）；不存在的 bag 404。
   - 数据源=既有 `bag_derivation`+`scene_analysis_version`+`scene_segment`+`bag_record`，**零新表/零迁移**。
2. `app/api/sources.py`（+8）
   - 挂接 `GET /api/v1/bags/{bag_uid}/lineage` 路由 + Pydantic schema。
3. `app/services/bag_search_service.py`（+169/-6）
   - `BagSearchState` 增 `view`（slices 默认/originals/all）、`purpose`（scene_slice/self_built）、`scene_code`、`current_only`；`normalize()` 校验非法 view/purpose → 400（purpose 校验从查询期前移，杜绝 500）。
   - `to_query_pairs()`：view 仅非空且非 slices 时输出（URL 极简，slices=裸 `/bags`）；purpose/scene_code 透传。
   - stmt 过滤：slices=SCENE_SLICE+AVAILABLE+current 版本 exists；originals=ORIGINAL 父包（purpose 限定用途）；all=不区分角色/版本（历史标注）。
   - 新增 `scene_view_page_context(db, page_bags)`：按本页 bag_uid 一次有界批量查（derivation+父包摘要+current 标记+segment label），无 N+1。
   - `build_active_filters` 补 scene_code 标签。
4. `app/web/bags.py`（+17）
   - `bag_list` 接 `view/purpose/scene_code` 参数；render 传 `scene_context`/`scene_codes`。
   - `bag_detail` 增双向跳转上下文：切片→父包卡片；原始包→场景状态区（场景→状态→切片数）。
   - all 视图跳过 scene_code 候选查询（模板不渲染该下拉，省一条 SQL）。
5. `app/templates/bags.html`（+44/-10）
   - 视图 tab 行（`当前可用切片`→`/bags`、`原始包`→`/bags?view=originals`、`全部/历史`→`/bags?view=all`）。
   - GET form 加 `hidden name="view"`：从 originals/all 提交筛选不回落 slices。
   - 新增 场景(scene_code)/用途(purpose) 筛选下拉（all 视图隐藏场景下拉）。
   - 表格 8→9 列（新增场景列 `col-scene`），detail 行/空态 `colspan="9"`。
   - 数据来源 badge：切片行显"场景切片"，非切片行保持"自建数据集/NVIDIA 数据集"既有文案（不回归）。
6. `app/templates/pipelines.html`（+6/-2）
   - 状态过滤加 `SCENE_SLICE_QUEUE/SCENE_RUNNING/SCENE_DONE`。
   - 数据类型列 `pipeline_type == 'SCENE_SLICE'` → "场景切片"徽标（判定在 nvidia 之后、自建之前）。
   - 取消按钮条件加 `SCENE_SLICE_QUEUE`；失败走既有 `/retry`（**不改状态机守卫**）。
7. `app/templates/detail.html`（+10）
   - 切片详情：父包追溯面板（父包卡片可点击跳父包）+ 生成版本（analysis_version + config_hash 前 12 位短显）。
   - 原始包详情：场景结果面板（场景→状态→切片数，点切片跳 `slices` 视图）。
8. `app/static/bag-search.css`（+84）
   - view-tabs/场景列/详情场景面板样式。
9. `tests/test_web.py`（+41/-25，**断言语义保留**）
   - 18 处 `client.get("/bags")` 中列举原始/NVIDIA/demo 包的用例显式改 `/bags?view=all`（旧"全部数据"语义在新默认下需显式声明，**未删断言、未弱化**）。
   - `test_bag_list_shows_default_results_and_route_filter` 改写为断言新契约：默认=当前可用切片（view-tabs 在、demo 原始包不在默认、在 view=all 在）。
10. `tests/test_bag_cleanup_web.py`（+10/-4）：同上，列举原始包用例显式 `view=all`。
11. `tests/test_task07a_visibility.py`（新增 446 行，6 用例）
    - lineage 双向+非场景包 200 null+不存在 404；三视图（默认排除 PENDING/非 current、originals 父包+场景列、all 全含）+非法 view 400；场景/用途筛选+非法 purpose 400；/pipelines 场景状态可见+取消+retry+父包跳转；详情双向跳转+生成版本+config_hash 短显；旧入口书签（/nvidia、/ingest、/pipelines、`view=all&dataset_type` 组合）不回归。
    - 夹具自造自清（共享 SQLite 库下 `_purge` 按 FK RESTRICT 链删除：der→seg→ver→purpose→bag→run；version/segment 删除前查引用计数防误删其他用例行）。

## 二、自测证据（真实执行）

- 环境：worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t07a`（venv 软链主仓 `.venv`，提交前已删）；Python 3.10；SQLite 测试库。
- `pytest tests/test_task07a_visibility.py` → **6 passed**（RC=0）。
- `pytest tests -k "scene or web or bags or pipeline"` → **328 passed, 534 deselected**（RC=0）。
- `pytest tests -q`（全量）→ **849 passed, 10 skipped, 3 failed**；3 failed 全在 `tests/test_devflow.py`（`test_external_sandbox_hides_home_and_only_binds_task_dirs`/`test_worker_resolves_codex_without_interactive_path`/`test_external_sandbox_binds_main_repo_git_for_worktree`），根因 = worktree 的 `.git` 是文件而非目录，devflow 沙箱按目录存在性检查主仓库 → **环境问题非回归**（同文件在主工作区 `/home/wang/work/rosbag-catalog` 跑 → 24 passed RC=0，已核实）。
- `ruff check app tests` → **All checks passed**（RC=0）。
- 页面实测（自包含 uvicorn，临时 SQLite `/tmp/t07a_smoke.db`，DEMO_DATA=0，场景夹具 parent/cur/pend + SCENE_DONE/SCENE_SLICE_QUEUE run）→ **12/12 页面 200 且 innerText 断言全过**：/bags 默认视图（view-tabs+当前切片+场景列+父包链接）、view=originals、view=all、view=slices&scene_code、/pipelines?status=SCENE_DONE（3 个场景 option+场景切片徽标+run 行）、/pipelines?status=SCENE_SLICE_QUEUE（取消入口）、lineage 切片视角/原始包视角（JSON 字段完整）、切片详情（父包追溯+生成版本+c*12+获取数据）、原始包详情（场景结果+切片数+slices 视图跳转）、/nvidia、/ingest、/pipelines 旧入口。
  - **证据文件**：`scratch/t07a_page_evidence.txt`（已随本回执附关键片段，全文 12 段 OK 清单）。
  - **越界申报（页面实测口径）**：ACK 原计划"本地 real 栈（453da0c 已 up）DB 口径实测"；开工时核实共享 real 栈（rosbag-catalog-local-*，:18080/:8181/MySQL 8.4）**有 1 个 RUNNING run + 3 个 NVIDIA_DONE 在途**，`local_stack.sh up`（real 模式）会 restart 两个宿主代理（systemd 服务），有打断活动 run 风险（local-verify skill 明示该坑）。故改用**自包含 uvicorn 实例**（独立端口 18642、独立临时 SQLite、场景夹具），对同一份 worktree 代码做真实 HTTP 渲染断言，不触碰共享栈/容器/代理/MySQL。该口径覆盖派单 2.5 三项（/pipelines 可见 SCENE_DONE run ✓、/bags 切片视图可见 fixture 子包 ✓、lineage 200 ✓）；共享 real 栈上的复测（若 TESTER 需要）由测试者在无活动 run 窗口执行，非本侧阻塞。

## 三、AC 达成对照（派单 §四口径）

- lineage API 双向查询 200 + 字段完整 + 非场景包 200 null：**达成**（定向测试 + 页面实测 JSON）。
- /pipelines 造 SCENE_DONE run 后页面可见且筛选生效：**达成**（option 可见、run 行渲染、状态筛选、取消/retry 入口）。
- /bags 三视图切换、场景/角色筛选、父↔子跳转闭环、旧入口书签不回归：**达成**（视图=当前可用切片/原始包/全部历史；筛选=场景 scene_code+用途 purpose；角色区分内嵌于三视图语义（slices 仅切片行、originals 仅父包行、all 混合）未做独立 bag_role 下拉——**待核对**：派单 2.3 列举"角色（bag_role：原始/切片/自建）"筛选，当前实现以三视图 tab 覆盖原始/切片维度、all 视图+数据类型下拉覆盖自建维度，未加独立 bag_role 参数；如协调者认定需要独立下拉请裁决，不改契约前先按现状交付）。
- 既有 Web 测试套件 0 红：**达成**（过滤组 328 passed；全量 849 passed，3 failed 为 worktree devflow 环境问题非本任务，主工作区同文件 24 passed）。

## 四、停止条件与后续

- 已冻结：`f94d006`（单 commit，未推送，等协调者合入）；worktree 洁净（`.venv` 软链已删）。
- 等协调者：机械核验 → 串行 OCR（app 面）→ 合入 → TESTER 页面+API 独立验证 → 07A DONE → 派 07B。
- 不越界：未跑 OCR/付费强审查、未合入、未动生产 compose/real 栈、未做 07B/07C 范围（纠错/下架/预览）、零新迁移。