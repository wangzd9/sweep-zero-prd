# TASK-03A attempt-1 回执（3号执行者）

- task_id: TASK-03A
- attempt: 1
- owner: 3号执行者（飞书"数据链路监控告警"会话，hermes default profile）
- status: REVIEW_PENDING
- requirement_version: v0.3.2（2026-10-08）
- interface_version: DESIGN §2.1/§3.1/§7.1/§8.1（v0.3.2）
- worktree: /home/wang/.local/state/rosbag-devflow/worktrees/scene-integration-03A
- branch: feature/scene-config-dto
- base_commit: 054b7538eb4069ae7f066b232bb0e2bf7e910238（main，领取时工作树干净，已重核对）
- upstream_accepted_commits: 无（执行集成基线尚未建立；02/04A 未交付）
- output_commit: 67f9f4c（分支 feature/scene-config-dto，三轮 ocr 返修后收敛；7714e89/d8bf93a/1038220 均未推送，已被替代）

## 允许范围与实际改动

允许（任务卡/DESIGN §11.3）：配置 DTO、纯解析、能力读取协议及限额、对应测试；不碰 ORM/迁移/Scanner/全局入口/schemas 总导出。

changed_files（4 个新增，零修改既有文件）：
1. `app/domain/scene_config.py` — 纯解析核心：IngestPurpose、CapabilityDescription/ParameterSpec、CapabilityRead 协议 + StaticCapabilityRegistry 替身、IngestProfile/SceneSelection/SubmissionSelection/ResolvedScene/EffectiveConfig、resolve_effective_config（DESIGN §3.1 九行规则表）、SceneConfigError（code 映射 §7.1 错误类别）、限额常量与路径/幂等键校验。
2. `app/schemas/scene_config.py` — Pydantic DTO：CapabilityDescriptionSchema（类型枚举、边界/重名校验）、IngestProfileSchema、SceneSelectionSchema、IngestSubmissionRequest（extra=forbid、路径/长度限额）、EffectiveConfigView（hash 格式校验、domain 双向转换）、check_request_body_size/check_json_field_size（§8.1 限额，供 03B 路由接线）。
3. `tests/test_scene_config_resolution.py` — 18 项纯解析验收测试。
4. `tests/test_scene_config_schemas.py` — 17 项 DTO 契约测试（含 DESIGN §7.1 配置提交示例走通）。

## 实现行为（AC 覆盖）

- 集合替换默认、不做隐式并集：显式 purposes/scenes 整体替换（test_explicit_purposes_replace_default_set / test_explicit_scenes_replace_default_set）。
- 无效/空场景：未注册 UNKNOWN_SCENE、已注册禁用 SCENE_DISABLED（带原因）、scene_slice 空集合 SCENE_EMPTY、self_built+scenes PURPOSE_SCENE_MISMATCH。
- 非法参数：未知键/类型/越界/null/未知用途 → INVALID_PARAMETERS/INVALID_PURPOSES。
- 版本冲突拒绝：重复 scene_code 不同 capability_version → SCENE_VERSION_CONFLICT；未指定版本接受时固定当前启用版本（latest 指针），profile/能力后续更新不影响冻结快照（test_version_pointer_drift_does_not_affect_frozen_config）。
- CONFIG_REQUIRED：入口无有效默认且无每包配置（含默认场景无可用能力）→ 返回 None 登记待处理，不抛硬错误、不猜测全场景。
- 幂等确定性：同请求两次解析 hash/内容完全一致；参数顺序不影响 hash（JSON 规范化 sha256）。
- 限额：请求体 1 MiB、JSON 字段 64 KiB、幂等键 ≤255、relative_path ≤1024 且拒绝绝对路径/越界/空（posix 归一化后判逃逸，允许 a/b/../c 内部折叠）、场景数 ≤16、参数数 ≤64；DTO 层 Pydantic 与纯解析层双保险。
- 能力读取使用协议替身 StaticCapabilityRegistry，未硬编码任何场景可用状态。

## ocr 审查（本机 Qwen vLLM，流程见 .agents/skills/ocr-code-review）

