"""t10-defect2 真实 7 袋复验：derive_storage_offset 修复后逐袋推导结果。

只读 NAS；对每条 slope 袋构造 header_stamp_ns basis 的 manifest，
调 app 真实 derive_storage_offset，记录 offset + 抖动带 + 是否可推导。
期望：全部 7 袋返回非 None 稳定 offset（修复前全部 None → PUBLISH_BLOCKED）。
"""
import json, statistics, sys
from pathlib import Path

WT = Path("/home/wang/.local/state/rosbag-scene/wt-04a-t10d2")
sys.path.insert(0, str(WT))

from app.scene.slope.bag_io import read_messages, read_topics  # noqa: E402
from app.scene.slope.cdr import decode_compressed_image, decode_image  # noqa: E402
from app.scene.types import SceneManifest, SceneSegment, EvidenceRef, SceneOutcome  # noqa: E402
from app.services import scene_publish_service as sps  # noqa: E402

ROOT = Path("/mnt/nas_backup/data_slice/1165414093/slope")
CAM = "/bev/cam_front_8m_jpg"
NANO = 1_000_000_000


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
    return s.sec * NANO + s.nanosec


def make_manifest(cam_topic):
    return SceneManifest(
        scene_code="slope",
        capability_version="slope-v1",
        run_id="r-t10d2",
        analysis_version=1,
        source_id="src-t10d2",
        source_generation=1,
        source_fingerprint="f",
        config_hash="c" + "a" * 61,
        outcome=SceneOutcome.SUCCESS,
        segments=(SceneSegment(
            label="slope", start_ns=1787021465142223739,
            end_ns=1787021479550464104, publish_target=True,
            mapping_basis="header_stamp_ns", evidence_ref="frame_log#0"),),
        evidence=(EvidenceRef(kind="SLOPE_TOPIC", path=cam_topic),),
        expected_slice_keys=("slope:1787021465142223739:1787021479550464104",),
    )


out = []
for bag in sorted(ROOT.iterdir()):
    if not bag.is_dir():
        continue
    topics = {t.name: t for t in read_topics(bag)}
    msgs = read_messages(bag, topic=CAM)
    offs = []
    for m in msgs:
        h = dec(m.data, topics[CAM].msgtype)
        if h is not None:
            offs.append(m.timestamp_ns - h)
    med = statistics.median(offs)
    cov100 = sum(1 for x in offs if abs(x - med) <= sps.STORAGE_OFFSET_JITTER_TOL_NS) / len(offs)
    derived = sps.derive_storage_offset(make_manifest(CAM), bag)
    out.append({
        "bag": bag.name,
        "frames": len(offs),
        "min_ms": round(min(offs) / 1e6, 3),
        "max_ms": round(max(offs) / 1e6, 3),
        "range_ms": round((max(offs) - min(offs)) / 1e6, 3),
        "median_ms": round(med / 1e6, 3),
        "maxdev_from_med_ms": round(max(abs(x - med) for x in offs) / 1e6, 3),
        "cov@100ms": round(cov100, 4),
        "unique_offsets": len(set(offs)),
        "derived_offset_ms": None if derived is None else round(derived / 1e6, 3),
        "derive_ok": derived is not None,
    })

print(json.dumps(out, ensure_ascii=False, indent=1))
print()
print("derive_ok all:", all(r["derive_ok"] for r in out), f"({sum(r['derive_ok'] for r in out)}/{len(out)})")