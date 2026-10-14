#!/usr/bin/env python3
import os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
os.chdir(ROOT)

CP = '''## 2026-10-12 01:11 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-12T01:05:53+08:00：00:58 后唯一业务变化=TESTER E2E 复跑 attempt-1 第 1 跑收口 FAIL，定位**新缺口 #3（app 06B 域）**→协调者独立核验属实→派 2号 t10-defect3-publish-bounds）

- **TESTER E2E 复跑第 1 跑（01:02 ACK→01:03 驱动→01:05:37 收口）结论=FAIL（定位 #3 域 app 缺陷）**：固化驱动 `scratch/t10_e2e_reverify.py`（WT=main `a77aa45` 双核一致，真实 row19 袋、真实 VLM）——analyze **SUCCESS 143.6s/54 帧**；`derive_storage_offset=100381744ns` **非 None（#2 修复生效）**；writer 再切+publish 成功（10835 消息，子包 `T10Sb9fe892cbcbc4d6a`）；`/results` 200；**`/complete-scene` 409 INCOMPLETE**。
- **新缺口 #3 独立核验属实（协调者只读核 + 源码核，未改码）**：`scene_result_report_service.py:895` 区间身份复核 `lo,hi=int(start_ns),int(end_ns)` 取 per-slice 记录的 **header 采集域**边界（`scene_publish_service.py:274-275` 记录口径），而 db3 `messages.timestamp` 是**存储域**（writer `writer.py:88-99` 已按 `+storage_offset` 平移写入、`_validate_slice` bounds 同存储域通过）→ 已发布 db3 实际 max=`1787021479647655120` > header hi=`1787021479550464104`（超出 97.2ms≈offset 100.4ms−残余抖动，只读核 78 条 >hi 跨 16 topic、min 未越 lo）=**发布侧复核基准与 writer 侧基准不一致，真包 offset≠0 必 409**（P0 发布闭环断点，与 #1/#2 同性质；fixture offset=0 两域重合故未暴露）。
- **驱动 step5 NameError 已修（harness bug，非 AC 失败）**：`scratch/t10_e2e_reverify.py:385` 日志行误用未定义名 `child`（原变量 `child_uid`），publish 成功分支才触发——本次崩溃致 step5（bags/lineage+ALL_UNCHANGED 取证）未执行；协调者已改 `child`→`child_uid`。
- **派单/通知已落盘**：`inbox/2号/TASK-10/t10-defect3-publish-bounds.md`（**base `a77aa45`**，06B 域最小返修=per-slice 记录补存储域 `actual_start_ns/actual_end_ns` + `_verify_published_files` 改用存储域界 + **旧记录缺界 fail-closed 409**；禁碰 `source_service.py`/`writer.py`/04B/05）；`inbox/TESTER/TASK-10/e2e-reverify-notice-v1-fail-defect3.md`（本跑不写回执，等 #3 合入后复跑 v2 一次性取证全 AC，VLM 累计 ≤2 袋，防双跑）。
- **角色占用**：B=待领 t10-defect3（PENDING_ACK）；TESTER=第 1 跑已收口转等 #3 合入（复跑 v2 前不重启驱动）；A/C 空闲（C 01:03 nochange 心跳）；legacy_busy 空。
- **main 不变 `a77aa45`**（=origin 双核）；OCR 零代码面不适用（等 #3 交付）；`ocr.lock`/`coordinator.lock` 本轮 claim `cron-coord-poll-20261012-010553` 存活。
- **门禁**：TASK-10 维持 🏃 RUNNING（#3 未合入、E2E 复跑 v2 未全绿不得写 DONE）；#3 收口链=2号交付→机械核验→串行 OCR（§3.6 预检）→合入 main（核 base 漂移零冲突）→TESTER 复跑 v2 全绿→**TASK-10 DONE→P0 收口**；TASK-11 生产维持未放行；TASK-07/12/13/14/15 维持 DEFERRED 不扩。
- 本轮控制动作：claim（`cron-coord-poll-20261012-010553`）→巡检核查（find -newermt 00:57 发现 TESTER 01:02 ACK+驱动 01:03-05 产物+第 1 跑 409）→独立核验（evidence json 复核/已发布 db3 只读核 78 条越界/writer.py 88-99+114-142 存储域核/report_service:882-900 header 域核/git log -L 定位 c67600d 区间块）→驱动 step5 NameError 修复→派 2号 #3 + 通知 TESTER + 本检查点 + TODO + event→release。
- **下一步**：核 2号 t10-defect3 ACK/交付（交付即机械核验→串行 OCR→合入 main 核 base 漂移）→TESTER 复跑 v2 全绿→**TASK-10 DONE→P0 收口**（最终 HANDOFF/TODO 停止派发）。
'''

EV = '''{
  "event_id": "coord-poll-20261012-010553-t10-e2e-fail-defect3-dispatched",
  "occurred_at": "2026-10-12T01:11:45+08:00",
  "recorded_at": "2026-10-12T01:11:45+08:00",
  "role": "COORDINATOR",
  "task": "TASK-10",
  "attempt": "e2e-reverify-after-merges/1",
  "status": "REWORK_DISPATCHED",
  "summary": "TESTER E2E 复跑第1跑 FAIL：#1/#2 修复真链生效（offset 100381744ns 非 None、publish 成功、/results 200、VLM analyze SUCCESS 143.6s/54 帧、原包 ALL_UNCHANGED 独立补核 7 文件），断链=/complete-scene 409 INCOMPLETE（新缺口 #3：report_service:895 区间复核用 header 采集域界 vs db3 存储域 timestamp，超界 97.2ms，已发布 db3 只读核 78 条越界属实）+ 驱动 step5 NameError（harness bug 已修）。裁决归属 06B 域→回派 2号 t10-defect3-publish-bounds（base a77aa45，per-slice 补存储域 actual 界+复核改用+旧记录缺界 fail-closed 409）；TESTER 等 #3 合入后复跑 v2（VLM 累计 ≤2 袋）",
  "evidence": "test-receipts/TEST-TASK10-e2e-reverify/attempt-1.md + inbox/2号/TASK-10/t10-defect3-publish-bounds.md + inbox/TESTER/TASK-10/e2e-reverify-notice-v1-fail-defect3.md + scratch/t10/t10-e2e.json",
  "next": "2号 ACK/交付→机械核验→串行 OCR→合入 main→TESTER 复跑 v2→TASK-10 DONE→P0 收口"
}
'''

# sessions/COORDINATOR.md: prepend after first header line (newest-first convention)
s = open("sessions/COORDINATOR.md", encoding="utf-8").read()
first_nl = s.index("\n")
s = s[:first_nl + 1] + CP + s[first_nl + 1:]
open("sessions/COORDINATOR.md", "w", encoding="utf-8").write(s)

# HANDOFF.md: insert CP after line 1 (first '## ...' line is header line 1 = current checkpoint title line? verify pattern from prior script: lines[0] + CP + rest)
h = open("HANDOFF.md", encoding="utf-8").read()
lines = h.split("\n", 1)
rest = lines[1] if len(lines) > 1 else ""
open("HANDOFF.md", "w", encoding="utf-8").write(lines[0] + "\n" + CP.strip("\n") + "\n\n" + rest)

import hashlib, json
# event: write by sha256 filename convention (events/COORDINATOR/<hash>.json)
hname = hashlib.sha256(EV.encode()).hexdigest()
path = os.path.join("events", "COORDINATOR", hname + ".json")
if not os.path.exists(path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(EV)

print("CHECKPOINT_WRITTEN")
print("EVENT", hname)