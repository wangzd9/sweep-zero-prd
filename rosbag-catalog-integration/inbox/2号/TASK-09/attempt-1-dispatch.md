# 派单：TASK-09 attempt-1 坡道真实能力与内容核验（用户授权真实样本）

- status: DISPATCHED
- 派单时间：2026-10-11 19:55 +08:00
- 任务：TASK-09（REQ-03、09 / AC-03、09），前置依赖 TASK-04B 已 DONE
- owner：2号（B，04B 适配器/writer 原 owner，wt-04a）
- base：main `0a8ca8a`（= origin/main，TASK-08 已 DONE 收口，无在途漂移）
- 授权来源：**用户 2026-10-11 19:5x 群内明确授权真实样本测试**（"授权真实样本测试，参考 slice 中的 csv 文件"）；真实样本=ros2_slice 产出已落 NAS 的坡道切片。VLM 服务=用户授权范围（协调者前置探明端点，见下）。
- 范围性质：本单是**真实能力核验与必要生产接线**，不是新建任务/扩需求；TODO TASK-09 既有 AC 为准，不新增功能。

## 一、协调者前置探明的事实（本单开发可直接引用，不必重探；证据脚本在 `~/.hermes/cache/scratch/vlm_probe*.py`）

1. **真实坡道样本已落 NAS**（用户授权参考的 CSV = `/home/wang/work/ros2_slice/slice_message.csv`，112 行 8 场景）：
   - **slope 7 行全部在位**（vehicle_id `1165414093`，vin `XL18SZXAR25120002`，beicai）：`/mnt/nas_backup/data_slice/1165414093/slope/<file_name>/`，每目录 1 个 `*_0.db3`（~239MB/15s，11279 消息，22 topic）+ metadata.yaml + 5 个相机 mp4。
   - 首帧实测（行 19：`1165414093_slope_20260818_105105_105120`）：`/bev/cam_front_8m_jpg` CompressedImage（format=jpeg，289700 字节，magic ffd8），**db3 存储时间 min=`1787021465017764635`** vs **CSV 声明 start=`1787021465`（10 位秒）**——时间映射核验锚点已给出；`/bev/cam_front_jpg` 等其他前相机 topic 同型。
   - **flat 16 行**（同 vehicle_id，阴性对照）：`/mnt/nas_backup/data_slice/1165414093/flat/1165414093_flat_20260818_105143_105201` 等（抽样确认 1 条在位即可，全部以 CSV 为准）。
   - 源原包（整袋）不在 `original_ros2bag` 下（无 1165414093 命中）——**本单直接以 data_slice 切片 db3 为"真实源 bag"跑 04B 适配器链（db3→抽帧→VLM→segment→writer 再切），不做原包重切**。
2. **VLM 端点可达且视觉能力实测有效**：`http://192.168.2.45:8002`（= 本机 18002 SSH 隧道同一实例，a100-wzd），模型 ID **必须用完整路径** `/home/sysadmin/data/disk02/jc/models/qwen3.8-27b-fp8`（`vlm.py` 里硬编码 `"model": "qwen-vl"` 会 404——接线必改，见二.1）。
3. **Qwen3 思考模式陷阱（本单最大坑，协调者实测确认）**：
   - `max_tokens=256`（vlm.py 现值）下图像请求 `finish_reason=length` + `content=None`（思考 token 吃光预算）→ **生产链会把所有帧判模型不可用/空返回**；
   - `max_tokens=2048` 正常（真实坡道帧 content=`'坡道'`，125 completion）；`chat_template_kwargs={"enable_thinking": False}` 时 512 足够（3 token 直答）；
   - 纯文本请求不受影响（58 prompt 正常作答）——**文本绿不能证明视觉可用，必须以图像请求+足量预算验证**；
   - 模型对 `<image>` 文本 token 自述"看不到图像"（视觉只认 OpenAI image_url 形态，v1 payload 形态正确）。

## 二、交付内容（最小范围，零新需求）

