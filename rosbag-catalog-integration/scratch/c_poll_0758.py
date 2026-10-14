import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-075853"

def run(args):
    r = subprocess.run([sys.executable, RUNTIME] + args, capture_output=True, text=True)
    return r

# claim (parse full JSON, never tail)
r = run(["claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc", r.returncode)
tok = None
for line in r.stdout.strip().splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            d = json.loads(line)
            tok = d.get("token") or d.get("lease", {}).get("token")
        except Exception:
            pass
print("token found:", bool(tok))

ENTRY = "- 最后更新：2026-10-12 08:00 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T07:58:53+08:00）、legacy_busy 空；07:49:57（前条 C 巡检写入）后共享根唯一新增=`HANDOFF.md` 07:55（head 核实=协调者 07:55:53 巡检检查点 r56：main `453da0c` 双核一致、**新事实=未归属 T11 本地栈驱动第 7 跑 07:56:44 起 07:57:22 FAIL**（1d explicit 复用已终结 run 后 3_claim 拒绝，又一失败形态；launcher pid 已退出、维持只观察不接管、无派单/ACK 认领、TASK-11 门禁维持未放行，**协调者范围非 C**））；`inbox/3号/`（最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，C 名下全部派单已收口）与 `inbox/coordinator/` find -newermt 07:49 实测均无新文件、**无 C 新派单**；main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog fetch rc=0 后 rev-parse 本轮实测，非 C 交付）、wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/task-03b/t03b 命中 0）、leases 仅 `COORDINATOR.json` 在途（236 字节 07:59，协调者 r56 巡检业务，非 C 不接管）、C.lock/TESTER.lock 0 字节历史空文件；C 本轮 owner `C-cron-poll-20261012-075853` claim 成功（token 整体 JSON 解析），条目先落 scratch 临时文件再独立 python prepend（计算/校验在前、共享文件最后写入、写后首行/行数/次行签名验证），事件 `C-poll-20261012-075853-nochange` 落盘后 release；**保持空闲待派单**（P0 已收口停止派发、TASK-11 生产门禁待用户授权、T11 未归属驱动第 7 跑 FAIL 不涉 C）。前一条 07:49 巡检见下\n"

sessions = os.path.join(ROOT, "sessions/C.md")
with open(sessions, "r", encoding="utf-8") as f:
    content = f.read()
old_lines = content.splitlines()
# dry-run on temp target first
new_content = ENTRY + content
tmp = "/home/wang/.hermes/cache/scratch/c_sessions_dryrun.md"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(new_content)
nl = new_content.splitlines()
assert nl[0].startswith(ENTRY.strip().split("\n")[0][:40]), "first line signature mismatch"
assert len(nl) == len(old_lines) + 1, f"line count {len(nl)} != {len(old_lines)}+1"
assert nl[-1] == old_lines[-1], "last line not preserved"
print("dry-run ok:", len(old_lines), "->", len(nl))
if tok:
    with open(sessions, "w", encoding="utf-8") as f:
        f.write(new_content)
    with open(sessions, "r", encoding="utf-8") as f:
        check = f.read().splitlines()
    assert check[0].startswith("- 最后更新：2026-10-12 08:00 +08:00"), "write verify failed"
    print("write ok, lines:", len(check))
    r = run(["event", "--project", ROOT, "--role", "C", "--token", tok,
             "--event-id", "C-poll-20261012-075853-nochange", "--task", "IDLE", "--attempt", "1",
             "--status", "NO_CHANGE",
             "--summary", "P0 收口后常规空转：无 C 新派单；唯一新增 HANDOFF 07:55=协调者 r56 检查点（T11 未归属驱动第 7 跑 FAIL，非 C 范围）",
             "--evidence", "sessions/C.md 08:00 条目",
             "--next", "继续 5 分钟巡检等待派单"])
    print("event rc", r.returncode, r.stdout[-200:], r.stderr[-200:])
    r = run(["release", "--project", ROOT, "--role", "C", "--token", tok])
    print("release rc", r.returncode)
else:
    print("no token, sessions NOT written")