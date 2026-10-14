# 派单：t10-defect3-publish-bounds（TASK-10 复跑发现缺口 #3，06B 域最小返修）

- status: ACKED（2026-10-12 01:20 +08:00，B 领取，独立 ACK 见 t10-defect3-publish-bounds-ack.md）
- task/attempt: TASK-10 / t10-defect3-publish-bounds / r1
- 角色: 2号（06B 域 owner）
- base: `a77aa45`（= origin/main，本轮 fetch 双核一致；含 #1 `277e40f` + #2 `d4719f6`）
- 优先级: P0（TASK-10 收口链最后一处 app 侧硬阻塞）

## 一、缺陷事实（协调者已独立核验，E2E 复跑证据）

TESTER 01:03 用固化驱动 `scratch/t10_e2e_reverify.py` 复跑（被测 main `a77aa45`，真实 row19 袋、真实 VLM）：

- analyze SUCCESS 143.6s（54 帧）；`derive_storage_offset = 100381744 ns`（**非 None，缺口 #2 修复生效**）；
- writer 再切成功：`slice_bag_to_staging` 按存储域窗口 `[start+100381744, end+100381744]` 过滤（`writer.py:88-99`），staging 校验 `_validate_slice` bounds=(lo,hi) 存储域（`writer.py:114,138-142`）通过，10835 消息发布成功；
- `/results` 200 登记成功（1 子包 `T10Sb9fe892cbcbc4d6a`，含 sha/count/topics）；
- **`/complete-scene` 409 INCOMPLETE**：`scene_result_report_service.py:895` 区间身份复核 `lo, hi = int(start_ns), int(end_ns)` 直接取 per-slice 记录的 `start_ns/end_ns`（**header 采集域**，`scene_publish_service.py:274-275` 记录口径），而 db3 messages.timestamp 是**存储域**（writer 已用 `+storage_offset_ns` 平移窗口写入）→ 实际 max=`1787021479647655120` > header hi=`1787021479550464104`（超出 97.2ms ≈ offset 100.4ms − 残余抖动），**发布侧复核基准与 writer 侧基准不一致，真包必 409**（P0 发布闭环断点，与 #1/#2 同性质：确定性 fixture offset=0 时两域重合故未暴露）。
- 证据：`scratch/t10/t10-e2e.json`（4_complete STATUS_409 + 4_offset 100381744）、`scratch/t10/t10-run.log` 01:05:37-38、协调者对已发布 db3 只读核（10835 行，78 条 > hi 跨 16 topic，min=1787021465246636294 未越 lo）。

## 二、修复口径（最小面，06B 域）

1. per-slice 记录补**存储域实际边界**：`SlicePublishSpec` 增加 `actual_start_ns/actual_end_ns`（writer 已算出，`writer.py:164-165` 同源），`scene_publish_service.py` 发布落 `slice_manifest.json`（`actual_start_ns/actual_end_ns` 字符串口径，与现有字段一致）。
2. `scene_result_report_service.py::_verify_published_files` 区间身份复核改用记录中的存储域边界：`lo, hi = int(actual_start_ns), int(actual_end_ns)`；**fail-closed：记录缺 `actual_start_ns/actual_end_ns`（旧发布物）→ 409 INCOMPLETE 明示不得放行**，不得回退用 header 边界冒充。
3. 定向测试：构造 offset≠0 场景（storage 域消息整体平移，如真实 7 袋口径的 jitter 或常数 offset），断言发布→`/results`→`/complete-scene` 200 可置 AVAILABLE；另断言旧记录（无 actual 边界）409 fail-closed。fixture 仓库内自构造，不用真实袋。
4. 不得弱化 writer 校验、不得删既有断言；`derive_storage_offset` fail-closed 语义保持。

## 三、范围/越界

- 允许改：`app/services/scene_publish_service.py`、`app/services/scene_result_report_service.py`、`tests/` 定向测试。
- 禁止碰：`source_service.py`（#1 已合）、`app/scene/slope/writer.py`（writer 侧基准正确，不改）、04B/05 域。

## 四、AC

1. 定向测试全绿（含 offset≠0 complete-scene 200 + 旧记录 409 fail-closed 两断言）+ ruff 绿。
2. 回执交付 `receipts/TASK-10/t10-defect3-publish-bounds.md`（commit、diff 逐文件、测试证据）。
3. 交付后协调者机械核验→串行 OCR→合入 main→TESTER 复跑 E2E（驱动已固化 `scratch/t10_e2e_reverify.py`，VLM ≤1 袋）。

## 五、停止条件

AC 全绿交付回执即停，不扩范围；同根因两轮返修失败升级。