第一轮（初版 7714e89，session 7765a28c，19m02s，exit 0）：6 findings，逐条核实对照 HEAD：
1. [bug·medium] CapabilityParameterSchema 只查 minimum<=maximum，default/allowed_values 未对照 type，str 参数带 min/max 不拒绝 → **属实已修**（_check_bounds 增加 _fits 校验 + str 禁 min/max）。
2. [other·low] 重复 scene_code 一律报 SCENE_VERSION_CONFLICT"版本不一致"，纯重复场景语义错误 → **属实已修**（拆分 DUPLICATE_SCENE / SCENE_VERSION_CONFLICT 两码，仅显式不同版本才报冲突）。
3. [bug·medium] ResolvedSceneView.parameters 禁 None，但解析器把 optional default=None 参数并入冻结配置，from_domain 会 ValidationError → **属实已修**（值类型放宽含 None，加 round-trip 用例）。
4. [maint·low] to_domain 未回传 schema_version，非默认值丢失 → **属实已修**（加 schema_version=self.schema_version + 用例）。
5. [bug·medium] NaN/±inf 绕过范围校验进入 hash（json 输出非标准 NaN）→ **属实已修**（math.isfinite 拒绝 + NaN/inf 用例）。
6. [bug·low] IngestPurpose(不可哈希 item) 抛 TypeError 逃逸 → **属实已修**（except 扩为 (ValueError, TypeError)）。

第二轮（d8bf93a，session edf4280e，22m17s，exit 0）：6 findings（1 medium + 5 low），逐条核实全部属实并已修（amend 进 1038220，各补回归用例）：
1. [bug·medium] raw-dict 防御路径 `item.get("parameters") or {}` 在 isinstance 前把假值（[]/0/""）静默归一成"无参数" → 改为仅 None 默认 {}，其余非 dict 拒绝（test_falsy_non_dict_parameters_rejected）。
2. [other·low] check_json_field_size 对不可序列化输入（键类型混杂触发 sort_keys TypeError）抛裸 TypeError 而非受控 ValueError → try 包裹统一 ValueError（测试覆盖）。
3. [maint·low] ResolvedSceneView.scene_code/capability_version 缺长度约束，持久快照回读时空值可过 → 补 min_length=1/max_length=64（测试覆盖）。
4. [maint·low] _validate_purposes 的 None 分支与 explicit 参数不可达（唯一调用方已保证非 None）→ 删除死分支与参数。
5. [bug·low] capability_version 未 strip，带空格版本查表失败报误导性 UNKNOWN_SCENE → 与 scene_code 一致 strip（测试覆盖）。
6. [other·low] 反斜杠仅拒绝开头，路径中段反斜杠造成 Windows 风格路径键冲突 → 整体拒绝反斜杠（测试覆盖）。

第三轮（1038220，session 539839fe，17m27s，exit 0）：1 finding，对照 HEAD 核实属实并已修（amend 进 67f9f4c）：
- [bug·medium] 非显式（入口默认）路径只预检查能力可用性，入口 default_scene_parameters 在能力 spec 变更后残留失效值、或 default_scenes 代码重复时，resolve 循环抛 INVALID_PARAMETERS/DUPLICATE_SCENE 硬错误，把入口配置问题变成对用户的 4xx 拒绝，违反"缺有效默认走 CONFIG_REQUIRED 登记待处理"契约 → 默认路径增加预检查：重复代码、默认参数过 spec 校验失败均降级返回 None（CONFIG_REQUIRED）；用户显式选择的失效参数仍硬拒绝（test_default_stale_parameters_degrade_to_config_required / test_default_duplicate_scene_codes_degrade_to_config_required / test_explicit_stale_parameters_still_hard_rejected）。

第四轮（67f9f4c 复核）：分两批完成，均 exit 0。
- 批 1（全量，session 27ba3526，12m24s）：schemas/scene_config.py 0 findings；domain/scene_config.py 因该文件单请求超时未出结论（1 of 2 failed，非 findings 为 0）。
- 批 2（`--exclude '**/app/schemas/**'` 补审 domain，session 16976aa3，6m23s）：domain/scene_config.py **0 findings**。
- 合计：67f9f4c 两个文件经独立审查均 0 findings，无未闭合意见。前三轮共 13 条意见（3 medium + 10 low，无 critical/high）已全部对照 HEAD 核实并修复，各带回归用例。

