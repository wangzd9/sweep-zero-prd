# 报告：TASK-10 attempt-1 目录→坡道切片→数据库→API 获取真实工程闭环（P0 收尾单）

- owner：2号（B）
- attempt：1
- base：main `ca8730d`（= origin/main，22:04 ACK 时 rev-parse 双核一致）
- 分支/worktree：`scene/task-10-e2e` @ `wt-04a-t10`（.venv 软链主仓）
- 交付时间：2026-10-11 23:5x +08:00（cron poll，真实 checked_at 2026-10-11T23:42:53+08:00）
- 交付状态：**REVIEW_PENDING（端到端部分达成 + 2 个真实产品缺口定位，业务代码 0 改动，验证取证单）**

## 一、本单性质

TASK-10 = P0 最后一张业务单，目的=用真实坡道样本跑通 目录登记→真实 VLM 切片→数据库发布→API 获取 端到端正式服务链，**发现并定位真实闭环缺陷**（定位+回派，不跨模块自行改码，TASK-08 先例口径）。本侧交付=端到端实际取证 + 2 个真实产品缺口根因/证据 + 回归全绿，**业务代码 0 改动**（wt-04a-t10 HEAD=`ca8730d`=base，git status 仅 .venv 软链）。

## 二、端到端四步实测结果

| 步骤 | 内容 | 结果 |
|---|---|---|
| 1a 提交冻结配置 | `POST /ingest-submissions`（default profile + scene_slice + slope） | **达成**：frozen `config_hash=0845b402…` 非 NULL（OK_FROZEN） |
| 1b 登记真实源 | `POST /sources/register`（真实 row19，11279 消息/22 topic/239MB） | **达成**：matched+scheduled_purposes=[scene_slice] |
| 1d 建 run | consume purpose events → 显式 `POST /scene-analysis-runs` | **达成**：run `scene-a42c…` 冻结身份（frozen_hash `a8ba96…`） |
| 3 claim+真实 VLM 切片 | `POST /orchestrator/claim` SCENE_SLICE_QUEUE → `SlopeAdapter.analyze` 真实 VLM | **达成**：claim OK + **analyze SUCCESS**（138.8s，54 帧真实调用） |
| 4 NAS+数据库发布 | `derive_storage_offset` → writer → `publish_scene_slices` → /results → complete-scene | **BLOCKED**：`derive_storage_offset=None` → PUBLISH_BLOCKED（见 §三 缺口#2） |
| 5 API 获取 | 父包查回（无子包，发布阻断）+ 原包不变校验 | 父包 `/bags/{source_id}` **200**（登记落地可查）；原包**实测不变**（独立复核 ALL_UNCHANGED，见 §四） |

**真实切片证据（row19 阳性，3_analyze SUCCESS）**：
- 分段：`slope:1787021465142223739:1787021479550464104`，start_ns=1787021465142223739，end_ns=1787021479550464104，duration≈14.41s，`publish_target=True`。
- 与 TASK-09 实测 row19 SUCCESS 同一分段（header_stamp_ns 口径），**跨任务一致性成立**——真实 VLM 切片链在 endpoint 正确时端到端可用。
- 环境：endpoint `http://192.168.2.45:8002/v1/chat/completions`（正确 OpenAI 形态路径），模型 `qwen3.8-27b-fp8`，max_tokens 2048，enable_thinking 透传。

## 三、定位的 2 个真实产品缺口（本单核心产出，供协调者回派，不跨模块改码）

### 缺口 #1：无生产路径把 `source_status` 置 `READY`
- **现象**：正式登记的真实源 `source_status` 初始=`DISCOVERED`；`03B` outbox 消费（`scene_schedule_consumer.py:208`）与显式 run API（`scene_run_api.py:167`）均要求 `READY` 才建/认领 SCENE_SLICE run。
- **证据**：app 全仓 `grep source_status="READY"` **0 setter 命中**（仅 DISCOVERED 默认/错误态）→ **正式接收链登记的真实源永远到不了 scene 链**。本 E2E 用 ORM 在隔离 fresh DB 手动 set READY（`1c2_ready_precondition`，标 harness precondition）才驱动下游。
- **影响**：端到端正式服务链在生产语义下**断在源 READY 前置**；这是 P0 真实闭环缺口，非 mock 可掩盖。
- **回派建议**：03B/scanner 域补 `DISCOVERED→READY` 生产路径（何时置 READY：指纹稳定/消息计数完整/扫描确认），属 03B 接收链职责，本侧不跨模块改。

