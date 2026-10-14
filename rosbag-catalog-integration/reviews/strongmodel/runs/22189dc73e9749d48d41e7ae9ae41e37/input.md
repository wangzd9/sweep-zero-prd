---
name: complex-task-reviewer
description: 复杂任务强模型纠错审查：用户手动提交或协调者在有效授权内通过Codex提交已完成功能/增量返修包时使用。按既定需求审真实代码和证据；不自动扩充任务、开发、合并或部署。
metadata:
  version: "1.2.0"
---

# 复杂任务独立审查者


你是按需工作的独立审查者，优先发现业务逻辑、跨模块契约、状态机、幂等、并发、恢复、错误发布和错误成功判定的问题。不是全程监督者，也不替代运行验证或弱 OCR。

## 功能纠错边界

- 默认审查已完成开发与常规测试的功能批次，按包内冻结的需求/AC、环境和阶段判断正确性。实现前契约审查仅在用户明确要求时进行。
- 每项发现标为 `CORRECTION`（原功能缺陷）、`VERIFICATION_GAP`（已有AC缺必要证据）或 `OUT_OF_SCOPE`（范围外建议）。前两类必须指出对应需求/AC或它直接蕴含的不变量；疑点标待验证。
- 阻塞项必须给预期/实际行为、触发、证据、错误后果、最小修复边界和解除条件；不能靠泛化风险或严重度标签增加任务。
- 只补保证原功能正确所需的修复与验证。新功能、未来规模、偏好式重构和额外质量标准不成为本轮要求；范围外建议单列且默认不派单、不阻塞，不因它们降级PASS。
- 必要上下游可以查，但须说明与当前错误的因果关系。模块不承担后续真实样本/生产阶段的验收；原有阶段门禁继续保留。
- 已有问题关闭且原AC满足就结束，不持续寻找无关改进。

## 审查流程

1. 读取审查包的 review_id、冻结需求/AC基线、已交付行为、具体待裁决问题、非范围、作用门禁、实际 base/target、契约版本及证据 commit。材料不足或快照不一致先明确与原AC相关的缺口，不只根据协调者摘要下结论。
2. 核对完整变更文件清单与可定位 diff，阅读关键实际代码、必要上下游和测试/成功条件修改；大材料按调用链取用，不机械截断文件或重读全部历史。
3. 核实成功前提、异常分类、状态/事务/释放顺序、并发唯一身份与当前版本、重试、文件与数据库一致性、时间精度/边界和 mock 掩盖的问题。疑点与确认缺陷分开；未执行测试如实写未执行。
4. 按 [结果模板](assets/result.md) 输出可执行问题：问题 ID/分类/严重度、对应需求/AC、预期与实际行为、代码位置及证据、触发、后果、最小修复边界、必要验证、阻塞与解除条件。避免风格清单、泛化架构扩张和整段重写。
5. 结论使用 PASS / PASS_WITH_FOLLOWUPS / REWORK_REQUIRED / INSUFFICIENT_EVIDENCE。声明通过的是契约、模块合入、集成、工程闭环或生产门禁；不能用模块通过替代缺真实时间映射/样本/故障证据的闭环。
6. 默认把结果写到约定路径；没有文件访问能力输出完整结果供保存并说明未写文件。不能编辑业务代码、合并或部署。

## 增量与费用

- 返修审查只看前轮问题 ID、修复 diff、对应测试及受影响上下文，复用有效的已接受材料。新发现只有证明破坏本批既定行为时才成为纠错项；无关建议不扩入复审范围。
- 结果绑定实际 commit 与契约版本；新逻辑不继承旧 PASS。非阻塞跟进要有 owner/阶段/解除条件。
- token/费用不可获取写未知，不猜测准确率或费用；记录确认缺陷、核实误报、遗漏、返修轮数及重复阅读情况。
- 审查由用户手动触发，或由协调者在用户明确授权的自定义时段/当前任务范围内通过限额脚本触发。自动起跑绑定grant_id/call_id，每次复审占额度；本审查者不续授权、不调用其他模型、不调起下一轮。
- Codex只读入口不能写约定文件时，返回完整最终结果，由调用脚本保存；不得声称自己已落盘。调用成功不代替协调者核验问题或批准。

## 协作流程文档维护（按需）

仅在用户要求修改本协作流程的Skill、脚本、协议或调度/显示规则时，按 [流程文档同步要求](../complex-task-coordinator/references/workflow-guide-maintenance.md) 更新 [统一开发流程指南](/home/wang/work/doc/SKILL-DEVELOPMENT-WORKFLOW.md) 的相关段落、图示和变更记录。普通开发/测试/审查/巡检不加载全文或更新它，发现差异按角色权限提交证据，不新增任务或授权。


You are a read-only reviewer authorized by the user. No code edits, model delegation, merges, deployments or extra review calls.

{"review_id": "SR-16B-R3-DIRECT-20261013", "grant_id": "6b2d83fb978644b7938424e4652024ce", "call_id": "22189dc73e9749d48d41e7ae9ae41e37", "base": "e1524657bda1f66f03034cb72ef05cd65e0c1dfc", "target": "15e4ef9094c7b51ec6f38832533c670d2664b985", "task": "TASK-16B", "gate": "原两项恢复CORRECTION未关闭不得合入", "risk": "原恢复补报与租约清除顺序", "question": "R1-02和R1-03是否关闭且Backend事务原子收尾是否正确", "AC": "原attempt仅补报不重复模型;七步确认后complete;REGISTER同事务DONE后清租约;默认提交hash正常一致"}

Return the complete independent result as your final message; the wrapper writes it. Do not try to write a result file in the read-only sandbox. Freeze existing requirements; OUT_OF_SCOPE suggestions do not block.

The following is the frozen review package. Read actual code in this detached snapshot and the cited verification evidence; do not merely trust the summary.

# TASK-16B R3直接修复增量复核

固定base=e152465，target=15e4ef9094c7b51ec6f38832533c670d2664b985。用户要求Codex直接修复收尾上线，grant6b2d83fb仍有效。仅核原R1-02/03未关闭问题及必要Backend事务链；R1-01/04/05已关闭，不重审全量。审查树含部署只读挂载修复，由常规OCR覆盖；本强审重点恢复/租约/后端终态。

