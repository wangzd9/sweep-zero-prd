---
event_id: OCR-RUNTIME-FIX-20261013
kind: workflow_migration
to: COORDINATOR
status: NEW
skill_version: 1.5.0
source: explicit-user-request
---

**OCR固定流程已落地：协调者Skill 1.5.0 2026-10-13 14:01 +08:00**

- **唯一入口：** 重新加载 `complex-task-coordinator`，先读 `references/ocr-runtime.md`。今后只调用 `ocr_runtime.py prepare → start → status`；禁止裸ocr review、terminal后台、nohup/setsid、临时runner/等待链及恢复18002。
- **运行规则：** prepare零模型冻结base/head、全入选与解析规则、背景/配置/模型及脚本副本；start独立systemd service跨回合、全链双锁、配置只读。固定max-tokens=0/medium/concurrency=1/任务60min/请求900s，弱模型不临时换参。15项隔离回归含真实systemd跨启动scope退出通过。
- **裁决规则：** 失败立即停后批。全批完整manifest、范围/文件/模型匹配且rc=0仅 **AWAITING_DECISION**，仍核findings、跨契约和测试；同run/身份换目录也拒绝重复。原run退出、有根因处理与授权时才显式reuse-run补审，复用有效成功批、最多一次，再失败升级。
- **12S-B在途保护：** 原1897396链保留自然收口，旧chain/restart入口已退役，未启动新真实OCR。独立一次性service在旧链退出后仅纠正它可能写回的18002。真实候选prepare已核12文件2批，start被LEGACY_OCR_BUSY拒绝；**不要在旧链完成后直接跑候选包重审已有成果**，先核旧manifest/发现。
- **证据与交接：** `/home/wang/work/doc/analysis/ocr-runtime-20261013/REPORT.md`；项目协议/ROLE-BINDINGS已同步，job ID/业务门禁/强审授权保持。仓库文档提交 `ee903d8` + `0e9a2df`，Skill/工具/共享指南在Git外。通知 `inbox/coordinator/OCR-RUNTIME-20261013/notice.md` 已落盘。
- **下一步：** 确认消费新版入口与规则，后续OCR派单写固定run路径/unit身份，由原poll观察；旧结果仍按实际覆盖/发现裁决。本修复不授权强审、部署或放行12S-B/16B。
