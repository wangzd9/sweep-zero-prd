# TEST-TASK16D 独立验证回执（attempt-1）

任务：TASK-16D 界面闭环独立验证恢复；入口 `inbox/control/V04-UI-RESUME-20261014.md`（2026-10-14T11:25:19+08:00，覆盖 UI 暂停）；派单 `inbox/TESTER/TASK-16D/attempt-1-dispatch.md`；OCR 15 项账 `reviews/TASK-16C/OCR-LEGACY-20261014.md`；验收 `ACCEPTANCE.md`（REQ/AC-16、AC-05）。
owner：TESTER（cron-tester-poll-167580c0500b-20261014-102453）。独立测试不改业务实现、不运行 OCR（归协调者 ocr_runtime.py）、不批准合入；缺陷回原 owner（A 查询面 / B Bag 视图 / C 流水线详情）。

## 固定被测输入（已确认）

- 独立测试树 seed：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（plan/v04-ui-resume-20261014）。**seed 未接受、含已知缺陷，不是已合入依赖，不宣验收 PASS**。
- 调查/生产基线（只读参照，不测移动分支）：main `63bfcf8`、生产业务 `3c9c496`。
- 专属 worktree：`/home/wang/.local/state/rosbag-scene/wt-tester-16d-20261014`（detached @ `bd0db1d`，`git status --porcelain` 干净，seed 关键文件 `app/services/bag_search_service.py`/`app/web/bags.py`/`app/web/pipelines.py`/`app/api/sources.py` 均在）。未动 seed/旧 B 冻结树(`wt-04a-t16c` 5c80857)/主仓脏文件。

## 环境预检（2026-10-14 12:3x 实测）

- 真实浏览器：`browser_exec` 可用（`example.com` title 渲染正常）；本机 `127.0.0.1:18000` 为处理机生产栈（本机不可达属预期，浏览器实测对象是本地 Compose/隔离栈而非生产）。缺浏览器才标 BLOCKED_BROWSER，当前**浏览器就绪**。
- MySQL 隔离库：seed 已有隔离 MySQL 测试先例（`tests/test_bag_cleanup_mysql.py` 等，env 形态 `*_MYSQL_TEST_URL`+`*_MYSQL_TEST_VERSION_PREFIX`，fixture 连不上/版本不符整文件 skip 而非 fail）。按 `rosbag-catalog-local-verify` 配方：docker network + MySQL 容器不带 `-p`、alembic 同网 python 容器跑 `upgrade head`、凭据走编程式 env（不落文本 `$VAR`）。**尚未起，为下一动作**。
- MySQL 隔离库：**已就绪（12:41:43 实测）**。docker network `rosbag-t16d-mysql-net` + `mysql:8.4` 容器 `rosbag-t16d-mysql`（Up、不带 `-p`、同网内网）；库 `rosbag_catalog_t16d`，`@@version=8.4.11`、32 表、`alembic head=20261013_01_scene_intake`（`python:3.10-slim` 容器 `pip install -r requirements.txt && alembic upgrade head` 实测 rc=0）。凭据编程式 env 生成（scratch `t16d_mysql_creds` chmod 600，不出现在任何文本/命令行）。配方坑已实测：本机 docker.io 直连被墙，镜像须用 `docker.m.daocloud.io/library/` 前缀（mysql:8.4/python:3.10-slim 本地已有）。
- 本地 Compose 栈（页面/API 实测用）：`./scripts/local_stack.sh up`（mock 模式；Web `127.0.0.1:8181`、Backend API `18080`；容器名 `rosbag-catalog_mysql_1`/`rosbag-catalog-local-backend-1`）。**尚未起**（C8 浏览器复现与页面/API 实测需要）。

## 复现目标（seed 已知缺陷，准备阶段复现、不修复、不下验收结论）

- C5（c02，owner A）：双用途原包显示双标签（`data_kind_labels_for` 返回 scene_original+self_built_original）却只命中单值 SQL CASE——Web/API、交集、分页。seed `bag_search_service.py:62` 与 `:313`/`:519` 可见该口径。
- C7（c03，owner A）：日期原始字符串直入 DateTime，非法值 500 与截止日偏差——隔离严格 MySQL 复现，期望非法日期 422、全天边界/时区与 Web 一致。
- C8（c05，owner C）：CANCELLED 场景无 retry-form，尾脚本 `null.querySelector` JS 异常——真实浏览器取消页无 JS 异常且不露自建强制重试。
- cursor/分类风险（16C-c03-02/03/04，owner A）：cursor 上下文漏实际筛选字段、旧 cursor scene_code None/空串兼容、Python 分类与 SQL 子包条件分叉（SCENE_SLICE 角色或有效 derivation 均可识别，含无血缘历史切片）。

## fixture 面（准备三类，脱敏最小，与真产物证据明确区分）

