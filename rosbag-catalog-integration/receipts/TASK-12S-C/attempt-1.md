# 回执：TASK-12S-C attempt-1 水雾正式接线（前置开发）

- status: **REVIEW_PENDING（待接线核验）**
- 交付性质：**前置编码 + 模块级自测**。硬依赖 16B(`40ab818`)/12S-A(`77c395b`)/12S-B(`f62a29c`) **未全部接受合入**，按派单 attempt-1 口径**不申报"正式联调 PASS"**（9.6 卡明文：任何依赖未接受不做正式联调 PASS）。真链冒烟留**接线核验单**（三依赖全合入后协调者另派），本单不重做。
- 回执时间：2026-10-13 14:xx +08:00
- owner：C
- 分支/worktree：`c/task-12s-c-spray-wiring` @ `/home/wang/.local/state/rosbag-scene/wt-03b-t12sc`
- 交付 head：**`92dcb52`**

## 一、消费基线（回执注明——派单 line 11 口径）

派单 base="main 届时最新（16B-r1 合入后的 head）"。实测 main=`0e9a2df`（16A 已合入、含 07B/06B/16A）**未含** `40ab818`（16B-r1 仍冻结 REVIEW_PENDING，增量 OCR `--from 0208a73 --to 40ab818` 排队于 12S-B c02 后，ps 实测 c02 在途=协调者范围，C 不启动不接管）。**按派单 fallback 口径以 `40ab818` 所在链为消费基线**，并 merge main 补齐 16A（spray 入口/profile 所需）：

- base 链：`40ab818`（16B-r1 冻结 head）← merge `0e9a2df`（main，含 16A `6fb42c4`+07B+06B，零冲突）→ `e3f3fb5`
- 固定 SHA import 级集成（**byte-identical，git diff 与固定 SHA 为空=0 行**）：
  - 12S-A = `77c395b`：`app/schemas/scene_config.py`、`app/api/ingest_submissions.py`、`app/services/{bootstrap,ingest_service}.py`、`tests/test_scene_spray_intake.py`
  - 12S-B = `f62a29c`：`app/scene/spray/*`（11 模块）、`config/scene_capabilities.yaml`（spray 条目 enabled=false 起步）、`tests/test_spray_adapter.py`
- 三依赖消费 SHA 清单（本单 import/契约消费，未改动其产物）：16B=`40ab818`、12S-A=`77c395b`、12S-B=`f62a29c`

## 二、接线内容（9.6 卡产物面，最小 additive 改动）

本单真实产品改动 **27 行**（orchestrator +18 / proxy +9），全部 spray/adapter_key 门禁，**slope 行为面零改动**：

1. **EXTRACT/INFER/SEGMENT 消费 12S-B spray 适配器（固定 SHA import，不复制逻辑）**
   `scripts/scene_host_orchestrator.py` import `from app.scene.spray import SPRAY_ADAPTER_KEY`——import 本包即安装 `ros2-spray-v1` 适配器（对照 slope 包自注册口径）。`dispatch()` 按 `capability.adapter_key` 路由到 `SprayAdapter`（B 产物：解码→渲染→双pass模型→整数 ns 分段），八步编排（PRECHECK→…→REGISTER）复用 16B 既有引擎，**无新旁路**。
2. **`mapping_basis=bag_storage_ns` 复用现有 offset=0 分支**（水雾无 header 偏移）
   `scene_publish_service.derive_storage_offset` 对 basis 全 `bag_storage_ns` 已返回 0（既有 06B 代码，未改）；B 的 spray 分段固定 `mapping_basis=bag_storage_ns`（`time_map.MAPPING_BAG_STORAGE`）。测试 `test_offset_bag_storage_ns_reuses_zero_branch` 实证 offset==0。
