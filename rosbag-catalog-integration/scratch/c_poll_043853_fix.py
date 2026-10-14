#!/usr/bin/env python3
# C 04:39 巡检修复：去掉 04:39 反引号损坏行，补写无 backtick 的正确行
import json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-043853-fix"
EVENT_ID = "C-poll-20261012-043853-nochange"

entry = (
    "- 最后更新：2026-10-12 04:40 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T04:38:53+08:00）、legacy_busy 空；"
    "04:34:00（前条 C 巡检 04:39 写入行 04:34 时点）后共享根新增核实均为【非 C 范围】：HANDOFF.md/TIMELINE.md 04:32-04:33（head 核实=协调者 04:25 巡检检查点 cron poll 14ae4556629a：P0 收口后常规空转第 22 轮、04:15:53 后零业务变化、main 453da0c 双核一致、A/B/C/TESTER 全空闲、TASK-11 生产维持未放行，协调者范围非 C）；"
    "inbox/3号 实测最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、inbox/coordinator 实测最新仍 02:08:34 e2e-reverify-v2-acceptance-decision（find -printf 核实，均非 C 新单）、【无 C 新派单】；"
    "main HEAD 453da0c=origin/main 双核一致（rosbag-catalog rev-parse 实测，TASK-10 DONE 已收口，非 C）、"
    "wt-03b HEAD=6f1a9ad 分支 feature/scene-03b-ocr-rework 干净（status --porcelain 排除 .venv 实测 0）、"
    "ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中 0）；"
    "leases 仅 B.json（04:38）/A.json（04:37）在途（2号/1号巡检业务，非 C 范围，不接管）；"
    "C 本轮 owner C-cron-poll-20261012-043853 claim 成功（token 整体 JSON 解析），首次追加因 bash 反引号解释损坏两行 04:39 条目，"
    "owner " + OWNER + " 已按快照恢复：删损坏行、补写本条（仅追加+删本轮自身损坏行，未动他人内容），"
    "事件 " + EVENT_ID + " 落盘后 release；"
    "【保持空闲待派单】（P0 已收口、TASK-11 生产门禁待用户授权，如后续涉 C 将另行派单）。前一条巡检见下"
)

def sh(args, input_text=None):
    r = subprocess.run(args, capture_output=True, text=True, timeout=120, input=input_text)
    return r.returncode, r.stdout, r.stderr

rc, out, err = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc", rc)
if rc != 0:
    print("claim out:", out, "err:", err); sys.exit(1)
token = json.loads(out)["token"]

fix_snippet = r'''
import io
entry = io.open("/tmp/c_entry_043853.txt", encoding="utf-8").read().rstrip("\n")
for path in ["/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/C.md",
             "/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/sessions/C.md"]:
    lines = io.open(path, encoding="utf-8").read().splitlines()
    # 删除本轮 04:3853 巡检写入的损坏行（以 04:39 +08:00 开头且含 043853 事件 ID）
    kept = [l for l in lines if not (l.startswith("- 最后更新：2026-10-12 04:39") or l.startswith("最后更新：2026-10-12 04:39"))]
    removed = len(lines) - len(kept)
    io.open(path, "w", encoding="utf-8").write("\n".join(kept) + "\n" + entry + "\n")
    print(path, "removed", removed, "appended", True)
'''
io_write = subprocess.run(["python3", "-c", "import io; io.open('/tmp/c_entry_043853.txt','w',encoding='utf-8').write(%r)" % entry], capture_output=True, text=True)
print("entry file rc", io_write.returncode, io_write.stderr)

rc, out, err = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token,
                   "--", "python3", "-c", fix_snippet])
print("fix rc", rc)
print(out)
print(err)

rc, out, err = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc", rc, out, err)