原始 / 双用途 / 合法无血缘历史切片 / 当前 AVAILABLE / 历史 / 待完成 / 下架 / 未知。受控 test 首包真产物（原包↔子包 UID、场景 run、受控获取、权限边界）走**只读生产 API 取证**：不新提交、不拷包、不 retry、不烧模型、不直接写库。

## 当前状态：PREP（准备阶段，无正式联合验收结论）

- 已完成：ACK、专属 worktree @ seed、浏览器就绪确认、seed 缺陷口径定位、隔离 MySQL/Compose 环境配方就绪。
- 下一动作（长工程步骤，分回合接续）：起隔离严格 MySQL 库（alembic upgrade head + 版本前缀核对）→ 建 8 类 fixture → 复现 C5/C7/C8 + cursor 风险并落复现证据（命令/退出码/DB 值/浏览器 Console）→ 准备检查点。叶 A/B/C 冻结到达后对冻结完整 SHA 做对应面独立增量验证；最终集成 SHA 由协调者提供后再联合验收。
- 并行面：原批次 TASK-11S-BATCH-1012 收尾增补卡 C1-C6 已核销闭合，TEST_REPORT_PENDING 待大包 `4acf689f` 终态；16D 准备不依赖大包，两线不冲突。

## C 叶增量独立验证（冻结 head `522bb3f`，2026-10-14 12:5x 实测）

被测：TASK-16C-C `522bb3f`（seed `bd0db1d` 之上 C 叶增量：`app/web/pipelines.py` + `app/templates/pipeline_detail.html` + `tests/test_task16cc_scene_detail.py`）。专属验证树 `wt-tester-16d-C`（detached @ `522bb3f`，与 seed 树/其他叶树隔离）。

- **pytest 独立复跑**：`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/test_task16cc_scene_detail.py -q` → **16 passed**（1.92s，退出码 0；`.venv` 软链主仓 venv，未入提交）。与 C 回执自报一致，非采信。
- **C8 浏览器面（TESTER 独有取证）**：本地 Compose 栈以 C worktree 重建（`backend`/`frontend` 镜像 12:5x build，容器内 `grep scene_terminal pipelines.py`=3 确认服务 C 代码）。自造 CANCELLED 场景 fixture（`t16d-c8-scene-cancelled01`，pipeline_run+8 step_run，`MYSQL_PWD` 编程式传递，测后删除归零已核）：
  - 页面 `/pipelines/t16d-c8-scene-cancelled01`：status=CANCELLED、**无 retry-form DOM**、**无自动刷新脚本**（SCENE 真实终态停刷新）、八步齐全、尾部脚本 guard `const retryForm=.../if(retryForm)` 在位。
  - **Console 零异常**：`Page.addScriptToEvaluateOnNewDocument` 注入 error/unhandledrejection 钩子后同 target 重载，`errors=[]` 且 `hookAlive=true`（钩子存活=证据有效）；页面尾部脚本块原地重放亦 `ok` 无抛出。
  - 夹具自造自清：`COUNT(*)` 测前 1/8 → 测后 0/0，无残留。
- **结论（仅 C 叶增量面）**：C 叶 pytest+C8 浏览器面 **PASS**（对应面验证，非联合验收、非 seed 缺陷验收；seed 固有 4 failed 口径与 C 回执一致：`test_devflow×3`+`test_web` bag_search 计时，属环境性）。C 叶 OCR（协调者 run `e7a5580c`）裁决面不属 TESTER，不代裁。
- 证据：本回执 + 下轮 session 条目；浏览器为真实 headless Chrome（browser_exec CDP），非 HTTP200 替代。

## B 叶增量独立验证（冻结 head `e399daf`，2026-10-14 13:0x 实测）

被测：TASK-16C-B `e399daf`（seed 之上 B 叶增量：`app/templates/bags.html` + `tests/test_task16cb_bag_views.py`）。专属验证树 `wt-tester-16d-B`（detached @ `e399daf`）。

- **pytest 独立复跑**：`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/test_task16cb_bag_views.py -q` → **11 passed**（1.92s，退出码 0）。用例覆盖 tab 标签/参数保留/页码重置、取消筛选 chip 保留其余条件、NVIDIA 空数据行、双用途双标一行、不相容组合空结果、详情/父包追溯/受控获取入口可达。
- **三视图浏览器取证（真实 headless Chrome）**：本地 Compose 栈以 B worktree 重建（容器内 `grep 原始数据 bags.html`=8 确认服务 B 代码）。
  - 默认 `/bags` → **切片** tab active、note「默认视图为切片（当前可用）；…旧入口书签行为不变」，三 tab href `切片=/bags`、`原始数据=/bags?view=originals`、`全部=/bags?view=all`。
  - `/bags?view=all` → active=全部，数据分类徽章分布 **英伟达原始数据×7 / 自建原始数据×11 / 场景原始数据×1 / 场景切片×1**（与 DB `bag_record` 角色分布一致，NOT_APPLICABLE 英伟达行入原始数据、无"未分类"误标）。
  - 筛选 `?view=all&data_kind=scene_slice` → 仅 **1 行（场景切片）**、`select[name=data_kind]` 值正确保留、分页摘要「第 1 / 1 页，共 1 条」——Web/API 交集筛选生效、条件保留。
