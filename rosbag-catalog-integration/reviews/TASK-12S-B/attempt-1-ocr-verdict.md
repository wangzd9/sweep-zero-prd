# TASK-12S-B attempt-1 OCR c01+c02 裁决 + attempt-2 返修单（修正版）

- 裁决人：协调者（逐条独立核 `f62a29c` 代码坐实，非照抄 OCR）
- OCR：c01 rc=0 **7 findings**（adapter/decode/render，23min 13:51 收口）；c02 rc=0 **8 findings**（precheck/references/pcd_io/time_map/init/yaml，14:16 收口）。两批 coverage 完整。
- 前版裁决表 c01 坐标凭记忆误写（S1-S8），本版按真实 findings F1-F7 修正。

## c01 裁决（7/7 CONFIRMED）

| ID | 级别 | 位置 | 结论（核代码坐实） | 处理 |
|---|---|---|---|---|
| F1 | high | adapter.py:186-188 | 模型循环/`cache.hit`/`SPRAY_RENDER_LOG` 计数用 `report.valid_frames` 驱动，非 `rendered_frames`：`account_frame` 对 <500KiB 已 unlink，`rendered_frames` 仍含被删帧 → 遍历 `read_bytes()` 命中已删文件=**FileNotFoundError 整 run ADAPTER_ERROR**，且小图喂模型违背"小图排除推理"设计 | **修**（B 已改） |
| F2 | medium | adapter.py:115-116 | `work_dir` 守卫仅在相对路径已存在时触发；新建相对 work_dir 通过检查后 `mkdir(parents=True)` 落到**进程 CWD 不可控位置**（PCD/JPG/render_log 全写错地方），`analyze()` 直调绕过 dispatch 的 ContractRunContextValidator | **修**：`if not work_dir.is_absolute():` |
| F3 | low | adapter.py:338-340 | 死分支：两条 decode 路线恒填 `fr.pcd_path`，`pcd_path is None` 不可达；活路径对每个选中 PCD 全量读+SHA-256 再查缓存 | 维护项（删 or 注明不变式） |
| F4 | low | decode.py:267-268 | pointcloud 解码循环无 `cancel_check`（函数签名都没有），长解码无法响应逐帧取消，与 packet 路线不对称 | 维护项（thread cancel_check） |
| F5 | high | decode.py:90-92 | `parse_pointcloud2` 仅对 3 处变长读有边界检查；所有定长 `struct.unpack_from`+裸 `data[pos]`（is_be/sec/nanosec/str_len/height/width…）**无 buffer 长度校验** → 截断 PointCloud2 抛 `struct.error`/`IndexError` 而非文档承诺的 `DecodeError("P2_TRUNCATED")`；`decode_pointcloud_route` 循环无 try/except，`_decode` 只捕 `DecodeError` → 原始异常**逃出 analyze()**，破坏 pointcloud 路线"存在但解不出=FAILED(DECODE_FAILED)"契约 | **修**（B 已加 `_p2_read`/`_p2_read_byte` 守卫，参照 slope cdr._read_struct） |
| F6 | high | render.py:168-169 | intensity 上色**静默从不生效**：`read_intensity` 返回全点 PCD 强度(len=n)，却与 `len(cropped)`=ROI mask 子集比较，条件几乎恒 False → `cloud.colors` 从不设、云渲染无色——**摧毁 intensity 水雾/正常判别**（参考图与 prompt 依赖它）；罕见相等时还传入未 mask 的完整 list | **修**：先对 intensity 数组应用同一 ROI mask 再上色（B 尚未改 render.py） |
| F7 | low | adapter.py:97-98 | `route=auto`(默认) 且 bag 两 topic 全缺 → `_resolve_route` 返回 "auto" 落入自相矛盾 reason `未知路线 'auto'（应为 packet/pointcloud/auto）`，实际是"两个必需 topic 都缺" | **修**：auto 解析失败归到 missing-topic NOT_APPLICABLE |

