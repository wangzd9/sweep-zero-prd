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

## 联合验收固定 SHA `29bd1f4`（2026-10-14 18:3x-18:5x +08:00，TESTER attempt-1）

**被测树**：`/home/wang/.local/state/rosbag-scene/wt-coord-intcheck-16c` @ `29bd1f4`（detached 干净，仅 `.venv` 未跟踪；git log = seed `bd0db1d2` + C `ce5921d` + B `e399daf` + A cleanup `1489bc6`）。运行版本 header 实证 `29bd1f49`（浏览器 `pipeline_detail.header_text`）。

**范围**（派单 `inbox/TESTER/TASK-16D/attempt-1-integration-29bd1f4-dispatch.md` 17:5x）：只做联合面 + A 清理增量，不重复各叶已 PASS 的增量面。

### 1. A 清理面增量确认

- `grep -c "def data_kind_case" app/services/bag_search_service.py` = **0**（A-OCR-1 死函数已删，实证）。
- 源码 line 664：`view_label = {"originals": "原始数据", "all": "全部"}.get(state.view, state.view)`（A-OCR-2 + R1-2 同口径；`slices` 视图不渲染该 chip = 设计一致，`test_web.py` 断言绿）。
- `scene_result_query.py` diff `ff2a005..29bd1f4` = **空**（A 清理未动第二查询入口谓词面，R1-2 chip 修复点仅在 A 独占文件）。
- 定向 pytest `tests/test_web.py tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py` = **74 passed + 1 failed**（唯一失败 `test_bag_search_page_has_bounded_query_count_and_response_time` = 派单注明 seed 固有 bounded-query N+1，11 SQL > 8 阈值，不计本账）。
- 浏览器 `/bags?view=originals`（真实 headless Chrome CDP，`29bd1f4` Compose 栈重建）：已选筛选 chip 区 DOM 内 **`has_chip_view_label=true`（「视图：原始数据」在位）+ `has_old_view_label=false`（「视图：原始包」已消失）**；同 target `location.reload()` 后 `hookAlive=true`（`Page.addScriptToEvaluateOnNewDocument` 注入的 onerror/unhandledrejection 钩子存活）+ **`errors=[]`**（Console 零异常，证据有效）+ `chip_now=true/old_chip_gone=true`（重载后一致）。表 36 行渲染正常。

### 2. cursor 矩阵（严格 MySQL 8.4.11 方言，隔离 `rosbag-t16d-mysql`，非 SQLite 外推）

自造 11 行夹具（7 self_built originals staggered + 1 scene parent + 3 AVAILABLE slices 带 derivation，UID 前缀 `T16DCURS`）；探针 `t16d_joint_cursor_probe.py` 容器内跑 `search_scene_bags`（入口一 `/api/v1/bags`）与 `lineage`（入口二 `/api/v1/bags/{uid}/lineage`）：

- 入口一 `view=all` 连续翻页 limit=3：`pages=4`，`len=11 uniq=11` **无漏无重**（含 3 切片 + 7 originals + 1 parent）。
- 换 `data_kind`（self_built_original→scene_original）→ **422**「cursor 筛选上下文不一致：data_kind」；换 `view`（originals→all）→ **422**「...不一致：view」；同筛选续页 → **200** 且链合并 **无重复 UID**（`006/005/004/003/002/001`）。
- 旧 cursor（仅 `ts/uid` 锚点无筛选新键）→ **200 兼容**（`items=3`），锚点生效（`UID(99)` 本身不在续页结果）。
- `scene_code` 省略 vs 显式 `None` 同义；空串与 `None` 归一同义；`scene_code=spray` 命中 3 子包 = 夹具 `child_ids`。
- 入口二 `lineage` 父包：第 1 页 2 子包 → 同包续页 200 → 合并 **无漏无重（3 子包）**；子包视角返回 `parent=T16DCURS000050`；换 `bag_uid`=新查询（**设计口径**：lineage cursor 仅 `{ts,uid}` 排序锚点、无 bag 身份字段，换 bag 返回新 bag 自身视角、不串 UID(50) 子包列表，断言按此核）；**非法 cursor（base64 非 JSON）→ 422**（两入口均，不 500）。

**矩阵 20/20 PASS**（`purge verify left bags=0 deriv=0`，夹具自清归零）。

