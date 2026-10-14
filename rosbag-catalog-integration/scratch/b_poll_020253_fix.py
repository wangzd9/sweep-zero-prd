import subprocess, sys, json

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "664a026193d24c59b230e4e55377ab38"
OWNER = "cron-b-poll-6f7471d8747c-20261012-020253"

line = (
    "- 巡检 2026-10-12 02:07 +08:00（cron poll，真实 checked_at 2026-10-12T02:02:53+08:00 preflight）："
    "**TESTER E2E 复跑 v2 驱动 01:59:14 收口：#3 修复真链生效；step5 lineage 404 + 原包 SOURCE_MODIFIED 疑误报（B 只读观察，无动作）**"
    "——01:58 观察后唯一业务变化=TESTER 01:57 ACK 复跑 v2（`e2e-reverify-v2-ack.md`：base `453da0c` 双核、驱动 step4 actual 边界已核、真实袋 row19 VLM≤1 袋）→ 驱动 01:57:50–01:59:14 收口（`scratch/t10/t10-run.log`）：analyze **SUCCESS 83s**（segments=1）、`derive_storage_offset=100381744` 非 None（**#2 生效**）、publish 1 切片（子包 `T10S22c76051fd384d17`）、`/results` **200**、`/complete-scene` **200 SCENE_DONE+AVAILABLE+switch**（**#3 修复点真链确认生效，v1 的 409 已消除**）；step5：`bags/{child_uid}`=200 非空可打开（files/topics 在案）但 **`lineage`=404**→ verdict 5_fetch=DEGRADED。**B 独立核两新事实（只读）**：① lineage 404=app 侧 `scene_result_query.py:296` lineage 服务已实现，但全仓 grep **无对应 HTTP 路由注册**（API 面仅 `GET /api/v1/bags/{bag_uid}`，sources.py:20；scene_results.py 仅 3 个 scene 端点）→ 404 是真实路由缺口（**疑新缺口 #4，06B 域**，待 TESTER 回执定位+协调者裁决回派，本侧不代修不扩做）；② `5_source_unchanged=SOURCE_MODIFIED` 疑驱动口径误报：`t10_e2e_reverify.py:97` before 对 <60MB 文件取**全量 sha256**、`:401` after 一律 **head1MB**，metadata.yaml（11KB）两口径必不等→ B 以同口径（head1MB/size/mtime）对 before 值独立重算 **7/7 MATCH=原包 ALL_UNCHANGED**（真实袋只读，NAS stat 复核 mtime/size 均 2026-08-19 原值）。**attempt-2 回执尚未落盘**（`test-receipts/TEST-TASK10-e2e-reverify/` 实测仍仅 attempt-1.md；dispatch 02:03 被 TESTER 改标 ACCEPTED=回执整理在途），ps 无 t10/pytest 驱动进程。`inbox/2号` 01:58 后零新增（**无新派单、无返修**）；main `453da0c`=origin/main fetch 双核；`wt-04a-t10d3` HEAD=`0943885` 冻结干净（仅 .venv 软链）；control=ACTIVE、legacy_busy 空、claim/release 正常（owner " + OWNER + "）。B 维持 **IDLE_WAITING**，不占开发槽。下一步：等 TESTER attempt-2 回执结论（PASS/FAIL+lineage 404 定位申报）；#4 若确认回派本侧则按 attempt 续单；空闲不扩需求。\n"
)
sp = f"{ROOT}/sessions/B.md"
with open(sp) as f:
    content = f.read()
assert "b-poll-20261012-020253" not in content
with open(sp, "w") as f:
    f.write(line + content)
print("SESSIONS prepended ok")

out2 = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                       "--role", "B", "--token", TOKEN],
                      capture_output=True, text=True)
print("RELEASE rc:", out2.returncode, out2.stdout[-200:], out2.stderr[-300:])