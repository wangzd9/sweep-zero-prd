import json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
TOKEN = "e56d5cc5a1a543d4a785fcedc6044bd8"
OWNER = "cron-coord-poll-215553"

def run_cmd(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print("CMD:", " ".join(cmd[:8]), "... rc=", p.returncode)
    if p.returncode != 0:
        print("STDERR:", p.stderr[:2000])
        sys.exit(1)
    return p

# 1) decision: TESTER post-merge verify ACCEPT -> TASK-09 DONE
decision = """# Decision：TASK-09 post-merge-ca8730d-verify（TESTER 合入后独立真 MySQL 验证）

- 时间：2026-10-11 21:5x +08:00（cron poll 14ae4556629a，checked_at 2026-10-11T21:50:53+08:00）
- 角色：协调者（单写）
- 对象：TESTER `TEST-TASK09-post-merge-ca8730d` attempt-1（派单 21:42，base `ca8730d`）
- 结论：**ACCEPT + TASK-09 DONE**

## 协调者独立核验（非采信 TESTER 自报）

1. **快照一致性**：`/home/wang/work/rosbag-catalog` `git rev-parse main origin/main` 双核 = `ca8730d7050c105b73e9387f4adda182d3a14e64`；`git merge-base --is-ancestor ca8730d main` = yes（`a60bb81` 已 --no-ff 合入在案）。
2. **原始证据复核**：`~/.hermes/cache/scratch/t09-tester-pm09/results.json`（21:47:36 落盘）all_pass=true，5 项全 PASS RC=0（mysql_06b_core 60 / mysql_slope_wiring 44 / alembic_upgrade head=`20261009_02_ingest_frozen (head)` 单头 31 表 / sqlite_full 813+10skipped / ruff_3files），`db_residue="(empty)"`；日志抽核 `pm09_mysql_06b_core.log` 尾部 `60 passed, 1 warning in 5.47s`、`pm09_sqlite_full.log` 尾部 `813 passed, 10 skipped in 55.50s` 与回执口径逐项一致。
3. **资源 0 残留**：`docker ps -a | grep tester-pm09` 0 命中、`git worktree list | grep pm09` 0 命中（独立实测）。
4. **回执/报告一致性**：`test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md`（21:49 交付 TEST_REPORT_PENDING）+ `reports/TEST-TASK09-post-merge-ca8730d/attempt-1.md` 与 results.json 无出入；零业务代码改动（仅 scratch 运行器/plug）。

## 裁决

- TASK-09 收口条件（21:42 检查点口径：TESTER PASS 后才可写 DONE）满足 → **TASK-09 转 ✅ DONE**（main `ca8730d`）。
- §G 既有裁决维持（row19 AC 达成；500 帧外部 VLM 缺陷入 TASK-11 前置事实，不派单）。
- 强审查 NOT_REQUIRED 维持（客户端构造面 +17/-3，21:42 decision 口径）。
- **TASK-10 候选重算**：前置 TASK-08 DONE ✅ + TASK-09 DONE ✅ 齐备，本期 P0 已授权、输入齐全（本地栈 8 容器 healthy / NAS 切片只读在位 / VLM 可达）→ **立即派 2号 attempt-1**（`inbox/2号/TASK-10/attempt-1-dispatch.md`，base `ca8730d`；owner=2号，B 为 TASK-09 原 owner、熟悉真实样本+VLM 链路且交付冻结转空闲，文件/资源无冲突）。
- 门禁：TASK-11 生产启用维持未放行（VLM 500 帧+假阴性事实为前置输入）；TASK-07/12/13/14/15 维持 DEFERRED 不扩。

## 事件

- event：`coord-poll-20261011215053-task09-done-task10-dispatched`
- TODO：TASK-09 行 ✅ DONE；TASK-10 行 RUNNING（attempt-1 已派 2号，待 ACK）
"""
with open(ROOT + "/inbox/coordinator/TASK-09/post-merge-ca8730d-verify-acceptance-decision.md", "w") as f:
    f.write(decision)
print("decision written")

# 2) TASK-10 dispatch to 2号
dispatch = """# 派单：TASK-10 attempt-1 目录→坡道切片→数据库→API 获取真实工程闭环（P0 收尾单）

- status: DISPATCHED
- 派单时间：2026-10-11 21:5x +08:00（协调者 cron poll 回合）
- 任务：TASK-10（REQ-01～10、13 的 P0 部分 / 对应 AC 的 P0 部分），前置依赖 TASK-08 DONE ✅ + TASK-09 DONE ✅（21:5x 收口）
- owner：2号（B，wt-04a；TASK-09 原 owner，熟悉真实 NAS 切片+VLM 接线，交付冻结转空闲）
- base：main `ca8730d`（= origin/main，21:5x rev-parse 双核一致；TASK-08/09 全链已合入，无在途漂移）
- 性质：**P0 最后一张业务单**（真实工程闭环收敛），不是新建任务/扩需求；TODO §3 TASK-10 卡为准。

## 一、上游已就绪的事实（可直接引用，不重探）

1. **本地栈 8 容器 healthy**（backend/frontend/mysql/scanner/orchestrator/bag-cleanup-worker/双代理，Up 35h，21:5x 实测）——接收/调度/执行/回报链在本地可用。
2. **真实坡道样本**（只读）：`/mnt/nas_backup/data_slice/1165414093/slope/` 7 条 db3 在位（~239MB/15s，11279 消息/袋，参考 `/home/wang/work/ros2_slice/slice_message.csv`）；**row19 `1165414093_slope_20260818_105105_105120` 已在 TASK-09 实测 SUCCESS**（可发布区间非空），其余 row20/21 有外部 VLM 单帧确定性 500 缺陷（TASK-11 前置事实，不阻塞本单）。
3. **生产接线已合入 `ca8730d`**（TASK-09）：`vlm.py` 模型 ID 完整路径默认（`/home/sysadmin/data/disk02/jc/models/qwen3.8-27b-fp8`）+ max_tokens 2048 + enable_thinking 透传；`SLOPE_VLM_ENDPOINT` fail-closed（未配置=MODEL_UNAVAILABLE）。VLM 端点 `http://192.168.2.45:8002`（=18002 隧道，**不重启/不改配置**）。
4. **迁移链单头** `20261009_02_ingest_frozen`（TESTER 21:47 真 MySQL 复核 RC=0）；scene-config-v1 / scene-capability/v1 契约已合入。

## 二、闭环内容（端到端，全走正式服务链，不留测试旁路）

以 row19（或另选 1 条 slope 袋，**VLM 预算 ≤1 袋 ~15-16 帧**）为样本，跑通：

1. **目录上传/配置**：用正式 Backend API（03B 接收链）登记指定目录 + 场景/用途配置（scene-config-v1，slope 场景、PHASE0 用途）→ 冻结配置 hash（不得发 NULL-hash 事件）。
2. **真实坡道切片**：04B 适配器链（db3→抽帧→VLM→segment→writer 再切），真实 VLM 调用（预算内），断言 `SUCCESS` + 可发布区间非空 + 区间落在源袋时间范围内。
3. **NAS+数据库**：06B 正式回报/发布链（staging 校验→原子发布→子 Bag 登记→血缘/标签），数据库登记完整（父/子 uid ≤26 字符、当前版本/历史版本）。
4. **API 获取**：经正式 API 查回切片产物（区间证据/父子关系/标签/当前版），可打开、内容合理；**原包（源 db3/NAS 源目录）不变**（只读校验 mtime/大小或 hash 前后一致）。

输出=端到端实际回执：每步命令/exit code/关键响应字段 + 数据库登记证据 + API 获取证据 + 原包不变校验，落 `reports/TASK-10/`；必要风险（VLM 500 帧影响/时间映射边界/未覆盖场景）如实申报。

## 三、AC 核对（验收口径，TODO §3 TASK-10）

- 切片非空可打开 ✓（二.2/二.4）
- 区间内容合理 ✓（二.2 断言 + 二.4 查回）
- 父子/标签/当前版可查 ✓（二.3/二.4 API 证据）
- 获取有效 ✓（二.4 正式 API 响应）
- 原包不变 ✓（二.4 前后校验）
- P0 必要基础完整 ✓（全链走正式服务，不 mock）

## 四、边界与禁止

- **不写 NAS 业务目录**（`/mnt/nas_backup/data_slice` 只读）；产物/缓存只进 run 私有 work_dir 或 `/home/wang/.hermes/cache/scratch/`，用完清理；
- 不动 192.168.2.45 服务本身；VLM 调用 ≤1 袋抽帧口径（~15-16 帧）；
- **不等 UI/其他四类场景/插盘工具/可视化/规模压测**（TASK-07/12/13/14/15 范围）；工程通过 ≠ 生产就绪（质量门禁仍 TASK-11）；
- 发现模块缺陷：**定位+最小复现+记录回派，不跨模块自行改码**（TASK-08 先例口径）；
- 回归：SQLite 定向（scene 全族）+ 全量（`--ignore=tests/test_devflow.py`）+ ruff；涉数据库语义面真 MySQL 8.4.11 STRICT 隔离库文件级复跑（用完即毁 0 残留）；
- 交付 commit 在 `wt-04a` 新分支或 `wt-04a-t10`，单 commit 或最小集；回执 `receipts/TASK-10/attempt-1.md`（REVIEW_PENDING）。

## 五、停止条件

端到端四步全绿（每步有实际命令+exit code+证据落盘）+ 回归全绿 + 隔离资源 0 残留 + 回执/报告落盘。**VLM 500 帧若命中所选袋且无替代袋可用**：换袋一次；仍失败则 BLOCKED 回执（外部服务缺陷，记 TASK-11 前置事实），不无限重试。

## 六、下游

交付后：协调者机械核验（端到端证据逐项+越界核对）→ 串行 OCR（app 面如有改动）→ 验收合入 → **TASK-10 DONE → P0 停止派发**（协调者更新最终 HANDOFF/TODO，不自动转 TASK-11 或后续阶段）。
"""
import os
os.makedirs(ROOT + "/inbox/2号/TASK-10", exist_ok=True)
with open(ROOT + "/inbox/2号/TASK-10/attempt-1-dispatch.md", "w") as f:
    f.write(dispatch)
print("TASK-10 dispatch written")

# 3) TODO updates: TASK-09 row DONE, TASK-10 row dispatched
with open(ROOT + "/TODO.md") as f:
    lines = f.readlines()
out = []
for ln in lines:
    if ln.startswith("| TASK-09 | 🏃"):
        ln = ln.replace("🏃", "✅")
        ln = ln.replace(
            "合入后验证派 TESTER `post-merge-ca8730d-verify`，**09 维持 RUNNING，TESTER PASS 后才可写 DONE**；强审查 NOT_REQUIRED（客户端构造面）；TASK-10 前置 09 未 DONE 维持 WAITING）",
            "合入后验证派 TESTER `post-merge-ca8730d-verify` → **【2026-10-11 21:5x 巡检收口】TESTER attempt-1 21:49 交付全 PASS（真 MySQL 8.4.11 STRICT：06B 核心 60 / slope 接线 44 / 迁移链单头 RC=0 / SQLite 813 / ruff 绿 / 隔离资源 0 残留，results.json all_pass=true，协调者独立复核日志+docker+worktree 一致）→ **TASK-09 ✅ DONE**（main `ca8730d`，decision `inbox/coordinator/TASK-09/post-merge-ca8730d-verify-acceptance-decision.md`）；强审查 NOT_REQUIRED（客户端构造面）；**TASK-10 前置齐备即派 2号 attempt-1**）"
        )
        ln = ln.replace(
            "| 2号 / attempt-1（已合入 `ca8730d`；【2026-10-11 21:42】TESTER 合入后验证在途（`inbox/TESTER/TASK-09/post-merge-ca8730d-verify-dispatch.md`，base `ca8730d`）） |",
            "| 2号 / attempt-1（DONE，main `ca8730d`；TESTER post-merge 验证 PASS 收口 21:5x） |"
        )
    if ln.startswith("| TASK-10 | ⏳"):
        ln = ("| TASK-10 | 🏃 | 目录→坡道切片→数据库→API 获取真实工程闭环 | REQ-01～10、13 的 P0 部分 / 对应 AC 的 P0 部分 | TASK-08、TASK-09 | "
              "**RUNNING（【2026-10-11 21:5x】前置齐备（08 DONE + 09 DONE `ca8730d`）→ 已派 2号 attempt-1（`inbox/2号/TASK-10/attempt-1-dispatch.md`，base `ca8730d`，PENDING 待 ACK）：真实 slope 袋（row19 或替代，VLM ≤1 袋）端到端=目录登记/配置冻结→04B 真实切片（SUCCESS+可发布区间）→06B NAS+数据库登记（父子/标签/当前版）→正式 API 获取（非空可打开+原包不变）；发现缺陷定位回派不跨模块改码；交付→机械核验→OCR（如有 app 面）→验收合入→**P0 停止派发**；TASK-11 生产门禁不因此解除）** | 2号 / attempt-1（待 ACK） |")
    out.append(ln)
with open(ROOT + "/TODO.md", "w") as f:
    f.writelines(out)
print("TODO updated")

# 4) TIMELINE append (2 rows)
tl_rows = (
    "| 2026-10-11 21:49 | 2026-10-11 21:5x | TESTER / 协调者 cron | TASK-09 / post-merge-ca8730d-verify | TESTER 合入后独立真 MySQL 验证 **attempt-1 交付全 PASS**（21:49 回执 TEST_REPORT_PENDING：06B 核心 60 / slope 接线 44 / 迁移链 `20261009_02_ingest_frozen (head)` 单头 RC=0 / SQLite 813 / ruff 绿 / 容器+网络+worktree 全毁 0 残留，results.json all_pass=true）→ 协调者独立复核（rev-parse 双核 main=origin=`ca8730d`、日志尾部抽核一致、docker/worktree 0 残留实测）→ **decision ACCEPT + TASK-09 ✅ DONE**（main `ca8730d`）；强审查 NOT_REQUIRED 维持；§G 裁决维持（500 帧外部缺陷入 TASK-11 前置事实） | DONE | `test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md`；decision `inbox/coordinator/TASK-09/post-merge-ca8730d-verify-acceptance-decision.md`；`~/.hermes/cache/scratch/t09-tester-pm09/results.json` | TASK-10 候选重算 |\n"
    "| 2026-10-11 21:5x | 2026-10-11 21:5x | 协调者 cron | TASK-10 / attempt-1 | 前置齐备（TASK-08 DONE + TASK-09 DONE `ca8730d`）→ **派 2号 attempt-1**（`inbox/2号/TASK-10/attempt-1-dispatch.md`，base `ca8730d`=origin 双核）：真实 slope 袋端到端闭环（目录登记/配置冻结→04B 真实 VLM 切片→06B NAS+数据库登记→正式 API 获取+原包不变校验），VLM ≤1 袋预算，发现缺陷定位回派不跨模块改码；P0 最后一张业务单，验收合入后 P0 停止派发 | DISPATCHED | 派单文件；本地栈 8 容器 healthy 实测 | 等 2号 ACK（5 分钟节奏）→ 交付→机械核验→OCR→合入→P0 收口 |\n"
)
with open(ROOT + "/TIMELINE.md") as f:
    tl = f.read()
with open(ROOT + "/TIMELINE.md", "w") as f:
    f.write(tl + tl_rows)
print("TIMELINE appended")

# 5) sessions/COORDINATOR.md prepend checkpoint
ckpt = """## 2026-10-11 21:55 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T21:50:53+08:00：TESTER TASK-09 合入后验证交付全 PASS → 09 收口 DONE + TASK-10 派 2号）

- **TASK-09 合入后验证 TESTER attempt-1 交付全 PASS（21:49，收口条件满足）**：base `ca8730d`（= origin/main，rev-parse 双核+`merge-base --is-ancestor a60bb81 main` yes）；独立真 MySQL 8.4.11 STRICT：06B 核心 60 / slope 接线 44 / 迁移链 upgrade head RC=0（`20261009_02_ingest_frozen (head)` 单头 31 表）/ SQLite 全量 813+10skipped / ruff 3 文件绿 / 隔离资源 0 残留；`results.json` all_pass=true（5 项全 PASS RC=0，elapsed 75.5s），日志抽核（`60 passed, 1 warning in 5.47s` / `813 passed, 10 skipped in 55.50s`）与回执一致；docker `tester-pm09` 0 命中 + worktree `pm09` 0 命中独立实测。零业务代码改动。
- **decision ACCEPT + TASK-09 转 ✅ DONE**（main `ca8730d`）：`inbox/coordinator/TASK-09/post-merge-ca8730d-verify-acceptance-decision.md`；强审查 NOT_REQUIRED 维持（客户端构造面）；§G 裁决维持（row19 AC 达成；500 帧外部 VLM 缺陷入 TASK-11 前置事实）。
- **TASK-10 候选重算→立即派 2号 attempt-1**：前置 08 DONE + 09 DONE 齐备、本期 P0 已授权、输入齐全（本地栈 8 容器 healthy Up 35h 实测 / NAS slope 切片只读在位 / VLM 可达）、文件/资源无冲突（B 交付冻结转空闲）；派单 `inbox/2号/TASK-10/attempt-1-dispatch.md`（base `ca8730d`，PENDING 待 ACK）：真实 slope 袋（row19 或替代，VLM ≤1 袋 ~15-16 帧）端到端=目录登记/配置冻结→04B 真实切片 SUCCESS+可发布区间→06B NAS+数据库登记（父子/标签/当前版）→正式 API 获取（非空可打开+原包不变校验）；发现缺陷定位回派不跨模块改码；**P0 最后一张业务单**，验收合入后 P0 停止派发（不自动转 TASK-11）。
- **角色占用**：2号=待 ACK（TASK-10 attempt-1）；1号/3号/TESTER 空闲（A 21:52 / C 21:48 心跳已感知 `ca8730d`，legacy_busy 空）；无在途 ocr/pytest 业务进程。
- **门禁**：TASK-11 生产启用维持未放行（VLM 500 帧+假阴性事实为前置输入）；TASK-07/12/13/14/15 维持 DEFERRED 不扩。
- 本轮控制动作：claim（`cron-coord-poll-215553`）→巡检核查（TESTER 回执/报告/results.json+日志独立复核/rev-parse 双核/docker+worktree 0 残留/本地栈容器/A C 占用核对）→decision+TASK-10 派单+TODO（09 行 ✅ DONE / 10 行 🏃 派单）+TIMELINE 两行+检查点→event→release。**有状态变更（09 DONE + TASK-10 派单）**。
- **下一步**：下轮核 2号 TASK-10 ACK/开工（wt 新分支 base `ca8730d`）；交付→机械核验（端到端证据逐项+越界）→串行 OCR（如有 app 面，§3.6 尺寸预检）→验收合入→**P0 收口**（最终 HANDOFF/TODO 更新，停止派发）。
"""
with open(ROOT + "/sessions/COORDINATOR.md") as f:
    sessions = f.read()
with open(ROOT + "/sessions/COORDINATOR.md", "w") as f:
    f.write(ckpt + "\n" + sessions)
print("sessions checkpoint prepended")

# 6) HANDOFF.md prepend checkpoint
handoff_ckpt = """## 2026-10-11 21:55 巡检检查点（cron poll 14ae4556629a，checked_at 2026-10-11T21:50:53+08:00：TASK-09 收口 DONE（TESTER 合入后验证全 PASS）+ TASK-10 派 2号）
- **TASK-09 ✅ DONE（main `ca8730d`）**：TESTER `post-merge-ca8730d-verify` attempt-1 21:49 交付全 PASS（真 MySQL 8.4.11 STRICT：06B 核心 60 / slope 接线 44 / 迁移链单头 RC=0 / SQLite 813 / ruff 绿 / 隔离资源 0 残留；results.json all_pass=true，协调者独立复核一致）→ decision ACCEPT（`inbox/coordinator/TASK-09/post-merge-ca8730d-verify-acceptance-decision.md`）。
- **TASK-10 已派 2号 attempt-1**（`inbox/2号/TASK-10/attempt-1-dispatch.md`，base `ca8730d`=origin 双核，PENDING 待 ACK）：真实 slope 袋端到端闭环（目录登记/配置冻结→04B 真实 VLM 切片→06B NAS+数据库登记→正式 API 获取+原包不变），VLM ≤1 袋预算，缺陷定位回派不跨模块改码；**P0 最后一张业务单**，验收合入后 P0 停止派发。
- main `ca8730d`=origin；本地栈 8 容器 healthy；A/C/TESTER 空闲，B 待 ACK；生产启用 TASK-11 门禁维持未放行（500 帧+假阴性事实为前置输入）。
- **下一步**：核 2号 TASK-10 ACK/开工→交付→机械核验→OCR（如有 app 面）→合入→P0 收口。

"""
with open(ROOT + "/HANDOFF.md") as f:
    handoff = f.read()
with open(ROOT + "/HANDOFF.md", "w") as f:
    f.write(handoff_ckpt + handoff)
print("HANDOFF checkpoint prepended")

# 7) event
run_cmd(["python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
         "--token", TOKEN,
         "--event-id", "coord-poll-20261011215053-task09-done-task10-dispatched",
         "--task", "TASK-09", "--attempt", "1", "--status", "DONE",
         "--summary", "TESTER TASK-09 合入后验证 attempt-1 全 PASS（真 MySQL 60/44/迁移单头/SQLite 813/ruff/0 残留，独立复核一致）→ decision ACCEPT，TASK-09 ✅ DONE（main ca8730d）；TASK-10 前置齐备→派 2号 attempt-1（base ca8730d，端到端真实闭环，P0 最后一单，待 ACK）",
         "--evidence", "test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md；decision inbox/coordinator/TASK-09/post-merge-ca8730d-verify-acceptance-decision.md；派单 inbox/2号/TASK-10/attempt-1-dispatch.md",
         "--next", "下轮核 2号 TASK-10 ACK/开工→交付→机械核验→OCR→合入→P0 收口"])
print("event done")

# 8) release
run_cmd(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN])
print("released")