# TASK-11S-BATCH-1012 / 协调者裁决 — 双写冲突收口 + A 续跑授权（ruling-doublewrite-2210）

时间：2026-10-13 22:10 +08:00，owner=COORDINATOR（批次唯一状态单写者）。
消费：A 21:52 `double-write-conflict-20261013.md` 四项裁决请求 + C obs4/obs5 异常链 5 条诉求 + 21:44 群请求「当前状态」（静默期不落群，此处归档）。

## 一、协调者独立核实事实（全部只读，直接查生产库/代理，非转述）

数据源：处理机 `processing-machine` 生产 backend `127.0.0.1:18000`（`/health/ready`=`environment:production`，healthy）、scene-proxy `127.0.0.1:8767`（`active_runs=[]`）、生产 MySQL `rosbag_catalog`（`ingest_submission`/`purpose_schedule_event` 全量读取）、NAS `/mnt/nas_backup/.../{incoming,ready}/spray/`。

1. **生产 18000 健康，非故障。** C obs4 报「18000 HTTP 000」系在本开发机探 `127.0.0.1:18000`，而生产 backend 在**处理机**侧 `18000`；本机 `18080`=本地栈 `environment:test`（C 已实测确认）。生产端点 ready 正常。**该异常项解除，C 无需再按 18000 挂起归因。**

2. **当前无在途 run。** `scene-proxy /health`=`active_runs:[]`；`purpose_schedule_event` 6 条全 `CONSUMED`。无 kill/retry 需求（符合「大包跨夜不因观察超窗 kill/retry」）。

3. **第二写者身份=用户恢复交接期 Codex 遗留 `zsh -lic` 上传循环**（A 申报 pid 2519775，PPID=hermes gateway 1366，**非 A 的 systemd runtime_tools 树**），主进程已退出、无存活 `cp -a`。其越界动作（对照生产库实证）：
   - date-grouped 复制 4 包进 `incoming/spray/20261012/`（违反 flat 契约，首包既有 bound source 即 flat）；scanner 已消费移入 `ready/spray/20261012/{14_42_48,16_00_13,16_37_47,16_58_28}`。
   - 以**非 A idempotency 格式** `1012-spray-20261012-16_02_03`/`1012-spray-20261008-14_42_48` 对 16_02_03/14_42_48 做了 flat 提交 → `ingest_submission` 行 `24d60fee…`/`13dc398c…`，均 `PENDING_INPUT`、**无 source 绑定、无 source_metadata（缺 vehicle_code）**，且持有该 flat `path_claim_key`（→ 这是 A flat 提交 14_42_48 得 409 PATH_CLAIMED 的直接原因）。

4. **date-grouped 三包已跑且 fail-closed FAILED，未烧模型。** 生产库 `purpose_schedule_event` + proxy 日志双证：
   - `03281a51…`（20261012/14_42_48）→ run `scene-a4824f1c…` `FAILED at RESOLVING: spray 场景缺车辆绑定…fail-closed 不执行`
   - `5e08e73d…`（20261012/16_37_47）→ run `scene-eb4397c3…` 同上 FAILED
   - `7f4e7b75…`（20261012/16_58_28）→ run `scene-24ab78bb…` 同上 FAILED
   均停在 RESOLVING（EXTRACT/INFER 之前），**无 VLM 调用**。「重复 scene run 烧模型」的最坏后果已被代理的车辆绑定门禁天然拦截，实际损耗=3 次空 RESOLVING 判定（可忽略）。

5. **正确 flat 链路已完成 3/8**：`9949d1a7…`(15_58_23 首包复用, PASS) / `99615748…`(16_00_13)→run SUCCESS / `e5649055…`(16_31_25)→run NOT_APPLICABLE（与 B 独立取证一致）。

## 二、逐包目标契约态 + 裁决处置

契约：flat `relative_path=<bag>`、source_metadata `vehicle_code=test`、A 唯一上传/提交 owner。目标=每包**恰好一条**带车辆绑定的 flat submission 绑定 flat ready 文件；date-grouped 与非 A 格式 submission=污染，清除。

