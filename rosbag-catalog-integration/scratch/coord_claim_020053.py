import subprocess, json

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
owner = "cron-coord-poll-20261012-020053-t10v2"

# verify db3 row/topic counts + manifest topics count
out = subprocess.run([
    "python3", "-c",
    "import sqlite3, json\n"
    "con=sqlite3.connect('file:/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/publish/unassigned/slope/3723682575DE4F949438A1B87E_T10S22c76051fd384d17/rosbag2_0.db3?mode=ro',uri=True)\n"
    "print('topics_rows',con.execute('SELECT COUNT(*) FROM topics').fetchone()[0])\n"
    "print('messages_rows',con.execute('SELECT COUNT(*) FROM messages').fetchone()[0])\n"
    "m=json.load(open('/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/publish/unassigned/slope/3723682575DE4F949438A1B87E_T10S22c76051fd384d17/slice_manifest.json'))\n"
    "print('manifest_topics',len(m['slice']['topics']))",
], capture_output=True, text=True)
print(out.stdout, out.stderr)

r = subprocess.run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", owner], capture_output=True, text=True)
print("CLAIM rc=", r.returncode)
print(r.stdout[-800:])
print(r.stderr[-400:])