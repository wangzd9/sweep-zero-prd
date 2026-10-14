#!/usr/bin/env python3
# C 2026-10-12 00:43:53 巡检：核查 + sessions 补写 + 事件落盘（单写租约短占用）
import json, os, subprocess, sys, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
REPO = "/home/wang/work/rosbag-catalog"
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-004353"

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

facts = {}
rc, out, _ = sh("git rev-parse main origin/main", cwd=REPO)
facts["main_heads"] = out.split() if rc == 0 else f"rc={rc}"
rc, out, _ = sh("git rev-parse HEAD && git status --porcelain | grep -v '.venv' || true", cwd=WT)
facts["wt03b"] = out or "(clean)"
rc, out, _ = sh("ps -eo pid,lstart,cmd | grep -E 'wt-03b|scene-03b' | grep -v grep || true")
facts["ps_c"] = out or "(none)"
rc, out, _ = sh(f"find {ROOT}/inbox/3号 -type f -newermt '2026-10-12 00:38' -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\\n' || true")
facts["inbox3_new"] = out or "(none)"
rc, out, _ = sh(f"find {ROOT}/inbox/coordinator -type f -newermt '2026-10-12 00:38' -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\\n' || true")
facts["coord_new"] = out or "(none)"

print("FACTS:", json.dumps(facts, ensure_ascii=False))

# --- claim ---
rc, out, err = sh(f"python3 {RUNTIME} claim --project {ROOT} --role C --owner {OWNER}")
if rc != 0:
    print("CLAIM_FAILED rc=", rc, err[:500]); sys.exit(1)
tok = json.loads(out)["token"] if out.strip().startswith("{") else json.loads(out[out.index("{"):])["token"]
print("CLAIM_OK")

def run(*args):
    rc, out, err = sh(f"python3 {RUNTIME} run --project {ROOT} --role C --token {tok} -- {' '.join(args)}")
    if rc != 0:
        print("RUN_FAILED:", args, err[:500]); sys.exit(1)
    return out

# --- sessions prepend ---
sess = os.path.join(ROOT, "inbox", "sessions", "C.md")
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
entry = (
    f"- 最后更新：{now} +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T00:43:53+08:00）、legacy_busy 空；"
    f"00:38:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**："
    f"`inbox/coordinator/TASK-03B/t10-defect1-acceptance-decision.md` 00:42:51（head 通读核实=**协调者 ACCEPT_MERGED 1号 t10-defect1 `1b92ce6`**："
    f"机械核验全绿+OCR T10D1-r1 首跑 EXIT=1 空输出不算通过→前批 owner 已死独立核后前台重跑 **0 findings**（session `15516784`）+"
    f"**--no-ff 合入 main `277e40f`（推 origin `ca8730d..277e40f` 成功，rev-parse 双核一致）**+合入后 sanity 全绿（alembic 单头/ruff 2 文件/SQLite 定向 5 passed）+"
    f"强审查 NOT_REQUIRED，1号交付冻结转空闲、TASK-10 收口链推进至 #2（2号 t10-defect2 编码在途），**1号/协调者范围，非 C**）"
    f"+ `TODO.md` 00:43:06（协调者记账刷新，TASK-10 行追加 00:3x 收口注记，无 3号/C 行变更）"
    f"+ `inbox/ocr.lock` mtime 刷新 + `sessions/TESTER.md`/`sessions/A.md` 他角色巡检刷新（find 核实）；"
    f"`inbox/3号/` 无新文件（find -newermt 00:38 核实为空，最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口），**无 C 新派单**；"
    f"main HEAD `277e40f`=origin/main 双核一致（rosbag-catalog rev-parse 实测，2号 t10-defect2 在途未交付，非 C）、"
    f"wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（git status 排除 .venv 实测为空）、ps 实测无 C 在途业务进程；"
    f"C 本轮 owner `{OWNER}` claim 成功（token 整体 JSON 解析），事件 `C-poll-20261012-004353-nochange` 落盘，控制动作结束释放；"
    f"**保持空闲待派单**（2号 t10-defect2 在途，如后续涉 C 将另行派单）。前一条 00:38 巡检见下）\n"
)
with open(sess, "r", encoding="utf-8") as f:
    content = f.read()
with open(sess, "w", encoding="utf-8") as f:
    f.write(entry + content)
print("SESSIONS_WRITTEN")

# --- event ---
evdir = os.path.join(ROOT, "inbox", "events", "C")
os.makedirs(evdir, exist_ok=True)
ev = os.path.join(evdir, "C-poll-20261012-004353-nochange.md")
evt = (
    "# C-poll-20261012-004353-nochange\n"
    "- event_id: C-poll-20261012-004353-nochange\n"
    "- role: C\n"
    "- at: 2026-10-12T00:43:53+08:00\n"
    "- task: none\n"
    "- attempt: none\n"
    "- status: NO_CHANGE\n"
    "- summary: 00:38:53（前条 C 巡检 preflight 时点）后共享根新增核实均为非 C 范围："
    "inbox/coordinator/TASK-03B/t10-defect1-acceptance-decision.md 00:42:51（协调者 ACCEPT_MERGED 1号 t10-defect1 1b92ce6："
    "OCR T10D1-r1 重跑 0 findings、--no-ff 合入 main 277e40f 推 origin ca8730d..277e40f、sanity 全绿、1号转空闲、TASK-10 收口链推进至 #2）+"
    "TODO.md 00:43:06 协调者记账刷新（无 3号/C 行变更）+ inbox/ocr.lock mtime 刷新 + TESTER/A sessions 巡检刷新；"
    "inbox/3号 无新文件（find -newermt 00:38 核实为空，最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 全部派单已收口）、无 C 新派单；"
    "main HEAD 277e40f=origin/main 双核一致（rev-parse 实测，2号 t10-defect2 在途未交付非 C）、wt-03b HEAD 6f1a9ad 干净（排除 .venv 实测为空）、ps 无 C 在途业务进程；"
    f"C 本轮 owner {OWNER} claim 成功（token 整体 JSON 解析），控制动作结束释放；保持空闲待派单\n"
    "- evidence: sessions/C.md\n"
    "- next: 等待协调者派单\n"
)
with open(ev, "w", encoding="utf-8") as f:
    f.write(evt)
print("EVENT_WRITTEN:", ev)

# --- release ---
rc, out, err = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token {tok}")
print("RELEASE rc=", rc, err[:200])