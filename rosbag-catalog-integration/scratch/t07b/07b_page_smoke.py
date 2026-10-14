"""T07B 页面实测（自包含 uvicorn + 临时 SQLite，口径同 07A attempt-2-r1 smoke）。

不触共享 real 栈/容器/代理/MySQL。断言 5 段：
1) 切片详情页渲染纠错+下架双表单与审计区（操作前）；
2) POST 页面纠错表单 → 303 → flash 成功 + 审计表出现操作者/原因/原值；
3) POST 页面下架表单 → 303 → flash 成功 + 详情"已下架"标注；
4) 默认 slices 视图表格行不再出现该切片；all 视图行仍在且标注"已下架"；
5) 下架后详情表单面：下架表单消失（不可重复下架入口）、纠错表单仍在、无 re-activate 入口。
"""

import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

WORKTREE = "/home/wang/.local/state/rosbag-scene/wt-04a-t07b"
PORT = 18762
SUFFIX = f"t07b{int(time.time()) % 100000}"
DB = tempfile.NamedTemporaryFile(prefix=f"t07b_smoke_{SUFFIX}_", suffix=".db", delete=False).name

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "pass": bool(cond), "detail": detail})
    print(f"{'PASS' if cond else 'FAIL'} - {name} {detail if not cond else ''}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = urllib.request.build_opener(NoRedirect)


def http(path, method="GET", data=None, headers=None):
    url = f"http://127.0.0.1:{PORT}{path}"
    req = urllib.request.Request(url, method=method, data=data, headers=headers or {})
    try:
        with _opener.open(req) as resp:
            return resp.status, resp.read().decode(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), dict(e.headers)


def post_form(path, fields):
    body = urllib.parse.urlencode(fields).encode()
    return http(path, method="POST", data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})


def rows(html):
    return "".join(re.findall(r"<tr data-bag-row.*?</tr>", html, re.S))


