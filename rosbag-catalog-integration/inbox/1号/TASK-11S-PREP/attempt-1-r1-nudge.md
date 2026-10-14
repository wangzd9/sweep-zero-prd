# 催办：TASK-11S-PREP attempt-1-r1 装配返修立即开工（用户 16:2x 群内指示"催A开始干"）

- status: NUDGE（催办，非新派单；原单 `attempt-1-r1-dispatch.md` 已派 16:0x，A 15:58 后未接单）
- 时间：2026-10-13 16:2x +08:00（协调者，用户直接指示）
- 背景：A 刚交付 `d8f7206` 后进入等待态，r1 单落 inbox 尚未 ACK（用户 16:02 加速指令④已点名 A 立即修部署装配）
- **用户口径**：ACK 时限是告警上限不是固定等待——A 本巡检回合立即 ACK 开工，不要等下一轮

## r1 四项（重申，见原单）
1. `scene-host.service` 宿主机 Python → **已验证 Docker 镜像**（`rosbag-spray-runtime:20261013` 固定摘要，装配口径以强模型线 `runtime-install-handoff.md` 为准）
2. `SPRAY_MODEL_ENDPOINT` → **`SPRAY_VLM_ENDPOINT`**（env.example 第 15 行 + DEPLOY-ENTRY.md，配套变量名以代理代码实读面为准）
3. "proxy 与 16B 旧 head 逐字节一致" → **发布时点固定 SHA 校验**（12S-C 已加 9 行接线，r2 还在其后）
4. 空库迁移六步 → **补生产数据副本隔离升级实验**（隔离库 dump→恢复→升级→抽样对照，副本 sha256+行数/字段证据，不触生产）

## 交付
- `d8f7206` 续 commit 冻结 + 回执 r1 段，**17:00 前**（17:30 停止点 G4 证据输入）
- ACK 写 `inbox/1号/TASK-11S-PREP/attempt-1-r1-ack.md`
- 若 16:40 仍无 ACK/sessions 无更新，协调者升级通报用户