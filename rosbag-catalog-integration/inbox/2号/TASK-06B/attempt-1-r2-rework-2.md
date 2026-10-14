---
task: TASK-06B
item: attempt-1-r2-rework-2
owner: 2号
status: DELIVERED (review pending, commit 9325155, 2026-10-10 15:58)
dispatched_by: 协调者
updated: 2026-10-10 15:51
base: wt-04a a07c181（你的 B8c high 小修之上续做）
round: 同返修单内小修（不占新轮次）
---
# 2号小修：r6 OCR 两条 medium（high 已修完，a07c181 验收认可）

r6（report_service 补审，ce42f0e4，1h15m34s 收口 3 findings）的 high（vehicle 路径注入）你已修（a07c181，三处口径统一+_safe_vehicle_key 继承父包 Vehicle，核验通过）。**剩 2 条 medium 一并修掉**，与 a07c181 同批 OCR：

1. **M-1 写库 aware_now → local_now**：`scene_result_report_service.py:563` `child.updated_at = aware_now()`——AGENTS.md 不变量"应用写库必须 app.clock.now()（naive 中国标准时间）"；当前 DISPLAY_TIMEZONE 默认 Asia/Shanghai 值碰巧对，配置一改写错墙钟，且与本文件其余写入（local_now）不一致。改 local_now()；**只改落库处，对外响应/日志的 aware 用法不动**；:501 docstring 里"updated_at 用 aware_now()"同步更正。
2. **M-2 父包指纹 fail-open → fail-closed**：`:266` `if parent.fast_fingerprint and manifest.source_fingerprint != parent.fast_fingerprint:`——父包无指纹时整条校验静默跳过，与函数 docstring（:244"缺失/不等 → 409 SOURCE_FINGERPRINT_MISMATCH"）和 R2-08"不覆盖不猜测"矛盾。改为：`if not parent.fast_fingerprint: raise 409 SOURCE_FINGERPRINT_MISMATCH: 父包缺少 fast_fingerprint 无法核对源身份`。

验证：两条各带定向回归（M-1 断言 child.updated_at 与 bag_record 表同口径 naive；M-2 父包无指纹 + manifest 带指纹 → 409）。交 a07c181 之上单 commit + 回执更新 + 群内通报。OCR 不自跑（协调者对 a07c181..tip 同批跑，拆批尺寸预检已进 skill）。