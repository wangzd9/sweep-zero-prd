import sys

ROOT = '/home/wang/work/doc/prd/rosbag-catalog-integration'
RUNTIME = '/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py'
import subprocess

res = subprocess.run(
    ['python3', RUNTIME, 'claim', '--project', ROOT, '--role', 'COORDINATOR',
     '--owner', 'cron-poll-coord-2235'], capture_output=True, text=True)
print('claim out:', res.stdout.strip(), res.stderr.strip())
token = res.stdout.strip().splitlines()[-1].strip()
if not token or 'error' in res.stdout.lower() or res.returncode != 0:
    print('CLAIM FAILED')
    sys.exit(1)

line = ("- 巡检：2026-10-10 22:35 +08:00（cron poll 14ae4556629a，真实 checked_at 22:35:53，ACTIVE，"
        "legacy_busy 空）：main HEAD `5f0124b`（=origin）不变；**2号 rework-5（codex 3 项：M-1 微秒精度/"
        "M-2 迁移边界 docstring/M-3 测试注释）22:30 ACK 后 IN_PROGRESS**——wt-04a 当前分支仍 "
        "`scene/task-06b-defect3-reconcile-replay`（HEAD `4e2158e` 已在 main 祖先链，22:25 后零 diff、"
        "无新文件、无在途 pytest/ocr 进程）；B 租约 `b-cron-rework5-20261010`（22:28:50 认领）在案，不接管；"
        "ACK 承诺新分支 `scene/task-06b-codex-rework5` 尚未建，**在途等待，不催单不重派**。强复审结果文件 "
        "`reviews/strongmodel/R2I-20261010-06-result.md` 仍不存在（pack 21:59 后零新 mtime，等用户手动触发，"
        "不自行调用付费模型）；TESTER 租约 `cron-tester-poll-2235` 为其巡检心跳非业务在途。03/05/06 聚合放行"
        "**仍卡强复审+rework-5 收口**：解锁路径=rework-5 交付→串行 OCR 增量→合入→TESTER 生产默认连接语义"
        "（CLIENT_FOUND_ROWS）复测→强模型增量复审（用户手动，附 codex 报告）→聚合 DONE→TASK-08。"
        "控制动作：claim→巡检记账→release，无状态变更、无新派单。")

p = ROOT + '/sessions/COORDINATOR.md'
s = open(p, encoding='utf-8').read()
anchor = '## 历史检查点（2026-10-10 22:20'
if line not in s:
    s = s.replace(anchor, line + '\n' + anchor, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('sessions updated')
else:
    print('sessions already has 22:35 checkpoint')

ev = subprocess.run(
    ['python3', RUNTIME, 'event', '--project', ROOT, '--role', 'COORDINATOR',
     '--token', token,
     '--event-id', 'coord-poll-2235-rework5-inprogress-20261010',
     '--task', 'TASK-06B', '--attempt', 'rework-5', '--status', 'IN_PROGRESS',
     '--summary', '巡检：2号 rework-5 ACK 后 IN_PROGRESS，wt-04a 未建新分支，等交付；强复审结果未返回',
     '--evidence', 'sessions/COORDINATOR.md',
     '--next', '下轮核 wt-04a 新分支/commit/回执与 R2I-20261010-06-result.md'],
    capture_output=True, text=True)
print('event out:', ev.stdout.strip(), ev.stderr.strip())

rl = subprocess.run(
    ['python3', RUNTIME, 'release', '--project', ROOT, '--role', 'COORDINATOR',
     '--token', token], capture_output=True, text=True)
print('release out:', rl.stdout.strip(), rl.stderr.strip())