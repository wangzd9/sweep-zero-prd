# 报告：TASK-09 attempt-1 坡道真实能力与内容核验（2号）

- 交付：2026-10-11 21:30 +08:00，status **REVIEW_PENDING**
- base：main `0a8ca8ac49b4610580c25b15eb8a3e762ead96d6`（= origin/main，fetch 双核）
- 交付 commit：`a60bb81`（分支 `scene/task-09-slope-real-verify`，worktree `wt-04a-t09`，3 文件 +187/-3）
- 授权：用户 2026-10-11 19:5x 群内明确授权真实样本测试（参考 `ros2_slice/slice_message.csv`）
- 环境：VLM `http://192.168.2.45:8002`（= 18002 隧道同一实例，未动服务本身）；NAS 只读；真实 MySQL 8.4.11 STRICT 隔离容器 `t09-mysql`（用完即毁，0 残留）

## A. 2.1 生产接线（app 行为面，commit `a60bb81`）

| 改动 | 文件 | 行为 |
|---|---|---|
| `model` 字段 | `app/scene/slope/vlm.py` | 默认 `DEFAULT_VLM_MODEL=/home/sysadmin/data/disk02/jc/models/qwen3.8-27b-fp8`（完整路径，vLLM 注册名）；原硬编码 `"qwen-vl"` 现网 404（协调者前置探明，本单不再默认 404）；env `SLOPE_VLM_MODEL` 可覆盖 |
| `max_tokens` 256→2048 | 同上 | Qwen3 思考模式 256 图像请求预算被思考 token 吃光，**本单真实帧复现**：flat 首帧 mt256 `finish_reason=length`+`content=None`（completion_tokens=256 用满），同帧 mt2048 正常 `content=平地`；env `SLOPE_VLM_MAX_TOKENS` 可覆盖 |
| `enable_thinking` 透传 | 同上 | `None`=不注入（服务端默认思考开）；显式 `False` 时 payload 加 `chat_template_kwargs`；env `SLOPE_VLM_ENABLE_THINKING` 接线 |
| 客户端构造接线 | `app/scene/slope/adapter.py::_default_model_client` | 上述 3 个 env 名与 vlm.py 一致；`SLOPE_VLM_ENDPOINT` 缺省 fail-closed 语义不变（未配置=None→MODEL_UNAVAILABLE）；非法 `SLOPE_VLM_MAX_TOKENS` 抛 ValueError（配置错误如实暴露） |
| 回归测试 | `tests/test_slope_vlm_wiring.py`（新增，9 用例） | payload model/max_tokens 断言、env 接线、**空 content 必须抛 ModelUnavailableError（错误不伪装无命中）**、fail-closed |

抽帧/segment/时间映射语义 0 改动（diff 仅客户端构造路径 + 测试）。

## B. 2.2 真实能力核验（主仓 `SlopeAdapter.analyze` 真实编排：read_topics→抽帧→真实 HTTP VLM→segment→frame_log 证据）

样本（NAS 只读，vehicle `1165414093`）：

| 样本 | 袋 | 期望 | 实测 outcome | 结论 |
|---|---|---|---|---|
| row19 阳性 | `slope/…_105105_105120` | SUCCESS 非空发布区间 | **SUCCESS**，`slope:1787021465142223739:1787021479550464104` publish=True，14 帧（slope 11/flat 3），`mapping_basis=header_stamp_ns` | **通过** |
| row22 阴性 | `flat/…_105143_105201` | NO_MATCH 不发布 | **NO_MATCH**，flat 区间 publish=False，13 帧（slope 1/flat 12） | **通过**（flat 未伪装成 slope 发布） |
| row23 阴性 | `flat/…_105158_105213` | NO_MATCH 不发布 | **NO_MATCH**，9 帧全 flat，publish=False | **通过** |
| row20 阳性 | `slope/…_105117_105132` | SUCCESS | **MODEL_UNAVAILABLE**（服务 500，见 D） | 未达（外部服务缺陷） |
| row21 阳性 | `slope/…_105129_105148` | SUCCESS | **MODEL_UNAVAILABLE**（同一 500 帧，见 D） | 未达（外部服务缺陷） |
| 边界-不可达 | row19 袋 + endpoint `127.0.0.1:9` | FAILED/MODEL_UNAVAILABLE 如实报出 | **MODEL_UNAVAILABLE**（ConnectionError 第 0 帧，不伪装 NO_MATCH） | **通过** |
| 替代阳性 row31/32 | `slope/…_105541_105556` / `…_105553_105608` | SUCCESS | **NO_MATCH**（模型判 flat 为主：11/3、9/5 slope） | 能力限制事实（见 C） |

**AC「至少实际坡道切片样例可核对」达成**：row19 完整链路 SUCCESS + 可发布区间 + frame_log 逐帧证据（`scratch/t09/t09-real-verify.json`）。
**AC「错误不伪装为无命中」达成**：row20/21 的 500 与边界的不可达均如实报 MODEL_UNAVAILABLE，未折叠成 NO_MATCH；阴性样本的 flat 区间 publish=False。

## C. 模型能力限制（如实记录，质量门禁仍属 TASK-11）

