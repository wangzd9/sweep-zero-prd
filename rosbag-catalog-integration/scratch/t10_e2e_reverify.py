"""TASK-10 attempt-1 端到端正式服务链驱动器（P0 收尾单）。

环境事实（本 driver 依据）：
- 共享 8 容器栈 backend 镜像 build 2026-10-08，早于 scene 路由（10-09/10-11），
  不含 /api/v1/scene-* 链 → 不可直接驱动。故用 ca8730d worktree 起独立 app 实例
  （fresh SQLite + create_all + seed default profile/scenes），走正式 TestClient API
  （TASK-06B/08 先例口径：不 mock 服务，app 本体全链路真实）。
- 执行面：仓库无已交付 scene 执行代理（orchestrator 派发到 SCENE_PROXY_URL，栈内为空）。
  按 dispatch §二.2 "04B 适配器链真实 VLM 调用" 由本 driver 驱动执行面
  （SlopeAdapter.analyze + 真实 HttpSlopeModelClient → writer 再切 → 06B 发布）。
- 样本 row19（15s，正相机 /bev/cam_front_8m_jpg CompressedImage，54 帧）。

步骤：
  1. 登记源目录（POST /sources/register，NAS_LOCAL_ROOT=挂载根，只读，源不变）
  2. 冻结配置（GET /ingest-profiles 确认 default 在位；POST /scene-analysis-runs 建 run=冻结能力 hash）
  3. 真实坡道切片（claim SCENE_SLICE_QUEUE → SlopeAdapter.analyze 真实 VLM → SUCCESS + 可发布区间）
  4. NAS+数据库（derive_storage_offset → writer staging → publish_scene_slices 原子发布 → /results → /complete-scene 登记父子/标签/当前版）
  5. API 获取（GET /bags/{child} / lineage / 切片可打开 + 原包前后 hash/mtime 校验）

每步落 evidence/t10-e2e.json + 日志，断言失败如实申报（不伪装成功）。
"""
import json
import os
import shutil
import sys
import time
import hashlib
import uuid
from pathlib import Path

WT = "/home/wang/work/rosbag-catalog"
sys.path.insert(0, WT)

OUT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10")
OUT.mkdir(parents=True, exist_ok=True)
EV = OUT / "t10-e2e.json"

ROOT_MOUNT = Path("/home/wang/.hermes/cache/scratch/t10-nasroot")
BAG_NAME = "1165414093_slope_20260818_105105_105120"
BAG_SRC = Path("/mnt/nas_backup/data_slice/1165414093/slope") / BAG_NAME  # 真实 NAS 袋（只读，不变校验对象）
LOCAL_BAG = ROOT_MOUNT / "incoming" / BAG_NAME  # 本地 NAS 根内物理副本（注册/切片用）
WORK = OUT / "work"
PUBLISH = OUT / "publish"
VLM_ENDPOINT = "http://192.168.2.45:8002/v1/chat/completions"
CAM = "/bev/cam_front_8m_jpg"

EVIDENCE = {"steps": {}, "verdicts": {}, "source_hash_before": None, "error": None}


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(OUT / "t10-run.log", "a") as f:
        f.write(line + "\n")