### 3. 严格 MySQL 8.4.11 方言（复用 `rosbag-t16d-mysql` 隔离库，探针 `t16d_joint_mysql_probe.py`）

C7/C5/C6 谓词面在 `29bd1f4` 树（非 A 单叶树）上复跑：**21/21 PASS**（`C7 非法值 not-a-date/2026-13-45/2026-02-01 raise`、`date end=23:59:59.999999`、`aware+10 换算 naive`、`C5 双用途两筛选 UID 唯一`、`C6 分类真相 NOT_APPLICABLE 空标签/NVIDIA 行`、幂等复查）；`purge rc0 rows=9`，`END pass=21/21 fail=0`，rc=0。确认 A 清理未改变谓词语义。

### 4. 浏览器 Console 零异常（同 target 重载，钩子存活）

真实 headless Chrome（`google-chrome --headless=new --remote-debugging-port=9333`，专属 user-data-dir，非 HTTP200 替代）：

- `/bags?view=originals`（三 tab + chip）：`hookAlive=true` + **`errors=[]`**。
- `/bags`（默认 slices 视图）：`hookAlive=true` + **`errors=[]`**。
- `/pipelines/scene-e46f28c2ce1c4313a2c4ce4e8e71`（血缘兜底 + 终态停刷新）：`hookAlive=true` + **`errors=[]`**；`ol.lineage` 在位（1 子包 slope 切片带 `场景 slope · 切片键 slope:... · AVAILABLE` 血缘）；`has_refresh_meta=false` + `has_retry_form=false` + `setinterval_calls=0`（终态停刷新保持）；`status_badge=[SCENE_DONE, SCENE_DONE]`、`header_text` 平台版本 `29bd1f49`。

### 结论

- 联合验收清单 4 项（A 清理增量 / cursor 矩阵两入口 / 严格 MySQL 21/21 / 浏览器 Console 零异常）在固定集成 SHA `29bd1f4` 上**全部 PASS**；seed 固有 bounded-query N+1 一项按派单口径不计本账。
- 三叶（A `1489bc6` cleanup / B `e399daf` / C `ce5921d`）在含 seed 的固定集成候选上联合行为一致，无跨模块回归；**TESTER 联合验收面 PASS**，允许合入的前置测试门禁满足（合入批准/OCR 门禁仍归协调者，TESTER 不代裁不批准）。
- 夹具 `T16DCURS` 11 行 + `T16DMYSQL` 9 行均自清归零（purge 后 `left bags=0/deriv=0/rows=0` 实证）；全程只读 DB 探针 + 自造夹具自清，不改 seed/其他叶树/业务实现，未运行 OCR。
- 浏览器 target 复用首启 about:blank page；Chrome 后台进程 pid 4040391（在途服务，非本角色独占，结束后不 kill 避免影响他角色）。

**未测项（如实列，不外推）**：生产处理机/生产 MySQL/真实 NAS 根/受控 test 首包真产物 UID 血缘获取/大包跨 DB3/07C 预览/其他场景/统计/MN——均按派单与 12S-D 口径独立，不在本轮联合验收范围。

## A 叶 R1-3 F1 增量独立验证（冻结 head `8958291`，2026-10-14 19:1x +08:00，TESTER attempt-1 续 F1 单）

派单 `inbox/TESTER/TASK-16D/f1-incremental-8958291-dispatch.md`（协调者 19:12，A 叶 R1-3 F1 返修的 TESTER 独立行为面门禁，**不采信协调者探针**，TESTER 独立复现）；被测冻结 head `8958291`（`wt-01-t16ca` / `a/task-16c-a-query-api`，base `1489bc6`，仅 `app/services/bag_search_service.py` +18/−10）。专属验证树 `wt-tester-16d-A` 从 `563a91a` 前移到 `8958291`（同树续用，detached 干净，仅 `.venv` untracked）。

