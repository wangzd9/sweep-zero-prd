import json, os, sys, subprocess

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
TOKEN = "1b1d1bdeb8f143afbea0d6df4ac37d77"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"

def run(*args):
    r = subprocess.run(["python3", RUNTIME] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        print("RUN FAIL:", r.stdout[-800:], r.stderr[-800:])
        sys.exit(1)
    return r.stdout

# 1) prepend checkpoint into sessions/COORDINATOR.md (raw text file)
ckpt_path = os.path.join(ROOT, "scratch", "coord-ckpt-201553-body.md")
sess = os.path.join(ROOT, "sessions/COORDINATOR.md")
run("run", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
    "--", "bash", "-c",
    "cat %s %s > %s.new && mv %s.new %s" % (ckpt_path, sess, sess, sess, sess))

# 2) event
run("event", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
    "--event-id", "coord-poll-20261011-201553-nochange",
    "--task", "none", "--attempt", "none", "--status", "NO_CHANGE",
    "--summary", "20:12 后零业务变化：main 0a8ca8a=origin 双核一致；20:10:53 后共享根业务目录零新增（find -newermt），仅 B/C 例行 IDLE 心跳（20:09/20:14）；A/B/C/TESTER 全空闲；ocr/coordinator lock 0 字节无在途持有者；TASK-08 DONE 已收口（19:46）；TASK-10 维持 WAITING（09 BLOCKED 待用户授权真实坡道样本/VLM）；生产门禁未放行",
    "--evidence", "sessions/COORDINATOR.md",
    "--next", "维持5分钟巡检；等 TASK-09 授权后重算 TASK-10 派单")

print("OK")