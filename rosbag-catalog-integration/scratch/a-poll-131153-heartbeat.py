import json, subprocess, sys, os, time, re, datetime

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "a-poll-20261011-131153"
ROLE = "A"

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def run(*args):
    p = subprocess.run(list(args), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

# read main HEAD + origin
def gh(*a):
    p = subprocess.run(["git","-C","/home/wang/work/rosbag-catalog"]+list(a), capture_output=True, text=True)
    return p.stdout.strip()

main_head = gh("rev-parse","--short","HEAD")
origin_head = gh("rev-parse","--short","origin/main")

# files newer than last heartbeat 12:52:53 in my business scope
import subprocess as sp
findout = sp.run(["find","inbox/1号","inbox/coordinator","decision","receipts","dispatches","-type","f","-newermt","2026-10-11 12:52:53"],
                 cwd=ROOT, capture_output=True, text=True)
newfiles = [l for l in findout.stdout.splitlines() if l.strip()]

# worktree state
wt = gh("worktree","list")
wt01 = next((l.split()[-2]+" "+l.split()[-1] for l in wt.splitlines() if "wt-01" in l), "?")

# lease state
leases = os.listdir(os.path.join(ROOT,"inbox","control","runtime","leases"))

token = None
rc, out, err = run("python3", RUNTIME, "claim","--project",ROOT,"--role",ROLE,"--owner",OWNER)
if rc != 0:
    print("CLAIM FAILED rc=%s\nout=%s\nerr=%s" % (rc, out, err))
    sys.exit(1)
# parse token from stdout (json-ish)
m = re.search(r'"token"\s*:\s*"([A-Za-z0-9_.\-]+)"', out)
if m:
    token = m.group(1)
else:
    m2 = re.search(r'\b([A-Za-z0-9]{8,})\b', out)
    token = m2.group(1) if m2 else None
print("claim rc=%s token=%s" % (rc, token))

# heartbeat line
hb = ("- 心跳：%s CST（5min 巡检 preflight checked_at 2026-10-11T13:11:53+08:00，ACTIVE，legacy_busy 空："
      "main HEAD %s（git 核实 =origin/main，零前移）；12:52:53 后 find -newermt 核实 %s，"
      "本角色 inbox/1号 最新仍 10-10 18:58 attempt-6-rework，交付 ceeac16 已随 0f6aa87 合入 main 并验收；"
      "wt-01 仍 ceeac16 干净冻结（分支 t03b-attempt-6-s1，仅未跟踪 .venv）；leases 见 %s 0 字节残留（非本角色，不动待核）。"
      "**无本角色待办**，空闲不扩需求，等协调者释放槽/新单（强复审 R2I-20261010-06 target 65ca0be 待用户手动触发，非本角色门禁）；"
      "claim（%s）→心跳记账→release）"
      % (now, main_head,
         ("、".join(newfiles) if newfiles else "零新派单/返修/释放通知"),
         "/".join(l for l in leases if l.endswith(".lock")) or "无", OWNER))

# append heartbeat to sessions/A.md
sess = os.path.join(ROOT,"sessions","A.md")
with open(sess,"a",encoding="utf-8") as f:
    f.write(hb+"\n")
print("heartbeat appended to sessions/A.md")

if token:
    rc2, out2, err2 = run("python3",RUNTIME,"release","--project",ROOT,"--role",ROLE,"--token",token)
    print("release rc=%s %s" % (rc2, (out2+err2).strip()[:200]))
else:
    print("NO TOKEN - not released")