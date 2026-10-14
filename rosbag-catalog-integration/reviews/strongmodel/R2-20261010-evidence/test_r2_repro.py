"""R2 独立复现：全部使用临时 SQLite / 临时发布目录，不修改业务代码。"""
import hashlib
import json
import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import BagRecord, PipelineRun, SceneAnalysisVersion
from app.services import scene_publish_service as pub
from app.services import scene_result_report_service as report
from app.services import scene_result_service as results
from app.services.scene_slice_service import SceneEntry, SceneRunCreate, create_scene_run
from tests import test_scene_result_report as h


@pytest.fixture
def client():
    if engine.url.drivername != "sqlite" or not str(engine.url.database).startswith("/tmp/r2-review-"):
        raise RuntimeError("仅允许使用 /tmp/r2-review-* 内的隔离 SQLite 库")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def no_match(parent, run):
    return h._manifest_dict(run, parent, outcome="NO_MATCH", segments=[], expected=[])


def body(parent, run, manifest):
    return h._complete_body(h._report_body(run, parent, manifest=manifest, child_map={}), publish_root=None)


def test_switch_failure_is_not_recovered_by_retry(client, monkeypatch):
    with SessionLocal() as db:
        parent = h._parent(db, "switch-retry")
        run = h._create_run(client, parent.bag_uid)
        run.update(h._claim_specific(client, run["pipeline_run_id"]))
        req = body(parent, run, no_match(parent, run))
        original = results.switch_current

        def fail(*args, **kwargs):
            raise HTTPException(409, "injected transient switch conflict")

        monkeypatch.setattr(results, "switch_current", fail)
        first = client.post(h._base_url(run["pipeline_run_id"], "complete-scene"), json=req)
        assert first.status_code == 409, first.text
        monkeypatch.setattr(results, "switch_current", original)
        second = client.post(h._base_url(run["pipeline_run_id"], "complete-scene"), json=req)
        assert second.status_code == 200, second.text
        assert second.json()["replayed"] is True
        assert second.json()["switch"]["current"] is False
        db.expire_all()
        stored = db.scalar(select(PipelineRun).where(PipelineRun.pipeline_run_id == run["pipeline_run_id"]))
        assert stored.status == "SCENE_DONE"
        assert not db.scalar(select(SceneAnalysisVersion).where(SceneAnalysisVersion.run_id == stored.pipeline_run_id)).current
        print("switch retry: HTTP 409 -> HTTP 200, SCENE_DONE, current=False")


def test_reconcile_mixes_historical_versions(client, tmp_path):
    with SessionLocal() as db:
        parent = h._parent(db, "reconcile-history")
        one = h._create_run(client, parent.bag_uid)
        two = h._create_run(client, parent.bag_uid, reanalysis_id="re-" + uuid.uuid4().hex)
        segs = [("slope", (h.BASE_S + 2) * h.NANO, (h.BASE_S + 4) * h.NANO)]
        root1, _, _ = h._stage_and_publish(tmp_path / "one", one, parent, segs)
        root2, _, _ = h._stage_and_publish(tmp_path / "two", two, parent, segs)
        import shutil
        for directory in (tmp_path / "one" / "publish" / "unassigned" / "slope").iterdir():
            shutil.copytree(directory, tmp_path / "two" / "publish" / "unassigned" / "slope" / directory.name)
        req = {"scene_code": "slope", "source_generation": parent.source_generation, "publish_root": root2}
        got = client.post(h._base_url(two["pipeline_run_id"], "reconcile-scene"), json=req)
        assert got.status_code == 409, got.text
        assert "digest" in got.text
        print("reconcile with two valid versions: ", got.status_code, got.text)


def test_empty_published_db3_becomes_available(client, tmp_path):
    with SessionLocal() as db:
        parent = h._parent(db, "empty-db3")
        run = h._create_run(client, parent.bag_uid)
        run.update(h._claim_specific(client, run["pipeline_run_id"]))
        segs = [("slope", (h.BASE_S + 2) * h.NANO, (h.BASE_S + 4) * h.NANO)]
        root, child_map, manifest = h._stage_and_publish(tmp_path, run, parent, segs)
        target = next((tmp_path / "publish" / "unassigned" / "slope").iterdir())
        (target / "rosbag2_0.db3").write_bytes(b"")
        record_file = target / pub.SLICE_MANIFEST_NAME
        record = json.loads(record_file.read_text())
        record["slice"]["db3_sha256"] = hashlib.sha256(b"").hexdigest()
        record["slice"]["message_count"] = 0
        record["slice"]["topics"] = {}
        record_file.write_text(json.dumps(record))
        req = h._complete_body(h._report_body(run, parent, manifest=manifest, child_map=child_map), publish_root=root)
        got = client.post(h._base_url(run["pipeline_run_id"], "complete-scene"), json=req)
        assert got.status_code == 200, got.text
        child = db.scalar(select(BagRecord).where(BagRecord.bag_uid == next(iter(child_map.values()))))
        assert child.availability == "AVAILABLE"
        assert (target / "rosbag2_0.db3").stat().st_size == 0
        print("empty db3: HTTP 200, availability=AVAILABLE, current=True, file_size=0")