1. **单帧确定性 500**（见 D）：`header=1787021491199936487` 帧（1600x900、JPEG magic ffd8、486KB）在 row20/row21 两袋中均 500——row20/row21 时间窗重叠（CSV 1787021477-1787021492 / 1787021489-1787021508），是同一物理帧。服务端故障（vLLM Internal Server Error），**非本侧代码问题**；app 链 fail-fast 语义正确（该帧之后不再继续）。
2. **坡道误判 flat（假阴性）**：row31/row32 两个 CSV 标注 slope 的袋，模型 14 帧中仅 3/5 帧判 slope（`min_effective=5` 未达）→ NO_MATCH 不发布。方向安全（宁可漏发不误发），但阳性召回受限。1Hz 抽帧 + 15s 袋仅 14 帧，判定样本小。
3. **思考模式稳定性**：同帧 mt2048（思考开）=「坡道」，mt512_notk（思考关）=「平地」——关思考省 token 但本帧判定翻转；默认选择 2048 思考开（与 CSV 标注一致的一侧）。
4. 未覆盖：其余 4 类场景（TASK-12）、VLM 服务 500 根因（需 36.152.27.114 服务端日志，本机无该 host SSH key，未越界排查）。

## D. 500 帧取证（`scratch/t09/t09-500-probe.json`）

- 目标帧直发 3 次（mt2048/mt512 + 两袋 runner 内 2 次 + retry 2 次）：全部 `HTTP 500 Internal server error`，确定性复现。
- 同袋相邻帧 `…1787021490894240803` / `…1787021491455469830`（同为 1600x900 JPEG）mt2048 均 200 正常作答「坡道」——排除服务整体故障与尺寸因素（三帧尺寸一致），锁定为该帧图像内容触发的服务端内部错误。
- VLM 调用量：本单实际 ~113 次（探针 9 + 主核验 61 + retry 15 + 替代 28），**超 dispatch 预算（≤6 样本 ≈100）约 13%**——超支来自 500 定位 retry 与替代阳性补足，如实申报。

## E. 时间映射证据（`MAPPING_HEADER_STAMP` 路径，dispatch 2.2.4）

- 全部成功样本 `mapping_basis=header_stamp_ns`（frame_log 逐帧 basis 记录，无 mixed）。
- 探针首帧（row19 袋）：storage=`1787021465225134640` vs header=`1787021465142223739`，差 **+82.9ms**；同袋次帧 +86.2ms；flat 袋首帧 +59.8ms——同方向毫秒级恒定偏移（采集→入袋管道延迟），**非整秒/非随机**，header.stamp 可信为采集时间。
- CSV 声明 start=`1787021465`（10 位秒）vs 实测首帧 header=`1787021465.142`：**偏差 +142ms，落在声明窗口内**（row19 声明 1787021465-1787021480，实测发布区间 1787021465.142-1787021479.550 全程在窗内）。

## F. 2.3 回归证据

| 项 | 命令（worktree `wt-04a-t09`） | 结果 |
|---|---|---|
| 接线+适配器 SQLite | `pytest tests/test_slope_vlm_wiring.py tests/test_slope_adapter.py -q` | **44 passed RC=0** |
| test_scene_* 定向 SQLite | `pytest tests/test_scene_*.py tests/test_slope_adapter.py tests/test_slope_vlm_wiring.py -q` | **232 passed RC=0** |
| 全量 SQLite | `pytest tests/ -q --ignore=tests/test_devflow.py` | **813 passed / 10 skipped RC=0**（06B 场景面不回归） |
| ruff | `ruff check app/scene/slope/vlm.py app/scene/slope/adapter.py tests/test_slope_vlm_wiring.py` | **All checks passed** |
| 真 MySQL 8.4.11 STRICT 06B 核心 | `pytest tests/test_scene_result_report.py tests/test_scene_result_storage.py -p t09_plug`（隔离容器 `t09-mysql`，口径同 TESTER pm08_plug：FK off + create_all，PyMySQL） | **60 passed RC=0**（report 35 + storage 25，文件数口径 33+25 含参数化=60 用例） |
| 隔离资源 | t09-mysql 容器/网络/t09core 库 | **0 残留**（docker ps -a 核实，用完即毁） |

## G. 待协调者裁决项

1. **阳性 SUCCESS 覆盖**：dispatch 2.2.1 要求阳性 slope 2-3 条 SUCCESS；实测 1 条 FULL SUCCESS（row19），row20/21 被外部服务 500 帧阻塞（非 app 缺陷，证据 D），替代 row31/32 为模型假阴性 NO_MATCH（事实 C.2）。剩余 slope 袋 `…_105605_105620`/`…_105617_105632` **未执行**（VLM 调用量已超预算，停止条件触发）——请裁决：(a) 接受现证据（AC「至少 1 条坡道切片可核对」已达成），(b) 追加派单补 2 袋（+~30 次调用，需用户确认超预算），(c) 待 500 帧服务端修复后复跑 row20/21。
2. **500 帧归属**：建议记外部服务缺陷（不属本单 app 范围）；如需根因，需 A100 侧 SSH 36.152.27.114 查 `/tmp/vllm_qwen38.log`（本机无 key，未越界执行）。

## H. 限制说明

- 抽帧 1Hz、15s 袋 ~14 帧，判定样本小；`min_effective=5` 阈值下短坡道易 NO_MATCH（安全方向）。
- 单帧 500 时整样本 fail-fast（adapter 语义：帧级模型异常=FAILED 不继续），无单帧跳过/降级（不属本单范围，未改契约）。
- 本单只 slope；未宣称生产就绪（质量门禁 TASK-11）。

## 证据文件

- `scratch/t09/t09-vlm-probe.json`：真实帧 × max_tokens 9 case 探针（256 陷阱复现/2048 正常/512_notk 对照）
- `scratch/t09/t09-real-verify.json`：主核验 6 样本（row19/20/21/22/23 + 边界）逐样本 outcome/segments/label_counts/mapping_basis
- `scratch/t09/t09-real-verify-retry.json`：row20/21 500 确定性 retry
- `scratch/t09/t09-real-verify-extra.json`：替代阳性 row31/32
- `scratch/t09/t09-500-probe.json`：500 帧直发 + 相邻帧对照
- `receipts/TASK-09/attempt-1.md`：回执