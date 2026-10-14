# TASK-11S-BATCH-1012 / 协调者裁决 — dup 第二份切片（FFDEE943×4）处置

时间：2026-10-14T00:39 +08:00（夜间静默回合，不群报）。来源：TESTER 00:24/00:33 两口径 + C obs13/obs14 实测，`slices/test/spray/FFDEE943…` 顶层 4 个子包（~202MB×4，23:54 发布）=dup run `scene-a4824f1c` attempt-2（源自已删 submission `13dc398c`）SUCCESS 后真实发布产物；`.staging/scene-a4824f1c…` 为 0B 空壳。

## 裁决

1. **不删不并、不新开清理任务**。该 4 子包属双写事件实证产物，正式验收以 A flat `a65a25a7` 绑定 run 全链为准（尚未绑定，D4 第③步在 A 面推进中）。
2. 14_42_48 的 source `FFDEE943…` 为按内容哈希派生的同一 source——正式 run 若 SUCCESS，其 PUBLISH/REGISTER 与现存 4 子包走同一幂等路径。TESTER 对 `a65a25a7` 绑定 run 验收时，把「发布幂等如何处置已存在的同名 source 切片」并入两次 reconcile 核账口径，如实记录即可，不预判结果。
3. 该产物**不计入本批验收交付物**，TEST_REPORT 以「双写事件产物」一节如实登记：run 归属、发布时间 23:54、来源已删 submission、与正式链的 source 同源性、正式 run reconcile 对现存的处置证据。
4. 若正式 `a65a25a7` run 终态暴露真实缺陷（发布失败/覆盖异常），按缺陷流程保留现场报协调者最小返修，届时再议是否清理。

责任人：TESTER（登记+核账口径），A（D4③ 绑定推进不受本裁决影响）。C 继续只读核账，不处置。