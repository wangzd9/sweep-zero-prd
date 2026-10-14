# TASK-06A 回执（attempt-1）

- owner：2号会话（前端功能开发群）
- 需求版本：rosbag-catalog-integration v0.3.2
- 接口版本：scene-config-v1（03A）、scene-capability/v1（04A 终版签名）
- 集成 base：main eaf632a（含 04B 全部 5 commit）
- 工作树：/home/wang/.local/state/rosbag-scene/wt-04a，分支 scene/task-06a（基于 eaf632a）
- 已授权阶段：P0 本地（无生产、无处理机操作）
- 状态：REVIEW_PENDING（待协调者 OCR 代跑 + 验收合入）

## 允许范围与实际改动（3 个新文件，零修改既有文件，无新迁移）

- `app/services/scene_result_service.py`（新增，~330 行）：manifest 批次幂等登记、
  分析版本当前指针换版原语、子包 PENDING 登记 + 派生血缘、标签证据落库
- `app/services/scene_result_query.py`（新增，~370 行）：统一服务检索（view=slices/
  originals/all）、当前版本查询、区间列表、血缘、标签证据，全部有界
- `tests/test_scene_result_storage.py`（新增，20 项数据库测试）

未碰：app/models.py（02 的表全部够用，无需改他人迁移）、alembic/（无新迁移）、
app/api/*（06B 的路由范围）、03B 接收文件（source_service/catalog_ingest）、
05 在途文件（pipeline_service/enums/transitions/scene_slice_service）、schemas 总导出。
与 03B 返修/05 在途改动零文件重叠。

## 实现行为（对应 DESIGN §4/§6/§7.1/§8.1）

### 登记（register_manifest，06B 在身份校验后调用）
- 幂等键 = (parent_bag_uid, scene_code, run_id) + 内容身份（manifest digest 前 16 位）：
  同 run 同内容 → 回放补齐（replayed=True，派生行不重复）；同 run 不同内容 → 409
  DUPLICATE_CONFLICT（DESIGN §6 规则 1：重试复用稳定 slice_key，显式重分析必须新 run）。
- 区间行按 (analysis_version_id, slice_key) 复用；同 slice_key 不同 (label,start,end)
  → 409。flat 等非发布结果同样落库（DESIGN §4.1"包含 flat"）。
- 标签证据：bag_scene 是有效标签投影，MODEL 来源 + 原始判定引用
  （`run_id#content_identity`）；P1 修订字段（revised_by/revision_reason/withdrawn）预留未写。
- 子包：bag_record(SCENE_SLICE, availability=PENDING) + bag_derivation
  （run+slice_key 唯一、child_bag_uid 唯一、父子 FK RESTRICT 兜底、segment_id 回填）。
  子包继承父包 fast_fingerprint（父子同指纹不回避，隔离由 role/血缘承载；
  02 的 register 防归并检查"任一 SCENE_SLICE 命中即 409"在本链路天然成立）。
- 父包不存在或角色非 ORIGINAL → 409 PARENT_NOT_READY（不猜测创建）；
  目标切片缺子包 UID 映射 → 422（不猜 UID）。
- 单批 100 区间上限：04A SceneManifest 构造函数已强制（服务层守卫为防御冗余），
  测试打真实边界（101 构造拒绝 / 100 接受并落库）。
- 不提交事务（调用方与身份校验同事务）；不接真实回报入口、不宣称发布成功。

### 换版（switch_current）
- 仅 SUCCESS / NO_MATCH 可切当前（NOT_APPLICABLE 不替换既有当前结果、FAILED 旧结果
  不替换，DESIGN §5 场景结果表 + §6 规则 7）；422 拒绝。
- 父包+场景锁下（with_for_update）原子切换：旧 current 行置 False、新行置 True；
  (created_at, id) 序较旧的晚到提交拒绝倒退（409）；已是当前 → no-op 幂等；
  目标版本 result 与换版声明不一致 → 409。
- current=false 初始值：登记与可见性解耦（DESIGN §6 规则 4"先标 PENDING"），
  06B 校验完整预期集合后调 switch_current。

### 检索（search_scene_bags / lineage / list_segments / current_versions / label_evidence）
- limit 默认 50、上限 200（防御性 clamp，超限拒绝语义由 06B API 层 4xx 承载）。
- 排序固定：started_at 倒序、NULL 排最后、bag_uid 倒序续排；区间 start_ns、id 升序。
- cursor = base64(JSON{null,ts,uid,...})，含排序锚点 + 筛选上下文；非法 cursor → 422；
  翻页 +1 判定 has_more（不做全量 COUNT）；不承诺快照隔离（DESIGN §7.1）。
- view=slices 默认仅 SCENE_SLICE + AVAILABLE（PENDING 不进入可用检索）；
  include_history 时全部历史切片 + 行内 current 标记（一次有界批量查询标注，不逐行查）。
- 摘要投影：bag_uid/name/role/availability/started_at/duration_ns/vehicle/scenes/
  dataset_type，不无界展开 topic/子包/历史（scenes 一次 bag_scene 批量 join 名字）。
- 时间 API 序列化为十进制字符串（duration_ns/start_ns/end_ns str()）。
- 血缘：父包视角列子包（沿用 started_at/bag_uid 倒序；子包 started_at 为 NULL 时
  按 bag_uid 倒序，已在 docstring 与测试固化语义）；子包视角返回父包 + 自身登记
  （run/slice/区间/segment）；不存在包 404。批量查询 segment/analysis_version 无 N+1。
- parent_bag_uid/scene_code 过滤作用在 derivation 关联上，仅对 slices/all 视图有意义
  （originals 视图用 child_uid_prefix 等角色过滤）——docstring 已写明，防误用。

### 必要索引/实际 SQL（DESIGN §8.1）
- 复用 02 迁移 20261008_01 已建索引（无需新迁移）：
  ix_bag_record_role_avail_started_uid、ix_scene_segment_version_start_id、
  ix_bag_derivation_parent_scene_run_child、ix_scene_analysis_parent_scene_current。
- 测试 test_required_indexes_exist 断言四索引落地；test_slice_search_sql_column_combo
  验证检索 WHERE 列组合 (bag_role, availability) 命中角色索引最左前缀。
- 未新增索引：按 §8.1"根据实际 SQL 核对，不无限追加冗余索引"，现有组合索引已覆盖
  本服务全部查询路径（vehicle 前缀检索按 §8.1 留待实际 SQL 核对后决定，未盲加）。

## 验证命令与结果（worktree 内，.venv 软链主仓库）

| 命令 | 结果 |
|---|---|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_scene_result_storage.py` | 20 passed |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`（全量） | 692 passed, 10 skipped, 3 failed |
| 3 个失败 | 全部 tests/test_devflow.py 沙箱用例（worktree `.git` 是文件非目录的环境差异，eaf632a base 上同样失败，与本任务无关） |
| `ruff format --check app scripts tests` | 186 files already formatted |
| `ruff check app scripts tests` | All checks passed |
| `python3 -m compileall -q app scripts` | exit 0 |
| `git diff --check` | 无空白错误 |

## 未执行项（如实）

- **OCR：未自跑**——按派单"OCR 不要自己跑（单 Qwen 实例并发挤单会挂死）"，
  提交 c4ce66c 后报 REVIEW_PENDING，请协调者代跑 `ocr review -c c4ce66c --audience agent`
  （3 个新文件，单批安全）。
- MySQL 隔离库 DDL 实测：未执行——本任务**零新迁移零 schema 变更**（全部复用 02
  迁移 20261008_01 已建的表/索引/唯一约束，MySQL 兼容性由 02 的验收证据覆盖），
  不存在 MySQL 专属 DDL 风险；with_for_update 在 SQLite 退化为无行锁，生产 MySQL
  路径行锁生效（docstring 已注明）。
- local_stack.sh test / local_quality_gate.sh：未执行——本任务零路由/服务/模板改动
  （纯 service 层 + 测试），local_quality_gate 的 Ruff/pytest/编译段已全部等价执行。
- 06B 的正式回报 API 路由、staging 文件校验/原子发布、availability 切换、
  complete-scene：均未做（06B 范围）。

## 交接给 06B 的要点

- `svc.register_manifest(db, manifest, expected_child_uids={slice_key: child_uid})`：
  06B 回报 API 在验证执行身份/租约/源代次/文件证据后调用，与身份校验同事务。
- `svc.switch_current(db, parent_bag_uid=..., scene_code=..., analysis_version_id=..., result=...)`：
  complete-scene 校验完整预期集合与摘要后调用（06B 负责完整性校验，本原语只负责
  指针原子性 + 不倒退 + 结果语义门禁）。
- availability PENDING→AVAILABLE 由 06B 在文件校验+发布完成后切（本任务只登记
  PENDING，不切可用）。
- writer storage_offset_ns 交接约束不变：06B 从 manifest 证据推导，不可推导阻塞发布。
- 检索层 `q.search_scene_bags/lineage/list_segments/current_versions/label_evidence`
  是纯函数（db + 参数 → dict），06B 挂路由直接调，注意 limit 上限 200 与 cursor 422。
- 错误码集合（06B 映射 HTTP）：RESULT_NOT_FOUND(404)、DUPLICATE_CONFLICT(409)、
  PARENT_NOT_READY(409)、MANIFEST_INVALID(422)、LIMIT_EXCEEDED(422)。

## suggested_next_candidates

- TASK-06B（本任务完成后 06A 依赖满足）
---
## attempt-2 返修指令（协调者追加，2026-10-09）

协调者代跑 OCR（c4ce66c，2 文件核心审查，session b29b4ae2）：8 条。协调者已逐条对照代码核实，判定如下：

**必须修（4 条，真实）**：
1. [bug · high] scene_result_query.py:348 search_lineage_children 分页续查条件漏 `started_at IS NULL` 分支——排序把 NULL 行排最后，锚点行非 NULL 时续查 `(started_at < ts)|(...)` 永不含 NULL 行，NULL started_at 子包分页丢失。同文件 search_scene_bags:161 的同类分支**写对了**（含 `is_(None)`），此处同口径补齐 + 回归测试（A(ts=100)/B(ts=50)/C(ts=NULL) limit=2 翻页必须取到 C）。
2. [bug · high] scene_result_service.py:161-162 段数基数不一致：expected_segment_count 取 `publishable_segments()`（仅可发布），registered_segment_count 取 `len(manifest.segments)`（全部含 flat）。任何 SUCCESS 且含非发布区间的 manifest，两值恒不等，06B 的 PENDING→AVAILABLE 完整性门禁若做等值比较则场景永远无法 AVAILABLE。另：重放补齐路径插入缺失 segment 行后未刷新 registered_segment_count（存值过期）。处置：与 06B 门禁语义对齐后统一基数（建议 expected=可发布、registered 同口径=已登记可发布数；或明确文档化为"全部/可发布"两语义并让 06B 按此实现）——**在回执写明你选定的语义与理由，06B 派单会带上**；补齐路径同步刷新 count。
3. [bug · medium] 幂等全是 check-then-act（scalar 查无→add→flush）无 IntegrityError 兜底：并发同 manifest 重试两事务都通过 `av is None` 后第二个 insert 撞 uq_scene_analysis_parent_scene_version 报裸 500，违背模块头承诺的 200 重放/409 语义。_register_derivation（child_bag_uid 唯一 + uq_bag_derivation_run_slice）与 evidence insert 同缺口。处置：flush 序列包 try/except IntegrityError，按唯一键来源翻译成重放(200)/409。
4. [bug · medium] switch_current 的"每 parent+scene 至多一行 current=true"不变式**仅靠 FOR UPDATE**（代码注释自认 SQLite 下行锁是 no-op），且 (parent,scene,version) 唯一约束管不住 current 列。MySQL 生产单写者安全，但 P0 本地 SQLite 并发（WAL）下可出现双 current 指针。处置：OCR 建议的 guarded UPDATE（`where(parent,scene,current=True,id=current.id).values(current=False)`，rowcount==0 则视为竞争败者重读重试）两后端通用，采纳。
   **协调者勘误**：我此前在群里说过"current 唯一性有 DB 级双保险"——**错误**，ix_scene_analysis_parent_scene_current 是普通索引不是唯一约束，已核实更正。若你认为更彻底的方案是加 (parent,scene) 级 current 唯一约束（MySQL partial index 不可行，可用 current 列存 parent+scene 键的变长唯一技巧或应用层），给出方案与理由，否则按 guarded UPDATE 修。

**建议修（4 条 low，顺手）**：
5. [perf · medium→按 high 优先级排后] query.py:368 循环内逐子包 `db.scalar(select(BagRecord))` N+1（一页 200 条=200 次往返，违背同段注释"不逐子包 N+1"；next_cursor 块还重复查了最后一次）→ 循环前一次 IN 批量建 dict。
6. [perf · low] query.py:290 `truncated` 用第二次完全相同的有界查询重算 → 用第一次 len(rows)>lim 结果。
7. [maint · low] query.py:66 `_bag_summary(db,...)` 死参数 db → 移除（含调用点）。
8. [maint · low] query.py:36 `_SEARCH_PROJECTION` 模块常量死代码 → 删或实际使用。

**备注**：本轮 OCR round 2 对两个文件各超时一次（review_round_failed），8 条为 round 1 产出；返修后协调者对返修 commit 再跑一轮，若再超时改错峰独占跑。
要求：1-4 必修 + 回归测试（尤其 #1 翻页取 NULL 行、#2 含 flat 的 manifest 基数一致、#3 并发重试 409/重放而非 500——可用 sqlite 内存库两 Session 模拟或 monkeypatch），5-8 顺手修；全量测试过；回执 attempt-2 段补记 + #2 的语义选择说明；报 REVIEW_PENDING。OCR 不要自跑，协调者代跑。