### 2.1 生产接线（app 行为面，必要修复）
- `app/scene/slope/vlm.py`：
  - `HttpSlopeModelClient` 的 `model` 字段：默认改为可配置（env `SLOPE_VLM_MODEL`，默认值=完整路径模型 ID；保留旧值能力但不得默认 404）；
  - `max_tokens` 默认 256→**≥2048**（或 `enable_thinking=False` 二选一，以实测稳定优先；若走关思考，payload 加 `chat_template_kwargs` 透传）——**必须有单测/探针实证图像请求 content 非空**，否则按缺陷处理；
- `app/scene/slope/adapter.py::_default_model_client`：`SLOPE_VLM_ENDPOINT` 缺省策略维持 fail-closed（未配置=MODEL_UNAVAILABLE，不变），仅确认 env 名与接线一致。
- 接线只允许动 `vlm.py`/`adapter.py` 客户端构造路径，**不改抽帧/segment/时间映射语义**。

### 2.2 真实能力核验（TASK-09 核心输出）
用主仓真实服务链（04B `SlopeAdapter.analyze` 或等价最小编排：read_topics→抽帧→VLM→segment_slope_ns→writer）跑：
1. **阳性 slope 2-3 条**（CSV 行 19/20/31 优先）：断言 `SUCCESS`（非 NO_MATCH 非 NOT_APPLICABLE 非 FAILED），可发布区间非空、区间落在源袋时间范围内、每段 ≥1 帧证据；
2. **阴性 flat 1-2 条**：断言 `NO_MATCH`（或 flat-only 证据、无发布区间）——**不得把 flat 判成 slope 发布**；
3. **边界/故障**：至少 1 例 VLM 不可达/空返回 → 断言 `FAILED`/`MODEL_UNAVAILABLE` 如实报出，**不伪装 NO_MATCH**（AC-03"错误不伪装为无命中"）；
4. **时间映射证据**：抽帧 header.stamp（采集时间）vs db3 存储时间差值逐帧恒定核验（`MAPPING_HEADER_STAMP` 路径）；CSV 声明秒 vs 实测首帧存储纳秒的偏差如实报告（锚点见一.1）。
输出=样本/模型/规则摘要 + 限制说明（帧率、抽帧间隔、判定阈值、未覆盖场景），落 `reports/TASK-09/`。

### 2.3 回归
- 接线改动后 `tests/test_scene_*`（slope 适配器/segment/time_map/vlm 相关）SQLite 定向全绿；VLM 相关测试注入确定性客户端（不真实调用）；
- ruff 绿；若动 app 行为面，真 MySQL 隔离库跑 06B 核心 35 用例不破坏（复用 TESTER 插件口径）。

## 三、AC 核对（验收口径）
- 至少实际坡道切片样例可核对 ✓（2.2.1）
- 错误不伪装为无命中 ✓（2.2.3）
- 能力/内容/时间分别有证据 ✓（2.2.1-4）
- 不扩成标注工程、不宣称生产就绪（质量门禁仍 TASK-11）✓（报告只写实测与限制）

## 四、边界与禁止
- 不写 NAS 业务目录（`/mnt/nas_backup/data_slice` 只读）；产物/缓存只进 run 私有 work_dir 或 `/home/wang/.hermes/cache/scratch/`，用完清理；
- 不动 192.168.2.45 服务本身（不重启/不改配置）；VLM 调用量控制在抽帧口径（15s 袋 ~15 帧/样本，≤6 样本 ≈100 次调用）；
- 不引入新场景（只 slope）；其他四类场景属 TASK-12 范围，不碰；
- 交付 commit 在 `wt-04a` 或新分支，单 commit 或最小 commit 集，回执 `receipts/TASK-09/attempt-1.md`（REVIEW_PENDING）。

## 五、下游
交付后：协调者机械核验（含 2.1 接线的图像 content 非空证据）→ 串行 OCR（app 面）→ 合入 → TASK-09 DONE → **TASK-10 候选重算**（08 DONE + 09 DONE 即派 TASK-10 真实工程闭环：目录→切片→NAS+数据库→API 获取）。