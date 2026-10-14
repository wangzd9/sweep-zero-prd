# 回执：TASK-12S-B attempt-1 水雾能力适配器（REVIEW_PENDING）

- **owner**：B（执行者B·前端功能开发群，cron poll `6f7471d8747c`）
- **派单**：`inbox/2号/TASK-12S-B/attempt-1-dispatch.md`（协调者 r147）｜**ACK**：`inbox/2号/TASK-12S-B/attempt-1-ack.md`
- **base**：`6fb42c4`（= origin/main，16A 已合入，`git fetch` 后 `git rev-parse` 双核一致）
- **head**：`f62a29c211ac846342dd79b2937962f8cb3c172c`（分支 `b/task-12s-b-spray-adapter`，worktree `wt-04a-t12sb`）
- **交付状态**：REVIEW_PENDING（冻结，未合入；等协调者机械核验→串行 OCR→TESTER 独立验证→合入 main）

## 文件清单（13 文件，+3136 行，全新增；原 slope/test-capability 条目零变化）

新增 `app/scene/spray/` 包：
- `__init__.py`（9）— import 即安装 `ros2-spray-v1`（对照 slope 自注册口径）
- `adapter.py`（427）— `SprayAdapter`（SceneAdapter 协议）+ `register_adapter(SPRAY_ADAPTER_KEY)`；两路线适用性/解码/选帧/渲染/模型/分段/缓存/取消/证据
- `decode.py`（279）— packet 路线（packet2pointcloud 子进程+returncode+序号映射源 ns）+ pointcloud 路线（纯 stdlib PointCloud2 CDR 解析，字段布局/intensity 校验）
- `render.py`（227）— 冻结选帧（跳过前 10/每 3 帧取 1）+ 500KiB 小图过滤记账（数量/失败/剩余）+ 最少有效门槛 + Open3D 离屏（惰性 import，缺失 fail-closed RENDER_UNAVAILABLE）
- `model.py`（272）— 双 pass（V18 thinking + SIM 参考图复核 1~4 正常/5~7 异常）+ 归一 spray/normal/unknown + 每 pass bytes/重试记账 + `HttpSprayModelClient`（有界重试，对照 request_spray）
- `segment.py`（207）— 整数 storage ns 分段（15s/0.15/3/5/前置 3s/合并 7s，对照 analysis_ros，不 round 秒）+ 参数 schema 校验
- `pcd_io.py`（181）— binary PCD 头解析 + intensity 抽取 + 测试 fixture 构造（纯 stdlib）
- `cache.py`（101）— 完整身份键（能力/规则/模型/参考图有序 hash/预处理/源指纹/帧 ns 序列/decoder+render 修订）manifest/hash 判断（禁止目录非空判完成）
- `references.py`（158）— 严格 7 文件受控清单（source_commit be23177，逐图 sha256/bytes/JPEG magic）
- `precheck.py`（163）— 部署预检（参考图/decoder 共享库/render 依赖/模型客户端，源码在但依赖缺失→明确 unavailable_reason，不宣称 enabled 可用）
- `time_map.py`（78）— 源 storage ns 映射（禁止 ms×1e6 冒充、禁止本地时间文件名回推，歧义拒绝）
- `config/scene_capabilities.yaml`（+82）— 新增 `spray-v1` descriptor（`enabled=false`、adapter_key `ros2-spray-v1`、model_profile 复用 slope VLM 面、rules_revision `spray-rules-v1`）
- `tests/test_spray_adapter.py`（952）— 54 用例

## 行为（对照 ros2_slice 契约，适配不照抄）

