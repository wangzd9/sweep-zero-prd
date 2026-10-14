event_id: coord-incident-20261012-100453-sessions-truncation
checked_at: 2026-10-12T10:00:53+08:00
role: COORDINATOR
status: INCIDENT_RECOVERED
summary: 10:0x 巡检写入脚本 scratch/coord_poll_100053_write.py 用 open(mode="w") 后调用 f.read() 抛 io.UnsupportedOperation，导致 inbox/sessions/COORDINATOR.md 被截断为 0 字节（原 9544B @ 09:58:47，截断 10:04:49）。event coord-poll-20261012-100053-nochange 已先写成功，租约已正确 release。10:1x 恢复：以 legacy 镜像 sessions/COORDINATOR.md（407123B，含 09:50 r71 检查点+完整历史，未波及）为基底重建 inbox 侧文件（409991B），丢失窗口（09:50 后 9.5KB）按 HANDOFF 顶部 09:47/09:50 检查点与 events 目录重建并标注[重建]。无业务交付/任务状态受损（业务状态权威源=TODO/HANDOFF/events，均完好）。
next: 后续 sessions 写入一律先 read 再整文件 rewrite 或用 append 模式；杜绝 mode="w"+read 组合。