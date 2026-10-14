# 过期租约恢复证据 — B 角色 15:45
- 旧 owner: cron-b-poll-6f7471d8747c-20261014-142853（cron-b-poll 14:38:41 claim，pid 字段 null，expires_at epoch 1791960221 ≈ 2026-10-14 14:43 +08:00 已过期）
- 核实: ps aux | grep 142853 零命中（15:45 实测）；该 owner 为上一轮 cron 会话，随会话结束不存在可定位存活进程
- 14:39 轮次已完成工作（role-record 事件 f54a534e 落盘），无未提交业务写
- 恢复操作: recover --owner 原owner --confirmed-stopped --evidence 本文件，再 claim