R1-02：_report_steps返回最终确认；失败/GET持续错不删恢复台账。R1-03：先持久FINALIZING_FAILURE/SUCCESS意图，恢复仅补报不再执行业务。成功七步先确认，Backend complete同事务将REGISTER推进DONE后清租约；新增flush支持缺REGISTER且autoflush=False。

另真实E2E发现正常默认提交hash与proxy不一致，因registry(None)默认15整数绕过正规化，Backend空参数正规化成15.0；proxy最小改为{}，保留hash failclosed；不改全局registry或旧坡道hash。新增真实Registry默认参数回归修前spray FAIL/slope PASS，修后13恢复/参数+11接线共24PASS，生产无写入。

独立验证：修前5失败→修后11严格Backend故障注入PASS，proxy/orchestrator50PASS；Backend真实事务新增8例，相关组94PASS；终态后step拒绝、恢复新增模型调用0、回滚不留半成品。报告test-receipts/TEST-TASK16B-r3/codex-independent-20261013.md。最终集成候选6ddcbcb含已审B f76e2a9、main6c7d983及已审C接线92dcb52；真实模型全链另行执行，不预报PASS。

请仅裁原两问题是否关闭及本变更必需调用链中可复现的CORRECTION/VERIFICATION_GAP；给触发步骤和最小修复。风格/文件大小/新可用性标准不扩本期需求。本强审不替代弱OCR或真实全链。

## 固定变更

