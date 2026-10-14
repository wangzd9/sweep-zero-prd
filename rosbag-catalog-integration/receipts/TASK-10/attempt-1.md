# 回执：TASK-10 attempt-1 目录→坡道切片→数据库→API 获取真实工程闭环（P0 收尾单）

- status: **REVIEW_PENDING**
- task/attempt：TASK-10 / attempt-1
- owner：2号（B）
- base/head：main `ca8730d`（= origin/main 双核一致）；**业务代码 0 改动，无新 commit**（取证/验证单，wt-04a-t10 仅 .venv 软链，先例=TASK-08 attempt-1 零业务改动）
- 分支/worktree：`scene/task-10-e2e` @ `wt-04a-t10`
- 交付时间：2026-10-11 23:5x +08:00（cron poll，真实 checked_at 2026-10-11T23:42:53+08:00）
- 详细报告：`reports/TASK-10/attempt-1.md`（端到端四步实测 + 2 真实产品缺口根因/证据/回派 + 原包不变独立复核 + 回归 + 环境事实）

## 交付内容摘要

1. **端到端正式服务链实测**（独立 app 实例 + 正式 TestClient API + 真实 VLM）：
   - 提交冻结 slope 配置 hash（`0845b402…` 非 NULL）→ 登记真实 row19（11279 消息/22 topic）matched → 建 SCENE_SLICE run → claim → **真实 VLM analyze SUCCESS（138.8s，54 帧）** 产出 publishable 坡道段 `slope:1787021465142223739:1787021479550464104`（≈14.4s，与 TASK-09 一致）。
2. **定位 2 个真实 P0 产品缺口**（本单目的，定位+回派不跨模块改码）：
   - **#1** 无生产路径把 `source_status` 置 `READY`（app 0 setter，正式登记真实源永远到不了 scene 链）→ 建议回派 03B 域。
   - **#2** `derive_storage_offset` fail-closed（bit 恒定）与真实 rosbag2 写入 jitter 冲突 → 全部 7 条 slope 袋 PUBLISH_BLOCKED，**发布硬阻塞** → 建议回派 06B 域（优先）。
3. **原包不变**：独立复核真实源 7 文件 size+mtime+一致口径全量 sha256 = **ALL_UNCHANGED**（驱动自身 SOURCE_MODIFIED 系 harness 比较口径 bug，已纠正）。
4. **回归全绿**：SQLite 定向 scene 族+slope 接线 **104 passed** RC=0；worktree 洁净 0 业务改动；隔离资源 0 残留（fresh SQLite+本地 NAS 根副本+独立 app 实例，无共享栈/容器/远端改动）。
5. **harness 修复**：首跑 404=本侧驱动裸 endpoint（非产品缺陷，VLM 实测存活），已修 `/v1/chat/completions`；补 `requests 2.34.2`（纯加法）。

## AC 达成

- 切片非空可打开：部分（真实切片 SUCCESS 产出可发布段，产物文件因发布阻断未落）
- 区间内容合理：达成（row19 坡道段在源袋时间范围内）
- 父子/标签/当前版可查：未达成（缺口#2 发布阻断无子包；父包 API 查回 200）
- 获取有效：部分（父包正式 API 查回有效）
- 原包不变：达成（独立复核 ALL_UNCHANGED）
- P0 必要基础完整：未达成（端到端正式链断在 #1/#2 真实产品缺口）

## 总判定

本单作为**取证/缺陷定位单完整交付**：端到端跑到真实切片 SUCCESS，精确定位 2 个 P0 硬阻塞根因+全袋证据+回派方向+原包不变独立复核+回归全绿+0 越界。**端到端闭环未全绿**因 2 个真实产品缺口（#1 READY 前置、#2 发布 offset），按 dispatch §四收口，**P0 闭环收口需协调者回派 #1/#2 修复后复跑**（E2E 驱动 `scratch/t10_e2e.py` 已固化可复用）。

## 未执行项

- 未发布/未登记子包（缺口#2 硬阻塞，非本侧能力问题）
- 未跑 MySQL 隔离库（0 数据库语义改动）；未跑全量 813（0 业务改动，定向 104 已覆盖）
- 共享栈 live :18080 scene 路由不可达=镜像版本滞后环境事实，非产品缺陷
