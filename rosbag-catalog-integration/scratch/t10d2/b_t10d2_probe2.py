import json, statistics, sys
from pathlib import Path

WT = Path("/home/wang/.local/state/rosbag-scene/wt-04a-t10d2")
sys.path.insert(0, str(WT))
from app.scene.slope.bag_io import read_messages, read_topics  # noqa: E402
from app.scene.slope.cdr import decode_compressed_image, decode_image  # noqa: E402

ROOT = Path("/mnt/nas_backup/data_slice/1165414093/slope")


def dec(data, mt):
    try:
        if "CompressedImage" in mt:
            o, _ = decode_compressed_image(data, 0)
        elif "Image" in mt:
            o, _ = decode_image(data, 0)
        else:
            return None
    except Exception:
        return None
    s = o.header.stamp
    return s.sec * 1_000_000_000 + s.nanosec


rows = []
for bag in sorted(ROOT.iterdir()):
    if not bag.is_dir():
        continue
    topics = {t.name: t for t in read_topics(bag)}
    cam = next(n for n, t in topics.items() if n == "/bev/cam_front_8m_jpg")
    msgs = read_messages(bag, topic=cam)
    off = [m.timestamp_ns - dec(m.data, topics[cam].msgtype) for m in msgs if dec(m.data, topics[cam].msgtype) is not None]
    med = statistics.median(off)
    maxdev = max(abs(x - med) for x in off) / 1e6
    cov100 = sum(1 for x in off if abs(x - med) <= 100e6) / len(off)
    cov50 = sum(1 for x in off if abs(x - med) <= 50e6) / len(off)
    rows.append({
        "bag": bag.name[-16:],
        "n": len(off),
        "min_ms": min(off) / 1e6, "max_ms": max(off) / 1e6,
        "median_ms": med / 1e6,
        "maxdev_from_med_ms": maxdev,
        "cov@50ms": round(cov50, 3), "cov@100ms": round(cov100, 3),
    })
print(json.dumps(rows, ensure_ascii=False, indent=1))
print()
print("max of maxdev_from_med_ms over 7 bags:", max(r["maxdev_from_med_ms"] for r in rows), "ms")
print("min of cov@100ms over 7 bags:", min(r["cov@100ms"] for r in rows))