- **结论（仅 B 叶增量面）**：B 叶 pytest+三视图/筛选/分页浏览器面 **PASS**（对应面验证，非联合验收）。取消条件 chip 保留其余条件、双用途双标、NVIDIA 空值由 pytest 11 用例覆盖。B 叶 OCR 排队（协调者）不属 TESTER 裁决。
- 证据：本回执 + session 条目；浏览器非 HTTP200 替代。
## A 叶增量独立验证（冻结 head `563a91a`，2026-10-14 13:3x-14:1x 实测）

被测：TASK-16C-A `563a91a`（`a1e416a` 续单，test_web.py tab 断言 1 行；查询面实现=`a1e416a` 冻结口径）。专属验证树 `wt-tester-16d-A`（detached @ `563a91a`）。

- **pytest 独立复跑（worktree SQLite 面）**：`tests/test_task16ca_query_api.py`（19）+`tests/test_task16c_ui_minimal.py`（15）+`tests/test_web.py` 转派断言面合跑，与 A 回执 74 passed+1 seed 固有失败同口径；seed 固有 `test_bag_search_page_has_bounded_query_count_and_response_time` 单跑 `no such table` 顺序依赖，不计本账。
- **A 回执明确交 TESTER 的 MySQL 关键行为独立探针（严格 MySQL 8.4.11 隔离库 `rosbag-t16d-mysql` / `rosbag_catalog_t16d`，head=20261013_01_scene_intake）→ 21/21 PASS，rc=0**（探针 `scratch/t16d_a_mysql_probe.py`，T16DMYSQL 夹具自清归零已核）：
  - C7：非法日期 `not-a-date`/`2026-13-45`/`2026/02/01` 均 raise `InvalidBagSearchState`（422/400 源头，不直入 DateTime）；`YYYY-MM-DD` end=23:59:59.999999、start=00:00:00；aware+10:00 换算业务 naive（`2026-12-02T10:00+10:00`→`2026-12-02 08:00:00`）。
  - C7 方言边界（真实 DATETIME(0) 秒精度）：全天窗口含 23:59:59 行、排次日 00:00:00 行、排前日 23:00 行；收紧到 23:59:58 排除 23:59:59 行。直接 SQL 佐证：`'…23:59:59' <= '…23:59:59.999999'`=1、`CAST('…59.999999' AS DATETIME)`=次日 00:00:00（MySQL 秒精度四舍五入，全天截止边界与注释口径一致）。
  - C5：双用途原包在 `scene_original` 与 `self_built_original` 两筛选**都命中且 UID 唯一**（MySQL IN 标量子查询方言正确）；纯 self_built 不入 scene_original；纯 scene 根（dataset_type=scene+scene_slice 用途）入 scene_original、不入 self_built_original。
  - C6：`data_kind_context` 与谓词同真相——双用途标签两类、NOT_APPLICABLE 非 NVIDIA 空标签（模板"未分类"）、NOT_APPLICABLE NVIDIA 行 `nvidia_original`。
  - 幂等：同条件复查结果一致。
- **Web/API 浏览器面（真实 headless Chrome + 本地 Compose 栈以 A 树 `563a91a` 重建；容器内 `grep data_kind_pred`=3 确认服务 A 代码；T16DCA 夹具 5 行自清归零已核）**：
  - `/bags?view=originals&data_kind=scene_original` → 命中 `t16dca-SCEN0001`+`t16dca-DUAL0001`（双标行：场景原始数据+自建原始数据），**不含** SELF0001；
  - `data_kind=self_built_original` → 命中 `t16dca-SELF0001`+`t16dca-DUAL0001`，与 DB 用途行一致；
  - `view=all&data_kind=scene_slice` → 仅 `t16dca-SLIC0001` 场景切片行（交集筛选生效）；
  - API `/api/v1/bags` 非法日期三例 **422**（非 500）；scene_original 行 `[T16DCASCEN0001, T16DCADUAL0001]`、self_built_original 行 `[T16DCASELF0001, T16DCADUAL0001]`，双用途行内 `data_kind=scene_original`（首个命中单值口径，与冻结契约一致）。
- **结论（仅 A 叶增量面）**：A 叶 pytest+严格 MySQL 关键行为+Web/API 浏览器面 **PASS**（对应面验证，非联合验收、不覆盖 seed 缺陷面）。