```diff
diff --git a/app/services/scene_result_report_service.py b/app/services/scene_result_report_service.py
index 156f8e7..a53c59d 100644
--- a/app/services/scene_result_report_service.py
+++ b/app/services/scene_result_report_service.py
@@ -71,7 +71,12 @@ from app.scene.types import SceneSegment as SegType
 from app.services import scene_result_service
 from app.services.control_plane import idempotent_replay, store_idempotency
 from app.services.scene_result_query import list_segments
-from app.services.scene_slice_service import PIPELINE_TYPE_SCENE_SLICE, finish_scene_run, record_scene_outcome
+from app.services.scene_slice_service import (
+    PIPELINE_TYPE_SCENE_SLICE,
+    finish_scene_run,
+    record_scene_outcome,
+    update_scene_step,
+)
 from app.services.source_fence import check_fence_for_source
 
 # 05 提交时分配的版本占位格式（allocate_analysis_version：av{N}）；
@@ -691,6 +696,19 @@ def complete_scene(db: Session, pipeline_run_id: str, payload: dict) -> dict:
     all_reported = set(expected_scenes) <= reported
     finished = None
     if all_reported:
+        # REGISTER与登记/激活同事务收敛。finish_scene_run随后清租约，代理
+        # 不能在complete之后再补写此步骤；事务回滚也不能留下假DONE。
+        from app.models import StepRun
+
+        register = db.scalar(select(StepRun).where(
+            StepRun.pipeline_run_id == run.pipeline_run_id,
+            StepRun.step_name == "REGISTER", StepRun.attempt == run.attempt,
+        ).with_for_update())
+        if register is None or register.status == "QUEUED":
+            update_scene_step(db, run, "REGISTER", "RUNNING", lease_token=payload.get("lease_token"))
+            db.flush()
+        if register is None or register.status in ("QUEUED", "RUNNING"):
+            update_scene_step(db, run, "REGISTER", "DONE", lease_token=payload.get("lease_token"))
         finished = finish_scene_run(db, run, payload.get("lease_token"))
     # R2-04：登记 + 场景结果 + 终态（若）+ 换版 在同一事务内收敛；
     # 换版 409（晚到旧版）→ 登记/终态/可用性保留，换版如实 409。
diff --git a/scripts/scene_host_proxy.py b/scripts/scene_host_proxy.py
index 825592b..1af2337 100644
--- a/scripts/scene_host_proxy.py
+++ b/scripts/scene_host_proxy.py
@@ -50,6 +50,7 @@ import time
 from dataclasses import dataclass
 from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
 from pathlib import Path
+from types import SimpleNamespace
 
 SCRIPT_DIR = Path(__file__).resolve().parent
 for _p in (SCRIPT_DIR.parent, SCRIPT_DIR,):
@@ -335,9 +336,9 @@ class ProxyBackendReporter:
         )
 
     def complete_scene(self, *, manifest, child_bag_uids, publish_root) -> dict:
-        return self._b.complete_scene(
-            self._run_id,
-            {
+        detail = self._b.run_detail(self._run_id)
+        attempt = int(detail["attempt"])
+        payload = {
                 "scene_code": self._scene_code,
                 "lease_token": self._token,
                 "source_generation": self._gen,
@@ -345,9 +346,36 @@ class ProxyBackendReporter:
                 "child_bag_uids": child_bag_uids,
                 "publish_root": str(self._cfg.publish_root) or None,
                 "vehicle_key": self._vehicle,
-            },
-            idem=f"{self._run_id}:{self._digest(manifest)}:complete",
-        )
+            }
+        work_root = self._cfg.work_root_base / self._run_id / f"attempt-{attempt}"
+        _save_finalization(self._cfg, self._run_id, attempt, self._token,
+                           stage="FINALIZING_SUCCESS", work_root=work_root,
+                           complete_payload=payload,
+                           complete_idem=f"{self._run_id}:{self._digest(manifest)}:complete")
+        # complete-scene会清任务租约，七步必须在此前确认；REGISTER由Backend
+        # 与complete同事务落终态，不能在终态后假设旧token还能写步骤。
+        if not _report_steps(self._b, run_id=self._run_id, attempt=attempt,
+                             lease_token=self._token, work_root=work_root,
+                             terminal_step="REGISTER"):
+            raise FinalizationPending("步骤尚未确认，保留完成意图待对账")
+        try:
+            return self._b.complete_scene(self._run_id, payload,
+                                          idem=f"{self._run_id}:{self._digest(manifest)}:complete")
+        except Exception as exc:
+            raise FinalizationPending(f"complete-scene尚未确认：{exc}") from exc
+
+
+class FinalizationPending(RuntimeError):
+    """执行结果已形成，仅待Backend对账；禁止回到业务执行或改报业务失败。"""
+
+
+def _save_finalization(cfg, run_id, attempt, lease_token, *, stage, work_root=None, **facts):
+    state = _read_json(state_path(cfg, run_id)) or {}
+    state.update({"version": "scene-proxy-recovery-v1", "pipeline_run_id": run_id,
+                  "attempt": attempt, "lease_token": lease_token, "stage": stage,
+                  "identity": _process_identity(), "updated_at": time.time(),
+                  "finalization": {"work_root": str(work_root) if work_root else None, **facts}})
+    _write_json_atomic(state_path(cfg, run_id), state)
 
 
 # ---------------------------------------------------------------------------
@@ -421,8 +449,9 @@ def resolve_spec(
 
     from app.scene import get_registry
 
-    eff = get_registry().effective_params(scene_code, None, cap_version)
-    # H5：Backend 按提交时参数冻结 capability_config_hash；此处 raw=None 用默认值
+    # 与 Backend 默认提交的参数正规化一致（例如 float 默认 15 应为 15.0）。
+    eff = get_registry().effective_params(scene_code, {}, cap_version)
+    # H5：Backend 按提交时参数冻结 capability_config_hash；此处空参数用默认值
     # 重推，非默认参数 run 会在烧完模型后 REGISTER 才 409 CONFIG_MISMATCH——
     # 快照 entry 不存提交参数、无法按提交值重推，按派单取 fail-fast 下限
     frozen_hash = entry.get("capability_config_hash")
@@ -470,7 +499,7 @@ def _report_steps(
     error_step: str | None = None,
     error_detail: str = "",
     terminal_step: str | None = None,
-) -> None:
+) -> bool:
     """把编排 checkpoint 台账映射回 Backend 既有八步 StepRun（03B 已建行）。
 
     状态机约束（app/domain/transitions.py）：QUEUED→RUNNING→{DONE,FAILED}，
@@ -487,7 +516,7 @@ def _report_steps(
         ledger = _read_json(checkpoint)
     steps_map = (ledger or {}).get("steps")
     if not isinstance(steps_map, dict) or not steps_map:
-        return
+        return True
     try:
         current = {
             s["step_name"]: s["status"]
@@ -593,6 +622,23 @@ def _report_steps(
             # 失败后的后续步：编排台账保持 PENDING（未执行）→ Backend 落 SKIPPED
             if allowed(current.get(name), "SKIPPED"):
                 post(name, "SKIPPED", f"SKIPPED after {error_step} failure")
+    # 不以post无异常或一次补报代替最终确认。持续失败/GET失败向收尾调用方
+    # 返回False，持久台账保留，run仍保有租约时才允许后续补报。
+    try:
+        actual = {s["step_name"]: s["status"]
+                  for s in backend.run_detail(run_id).get("steps") or []
+                  if s.get("attempt") == attempt}
+    except Exception:
+        return False
+    for name in STEPS:
+        if name == terminal_step:
+            continue
+        expected = (steps_map.get(name) or {}).get("status")
+        if expected == "PENDING" and error_step in STEPS and STEPS.index(name) > STEPS.index(error_step):
+            expected = "SKIPPED"
+        if expected in ("DONE", "FAILED", "SKIPPED") and actual.get(name) != expected:
+            return False
+    return True
 
 
 def _report_step_single(
@@ -789,6 +835,12 @@ def execute_run(cfg: ProxyConfig, backend: Backend, payload: dict) -> None:
                         accepted_at=payload.get("accepted_at") or time.time())
     try:
         manifest, _steps = SceneHostOrchestrator().run(spec)
+    except FinalizationPending as exc:
+        print(f"scene finalization pending {run_id}: {exc}", flush=True)
+        _stop_threads(stop_cancel)
+        _release_resource(cfg, resource_token)
+        ACTIVE.remove(run_id)
+        return
     except SceneExecError as exc:
         # 失败归因：步骤 + 错误保留（不当 NO_MATCH）；停写信号（取消/租约失效）
         # 经 spec.stop_event 协作式触发 adapter 抛出 CANCELLED → 走取消收尾。
@@ -797,10 +849,9 @@ def execute_run(cfg: ProxyConfig, backend: Backend, payload: dict) -> None:
             _finish_cancelled(cfg, backend, run_id, attempt, lease_token, resource_token, stop_cancel,
                               note=f"停写信号({reason})后编排退出：{exc}")
             return
-        _report_steps(backend, run_id=run_id, attempt=attempt, lease_token=lease_token,
-                      work_root=spec.work_root, error_step=exc.step, error_detail=f"{exc.code}: {exc.detail}")
         _finish_failure(cfg, backend, run_id, attempt, lease_token, resource_token,
-                        spec, _prefixed_error(reason, f"{exc.code}: {exc.detail}"), stop_cancel, reason, stage=stage)
+                        spec, _prefixed_error(reason, f"{exc.code}: {exc.detail}"), stop_cancel, reason,
+                        stage=stage, error_step=exc.step)
         return
     except Exception as exc:  # 编排外异常（含取消中断）
         reason = stop_reason["value"]
@@ -821,12 +872,6 @@ def execute_run(cfg: ProxyConfig, backend: Backend, payload: dict) -> None:
     # 成功路径：七步台账先回报（此时任务租约仍有效——REGISTER 内的
     # complete-scene 会触发 finish_scene_run 清租约切终态，之后再写步骤会 409）；
     # REGISTER 步在终态后补报，失败按预期留痕不视为执行失败。
-    _report_steps(backend, run_id=run_id, attempt=attempt, lease_token=lease_token,
-                  work_root=spec.work_root, terminal_step="REGISTER")
-    # 终态由 complete-scene（REGISTER 内）经 Backend finish_scene_run 驱动；
-    # 此处仅收尾：补报 REGISTER 步（容忍 409）→ 释放资源租约 → 清恢复文件。
-    _report_step_single(backend, run_id=run_id, attempt=attempt, lease_token=lease_token,
-                        name="REGISTER", work_root=spec.work_root)
     _finish_success(cfg, backend, run_id, attempt, lease_token, resource_token, spec, stop_cancel)
 
 
@@ -853,7 +898,9 @@ def _finish_success(cfg: ProxyConfig, backend: Backend, run_id: str, attempt: in
     print(f"scene run {run_id} attempt {attempt} finished: outcome reported via complete-scene", flush=True)
     _stop_threads(stop_cancel)
     _release_resource(cfg, resource_token)
-    clear_recovery_state(cfg, run_id)
+    if _report_steps(backend, run_id=run_id, attempt=attempt, lease_token=lease_token,
+                     work_root=spec.work_root, terminal_step="REGISTER"):
+        clear_recovery_state(cfg, run_id)
     ACTIVE.remove(run_id)
 
 
@@ -890,13 +937,24 @@ def _confirm_terminal(backend: Backend, run_id: str, lease_token: str,
 
 def _finish_failure(cfg: ProxyConfig, backend: Backend, run_id: str, attempt: int,
                     lease_token: str, resource_token: str | None, spec: SceneExecSpec | None,
-                    error: str, stop_cancel: threading.Event, reason: str, stage: str) -> None:
+                    error: str, stop_cancel: threading.Event, reason: str, stage: str,
+                    error_step: str | None = None) -> None:
     print(f"scene run {run_id} attempt {attempt} FAILED at {stage}: {error}", flush=True)
-    _stop_threads(stop_cancel)
+    _save_finalization(cfg, run_id, attempt, lease_token, stage="FINALIZING_FAILURE",
+                       work_root=spec.work_root if spec is not None else None,
+                       target="SCENE_FAILED", error=error, error_step=error_step)
+    if spec is not None and not _report_steps(
+            backend, run_id=run_id, attempt=attempt, lease_token=lease_token,
+            work_root=spec.work_root, error_step=error_step, error_detail=error):
+        _stop_threads(stop_cancel)
+        _release_resource(cfg, resource_token)
+        ACTIVE.remove(run_id)
+        return
     # R1-03：先对账确认终态再决定清不清恢复台账——上报未提交/响应丢失时
     # run 停 SCENE_RUNNING 且台账被删 = 重启失恢复入口（phantom run）；
     # 未确认则保留台账留痕，recover_pending_runs 重启后按原身份重新对账续收尾
     confirmed = _confirm_terminal(backend, run_id, lease_token, "SCENE_FAILED", error)
+    _stop_threads(stop_cancel)
     _release_resource(cfg, resource_token)
     if confirmed:
         clear_recovery_state(cfg, run_id)
@@ -938,6 +996,34 @@ def _finish_cancelled(cfg: ProxyConfig, backend: Backend, run_id: str, attempt:
 # ---------------------------------------------------------------------------
 # 启动恢复：旧写者终止核验后按原身份续跑（不重新 ACK、不产生第二写者）
 # ---------------------------------------------------------------------------
+def _resume_finalization(cfg: ProxyConfig, backend: Backend, state: dict) -> None:
+    run_id = state["pipeline_run_id"]
+    attempt = int(state["attempt"])
+    facts = state.get("finalization") or {}
+    try:
+        detail = backend.run_detail(run_id)
+        if int(detail.get("attempt", 0)) != attempt:
+            # 新attempt拥有写权，旧收尾只保留审计依据，绝不写入或重执行。
+            return
+        work = Path(facts["work_root"]) if facts.get("work_root") else None
+        if state["stage"] == "FINALIZING_FAILURE":
+            _finish_failure(cfg, backend, run_id, attempt, state["lease_token"],
+                            state.get("resource_lease_token"),
+                            SimpleNamespace(work_root=work) if work else None,
+                            str(facts.get("error") or ""), threading.Event(), "none",
+                            stage="RECOVERING_FINALIZATION", error_step=facts.get("error_step"))
+        elif work is not None and _report_steps(
+                backend, run_id=run_id, attempt=attempt, lease_token=state["lease_token"],
+                work_root=work, terminal_step="REGISTER"):
+            # 相同幂等身份的complete可对账已提交丢响应；不重做模型、发布或results。
+            backend.complete_scene(run_id, facts["complete_payload"], idem=facts["complete_idem"])
+            clear_recovery_state(cfg, run_id)
+    except Exception as exc:
+        print(f"scene finalization remains pending {run_id}: {exc}", flush=True)
+    finally:
+        ACTIVE.remove(run_id)
+
+
 def recover_pending_runs(cfg: ProxyConfig, backend: Backend) -> int:
     recovered = 0
     if not cfg.state_root.is_dir():
@@ -955,6 +1041,12 @@ def recover_pending_runs(cfg: ProxyConfig, backend: Backend) -> int:
             # 旧写者仍存活 → 不接管，留痕等待下轮
             print(f"scene recovery skipped, writer still alive: {run_id} {identity}", flush=True)
             continue
+        if state.get("stage") in ("FINALIZING_FAILURE", "FINALIZING_SUCCESS"):
+            if ACTIVE.try_reserve(run_id, {"stage": "RECOVERING_FINALIZATION", "attempt": state.get("attempt")}):
+                threading.Thread(target=_resume_finalization, args=(cfg, backend, state),
+                                 daemon=True, name=f"scene-finalize-{run_id}").start()
+                recovered += 1
+            continue
         # 对账：Backend 当前状态决定是否续跑
         try:
             detail = backend.run_detail(run_id)
@@ -1062,6 +1154,17 @@ def build_server(cfg: ProxyConfig, backend: Backend):
                     self._reply(409, {"error": f"another attempt is active for {run_id}"})
                 return
             # 台账先落盘（进程身份+检查点）再返回 accepted——派发响应丢失也据此对账
+            pending = _read_json(state_path(cfg, run_id)) or {}
+            if pending.get("stage") in ("FINALIZING_FAILURE", "FINALIZING_SUCCESS"):
+                if pending.get("attempt") != attempt or pending.get("lease_token") != token:
+                    ACTIVE.remove(run_id)
+                    self._reply(409, {"error": "pending finalization belongs to another attempt/token"})
+                    return
+                threading.Thread(target=_resume_finalization, args=(cfg, backend, pending),
+                                 daemon=True, name=f"scene-finalize-{run_id}").start()
+                self._reply(202, {"accepted": True, "finalizing": True,
+                                  "pipeline_run_id": run_id, "attempt": attempt})
+                return
             try:
                 save_recovery_state(
                     cfg, run_id=run_id, attempt=attempt, lease_token=token,
@@ -1125,4 +1228,4 @@ def main() -> int:
 
 
 if __name__ == "__main__":
-    raise SystemExit(main())
\ No newline at end of file
+    raise SystemExit(main())
diff --git a/tests/test_scene_completion_register_atomic.py b/tests/test_scene_completion_register_atomic.py
new file mode 100644
index 0000000..6a6dee3
--- /dev/null
+++ b/tests/test_scene_completion_register_atomic.py
@@ -0,0 +1,160 @@
+"""通过真实 API 和 SQLite 验证 complete-scene 的 REGISTER 原子收敛。"""
+
+from __future__ import annotations
+
+import json
+
+import pytest
+from fastapi.testclient import TestClient
+from sqlalchemy import delete, select
+
+from app.database import Base, SessionLocal, engine
+from app.main import app
+from app.models import BagDerivation, PipelineEvent, PipelineRun, SceneAnalysisVersion, StepRun
+from app.services import scene_result_report_service
+from tests import test_scene_result_report as fixtures
+
+
+@pytest.fixture
+def setup_run():
+    Base.metadata.create_all(engine)
+    with TestClient(app) as client:
+        with SessionLocal() as db:
+            parent = fixtures._parent(db, "atomic")
+        run_ids = []
+
+        def create(*, multi=False):
+            scenes = [{"scene_code": "slope"}]
+            if multi:
+                scenes.append({"scene_code": "test-capability"})
+            response = client.post("/api/v1/scene-analysis-runs", json={"source_id": parent.bag_uid, "scenes": scenes})
+            assert response.status_code == 202, response.text
+            run_id = response.json()["pipeline_run_id"]
+            run_ids.append(run_id)
+            return fixtures._claim_specific(client, run_id)
+
+        yield client, parent, create
+        with SessionLocal() as db:
+            # lineage 测试会开启 SQLite 外键；先删本测试的血缘，避免反向引用 segment。
+            child_uids = db.scalars(select(BagDerivation.child_bag_uid).where(BagDerivation.run_id.in_(run_ids))).all()
+            db.execute(delete(BagDerivation).where(BagDerivation.run_id.in_(run_ids)))
+            fixtures._purge(db, [parent.bag_uid, *child_uids], run_ids)
+
+
+def _stored_state(run_id):
+    with SessionLocal() as db:
+        run = db.scalar(select(PipelineRun).where(PipelineRun.pipeline_run_id == run_id))
+        steps = db.scalars(
+            select(StepRun).where(StepRun.pipeline_run_id == run_id, StepRun.step_name == "REGISTER")
+        ).all()
+        events = db.scalars(select(PipelineEvent).where(PipelineEvent.pipeline_run_id == run_id)).all()
+        register_events = [
+            event.event_type
+            for event in events
+            if event.event_type.startswith("SCENE_STEP_")
+            and json.loads(event.payload_json).get("step_name") == "REGISTER"
+        ]
+        return {
+            "status": run.status,
+            "lease": (run.lease_owner, run.lease_token_hash, run.lease_expires_at),
+            "steps": [(step.status, step.started_at, step.finished_at) for step in steps],
+            "events": register_events,
+        }
+
+
+@pytest.mark.parametrize("outcome", ["SUCCESS", "NO_MATCH"])
+@pytest.mark.parametrize("initial", ["QUEUED", "RUNNING", "MISSING"])
+def test_complete_finishes_register_before_lease_release(setup_run, tmp_path, outcome, initial):
+    client, parent, create = setup_run
+    run = create()
+    run_id = run["pipeline_run_id"]
+    with SessionLocal() as db:
+        register = db.scalar(select(StepRun).where(StepRun.pipeline_run_id == run_id, StepRun.step_name == "REGISTER"))
+        if initial == "MISSING":
+            db.delete(register)
+        elif initial == "RUNNING":
+            register.status = "RUNNING"
+        db.commit()
+    if outcome == "SUCCESS":
+        segs = [("slope", (fixtures.BASE_S + 2) * fixtures.NANO, (fixtures.BASE_S + 4) * fixtures.NANO)]
+        publish_root, child_map, manifest = fixtures._stage_and_publish(tmp_path, run, parent, segs)
+    else:
+        publish_root, child_map = None, {}
+        manifest = fixtures._manifest_dict(run, parent, outcome="NO_MATCH", segments=[], expected=[])
+    body = fixtures._complete_body(
+        fixtures._report_body(run, parent, manifest=manifest, child_map=child_map), publish_root=publish_root
+    )
+    response = client.post(fixtures._base_url(run_id, "complete-scene"), json=body)
+    assert response.status_code == 200, response.text
+    state = _stored_state(run_id)
+    assert state["status"] == "SCENE_DONE"
+    assert state["lease"] == (None, None, None)
+    assert len(state["steps"]) == 1
+    assert state["steps"][0][0] == "DONE"
+    assert state["steps"][0][2] is not None
+    assert state["events"] == (
+        ["SCENE_STEP_DONE"] if initial == "RUNNING" else ["SCENE_STEP_RUNNING", "SCENE_STEP_DONE"]
+    )
+    replay = client.post(fixtures._base_url(run_id, "complete-scene"), json={**body, "lease_token": None})
+    assert replay.status_code == 200, replay.text
+    assert replay.json()["replayed"] is True
+    assert _stored_state(run_id) == state
+
+
+def test_complete_failure_rolls_back_register_run_and_lease(setup_run, monkeypatch):
+    client, parent, create = setup_run
+    run = create()
+    run_id = run["pipeline_run_id"]
+    before = _stored_state(run_id)
+    manifest = fixtures._manifest_dict(run, parent, outcome="NO_MATCH", segments=[], expected=[])
+    body = fixtures._report_body(run, parent, manifest=manifest, child_map={})
+    original_finish = scene_result_report_service.finish_scene_run
+
+    def fail_after_finish(db, stored_run, lease_token):
+        original_finish(db, stored_run, lease_token)
+        db.flush()
+        raise RuntimeError("注入：终态写入后、提交前失败")
+
+    with monkeypatch.context() as patch:
+        patch.setattr(scene_result_report_service, "finish_scene_run", fail_after_finish)
+        with pytest.raises(RuntimeError, match="注入"):
+            client.post(fixtures._base_url(run_id, "complete-scene"), json=body)
+    assert _stored_state(run_id) == before
+    with SessionLocal() as db:
+        versions = db.scalars(select(SceneAnalysisVersion).where(SceneAnalysisVersion.run_id == run_id)).all()
+        assert len(versions) == 1
+        assert versions[0].current is False
+        assert versions[0].analysis_version.startswith("av")
+    retry = client.post(fixtures._base_url(run_id, "complete-scene"), json=body)
+    assert retry.status_code == 200, retry.text
+    assert _stored_state(run_id)["steps"][0][0] == "DONE"
+
+
+def test_multi_scene_register_waits_for_last_completion(setup_run):
+    client, parent, create = setup_run
+    run = create(multi=True)
+    run_id = run["pipeline_run_id"]
+    before = _stored_state(run_id)
+    manifest = fixtures._manifest_dict(run, parent, outcome="NO_MATCH", segments=[], expected=[])
+    body = fixtures._report_body(run, parent, manifest=manifest, child_map={})
+    first = client.post(fixtures._base_url(run_id, "complete-scene"), json=body)
+    assert first.status_code == 200, first.text
+    assert first.json()["run_finalized"] is False
+    assert _stored_state(run_id) == before
+    v2, h2 = fixtures._cap2()
+    second_manifest = {
+        **manifest,
+        "scene_code": "test-capability",
+        "capability_version": v2,
+        "config_hash": h2,
+        "outcome": "NOT_APPLICABLE",
+    }
+    last = client.post(
+        fixtures._base_url(run_id, "complete-scene"),
+        json={**body, "scene_code": "test-capability", "manifest": second_manifest},
+    )
+    assert last.status_code == 200, last.text
+    assert last.json()["run_finalized"] is True
+    state = _stored_state(run_id)
+    assert state["steps"][0][0] == "DONE"
+    assert state["lease"] == (None, None, None)
diff --git a/tests/test_scene_host_proxy_r3.py b/tests/test_scene_host_proxy_r3.py
new file mode 100644
index 0000000..9abe471
--- /dev/null
+++ b/tests/test_scene_host_proxy_r3.py
@@ -0,0 +1,398 @@
+"""R3 独立故障回归：终态补报恢复必须保留租约、且不得再次执行业务。"""
+
+from __future__ import annotations
+
+import copy
+import json
+import sys
+import threading
+from pathlib import Path
+from types import SimpleNamespace
+
+import pytest
+
+ROOT = Path(__file__).resolve().parents[1]
+sys.path.insert(0, str(ROOT / "scripts"))
+import scene_host_proxy as proxy  # noqa: E402
+
+
+class StrictBackend:
+    """模拟真实 Backend 的步骤状态机、同 attempt 和终态清租约约束。"""
+
+    def __init__(self):
+        self.run_status = "SCENE_RUNNING"
+        self.steps = {name: "QUEUED" for name in proxy.STEPS}
+        self.steps["PRECHECK"] = "RUNNING"
+        self.fail_step_terminal = False
+        self.fail_reads = False
+        self.fail_status = False
+        self.lose_step_response = False
+        self.lose_status_response = False
+        self.calls = []
+        self.terminal_step_attempts = 0
+        self.lease_live = True
+        self.fail_complete = False
+        self.lose_complete_response = False
+        self.completed_idem = set()
+
+    def run_detail(self, run_id):
+        if self.fail_reads:
+            raise TimeoutError("注入 GET 持续超时")
+        return {
+            "pipeline_run_id": run_id,
+            "status": self.run_status,
+            "attempt": 1,
+            "pipeline_type": "SCENE_SLICE",
+            "source_id": "source-r3",
+            "steps": [{"step_name": n, "status": s, "attempt": 1} for n, s in self.steps.items()],
+        }
+
+    def step(self, run_id, name, status, attempt, lease_token, error=""):
+        from app.domain.transitions import STEP_TRANSITIONS
+
+        self.calls.append(("step", name, status, attempt))
+        if not self.lease_live:
+            self.terminal_step_attempts += 1
+            raise RuntimeError("409: terminal run lease cleared")
+        assert attempt == 1 and lease_token == "token-r3"
+        if self.fail_step_terminal and status in {"DONE", "FAILED"}:
+            raise TimeoutError("注入步骤终态持续未提交")
+        current = self.steps[name]
+        if current != status and status not in STEP_TRANSITIONS.get(current, set()):
+            raise RuntimeError(f"409: forbidden step transition {current} -> {status}")
+        self.steps[name] = status
+        if self.lose_step_response and status in {"DONE", "FAILED"}:
+            self.lose_step_response = False
+            raise TimeoutError("注入步骤已提交丢响应")
+
+    def status(self, run_id, target, lease_token, error=""):
+        self.calls.append(("status", target, error))
+        assert lease_token == "token-r3"
+        if self.fail_status:
+            raise TimeoutError("注入失败终态持续未提交")
+        self.run_status = target
+        if target in proxy._TERMINAL_RUN_STATUSES:
+            self.lease_live = False
+        if self.lose_status_response:
+            self.lose_status_response = False
+            raise TimeoutError("注入失败终态已提交丢响应")
+        return {"status": target}
+
+    def complete_scene(self, run_id, payload, *, idem):
+        # 与Backend幂等回放顺序一致：已提交请求先回放，再核新写入租约。
+        self.calls.append(("complete", idem))
+        if idem in self.completed_idem:
+            return {"run_status": "SCENE_DONE"}
+        if self.fail_complete:
+            raise TimeoutError("注入complete持续未提交")
+        assert self.lease_live, "新complete请求必须持有有效租约"
+        assert all(self.steps[n] == "DONE" for n in proxy.STEPS if n != "REGISTER")
+        self.steps["REGISTER"] = "DONE"
+        self.run_status = "SCENE_DONE"
+        self.lease_live = False
+        self.completed_idem.add(idem)
+        if self.lose_complete_response:
+            self.lose_complete_response = False
+            raise TimeoutError("注入complete已提交丢响应")
+        return {"run_status": "SCENE_DONE"}
+
+
+@pytest.fixture
+def recovery_case(tmp_path, monkeypatch):
+    cfg = proxy.ProxyConfig(
+        backend_url="http://unused",
+        bind="127.0.0.1",
+        port=0,
+        state_root=tmp_path / "state",
+        work_root_base=tmp_path / "work",
+        publish_root=tmp_path / "publish",
+        ready_root=str(tmp_path / "ready"),
+        min_free_bytes=0,
+        cancel_poll_seconds=30,
+        heartbeat_interval_seconds=30,
+        heartbeat_fail_budget=4,
+        lease_ttl_seconds=120,
+    )
+    run_id = "independent-r3"
+    work = cfg.work_root_base / run_id / "attempt-1"
+    work.mkdir(parents=True)
+    backend = StrictBackend()
+    monkeypatch.setattr(proxy, "_release_resource", lambda *args: None)
+    monkeypatch.setattr(proxy, "_writer_stopped", lambda identity: True)
+    monkeypatch.setattr(proxy, "_lease_watchdog", lambda *args: None)
+    monkeypatch.setattr(proxy, "_cancellation_watchdog", lambda *args: None)
+
+    # 同步执行实际恢复入口，避免测试对线程调度时间产生偶然依赖。
+    class InlineThread:
+        def __init__(self, *, target, args=(), **kwargs):
+            self.target, self.args = target, args
+
+        def start(self):
+            self.target(*self.args)
+
+    monkeypatch.setattr(proxy.threading, "Thread", InlineThread)
+    model_calls = []
+    spec = SimpleNamespace(work_root=work, run_id=run_id, attempt=1)
+    monkeypatch.setattr(proxy, "resolve_spec", lambda *args, **kwargs: (spec, backend.run_status))
+
+    def unexpected_business(*args, **kwargs):
+        model_calls.append("业务编排被重新调用")
+        raise proxy.SceneExecError("MODEL_FAILED", "禁止恢复重入模型", step="INFER")
+
+    monkeypatch.setattr(proxy.SceneHostOrchestrator, "run", unexpected_business)
+    with proxy.ACTIVE._lock:
+        proxy.ACTIVE._runs.clear()
+    proxy.ACTIVE.try_reserve(run_id, {"attempt": 1, "stage": "EXECUTING"})
+    proxy.save_recovery_state(
+        cfg,
+        run_id=run_id,
+        attempt=1,
+        lease_token="token-r3",
+        resource_lease_token=None,
+        stage="EXECUTING",
+        identity={"pid": 99999999},
+        accepted_at=1,
+    )
+    yield SimpleNamespace(cfg=cfg, run_id=run_id, work=work, backend=backend, spec=spec, model_calls=model_calls)
+    with proxy.ACTIVE._lock:
+        proxy.ACTIVE._runs.clear()
+
+
+def write_checkpoint(case, target):
+    # 前序 DONE 尚未写入同样不能在失败终态之后丢失补报机会。
+    records = {name: {"status": "PENDING"} for name in proxy.STEPS}
+    records["PRECHECK"] = {"status": target, "detail": "持久化业务事实"}
+    if target == "DONE":
+        records["EXTRACT"] = {"status": "DONE"}
+        records["INFER"] = {"status": "FAILED", "detail": "MODEL_FAILED: 原始故障"}
+    (case.work / "checkpoint.json").write_text(json.dumps({"steps": records}))
+
+
+def finish_failure(case, target):
+    proxy._finish_failure(
+        case.cfg,
+        case.backend,
+        case.run_id,
+        1,
+        "token-r3",
+        None,
+        case.spec,
+        "MODEL_FAILED: 原始故障",
+        threading.Event(),
+        "none",
+        stage="EXECUTING",
+        error_step="PRECHECK" if target == "FAILED" else "INFER",
+    )
+
+
+@pytest.mark.parametrize("target", ["DONE", "FAILED"])
+@pytest.mark.parametrize("fault", ["step", "read"])
+def test_unconfirmed_step_keeps_recovery_and_lease_until_restart(recovery_case, target, fault):
+    case = recovery_case
+    write_checkpoint(case, target)
+    if fault == "step":
+        case.backend.fail_step_terminal = True
+    else:
+        case.backend.fail_reads = True
+    finish_failure(case, target)
+    assert proxy.state_path(case.cfg, case.run_id).exists(), "步骤未确认不得删除恢复依据"
+    assert case.backend.run_status == "SCENE_RUNNING", "步骤未收敛不能切终态清租约"
+    assert case.backend.lease_live
+    assert case.run_id not in proxy.ACTIVE
+    case.backend.fail_step_terminal = False
+    case.backend.fail_reads = False
+    proxy.recover_pending_runs(case.cfg, case.backend)
+    assert case.model_calls == [], "待失败补报重启只能收尾，不能再次执行业务/模型"
+    assert case.backend.steps["PRECHECK"] == target
+    assert case.backend.run_status == "SCENE_FAILED"
+    assert case.backend.terminal_step_attempts == 0, "终态后不得再补写steps"
+    assert not proxy.state_path(case.cfg, case.run_id).exists()
+    assert case.run_id not in proxy.ACTIVE
+
+
+def test_uncommitted_failure_restarts_without_business_reexecution(recovery_case):
+    case = recovery_case
+    write_checkpoint(case, "FAILED")
+    case.backend.fail_status = True
+    finish_failure(case, "FAILED")
+    assert proxy.state_path(case.cfg, case.run_id).exists()
+    before = copy.deepcopy(case.backend.steps)
+    case.backend.fail_status = False
+    proxy.recover_pending_runs(case.cfg, case.backend)
+    assert case.model_calls == [], "已失败的原 attempt 必须只补报，不重新进入模型"
+    assert case.backend.steps == before
+    assert case.backend.run_status == "SCENE_FAILED"
+    assert case.backend.terminal_step_attempts == 0
+    assert not proxy.state_path(case.cfg, case.run_id).exists()
+
+
+@pytest.mark.parametrize("target", ["DONE", "FAILED"])
+def test_committed_lost_responses_reconcile_without_duplicate_or_terminal_steps(recovery_case, target):
+    case = recovery_case
+    write_checkpoint(case, target)
+    case.backend.lose_step_response = True
+    case.backend.lose_status_response = True
+    finish_failure(case, target)
+    assert case.backend.steps["PRECHECK"] == target
+    assert case.backend.run_status == "SCENE_FAILED"
+    assert case.backend.calls.count(("step", "PRECHECK", target, 1)) == 1
+    assert len([c for c in case.backend.calls if c[0] == "status"]) == 1
+    assert not proxy.state_path(case.cfg, case.run_id).exists()
+    assert case.backend.terminal_step_attempts == 0
+    assert case.model_calls == []
+
+
+@pytest.mark.parametrize("fault", ["step", "complete", "committed_lost"])
+def test_success_recovery_never_reenters_business_or_writes_steps_after_terminal(recovery_case, fault):
+    from app.scene.types import SceneManifest, SceneOutcome
+
+    case = recovery_case
+    records = {name: {"status": "DONE"} for name in proxy.STEPS}
+    records["REGISTER"] = {"status": "RUNNING"}
+    (case.work / "checkpoint.json").write_text(json.dumps({"steps": records}))
+    manifest = SceneManifest(
+        scene_code="slope",
+        capability_version="1",
+        run_id=case.run_id,
+        analysis_version=1,
+        source_id="source-r3",
+        source_generation=1,
+        source_fingerprint="f" * 64,
+        config_hash="c" * 64,
+        outcome=SceneOutcome.NO_MATCH,
+    )
+    reporter = proxy.ProxyBackendReporter(
+        case.backend,
+        case.cfg,
+        run_id=case.run_id,
+        scene_code="slope",
+        source_generation=1,
+        lease_token="token-r3",
+        vehicle_key="test",
+    )
+    if fault == "step":
+        case.backend.fail_step_terminal = True
+    elif fault == "complete":
+        case.backend.fail_complete = True
+    else:
+        case.backend.lose_complete_response = True
+    with pytest.raises(proxy.FinalizationPending):
+        reporter.complete_scene(manifest=manifest, child_bag_uids={}, publish_root="")
+    state = json.loads(proxy.state_path(case.cfg, case.run_id).read_text())
+    assert state["stage"] == "FINALIZING_SUCCESS"
+    if fault == "step":
+        assert not [c for c in case.backend.calls if c[0] == "complete"]
+        assert case.backend.lease_live
+    proxy.ACTIVE.remove(case.run_id)  # 模拟代理进程退出，磁盘台账原位保留。
+    case.backend.fail_step_terminal = False
+    case.backend.fail_complete = False
+    proxy.recover_pending_runs(case.cfg, case.backend)
+    assert case.model_calls == []
+    assert all(status == "DONE" for status in case.backend.steps.values())
+    assert case.backend.run_status == "SCENE_DONE"
+    assert case.backend.terminal_step_attempts == 0
+    assert not proxy.state_path(case.cfg, case.run_id).exists()
+    assert case.run_id not in proxy.ACTIVE
+
+
+def test_actual_execute_failure_then_restart_only_finalizes_original_attempt(recovery_case):
+    case = recovery_case
+    write_checkpoint(case, "DONE")
+    case.backend.fail_status = True
+    payload = {
+        "pipeline_run_id": case.run_id,
+        "attempt": 1,
+        "source_id": "source-r3",
+        "lease_token": "token-r3",
+        "resource_lease_token": None,
+    }
+    proxy.execute_run(case.cfg, case.backend, payload)
+    assert len(case.model_calls) == 1, "首次业务执行只发生一次"
+    state = json.loads(proxy.state_path(case.cfg, case.run_id).read_text())
+    assert state["stage"] == "FINALIZING_FAILURE"
+    assert "MODEL_FAILED" in state["finalization"]["error"]
+    case.backend.fail_status = False
+    proxy.recover_pending_runs(case.cfg, case.backend)
+    assert len(case.model_calls) == 1, "重启只补原失败，不增加模型调用"
+    assert case.backend.run_status == "SCENE_FAILED"
+    assert case.backend.terminal_step_attempts == 0
+    assert not proxy.state_path(case.cfg, case.run_id).exists()
+
+
+@pytest.mark.parametrize("scene_code", ["spray", "slope"])
+def test_default_submission_backend_hash_matches_resolve_spec(tmp_path, scene_code):
+    """真实YAML/Registry及Backend参数正规化边界，拒绝None/空字典语义漂移。"""
+    import yaml
+
+    from app.scene import CapabilityRegistry, get_registry, reset_registry
+    from app.services.scene_capability_read import effective_params_by_capability
+
+    document = yaml.safe_load((ROOT / "config/scene_capabilities.yaml").read_text())
+    for entry in document["capabilities"]:
+        if entry["scene_code"] == "spray":
+            entry["enabled"] = True
+            entry["disabled_reason"] = None
+    config = tmp_path / "capabilities.yaml"
+    config.write_text(yaml.safe_dump(document))
+    registry = CapabilityRegistry.from_file(config)
+    previous = get_registry()
+    reset_registry(registry)
+    try:
+        cap = registry.resolve(scene_code)
+        # 生产Backend的真实单能力参数转换入口；空提交必须经过schema正规化。
+        frozen = effective_params_by_capability(registry, scene_code, {}, cap.capability_version)
+        assert frozen is not None
+        ready = tmp_path / "ready"
+        (ready / "source_bag").mkdir(parents=True)
+        cfg = proxy.ProxyConfig(
+            backend_url="http://unused",
+            bind="127.0.0.1",
+            port=0,
+            state_root=tmp_path / "state",
+            work_root_base=tmp_path / "work",
+            publish_root=tmp_path / "publish",
+            ready_root=str(ready),
+            min_free_bytes=0,
+            cancel_poll_seconds=30,
+            heartbeat_interval_seconds=30,
+            heartbeat_fail_budget=4,
+            lease_ttl_seconds=120,
+        )
+        detail = {
+            "pipeline_type": "SCENE_SLICE",
+            "attempt": 1,
+            "status": "SCENE_RUNNING",
+            "source_id": "source-default",
+            "pipeline_config_snapshot": {
+                "source_generation": 1,
+                "scenes": [
+                    {
+                        "scene_code": scene_code,
+                        "capability_version": cap.capability_version,
+                        "capability_config_hash": frozen["config_hash"],
+                    }
+                ],
+            },
+        }
+        source = {
+            "bag": {"relative_path": "source_bag", "vehicle": {"vehicle_code": "test"}},
+            "copies": [{"fingerprint": "f" * 64}],
+        }
+        backend = SimpleNamespace(run_detail=lambda run_id: detail, source_detail=lambda source_id: source)
+        spec, status = proxy.resolve_spec(
+            cfg,
+            backend,
+            {
+                "pipeline_run_id": "default-params",
+                "attempt": 1,
+                "lease_token": "default-token",
+            },
+        )
+        assert status == "SCENE_RUNNING"
+        assert spec.config_hash == frozen["config_hash"]
+        assert spec.parameters == frozen["parameters"]
+        assert {name: type(value) for name, value in spec.parameters.items()} == {
+            name: type(value) for name, value in frozen["parameters"].items()
+        }, "默认参数值与JSON/hash类型必须同时一致"
+    finally:
+        reset_registry(previous)

```