| 包 | 正确 flat submission | 现态 | 裁决处置 |
|---|---|---|---|
| 15_58_23 | `9949d1a7` | SCHEDULED, PASS | **保持**（不动） |
| 16_00_13 | `99615748` | SCHEDULED, SUCCESS | **保持**（不动） |
| 16_31_25 | `e5649055` | SCHEDULED, NOT_APPLICABLE | **保持**（不动） |
| 16_33_10（空包） | `7a71e404` | PENDING_INPUT, 0B 文件在 incoming | **保持**，走 scanner parse 拒绝路径（`missing rosbag2_bagfile_information`）；TESTER 核拒绝可追溯 |
| 16_58_28 | `518089ed`（A flat） | PENDING_INPUT 未绑定；flat 文件在 `ready/spray/16_58_28`；date-grouped `7f4e7b75` 已 FAILED | A **确保 flat `518089ed` 绑定 flat ready 文件并跑**（预期 NOT_APPLICABLE）；清除 date-grouped 副本 |
| 16_37_47 | **A 尚未提交 flat** | flat 文件在 `ready/spray/16_37_47`；仅 date-grouped `5e08e73d`（FAILED） | A **提交 flat `16_37_47`**（source_metadata vehicle=test）；清除 date-grouped 副本 |
| 14_42_48 | A flat 提交 409 受阻 | 被第二写者 `13dc398c` 占 flat claim；flat 文件在 `ready/spray/14_42_48`；date-grouped `03281a51` 已 FAILED | **清除 `13dc398c`**（释放 flat claim）+ date-grouped 副本 → A **提交 flat `14_42_48`**（NEEDS_RUNTIME_RESULT，全链验收） |
| 16_02_03 | **文件全域失踪**，A 未提交 | 仅第二写者 `24d60fee`（PENDING 未绑定、无文件）；源 `~/下载/1012/…16_02_03` 完整在位 | **清除 `24d60fee`** + 残留；A **从源重拷 flat `16_02_03`（10.1GB）→ 逐文件 SHA → 原子移入 → 提交 flat**（NEEDS_RUNTIME_RESULT） |

## 三、授权 A 最小纠错范围（生产数据/库写，A 是唯一 upload/submit owner，据此授权）

A 可执行、且仅限以下；每步先备份+日志，SHA 核验后操作，**严禁触碰上表「保持」行及其文件/submission**：

1. **收口滞留 op**：A `runtime_tools` operation `TASK-11S-BATCH-1012-attempt-1-bigbags-copy` result.json 仍 `status=RUNNING pid=2520120` 但进程已退、result.log 0 字节、current_step 停 1、staging 空=僵尸记录（C obs7 第⑥项）。A 用 `runtime_tools status`/recover 收口为终态（UNKNOWN/FAILED，不自动重跑大包 op；16_02_03 走新的独立 op 重拷）。
2. **清除污染 submission**（处理机生产 MySQL `rosbag_catalog.ingest_submission`，先 `SELECT … WHERE submission_id IN (…)` 备份到 receipt 再 `DELETE`）：`13dc398c9301…`(14_42_48 第二写者 flat)、`24d60fee4455…`(16_02_03 第二写者 flat)、`03281a51…`/`5e08e73d…`/`7f4e7b75…`(3 个 date-grouped，已 FAILED)。删除后核对应 flat `path_claim_key` 释放（重提交不再 409）。
3. **清除 date-grouped NAS 文件**：`ready/spray/20261012/{14_42_48,16_00_13,16_37_47,16_58_28}`（整目录 4 包，~21GB；删除前 `du -sb`+各文件 SHA 留证，确认 flat 顶层同名文件完好后再删）。`incoming/spray/20261012/` 若残留一并清。
4. **续跑 flat 提交**（A 既有 stable idempotency 格式 `spray1012:<bag>:<hash>`，source_metadata `vehicle_code=test`）：14_42_48 / 16_37_47 / 16_58_28(确认 `518089ed` 绑定) / 16_02_03(重拷+提交)。大包用 `runtime_tools` 冻结 operation 跨夜执行，不占模型回合。
5. **禁止**：重提交已 PASS/SUCCESS/NOT_APPLICABLE 的 15_58_23/16_00_13/16_31_25；改 16_33_10 空包文件；kill 任何非 A 进程（第二写者已退出）；改业务代码/部署（本批无代码变更）。

## 四、TESTER / C 范围

- **TESTER**：按更正后分类增量独立验收——① date-grouped 3 个 FAILED run 确认**无 VLM 调用/无产物**（防伪切片）；② 16_33_10 空包拒绝可追溯；③ A 续跑的 14_42_48/16_37_47/16_58_28/16_02_03 flat run 逐包终态+产物+两次 reconcile 幂等；④ 16_02_03 重拷 SHA=源。回执 `test-receipts/TASK-11S-BATCH-1012/attempt-1.md`。
- **3 个 date-grouped 重复 run 记录处置（答 TESTER 22:05 提问）**：`scene-a4824f1c…`/`scene-eb4397c3…`/`scene-24ab78bb…` 均已终态 `SCENE_FAILED`（RESOLVING 前八步全 QUEUED，零模型零切片，TESTER 独立取证一致），危害=重复 run 记录非数据损坏。**裁决=保留 run 历史记录不删**（终态、无产物、无 VLM 调用，作为双写事件取证）；A 删除其对应 submission（`03281a51`/`5e08e73d`/`7f4e7b75`）即阻断任何再 claim/再 run，无需清理 run 行本身。
- **C**：18000 归因已解除（非生产故障）；继续只读观察处理机装配/资源/租约/进度，SCENE_EXEC_HOST 串行，大包跨夜不 kill/retry；发现新问题只取证报协调者。

## 五、群请求「当前状态」归档（21:44，静默期不落群，08:00 汇总一并给出）

本批 8 包：3 完成（首包 PASS/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE），1 空包拒绝中（16_33_10），4 因 Codex 遗留双写污染受阻（14_42_48/16_58_28/16_37_47/16_02_03），已裁决清除+授权 A 续跑，生产 18000 健康无在途风险。