3. **发布路径受控**：`work_root/<run_id>/<attempt>/staging` → 原子 rename 到受控 slices 根 `…/vehicle_key/spray/…`（06B `publish_scene_slices` 按 `scene_code` 命名，同文件系统 rename，未改机制）。父车辆绑定经 `spec.vehicle_key` 传递到发布树 vehicle 段。
4. **PRECHECK 消费 12S-B 7 图 hash 受控预检产物（fail-closed，不烧模型）**
   orchestrator `_step_precheck`：`cap.adapter_key == SPRAY_ADAPTER_KEY` 时调 `app.scene.spray.precheck.check_references()`（B 产物），7 参考图 hash/字节/顺序/JPEG 可解码任一不过 → `PRECHECK_SPRAY_REFERENCE_*` 阻塞（不进分析、不请求模型）。**decoder/render/模型可用性经 B `analyze` 既有 fail-closed 路径消费**（RENDER_UNAVAILABLE/MODEL_UNAVAILABLE/DECODE_FAILED→FAILED 归因），不复制 B 逻辑到编排层。
5. **元数据/车辆绑定消费 12S-A source_metadata（登记/回报面接线）**
   12S-A 在提交面强制 spray 入口 `source_metadata.vehicle_code`（缺→422 未调度）；父包车辆绑定后传递。`scripts/scene_host_proxy.py` `resolve_spec`：`scene_code == "spray"` 且父包缺车辆 = 父绑定链断裂 → `SpecError` fail-closed 不执行（不猜车、不静默 unassigned）。slope 保持既有 lenient `unassigned` 兜底（旧坡道无回归）。
6. **恢复/幂等/租约复用 16B 机制**：`(run_id, attempt)` 幂等、checkpoint 崩溃恢复、租约看门狗、协作式取消——spray 走同一 `SceneHostOrchestrator.run`/`execute_run`，无新旁路。

## 三、模块级自测证据（9.6 卡清单，真实执行）

新增 `tests/test_scene_spray_wiring.py` **11 passed**。模型/渲染用确定性替身（`DeterministicModel`/`patch_render`，复用 B 面替身），7 图 hash 预检走**真实受控目录** `SPRAY_REFERENCE_DIR=/home/wang/work/ros2_slice/images/refs`（B 面 `test_real_refs_7_of_7` 已核验 hash）；**真实 VLM / 真实渲染不做**（留 12S-D 授权执行面；open3d 本机缺失=处理机依赖，不 mock 当真实渲染）。

| 9.6 清单项 | 测试 | 关键断言 | 结果 |
|---|---|---|---|
| 正常八步水雾→results/complete/reconcile | test_success_publishes… | 八步全 DONE；manifest SUCCESS；发布落 `…/spray-veh-01/spray/`；REGISTER report+complete 子包 uid 一致 | PASS |
| `bag_storage_ns` 复用 offset=0 | test_offset_bag_storage… | `derive_storage_offset`==0（水雾无 header 偏移） | PASS |
| 无命中 | test_no_match… | NO_MATCH；不发布；只 complete 无 report（无文件义务） | PASS |
| 缺前雷达 topic | test_not_applicable… | NOT_APPLICABLE 终态（非 FAILED）；EXTRACT DONE | PASS |
| PRECHECK 7 图失败不烧模型 | test_missing_references_blocks… | step==PRECHECK；`PRECHECK_SPRAY_` 码；模型 judge 调用数==0；未发布 | PASS |
| 恢复/幂等（复用 16B） | test_recovery_reuses_manifest… | 同 identity 重跑复用 manifest；**模型调用 0**（不重复计费）；digest 不变 | PASS |
| 失败归因 | test_model_failed… | MODEL_FAILED 归因 INFER（非 NO_MATCH）；不发布 | PASS |
| **旧坡道 header 轴一包恢复回归（硬证据）** | test_slope_header_axis_crash_recovery… | **同进程已 import spray 适配器**下：slope offset 推导非 None、恢复重跑模型调用 0、digest 不变、全链 SUCCESS | PASS |
| 消费 12S-A 车辆绑定（fail-closed） | test_spray_missing_vehicle… | spray 缺车辆 → SpecError（不猜车） | PASS |
| 消费 12S-A 车辆传递 | test_spray_with_vehicle… | `spec.vehicle_key`==父包车辆（非 unassigned） | PASS |
| slope 缺车辆 lenient 无回归 | test_slope_missing_vehicle… | `spec.vehicle_key`=="unassigned"（旧坡道口径保持） | PASS |

