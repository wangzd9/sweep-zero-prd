import json, subprocess, sys
ROOT='/home/wang/work/doc/prd/rosbag-catalog-integration'
RUN='/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py'
OWNER='C-cron-poll-20261012-001353'
out = subprocess.run([sys.executable,RUN,'claim','--project',ROOT,'--role','C','--owner',OWNER],capture_output=True,text=True)
data = json.loads(out.stdout)
tok = data['token']
line = open(ROOT+'/scratch/c_001353_line.txt').read()
ins = "import sys;p='sessions/C.md';s=open(p).read();l=open('/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_001353_line.txt').read();i=s.find('- 最后更新：2026-10-12 00:10 +08:00');assert i>=0;open(p,'w').write(s[:i]+l+s[i:])"
r = subprocess.run([sys.executable,RUN,'run','--project',ROOT,'--role','C','--token',tok,'--',sys.executable,'-c',ins],capture_output=True,text=True)
assert r.returncode==0, f"run1 failed: {r.stdout} {r.stderr}"
ev = "cp /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_001353_event.txt /home/wang/work/doc/prd/rosbag-catalog-integration/events/C/C-poll-20261012-001353-nochange.md"
r2 = subprocess.run([sys.executable,RUN,'run','--project',ROOT,'--role','C','--token',tok,'--','sh','-c',ev],capture_output=True,text=True)
assert r2.returncode==0, f"run2 failed: {r2.stdout} {r2.stderr}"
rel = subprocess.run([sys.executable,RUN,'release','--project',ROOT,'--role','C','--token',tok],capture_output=True,text=True)
print("release rc", rel.returncode, rel.stdout.strip()[:80], rel.stderr.strip()[:120])