1. **两路线输入按 sensor profile 选择（不 AND、不默默后雷达）**：packet 优先 `/iv_packets_front_mid`（seyond/msg/SeyondScan）→ packet2pointcloud；替代 `/iv_points_front_mid_transformed`（PointCloud2）。缺 topic = **NOT_APPLICABLE**；存在但解不出有效帧/选帧后无 PCD/渲染无有效图 = **FAILED**（returncode/实际 PCD/有效渲染图/有效判断数逐项区分，禁止照搬原 `result == '是'` 导致全 NO_MATCH）。
2. **本机预处理冻结**（保持原调用行为与参数，不降阈值）：PCD 有序序列跳过前 10 帧每 3 帧取 1；渲染 3840×2160 旋转 90°、ROI x=(-2,6)/y=(-3,3)、intensity 配色、JPG q95；参考图过滤阈值 500KiB（过滤数量/失败/剩余数记录）；过滤后无足够有效数据 = FAILED（不把图片小当无水雾）。
3. **模型判定归一**：复用 `SPRAY_SYSTEM`+`SPRAY_PROMPT_V18`+`SPRAY_PROMPT_SIM` 双 pass；pass1 明确异常直接判异常，否则 pass2 参考图编号复核；归一 spray/normal/unknown；有界重试后仍不确定 = **FAILED**（禁止 `!=异常` 统称正常）；每 pass 记录目标图/7 参考图重复传输 bytes 与重试次数。
4. **时间轴与分段**：全程**源 DB3 存储时间整数纳秒**（不从本地时间文件名/毫秒 round 回推，不把 ms×1e6 冒充源 ns）；沿用 analysis_ros2 实际参数 15s/0.15/enter3/exit5/前置3s/重叠>=7s合并，整数 ns 保留相同语义（对照实现末尾 `int(round(...))` 丢精度，本实现禁止）；短包裁剪窗口不补帧、抽帧不足 FAILED。
5. **缓存/证据**：run/attempt 私有 work 目录 + 完整 manifest/hash 判断缓存（禁止目录非空判完成、禁止 PCD/图/cache 写原包，NAS 原包不可变）；证据含模型名/修订、提示词 hash、7 图有序 hash、decoder/render 修订、预处理参数、源指纹与帧摘要；改变参考图/规则不复用旧判断；取消不继续写。
6. **参考图受控**：严格 7 文件清单（1~4 正常/5~7 异常），逐图 sha256/bytes/尺寸/顺序校验，缺失 = REFERENCE_MISSING，不虚造替代图。

## 验证（命令 / 退出码 / 环境 / 关键断言）

环境：`/home/wang/.local/state/rosbag-scene/wt-04a-t12sb`（base `6fb42c4`，.venv 软链主仓 python 3.10）；开发机缺 numpy/open3d/rosbags/PIL/decoder 共享库（libseyond*/librclcpp/libpcl），sqlite3(stdlib) 可读 bag。

1. **spray 新用例全绿**：`PYTHONPATH=$PWD .venv/bin/python -m pytest tests/test_spray_adapter.py -q` → **54 passed**（exit 0）。覆盖派单 §9：合成已知命中/正常、字符串冲突归一（正常/异常/未知:xx 三分离，禁止 == 是）、未知/空模型/空图 FAILED、缺 topic NOT_APPLICABLE（packet/pointcloud 显式路线+缺前雷达）、缺图 REFERENCE_MISSING/REF 字节数不符 MISMATCH、非零 converter 返回 DECODER_FAILED、序号歧义（PCD 数≠源消息数）DECODE_FAILED、PointCloud 字段布局/缺 intensity P2_NO_INTENSITY、短包（<10 帧选帧后无 PCD）FAILED、乱序/多 DB3 解码层升序合并、源不变（原包 hash 前后一致）、取消（CANCELLED 停止写）、缓存版本（参考图/规则变更 key 失效、命中不再调模型、损坏文件不复用）、整 end-to-end（decode→选帧→render→model→segment SUCCESS+可发布 spray 区间，整数 ns，mapping_basis=bag_storage_ns）。
2. **场景域零回归**：`pytest tests/test_scene_capability_contract.py tests/test_scene_config_resolution.py tests/test_slope_adapter.py tests/test_spray_adapter.py -q` → **142 passed**（slope/test-capability 全绿）。
3. **全仓 SQLite 复跑**：`PYTHONPATH=$PWD .venv/bin/python -m pytest tests/ -q -p no:cacheprovider` → **937 passed, 4 failed, 10 skipped**。4 失败 = `test_devflow.py::test_external_sandbox_hides_home_and_only_binds_task_dirs` / `test_worker_resolves_codex_without_interactive_path` / `test_external_sandbox_binds_main_repo_git_for_worktree` + `test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`——**base `6fb42c4` 洁净 worktree 实测同 4 项失败（既有失败集=对照口径），本分支零新增失败**。
4. **ruff**：`.venv/bin/ruff check app/scene/spray/ tests/test_spray_adapter.py` → **All checks passed**（line-length 120，E/F/I/UP）。
5. **git diff --check**：exit 0（无空白错误）。
6. **merge-tree 预核**：`git merge-tree --write-tree --name-only HEAD origin/main` → **exit 0，无冲突路径**（零冲突面；全部新增文件，不改 slope/test 既有行为）。
7. **注册/描述**：import `app.scene.spray` 后 registry 含 `spray/spray-v1`（`enabled=false`、adapter_key `ros2-spray-v1`），slope `enabled=true`/test-capability 不变，已安装适配器含 `ros2-spray-v1`，defaults 15/0.15/3/5/3/7.0 冻结参数正确。