# 1) 起 uvicorn（临时库 + DEMO 关闭，避免污染断言）
env = dict(os.environ, DATABASE_URL=f"sqlite:///{DB}", DEMO_DATA="0", PYTHONPATH=WORKTREE)
proc = subprocess.Popen(
    [f"{WORKTREE}/.venv/bin/uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
    cwd=WORKTREE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
)
up = False
for _ in range(60):
    try:
        s = socket.create_connection(("127.0.0.1", PORT), timeout=1)
        s.close()
        up = True
        break
    except OSError:
        if proc.poll() is not None:
            break
        time.sleep(0.5)
if not up:
    print("UVICORN FAILED TO START")
    print(proc.stdout.read().decode()[-3000:])
    proc.kill()
    sys.exit(2)

try:
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/openapi.json") as r:
        print("openapi:", r.status)
    # 造数：父包 + AVAILABLE 切片 + 派生登记 + MODEL 证据（直接 SQL 走 ORM 口径，库已 create_all）
    seed = """
import os, sys, json
os.environ["DATABASE_URL"] = "sqlite:///__DB__"
os.environ["DEMO_DATA"] = "0"
sys.path.insert(0, "__WORKTREE__")
from datetime import datetime
from app.database import SessionLocal
from app.models import (
    BagRecord, BagDerivation, SceneAnalysisVersion, SceneSegment,
    BagSceneLabelEvidence, Scene,
)
db = SessionLocal()
parent = BagRecord(
    bag_uid="0__SUFFIX_UPPER__PARENT1111111111", name="smoke-parent-__SUFFIX__",
    relative_path=f"/smoke/__SUFFIX__/parent", bag_role="ORIGINAL", status="READY",
    started_at=datetime(2026, 10, 1, 8, 0, 0), duration_ns=10**9,
)
child = BagRecord(
    bag_uid="0__SUFFIX_UPPER__SLICE11111111111", name="smoke-child-__SUFFIX__",
    relative_path=f"/smoke/__SUFFIX__/child", bag_role="SCENE_SLICE", availability="AVAILABLE",
    status="READY", started_at=datetime(2026, 10, 1, 8, 5, 0), duration_ns=10**9,
)
db.add_all([parent, child]); db.flush()
run_id = "smoke-run-__SUFFIX__"
ver = SceneAnalysisVersion(
    parent_bag_uid=parent.bag_uid, scene_code="slope_smoke", analysis_version=run_id[:16],
    run_id=run_id, config_hash="e" * 64, result="SUCCESS", current=True,
)
db.add(ver); db.flush()
seg = SceneSegment(analysis_version_id=ver.id, label="slope", start_ns=1000, end_ns=2000,
                   duration_ns=1000, publish_target=True, slice_key="k-smoke")
db.add(seg); db.flush()
db.add(BagDerivation(parent_bag_uid=parent.bag_uid, child_bag_uid=child.bag_uid, run_id=run_id,
                     slice_key="k-smoke", scene_code="slope_smoke", analysis_version_id=ver.id,
                     segment_id=seg.id, start_ns=1000, end_ns=2000, duration_ns=1000))
scene = Scene(name="slope_smoke"); db.add(scene); db.flush()
db.add(BagSceneLabelEvidence(bag_uid=parent.bag_uid, scene_id=scene.id, label_source="MODEL",
                             analysis_version_id=ver.id, original_judgment_ref=f"{run_id}#seed123"))
db.commit()
print(json.dumps({"parent": parent.bag_uid, "child": child.bag_uid, "rv": child.row_version}))
"""
    seed = seed.replace("__DB__", DB).replace("__WORKTREE__", WORKTREE)
    seed = seed.replace("__SUFFIX_UPPER__", SUFFIX.upper()).replace("__SUFFIX__", SUFFIX)
    p = subprocess.run([f"{WORKTREE}/.venv/bin/python", "-c", seed], capture_output=True, text=True)
    if p.returncode != 0:
        print("SEED FAILED", p.stderr[-2000:])
        sys.exit(2)
    ids = json.loads(p.stdout.strip().splitlines()[-1])
    parent_uid, child_uid, rv = ids["parent"], ids["child"], ids["rv"]
    q = f"smoke-child-{SUFFIX}"

    # 1) 详情页：双表单+审计区
    st, html, _ = http(f"/bags/{child_uid}?return_to=/bags")
    check("detail 200", st == 200)
    check("detail has revise form", f"/bags/{child_uid}/scene-revise" in html)
    check("detail has withdraw form", f"/bags/{child_uid}/scene-withdraw" in html)
    check("detail has audit section", "审计记录" in html)
    check("detail has human panel", "人工纠错 / 下架" in html)
    check("detail not withdrawn before", "已下架" not in html)

    # 2) 页面纠错 → 303 flash + 审计
    st2, _, h2 = post_form(f"/bags/{child_uid}/scene-revise", {
        "scene_code": "slope_smoke", "corrected_label": "flat",
        "reason": "页面实测：人工复核为平地", "operator": "smoke-wang",
        "row_version": rv, "return_to": "/bags",
    })
    check("revise 303", st2 == 303, f"got {st2}")
    check("revise flash ok", "revision_flash=REVISE" in h2.get("location", ""), h2.get("location", ""))
    loc = h2["location"]
    st3, html3, _ = http(loc)
    check("revise flash rendered", "操作已记录" in html3)
    check("revise audit operator shown", "smoke-wang" in html3)
    check("revise audit reason shown", "页面实测：人工复核为平地" in html3)
    check("revise audit original ref shown", "slope#smoke-run-" in html3 or "seed123" in html3)

    # 3) 页面下架 → 303 flash + 已下架标注
    rv2 = rv + 1
    st4, _, h4 = post_form(f"/bags/{child_uid}/scene-withdraw", {
        "scene_code": "slope_smoke", "reason": "页面实测：时间窗口不符",
        "operator": "smoke-wang", "row_version": rv2, "return_to": "/bags",
    })
    check("withdraw 303", st4 == 303, f"got {st4}")
    check("withdraw flash ok", "revision_flash=WITHDRAW" in h4.get("location", ""))
    st5, html5, _ = http(h4["location"])
    check("withdraw flash rendered", "操作已记录" in html5)
    check("detail shows withdrawn badge", "已下架" in html5)

    # 4) 视图语义：默认 slices 表格行消失、all 仍在且标注
    st6, html6, _ = http(f"/bags?q={q}")
    check("default view 200", st6 == 200)
    check("default view row gone", q not in rows(html6))
    st7, html7, _ = http(f"/bags?view=all&q={q}")
    check("all view 200", st7 == 200)
    all_rows = rows(html7)
    check("all view row still present", q in all_rows)
    check("all view withdrawn mark", "已下架" in all_rows)

    # 5) 下架后表单面：下架表单消失、纠错表单仍在
    st8, html8, _ = http(f"/bags/{child_uid}?return_to=/bags")
    check("after withdraw: revise form still", f"/bags/{child_uid}/scene-revise" in html8)
    check("after withdraw: withdraw form gone", f"/bags/{child_uid}/scene-withdraw" not in html8)
    # 精确门禁：下架后不存在任何 re-activate 表单动作（scene-reactivate 端点本单未实现=普通重试不能重新上架）
    check("after withdraw: no reactivate action", "scene-reactivate" not in html8)

    # 错误回显：row_version 冲突
    st9, _, h9 = post_form(f"/bags/{child_uid}/scene-revise", {
        "scene_code": "slope_smoke", "corrected_label": "slope",
        "reason": "冲突用例", "operator": "smoke-wang", "row_version": 999, "return_to": "/bags",
    })
    check("conflict 303", st9 == 303)
    check("conflict error flash", "revision_error=" in h9.get("location", ""))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    os.unlink(DB)

summary = {"total": len(results), "passed": sum(1 for r in results if r["pass"]), "failed": sum(1 for r in results if not r["pass"])}
print(json.dumps(summary))
print(json.dumps(results, ensure_ascii=False, indent=1))
sys.exit(0 if summary["failed"] == 0 else 1)