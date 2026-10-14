# 派单：TASK-12S-B attempt-1-rework（12S-B c01+c02 全链 OCR 16 findings 一次最小返修）

- status: DISPATCHED
- 派单时间：2026-10-13 14:2x +08:00（协调者 r158，c02 收口 14:16:32 rc=0 后合并派单）
- 任务：TASK-12S-B attempt-1 交付 `f62a29c` 的 OCR 全链收口返修（c01 核心算法面 5 文件 8 findings + c02 辅助配置面 7 文件 8 findings=16 findings，协调者逐条只读代码核 16/16 CONFIRMED，误报 0）
- owner：B（2号）｜attempt：attempt-1-rework（base `f62a29c` 续 commit，不新开分支/attempt 号）
- base：`f62a29c`（wt-04a-t12sb，12S-B attempt-1 交付冻结 head）
- 收口链：本单交付冻结 → 协调者机械核验 → 返修增量 OCR（**固定入口** `ocr_runtime.py prepare→start→status`，`--from f62a29c --to <新head>` 或按 diff 面拆批）→ TESTER 12S-A/B 独立验证（B 侧快照更新为新 head，A 侧 `77c395b` 不变，另发通知）→ 合入 main → 12S-B DONE → 重算 12S-C 依赖

## 一、返修项（16 条，按文件；CORRECTION 级必改，LOW 级最小改或回执书面说明取舍理由，不扩需求）

### app/scene/spray/adapter.py（S1/S2/S5/S8）
- **S1 [HIGH·CORRECTION] :186-188** 模型循环+`cache.hit(expected_frame_count)`+`model_storage_ns` 推导+`SPRAY_RENDER_LOG` 计数必须改用 `report.valid_frames`（`render.py account_frame` 对 <500KiB 的 JPG 已 unlink，`rendered_frames` 仍含已删帧 → `jpg.read_bytes()` 抛 FileNotFoundError 整 run ADAPTER_ERROR；且小图会喂入模型违背设计、时间轴与缓存帧数错位）。
- **S2 [MED·CORRECTION] :115-116** work_dir 相对路径守卫只在"已存在"时触发：新相对路径穿透守卫后 `mkdir(parents=True)` 落到进程 CWD。守卫改为 `if not work_dir.is_absolute():` 直接拒绝。
- **S5 [LOW] :338-340** `pcd_path is None` 死分支（两路线恒填 pcd_path）：删 else 或注释不变式。
- **S8 [LOW] :97-98** route=auto 且 packet/pointcloud 双缺 topic 时误报 `未知路线 'auto'`：auto 解析失败归入缺 topic 的 NOT_APPLICABLE 口径。

### app/scene/spray/decode.py（S3/S6）
- **S3 [HIGH·CORRECTION] :90-92** `parse_pointcloud2` 固定尺寸 `struct.unpack_from`（sec/nanosec/str_len/height/width/nfields/fname_len/f_off/point_step/row_step/data_len）与裸 `data[pos]` 读均无越界守卫 → 截断/畸形 PointCloud2 抛 `struct.error`/`IndexError` 而非 `DecodeError("P2_TRUNCATED")`，且 `decode_pointcloud_route` 循环无 try/except、adapter `_decode` 只捕 DecodeError → 契约"存在但解不出有效帧=DECODE_FAILED"被破坏。参照 slope `cdr.py _read_struct` 口径加守卫，全部失败收敛 DecodeError。
- **S6 [LOW] :267-268** pointcloud 路线解码循环无 `cancel_check`：透传与 packet 路线对齐（或回执说明取舍）。

### app/scene/spray/render.py（S4/S7）
- **S4 [HIGH·CORRECTION] :168-169** intensity 上色恒不生效：`read_intensity` 返回全点序列（len=n），与 `len(cropped)`（ROI mask 子集）比较几乎恒 False → `cloud.colors` 从不设置，强度判别失效。先对 intensity 数组应用同一 ROI mask 再上色。
- **S7 [LOW·perf] :214-217** 渲染热路径纯 Python 逐点循环：向量化（`np.select`/分箱 mask）。