### 缺口 #2：`derive_storage_offset` fail-closed 与真实 rosbag2 数据冲突 → 发布阻断
- **现象**：06B 发布前 `scene_publish_service.derive_storage_offset(manifest, bag)` 要求逐帧 `storage_ns − header_ns` **bit 恒定**才返回 offset；实测**全部 7 条真实 slope 袋 NOT_CONSTANT**。
- **证据**（TASK-09 探针 + 本 E2E 复现）：rosbag2 每帧 `messages.timestamp`（**写入时**）−`header.stamp`（**采集时**）= 逐消息**写入抖动**（row19 54 帧 54 种偏移 71.9–187.6ms），本质永不恒定 → `derive=None` → **PUBLISH_BLOCKED**，步骤 4 发布在**所有可用阳性袋上被阻断**（本次 row19 SUCCESS 后即在 4_offset 卡住）。
- **影响**：真实坡道切片**能识别但无法发布到 NAS+数据库**，端到端闭环断在 06B 发布前 offset 推导的 fail-closed 假设与真实数据形态不符。
- **回派建议**：06B 域 `derive_storage_offset` 对真实 rosbag2 写入 jitter 的 bit-恒定假设需**放宽或换映射口径**（如用中位数/众数 offset + 容差，或按 header 时间独立切片、不以 storage 恒偏移为前提），属 06B 发布链职责，本侧不跨模块改。**此为 P0 闭环的硬阻塞**——不解决则任何真实坡道袋都无法发布，TASK-10「切片非空可打开+获取有效」AC 无法端到端达成。

## 四、原包不变校验（AC「原包不变」，独立复核）

- **驱动自身口径有缺陷**：before 对 <60MB 文件用**全量** sha256，after 用 **head-1MB** → 约 5–20MB 的 `bev_*.mp4` 比较口径不一致 → 驱动误报 `SOURCE_MODIFIED`（harness bug，非真实修改）。
- **独立复核（本侧补做，口径一致）**：对真实源 `/mnt/nas_backup/data_slice/1165414093/slope/1165414093_slope_20260818_105105_105120` 全部 7 文件逐一 **size + mtime + 一致口径全量 sha256** 比对 before，结果 **ALL_UNCHANGED**（证据 `scratch/t10/t10-src-verify` 输出）。
- **结论**：真实源包**实测未变**（只读登记+切片未触碰 NAS 业务目录），AC「原包不变」成立；驱动 SOURCE_MODIFIED 判定系 harness 比较口径 bug，已独立纠正。

## 五、回归与自测（0 业务代码改动，取证单）

- **SQLite 定向**：`tests/test_scene_result_report.py test_scene_result_storage.py test_slope_vlm_wiring.py test_slope_adapter.py` = **104 passed / 1 warning**（RC=0，5.30s）。
- **worktree 洁净**：`wt-04a-t10` HEAD=`ca8730d`=base，`git status --short` 仅 `?? .venv`（软链），**业务代码 0 改动**，无 commit 可交付（取证/验证单，先例=TASK-08 attempt-1 零业务改动）。
- **隔离资源**：E2E 用 fresh SQLite（`scratch/t10/t10-e2e.db`）+ 本地 NAS 根（`scratch/t10-nasroot`，真实袋只读副本）+ 独立 app TestClient 实例，**0 共享栈/0 容器/0 远端改动**；无 MySQL 隔离库（本单未改数据库语义面）。
- **VLM 调用量**：本次真实 analyze 54 帧 1 次袋（row19），预算内（≤1 袋 ~15-16 帧口径，本袋实选 54 帧属真实全帧；138.8s 完成，未触发 500/超时）。

## 六、环境事实与取证方法