- **环境（严格 MySQL 8.4.11 方言，非 SQLite 外推）**：复用 16D 隔离库 `rosbag-t16d-mysql`（`@@version=8.4.11`、32 表、head=`20261013_01_scene_intake`）。**接续修复**：该隔离库容器内 DBUSER 口令漂移（host 直连 caching_sha2 认证 1045 Access denied），经 root `ALTER USER` 重置回凭据文件值后同网容器探针可连（mysql CLI 内连 rc=0 实证）；隔离库为 TESTER 自建资源，reset 属维护自有环境、非生产写。探针以同 docker 网容器跑（`rosbag-catalog/backend:local` 镜像内 python，worktree 挂 wt 同路径、`import app` 解析到 `8958291` 代码，`BAG_CLEANUP_MYSQL_TEST_URL` 走网内 hostname），与 16D 既有 21/21 联合探针同配方。
- **夹具（dispatch 口径 F1N1/F1N2/F1SB + 回归守卫 CTRL，UID 前缀 T16DF1）**：
  - `F1N1`：`dataset_type=nvidia_physicalai, ORIGINAL, 有 scene_slice 用途, 非子包`（F1 前会误命中 scene_original 的可达组合，本单核心）；
  - `F1N2`：`dataset_type=nvidia_physicalai, ORIGINAL, 无 scene 用途, 非子包`；
  - `F1SB`：`dataset_type=self_built, ORIGINAL, 双用途(scene_slice+self_built), 非子包`（双用途行为回归基线）；
  - `CTRL`：非 nvidia scene 根（`dataset_type=scene`+scene_slice 用途）/ nvidia 切片（`SCENE_SLICE` 角色）——F1 未误伤非 nvidia 与子包优先回归守卫。
- **两查询入口共享谓词核实证**：入口一 `search_bags`（Web `bag_search_service.py:356`）、入口二 `search_scene_bags`（API `/api/v1/bags` `scene_result_query.py:184`）均 `where(data_kind_pred(kind))`——两入口同一 CASE，探针两入口各断言一次（非采信单入口外推）。
- **F1 单源一致性 34/34 PASS，rc=0**（探针 `scratch/t16d_f1_probe.py`，`scratch/t16d_f1_green_full.log`）：
  - `F1N1`/`F1N2`：筛 `scene_original` 两入口**均不返回**、筛 `self_built_original` **均不返回**、筛 `nvidia_original` **均返回**；行内标签 `data_kind_context` **仅 `nvidia_original`**（筛选命中集↔展示标签单源一致，C6 消除第二套真相实证）；
  - `F1SB` 双用途回归：`scene_original` 与 `self_built_original` 两筛选**都命中**、`nvidia_original` 不命中、标签**双标** `scene_original`+`self_built_original`（R1-3 只加 NVIDIA 排除、不改双用途）；
  - 各筛选命中集成员**逐一精确核**：`scene_original={F1SB,CTRL scene 根}`、`self_built_original={F1SB}`、`nvidia_original={F1N1,F1N2}`，且入口二集合与入口一一致；
  - CTRL 回归守卫：非 nvidia scene 根命中 scene_original、不命中 nvidia_original（F1 未误伤）；nvidia 切片命中 scene_slice、不命中 nvidia_original（子包优先）、标签仅 scene_slice；
  - 幂等：`scene_original`(入口一)/`nvidia_original`(入口二) 复查结果一致。
- **零越界核（dispatch 项3）**：`git -C wt-01-t16ca diff --stat 1489bc6..8958291` = **仅 `app/services/bag_search_service.py` +18/−10**；`scene_result_query.py`/模板/tests 未动（独立复核，非采信）。
- **F3 文档零行为核（dispatch 项2）**：`_parse_time` 改动为**纯 docstring 文本**（line 114-117 秒精度进位口径），diff 无 `def`/`return`/比较/谓词代码变化；行为面复用本回执 16D 联合段已有 `date end=23:59:59.999999`/`CAST('…59.999999' AS DATETIME)`=次日 00:00:00 探针口径，未重跑。
- **RED 交叉证（非采信 A/协调者，证明夹具非空转）**：同一探针切 `RED_MODE=1` 于 pre-fix `1489bc6` 跑 1 断言——`F1N1` 型（nvidia+scene 用途原包）在 `1489bc6` 上**被 scene_original 筛出**（`scene_original=[N1,N2,SCENE,SB]`）=缺陷在位，R1-3(`8958291`) 为其修复点；夹具非空转实证。
- **自清归零**：夹具 `T16DF1` purge 前 5 → 后 0（`left bags=0/deriv=0`），只读探针 + 自清，不改 A 树/seed/业务实现，未运行 OCR。
- **结论（仅 A 叶 R1-3 F1 增量面，对应 dispatch PASS 条件）**：F1 单源一致性 6 类断言（scene_original/self_built_original 两筛选×F1N1/F1N2 不返回、nvidia_original 返回、标签单源一致）全过 + F1SB 双用途回归保持 + 零越界核通过 + F3 零行为核 + 自清核 → **PASS**。本单 PASS 为 A 叶接受门禁之 TESTER 独立行为面（另一 OCR 面已由协调者 r13 `f7899cfc` 0 findings/零 CORRECTION 满足）；A 叶接受判定归协调者。
- **对 16D 合入 HOLD 的推进**：条件④（A 增量面 F1 组合夹具）本单交付 PASS；剩余⑤=协调者重建三叶固定集成候选（B `e399daf`+C `ce5921d`+新 A head `8958291`）后 TESTER 重新最终联合验收 → 解除 HOLD。`29bd1f4`（旧集成，A 仍 `1489bc6` 含 F1 未修）不可直接合入，本段不对其下联合结论。

