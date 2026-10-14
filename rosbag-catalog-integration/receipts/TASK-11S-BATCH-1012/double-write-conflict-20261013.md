# TASK-11S-BATCH-1012 / A — 双写冲突申报（需协调者裁决）

时间：2026-10-13 21:50 +08:00，owner=A（A-batch-1012）。**夜间静默，工作照常落盘不群报；此冲突属生产 incoming/ready 根，需协调者裁决，A 未擅自删除任何数据、未 kill 未知 owner 进程。**

## 事实（实测证据）

### 1. 本角色（A）按契约正确落位（flat `incoming/spray/<bag>`）
契约：`relative_path=<bag_name>`（相对 `spray/`，不加日期子目录）；首包既有 submission `9949d1a7…` 的 bound source 即 `ready/spray/rosbag2_2026_10_12-15_58_23`（flat），确认 flat 为既有正确口径。
A 用 staging（`.upload-staging/spray-production-1012-20261013/`，扫描树外同盘）rsync→逐文件 SHA 一致→原子 rename 入 `incoming/spray/<bag>`→移后 SHA 复验。正式提交（`POST /api/v1/ingest-submissions`，profile scene-spray，stable idempotency_key 持久存 `upload-ledger.json`）：

| 包 | A 落位 | A 提交结果 | submission_id |
|---|---|---|---|
| rosbag2_2026_10_12-15_58_23（首包） | 复用（本机 vs `ready/spray/` 副本逐字节 SHA 一致，metadata `5a3cb296…`=manifest） | **不重提交**，复用既有 PASS | `9949d1a7…`（既有 SCHEDULED/CONSUMED） |
| rosbag2_2026_10_12-16_31_25（25MB） | flat 落位 | **HTTP 201 PENDING_INPUT** | `e5649055…` |
| rosbag2_2026_10_12-16_00_13（90MB） | flat 落位 | **HTTP 201 PENDING_INPUT** | `99615748…` |
| rosbag2_2026_10_12-16_58_28（6.8GB） | flat 落位 | **HTTP 201 PENDING_INPUT** | `518089ed…` |
| rosbag2_2026_10_08-14_42_48（725MB） | flat 落位 | **HTTP 409 PATH_CLAIMED**（存在 A 未创建的 pending submission 已占该 flat relative_path） | A 侧无 id |
| rosbag2_2026_10_12-16_33_10（空包 0B×2） | flat 落位 | HTTP 201 PENDING_INPUT（提交仅记录意图） | `7a71e404…` |
| rosbag2_2026_10_12-16_37_47（7.3GB） | 见下 | A 冻结 op 前在 staging 复制中，**A 未提交** | — |
| rosbag2_2026_10_12-16_02_03（10.1GB） | 见下 | A 冻结 op 前未开始，**A 未落位/未提交** | — |

空包 16_33_10 实际拒绝门（已用 app 代码只读探针复现，非猜测）：`app/scanner/metadata.py:parse_metadata` 对 0 字节 metadata 抛 `ValueError: missing rosbag2_bagfile_information`（scanner `_process_bag`→`validate_bag_input` 处拒绝），不回退、不补造、可追溯。

### 2. 未授权的第二写者（双写冲突源）
- 进程：`/usr/bin/zsh -lic 'set +m; SRC=~/下载/1012 DST=/mnt/nas_backup/rosbag_scene_processing/incoming/spray/20261012; mkdir -p $DST; for bag in rosbag2_2026_10_12-16_00_13 rosbag2_2026_10_08-14_42_48 rosbag2_2026_10_12-16_37_47 rosbag2_2026_10_12-16_58_28; do cp -a "$SRC/$bag" "$DST/.$bag.tmp" && mv …'`（pid 2519775，21:25 观察在途，子 `cp -a` pid 2530899/2525494 等）。
- 归属：PPID=1366 = `hermes_cli.main gateway run`（Hermes gateway 进程），**不在 A 的 systemd runtime_tools worker 树（pid 1281→2520120→2520138）内**，也非 A 的 terminal bash 树 → **属另一并行 Hermes 会话/遗留进程**（疑 Codex 临时接管期未清干净的上传循环，但 A 未确证，如实标注为"未识别 owner 的第二写者"）。
- 口径：**date-grouped** `incoming/spray/20261012/<bag>`（`cp -a` 保留源 mtime，故文件 mtime 显示 10月12 为源原始时间，非创建时间）。
- 现状：主 zsh 已退出、无孤儿 `cp -a` 在跑；但其产物已存在于**扫描树内**：
  - `incoming/spray/20261012/{rosbag2_2026_10_08-14_42_48, rosbag2_2026_10_12-16_00_13, rosbag2_2026_10_12-16_37_47, rosbag2_2026_10_12-16_58_28}`（21:35 观察）
  - `ready/spray/20261012/{rosbag2_2026_10_08-14_42_48, rosbag2_2026_10_12-16_00_13, rosbag2_2026_10_12-16_37_47, rosbag2_2026_10_12-16_58_28}`（21:47 观察，scanner 已把 date-grouped incoming 移入 date-grouped ready）
  - `incoming/spray/20261012/rosbag2_2026_10_12-16_02_03`（孤儿 cp 目标，mtime 18:06，疑 10-12 遗留或当晚产物，A 未确证）

