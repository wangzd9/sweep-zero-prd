# TASK-04B 强模型审查请求（attempt-2）

> 协调者生成，供强模型定向审查。所有证据均为真实命令输出/代码，未执行项已标注。
> 生成时间 2026-10-09，集成基线 main=eaf632a（GitLab origin 已同步）。

## 1. 任务卡摘要

- 任务 ID：TASK-04B ｜ 状态：✅ DONE（已合入）｜ owner：2号会话
- 交付行为：坡道结构化适配、header→bag 整数纳秒时间映射、切包 writer、证据引用
- 验收范围：REQ-03、09、13 / AC-03、09、13
- 依赖：TASK-04A（scene-capability/v1，已 DONE）
- 当前进度：合入 eaf632a，聚合验证 PASS（见 §4）

## 2. 代码变更摘要

- Base：8e97ef1（含 02/03A/04A/接线）→ Output：eaf632a（合入 commit），交付 commit 40bc262 + 9582b88
- 变更文件（13，+2166/-26）：
  - app/scene/slope/{__init__,adapter,bag_io,cache,cdr,segment,time_map,vlm,writer}.py（全部新增）
  - config/scene_capabilities.yaml（slope enabled=false→true）
  - tests/scene_fixture.py（新增）、tests/test_slope_adapter.py（新增 609 行）、tests/test_scene_capability_contract.py（适配 slope enabled）
- 高风险代码（时间映射 / 封装头检测，真实样本锚定核心）见下方 diff（cdr.py 关键段，已截断至 <500 行）

```diff
+# ROS2 封装头常量（小端 CDR_LE）：endianness=0x00, encapsulation=0x01, reserved=0x0000
+ENCAP_LE = b"\x00\x01\x00\x00"
+_MAX_VALID_SEC = 10**10   # 约 2287 年

+def _encap_candidates(data: bytes) -> list[tuple[str, int]]:
+    """先试 ROS2 封装头，再试裸 CDR。消息字段从 offset 4 开始（非 0）。"""
+    cands = []
+    if len(data) >= 4:
+        endian, cap = data[0], data[1]
+        if ((endian == 0 and cap == 1) or (endian == 1 and cap == 2)) and data[2:4] == b"\x00\x00":
+            cands.append(("<" if endian == 0 else ">", 4))
+    cands.append(("<", 0))  # 裸 CDR 小端回退
+    return cands

+def _valid_stamp(stamp: TimeMsg) -> bool:
+    return 0 <= stamp.nanosec < 1_000_000_000 and 0 <= stamp.sec < _MAX_VALID_SEC
```

- attempt-2 修复（40bc262，CDR pos 偏移契约，2 medium）：

```diff
-    header, order, p = _decode_header(data[pos:])
-    fmt, p = _read_string(data, p, order)
+    sub = data[pos:]
+    header, order, p = _decode_header(sub)
+    fmt, p = _read_string(sub, p, order)
-    return CompressedImageMsg(..., data=data[p : p + length]), pos + p + length
+    return CompressedImageMsg(..., data=sub[p : p + length]), pos + p + length
```
  （decode_image 同型修复；新增 7 字节前缀回归 test_pos_nonzero_offset_contract）

## 3. 设计与契约对照

- 设计章节：DESIGN §1（异常收敛为 FAILED 不当 NO_MATCH）、§2/§4（时间映射/封装头）、§5（整数纳秒分段）
- 契约项 / 实现位置 / 验证方式：
  - CDR 编解码（rosbag2 4 字节封装头 + Image 类型）→ app/scene/slope/cdr.py → 真实 A100 采集 golden 锚定（test_decode_real_a100_golden_header）
  - header 时间优先、存储轴回退 → time_map.py → test_header_preferred / test_storage_fallback_marked
  - slope/flat 整数纳秒分段、overlap<segment_len → segment.py + registry 跨字段约束 → test_slope_flat_split_integer_ns + test_overlap_lt_len_enforced
  - 抽帧失败≠空命中 → dispatch 收敛 FAILED → test_empty_frames_raises_not_no_match
  - 不依赖 ROS2 运行时（自足 CDR）→ cdr.py 模块 docstring 明示

## 4. 测试证据

- 命令 + 退出码（协调者独立复跑，main worktree，Python 3.10 venv）：
  - `pytest tests/test_slope_adapter.py tests/test_scene_capability_contract.py -q` → 58 passed（exit 0）
  - `pytest -q`（全量）→ 672 passed, 10 skipped, 3 failed（exit 非 0，见未执行说明）
  - 聚合脚本 verify_task04_agg.py → TASK-04 聚合验证 PASS（slope-v1 enabled+适配器注册+config_hash 一致+跨字段拒绝+真实 Image 封装 fixture analyze→SUCCESS/6 段）
- 关键测试用例：封装头 golden 锚定、pos>0 回归、时间回退标记、slope/flat 分段、空帧抛错、CDR wire order 与 ROS2 一致
- 手动验证：真实样本第 3 轮（用户指正"自洽 fixture 不算数"后，2号从 A100 真实采集 bag 提取 golden 字节独立锚定 decoder，发现 4 字节封装头偏移 + 真实 topic 是 Image 非 CompressedImage 两个根本 bug）
- 未执行测试及原因：全量 3 个失败为 tests/test_devflow.py 沙箱用例（worktree `.git` 文件非目录的已知环境问题，与本任务改动无关，base 8e97ef1 时同样失败）

## 5. OCR 审查结果

- 发现问题（协调者代跑 c40304f 全文件核心 OCR，因 2号原审查客户端挂死 0 产出）：3 条
  - [medium] decode_compressed_image pos 偏移契约坏 → 已修（§2）
  - [medium] decode_image 同型 → 已修
  - [low] 注释年份 2554→2287 → 已修
- 已修复：attempt-2（40bc262）全部落实，7 字节前缀回归红绿验证
- 误报：无（3 条均成立）
- 复审：40bc262 OCR 0 findings（session a934a443）；9582b88 OCR 0 findings（session 25167287）
- 待裁决：无

## 6. 风险与待决策项

- 已知风险：
  - 时间映射基于确定性 fixture（header 时间域==存储时间域）；真包 offset 与 VLM 端点需 TASK-09 真实授权样本/服务验证（DESIGN §4）
  - writer 的 storage_offset_ns 须由编排层（TASK-06B）从 manifest/逐帧证据推导，不可推导则阻塞发布
- 建议强模型重点关注：
  - CDR 封装头检测的误判边界（_encap_candidates 裸 CDR 回退是否可能与真实字段冲突）
  - _MAX_VALID_SEC 上界（10^10）对封装头误判 vs 合法解析的区分是否充分
  - pos 偏移修复后跨调用方（bag_io 抽帧→time_map）的端到端一致性