**同 run/attempt 重复、响应丢失对账、manifest/checkpoint 断点、取消/租约失效** 属 16B 既有机制面（本单 spray 复用同一 `SceneHostOrchestrator`/`execute_run`，非本单新增行为）——由 16B 既有回归覆盖（下表），本单不重复实现；接线核验单真链冒烟时统一复核。

## 四、回归 / 零越界（真实执行）

命令/退出码/环境：
- `.venv`（主仓 python3.10，worktree 软链）、`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`、dev 机（open3d 缺失=预期，渲染走替身）
- 定向 + 回归合集：`pytest tests/test_scene_host_orchestrator.py tests/test_scene_host_proxy.py tests/test_scene_capability_contract.py tests/test_scene_spray_wiring.py tests/test_spray_adapter.py tests/test_scene_spray_intake.py -q` → **148 passed**（16B 编排 12 + 16B 代理 20 + 能力契约 26 + 本单接线 11 + 12S-B 适配器 54 + 12S-A intake 25），exit 0
- `ruff check scripts/scene_host_orchestrator.py scripts/scene_host_proxy.py tests/test_scene_spray_wiring.py` → **All checks passed**
- `python -m compileall` 三文件 → OK

零越界核实：
- 本单产品改动仅 `scripts/scene_host_{orchestrator,proxy}.py`（§9.2 12S-C 独占面）+ 新测试文件；`git diff --numstat 22ffb71..HEAD` = `18/0 orchestrator + 9/0 proxy + 470/0 test`，**无 app/ 行为面改动**
- 12S-A/B 产物 import 后 **byte-identical**（`git diff 77c395b..HEAD -- app/{schemas/api/services}` =0、`git diff f62a29c..HEAD -- app/scene/spray` =0）
- 不碰 16C 冻结面/07B 文件、不部署生产、不跑真链全冒烟、真实 VLM 不做

## 五、未执行项 / 越界申报 / 留待接线核验单

- **未执行（派单明确留后）**：真实 VLM 调用、真实 Open3D 渲染、真链全冒烟（三依赖全合入后接线核验单）；`/run` 八步**正式联调 PASS** 不申报（依赖未接受）。
- **口径待协调者/OCR 确认（非越界，属解释）**：
  1. "发布到 12S-A 的 spray profile 受控 slices 根"——本单按**既有受控 slices 根（`SCENE_SLICE_PUBLISH_ROOT` 部署配置）下 `…/vehicle/spray/…` 场景子树**（06B `publish_scene_slices` 按 `scene_code` 命名，原子 rename），spray profile 控制的是 intake 根（A 面窄前缀 `spray/`）；**未新开 per-scene 发布根配置**。若协调者意图是独立 spray 发布根，请裁决回派。
  2. `resolve_spec` 消费 12S-A 车辆绑定的**判定信号**用 `source.bag.vehicle.vehicle_code`（父包登记值，A 面提交时 fail-closed 已保证非空）；run 快照 `scenes[0]` 不携带 `source_metadata` 块（16B H5 已知口径=快照只存 scene_code/capability_version/capability_config_hash），故本单不新增读快照面，改读父包车辆（既有 resolve_spec 已读 `bag.vehicle`）。若意图是直读快照 source_metadata，请裁决。
- **16B H5 下限口径在案**：`capability_config_hash` 冻结值 fail-fast（快照不存提交参数，非默认参数 run 在烧模型前 fail-closed 不执行）——本单 spray 默认参数 run 不受影响（`effective_params("spray", None)` 与冻结 hash 一致），非默认参数 spray run 会走 H5 fail-fast（16B 既有行为，非本单引入）。

## 六、收口链（等协调者）

机械核验 → 增量 OCR（本单 `92dcb52` 消费面 27 行 + base import）→ 强审 pack（`auth-24h-20261013` 期限内，范围=本次 spray 接线 2 文件）→ **三依赖 16B/12S-A/12S-B 全合入后派接线核验单**（真链冒烟 + 12S-D 输入）→ 12S-C DONE。本单 findings 届时增量 OCR，不重做前置编码。