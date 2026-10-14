# TASK-04A attempt-1 回执

- task_id: TASK-04A
- attempt: 1
- owner: 2号会话（飞书「前端功能开发」群，hermes default profile）
- status: REVIEW_PENDING
- requirement_version: PRD v0.3.2（2026-10-08）
- interface_version: scene-capability/v1（本回执定义，字段与 DESIGN §2.1 逐一对应）

## 工作树 / 基线

- worktree: /home/wang/.local/state/rosbag-scene/wt-04a（分支 scene/task-04a）
- base_commit: 054b7538eb4069ae7f066b232bb0e2bf7e910238（main，2026-10-08 17:05 核对干净）
- output_commit: 28d958c（主实现）→ f5f14ba（第 1 轮 OCR 返修）→ a23c541（第 2 轮 OCR 返修）
- upstream_accepted_commits: 无（首波）

## 允许范围 / 实际改动（7 文件，+1602 行，全新增，不改任何既有文件）

- app/scene/types.py（新增）：INTERFACE_VERSION、SceneCapability/ParameterSpec/OutputLabel/TopicRequirement、SceneSegment（纳秒整数闭区间+slice_key）、EvidenceRef、AnalysisOutput/SceneOutcome 四语义、SceneRunRequest、SceneManifest（schema_version/expected_slice_keys/digest/限额）、限额常量（单批 100 区间、JSON 64KiB）
- app/scene/registry.py（新增）：CapabilityRegistry（能力读取协议：resolve/get/list_descriptions）、config/scene_capabilities.yaml 受版本控制加载、纯参数解析（未知字段/类型/范围拒绝、默认补齐）、config_hash 冻结身份
- app/scene/adapter.py（新增）：SceneAdapter 协议（preprocess/check_applicability/analyze）、register_adapter 安装表、dispatch 统一分派（按 adapter_key 选择，无场景名称分支）、RunContextValidator/SceneRepository 协议、ContractRunContextValidator（契约层验证）、build_manifest、TestCapabilityAdapter（确定性 fixture 适配器）
- config/scene_capabilities.yaml（新增）：slope-v1 完整描述（参数 segment_len=15/overlap=3/min_effective=5 及范围、前相机 4 topic 候选、slope 可发布/flat 不可发布、model_profile/rules_revision），enabled=false + disabled_reason（真实适配器待 04B）；test-capability 启用
- app/api/scene_capabilities.py（新增）：GET /api/v1/scene-capabilities（含 disabled_reason、JSON 有界检查）
- tests/test_scene_capability_contract.py（新增）：20 项契约测试
- app/scene/__init__.py（新增）：包导出（总导出由协调者合入时更新，未动 app/schemas/__init__.py）

未碰：app/models.py、alembic/、app/api/__init__.py（路由总入口）、app/schemas/__init__.py、ros2_slice 原项目。

## 验收覆盖（TASK-04A 卡）

- AC-10（注册/分派）：测试适配器经 register_adapter + adapter_key 分派，dispatch 内无任何 scene_code 分支（契约测试 test_success_* 用 slope 能力描述跑通）；未安装适配器、伪造能力描述、禁用能力、未知场景/版本均明确拒绝（各有测试）
- AC-03 四语义：SUCCESS / NO_MATCH（仅非发布标签）/ NOT_APPLICABLE（缺 topic 原因）/ FAILED（解码失败、无有效输入、非法区间），抽帧失败≠[] 无命中（test_decode_failure_is_failed_not_no_match）
- 与 03A 一致性：能力描述字段严格对齐 DESIGN §2.1 表（3号 03A 回执亦声明同一来源）；config_hash 覆盖 scene_code+version+最终参数，可与其 EffectiveConfig 核对
- 限额：manifest 单批 >100 区间拒绝（test_segment_batch_limit_rejected）、JSON 64KiB 检查（test_json_bound_enforced）、API 目录 JSON 有界
- 时间单位：SceneSegment 纳秒整数闭区间，API 序列化为十进制字符串（to_dict 断言）

## 命令 / 退出码

