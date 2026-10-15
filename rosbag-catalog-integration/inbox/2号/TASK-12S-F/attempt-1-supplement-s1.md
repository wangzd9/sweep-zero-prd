# TASK-12S-F 派单补充 S1（协调者，2026-10-15 08:52 +08:00）

- **状态**：SUPPLEMENT（不改 attempt-1 正文与 REQ-21/AC-21 范围）。owner=执行者 B。
- **背景**：08:38 原派单前提"E 已接受、base=E head `b39a3ec`"失效——E 的 OCR retry1 裁决 08:52 更正为 6 条 CONFIRMED CORRECTION（E-R1～E-R8），接受撤销、A 返修 attempt-2 已派（`inbox/1号/TASK-12S-E/attempt-2-r1-rework-dispatch.md`）。E-R1/R2/R3 落在 `pending_binding.py` 的**字段持久化/选取/防御分支**点位，E-R7/R8 落在 `source_service.py` 指纹判定区——与 F 的拒绝态接线点相邻但不改 F 需求语义。

## 对 B 的口径调整（仅三条）

1. **开发继续，不暂停**：按原派单文件边界开工/进行中均有效；`b39a3ec` 上 E 的行为语义不因本次返修改变（A 只修 OCR 纠正点位），F 的设计不返工。
2. **冻结 base 后移**：F 的交付冻结 head 最终须以 **E attempt-2 冻结 head**（A 交付后协调者通知）为 base——若 B 已基于 `b39a3ec` 提交，届时做 rebase 到新 head（机械操作，无冲突预期；冲突则报协调者指定接线处理）。**在收到"E attempt-2 冻结 head=XXX"通知前，F 不必提前冻结交付**，可继续自测/完善用例。
3. **验收链后移**：F 交付门禁（机械核验 → OCR → TESTER → 接受）在 E attempt-2 收口接受后启动；E/F 仍按"随 12S 集成节奏 --no-ff、不单独合 main"口径。

## 边界不变

原派单硬边界/回执要求/ACK 事实全部保留；本补充不新增范围、不改 REQ-21/AC-21。