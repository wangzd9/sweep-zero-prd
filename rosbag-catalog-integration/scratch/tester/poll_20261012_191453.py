#!/usr/bin/env python3
# TESTER 5-min poll 2026-10-12 19:14:53: claim -> event+sessions heartbeat -> release
import json, subprocess, sys, pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-tester-poll-20261012-191453"
EVENT_ID = "tester-poll-20261012-191453-nochange"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    print("$", " ".join(str(a) for a in args))
    print(p.stdout.strip())
    if p.stderr.strip():
        print("STDERR:", p.stderr.strip())
    return p

p = sh(["python3", RUNTIME, "claim", "--project", str(ROOT), "--role", "TESTER", "--owner", OWNER])
if p.returncode != 0:
    print("CLAIM_FAILED rc=%d" % p.returncode)
    sys.exit(1)

token = None
for line in p.stdout.splitlines():
    line = line.strip()
    if line.startswith("token") or "token" in line.lower():
        print("token-line:", line)
lease = ROOT / "inbox/control/runtime/leases/TESTER.json"
if lease.exists():
    d = json.loads(lease.read_text())
    if d.get("owner") == OWNER:
        token = d.get("token")
        print("lease-owner-match, token from lease file")
if not token:
    print("NO_TOKEN: claim owner mismatch, abort writes")
    sys.exit(2)

beat = (
    "- 心跳：2026-10-12 19:14:53 +08:00（v2 5分钟巡检 preflight checked_at 2026-10-12T19:14:53+08:00 control=ACTIVE legacy_busy空；"
    "核：19:09:53 后 inbox/TESTER 与 test-receipts 零新增 TESTER 派单/回执（find -newermt 实测空）、origin/main 仍 502bf8e（fetch rc=0 实测，"
    "本地 main 30e55a3 仅 changelog 审计文档提交不触及被测面，07A 快照 caf385b+502bf8e 有效）；新他角色事实=协调者 07B OCR b5 "
    "scene_manual_revision_service.py 19:12 重启在途（ps 实测 pid 405860/405862 timeout 400，log 0 字节，属协调者门禁职责不接管）、"
    "leases C.json owner=C-cron-poll-*191353 属 C 在途不接管、TESTER 无残留租约 json；ps 无 TESTER 业务进程维持 IDLE；"
    "07A post-merge 回执 32/32 PASS 维持 TEST_REPORT_PENDING（TODO L34 14:50 已裁决 07A DONE，两记录并存如实申报）、"
    "07B attempt-1 维持 REVIEW_PENDING（HEAD f4bfcf2，OCR b5-b10 收口+裁决待协调者，独立验证为合入后下游门禁未派单不预占不启动）、"
    "T10 DONE 维持、TASK-11 生产门禁维持 BLOCKED 待用户授权。event %s 已落盘。claim/run/release 闭环。"
    "下一步=继续 5 分钟巡检；07B 合入后如派 TESTER 独立验证单再 ACK 固定快照开工，不扩需求）"
) % EVENT_ID

sess = ROOT / "sessions/TESTER.md"
content = beat + "\n" + sess.read_text()
sh(["python3", RUNTIME, "run", "--project", str(ROOT), "--role", "TESTER", "--token", token,
    "--", "python3", "-c", "import pathlib;pathlib.Path('%s').write_text('''%s''')" % (sess, beat)])
# run wrapper executes the inner command; verify file updated
if not sess.read_text().startswith(beat):
    # fallback: run via sh -c string
    sh(["python3", RUNTIME, "run", "--project", str(ROOT), "--role", "TESTER", "--token", token,
        "--", "sh", "-c", "python3 - <<'EOF'\nimport pathlib\np = pathlib.Path('%s')\nbeat = '''%s'''\nt = p.read_text()\nif not t.startswith(beat):\n    p.write_text(beat + chr(10) + t)\nprint('sessions-updated')\nEOF" % (sess, beat)])
print("sessions starts with beat:", sess.read_text().startswith(beat))

ev = ROOT / "inbox/events/TESTER"
ev.mkdir(parents=True, exist_ok=True)
evtext = (
    "# event %s\n\n- role: TESTER\n- owner: %s\n- checked_at: 2026-10-12T19:14:53+08:00\n"
    "- status: NO_CHANGE (idle poll)\n- facts:\n"
    "  - 19:09:53 后零新增 TESTER 派单/回执（find -newermt 实测空）\n"
    "  - origin/main 502bf8e 不变（fetch rc=0）；07A 快照 caf385b+502bf8e 有效\n"
    "  - 协调者 07B OCR b5 19:12 重启在途（pid 405860/405862，log 0 字节，不接管）\n"
    "  - leases: C.json 属 C 在途；TESTER 无残留 json 租约\n"
    "  - ps 无 TESTER 业务进程，维持 IDLE\n"
    "  - 07A 回执 TEST_REPORT_PENDING vs TODO 14:50 裁决 DONE：两记录并存如实申报待协调者核对\n"
    "- next: 继续 5 分钟巡检；07B 合入后如派独立验证单再 ACK 固定快照开工\n"
) % (EVENT_ID, OWNER)
sh(["python3", RUNTIME, "run", "--project", str(ROOT), "--role", "TESTER", "--token", token,
    "--", "sh", "-c", "cat > '%s/%s.md' <<'EOF'\n%sEOF" % (ev, EVENT_ID, evtext)])
print("event exists:", (ev / (EVENT_ID + ".md")).exists())

p = sh(["python3", RUNTIME, "release", "--project", str(ROOT), "--role", "TESTER", "--token", token])
print("RELEASE_RC=%d" % p.returncode)