- `pytest tests/test_scene_capability_contract.py -q` → 25 passed（exit 0，三轮返修后）
- `ruff format --check app scripts tests` → 166 files already formatted（exit 0）
- `ruff check app scripts tests` → All checks passed（exit 0）
- `python3 -m compileall -q app scripts` → exit 0
- `git diff --check` → exit 0
- 全量 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` → 577 passed, 10 skipped, 3 failed；3 个失败全部在 tests/test_devflow.py（worktree 无主仓库 .git 目录导致沙箱测试 ValueError），同一文件在 base 主工作区 24 passed，与本次改动无关（本次未改 devflow 任何代码）
- OCR：commit 28d958c 审查完成，session=ad3d9cfd-e311-4a68-a42e-f2d79c807020，exit 0，8 条意见（medium×5、low×3，无 critical/high）。对照当前 HEAD 核实：
  1. api/scene_capabilities.py:19 [medium] 路由未挂进 app/api/__init__.py——**属实但属 DESIGN §11.3 设计**：路由总入口由协调者合入时串行更新，回执已列出待办，非遗漏；
  2. api/scene_capabilities.py:25 [low] 只捕获 CapabilityError，yaml/IO 异常裸 500——属实，待修；
  3. scene/adapter.py:41 [low] register_adapter 拒绝覆盖时报的是新类名——属实（笔误），待修；
  4. scene/adapter.py:129 [low] dispatch 把 CapabilityError 类型名当 error_code，适配器无法传结构化错误码——属实（契约缺口），04B 接入前建议补 SceneAdapterError(code, detail)；
  5. scene/registry.py:117 [medium] defaults 块只查键集、值被 schema default 覆盖，配置者写 30 实际 15 且不可见——属实，待修（值与 schema 不一致时拒绝）；
  6. scene/registry.py:209 [medium] 未指定版本用字符串 max() 选"当前启用版本"，slope-v9>slope-v10 字典序错误——属实，待修（显式版本序）；
  7. scene/registry.py:227 [medium] 跨字段约束缺失：segment_len=5, overlap=60 可通过并冻结进 config_hash——属实，待修（能力级约束钩子）；
  8. scene/types.py:311 [low] _utc_now_iso 实为主机本地时区——属实，待修。
  按仓库规则先向协调者核实；2/3/5/6/7/8 属本任务交付代码缺陷，已在 attempt-1 第 1 轮返修完成（commit f5f14ba，+4 项针对性测试，24 项契约测试全过）：
  - #2 API 异常分类：CapabilityError→422 配置错误、yaml/IO→结构化 500（不裸抛栈）；
  - #3 register_adapter 报既有 owner 类名；
  - #4 新增 SceneAdapterError(code, detail)，dispatch 按 code 原样落 manifest（测试：取消信号 → error_code=ADAPTER_CANCELLED）；
  - #5 defaults 块值与 schema default 不一致时加载即拒绝（测试覆盖）；
  - #6 版本排序改数字后缀序（v9<v10），等价键并列时拒绝猜测、要求显式版本（测试覆盖）；
  - #7 新增能力级声明式跨字段约束（SceneCapability.constraints + ParameterConstraint，yaml 可表达），slope 配置加 overlap<segment_len，冻结进 config_hash 前执行（测试覆盖）；
  - #8 manifest 时间兜底改 UTC，digest 不随部署主机时区漂移。
  f5f14ba 的 OCR 审查已完成，session=b4947304-b6be-40b7-9bc7-bfd88e6aa25c，6 文件 4 条（medium×1、low×3，无 critical/high）：
  - [medium] registry.py:195 约束参数名未与 parameter_schema 交叉校验，写错字段名会静默禁用约束——属实，已修（加载时校验 field/ref_field 均存在，测试 test_constraint_unknown_field_rejected_at_load）；
  - [low] registry.py:269 注释并列示例不准确——属实，已改文案；
  - [low] types.py:111 constraints 用 tuple[Any,...] 失去静态类型——属实，已改 tuple[ParameterConstraint,...] + TYPE_CHECKING 守卫；
  - [low] types.py:325 函数内局部 import timezone 与顶部重复——属实，已合并为顶层 from datetime import datetime, timezone。
  第 2 轮返修 commit=a23c541，其 OCR 审查完成 session=8c7ae34f-19c9-4bf9-a1d9-93c20211b0e2，2 文件 0 findings。
  三轮 commit（28d958c→f5f14ba→a23c541）OCR 全部闭环，无未处理的 critical/high。返修后 25 项契约测试全过。

## 未执行项

- 未接 alembic/数据库仓储（TASK-02 独占迁移链；本任务 Registry/Repository 为内存+协议，正式落库由 06A）
- 未注册进 app/api/__init__.py 路由总入口与 app/schemas/__init__.py 总导出（DESIGN §11.3 协调者合入时串行更新）
- 未做真实坡道推理/writer（TASK-04B；SLOPE_ADAPTER_KEY="ros2-slope-v1" 已预留，04A 不装占位实现）
- 未推送 github：commit 在个人分支 scene/task-04a，按专项规则待协调者验收合入集成基线后再随主分支同步
- 未做生产/处理机任何操作

## 需要协调的契约 / 共享文件

- 合入时请协调者在 app/api/__init__.py 追加 scene_capabilities.router（import 与 include 两处）
- interface_version=scene-capability/v1 请协调者记入 DESIGN 共享契约清单；04B/05/06A/06B 消费 SceneRunRequest/SceneManifest/SceneRepository/RunContextValidator 四个契约类型
- 建议 04B 领取时先读本回执与 app/scene/ 包，真实适配器用 register_adapter(SLOPE_ADAPTER_KEY, <SlopeAdapter>) 安装，并把 config/scene_capabilities.yaml 的 slope enabled 切 true（随真实实现同批提交）

## suggested_next_candidates

- TASK-04B（本任务完成后依赖满足，立即可接）
---

## 协调者代记：OCR 审查与 attempt-2 返修指令（2026-10-08，非执行者自写）

- OCR（本机 Qwen，session ad3d9cfd）审 commit 28d958c：6 文件 8 条意见。
- 核实结论（对照当前集成 HEAD 逐条）：
  1. [medium] scene_capabilities.router 未挂载 → **已修复**（协调者接线提交 dfd4f0e，TestClient 实测 200）。
  2. [medium] 版本字典序取 latest（v9 vs v10）→ 当前仍成立，**待 attempt-2 修复**。
  3. [medium] YAML defaults 与 schema default 不一致被静默丢弃 → 当前仍成立，**待修复**。
  4. [medium] 缺 overlap<segment_len 跨字段约束，非法组合被冻结进 config_hash → 当前仍成立，**待修复**。
  5. [low] register_adapter 报错把新类当旧 owner → 当前仍成立，**待修复**。
  6. [low] CapabilityError 无结构化 code，dispatch 用类名当 error_code → 当前仍成立，**待修复**。
  7. [low] _utc_now_iso 用宿主时区 → 当前仍成立，**待修复**。
  8. [low] 路由只捕获 CapabilityError，YAML/OSError 裸抛 500 → 当前仍成立，**待修复**。
- 协调者曾越界直接合入一版修复（3a87027）后又撤出 main，main 已恢复 dfd4f0e。修复代码保留供参考：
  - 本地分支 `fix/scene-04a-ocr-rework`（tip=3a87027）
  - 补丁 /home/wang/work/doc/prd/rosbag-catalog-integration/ocr-fixes/task-04a-ocr-fix-3a87027.patch
  - 参考补丁含 5 项回归测试（版本排序/defaults 漂移/跨字段约束/未知约束名/坏 YAML）。
- **attempt-2 指令**：请在自己的工作树（/home/wang/.local/state/rosbag-scene/wt-04a）按 ocr-code-review skill 的返修流程处理上述 7 条（可用参考补丁做对照，但以你核实后的实现为准；跨字段约束机制若与参考实现不同，在回执说明）。注意：参考补丁给 app/scene/types.py 的 CapabilityError 加了 code 字段、给 SceneCapability 加了 parameter_constraints 字段——这两个是接口面变化，若采纳请在回执里明确 interface_version 是否需要升级为 scene-capability/v2，并告知下游（04B/05/06A）。完成后写 receipts/TASK-04A/attempt-2.md，报 REVIEW_PENDING。
- 约束：不改协调者接线文件（app/api/__init__.py 总入口、app/schemas/__init__.py）；不碰 02 号在途的 models.py/迁移/清理服务文件。
