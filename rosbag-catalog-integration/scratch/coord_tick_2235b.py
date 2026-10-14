import subprocess, json

ROOT = '/home/wang/work/doc/prd/rosbag-catalog-integration'
RUNTIME = '/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py'
TOKEN = 'da879dc9ac99409da4f321a97fff2e84'

ev = subprocess.run(
    ['python3', RUNTIME, 'event', '--project', ROOT, '--role', 'COORDINATOR',
     '--token', TOKEN,
     '--event-id', 'coord-poll-2235-rework5-inprogress-20261010',
     '--task', 'TASK-06B', '--attempt', 'rework-5', '--status', 'IN_PROGRESS',
     '--summary', '巡检：2号 rework-5 ACK 后 IN_PROGRESS，wt-04a 未建新分支，等交付；强复审结果未返回',
     '--evidence', 'sessions/COORDINATOR.md',
     '--next', '下轮核 wt-04a 新分支/commit/回执与 R2I-20261010-06-result.md'],
    capture_output=True, text=True)
print('event:', ev.stdout.strip(), ev.stderr.strip())

rl = subprocess.run(
    ['python3', RUNTIME, 'release', '--project', ROOT, '--role', 'COORDINATOR',
     '--token', TOKEN], capture_output=True, text=True)
print('release:', rl.stdout.strip(), rl.stderr.strip())