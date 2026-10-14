# 测试回执：TASK-10 E2E 复跑（两笔返修合入后独立验收）

- 角色：测试者（TESTER）
- task/attempt：TASK-10 / e2e-reverify-after-merges / attempt-1
- status: **FAIL**（核心修复面 PASS，但 AC-2 端到端全链 SUCCESS 未达成 + AC-4 步骤 5 未执行）
- 交付时间：2026-10-12T01:1x +08:00

## 被测快照（独立双核）
- 驱动 WT `/home/wang/work/rosbag-catalog`（main 分支）HEAD=`a77aa45433`，`git fetch origin main` 后 `origin/main`=`a77aa45433`，**双核一致**。
- `git merge-base --is-ancestor 277e40f HEAD`=yes（defect1 source READY 修复在位）；`git merge-base --is-ancestor d4719f6 HEAD`=yes（defect2 storage offset 修复在位）。
- 旧 worktree `wt-04a-t10`@ca8730d 不含修复，**未使用**（与派单口径一致）。
- 容器镜像 2026-10-08 build 早于 main `a77aa45`（不含 scene 路由）→ 沿用 attempt-1 既有口径：驱动在 `a77aa45` 代码上起独立 app 实例（fresh SQLite `scratch/t10/t10-e2e.db` + create_all + 正式 TestClient API），非旧镜像冒充；执行面由驱动直接走真实 VLM 链。此环境事实已记 ACK。

## 实际命令与执行
- 命令：`/home/wang/work/rosbag-catalog/.venv/bin/python /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10_e2e_reverify.py`
- 后台 pid 3156631（01:03:08 起跑 → 01:05:38 退出，**rc=1**，NameError 崩溃于 step 5 首行，非测试逻辑失败）
- 日志：`scratch/t10/t10-run.log` + `t10-reverify-driver.out`；证据：`scratch/t10/t10-e2e.json`（steps/verdicts 全落盘）
- VLM 真实调用：`http://192.168.2.45:8002/v1/chat/completions`（完整路径口径），row19 54 帧，analyze latency 143.6s，**SUCCESS**

## AC 逐项取证
1. **步骤 4 发布不再 PUBLISH_BLOCKED：PASS**——`derive_storage_offset` 返回 **100381744 ns（≈100.382ms 非 None）**，与 AC 预期值精确一致；`publish_scene_slices` 原子发布 1 切片成功（产物 `scratch/t10/publish/unassigned/slope/13551AA0FD504BF28BC282DD7E_T10Sb9fe892cbcbc4d6a`）；`/results` **200**（registered_segments=1, derived_children=1, availability=PENDING）→ **defect2 修复在 E2E 真链上生效**。
   - 但 `/complete-scene` **409**：`INCOMPLETE: 切片 slope:1787021465142223739:1787021479550464104 消息超出区间上界 1787021479647655120 > 1787021479550464104`（超界 97.2ms）。代码面：校验来自 `app/services/scene_result_report_service.py:899`（complete-scene 完整性核对复用 `app/scene/slope/writer.py:142` 界），**该两文件在 a77aa45 未被 defect1/defect2 改动**（defect1 只动 source_service，defect2 只动 scene_publish_service）→ **新暴露的真实缺口 #3**：analyze 段的 slice_key 区间端点（header_stamp_ns 基准）与写入/校验窗口的存储轴端点存在时间基准漂移，complete-scene 完整性门禁拦截了本应收尾的 run（run 停在 availability=PENDING 非 AVAILABLE）。
2. **端到端全链 SUCCESS：FAIL**——登记 matched（1b OK）/ run 冻结（config_hash `0845b402…`）/ analyze SUCCESS（143.6s/54 帧，真实 VLM）/ 可发布区间非空 均过；**断链在 complete-scene 409**，全链未收口。
3. **原包独立复核 ALL_UNCHANGED：PASS**——驱动内置 before/after 校验因 NameError 未跑到；TESTER 独立补核 `scratch/t10_src_after_check.py`（after 独立重算 sha256 head1MB+size+mtime 对照证据内 before 值）：**7 文件全部 match，ALL_UNCHANGED rc=0**。
4. **步骤 5 API 获取：NOT_RUN**——驱动 `t10_e2e_reverify.py:385` **`NameError: name 'child' is not defined`**（日志行内变量应为 `child_uid`，`child_map` 非空走 step5 分支时崩溃）→ bags/{child}/lineage/切片可打开**未取证**。属 **harness 驱动脚本缺陷**（协调者固化版 00:58 落盘），非 app 行为。
5. **每步证据：PASS**——`t10-e2e.json` steps/verdicts 全落盘，409 与 NameError 均如实申报（未弱化断言、未跳过 VLM、未 mock）。

## 定位（按派单 §三分类）
- **#3 complete-scene 409（app 行为面，TASK-10 新缺口）**：切片端点时间基准漂移 → 06B/04B 域待协调者裁决归属（scene_result_report_service 完整性校验 vs writer 界 vs analyze 端点语义）；**非 defect1/defect2 修复引入**（两文件本轮零改动，独立核）。
- **step5 NameError（harness env 域）**：驱动脚本 `:385` 变量名错误，修复后重跑可完成 API 获取取证。
- AC-1 核心（offset 非 None+发布成功）已证明 defect2 修复生效；defect1（source READY）在本轮由 harness 前置显式置位（`1c2`：app 仍无生产 setter，finding #1 口径不变——但注意 main `277e40f` 已含 DISCOVERED→READY 生产路径，本驱动未验证该生产路径实际落位，如实申报为**未覆盖项**）。

## 未执行项
- 步骤 5（bags/{child}/lineage/切片可打开）：NameError 阻断，待驱动修复后补。
- defect1 生产路径（03B DISCOVERED→READY 无 harness 前置）实际落位验证：本轮驱动沿用 attempt-1 前置口径未覆盖。

## 清理
- 驱动进程已退出（ps rc=1 核实）；本轮无 TESTER 自建容器（SQLite 文件级）；`scratch/t10`（221M，含证据+work+publish 产物）与 `t10-nasroot`（229M 本地袋副本）为本角色/驱动创建的隔离资源，**保留作 #3 与 step5 修复后复跑的最小复现现场**（含 fresh DB+run 状态），不回清。
- 零业务代码改动（TESTER 边界）。

## 结论
**FAIL**——两笔返修的修复面本身在真链上生效（offset 非 None+发布成功+原包不变+真实 VLM analyze SUCCESS），但端到端全链在 **complete-scene 409（新缺口 #3，app 行为面）** 断链，且步骤 5 取证被 **驱动 NameError（harness 面）** 阻断。需协调者裁决：#3 回派执行者定位修复 + 驱动 step5 修复后按新 attempt 复跑收口。**不满足 TASK-10 DONE 判定条件**（全链 SUCCESS 未达成）。