# TASK-11S-BATCH-1012 / C / 只读观察指针 — ruling-duprun-2338

状态：DISPATCHED，owner=C，2026-10-13T23:38+08:00。批次状态见 `inbox/coordinator/SPRAY-BATCH-1012-20261013/BATCH-STATUS.md` 与裁决 `ruling-duprun-2338.md`。

你的范围（D5 + 常规观察）：

1. **D5 RETRY 发起方归因（只读）**：查 3c9c496 代码/调度器是否存在对 SCENE_FAILED run 的自动 RETRY（retry_mode=normal）机制及 22:53:02 三 run 同刻 RETRY_REQUESTED 的触发源；结论落 C 观察事件报协调者。**不新开任务、不改代码、不扩需求**；若属系统设计，如实记录为既有行为。
2. 常规只读核账维持：`scene-4acf689f`（16_02_03，跨 DB3 大包）推进与终态、`scene-a4824f1c` attempt-2（A 按 D2 处置中，只读跟踪 cancel/收敛结果）、`scene-eb4397c3`/`scene-24ab78bb` attempt-2 收敛、SCENE_EXEC_HOST 串行租约、NAS 余量/负载、proxy active_runs。
3. 禁止：kill/retry/重启/改挂载/起新 run/模型线；发现问题只取证报协调者。

事件按既有格式落 `inbox/events/C/`，夜间静默照常（落盘继续，不群报）。