## 真实探针（NOT_RUN，派单 §9 有界口径）

- **真实解码/渲染**：`/home/wang/work/ros2_slice/utils/packet2pointcloud` `ldd` 实测 `libseyond*/librclcpp/libpcl` 全部 not found（型号/依赖只在处理机安装）；开发机 venv+系统 python 均无 numpy/open3d → 真实 PCD 解码 + Open3D 离屏渲染 **NOT_RUN**（`render_pcd_to_jpg` fail-closed 抛 RENDER_UNAVAILABLE，不 mock 当 PASS）。
- **真实 VLM 多图调用**：模型端点依赖服务端 `SPRAY_VLM_ENDPOINT`（未配置）+ 带宽预记账（基线 7 图 Base64≈20.25MB/pass，双 pass 可 ≥40.5MB/帧）→ **NOT_RUN**（`_default_model_client` 未配置返回 None→MODEL_UNAVAILABLE，不扩付费）。
- **真实 bag 适用性探针（只读，已执行）**：`/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`（57MB/4.38s，sqlite3 只读）实测含 `/iv_packets_front_mid`（n=1184）→ **packet 路线适用（NOT_APPLICABLE 判定正确）**；解码需处理机（NOT_RUN），未复制/未写/未迁 A100，1012 目录只读。

## 未执行项（交接/他域，本单不扩）

- **运行时 dispatch 接线**（import `app.scene.spray` 使 spray 在 16B 代理生效）属 **12S-C / 16B 域**（`scripts/`），本单只交付能力包+注册+descriptor，不改 `scripts/`；`enabled=false` 起步，处理机实测预检通过后由 12S-C/12S-D 口径开启。
- **真实模型请求 / 写测试 NAS**：12S-C/12S-D 派单口径（§9.5 自测面已授权真实模型调用，但需端点配置+带宽预算，本机 NOT_RUN）。
- 若 spray 需要新 config/env 字段（如 `SPRAY_VLM_ENDPOINT`/`SPRAY_REFERENCE_DIR` 的集中供应）：已用 env 惰性读取实现，**不写 `scene_config.py` DTO / source_metadata**（12S-A 在途），书面留待协调者集中供应。

## 越界申报

无越界。未触碰：`scripts/`（16B）、`app/web/`+`app/templates/`+`bag_search_service.py`+`scene_result_query.py`+`app/api/sources.py`（16C 冻结）、`ros2_slice` 代码（只读复用契约/参考图）、slope 既有模块、16A 双根语义、`app/models.py`/`alembic/`（零迁移/零 DDL）；1012 目录只读；`wt-04a-t16c` 冻结不动（16C 暂停证据面）。

## 下一步

等协调者机械核验 → 串行 OCR（尺寸预检拆批；`ocr.lock` 当前被 16C 链持有，c05-c07 收口后排）→ TESTER 12S-B 独立验证 → 合入 main → 12S-B DONE → 重算 12S-C 依赖（仍需 16B 接受 + 12S-A 合入）。冻结不占开发槽。