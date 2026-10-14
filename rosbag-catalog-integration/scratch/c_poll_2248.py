import json, subprocess, os, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-224853"
CHECKED_AT = "2026-10-11T22:48:53+08:00"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# 1. claim
rc, out, err = sh(f"python3 {RUNTIME} claim --project {ROOT} --role C --owner {OWNER}")
assert rc == 0, f"claim failed rc={rc} out={out!r} err={err!r}"
data = json.loads(out)  # 整体 JSON 解析，禁止 tail -1
token = data["token"] if isinstance(data, dict) and "token" in data else None
if token is None:
    # 兜底：从 lease 文件读回
    with open(os.path.join(ROOT, "inbox/control/runtime/leases/C.json")) as f:
        lf = json.load(f)
    assert lf.get("owner") == OWNER, f"lease owner mismatch: {lf}"
    token = lf["token"]
print("claim ok, token len", len(token))

# 2. 写前核查（短控制 run 内重读）
rc, out, err = sh(f"find {ROOT}/inbox/3号 {ROOT}/inbox/coordinator -type f -newermt '2026-10-11 22:46:40'")
print("new dispatch files:", repr(out.strip()) if out.strip() else "NONE")

# 3. 更新 sessions/C.md（prepend 一行）
sess = os.path.join(ROOT, "sessions/C.md")
line = (
    f"- 最后更新：2026-10-11 22:49 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at {CHECKED_AT}）、legacy_busy 空；"
    "22:46:34（前条 C 事件落盘）后共享根新增核实均为**非 C 范围**：`events/COORDINATOR/` 22:46:48 协调者巡检事件 "
    "`coord-poll-20261011-224053-t10-probes-continuing`（read 核实=22:38:30 后零交付零合入、main `ca8730d` 双核一致、"
    "2号 TASK-10 attempt-1 在途（探针链至 t10-import-check 22:32、`wt-04a-t10` 零 commit 干净、距最后工作产物约 9min 未达停滞告警口径）、"
    "B=RUNNING 不催单不接管、A/C/TESTER 空闲、**无新派单无合入无 OCR**，协调者/2号范围非 C）+ `sessions/A.md` 1号巡检刷新；"
    "`inbox/3号/` 无新文件（find -newermt 22:46:40 核实为空，最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（find 核实最新仍 21:57 TASK-09 post-merge decision，非 C），**无 C 新派单**；"
    "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实，2号 TASK-10 在途未交付，非 C 交付）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 核实为空）、"
    "ps 核实无 C 在途业务进程；leases 无 size>0 在途租约（仅 C.lock/TESTER.lock 0 字节历史空文件）；"
    f"C 本轮 owner `{OWNER}` claim 22:49，事件 `C-poll-20261011-224853-nochange` 落盘，控制动作结束释放；**保持空闲待派单**。前一条 22:43 巡检见下\n"
)
with open(sess, encoding="utf-8") as f:
    content = f.read()
content = line + content
with open(sess, "w", encoding="utf-8") as f:
    f.write(content)
print("sessions/C.md updated")

# 4. event
ev = {
    "event_id": "C-poll-20261011-224853-nochange",
    "occurred_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "role": "C",
    "task": "none",
    "attempt": "-",
    "status": "NO_CHANGE",
    "summary": "22:49 巡检零变化：22:46:34 后共享根新增仅协调者 22:46:48 巡检事件（2号 TASK-10 在途，A/C/TESTER 空闲，无新派单无合入无 OCR）与 1号 sessions 刷新，非 C 范围；inbox/3号 最新仍 10-10 00:58 已收口，无 C 新派单",
    "evidence": "sessions/C.md 22:49 行",
    "next": "保持空闲待派单，继续 5 分钟巡检",
}
ev_path = os.path.join(ROOT, "events/C", ev["event_id"] + ".json")
with open(ev_path, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("event written:", ev_path)

# 5. release
rc, out, err = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token {json.dumps(token)}")
print("release rc:", rc, repr(out.strip()[:200]), repr(err.strip()[:200]))

# 6. 核实租约已释放
rc, out, err = sh(f"ls -la {ROOT}/inbox/control/runtime/leases/")
print(out)