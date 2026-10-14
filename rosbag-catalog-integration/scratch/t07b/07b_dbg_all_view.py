import os, tempfile
os.environ["DEMO_DATA"] = "1"
f = tempfile.NamedTemporaryFile(prefix="t07b-dbg-", suffix=".db", delete=False)
f.close()
os.environ["DATABASE_URL"] = f"sqlite:///{f.name}"
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.database import SessionLocal
from app.main import app
from app.models import BagRecord
from tests.test_task07b_manual_revision import _mk_bag, _mk_scene_slice, SCENE, _purge

client = TestClient(app)
with client:
    with SessionLocal() as db:
        parent = _mk_bag(db, role="ORIGINAL", name="t07b-dbg-parent")
        child, ver_id, seg_id, _ = _mk_scene_slice(db, parent=parent, name="t07b-dbg-child")
        w = client.post(
            f"/api/v1/bags/{child.bag_uid}/withdraw",
            headers={"X-Operator": "dbg"},
            json={"scene_code": SCENE, "reason": "dbg", "row_version": child.row_version},
        )
        print("withdraw:", w.status_code, w.json().get("availability"))
        page = client.get(f"/bags?view=all&q={child.name}")
        print("all status:", page.status_code, "name in all:", child.name in page.text, "count rows:", page.text.count("data-bag-row"))
        d = client.get(f"/bags?q={child.name}")
        print("default status:", d.status_code, "name in default:", child.name in d.text, "count rows:", d.text.count("data-bag-row"))
        with SessionLocal() as db2:
            c = db2.scalar(select(BagRecord).where(BagRecord.bag_uid == child.bag_uid))
            print("availability now:", c.availability)
            _purge(db2, [parent.bag_uid, child.bag_uid], [parent.id, child.id], [ver_id], [seg_id])