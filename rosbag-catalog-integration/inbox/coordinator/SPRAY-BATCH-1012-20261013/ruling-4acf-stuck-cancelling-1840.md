# 裁决：大包 16_02_03（scene-4acf689f）SCENE_CANCELLING 滞留定性（协调者，2026-10-14 18:40 +08:00）

## 事实链（全部有证据来源，本轮只读核实）

- 15:57:45 处理机 kernel OOM-kill 旧 scene proxy（C obs77 16:06 实测申报）；容器 15:57:52 systemd 拉新代次 ddcc7df81635。
- 16:22:22 新代次容器日志 `cancellation observed (status=SCENE_CANCELLING)`；run 行 16:21:55 heartbeat 停、lease_expires_at=16:23:55 起 stale。
- 17:14:25 容器日志 `attempt 1 CANCELLED: 停写信号(cancel)后编排退出：[INFER] CANCELLED: decoder 阶段收到取消信号`，同刻 `cancel confirm failed … HTTP 409 {"detail":"task lease expired"}` ×2（C obs78 17:35 实测、TESTER 18:00-18:09 独立复得原文，三方一致）。
- 18:34 协调者本轮只读实测（ssh processing-machine curl 127.0.0.1:8180）：run 仍 **SCENE_CANCELLING** attempt1、INFER 仍标 RUNNING、PUBLISH 等 5 步 QUEUED、8767 `active_runs=[]`、`.staging/scene-4acf689f…/attempt-1` 空壳、`slices/test/spray/` 无 4acf689f 切片发布。**滞留 16:22 起约 2 小时 10 分钟，无收敛方。**

## 定性

- **取消已实际发生**（编排退出、INFER 中断、零 PUBLISH 产物、无第 8 run、零重烧模型）；DB run 行滞留 SCENE_CANCELLING 是**确认写被过期租约守卫（`app/domain/security.py:39` 409 task lease expired）挡回后的状态收口缺口**，非业务未取消。
- 代码面核实（3c9c496）：`cancel_scene_run` 对 SCENE_CANCELLING 状态 409；无 reap/对账端点把过期租约的 CANCELLING run 推到 CANCELLED；`scene_host_proxy._try_finalization` 遇 SCENE_CANCELLING 主动 FinalizationBlocked 不接手；新代次 `active_runs=[]` 不再认领。→ **该 run 行将永久滞留 SCENE_CANCELLING，属受控对账缺口，登记为缺陷候选入 16R 盘点（不新开任务、不代修、不直写生产 DB）**。
- 批次面处置（解除批次 RUNNING 收口阻塞）：16_02_03 验收面按取消链证据收口——TESTER 18:13 独立核实的取消链三要素（取消观察/编排退出/确认失败原文）+ 零产物（.staging 空壳、slices 无该 run 切片、8767 空 active）+ SHA=源 PASS（23:0x 既有）已齐，**本批 8 包全部独立验收面闭合**（7 包终态 PASS + 大包取消链 PASS）；DB run 行滞留不阻挡批次 TEST_REPORT_PENDING 收口，报告按「取消已证实、终态登记待缺陷修复后补对账」如实写。
- 生产写边界：协调者/TESTER/C 均**不直改生产 DB、不重启服务、不重提 run**；若用户后续要求清滞留行，走隔离树最小修复（reap 对账）+ 正式门禁（开发/测试/OCR），属 16R/新授权面，本裁决不预授。

## 各角色动作

- TESTER：按本口径出 TEST_REPORT_PENDING（大包节=取消链证据+产物完整性+滞留登记），全批收口。
- A：本批上传提交面已全闭环（10:23 三 flat 绑定恢复），转 IDLE；滞留行面 A 不处置。
- C：obs 面把 4acf689f 从「下轮核收敛」改为「滞留已定性，仅监控 run 行是否被外部变更」，不再逐轮重复申报。
- 协调者：BATCH-STATUS 16_02_03 行与批次任务行更新；缺陷候选入 16R 盘点待办；白天 20min 报告向用户说明（含是否需要用户决定是否修 reap）。

## 证据索引

- 容器日志原文：C obs78 事件 + TESTER 回执 18:13 段（test-receipts/TASK-11S-BATCH-1012/attempt-1.md）+ A 18:04 只读事件，三方独立一致。
- 18:34 协调者实测：8180 GET run 行（本裁决落盘前执行，输出在案）。
- 代码面：3c9c496 `app/services/scene_slice_service.py:565-601`（CANCELLING 态 cancel 409）、`app/domain/security.py:39`（lease 守卫）、`scripts/scene_host_proxy.py:1048`（finalization 不接手 CANCELLING）、`transitions.py:97`（CANCELLING→CANCELLED/SCENE_FAILED 仅由持有效租约方写）。