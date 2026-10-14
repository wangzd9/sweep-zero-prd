# 派单：TASK-12S-B 水雾能力 attempt-1（协调者 r147 派发，2026-10-13 11:5x +08:00）

- **角色/owner**：执行者 B（2号）｜**attempt**：attempt-1｜**父任务**：TASK-12S（TODO §9 v0.5 水雾优先）
- **前置**：16C 界面增量已按用户要求 PAUSED（`wt-04a-t16c` 冻结 head `5c80857`，**零触碰**）；你当前空闲，本单为 §9.2 标记的下一就绪叶任务。16B 仍 NEEDS_REVIEW 冻结，与本单无关，不接管。
- **固定 base**：`6fb42c4`（= origin/main，16A 已合入；领取时 `git fetch` 后双核一致才可开工）
- **worktree**：新建 `wt-04a-t12sb`（分支 `b/task-12s-b-spray`），.venv 软链主仓；**不移动/复用 `wt-04a-t16c`**（16C 冻结证据面）。
- **最小阅读**：SESSION-START → TODO §9（9.2/9.3/9.5 卡）→ `SPRAY-INTEGRATION.md`（§1/§2/§3/§4）→ `RAW-DATA-REQUIREMENTS.md` → ACCEPTANCE `AC-17.1/17.2/17.3` → `app/scene/slope/`（既有真实适配器接线样板）+ `app/scene/adapter.py`（SceneAdapter 协议 + register_adapter）+ `config/scene_capabilities.yaml`（能力登记格式）。

## 交付范围（仅这些，逐文件核 diff）

1. **spray 适配器与注册**（新增 `app/scene/spray/` 包 + 在 `app/scene/adapter.py` 的 `_ADAPTERS` 注册 `ros2-spray-v1`）：
   - `scene_code=spray`、`capability_version=spray-v1`、`adapter_key=ros2-spray-v1`；
   - 实现 `SceneAdapter` 协议（analyze/applicability/segment/writer 面参照 `app/scene/slope/`），**核心 dispatch 不加任何 spray 硬编码分支**（AC-10 口径，参照 slope 先例）；
   - descriptor 与真实 adapter 同一 owner（你）：源码在但依赖缺失时返回明确 `unavailable_reason`，**不把 enabled 当可用**。
2. **两路线输入，按 sensor profile 选择**（不 AND、不默默用后雷达，见 SPRAY-INTEGRATION §2）：
   - 优先 `/iv_packets_front_mid`（`seyond/msg/SeyondScan`）→ 已批准 packet2pointcloud（`/home/wang/work/ros2_slice/utils/packet2pointcloud` x86-64 ELF；型号/动态依赖只在**处理机**安装，本单做服务端预检 + 路径封装，不迁 A100）；
   - 替代 `/iv_points_front_mid_transformed`（PointCloud2 x/y/z/intensity，校验字段布局/强度/offset/row_step/字节序）。
   - 缺 topic = **NOT_APPLICABLE**；存在但不能解码/渲染无有效图 = **FAILED**（packet 子进程 returncode、实际 PCD、有效渲染图、有效判断数逐项区分，禁止照搬原 `result == '是'` 口径导致全 NO_MATCH）。
