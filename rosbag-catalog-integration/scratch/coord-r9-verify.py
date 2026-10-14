"""rework-9 (c2cee73 vs 65ca0be) AST 全量比对 + 定向验证，供协调者独立核验。"""
import ast
import collections
import subprocess
import sys

WT = "/home/wang/.local/state/rosbag-scene/wt-04a-r9"
TARGET = "tests/test_scene_slice_scheduling.py"

def get_file(commit):
    return subprocess.run(
        ["git", "show", f"{commit}:{TARGET}"], cwd=WT, capture_output=True, check=True
    ).stdout.decode("utf-8")

old_src = get_file("65ca0be")
new_src = get_file("c2cee73")

def consts(src):
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Constant,)):
            out.append(repr(node.value))
        elif isinstance(node, ast.Str):
            out.append(repr(node.s))
    return out

def nonconst(src):
    tree = ast.parse(src)
    out = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Constant, ast.Str)):
            out += 1
    return out

co, cn = consts(old_src), consts(new_src)
ho, hn = collections.Counter(co), collections.Counter(cn)
diff = ho - hn
diff2 = hn - ho
print("consts old/new:", len(co), len(cn))
print("nonconst old/new:", nonconst(old_src), nonconst(new_src))
print("removed:", dict(diff))
print("added:", dict(diff2))

# docstring 差异应且仅应在这一条
removed_items = list(diff.elements())
added_items = list(diff2.elements())
if len(removed_items) != 1 or len(added_items) != 1:
    print("FAIL: expected exactly one docstring swap, got", len(removed_items), len(added_items))
    sys.exit(1)
r = removed_items[0]
a = added_items[0]
print("REMOVED_DOCSTRING_TAIL:", r[-200:])
print("ADDED_DOCSTRING_TAIL:", a[-260:])
if "无条件" in a or "零兼容风险" in a:
    print("FAIL: 旧无条件兼容声明残留")
    sys.exit(1)
if "已核实的存活库" not in a:
    print("FAIL: 新口径未落")
    sys.exit(1)

# ruff + 定向
for cmd in (
    [".venv/bin/ruff", "check", TARGET],
    [".venv/bin/python", "-m", "pytest", TARGET, "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
):
    p = subprocess.run(cmd, cwd=WT, capture_output=True, text=True)
    print("$", " ".join(cmd), "-> rc", p.returncode)
    tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
    print("\n".join(tail))
    if p.returncode != 0:
        sys.exit(2)

print("VERIFY_OK")