### app/scene/spray/precheck.py（T1/T2/T3）
- **T1 [MED·CORRECTION] :116** fail-closed 被破坏：`_ldd_missing_libs` 探针自身失败（OSError/TimeoutExpired）返回 `["ldd 失败：…"]`，不匹配任何必需库族 → `required_missing` 空 → `ok=True` 且 detail 自相矛盾（"关键共享库在位（ldd not found 1）"）。ldd 不可用时必须报 unavailable（如 reason=`DECODER_DEPS_UNKNOWN`），不宣称在位。
- **T2 [LOW] :109-110** 硬编码机器路径 `/home/wang/work/ros2_slice/utils/packet2pointcloud`：改 env（建议 `SPRAY_DECODER_PATH`）受控提供，未配置报 `DECODER_UNAVAILABLE`，对齐 `references.py` 的 `SPRAY_REFERENCE_DIR` 口径。
- **T3 [LOW] :89** reference 错误码误分类：`verify_references` 抛 `REFERENCE_UNDECODABLE`（字节/hash 对但非 JPEG）时被标成 `REFERENCE_MISMATCH`。按实际 reason 前缀传播（UNDECODABLE→MISMATCH→MISSING 优先级）。

### app/scene/spray/pcd_io.py（T5/T6/T7）
- **T5 [LOW·CORRECTION 契约] :66-71** 头解析非数值 SIZE/COUNT/WIDTH/HEIGHT/POINTS（或缺第二 token）抛未捕 `ValueError`/`IndexError`：两调用方（`decode_packet_route`、`adapter.py:321`）只捕 `PcdError`。header 解析全部失败收敛 `PcdError`。
- **T6 [LOW] :78-79** 同函数两个补充契约缺口：① COUNT 行缺失时 `counts=[]` 触发误报长度不一致（PCD 规范 COUNT 可选=全 1，按规范默认）；② 解析接受 `DATA binary_compressed` 但 `read_intensity` 只处理 binary/ascii → 压缩 PCD 过 header 检后 intensity 抽取报错误导。header 检与 intensity 能力口径对齐（compressed 在 header 层即报不支持）。
- **T7 [MED·CORRECTION] :120-123** ASCII intensity off-by-one：`data_start` 指在 DATA 行换行后，`raw[:data_start].split("\n")` 多一个尾空元素 → 多跳一行，首条 ASCII 数据被静默丢弃（n 点返 n-1 值）。按 DATA 行前实际头行数跳（`len(head_lines)-1` 或等价）。

### app/scene/spray/references.py（T4）
- **T4 [LOW] :22-24** `REF_ORDER`/`NORMAL_ORDERS`/`ABNORMAL_ORDERS`/`SOURCE_COMMIT` 死代码（全仓零引用，`adapter.py:389` 硬编码 `"be23177…"` 未 import `SOURCE_COMMIT`）：删，或让 adapter/manifest 消费 `SOURCE_COMMIT`/`REF_ORDER` 保持单一来源。

### config/scene_capabilities.yaml
- 无 findings；不改动。

### app/scene/spray/time_map.py（T8）
- **T8 [LOW·CORRECTION] :62-66** 最近候选 tie（等距双候选，如 t±25ms）时 `min` 取首个 → `hits=[nearest]` 恒 len 1，"唯一最近"歧义拒绝永不触发，违背防误配意图。tie 时必须拒绝（显式唯一性检查），或按契约口径回执说明取舍。

## 二、自测/证据
- 返修面定向用例：S1 小图删除后 run 不炸且模型只吃 valid_frames；S3 截断 PCD 收敛 `PcdError`/DecodeError（合成畸形头矩阵）；S4 上色后 `cloud.colors` 已设置且长度=mask 点数；T1 ldd 探针失败报 unavailable（mock）；T5/T6 畸形 header 矩阵（非数值/缺 COUNT/compressed）；T7 ASCII 强度首值不丢（合成 ASCII PCD 往返）；T8 tie 等距双候选被拒绝。
- 全仓回归：spray 域 + 场景域 + 全仓 pytest，口径同 attempt-1（仅 base 既有 4 失败，零新增）。
- ruff 全过。
- 真实 decode/render/VLM 仍 NOT_RUN（本机依赖缺失口径不变），1012 只读 bag 探针如适用补跑。

## 三、边界
- 只动 `app/scene/spray/*` 与 `tests/test_spray_*`（+本单涉及测试）；不改 12S-A DTO/16B scripts/16C 冻结面/旧 slope；禁新迁移；不改能力注册 enabled=false 状态。
- 不扩需求：LOW 项可最小修+书面取舍，不因返修改契约语义（`bag_storage_ns`/整数 ns/双路线选择逻辑不变）。

## 四、交付物
- 冻结 commit（续 `b/task-12s-b-spray-adapter` @ `wt-04a-t12sb`，实测分支）+ 回执 `receipts/TASK-12S-B/attempt-1-rework.md`（REVIEW_PENDING，16 条逐项：修复/取舍说明 + 自测证据表）。
- 回执需列实际 base→head、文件清单、定向/全仓测试数。

## 五、ACK 时限
- 收到后 30min 内 ACK（B 当前无在途任务，直接接）。