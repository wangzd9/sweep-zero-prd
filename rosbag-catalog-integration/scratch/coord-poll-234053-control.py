#!/usr/bin/env python3
import subprocess, json, sys
RUNTIME="/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT="/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER="cron-coord-poll-234053"
def sh(cmd):
    r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=120)
    return r.returncode,r.stdout,r.stderr
rc,out,err=sh(f"python3 {RUNTIME} claim --project {ROOT} --role COORDINATOR --owner {OWNER}")
print("CLAIM",rc,out[:200],err[:200])
try:
    tok=json.loads(out)["token"]
except Exception:
    tok=out.strip().split()[-1] if out.strip() else None
if not tok:
    print("NO TOKEN, abort"); sys.exit(1)
import subprocess as _sp
def run(*args):
    r=_sp.run(list(args),capture_output=True,text=True,timeout=120)
    return r.returncode,r.stdout,r.stderr
# prepend checkpoint to sessions/COORDINATOR.md
cp="""## 2026-10-11 23:40 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T23:40:53+08:00：23:25:53 后零交付零合入，2号 TASK-10 驱动第 4 跑推进至 3_analyze 失败，失败形态变化=VLM 根路径 404）

- **23:25:53 后零业务交付/零合入**：main HEAD `ca8730d`（= origin/main，rev-parse 双核一致）；`receipts/TASK-10/` 仍不存在；23:25:53 后共享根业务目录零新增（find -newermt 核实，仅 C 23:38 nochange 心跳与各角色 sessions/ticks）。
- **2号 TASK-10 attempt-1 端到端驱动第 4 跑推进（在途排查，不催单不接管）**：`scratch/t10/t10-run.log` 23:31:40 独立复核——1a 冻结 `0845b402…`（OK）/ 1b register 成功 `source_id=5D4CA9F8…` matched=True / 1d consume 仍无 run、显式 fallback 生 `run_id=scene-a837d694…` 冻结 config_hash（同第 3 跑）/ 3 claim SCENE_SLICE_QUEUE 成功（lease `676b0544…` attempt=1 gen=1，frozen_hash `a8ba9678…`）→ **新失败形态=3_analyze `MODEL_UNAVAILABLE：第 0 帧…模型请求失败：HTTPError: 404 …for url: http://192.168.2.45:8002/`**——与第 3 跑的 `ModuleNotFoundError: requests` 不同，现驱动已进真实 VLM 调用链但请求落在 **VLM 根路径（非 `/v1/chat/completions`）**，404 属 endpoint 拼接/配置问题（harness env 或 adapter 面待 B 判定）；findings #1（app 无 source_status setter，harness workaround）维持记录。协调侧受 cron 安全扫描限制无法代探该私有 IP 端点（BLOCKED），归 B 在驱动内实测。ps 无 B 侧业务进程（驱动失败退出，判 RUNNING 排查间隙）。
- **角色占用**：B=RUNNING（TASK-10 attempt-1 第 4 跑失败排查中，B tick report 存活）；A/C/TESTER 空闲（例行 tick；TESTER 23:42 短租约例行瞬态；legacy_busy 空）；leases 无他角色在途业务持有；`ocr.lock`/`coordinator.lock` 0 字节。
- **门禁**：TASK-11 生产启用维持未放行；TASK-07/12/13/14/15 维持 DEFERRED 不扩；3_analyze 404 若属 harness env（SLOPE_VLM_ENDPOINT 配置口径），B 修驱动即可；若涉 app 面（adapter URL 拼接）按派单口径定位+记录回派、不跨模块改码。
- 本轮控制动作：claim（`cron-coord-poll-234053`）→巡检核查（rev-parse 双核/find -newermt/scratch/t10 run.log+json 独立复核/wt-04a-t10 零 commit 复核/ticks/leases/ps）→prepend 检查点+event→release。**无新派单、无合入、无 OCR、无状态变更**（TASK-10 维持 RUNNING，3_analyze 失败形态演进在途排查）。
- **下一步**：每轮核 2号 TASK-10（wt-04a-t10 commit/回执 `receipts/TASK-10/`/scratch/t10 驱动进展）；交付即机械核验→串行 OCR→验收合入→TESTER 验证→**P0 收口**；多轮零活动则记停滞告警口径，不自动接管。
"""
p=f"{ROOT}/sessions/COORDINATOR.md"
cur=open(p).read()
open(p,"w").write(cp+"\n"+cur)
rc2,o2,e2=run("python3",RUNTIME,"run","--project",ROOT,"--role","COORDINATOR","--token",tok,"--",
    "python3",RUNTIME,"event","--project",ROOT,"--role","COORDINATOR","--token",tok,
    "--event-id","coord-poll-20261011-234053-t10-vlm-404-probing",
    "--task","TASK-10","--attempt","1","--status","RUNNING",
    "--summary","巡检:2号TASK-10驱动第4跑推进,3_analyze失败形态变化=VLM根路径404(非requests缺依赖),B在途排查,零交付零合入",
    "--evidence","scratch/t10/t10-run.log",
    "--next","等2号定位404(endpoint配置或adapter面),交付即核验+OCR+合入")
print("EVENT",rc2,o2,e2)
rc3,o3,e3=run("python3",RUNTIME,"release","--project",ROOT,"--role","COORDINATOR","--token",tok)
print("RELEASE",rc3,o3,e3)
print("DONE")