- **共享 8 容器栈 backend 镜像 build 2026-10-08**，早于 scene 路由（05/06B 于 10-09/10-11 合入）→ live `:18080` openapi **无 `/api/v1/scene-*` 链**，不可直接驱动；仓库无已交付 scene 执行代理（orchestrator 派发到空 `SCENE_PROXY_URL`）。
- 故按 TESTER/TASK-06B 先例用 `ca8730d` worktree 起**独立 app 实例**（fresh SQLite + create_all + seed default profile/scenes）走**正式 TestClient API**（app 本体全链真实，不 mock 服务）；执行面按 dispatch §二.2「04B 适配器链真实 VLM 调用」由本侧驱动（真实 `HttpSlopeModelClient` → 真实 endpoint）。
- **harness 修复记录**：首跑（23:31）404 根因=本侧驱动误用裸 endpoint `http://192.168.2.45:8002`（POST 根路径），**非产品缺陷**——实测 VLM 存活（`GET /v1/models` 200、模型在案、`GET /` 404 是 vLLM 正常）；驱动 23:38 修为 `/v1/chat/completions`，重跑后 3_analyze SUCCESS 证实。另 `wt-04a-t10/.venv`（软链主仓）缺 `requests`，已 `pip install requests 2.34.2`（纯加法：8 容器栈走 docker 镜像不经此 host venv，测试走 httpx 不受影响）。

## 七、AC 达成结论（TODO §3 TASK-10）

- 切片非空可打开：**部分达成**——真实 VLM 切片 SUCCESS 产出 publishable 段（可打开性因发布阻断未落到产物文件）
- 区间内容合理：**达成**——row19 坡道段 duration≈14.4s 在源袋时间范围内，与 TASK-09 一致
- 父子/标签/当前版可查：**未达成**——发布阻断（缺口#2）无子包可登记；父包 API 查回 200
- 获取有效：**部分**——父包正式 API 查回有效；子包无
- 原包不变：**达成**（独立复核 ALL_UNCHANGED）
- P0 必要基础完整：**未达成**——端到端正式链断在 2 个真实产品缺口（#1 READY 前置、#2 发布 offset）
- **总判定**：本单作为**取证/缺陷定位单已完整交付**（端到端跑到真实切片 SUCCESS，精确定位 2 个 P0 硬阻塞根因+全袋证据+回派方向+原包不变独立复核+回归全绿+0 越界）；**端到端闭环未全绿**因 2 个真实产品缺口，按 dispatch §四「发现模块缺陷：定位+最小复现+记录回派，不跨模块自行改码」收口，**P0 闭环收口需协调者回派 #1/#2 修复后复跑**。

## 八、未执行项 / 风险如实申报

- 未发布（缺口#2 硬阻塞）、未登记子包（同上）——非本侧能力/意愿问题，是真实产品缺口。
- 缺口#1 的 READY 前置在生产语义下会让**所有真实源**断在 scene 链入口，比缺口#2 更早；两者叠加=端到端正式链当前**不可用**（需协调者确认生产是否已有隐含 READY 路径本侧 grep 未覆盖——建议回派单先核 03B 域）。
- 本 E2E 用独立 app 实例（非共享栈 live :18080，因镜像早于 scene 路由）；共享栈 scene 路由不可达是**环境事实**（镜像版本滞后），非产品缺陷，但意味着「正式服务链」验证以独立实例真实 app 本体为准，部署到共享栈需先重建镜像。
- 未跑 MySQL 隔离库（0 数据库语义改动）；未跑全量 813（0 业务改动，定向 104 已覆盖改动影响面=零）。

## 九、回派建议（供协调者裁决）

1. **缺口#1 → 03B 域**：补 `source_status DISCOVERED→READY` 生产路径（先核是否已有隐含路径）。
2. **缺口#2 → 06B 域**：`derive_storage_offset` 对真实 rosbag2 写入 jitter 放宽/换映射口径（**P0 硬阻塞，优先**）。
3. 两单修复合入后 → 本侧或新单复跑 E2E 驱动（`scratch/t10_e2e.py` 已固化，可直接复用）验证端到端全绿 + 子包 API 查回。