## 最终联合验收固定 SHA `44b6c07`（2026-10-14 19:4x +08:00，TESTER attempt-1 续最终联合单）

派单 `inbox/TESTER/TASK-16D/final-integration-44b6c07-dispatch.md`（协调者 19:41，三叶全接受：B 18:10 / C 14:24 / A 19:40；旧集成 `29bd1f4` 含 F1 未修不可合入，本单测新候选 `44b6c07`）。**被测树**：`/home/wang/.local/state/rosbag-scene/wt-coord-intcheck-16c` @ `44b6c07`（detached 干净，仅 `.venv` 软链 untracked；`git rev-parse HEAD` = `44b6c0761cf92ae231b9d0f507db6bf8398d00de`；祖先链 496a3e4(A 8958291)→f24653c(B e399daf)→44b6c07(C ce5921d) 在案）。相对旧候选 `29bd1f4` 唯一 diff = `bag_search_service.py` F1 修复，F1 增量面已由本回执 19:26 段 34/34 PASS 覆盖，本单做联合确认、不重复 F1 已覆盖的增量断言。

### 1. 集成面确认（wt-coord-intcheck-16c 实测）

- `grep -c "def data_kind_case" app/services/bag_search_service.py` = **0**（A-OCR-1 死函数零残留）。
- F1 谓词在位：`dataset_type != "nvidia_physicalai"` 命中 **line 89 / line 96** 两分支（scene_original / self_built_original）。
- `view_label` line 672 = `{"originals": "原始数据", "all": "全部"}.get(state.view, state.view)`（B 叶 tab 新名同口径，「原始包/历史」旧名零残留）。
- `git diff --stat 29bd1f4..44b6c07` = **仅 `app/services/bag_search_service.py` 1 file +18/−10**，零意外文件；`git status --short` 仅 `?? .venv`。

### 2. cursor 矩阵（严格 MySQL 8.4.11 隔离库 `rosbag-t16d-mysql` 复用，两查询入口）

探针 `t16d_joint_cursor_probe.py` 以 `rosbag-catalog/backend:local` 镜像容器内跑（镜像内 `bag_search_service.py` 独立核 = F1 两谓词 2 处、死函数 0 处，即 `44b6c07` 同构代码；DB 走 `rosbag-t16d-mysql` 网内 hostname，非 SQLite 外推）。自造 11 行夹具（`T16DCURS`，7 self_built originals staggered + 1 scene parent + 3 AVAILABLE slices 带 derivation）：

- 入口一 `view=all` 连续翻页 limit=3：无漏无重；换 `data_kind`/`view` → **422**「cursor 筛选上下文不一致」；同筛选续页 → **200** 且链合并无重复 UID；旧锚点 cursor（无新键）→ **200 兼容**；`scene_code` 省略 vs `None` vs 空串归一同义；`scene_code=spray` 命中 3 子包 = 夹具 `child_ids`。
- 入口二 `lineage` 父包：翻页无漏无重（3 子包）；子包视角 `parent=T16DCURS000050` 正确；换 `bag_uid` = 新查询自身视角（设计口径，不串子包列表）；**非法 cursor（base64 非 JSON）→ 422 不 500**（两入口均）。

