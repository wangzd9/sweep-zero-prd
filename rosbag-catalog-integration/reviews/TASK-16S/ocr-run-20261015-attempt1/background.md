# TASK-16S app 面审查背景（协调者 2026-10-15 17:5x +08:00）

## 需求与交付身份
- 需求来源：用户 2026-10-15 明确要求"把最新的 ros2_slice 当独立程序调用，不修改识别、抽帧、分段等算法"；随后要求"用已验证小包复核水雾全流程"。
- 授权：用户 2026-10-15 17:2x 选「甲」——把该脚本线合回 main 基线、跑全仓测试、补 OCR 与独立测试门禁后再谈部署（原生消息 `om_x100b623df418c4a0de1c0a9bd8f67e2`，request `d7c58fe39f0fbdd5452ae38ebd98690681e5ffcf1ce2112c46759af2cc318156`）。**不含生产部署授权**。
- 冻结范围：`16a154f` → `21b191cf3754225ba6453dc26c14793ebc91510e`（合并候选分支 `coord/merge-spray-script-into-16c`，worktree `/home/wang/.local/state/rosbag-scene/wt-coord-merge-script-20261015`）。该线此前已在生产运行（`.deployed-git-revision=cad585a`）但未走本协作流程门禁。

## 关键不变量（审查须围绕）
1. **不改算法**：上游 `ros2_slice` 固定 `deb8be8515ffaa8b556e442332725e876dc2f2ca` 原样调用；平台侧不得实现识别/抽帧/分段/切包算法。秒级上游边界只做 `×10**9` 单位换算，不得宣称为纳秒级识别精度。
2. **身份五元绑定与单 run 认领**：`job.json` 的 `source_id`/`source_generation`/`source_fingerprint`/`upstream_commit` 必须与请求一致，`platform-claim.json` 以 `(源UID,代次,指纹,commit,config_hash,run_id)` 认领；同一作业不得被第二个 run 抢占，同一 run 重试可接续。
3. **作业根越界防护**：`job_id` 必须匹配 `[a-zA-Z0-9_-]{1,100}`，解析后须仍在 `SCENE_SCRIPT_JOBS_ROOT` 内；切片路径须在受控 `slices` 根内、非符号链接、单 DB3。
4. **原包/切片字节不可变**：只读 NAS 源包；接收仅复制上游已关闭切片，允许改 DB3 文件名与 metadata 路径映射，不得修改 DB3 内容。
5. **零消息 topic 证据完整**：上游 DB3 保留消息数为零的 topic 定义；发布证据须覆盖真实 DB3 的完整 topic 集合与计数（含零），不得删 topic、改 DB3 或放宽 Backend 完整性校验来掩盖。
6. **失败/取消可观察**：`FAILED`→SCRIPT_FAILED、超时→SCRIPT_TIMEOUT+写 `cancel-request.json`、取消→CANCELLED+写 `cancel-request.json`；不得永远停在 RUNNING。容器崩溃/OOM 由监控器转明确失败。
7. **默认不改变既有能力**：新增能力 `spray-script-deb8be8-call` 仓内 `enabled: false`，`spray-v1` 默认选择与行为不变。
8. **编排分流**：WRITE 步按 `adapter_key == ros2-spray-script-v1` 走 `receive_script_slice`，其余（含 spray-v1）仍走 `slice_bag_to_staging`。

## 已完成的协调者机械核验（供对照，不作为本审查结论）
- 双面逐文件 sha256：脚本线 6 文件与 `cad585a` 逐字节一致；16C 六文件与 `16a154f` 逐字节一致。
- 全仓 pytest：候选 `21b191c` = 1181 passed / 4 failed / 10 skipped；基线 `16a154f` = 1174 passed / 4 failed / 10 skipped，失败集合完全相同（`test_devflow.py`×3 环境性、`test_web.py` bounded-query 1），零候选回归。
- ruff：与基线同为 4 errors（`tests/test_task16cc_scene_detail.py` E501，16C 既有面），零新增；alembic 单头 `20261013_01_scene_intake`，零迁移改动。
- TESTER 独立行为面验证已派（`inbox/TESTER/TASK-16S/attempt-1-independent-verify-dispatch.md`）。

## 明确本期范围与非范围
- 在范围：本次合并带来的 6 个非文档文件（含测试默认排除）。
- 非范围：上游脚本算法质量、真实模型识别准确率、生产部署与处理机 overlay、自动扫描启动任意源包（未实现）、真实阴性/实车/多 DB3 边界（属原 12S-D 矩阵）。

## 待核实风险（请重点复核）
- `receive_script_slice` 的 metadata 改写与 `_validate_slice` 复用是否存在未覆盖的失败分支；
- 认领文件并发写入（`open("x")` + 事后比对）在异常/并发下的行为；
- 轮询循环的取消/超时优先级与 `status.json` 缺字段时的错误分类是否稳定；
- 编排分流在能力未注册/`_registry.get` 返回 None 时的行为。
