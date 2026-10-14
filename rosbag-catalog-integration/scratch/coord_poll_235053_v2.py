#!/usr/bin/env python3
"""coord poll 235053 v2: robust JSON token parse; claim -> prepend HANDOFF -> event -> release."""
import json, os, subprocess, sys, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-235053"

def run(args):
    r = subprocess.run([sys.executable, RUNTIME] + args, capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def parse_obj(out):
    # try whole output, then each {...} block, then last { line onward
    try:
        return json.loads(out)
    except Exception:
        pass
    i = out.find("{")
    if i >= 0:
        try:
            return json.loads(out[i:])
        except Exception:
            pass
    return None

rc, out = run(["claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER])
d = parse_obj(out)
tok = (d or {}).get("token")
if not tok:
    # same-owner re-claim may be refused but token recoverable from lease file
    print("CLAIM rc=%d out=%s" % (rc, out[:600]))
    sys.exit(1)
print("CLAIM ok token=%s claimed=%s" % (tok, (d or {}).get("claimed_at")))

checkpoint = """## 2026-10-11 23:50 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T23:50:53+08:00：2号 TASK-10 驱动第 5 跑——VLM endpoint 404 已解（B 改完整路径 /v1/chat/completions），新失败=requests 模块缺失复发，harness 环境层在途）

- **23:33 后唯一业务变化 = 2号 TASK-10 端到端驱动推进至第 5 跑（`scratch/t10/t10-run.log` 23:50:55，距本轮 preflight 约 30 秒，在途迭代不催单不接管）**：run4 的 **VLM 根路径 404 已解**——B 将 `SLOPE_VLM_ENDPOINT` 从 `http://192.168.2.45:8002/` 改为完整路径 `http://192.168.2.45:8002/v1/chat/completions`（21:42 检查点 TASK-09 已实证该完整路径可用）；1a 冻结 `config_hash 0845b402…` OK / 1b register `source_id=84ACFA57…` matched=True / 1d 显式 POST fallback 生 `run_id=scene-e3d62c29…` / 3 claim OK → **3_analyze 新失败 `ModuleNotFoundError: No module named 'requests'`**（run3 曾解、run4 已正常走到 VLM 调用，run5 复发=**harness 环境/venv 层，非 app 代码缺陷**，B 在途处置）。
- **main 不变**：`ca8730d7050c105b73e9387f4adda182d3a14e64`（=origin/main，rev-parse 双核一致）；`wt-04a-t10` 零 commit（HEAD `ca8730d`，仅 `?? .venv` 未跟踪软链）；`receipts/TASK-10/` 不存在；本地栈 8 容器在位。
- **角色占用**：B=RUNNING（TASK-10 attempt-1 第 5 跑 harness 环境排查中，B 侧活动 23:50:55 最新）；A/C/TESTER 空闲（C 23:49:55 nochange 心跳，legacy_busy 空）；无 OCR/合入/新派单。
- **门禁**：TASK-11 生产启用维持未放行；TASK-07/12/13/14/15 维持 DEFERRED 不扩；P0 唯一在途单=TASK-10。requests 缺失属 B 侧驱动 harness 环境（不跨模块改 app 码）；若 B 定位属 app 侧依赖声明缺陷，按派单口径记录回派最小修。
- 本轮控制动作：claim（`cron-coord-poll-235053`）→巡检核查（scratch/t10 run.log 第 5 跑独立复核/rev-parse 双核/wt-04a-t10 零 commit/receipts 不存在/docker 8 容器/events 23:33 后仅 C nochange 心跳与上轮自身事件）→prepend 检查点+event→release。**无新派单、无合入、无 OCR、无状态回退**（TASK-10 维持 RUNNING，VLM 404 已解、requests 复发在途）。
- **下一步**：核 B harness 环境处置与驱动续跑（4/5 步：analyze→publish/06B 登记→API 获取）；交付即机械核验→串行 OCR（如有 app 面 §3.6 尺寸预检）→验收合入→TESTER 验证→**P0 收口**。连续多轮零活动才记停滞告警口径，不自动接管。
"""

handoff_path = os.path.join(ROOT, "HANDOFF.md")
with open(handoff_path) as f:
    handoff = f.read()
if "coord-poll-20261011-235053" in handoff.split("##")[0]:
    print("HANDOFF already prepended this round; skip")
else:
    with open(handoff_path, "w") as f:
        f.write(checkpoint + "\n" + handoff)
    print("HANDOFF prepended")

event = {
    "event_id": "coord-poll-20261011-235053-t10-run5-endpoint-fixed-requests-recur",
    "occurred_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "role": "COORDINATOR",
    "task": "TASK-10",
    "attempt": "1",
    "status": "RUNNING",
    "summary": "2号TASK-10驱动第5跑:VLM endpoint 404已解(B改完整路径/v1/chat/completions),新失败=requests模块缺失复发(harness环境层,非app缺陷),B在途处置;零交付零合入",
    "evidence": "scratch/t10/t10-run.log:23:50:55 (run5 FAIL 3_analyze ModuleNotFoundError: No module named 'requests'); wt-04a-t10 HEAD=ca8730d 零 commit; receipts/TASK-10 不存在",
    "next": "等2号harness环境修复与驱动续跑,交付即核验+OCR+合入+TESTER验证+P0收口"
}
epath = os.path.join(ROOT, "events/COORDINATOR", event["event_id"] + ".json")
if not os.path.exists(epath):
    with open(epath, "w") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)
    os.chmod(epath, 0o600)
print("event written", epath)

rc3, out3 = run(["release", "--project", ROOT, "--role", "COORDINATOR", "--token", tok])
print("RELEASE rc=%d" % rc3)
if rc3 != 0:
    print(out3[:500])
print("OK")