3. **本机预处理冻结**（SPRAY-INTEGRATION §3，保持原调用的行为与参数，不降尺寸/频率/阈值）：PCD 有序序列跳过前 10 帧、每 3 帧取 1；渲染 3840×2160 旋转 90°、ROI x=(-2,6)/y=(-3,3)、intensity 配色、JPG q95；参考图过滤阈值 500KiB，**过滤数量/失败/剩余数必须记录**；过滤后无足够有效数据 = FAILED（不把图片小当「无水雾」）。GPU/CPU 离屏渲染在本机实测；EGL 不可用时用已验证输出等效的本机软件渲染。
4. **模型判定归一**（§3）：复用 `SPRAY_SYSTEM` + `SPRAY_PROMPT_V18` + `SPRAY_PROMPT_SIM` 双 pass；pass1 明确异常直接判异常，否则按 pass2 参考图编号复核（1~4 正常 / 5~7 异常）；归一 `spray/normal/unknown`；HTTP 错误/解析失败有界重试后仍不确定 = FAILED，**禁止 `!=异常` 统称正常**。每 pass 记录目标图/参考图重复传输 bytes 与重试次数（不只统计目标图）。
5. **时间轴与分段**（§4）：全程**源 DB3 存储时间整数纳秒**（不从本地时间文件名/毫秒 round 回推；旧二进制若只输出 ms，在工作副本/包装层建立确定映射并检验，重复/歧义拒绝，**不把 ms×1e6 冒充源 ns**）；沿用 analysis_ros2 实际参数 window_size=15s / min_abnormal_ratio=0.15 / enter=3 / exit_=5 / 前置 3s / 重叠>=7s 合并，整数 ns 保留相同语义，参数 schema 校验（密度[0,1]、整数阈值>=1、时长>0）；短包可裁剪窗口不补帧，抽样不足不得 NO_MATCH。
6. **缓存/证据**（§2/§3）：run/attempt 私有 work 目录 + 完整 manifest/hash 判断缓存（**禁止「目录非空」判完成、禁止 PCD/图/cache 写原包内**，保持 NAS 原包不可变）；执行证据含模型名/修订、提示词 hash、7 图有序 hash、decoder/render 修订、预处理参数、源指纹与帧摘要；改变参考图不复用旧判断；取消不继续写。
7. **参考图受控**（§3）：严格 7 文件清单 `SPRAY-REFERENCES.json`（source_commit `be23177eca685b5f0f75160ca82503beeb63147d`，本机 `/home/wang/work/ros2_slice/images/refs/` 已核 7/7，逐图 sha256/bytes/尺寸/顺序）；部署路径由服务端 `SPRAY_REFERENCE_DIR` 受控提供，启动预检校验非空/可解码/hash/顺序，缺失返回 `REFERENCE_MISSING`；不把待判定图当参考图，不虚造替代图。
8. **能力登记**（`config/scene_capabilities.yaml`）：新增 `spray-v1` descriptor（`enabled=false` 起步，资产/依赖未核实不宣称可用；`model_profile` 复用 slope 的 VLM 面，见 §9.3「spray 与坡道共用原 VLM/NAS 额度」）；**原 slope / test-capability 条目零变化**。
9. **测试**：合成已知命中与正常、字符串冲突修正（原代码结果字符串不一致归一）、未知/空图/空模型 FAILED、缺 topic NOT_APPLICABLE、缺图/非零 converter 返回、PointCloud 字段布局/强度校验、短包/边界/乱序/多 DB3、源不变（原包 hash 前后一致）/取消/缓存版本。
10. **真实渲染 + 模型多图成功证据（有界，可 NOT_RUN）**：用只读小包 `/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`（57MB/4.38s，只读，不复制/不写/不迁 A100）做转换/渲染探针；模型面复用既有 `VLM_PERMITS`（直连 `192.168.2.45:8002/v1`，18002 隧道当前已断，模型 ID 用完整路径，**Qwen3 思考模式 max_tokens=256 图像请求 content=None 陷阱，建议 2048**）。**有界**=≤1 包、帧数/bytes 预记账（基线 7 图 Base64 ≈20.25MB/pass，双 pass 可 ≥40.5MB/帧），超预算/带宽/依赖缺失**如实报 NOT_RUN，绝不 mock 当 PASS**。真实模型调用属 v0.5 已授权范围（§9.5 自测面），不另扩付费。

## 验收（AC，ACCEPTANCE.md）

- **AC-17.1**：spray-v1 正常注册且实装；两路线按 profile 正确选择；缺 topic 不适用 / 缺图/坏 decoder/渲染无图失败区分；不写原包、不迁非模型计算到 A100。
- **AC-17.2**：模型异常/正常/未知归一正确；双 pass 与 7 图顺序保留；15s/0.15/3/5/前置 3s/合并 7s 规则与 storage 整数 ns 可对照；未知不充当正常。
- **AC-17.3**：跨 DB3、乱序/重复、短包/缺帧正确或明确失败；用源 storage ns 不从本地时间文件名猜；缓存/恢复含参考图与规则版本；取消不继续写。

## 硬边界（越界即停并回报协调者，不自行扩）

- **禁止新模型/迁移/DDL**（`app/models.py`、`alembic/versions/` 不动）；`intake_snapshot_json` / `ingest_submissions` / `scene_config.py` DTO / source_metadata 属 **12S-A（A 在途）**，不写不抢——若 spray 需要新 config/env 字段，**书面提给协调者**，由 12S-A 集中供应（§9.3）；
- **不碰**：`scripts/`（16B 域）、`app/web/` + `app/templates/` + `bag_search_service.py` + `scene_result_query.py` + `app/api/sources.py`（16C 暂停冻结面）、`ros2_slice` 仓库（只读复用其算法契约与参考图，不改其代码）、slope 既有模块行为面（零回归）、16A 已合入双根语义；
- 1012 目录**只读**；运行产物只落私有 work 与授权 staging，NAS 原包不可变；
- 缺图/decoder 型号/软件渲染不等效 = 阻断真实 PASS，**不迁 A100、不加图像生成、不随意降阈值**（§9.5 停止条件）。

## 自测口径（回执必填）

- 定向新用例 + 全仓 SQLite 复跑（base `6fb42c4` 既有失败集为对照口径）+ ruff + `git diff --check`；merge-tree 预核与 main 零冲突面。
- 真实渲染/模型探针的命令/退出码/bytes/帧数，或 NOT_RUN 的真实原因（依赖/带宽/预算），逐项落回执。
- 回执 `receipts/TASK-12S-B/attempt-1.md`：commit sha、文件集、逐 AC 证据、探针命令/退出码、NOT_RUN 项、越界申报。

## 后续（协调者面）

机械核验 → 串行 OCR（尺寸预检拆批；`ocr.lock` 当前被 16C 链 pid 1682826 持，c05-c07 收口后排）→ TESTER 12S-B 独立验证 → 合入 main → 12S-B DONE → 重算 12S-C 依赖（仍需 16B 接受 + 12S-A 合入）。