### 3. 冲突后果（若不清理）
- **重复 scene run**：date-grouped `ready/spray/20261012/<bag>` 会被 scanner 以 `relative_path=20261012/<bag>` 登记为**新 source**，与 A 的 flat `ready/spray/<bag>`（`relative_path=<bag>`）并存 → 同一物理包跑两遍，烧模型，违反"唯一正式 proxy / SCENE_EXEC_HOST 串行 / 不重复启动任务"。
- **14_42_48 已现 409**：A 提交 flat `rosbag2_2026_10_08-14_42_48` 被 `PATH_CLAIMED` 拒绝——一个 A 未创建的 pending submission 已占用该 flat path（无法枚举 id，GET 仅按 id 查）。说明第二写者或另一会话**也在做 flat 提交**，文件 date-grouped 与提交 flat 混用，进一步加剧身份错乱。

### 4. A 已采取的自保动作（均在本角色权限内）
- **冻结 A 的大包 op**：`systemctl --user stop role-operation-c9eea960e21ba9c8413ade01.service`（runtime_tools op `TASK-11S-BATCH-1012-attempt-1-bigbags-copy` → status **UNKNOWN**，worker 2520120 已消失，helper 不自动重跑）。防止 A 继续放置 16_37_47/16_02_03 flat 副本、与 date-grouped 副本叠加成第 4/5 重。
- A **未 kill** 第二写者进程（owner 未识别，非 A 树）、**未删除** 任何 `incoming/spray/20261012/` 或 `ready/spray/20261012/` 数据（生产根、非 A 创建）、**未 PATCH** 14_42_48 的未知 pending submission（非 A 所有）。

## 需协调者裁决（A 待指令，不自行处置）
1. **date-grouped `20261012/` 归属与处置**：确认第二写者身份（Codex 遗留？另一绑定会话？）；裁决保留哪一口径（应为 flat `relative_path=<bag>`，与首包既有 bound source 一致），并授权**安全移除** `ready/spray/20261012/*` 与 `incoming/spray/20261012/*`（date-grouped 重复副本，防止重复 scene run）——此移除属生产数据写操作，A 需协调者明确最小纠错范围+授权才执行。
2. **14_42_48 flat 409 的占用方**：请协调者核该 pending submission 的 owner/identity（A 无 list 端点无法自查）；若是第二写者误占，需其撤回或协调者裁决以何者为正。
3. **16_37_47 / 16_02_03 收尾**：A 冻结后未提交这两包 flat；待上述清理+裁决后，A 从 A staging 续放 flat 副本并正式提交（stable key 已可派生，ledger 有 src_sha）。16_02_03 A 尚未落位，需重放。
4. **BATCH-STATUS 唯一状态表**：请协调者更新逐包表，标注 14_42_48=409 冲突、date-grouped 重复、A op 冻结，避免 C/TESTER 误按"单套 flat"口径验收。

## 证据文件
- `receipts/TASK-11S-BATCH-1012/upload-ledger.json`（A 每包 state/src_sha/idempotency_key/submission HTTP 响应）
- 进程证据：`ps` 输出（2519775 zsh -lic date-grouped cp -a；2520120/2520138 A runtime_tools worker/pipeline）
- 路径证据：`incoming/spray/{flat…,20261012/*}`、`ready/spray/{flat…,20261012/*}`、`20261012/.rosbag2_2026_10_12-16_02_03.tmp`
- A op 冻结：`operations/A/TASK-11S-BATCH-1012-attempt-1-bigbags-copy/result.json`（status UNKNOWN，"原 worker 不在；不推断成功、不自动重跑"）
- 空包拒绝复现：`app/scanner/metadata.py:parse_metadata` 0 字节输入 → `ValueError: missing rosbag2_bagfile_information`