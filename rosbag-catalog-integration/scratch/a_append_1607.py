import os
root = "/home/wang/work/doc/prd/rosbag-catalog-integration"
src = open(os.path.join(root, "scratch/a-heartbeat-1607.md")).read().rstrip("\n") + "\n"
path = os.path.join(root, "sessions/A.md")
with open(path, "a") as f:
    f.write(src)
print("appended", len(src), "chars to", path)