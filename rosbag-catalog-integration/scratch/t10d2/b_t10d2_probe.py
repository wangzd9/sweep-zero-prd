"""t10-defect2 探针：7 条真实 slope 袋逐帧 (storage_ns - header_ns) 分布。

只读 NAS；输出每袋帧数、offset min/max/mode/median/带宽/占比证据。
"""
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

WT = Path("/home/wang/.local/state/rosbag-scene/wt-04a-t10d2")
sys.path.insert(0, str(WT))

from app.scene.slope.bag_io import BagIoError, read_messages, read_topics  # noqa: E402
from app.scene.slope.cdr import decode_compressed_image, decode_image  # noqa: E402

ROOT = Path("/mnt/nas_backup/data_slice/1165414093/slope")
bags = sorted(p for p in ROOT.iterdir() if p.is_dir())

CANDIDATES = [
    "/camera/front/image",
    "/camera/front/rgb/image_raw",
    "/front_cam/image_raw",
    "/camera/front",
]


def find_cam_topic(topics):
    names = list(topics)
    for c in CANDIDATES:
        if c in topics:
            return c
    # fallback: any Image/CompressedImage topic with max count
    imgs = [
        (n, t.msgtype, t.message_count)
        for n, t in topics.items()
        if "Image" in t.msgtype
    ]
    if not imgs:
        return None
    imgs.sort(key=lambda x: -x[2])
    return imgs[0][0]


def decode_header_ns(data, msgtype):
    try:
        if "CompressedImage" in msgtype:
            obj, _ = decode_compressed_image(data, 0)
        elif "Image" in msgtype:
            obj, _ = decode_image(data, 0)
        else:
            return None
    except Exception:
        return None
    stamp = obj.header.stamp
    if not isinstance(stamp.sec, int) or not isinstance(stamp.nanosec, int):
        return None
    return stamp.sec * 1_000_000_000 + stamp.nanosec


out = []
for bag in bags:
    try:
        topics = {t.name: t for t in read_topics(bag)}
    except BagIoError as e:
        out.append({"bag": bag.name, "error": str(e)})
        continue
    cam = find_cam_topic(topics)
    if cam is None:
        out.append({"bag": bag.name, "error": "no image topic", "topics": list(topics)})
        continue
    msgs = read_messages(bag, topic=cam)
    offsets = []
    dec_fail = 0
    for m in msgs:
        h = decode_header_ns(m.data, topics[cam].msgtype)
        if h is None:
            dec_fail += 1
            continue
        offsets.append(m.timestamp_ns - h)
    if not offsets:
        out.append({"bag": bag.name, "cam": cam, "error": "no decodable frames", "frames": len(msgs), "dec_fail": dec_fail})
        continue
    off = sorted(offsets)
    n = len(off)
    med = statistics.median(off)
    mode, mode_cnt = Counter(offsets).most_common(1)[0]
    # 带宽：中位数 ± 半带宽内占比（扫候选带宽，取 >=90% 的最小带宽）
    band = None
    for frac in (0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500):
        b = int(frac * 1e6)
        in_band = sum(1 for x in off if abs(x - med) <= b)
        if in_band / n >= 0.9:
            band = (b, in_band / n)
            break
    out.append({
        "bag": bag.name,
        "cam": cam,
        "frames": len(msgs),
        "dec_fail": dec_fail,
        "n_offsets": n,
        "min_ms": off[0] / 1e6,
        "max_ms": off[-1] / 1e6,
        "range_ms": (off[-1] - off[0]) / 1e6,
        "median_ms": med / 1e6,
        "mean_ms": statistics.mean(off) / 1e6,
        "mode_ms": mode / 1e6,
        "mode_count": mode_cnt,
        "stdev_ms": statistics.pstdev(off) / 1e6 if n > 1 else 0.0,
        "min_band_90pct": band,
        "unique_offsets": len(set(offsets)),
        "first10_ms": [x / 1e6 for x in off[:10]],
        "last5_ms": [x / 1e6 for x in off[-5:]],
    })

print(json.dumps(out, ensure_ascii=False, indent=1))