#!/usr/bin/env python3
import subprocess, json, shlex, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-175553"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# 1. claim
rc, out, err = sh(f"python3 {RUNTIME} claim --project {ROOT} --role COORDINATOR --owner {OWNER}")
print("claim rc:", rc, out.strip()[:200], err.strip()[:200])
if rc != 0 or not out:
    sys.exit("claim failed")
d = json.loads(out)
if not d.get("claimed"):
    print("NOT CLAIMED:", out)
    sys.exit(2)
TOKEN = d["token"]
json.dump(d, open(f"{ROOT}/scratch/coord-poll-175553-claim.json", "w"), indent=2)

# 2. 重读核实（run 内再核一次，防旧 token 复用前状态漂移）
head = sh(f"git -C /home/wang/work/rosbag-catalog rev-parse HEAD")[1].strip()
origin = sh(f"git -C /home/wang/work/rosbag-catalog rev-parse origin/main")[1].strip()
assert head == origin, (head, origin)
recv = sh(f"ls -1 {ROOT}/receipts/TASK-08/")[1].strip().splitlines()
wt_head = sh("git -C /home/wang/.local/state/rosbag-scene/wt-04a-t08c rev-parse --short HEAD")[1].strip()
mtime = sh("stat -c '%y' /home/wang/.local/state/rosbag-scene/wt-04a-t08c/tests/test_bag_cleanup_concurrency.py")[1].strip()
print(f"head={head[:7]} origin={origin[:7]} receipts={recv} wt_head={wt_head} lastwrite={mtime}")

cp = f"""## 2026-10-11 17:56 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T17:55:53+08:00：17:50 后零业务交付，2号 t08c-1 编码继续活跃）
- **17:50 后零业务交付**：main HEAD `{head[:7]}`（= origin/main，rev-parse 双核一致，top1=c3-1 合入 17:02 已在案）；17:50:53 后共享根业务目录（receipts/test-receipts/inbox/events/reviews/decision）**零新增**（find -newermt 核实，无新回执/派单/事件）。
- **2号 t08c-1（C1/C2 秒精度专项）编码继续推进（活性良好，不催单不接管）**：`wt-04a-t08c` 最新业务写入 `tests/test_bag_cleanup_concurrency.py` **{mtime[:19]}**（较 17:50 检查点的 17:48:51 更新）；HEAD 仍 `{wt_head}` 无 commit、`receipts/TASK-08/` 仍仅 attempt-1 + c3-lineage-c3-1 两份**无 t08c 交付回执**；当前 4 业务文件改动（bag_cleanup_service/catalog_ingest/clone 脚本/并发测试）+ `test_t08c_probe8.py` 新 probe 夹具未 commit。
- **角色占用**：B=t08c-1 RUNNING（编码中）；A/C/TESTER 空闲（C 17:48 nochange 心跳为最新例行）；leases 目录空无在途持有者；`ocr.lock`/`coordinator.lock` 无他角色在途；ps 无业务进程（仅 wxocr 桌面）。
- **门禁**：生产启用/真实样本（TASK-09/10/11）维持未放行；TASK-08 收口 1/2（c3-1 已合入 `98f6c88`），剩 t08c-1 交付→机械核验（含 C1/C2 逐修复点覆盖核对）→串行 OCR 增量（app 行为面）→合入→9 红文件全绿复核→08 DONE→TASK-10 候选重算。
- 本轮控制动作：claim（{OWNER}）→巡检核查（rev-parse 双核/find -newermt/wt-04a-t08c mtime+status/receipts/leases/ps 复核）→append 检查点+event→release，**无新派单、无合入、无 OCR、无状态变更**。
- **下一步**：等 2号 t08c-1 交付信号（wt-04a-t08c 新 commit/回执 `receipts/TASK-08/`）→机械核验→串行 OCR 增量→合入→9 红文件全绿复核→TASK-08 DONE；若交付前再次连续多轮零活动则恢复停滞告警口径，不自动接管。
"""

run_cp = (f"python3 {RUNTIME} run --project {ROOT} --role COORDINATOR --token {TOKEN} -- "
          + " ".join(shlex.quote(x) for x in ["python3", "-c",
          f"open('{ROOT}/sessions/COORDINATOR.md','a').write({json.dumps(cp)})"]))
rc, out, err = sh(run_cp)
print("cp run rc:", rc, out[-150:], err[-150:])

ev = (f"python3 {RUNTIME} event --project {ROOT} --role COORDINATOR --token {TOKEN} "
      f"--event-id coord-poll-20261011-175553-t08c1-encoding-active-nochange "
      f"--task TASK-08 --attempt 1 --status RUNNING "
      f"--summary 17:50 后零业务交付：main 98f6c88=origin 双核一致、共享根业务目录零新增；2号 t08c-1 编码继续（test_bag_cleanup_concurrency.py {mtime[:19]} 活跃写入，4 文件+probe 未 commit，无回执）；A/C/TESTER 空闲；无新派单/无 OCR "
      f"--evidence sessions/COORDINATOR.md "
      f"--next 等 t08c-1 交付后机械核验+串行 OCR 增量+合入+9 红文件全绿复核")
rc, out, err = sh(ev)
print("event rc:", rc, out[-150:], err[-150:])

rc, out, err = sh(f"python3 {RUNTIME} release --project {ROOT} --role COORDINATOR --token {TOKEN}")
print("release rc:", rc, out[:150], err[:150])
print("DONE")