def save():
    EV.write_text(json.dumps(EVIDENCE, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def fail(step, msg, code=None):
    log(f"[FAIL] {step}: {msg}")
    EVIDENCE["error"] = {"step": step, "message": msg, "code": code}
    save()
    raise SystemExit(f"{step} FAILED: {msg}")


# ---- 0. setup env (fresh SQLite, NAS local root = mount, real VLM) ----
DB = OUT / "t10-e2e.db"
if DB.exists():
    DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEPLOYMENT_MODE"] = "development"
os.environ["TEST_EXECUTION_MODE"] = "mock"
os.environ["NAS_LOCAL_ROOT"] = str(ROOT_MOUNT)
os.environ["NAS_STORAGE_ROOT"] = "/test"
os.environ["NAS_SCAN_ROOT"] = "/test/incoming"
os.environ["NAS_READY_ROOT"] = "/test/ready"
os.environ["NAS_FINAL_ROOT"] = "/test/final"
os.environ["NVIDIA_NAS_ORIGIN_ROOT"] = "/test/nvidia_origin"
os.environ["DEMO_DATA"] = "0"
os.environ["SCENE_INGEST_ENABLED"] = "1"
os.environ["SLOPE_VLM_ENDPOINT"] = VLM_ENDPOINT
os.environ["DISPLAY_TIMEZONE"] = "Asia/Shanghai"
# fresh scratch dirs
for d in (WORK, PUBLISH):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
log(f"[0] env set; DB={DB}; local_nas_root={ROOT_MOUNT}")
log(f"[0] SLOPE_VLM_ENDPOINT={VLM_ENDPOINT}")

# source before hash/mtime (bag files)
before = {}
for f in sorted(BAG_SRC.iterdir()):
    h = hashlib.sha256(f.read_bytes()).hexdigest() if f.stat().st_size < 60_000_000 else hashlib.sha256(open(f,'rb').read(1<<20)).hexdigest()
    before[f.name] = {"size": f.stat().st_size, "mtime": f.stat().st_mtime, "sha256_head1MB": h}
EVIDENCE["source_hash_before"] = before
save()

import app.config  # noqa
from app.config import settings
assert settings.nas_local_root == str(ROOT_MOUNT), settings.nas_local_root
from app.main import app as fastapi_app
from fastapi.testclient import TestClient

# Local NAS root: copy real bag (byte-identical .db3 + metadata.yaml) into incoming/ so
# MountedNasClient (which .resolve()s symlinks) accepts the path. Only the rosbag2 files
# are needed for inspection/slicing; the bev_*.mp4 extras are skipped (not in metadata).
(ROOT_MOUNT / "incoming").mkdir(parents=True, exist_ok=True)
(ROOT_MOUNT / "ready").mkdir(parents=True, exist_ok=True)
(ROOT_MOUNT / "final").mkdir(parents=True, exist_ok=True)
if LOCAL_BAG.is_symlink() or LOCAL_BAG.exists():
    if LOCAL_BAG.is_symlink():
        LOCAL_BAG.unlink()
    else:
        shutil.rmtree(LOCAL_BAG)
LOCAL_BAG.mkdir(parents=True)
import yaml  # noqa
_meta = yaml.safe_load((BAG_SRC / "metadata.yaml").read_text(encoding="utf-8"))
_rel_files = []
try:
    _info = _meta["rosbag2_bagfile_information"]
    for f in _info.get("relative_file_paths", []):
        _rel_files.append(f)
except Exception:
    _rel_files = []
log(f"[0] copying real bag .db3+metadata into local NAS root: files={_rel_files}")
copied = []
for _f in _rel_files:
    src_f = BAG_SRC / _f
    if src_f.exists():
        shutil.copy2(src_f, LOCAL_BAG / _f)
        copied.append(_f)
shutil.copy2(BAG_SRC / "metadata.yaml", LOCAL_BAG / "metadata.yaml")
log(f"[0] copied {len(copied)} data files (byte-identical) into {LOCAL_BAG}")

with TestClient(fastapi_app) as client:
    # ---- 1. 03B 接收链：提交（冻结 slope 配置 hash）+ 登记源目录 + 事件消费建 run ----
    from app.services.fingerprint import fingerprint_bag
    fp = fingerprint_bag(BAG_SRC)["fast_fingerprint"]
    log(f"[1a] create ingest submission (default profile, scene_slice + slope); fast_fingerprint={fp[:24]}...")
    sub = client.post("/api/v1/ingest-submissions", json={
        "profile_id": "default", "relative_path": BAG_NAME,
        "purposes": ["scene_slice"], "scenes": [{"scene_code": "slope"}]},
        headers={"Idempotency-Key": "t10-sub-" + uuid.uuid4().hex})
    EVIDENCE["steps"]["1a_submission"] = {"status": sub.status_code, "body": sub.json()}
    if sub.status_code not in (200, 201):
        fail("1a_submission", f"status {sub.status_code}: {sub.text[:400]}")
    sub_hash = (sub.json().get("effective_config") or {}).get("config_hash") or sub.json().get("config_hash")
    log(f"[1a] submission frozen config_hash={sub_hash}")
    EVIDENCE["verdicts"]["1a_submission"] = "OK_FROZEN" if sub_hash else "NULL_HASH"
    save()

    log("[1b] register source dir via /sources/register (incoming_path for 03B bind)")
    reg = client.post("/api/v1/sources/register",
                      json={"path": f"/test/incoming/{BAG_NAME}", "incoming_path": f"/test/incoming/{BAG_NAME}",
                            "fast_fingerprint": fp, "fingerprint_version": "rosbag-fast-v1"},
                      headers={"Idempotency-Key": "t10-reg-" + uuid.uuid4().hex})
    EVIDENCE["steps"]["1b_register"] = {"status": reg.status_code, "body": reg.json()}
    if reg.status_code not in (200, 201):
        fail("1b_register", f"status {reg.status_code}: {reg.text[:400]}")
    source_id = reg.json().get("source_id")
    ingest = reg.json().get("ingest")
    log(f"[1b] source_id={source_id} ingest={ingest}")
    EVIDENCE["verdicts"]["1b_register"] = "OK" if source_id else "NO_SOURCE_ID"
    save()
    if not source_id:
        fail("1b_register", "no source_id in register response")
    # source_status precondition: in app code nothing sets source_status="READY" (only
    # DISCOVERED default / error types — 0 setters in app/). The scene consumer and the
    # explicit run API both require READY, so a normally-registered real source never
    # reaches the scene chain. This is TASK-10 finding #1 (formal registration path cannot
    # produce a scene-ready source). To exercise the downstream chain with REAL evidence we
    # apply the documented harness precondition (same as the 03B->05 e2e fixtures set
    # source_status="READY") via the ORM on this isolated fresh DB. Reported separately as #1.
    log("[1c2] applying documented harness precondition source_status=READY (app has no setter -> finding #1)")
    from app.database import SessionLocal as _SL
    from app.models import BagRecord as _BR
    from sqlalchemy import select as _sel
    with _SL() as _db:
        _bag = _db.scalar(_sel(_BR).where(_BR.bag_uid == source_id))
        _bag.source_status = "READY"
        _db.commit()
        EVIDENCE["steps"]["1c2_ready_precondition"] = {"source_status_before": "DISCOVERED", "set_to": "READY", "note": "harness precondition; app code has 0 setters of source_status=READY (finding #1)"}
    EVIDENCE["verdicts"]["1c2_ready_precondition"] = "PRECONDITION_APPLIED"
    save()
    src = client.get(f"/api/v1/sources/{source_id}")
    EVIDENCE["steps"]["1c_source_detail"] = {"status": src.status_code, "body": src.json()}
    save()

    log("[1d] consume purpose events -> create SCENE_SLICE run (frozen identity, no NULL-hash)")
    cons = client.post("/api/v1/orchestrator/purpose-events/consume", json={})
    EVIDENCE["steps"]["1d_consume"] = {"status": cons.status_code, "body": cons.json()}
    save()
    # locate the scene run for this source
    run_id, frozen_hash, created = None, None, None
    src2 = client.get(f"/api/v1/sources/{source_id}")
    runs = (src2.json().get("runs") or []) if src2.status_code == 200 else []
    for r in runs:
        if r.get("pipeline_type") == "SCENE_SLICE":
            run_id = r.get("pipeline_run_id"); break
    if not run_id:
        # fallback: explicit formal run API (DESIGN §7.1, same service)
        log("[1d] no scene run from consume; falling back to explicit POST /scene-analysis-runs")
        _k = "t10-run-" + uuid.uuid4().hex
        rrun = client.post("/api/v1/scene-analysis-runs", json={"source_id": source_id, "scenes": [{"scene_code": "slope"}], "idempotency_key": _k}, headers={"Idempotency-Key": _k})
        EVIDENCE["steps"]["1d_explicit_fallback"] = {"status": rrun.status_code, "body": rrun.json()}
        if rrun.status_code in (202, 200):
            run_id = rrun.json()["pipeline_run_id"]
            frozen_hash = rrun.json().get("scenes", [{}])[0].get("capability_config_hash")
            created = rrun.json().get("created")
    else:
        # read frozen hash from run detail
        rd = client.get(f"/api/v1/scene-analysis-runs/{run_id}")
        EVIDENCE["steps"]["1e_run_detail"] = {"status": rd.status_code, "body": rd.json()}
        save()
    EVIDENCE["verdicts"]["1_run_created"] = "OK" if run_id else "NO_RUN"
    log(f"[1d] run_id={run_id} (frozen via 03B chain, config_hash from submission={sub_hash})")
    save()
    if not run_id:
        fail("1_run", "no SCENE_SLICE run created via 03B chain or explicit fallback")

    # ---- 3. claim + real VLM analyze ----
    log("[3] claim SCENE_SLICE_QUEUE run")
    claim = client.post("/api/v1/orchestrator/claim", json={"queue": "SCENE_SLICE_QUEUE", "executor_id": "t10-b", "ttl_seconds": 600})
    EVIDENCE["steps"]["3_claim"] = {"status": claim.status_code, "body": {k: claim.json().get(k) for k in ("claimed", "pipeline_run_id", "lease_token", "attempt", "source_generation", "pipeline_type")}}
    if not (claim.json().get("claimed") and claim.json().get("pipeline_run_id") == run_id):
        # maybe claimed a different run; release and retry up to 5
        body = claim.json()
        for _ in range(5):
            if body.get("claimed"):
                client.post(f"/api/v1/orchestrator/task-leases/{body['lease_token']}/release-claim", json={"reason": "not target run"})
            claim = client.post("/api/v1/orchestrator/claim", json={"queue": "SCENE_SLICE_QUEUE", "executor_id": "t10-b", "ttl_seconds": 600})
            body = claim.json()
            if body.get("claimed") and body.get("pipeline_run_id") == run_id:
                break
    EVIDENCE["steps"]["3_claim_retry"] = {"claimed": claim.json().get("claimed"), "run": claim.json().get("pipeline_run_id")}
    save()
    if not (claim.json().get("claimed") and claim.json().get("pipeline_run_id") == run_id):
        fail("3_claim", f"could not claim target run: {claim.text[:300]}")
    lease_token = claim.json()["lease_token"]
    attempt = claim.json().get("attempt", 1)
    source_generation = claim.json().get("source_generation")
    # run detail: authoritative frozen hash + generation (both consume/explicit paths)
    rd = client.get(f"/api/v1/scene-analysis-runs/{run_id}")
    rdd = rd.json() if rd.status_code == 200 else {}
    EVIDENCE["steps"]["3_run_detail"] = {"status": rd.status_code, "body": rdd}
    scenes_info = rdd.get("scenes") or []
    if scenes_info and scenes_info[0].get("capability_config_hash"):
        frozen_hash = scenes_info[0]["capability_config_hash"]
    if not frozen_hash:
        fail("3_frozen_hash", f"no frozen capability_config_hash in run detail: {str(rdd)[:300]}")
    if not source_generation:
        from app.database import SessionLocal as _SL2
        from app.models import BagRecord as _BR2
        from sqlalchemy import select as _sel2
        with _SL2() as _db:
            source_generation = _db.scalar(_sel2(_BR2).where(_BR2.bag_uid == source_id)).source_generation
    log(f"[3] claimed run={run_id} lease={lease_token[:16]}... attempt={attempt} gen={source_generation} frozen_hash={frozen_hash}")
    EVIDENCE["verdicts"]["3_claim"] = "OK"
    save()

    # build execution request from run + parent facts (real capability resolution, real VLM client)
    from app.scene import get_registry
    from app.scene.slope.adapter import SlopeAdapter
    from app.scene.slope.vlm import HttpSlopeModelClient
    from app.scene.types import SceneRunRequest
    regdb = get_registry()
    eff = regdb.effective_params("slope", None)
    cap = regdb.resolve("slope", eff.capability_version)
    vlm_client = HttpSlopeModelClient(endpoint=VLM_ENDPOINT, api_key="t10", system_prompt="判断车辆前向图像：平地还是坡道，只输出'平地'或'坡道'。", frame_prompt="这是车辆前向图像，判断当前行驶在平地还是坡道上。只输出'平地'或'坡道'。", max_retries=2, timeout_seconds=180)
    adapter = SlopeAdapter(model_client=vlm_client)
    # parent bag facts (fingerprint, generation, path)
    from app.database import SessionLocal
    from app.models import BagRecord
    from sqlalchemy import select
    with SessionLocal() as db:
        bag = db.scalar(select(BagRecord).where(BagRecord.bag_uid == source_id))
        parent_fp = bag.fast_fingerprint
        parent_gen = bag.source_generation
    log(f"[3] parent fp={parent_fp} gen={parent_gen}; running real VLM analyze on {BAG_SRC} (work={WORK})")
    save()
    t0 = time.time()
    try:
        out = adapter.analyze(SceneRunRequest(
            source_id=source_id, source_generation=parent_gen, source_fingerprint=parent_fp,
            source_path=str(LOCAL_BAG), source_topics=(CAM,), capability=cap,
            parameters=eff.parameters, config_hash=frozen_hash, work_dir=str(WORK)))
    except Exception as e:
        fail("3_analyze", f"adapter.analyze raised {type(e).__name__}: {e}", code=getattr(e, "code", None))
    outcome = out.outcome.value
    segs = [s.to_dict() for s in out.segments]
    EVIDENCE["steps"]["3_analyze"] = {"outcome": outcome, "latency_s": round(time.time() - t0, 1), "segments": segs, "evidence": [e.__dict__ for e in out.evidence], "error_code": out.error_code, "error_detail": out.error_detail}
    log(f"[3] analyze outcome={outcome} segments={len(segs)} err={out.error_code}")
    EVIDENCE["verdicts"]["3_analyze"] = outcome
    save()
    if outcome != "SUCCESS":
        # MODEL_UNAVAILABLE / NO_MATCH / FAILED: real result, not fake
        log(f"[3] non-SUCCESS outcome {outcome} -> real capability result, publish step N/A (NO_MATCH empty publish)")
        # still attempt report/complete with this outcome to prove the chain handles it
        pass

    # ---- 4. writer staging + derive offset + publish + register + complete ----
    from app.scene.types import SceneManifest, SceneOutcome
    from app.scene.slope.writer import slice_bag_to_staging
    from app.services import scene_publish_service
    publishable = [s for s in out.segments if s.publish_target and s.duration_ns > 0]
    log(f"[4] publishable segments={len(publishable)}")
    EVIDENCE["steps"]["4_manifest"] = {"publishable": [s.slice_key for s in publishable]}
    save()

    manifest = SceneManifest(
        scene_code="slope", capability_version=cap.capability_version, run_id=run_id, analysis_version=1,
        source_id=source_id, source_generation=parent_gen, source_fingerprint=parent_fp,
        config_hash=frozen_hash, outcome=out.outcome, segments=tuple(out.segments), evidence=out.evidence,
        expected_slice_keys=tuple(s.slice_key for s in publishable), created_at=time.strftime("%Y-%m-%dT%H:%M:%S+08:00"))

    # derive storage offset (fail-closed)
    offset = scene_publish_service.derive_storage_offset(manifest, LOCAL_BAG)
    EVIDENCE["steps"]["4_offset"] = {"derive_storage_offset": offset, "note": "None -> PUBLISH_BLOCKED (fail-closed, real data non-constant)" }
    log(f"[4] derive_storage_offset = {offset}")
    EVIDENCE["verdicts"]["4_offset"] = "OK_CONSTANT" if (offset is not None) else "PUBLISH_BLOCKED_NONE"
    save()

    child_map = {}
    specs = []
    if offset is not None and publishable:
        staging_root = WORK / "staging"
        for s in publishable:
            res = slice_bag_to_staging(LOCAL_BAG, staging_root, s, storage_offset_ns=offset)
            child_uid = "T10S" + uuid.uuid4().hex[:16]  # <=26 chars
            assert len(child_uid) <= 26
            child_map[s.slice_key] = child_uid
            specs.append(scene_publish_service.SlicePublishSpec(
                slice_key=s.slice_key, child_bag_uid=child_uid, staging_dir=res.out_dir,
                db3_sha256=res.db3_sha256 or "", message_count=res.message_count,
                start_ns=s.start_ns, end_ns=s.end_ns, topics=res.topics,
                # t10-defect3（main 453da0c）：complete-scene 区间复核改用存储域实际边界，
                # 缺此两项按新 fail-closed 语义将 409（预期拦截，非修复未生效）。
                actual_start_ns=res.actual_start_ns, actual_end_ns=res.actual_end_ns))
        # vehicle key: parent has no vehicle -> unassigned
        published = scene_publish_service.publish_scene_slices(manifest, publish_root=PUBLISH, vehicle_key="unassigned", specs=specs)
        EVIDENCE["steps"]["4_publish"] = {"published": [str(p) for p in published]}
        log(f"[4] published {len(published)} slices")
        EVIDENCE["verdicts"]["4_publish"] = "OK"
    else:
        EVIDENCE["steps"]["4_publish"] = {"published": [], "blocked": offset is None}
        log("[4] publish BLOCKED (offset None) or NO_MATCH (no publishable) -> complete-scene will reflect outcome")
        EVIDENCE["verdicts"]["4_publish"] = "BLOCKED_OR_EMPTY"
    save()

    # report + complete via formal API — only reachable when publish actually landed
    # (complete-scene verifies published files; /results registers children PENDING).
    if offset is not None and publishable and child_map:
        report_body = {"scene_code": "slope", "lease_token": lease_token, "source_generation": parent_gen,
                       "manifest": manifest.to_dict(), "child_bag_uids": child_map}
        rrep = client.post(f"/api/v1/scene-analysis-runs/{run_id}/results", json=report_body, headers={"Idempotency-Key": "t10-res-" + uuid.uuid4().hex})
        EVIDENCE["steps"]["4_report"] = {"status": rrep.status_code, "body": rrep.json() if rrep.headers.get('content-type','').startswith('application/json') else rrep.text[:300]}
        log(f"[4] /results status={rrep.status_code}")
        save()
        complete_body = {"scene_code": "slope", "lease_token": lease_token, "source_generation": parent_gen,
                         "manifest": manifest.to_dict(), "child_bag_uids": child_map, "publish_root": str(PUBLISH)}
        rcom = client.post(f"/api/v1/scene-analysis-runs/{run_id}/complete-scene", json=complete_body)
        EVIDENCE["steps"]["4_complete"] = {"status": rcom.status_code, "body": rcom.json() if rcom.headers.get('content-type','').startswith('application/json') else rcom.text[:300]}
        log(f"[4] /complete-scene status={rcom.status_code} body={str(rcom.json() if rcom.status_code<500 else rcom.text)[:200]}")
        EVIDENCE["verdicts"]["4_complete"] = "OK" if rcom.status_code == 200 else f"STATUS_{rcom.status_code}"
        save()
    else:
        EVIDENCE["steps"]["4_report"] = {"skipped": True, "reason": "PUBLISH_BLOCKED (derive_storage_offset=None, real data non-constant) or NO_MATCH: no published files to register/complete"}
        EVIDENCE["verdicts"]["4_complete"] = "REACHED_BLOCKER"
        # release the claim (no publish to complete); run left in queue, orchestrator reconciles
        rrel = client.post(f"/api/v1/orchestrator/task-leases/{lease_token}/release-claim", json={"reason": "PUBLISH_BLOCKED: derive_storage_offset=None (real rosbag2 per-message write-time jitter, offset not bit-constant)"})
        EVIDENCE["steps"]["4_release_claim"] = {"status": rrel.status_code, "body": rrel.json() if rrel.headers.get('content-type','').startswith('application/json') else rrel.text[:200]}
        log(f"[4] publish blocked -> claim released (run stays in queue for reconcile)")
        save()

    # ---- 5. API 获取 + 原包不变 ----
    if child_map:
        child_uid = next(iter(child_map.values()))
        mf = client.get(f"/api/v1/bags/{child_uid}")
        lin = client.get(f"/api/v1/bags/{child_uid}/lineage")
        EVIDENCE["steps"]["5_fetch"] = {"child": child_uid, "bags_status": mf.status_code, "lineage_status": lin.status_code,
                                        "bags_body": mf.json() if mf.status_code == 200 else mf.text[:200],
                                        "lineage_body": (lin.json() or {}) if lin.status_code == 200 else lin.text[:200]}
        EVIDENCE["verdicts"]["5_fetch"] = "OK" if (mf.status_code == 200 and lin.status_code == 200) else "DEGRADED"
        log(f"[5] bags/{child_uid}={mf.status_code} lineage={lin.status_code}")
    else:
        # fetch the PARENT via formal API (proves 03B registration landed) + its run
        pf = client.get(f"/api/v1/bags/{source_id}")
        EVIDENCE["steps"]["5_fetch"] = {"child": None, "note": "PUBLISH_BLOCKED: no child bag (derive_storage_offset=None on all 7 real slope bags)",
                                        "parent_bags_status": pf.status_code,
                                        "parent_body": {k: pf.json().get(k) for k in ("bag_uid", "name", "status", "source_status", "source_generation", "fast_fingerprint", "bag_role")} if pf.status_code == 200 else pf.text[:200]}
        EVIDENCE["verdicts"]["5_fetch"] = "PARENT_FETCHED_NO_CHILD"
        log(f"[5] no child (publish blocked); parent bags/{source_id}={pf.status_code}")
    save()
    # source unchanged
    after = {}
    for f in sorted(BAG_SRC.iterdir()):
        h = hashlib.sha256(open(f, 'rb').read(1 << 20)).hexdigest()
        after[f.name] = {"size": f.stat().st_size, "mtime": f.stat().st_mtime, "sha256_head1MB": h}
    EVIDENCE["steps"]["5_source_unchanged"] = {"unchanged": after == EVIDENCE["source_hash_before"]}
    EVIDENCE["verdicts"]["5_source_unchanged"] = "OK" if after == EVIDENCE["source_hash_before"] else "SOURCE_MODIFIED"
    log(f"[5] source unchanged={after == EVIDENCE['source_hash_before']}")
    save()

save()
log("[DONE] evidence written to " + str(EV))
print("=== E2E COMPLETE ===")
print(json.dumps({k: v for k, v in EVIDENCE.items() if k != "source_hash_before"}, ensure_ascii=False, indent=2, default=str)[:2500])