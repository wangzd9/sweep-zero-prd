# 回执：TASK-07B attempt-1 统一界面·人工纠错/下架

- status: REVIEW_PENDING
- task/attempt：TASK-07B / attempt-1
- owner：B（前端功能开发群，wt-04a 系）
- 交付时间：2026-10-12 17:15 +08:00
- ACK：`inbox/2号/TASK-07B/attempt-1-ack.md`（15:01）
- base：main `502bf8e`（= origin/main；caf385b=07A 合入点为其祖先）
- HEAD：`f4bfcf2`（分支 `scene/task-07b-manual-revision-withdraw`，worktree `wt-04a-t07b`）
- commit 链（base..HEAD，2 个，均属本任务）：
  - `5fa0942` 数据面/API/页面/迁移/定向测试主体
  - `f4bfcf2` 契约修正：corrected_label 域对齐模型段判定域

## 一、文件清单（11 文件，+1235 / -4）
| 文件 | 说明 |
|---|---|
| `app/models.py` | 新增 `SceneManualRevision`（表 `scene_manual_revision`，`_BIGINT_PK`，审计列） |
| `alembic/versions/20261012_01_scene_manual.py` | 迁移（含 downgrade，逐对象 gate，revision ID ≤25 字符） |
| `app/services/scene_manual_revision_service.py` | `revise_scene_labels` / `withdraw_slice` / 审计展示 / 批量上下文（383 行） |
| `app/api/scene_manual_revision.py` | `PATCH /scene-labels` + `POST /withdraw` 两 async 端点 |
| `app/api/__init__.py` | 注册新 router |
| `app/web/bags.py` | 详情页审计上下文 + 两表单 POST handler + flash/错误回显 |
| `app/templates/detail.html` | 切片详情页人工纠错/下架双表单 + 审计区 + 已下架标注 |
| `app/templates/bags.html` | 列表已下架标注 |
| `app/static/bag-detail.css` / `bag-search.css` | 面板/标注样式 |
| `tests/test_task07b_manual_revision.py` | 定向 3 用例（570 行） |

## 二、行为（对 AC-04）
- **纠错保留原始模型结果**：只更新 `bag_scene` 有效投影 + 写 `bag_scene_label_evidence` 的 MANUAL 修订行；MODEL 证据行与 `scene_segment` 判定**绝不覆盖/删除**。
- **下架不删文件**：切片 `availability` 转 `WITHDRAWN`，退出默认可用检索（`/bags` 默认视图行消失），`view=all` 仍可见且标注「已下架」；重复下架幂等；无 re-activate 入口（普通重试不能重新上架，需走新分析/新版本）。
- **四要素**：`row_version` 冲突 409；`reason` 必填 422；幂等键重放 200 同结果（同 key 不同参数 409）；操作者证据 `X-Operator`/body `operator`（不一致 409，缺失 422）落审计可验证。
- **只接受切片**：非 `SCENE_SLICE`（含 ORIGINAL 父包）422 明确拒绝（detail 含 SCENE_SLICE）。
- **契约修正（本交付内自查）**：`corrected_label` 合法域原误硬编码 `{slope, flat, construction, congestion, night, rain, other}`（后 5 个模型不产出）→ 改为引用 `app/scene/slope/segment.py` 权威常量 `{slope, flat, unknown}`，与 TASK-04B 段判定域对齐，否则合法纠错被 422 挡。

## 三、验证证据（契约修正后口径）
- **定向 + 07A 回归**：`pytest tests/test_task07b_manual_revision.py tests/test_task07a_visibility.py` → **10 passed**（退出码 0）
- **全量**：`pytest tests` → **852 passed, 4 failed, 10 skipped**；4 failed = `test_devflow.py`×3 + `test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`×1，**均在 base `502bf8e`（stash 后）复现同样失败**，属环境性（devflow 外部沙箱 + web 性能计时），非本侧回归。
- **ruff**：`ruff check`（11 交付文件）→ **All checks passed**（退出码 0）；全仓 21 error 均为**既有** `alembic/versions/2026xxxx_*`（非本单新增），本单文件零新增。
- **alembic 单头**：`alembic heads` → `20261012_01_scene_manual (head)`
- **真 MySQL 8.4 隔离库迁移往返**（T03/T04 教训，SQLite 绿不算）：`scratch/t07b/07b_mysql_roundtrip.py`（独占容器 + 隔离库 t07b_isolated + STRICT sql_mode）→ **UPGRADE rc=0 / 边界宽度 INSERT rc=0 / 超宽 INSERT rc=1(1406 真实生效) / DOWNGRADE rc=0 / RE-UPGRADE rc=0 / CLEANUP 完成**，输出 `scratch/t07b/mysql_roundtrip_out.txt`
- **页面实测**（自包含 uvicorn + 临时 SQLite，口径同 07A，不触共享 real 栈/容器/代理/MySQL）：`scratch/t07b/07b_page_smoke.py` → **26/26 PASS**，输出 `scratch/t07b/page_smoke_out.txt`（覆盖：详情页双表单+审计区渲染、页面纠错 303→flash→操作者/原因/原值展示、页面下架 303→flash→已下架标注、默认视图行消失、all 视图行仍在+已下架标注、下架后无 re-activate 入口、row_version 冲突错误回显）

证据文件均在项目共享 `scratch/t07b/`。

## 四、未执行项 / 越界申报
- **OCR/强审查**：本角色不运行（协议：OCR 串行单独，强审查由协调者按 24h 授权判定，写接口面大概率 REVIEW_NOW）。
- **合入/推 origin**：本角色不代推；base 申报——`502bf8e` 在本地 main + github/main（= caf385b 之上 1 个纯 changelog 文档 commit，无代码差异），origin/main 此前 fetch 仍为 `caf385b`，**推 origin 动作留协调者合入面**。
- **部署/生产**：本单不改生产 compose、不操作生产数据（生产启用随 TASK-11 门禁）。
- **越界申报**：无。未触碰 03~06B 状态机/幂等/发布逻辑；未新增 `bag_record.status` 枚举值；未删除任何数据文件；测试夹具自造自清（`_purge`）。

## 五、交付后（协调者流程）
机械核验 → 串行 OCR（app 面拆批）→ 强审查判定 → 合入 → TESTER 独立验证（验收口径见派单第四节：API 四要素逐项、模型原结果仍在库、下架检索语义、迁移往返、既有套件 0 红）→ 07B DONE → 派 07C。