## C 叶 CC-R1 返修面独立验证（冻结 head `ce5921d`，2026-10-14 13:2x-14:0x 实测）

被测：TASK-16C-C `ce5921d`（`522bb3f` 之上返修：模板血缘兜底补 `<ol class="lineage">` 开始标签 1 行 + `test_no_lineage_fallback_li_in_ol` 断言同步）。`wt-tester-16d-C` 从 `522bb3f` 前移 detached 到 `ce5921d`（同验证树续用，未动 seed/其他叶树）。

- **pytest 独立复跑**：`tests/test_task16cc_scene_detail.py` → **16 passed**（rc=0）；`tests/test_task16c_ui_minimal.py` → **15 passed**（rc=0）。与 C 回执 31 passed 同口径，非采信。
- **RED→GREEN 独立复核（TESTER 自做，非引 C 自报）**：把模板单文件还原到旧版 `522bb3f`（新断言仍在）→ 目标用例 **1 failed**（开始标签缺失被捕获，rc=1）；恢复 `ce5921d` 模板 → **1 passed**（rc=0）。证断言非空转、返修真实生效。
- **浏览器面（真实 headless Chrome + Compose 栈以 `ce5921d` 重建，容器内模板血缘兜底段 + `scene_terminal`=3 确认服务 C 返修代码）**：自造无血缘 `SCENE_SLICE` run `T16DCC-LINEAGE01`（source bag 行缺失→血缘降级空 envelope 走 `{% else %}` 兜底分支，8 步全 DONE，测后删除归零 0/0 已核）：
  - 页面 `/pipelines/T16DCC-LINEAGE01` 200：`ol.lineage` 实际 DOM = `<ol class="lineage"><li class="muted">该 Bag 无场景血缘登记（非切片、无子切片）。</li></ol>`（**开始标签在位**，CC-R1 修复面渲染实证）；status=SCENE_DONE、无 retry-form、无 refresh meta、无 setInterval（终态停刷新保持）。
  - **Console 零异常**：`Page.addScriptToEvaluateOnNewDocument` 注入 error/unhandledrejection 钩子后同 target 重载，`errors=[]` 且 `hookAlive=object`（钩子存活=证据有效）。
- **结论（仅 C 叶返修面）**：CC-R1 增量 **PASS**（对应面验证；此前 C 叶 `522bb3f` 增量 PASS 口径不变，本段只覆盖返修 diff 两小面）。协调者对 `ce5921d` 的独立 diff 核与 C 叶 OCR 面不属 TESTER，不代裁。
- **C 叶接受事件（2026-10-14 14:24，观测）**：协调者落盘 `inbox/coordinator/TASK-16C-C/leaf-acceptance-decision-20261014.md`——C `ce5921d` **开发叶收口（未合入主分支）**，本叶承担 8 条遗留账（C1/C2/C3+c05-03/C8/C9/c05-04/c05-05）处置成立（OCR 面+TESTER 面双证）、C4 维持驳回；父 16C 聚合接受仍需三叶齐+固定集成候选联合验收。TESTER 面证据=本回执 C 叶/返修面两段（pytest 独立复跑、RED→GREEN、真实 Chrome DOM+Console 零异常），口径与决策一致，无分歧。

## 准备面收尾核对（cursor 三项口径，2026-10-14 14:5x）

- **c03-02（cursor 上下文漏实际筛选字段）/c03-03（旧 cursor scene_code None 与空串）/c03-04（Python 分类与 SQL 子包条件分叉）**：实现面在 A 树 `563a91a` 的 `app/services/scene_result_query.py`（base64(JSON) cursor=排序锚点+全部实际筛选字段上下文；换筛选 422 不复用错误上下文；历史 cursor 无新键按旧口径兼容；scene_code None/空串归一）与 `tests/test_task16ca_query_api.py` 19 用例（`test_cursor_chain_no_gap_no_dup`/`test_cursor_with_changed_filter_422`/`test_legacy_cursor_without_new_keys_accepted`/`test_legacy_cursor_scene_code_none_equivalent_empty` 等）——**已由本回执 A 叶段独立 pytest 复跑（74 passed 同口径，非采信 A 自报）覆盖**，准备阶段无新增探针需求；c03-04 的 SCENE_SLICE 角色/有效 derivation 分类一致性另由 21/21 MySQL 探针 C6 面（`data_kind_context` 与谓词同真相）交叉覆盖。
- **保留到联合验收固定 SHA 段**：cursor 矩阵在两查询入口的真实行为（换条件 422/连续翻页无漏无重/旧 cursor 兼容）+严格 MySQL 日期/分类方言，按派单联合矩阵在含 seed+三叶的固定集成 SHA 上执行，不提前。