def test_unclaimed_run_accepts_worker_result_and_poison_identity(client):
    with SessionLocal() as db:
        parent = h._parent(db, "unclaimed")
        run = h._create_run(client, parent.bag_uid)
        run["lease_token"] = None
        req = body(parent, run, no_match(parent, run))
        got = client.post(h._base_url(run["pipeline_run_id"], "results"), json=req)
        assert got.status_code == 200, got.text
        actual = no_match(parent, run)
        actual["created_at"] = "2026-10-10T08:00:00+00:00"
        run.update(h._claim_specific(client, run["pipeline_run_id"]))
        genuine = client.post(h._base_url(run["pipeline_run_id"], "results"), json=body(parent, run, actual))
        assert genuine.status_code == 409, genuine.text
        print("unclaimed result accepted without lease (HTTP 200); genuine worker later blocked: ", genuine.text)


def test_stale_run_accepts_different_outer_generation(client):
    with SessionLocal() as db:
        parent = h._parent(db, "generation")
        run = h._create_run(client, parent.bag_uid)
        run.update(h._claim_specific(client, run["pipeline_run_id"]))
        manifest = no_match(parent, run)
        parent.source_generation = 2
        db.commit()
        req = body(parent, run, manifest)
        assert req["source_generation"] == 2
        assert manifest["source_generation"] == 1
        got = client.post(h._base_url(run["pipeline_run_id"], "complete-scene"), json=req)
        assert got.status_code == 200, got.text
        assert got.json()["switch"]["current"] is True
        print("run generation=1, manifest generation=1, outer/parent generation=2: HTTP 200 current=True")


def test_late_old_event_run_overwrites_new_current(client):
    with SessionLocal() as db:
        parent = h._parent(db, "event-order")
        entry = SceneEntry("slope", *h._cap())
        spec = SceneRunCreate(source_id=parent.bag_uid, source_generation=parent.source_generation,
                              purpose="scene_slice", scenes=(entry,))
        old, created = create_scene_run(db, spec)
        assert created
        db.commit()
        old_info = {"pipeline_run_id": old.pipeline_run_id}
        old_info.update(h._claim_specific(client, old.pipeline_run_id))
        new_info = h._create_run(client, parent.bag_uid, reanalysis_id="re-" + uuid.uuid4().hex)
        new_info.update(h._claim_specific(client, new_info["pipeline_run_id"]))
        new_req = body(parent, new_info, no_match(parent, new_info))
        new_res = client.post(h._base_url(new_info["pipeline_run_id"], "complete-scene"), json=new_req)
        assert new_res.status_code == 200, new_res.text
        old_req = body(parent, old_info, no_match(parent, old_info))
        old_res = client.post(h._base_url(old.pipeline_run_id, "complete-scene"), json=old_req)
        assert old_res.status_code == 200, old_res.text
        db.expire_all()
        current = db.scalar(select(SceneAnalysisVersion).where(SceneAnalysisVersion.parent_bag_uid == parent.bag_uid,
                                                             SceneAnalysisVersion.current.is_(True)))
        assert current.run_id == old.pipeline_run_id
        print("new explicit analysis current -> late OLD event run overwrites current (HTTP 200)")


def test_successful_publish_cannot_retry_original_specs(tmp_path):
    seg = h.SegT("slope", (h.BASE_S + 2) * h.NANO, (h.BASE_S + 4) * h.NANO, True, "header_stamp_ns")
    manifest = h._publish_manifest("repro-publish", "parent", [seg])
    bag = h._bag_with_offset(tmp_path / "src", offset_ns=0)
    written = h.slice_bag_to_staging(bag, tmp_path / "staging", seg, storage_offset_ns=0)
    spec = h._spec(seg, written, "child")
    pub.publish_scene_slices(manifest, publish_root=tmp_path / "publish", vehicle_key="", specs=[spec])
    assert not written.out_dir.exists()
    with pytest.raises(FileNotFoundError):
        pub.publish_scene_slices(manifest, publish_root=tmp_path / "publish", vehicle_key="", specs=[spec])
    print("successful publish replay with original specs: FileNotFoundError before target reuse")


def test_available_child_has_no_published_file_index(client, tmp_path):
    with SessionLocal() as db:
        parent = h._parent(db, "file-index")
        run = h._create_run(client, parent.bag_uid)
        run.update(h._claim_specific(client, run["pipeline_run_id"]))
        segs = [("slope", (h.BASE_S + 2) * h.NANO, (h.BASE_S + 4) * h.NANO)]
        root, child_map, manifest = h._stage_and_publish(tmp_path, run, parent, segs)
        req = h._complete_body(h._report_body(run, parent, manifest=manifest, child_map=child_map), publish_root=root)
        got = client.post(h._base_url(run["pipeline_run_id"], "complete-scene"), json=req)
        assert got.status_code == 200, got.text
        child = db.scalar(select(BagRecord).where(BagRecord.bag_uid == next(iter(child_map.values()))))
        target = next((tmp_path / "publish" / "unassigned" / "slope").iterdir())
        assert child.availability == "AVAILABLE"
        assert child.relative_path.startswith("scene/slope/")
        assert not child.files
        assert not child.topics
        assert child.message_count == 0 and child.total_size_bytes == 0
        print("AVAILABLE child: relative_path=", child.relative_path,
              "actual_target=", target, "files=0 topics=0 message_count=0 total_size_bytes=0")