## c02 裁决（8/8 CONFIRMED，独立核代码坐实）

| ID | 级别 | 位置 | 结论 | 处理 |
|---|---|---|---|---|
| P1 | medium | precheck.py:110-124 | `_ldd_missing_libs` 探测失败返回 `["ldd 失败…"]` → 不匹配任何 required family → `required_missing` 空 → **ok=True 且 detail 自相矛盾**（"关键共享库在位（ldd not found 1）"）；极简容器 decoder 预检放行，违反 docstring fail-closed | **修**：探测失败=DEPS_UNKNOWN 不可用 |
| P2 | low | precheck.py:109 | 硬编码 `/home/wang/...` 机器路径（包内其他部署路径均走 env） | **修**：`SPRAY_DECODER_PATH` env，缺省不可用 |
| P3 | low | precheck.py:89 | ReferenceError 原因码分类错：非 MISSING 一律 MISMATCH，UNDECODABLE 被误报 | **修**：按前缀精确传播 |
| P4 | low | references.py:22-24 | REF_ORDER/NORMAL_ORDERS/ABNORMAL_ORDERS/SOURCE_COMMIT 死代码（adapter 硬编码 commit 字符串） | **修**：删除或单一来源化 |
| P5 | low | pcd_io.py:66-71 | header 非数值/缺第二 token → 未捕获 ValueError/IndexError（调用方只捕 PcdError） | **修**：收敛 PcdError |
| P6 | low | pcd_io.py:78-79 | 同 P5 + COUNT 缺失按 PCD spec 应默认全 1（现抛 PcdError）+ binary_compressed 过 header 后 intensity 抽取误导报错 | **修**：PcdError 收敛 + COUNT 默认 1 + compressed 明确拒绝 |
| P7 | medium | pcd_io.py:120-123 | ASCII intensity：`data_start` 含 DATA 行换行 → `split("\n")` 尾空元素 → `len(head_lines)` 多 1 → readline 跳过头+**首条数据** → 静默丢首值（n-1 值对 n 点） | **修**：按 DATA 前实际行数跳 |
| P8 | low | time_map.py:62-66 | 等距 tie 时 `min` 取首元素 → `hits=[nearest]` 恒 len1 → 下方歧义拒绝**永不触发**，违反"要求唯一最近"注释 | **修**：接受 nearest 前校验距离唯一 |

## 返修单（attempt-2 派 B）

- **f62a29c 提交保持冻结**（c01/c02 审查对象已固定收口），修复以**新 commit 叠在其上**成 attempt-2 head，不得 amend/rewrite f62a29c；B 当前未提交 diff 方向正确
- **必须覆盖全部 15 条 CONFIRMED**，当前 B 的 diff 仅 adapter/decode/references（F1/F5 已改，F2/F7 待补），**render.py F6（intensity high）尚未触碰**——这是水雾/正常判别的核心，必须修
- 范围：`app/scene/spray/*`（F1-F7 + P1-P8，维护项 F3/F4 一并）+ 回归测试；**禁改**采样策略/参考图/质量阈值/`scene_capabilities.yaml` 坡道面（16A 冻结 hash 不变）
- 增量 OCR 范围：`f62a29c..attempt-2 head`，tests 排除挂 TESTER
- 停止条件：15 处各带回归 + 全量 spray 定向测试绿 + ruff 绿 + 零越界 + f62a29c 未移动
- 特别验证（REPORT 点名）：disabled spray 窄前缀回退坡道默认风险——关闭 spray 时 `incoming/spray` 不得被错误调度为坡道；成立则加最小入口约束，原根默认与历史 hash 不漂移

## 下游
- B 返修冻结 attempt-2 head → 增量 OCR → B 合入
- C 12S-C 前置开发消费 `f62a29c` 冻结契约接口面，返修后做受影响接线核验
- TESTER 12S-A/B 并行验证在途（A=`77c395b`；B=冻结快照功能验证+返修后复验受影响项，不重复整仓全测）