import json, glob, os, sys
root = "/home/wang/work/doc/prd/rosbag-catalog-integration"
leases = root + "/inbox/control/runtime/leases"
if not os.path.isdir(leases):
    print("no leases dir at", leases)
else:
    for f in sorted(glob.glob(leases + "/*.json")):
        try:
            d = json.load(open(f))
            print(os.path.basename(f), json.dumps(d, ensure_ascii=False)[:400])
        except Exception as e:
            print(os.path.basename(f), "err", e)
print("--- control tree ---")
for f in glob.glob(root + "/inbox/control/**", recursive=True):
    if os.path.isfile(f):
        print(f.replace(root + "/", ""), os.path.getsize(f))