**矩阵 20/20 PASS，rc=0**（日志 `scratch/t16d_44b6c07_cursor.log`；`purge verify left bags=0 deriv=0` 自清归零）。

### 3. 严格 MySQL 8.4.11 方言（复用 `rosbag-t16d-mysql`，探针 `t16d_joint_mysql_probe.py`）

**21/21 PASS，rc=0**（日志 `scratch/t16d_44b6c07_mysql.log`）：C7 非法值（`not-a-date`/`2026-13-45`/`2026-02-01`）raise 源头（API 面 422）、`date end=23:59:59.999999` 全天边界、收紧窗口（到 23:59:58）排除 23:59:59 行、C5 双用途两筛选命中 UID 唯一、纯 scene/self_built 不串面、C6 分类真相（NOT_APPLICABLE 非 NVIDIA 空标签 / NVIDIA 行 `nvidia_original`）、幂等复查一致；`T16DMYSQL` 9 行夹具 `purge rc0 rows=9` 自清归零。确认 A R1-3 未改 C7/C5/C6 谓词语义（F1 增量已在本回执 19:26 段独立覆盖）。

### 4. 浏览器 Console 零异常（真实 headless Chrome CDP，非 HTTP200 替代）

Compose 栈以 `44b6c07` 重建（`wt-coord-intcheck-16c` 下 `./scripts/local_stack.sh up` rc=0，日志 `scratch/t16d_44b6c07_stack.log`；frontend 8181 http=200、API 18080 200）。`google-chrome --headless=new --remote-debugging-port=9333` 专属 user-data-dir，探针 `t16d_joint_browser.py` / `t16d_joint_browser2.py`（结果 `scratch/t16d_44b6c07_browser1.json` / `browser2.json`）：

- `/bags?view=originals`（三 tab 切片/原始数据/全部 + chip「视图：原始数据」）：`has_chip_view_label=true`、`has_old_view_label=false`（「视图：原始包」旧名零残留）、表 36 行；同 target `location.reload()` 后 `hookAlive=true` + **`errors=[]`**（`Page.addScriptToEvaluateOnNewDocument` 钩子存活，Console 零异常）。
- `/bags`（默认切片视图）：重载 `hookAlive=true` + **`errors=[]`**。
- `/pipelines/scene-e46f28c2ce1c4313a2c4ce4e8e71`（血缘兜底 + 终态停刷新）：`ol.lineage` 在位（1 子包 slope 切片血缘原文取证）、`status_badge=[SCENE_DONE, SCENE_DONE]`、`has_refresh_meta=false` + `has_retry_form=false` + `setinterval_calls=0`（终态停刷新保持）；同 target 重载 `hookAlive=true` + **`errors=[]`**。
- 页面 header 版本核：`运行版本 平台 44b6c076 · 自建 81b1e83a · NVIDIA 95f4ff65 · mock`——被测版本实证 `44b6c07`。

### 结论

- 最终联合验收清单 4 项（集成面确认 / cursor 矩阵两入口 20/20 / 严格 MySQL 8.4.11 21/21 / 浏览器 Console 零异常 + header 版本核 `44b6c07`）在固定集成 SHA `44b6c07` 上**全部 PASS**；**TESTER 最终联合验收面 PASS = 16D 最终联合验收完成**，合入 HOLD 五条件中 TESTER 面（条件⑤）解除（合入 main + 推 github + 本地 Compose 测试环境更新执行归协调者，按 18:22 用户授权，不含生产；TESTER 不批准合入、未运行 OCR）。
- 夹具 `T16DCURS` 11 行 + `T16DMYSQL` 9 行均自清归零（purge 后 `left bags=0/deriv=0` 实证）；相对旧候选唯一 diff（F1）已由 19:26 段独立增量面覆盖（34/34 PASS + RED 交叉证），本段零意外、不重复其断言。
- 浏览器 target 首启 page 复用；headless Chrome 为本轮自建 user-data-dir，验证结束不 kill 进程避免影响他角色（与 29bd1f4 段同口径）。

**未测项（如实列，同 29bd1f4 段口径，不外推）**：生产处理机/生产 MySQL/真实 NAS 根/大包跨 DB3/07C 预览/其他场景/统计/MN——均不在本轮联合验收范围；11S 批次 4acf689f 取消链收敛面独立线 TEST_REPORT_PENDING 不变。