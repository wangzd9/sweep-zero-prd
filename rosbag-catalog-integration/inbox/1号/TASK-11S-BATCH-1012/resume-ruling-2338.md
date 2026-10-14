# TASK-11S-BATCH-1012 / A / 续跑指针 — ruling-duprun-2338

状态：RESUME_DISPATCHED，owner=A，2026-10-13T23:38+08:00。你 23:2x 回执（a-attempt-1.md）四项「未执行项」已由协调者裁决。

通读 `inbox/coordinator/SPRAY-BATCH-1012-20261013/ruling-duprun-2338.md`（取代 2210 中与 attempt-2 冲突的前提；其余 2210 禁止事项继续有效）。BATCH-STATUS 已同步。

你的动作（按裁决顺序）：

1. **D2 — 14_42_48 dup run `scene-a4824f1c` attempt-2**：**23:5x 增补：C obs11 实测该 run EXTRACT 产物已全量落盘（171 jpg/534 pcd）+ INFER 活跃在途（VLM Running=4）= 正在真实烧模型**。你的下一动作=**立即**只读核 3c9c496 是否有正式 run cancel 端点：有→尽快 cancel 止血（cancel 前留证 run 状态/事件链/slices 目录计数，cancel 后核终态+资源释放，run 行保留不删）；无→不得直删表/强杀，让其自然收敛，任一 SUCCESS=重复烧模型实证第一时间报协调者保留现场。14_42_48 正式验收以你的 flat `a65a25a7` 绑定 run 为准。
2. **D4 — 时序固定**：等 3 dup run 全终态+claim 释放 → 备份后删 3 条 date-grouped submission（`03281a51`/`5e08e73d`/`7f4e7b75`）→ 核你的 flat 三提交 409 释放/scanner 绑定 → 删 `ready/spray/20261012/`（删前 du+SHA 留证，flat 顶层文件完好后再删）+ `incoming/spray/20261012/` 残留。大包/删除机械操作走 runtime_tools 冻结 op。
3. **D1 — `24d60fee` 保留确认**：不删不重提（2210 清除指令已作废），维持你 22:56/23:2x 口径。
4. **D6 — 16_33_10**：正式拒绝痕迹补进 `upload-ledger.json`。
5. **下回合观察项不变**：flat 三提交绑定推进 + `scene-4acf689f`（16_02_03）跨夜推进，大包不因超窗 kill/retry。

## 00:0x 增补（协调者 2026-10-14，消费 C obs12 D5 归因 + D2 观察点命中）

- **D2 关闭（自然收敛 SUCCESS 分支）**：`scene-a4824f1c` attempt-2 已 SCENE_DONE SUCCESS（23:54:41，C 实测），cancel 端点核查**不再需要**；`.staging/scene-a4824f1c…` 第二份切片保留现场，TESTER 取证。你的 D2 待办项核销。
- **D4 时序解锁条件推进中**：dup 1/3 终态（a4824f1c SUCCESS）；`scene-eb4397c3` 23:58 SCENE_RUNNING（预期 NOT_APPLICABLE 快速拒绝）、`scene-24ab78bb` 排队。你继续按 D4 固定顺序：3 dup 全终态+claim 释放（只读 SELECT 核）→备份删 3 date-grouped submission→核 flat 三提交 409 释放→删 `ready/spray/20261012/`+`incoming/spray/20261012/` 残留（删前 du+SHA 留证）。删除机械操作走 runtime_tools 冻结 op 跨回合。
- **D5 归因结论（C obs12）知会**：22:53:02 三 RETRY 非系统自动重试，是开发机 192.168.2.132 外部人工经正式 /retry API 三发（scratch 脚本 retry3.sh/bind_vehicle.sh 自称『运营授权』）。肇事者身份核实面在协调者/用户，你无需处置；`bag_record` 三包 vehicle_id=1 MANUAL 绑定为外部操作产物，**不改动**。
- 其他不变：D1 `24d60fee` 保留、D6 16_33_10 落账、禁止触碰保持行/改代码部署。

禁止：触碰保持行（15_58_23/16_00_13/16_31_25）、改代码/部署、D2 之外 kill 任何进程。完成后更新 `receipts/TASK-11S-BATCH-1012/a-attempt-1.md` + 事件，TESTER 按裁决第四节增量验收。