## 验证命令与退出码（worktree 内，.venv 软链主仓库后执行，提交前已移除软链）

| 命令 | 结果 |
|---|---|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/test_scene_config_resolution.py tests/test_scene_config_schemas.py -q` | 46 passed（三轮返修后），exit 0 |
| 全量 `pytest -q` | 603 passed, 10 skipped, 3 failed（三轮返修后）——3 个失败全部为 tests/test_devflow.py 沙箱用例，根因是 worktree 的 `.git` 是文件非目录（`主仓库缺少 .git`），主工作区同文件 24 passed 佐证为环境问题，与本次 4 个新增文件无关 |
| `.venv/bin/ruff format --check app scripts tests` + `.venv/bin/ruff check app scripts tests` | 164 files already formatted / All checks passed |
| `python3 -m compileall -q app scripts` | exit 0 |
| `git diff --check` | 无空白错误 |

未执行：`local_quality_gate.sh`/`local_stack.sh test`（本任务零路由/服务/模板改动，且按 §5 共享资源由协调者安排）；`alembic heads`（无迁移）。

## 交接给下游的接口要点（供 03B/05/06A 对齐，待协调者接受后固定）

- `resolve_effective_config(profile, capabilities, selection) -> EffectiveConfig | None`；None 即 CONFIG_REQUIRED。
- `CapabilityRead` 协议 4 方法：capability_codes / enabled_capability / capability / latest_capability；04A 注册产物与 03B 真实仓储实现同一协议即可互换。
- EffectiveConfig.config_hash 为 sha256(schema_version+profile_id+profile_version+排序后 purposes+scenes 含固定版本与完整参数)，幂等回放可据此判定同请求。
- DTO `IngestSubmissionRequest.to_selection()` → 领域选择；`EffectiveConfigView.from_domain/to_domain` 双向；`check_request_body_size/check_json_field_size` 待 03B 在路由接线。
- 错误码集合（SceneConfigError.code）：UNKNOWN_SCENE、SCENE_DISABLED、SCENE_EMPTY、SCENE_VERSION_CONFLICT、PURPOSE_SCENE_MISMATCH、INVALID_PURPOSES、INVALID_SCENES、INVALID_PARAMETERS、INVALID_RELATIVE_PATH、INVALID_IDEMPOTENCY_KEY；03B 映射 422/409 时注意 UNKNOWN_SCENE/SCENE_DISABLED/INVALID_PARAMETERS 为 422，幂等/路径抢占为 409（按 DESIGN §7.1）。
- **建议的契约修订（最小）**：DESIGN §2.1 能力描述表未含 `latest_capability`（查询该代码最近登记版本以区分"未注册"与"已禁用"）；CapabilityRead 协议方法集建议在 DESIGN §2/§11.2 补充一行，避免 04A 注册时字段漂移。其余无修订。
- schemas 总导出（app/schemas/__init__.py）未动，请协调者合入时追加 scene_config 导出。

## 与 TASK-04A（2号）契约一致性核对（已读其回执与 wt-04a 代码）

能力描述的类型 owner 按 DESIGN §2.1/§11.2 归 04A；03A 只定义消费侧读取协议。两者字段级存在漂移，**需协调者在合入前定夺唯一字段名/方法集**（我已按 DESIGN §11.3 未动 04A 类型，04A 亦未动我的文件，无文件冲突）：

| 03A 消费侧（app/domain/scene_config.py） | 04A 供给侧（app/scene/types.py） | 差异与处理 |
|---|---|---|
| `CapabilityRead.enabled_capability(code)` | `CapabilityRegistry.resolve(code, None)`（无启用版抛 CapabilityError） | 语义等价；03B 接线时包一层即可（resolve 失败→None/异常分类） |
| `CapabilityRead.capability(code, ver)` | `CapabilityRegistry.get(code, ver)` | 同名异叫，适配器直转 |
| `CapabilityRead.latest_capability(code)` | 无直接对应（`known_versions` 返回版本串列表） | 我新增方法用于区分"未注册 vs 已注册但禁用"；04A 可补或 03B 用 resolve 失败分类替代 |
| `CapabilityDescription.parameter_specs` | `parameter_schema` | **字段名不同**，同一概念；建议以 04A 的 `parameter_schema` 为准，03A 更名 |
| `CapabilityParameterSpec.required/allowed_values` | `ParameterSpec` 无 required/allowed_values，另有 `defaults` 块与 `constraints` | 04A 的 defaults 块与 ParameterSpec.default 双轨（其 ocr #5 已修"值不一致拒绝"）；我的 allowed_values 是 04A 没有的能力。建议协调者在 DESIGN §2.1 冻结一份权威字段表 |
| `required_inputs: tuple[dict[str,str]]` | `tuple[TopicRequirement(topic,message_type,required)]` | 结构不同；03A 消费侧可放宽为 Any 序列，04A 的 TopicRequirement 更精确 |
| `unavailable_reason` | `disabled_reason: str \| None` | 字段名不同，同义 |
| `output_labels: tuple[str]` / `publish_labels` | `output_labels: tuple[OutputLabel(label,scene_tag,publish_target)]` | 04A 结构更丰富；03A 的 publish_labels 可由 OutputLabel.publish_target 推导 |
| `CapabilityRead.capability_codes()` | `CapabilityRegistry.all()` | 03B 适配器覆盖 |

- 限额一致性：双方均为 JSON 64 KiB、单批 100 区间（04A manifest 侧）、幂等键 ≤255——**一致，无冲突**。
- hash 一致性：我的 `EffectiveConfig.config_hash`（profile+purposes+冻结 scenes 含版本与完整参数）与 04A 的 `config_hash`（scene_code+version+最终参数）粒度不同、可互相嵌套：03B 持久快照存我这份整包 hash，04A 那份是单能力维度。建议在 DESIGN §3.1 注明两级 hash 关系，避免 05/06B 对账时混淆。
- 03A 不消费 04A 的 SceneSegment/EvidenceRef/manifest（归 04B/06A），无该层对齐负担。

## 建议可解锁

- TASK-03B、TASK-05、TASK-06A 的 03A 依赖在本 commit 接受后满足（接口版本 scene-config-v1）。
- 建议下一个候选按 §6.3 优先序：06B → 05 → 06A → 03B → 04B。
---

## 协调者代记：OCR 审查与 attempt-2 返修指令（2026-10-08，非执行者自写）

- OCR（本机 Qwen，session 4647916e，含 1 次 LLM 超时重试）审 commit 7714e89：2 文件 6 条意见，逐条核实如下：
  1. [medium] 同场景重复代码一律报 SCENE_VERSION_CONFLICT，相同重复误报 → 当前仍成立，**待修复**（相同版本/参数应去重取先者，仅版本不一致拒绝）。
  2. [medium] IngestPurpose(item) 在 Py3.10/3.11 下不可哈希元素逃逸 TypeError（500 而非 4xx）→ 当前仍成立，**待修复**（except 加 TypeError）。
  3. [low] to_domain 丢 schema_version，round-trip 漂移回当前常量 → 当前仍成立，**待修复**。
  4. [low] CapabilityParameterSchema.default 无 type/bounds/allowed_values 一致性校验 → 当前仍成立，**待修复**。
  5. [low] NaN/Inf 与上下限比较恒 False 静默通过 → 当前仍成立，**待修复**（math.isfinite 显式拒绝）。
  6. [low] parameters 为 falsy 非 dict（0/False/[]）被 `or {}` 静默强转 → 当前仍成立，**待修复**（仅 None 视为未提供）。
- 协调者曾越界直接合入一版修复后撤出 main，main 已恢复 dfd4f0e。参考补丁（含 6 项回归测试）：
  /home/wang/work/doc/prd/rosbag-catalog-integration/ocr-fixes/task-03a-ocr-fix.patch
- **attempt-2 指令**：在你的工作树（/home/wang/.local/state/rosbag-devflow/worktrees/scene-integration-03A）处理上述 6 条，可用参考补丁做对照（去重实现注意：参考版用 dict[scene_code]→version 跟踪已见版本，两者都未指定版本时视为一致）。接口面（Error code 集合、EffectiveConfig 字段）若变化请在回执说明；schema_version 修复不改契约。完成后写 receipts/TASK-03A/attempt-2.md，报 REVIEW_PENDING。
- 约束：不碰 app/schemas/__init__.py 总导出与 02 号在途文件。
