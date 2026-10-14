import json, subprocess
ROOT='/home/wang/work/doc/prd/rosbag-catalog-integration'
RUN='/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py'
OWNER='C-cron-poll-20261012-001353'
out = subprocess.run(['python3',RUN,'claim','--project',ROOT,'--role','C','--owner',OWNER],capture_output=True,text=True)
tok = json.loads(out.stdout).get('token') if out.stdout.strip().startswith('{') else None
assert out.returncode==0 and tok, f"claim failed: {out.stdout} {out.stderr}"
line = ("- 最后更新：2026-10-12 00:13 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T00:13:53+08:00）、legacy_busy 空；"
"00:08:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**：`inbox/1号/TASK-03B/t10-defect1-source-ready-ack.md`（find -newermt 23:50 核实=1号 00:1x ACK ACCEPTED，协调者 00:07 回派的 source_status DISCOVERED→READY 最小返修单 owner 1号，收件箱在 1号 目录，非 C）"
"+ `inbox/2号/TASK-06B/t10-defect2-storage-offset-ack.md`（2号 ACK，00:10 条已核，非 C）+ 各角色 sessions 巡检刷新；"
"`inbox/3号/` 无新文件（ls 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口），**无 C 新派单**；"
"main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 实测，1号 t10-defect1/2号 t10-defect2 返修均未合入，非 C）、"
"wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（git status 实测仅 `?? .venv`）、ps 实测无 C 在途业务进程；"
"C 本轮 owner `"+OWNER+"` claim 成功（token 整体 JSON 解析），事件 `C-poll-20261012-001353-nochange` 落盘，控制动作结束释放；**保持空闲待派单**（1号/2号 两笔 TASK-10 返修在途，如后续涉 C 将另行派单）。前一条 00:10 巡检见下）\n")
ev = ("# C poll no-change 2026-10-12 00:13\n\n"
f"- checked_at: 2026-10-12T00:13:53+08:00（preflight，cron poll f01517c16f2f）\n- owner: {OWNER}\n"
"- 无 C 新派单；00:08:53 后共享根新增=1号 t10-defect1 ACK + 2号 t10-defect2 ACK + 各角色 sessions 刷新，均非 C 范围\n"
"- main `ca8730d`=origin/main；wt-03b HEAD `6f1a9ad` 干净（仅 ?? .venv）；无 C 在途业务进程\n"
"- 保持空闲待派单，未进行业务动作\n")
def run(*args):
    r = subprocess.run(list(args),capture_output=True,text=True)
    assert r.returncode==0, f"run failed: {r.stdout} {r.stderr}"
    return r
run('python3',RUN,'run','--project',ROOT,'--role','C','--token',tok,'--','python3','-c',
    "import sys,io; p='sessions/C.md'; s=open(p).read(); l=sys.stdin.read(); i=s.find('- 最后更新：2026-10-12 00:10 +08:00'); assert i>=0; open(p,'w').write(s[:i]+l+s[i:])",
    )
