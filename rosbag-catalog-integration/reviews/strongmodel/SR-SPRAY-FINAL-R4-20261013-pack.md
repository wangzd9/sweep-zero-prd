# 固定最终修复增量：29af08a58819790fe6cc467603091817a5b705fb

用户要求Codex直接解决收尾上线；原grant6b2d83fb有效。本次base=6ddcbcb，target=29af08a58819790fe6cc467603091817a5b705fb，仅上轮22189dc…两项CORRECTION及真实全链暴露的必要索引/部署映射修复。不是全量审查，不扩UI或模型要求。

原R1-02：待收尾不再停止心跳/释放ACTIVE，移交后台finalization_loop续租并仅补报；恢复线程自己续租。有效身份跨TTL后可收敛；实际过期/缺租约/attempt变化/明确停写时持久FINALIZATION_BLOCKED，禁止旧身份重写/重执行业务。三个租约周期有界收尾，超窗保留证据交现有受控reconcile，不全局放宽Backend租约。ACTIVE防重复写者，状态分支不回模型。

原R3-01：reporter从resolve_spec冻结attempt（直接构造时从持久台账读），成功意图保存前无Backend GET；后续GET/step/complete失败保持FINALIZING_SUCCESS。

独立机械验证：先以实际旧函数复现首GET两例FAIL；修后proxy/orchestrator/wiring共72PASS，其中22参数/故障例。真实单调时钟有效期Backend逐写核token/attempt/expiry，成功pending、失败pending、重启resume三支均跨2.2倍原TTL保持续租再解除故障，正确outcome且模型/业务不增加；过期/新attempt/无租约/stop先block均零补写。旧单次夹具暂停后台调度用于精确断点，新TTL族真实线程/心跳/时钟验证，并清理daemon，不用布尔lease伪证。日志.local/spray-runtime/r4-proxy-orchestrator-wiring-final.log。

真实VLM已完成：6ddcbcb固定正式Scanner/Orchestrator/proxy/MySQL，12次请求、1非空3.302s水雾切片、1752消息/43MB、8步DONE，原包SHA不变。独立验收发现child.vehicle为空、relative_path漏scene/slices、started_at UTC naive错8h。6e91c3b最小修复：继承父车，按服务端场景根相对NAS_STORAGE_ROOT登记，epoch整秒转业务Asia/Shanghai naive，原零UPDATE幂等保护保留。新增3例修前FAIL→相关50PASS；同真实产物用正式reconcile两次200，车辆test/路径指到真实DB3/时间15:58正确、current及8步不变、零新模型。证据real-e2e-6ddcbcb02004/reconcile-result.json。

部署只补必需装配：bag.relative_path相对存储根，proxy只挂ready子树到/nas/rosbag_scene_processing/ready并前缀/nas；独立发布slices。Backend/proxy同一只读受控能力配置，catalog-scene overlay显式开启且默认INGEST0/CONSUMER0/URL空；源码默认spray仍禁用。Compose真实解析逐服务比较旧NAS/NVIDIA/A100环境/挂载不变，固定imageID/refs只读/home工作根。零生产迁移/服务切换（仅用户授权准备空目录及staging预构建）。

请确认原两项是否关闭，并仅报告以上真实需求范围内可复现问题。不要重审已关闭R1-01/03/04/05、B算法或提出新可用性标准。若存在缺陷给准确触发和最小修复；此强审不替代弱OCR及生产验收。最终生产尚未执行。

```diff
diff --git a/app/services/scene_result_report_service.py b/app/services/scene_result_report_service.py
index a53c59d..6e1b514 100644
--- a/app/services/scene_result_report_service.py
+++ b/app/services/scene_result_report_service.py
@@ -57,7 +57,9 @@ from sqlalchemy import select
 from sqlalchemy.orm import Session
 
 from app.clock import now as local_now
+from app.config import settings
 from app.domain.transitions import SCENE_TERMINAL_STATES as SCENE_TERMINAL
+from app.environment_contract import PRODUCTION_SCENE_SLICE_PUBLISH_ROOT, TEST_SCENE_SLICE_PUBLISH_ROOT
 from app.models import (
     BagDerivation,
     BagFile,
@@ -498,20 +500,21 @@ def _mark_children_available(
     R2-10：AVAILABLE 推进与真实发布索引回填是**一致完成条件**（不得先 AVAILABLE
     后补索引）——
     - relative_path：06A 登记时的占位 `scene/<scene>/<parent>/<child>` 回填为真实
-      受控发布逻辑路径 `<vehicle>/<scene>/<parent>_<child>`（vehicle 继承父包
+      NAS存储根下的 `<场景发布根>/<vehicle>/<scene>/<parent>_<child>`（vehicle 继承父包
       vehicle_code，缺省 unassigned，与发布目录一致），bag_access_info 按此拼 NAS
       实际路径；
     - BagFile/BagTopic 索引：按 per-slice manifest 的发布记录（db3 文件名/大小、
       topic/消息数）幂等 upsert——重复 complete/reconcile 不产生重复索引行；
     - message_count/total_size_bytes：以发布记录为事实来源；
     - 时间口径（B8a timezone 项）：started_at/duration 以登记区间事实为准
-      （存储域首末纳秒，UTC 解释，naive 存储），updated_at 用 local_now()
-      （app.clock.now，naive 中国标准时间写库口径，与 bag_record 表一致），
-      不再混用业务时区 naive 与 UTC 纳秒。
+      （存储域首末epoch纳秒，转换为业务时区后naive存储），updated_at 用 local_now()
+      （app.clock.now），均遵循bag_record中国标准时间写库口径。
     无发布记录的子包（publish_root 缺失等）→ 409 INCOMPLETE：索引回填是
     AVAILABLE 的前置条件，不得先可用后补。
     """
-    from datetime import datetime, timezone
+    from datetime import datetime
+    from pathlib import PurePosixPath
+    from zoneinfo import ZoneInfo
 
     uids: list[str] = []
     ders = db.scalars(
@@ -522,6 +525,11 @@ def _mark_children_available(
     if not ders:
         return uids
     vehicle_key = _effective_vehicle_key(payload, parent)
+    # BagRecord路径相对NAS存储根；发布根来自服务端配置，不能取请求自报的物理路径。
+    logical_publish_root = settings.scene_slice_publish_root or (
+        PRODUCTION_SCENE_SLICE_PUBLISH_ROOT if settings.environment == "production" else TEST_SCENE_SLICE_PUBLISH_ROOT
+    )
+    relative_publish_root = PurePosixPath(logical_publish_root).relative_to(PurePosixPath(settings.nas_storage_root))
     records = _slice_records_of(db, run, row, parent, payload)
     for der in ders:
         child = db.scalar(select(BagRecord).where(BagRecord.bag_uid == der.child_bag_uid))
@@ -575,8 +583,14 @@ def _mark_children_available(
             child.duration_ns,
             child.message_count,
             child.total_size_bytes,
+            child.vehicle_id,
+            child.vehicle_link_status,
         )
-        child.relative_path = f"{vehicle_key}/{manifest.scene_code}/{run.source_id}_{der.child_bag_uid}"[:1024]
+        child.relative_path = str(
+            relative_publish_root / vehicle_key / manifest.scene_code / f"{run.source_id}_{der.child_bag_uid}"
+        )[:1024]
+        child.vehicle_id = parent.vehicle_id
+        child.vehicle_link_status = parent.vehicle_link_status
         if child.availability != "AVAILABLE":
             child.availability = "AVAILABLE"
         # codex M-1（attempt-1-r2-rework-5）：started_at 统一 truncate 到秒——
@@ -589,7 +603,9 @@ def _mark_children_available(
         # 救不回，同一物理时刻按 ns 末落库秒不同。
         # 改整数除法 `// 1_000_000_000` 先求整秒，构造即整秒（无需再 replace
         # microsecond），纳秒末一律向下截断到前整秒。
-        started_at = datetime.fromtimestamp(der.start_ns // 1_000_000_000, tz=timezone.utc).replace(tzinfo=None)
+        started_at = datetime.fromtimestamp(
+            der.start_ns // 1_000_000_000, tz=ZoneInfo(settings.display_timezone)
+        ).replace(tzinfo=None)
         child.started_at = started_at
         child.duration_ns = der.duration_ns
         child.message_count = message_count
@@ -601,6 +617,8 @@ def _mark_children_available(
             child.duration_ns,
             child.message_count,
             child.total_size_bytes,
+            child.vehicle_id,
+            child.vehicle_link_status,
         ):
             child.updated_at = local_now()
         uids.append(der.child_bag_uid)
@@ -700,10 +718,15 @@ def complete_scene(db: Session, pipeline_run_id: str, payload: dict) -> dict:
         # 不能在complete之后再补写此步骤；事务回滚也不能留下假DONE。
         from app.models import StepRun
 
-        register = db.scalar(select(StepRun).where(
-            StepRun.pipeline_run_id == run.pipeline_run_id,
-            StepRun.step_name == "REGISTER", StepRun.attempt == run.attempt,
-        ).with_for_update())
+        register = db.scalar(
+            select(StepRun)
+            .where(
+                StepRun.pipeline_run_id == run.pipeline_run_id,
+                StepRun.step_name == "REGISTER",
+                StepRun.attempt == run.attempt,
+            )
+            .with_for_update()
+        )
         if register is None or register.status == "QUEUED":
             update_scene_step(db, run, "REGISTER", "RUNNING", lease_token=payload.get("lease_token"))
             db.flush()
diff --git a/deploy/scene/catalog-scene.yaml b/deploy/scene/catalog-scene.yaml
new file mode 100644
index 0000000..11ed5c2
--- /dev/null
+++ b/deploy/scene/catalog-scene.yaml
@@ -0,0 +1,23 @@
+# 仅在受控水雾发布时显式叠加到compose.yaml+compose.processing.yaml。
+# 标准发布先保持关闭；完成旧功能健康检查后才由发布owner配置开关。
+services:
+  backend:
+    environment:
+      SCENE_INGEST_ENABLED: ${SCENE_INGEST_ENABLED:-0}
+      SCENE_NAS_SCAN_ROOT: /public/rosbag_scene_processing/incoming
+      SCENE_NAS_READY_ROOT: /public/rosbag_scene_processing/ready
+      SCENE_SLICE_PUBLISH_ROOT: /public/rosbag_scene_processing/slices
+    volumes:
+      - type: bind
+        source: ${SCENE_CAPABILITIES_HOST_FILE:?需配置受控能力注册表文件}
+        target: /app/config/scene_capabilities.yaml
+        read_only: true
+  scanner:
+    environment:
+      SCENE_NAS_SCAN_ROOT: /public/rosbag_scene_processing/incoming
+      SCENE_NAS_READY_ROOT: /public/rosbag_scene_processing/ready
+      SCENE_SLICE_PUBLISH_ROOT: /public/rosbag_scene_processing/slices
+  orchestrator:
+    environment:
+      SCENE_SLICE_CONSUMER_ENABLED: ${SCENE_SLICE_CONSUMER_ENABLED:-0}
+      SCENE_PROXY_URL: ${SCENE_PROXY_URL:-}
diff --git a/deploy/scene/rosbag-scene.env.example b/deploy/scene/rosbag-scene.env.example
index 716c3e5..db76713 100644
--- a/deploy/scene/rosbag-scene.env.example
+++ b/deploy/scene/rosbag-scene.env.example
@@ -21,6 +21,9 @@ SPRAY_VLM_API_KEY=
 # 水雾参考数据目录（7 受控参考图，app/scene/spray/references.py 实读 SPRAY_REFERENCE_DIR）
 SPRAY_REFERENCE_DIR=/opt/spray/refs
 SPRAY_REFERENCE_HOST_DIR=/home/data-process/spray-runtime/20261013/reference/images/refs
+SCENE_CAPABILITIES_HOST_FILE=/home/data-process/scene/scene_capabilities.yaml
+EGL_PLATFORM=surfaceless
+LIBGL_ALWAYS_SOFTWARE=1
 # 点云 decoder 可执行路径（容器内 /opt/spray/bin/packet2pointcloud；
 # 由spray.precheck.resolve_decoder_path及adapter实际读取，空值会覆盖镜像默认）
 SPRAY_DECODER_PATH=/opt/spray/bin/packet2pointcloud
@@ -40,7 +43,8 @@ BACKEND_URL=http://127.0.0.1:18000
 # 环境标识
 ENVIRONMENT=production
 # NAS 就绪根 / 切片发布根（部署时按生产 NAS 根填实际值，本单占位）
-SCENE_NAS_READY_ROOT=/public/rosbag_scene_processing/ready
+# 代理拼 bag.relative_path（相对NAS_STORAGE_ROOT），容器只映射ready子树到/nas对应层级。
+SCENE_NAS_READY_ROOT=/nas
 SCENE_SLICE_PUBLISH_ROOT=/public/rosbag_scene_processing/slices
 # 宿主实际NAS路径发布前核实；ready只读，slices允许独立新产物发布。
 SCENE_READY_HOST_ROOT=
diff --git a/deploy/scene/scene-proxy.yaml b/deploy/scene/scene-proxy.yaml
index f00d550..62afa6e 100644
--- a/deploy/scene/scene-proxy.yaml
+++ b/deploy/scene/scene-proxy.yaml
@@ -41,12 +41,18 @@ services:
         read_only: true
       - type: bind
         source: ${SCENE_READY_HOST_ROOT:?SCENE_READY_HOST_ROOT 未配置}
-        target: /public/rosbag_scene_processing/ready
+        # bag.relative_path相对NAS_STORAGE_ROOT，保留其目录层级；仅挂ready子树。
+        target: /nas/rosbag_scene_processing/ready
         read_only: true
       - type: bind
         source: ${SPRAY_REFERENCE_HOST_DIR:?SPRAY_REFERENCE_HOST_DIR 未配置}
         target: /opt/spray/refs
         read_only: true
+      # Backend与proxy必须读取同一冻结注册表；仅spray启用位由发布owner调整。
+      - type: bind
+        source: ${SCENE_CAPABILITIES_HOST_FILE:?SCENE_CAPABILITIES_HOST_FILE 未配置}
+        target: /code/config/scene_capabilities.yaml
+        read_only: true
       # 代理状态/工作根：必要可写根（与 env SCENE_PROXY_STATE_ROOT/WORK_ROOT 一致）
       - type: bind
         source: /home/data-process/scene/state
diff --git a/scripts/scene_host_proxy.py b/scripts/scene_host_proxy.py
index 5c558d1..73a2eec 100644
--- a/scripts/scene_host_proxy.py
+++ b/scripts/scene_host_proxy.py
@@ -50,7 +50,6 @@ import time
 from dataclasses import dataclass
 from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
 from pathlib import Path
-from types import SimpleNamespace
 
 SCRIPT_DIR = Path(__file__).resolve().parent
 for _p in (SCRIPT_DIR.parent, SCRIPT_DIR,):
@@ -304,7 +303,8 @@ class ProxyBackendReporter:
     manifest digest，同身份重放不重复登记）。publish_root 回报受控根。"""
 
     def __init__(self, backend: Backend, cfg: ProxyConfig, *, run_id: str, scene_code: str,
-                 source_generation: int, lease_token: str, vehicle_key: str | None):
+                 source_generation: int, lease_token: str, vehicle_key: str | None,
+                 attempt: int | None = None):
         self._b = backend
         self._cfg = cfg
         self._run_id = run_id
@@ -312,6 +312,7 @@ class ProxyBackendReporter:
         self._gen = source_generation
         self._token = lease_token
         self._vehicle = vehicle_key
+        self._attempt = attempt
 
     def _digest(self, manifest) -> str:
         import hashlib
@@ -336,8 +337,11 @@ class ProxyBackendReporter:
         )
 
     def complete_scene(self, *, manifest, child_bag_uids, publish_root) -> dict:
-        detail = self._b.run_detail(self._run_id)
-        attempt = int(detail["attempt"])
+        # 执行身份已由resolve_spec冻结；保存成功意图之前不访问可能超时的Backend。
+        state = _read_json(state_path(self._cfg, self._run_id)) or {}
+        attempt = self._attempt if self._attempt is not None else state.get("attempt")
+        if not isinstance(attempt, int) or attempt < 1:
+            raise SpecError("成功收尾缺少冻结attempt，拒绝猜测身份")
         payload = {
                 "scene_code": self._scene_code,
                 "lease_token": self._token,
@@ -369,6 +373,10 @@ class FinalizationPending(RuntimeError):
     """执行结果已形成，仅待Backend对账；禁止回到业务执行或改报业务失败。"""
 
 
+class FinalizationBlocked(RuntimeError):
+    """旧身份失效或收尾窗口耗尽；保留事实交受控对账，禁止重新执行业务。"""
+
+
 def _save_finalization(cfg, run_id, attempt, lease_token, *, stage, work_root=None, **facts):
     state = _read_json(state_path(cfg, run_id)) or {}
     state.update({"version": "scene-proxy-recovery-v1", "pipeline_run_id": run_id,
@@ -488,6 +496,7 @@ def resolve_spec(
         reporter=ProxyBackendReporter(
             backend, cfg, run_id=run_id, scene_code=scene_code,
             source_generation=gen, lease_token=str(payload["lease_token"]), vehicle_key=vehicle,
+            attempt=attempt,
         ),
         min_free_bytes=cfg.min_free_bytes,
         stop_event=stop_event,
@@ -846,9 +855,7 @@ def execute_run(cfg: ProxyConfig, backend: Backend, payload: dict) -> None:
         manifest, _steps = SceneHostOrchestrator().run(spec)
     except FinalizationPending as exc:
         print(f"scene finalization pending {run_id}: {exc}", flush=True)
-        _stop_threads(stop_cancel)
-        _release_resource(cfg, resource_token)
-        ACTIVE.remove(run_id)
+        _handoff_finalization(cfg, backend, run_id, stop_cancel, stop_reason)
         return
     except SceneExecError as exc:
         # 失败归因：步骤 + 错误保留（不当 NO_MATCH）；停写信号（取消/租约失效）
@@ -955,22 +962,21 @@ def _finish_failure(cfg: ProxyConfig, backend: Backend, run_id: str, attempt: in
     if spec is not None and not _report_steps(
             backend, run_id=run_id, attempt=attempt, lease_token=lease_token,
             work_root=spec.work_root, error_step=error_step, error_detail=error):
-        _stop_threads(stop_cancel)
-        _release_resource(cfg, resource_token)
-        ACTIVE.remove(run_id)
+        _handoff_finalization(cfg, backend, run_id, stop_cancel, {"value": reason})
         return
     # R1-03：先对账确认终态再决定清不清恢复台账——上报未提交/响应丢失时
     # run 停 SCENE_RUNNING 且台账被删 = 重启失恢复入口（phantom run）；
     # 未确认则保留台账留痕，recover_pending_runs 重启后按原身份重新对账续收尾
     confirmed = _confirm_terminal(backend, run_id, lease_token, "SCENE_FAILED", error)
-    _stop_threads(stop_cancel)
-    _release_resource(cfg, resource_token)
     if confirmed:
+        _stop_threads(stop_cancel)
+        _release_resource(cfg, resource_token)
         clear_recovery_state(cfg, run_id)
+        ACTIVE.remove(run_id)
     else:
         print(f"scene run {run_id} SCENE_FAILED unconfirmed (Backend 不可用/未提交)：保留 recovery 台账作恢复依据",
               flush=True)
-    ACTIVE.remove(run_id)
+        _handoff_finalization(cfg, backend, run_id, stop_cancel, {"value": reason})
 
 
 def _finish_cancelled(cfg: ProxyConfig, backend: Backend, run_id: str, attempt: int,
@@ -1005,34 +1011,114 @@ def _finish_cancelled(cfg: ProxyConfig, backend: Backend, run_id: str, attempt:
 # ---------------------------------------------------------------------------
 # 启动恢复：旧写者终止核验后按原身份续跑（不重新 ACK、不产生第二写者）
 # ---------------------------------------------------------------------------
-def _resume_finalization(cfg: ProxyConfig, backend: Backend, state: dict) -> None:
+def _try_finalization(cfg: ProxyConfig, backend: Backend, state: dict) -> bool:
+    """仅对账一个原attempt；暂时通信故障由调用者等待，失效身份不再重试。"""
+    from datetime import datetime
+
     run_id = state["pipeline_run_id"]
     attempt = int(state["attempt"])
     facts = state.get("finalization") or {}
-    try:
-        detail = backend.run_detail(run_id)
-        if int(detail.get("attempt", 0)) != attempt:
-            # 新attempt拥有写权，旧收尾只保留审计依据，绝不写入或重执行。
-            return
-        work = Path(facts["work_root"]) if facts.get("work_root") else None
-        if state["stage"] == "FINALIZING_FAILURE":
-            _finish_failure(cfg, backend, run_id, attempt, state["lease_token"],
-                            state.get("resource_lease_token"),
-                            SimpleNamespace(work_root=work) if work else None,
-                            str(facts.get("error") or ""), threading.Event(), "none",
-                            stage="RECOVERING_FINALIZATION", error_step=facts.get("error_step"))
-        elif work is not None and _report_steps(
+    detail = backend.run_detail(run_id)
+    if int(detail.get("attempt", 0)) != attempt:
+        raise FinalizationBlocked("原attempt已被替换，禁止覆盖新写者")
+    status = detail.get("status")
+    if status in _TERMINAL_RUN_STATUSES:
+        if state["stage"] == "FINALIZING_SUCCESS":
+            # 丢响应只重放原幂等complete，不在终态后写steps。
+            try:
+                backend.complete_scene(run_id, facts["complete_payload"], idem=facts["complete_idem"])
+            except Exception as exc:
+                raise FinalizationBlocked(f"终态结果不能按原身份重放：{exc}") from exc
+        elif status != facts.get("target", "SCENE_FAILED"):
+            raise FinalizationBlocked(f"原运行已变更为其他终态：{status}")
+        clear_recovery_state(cfg, run_id)
+        return True
+    if status == "SCENE_CANCELLING":
+        raise FinalizationBlocked("取消已接管，保留结果待受控对账")
+    expiry = detail.get("lease_expires_at")
+    if "lease_expires_at" in detail and not expiry:
+        raise FinalizationBlocked("原运行已无任务租约，禁止补写")
+    if expiry:
+        from app.clock import aware_now, now
+
+        expires = datetime.fromisoformat(str(expiry))
+        current = aware_now() if expires.tzinfo is not None else now()
+        if expires <= current:
+            raise FinalizationBlocked("原任务租约已过期，禁止使用旧token补写")
+    work = Path(facts["work_root"]) if facts.get("work_root") else None
+    if state["stage"] == "FINALIZING_FAILURE":
+        if work is not None and not _report_steps(
                 backend, run_id=run_id, attempt=attempt, lease_token=state["lease_token"],
-                work_root=work, terminal_step="REGISTER"):
-            # 相同幂等身份的complete可对账已提交丢响应；不重做模型、发布或results。
-            backend.complete_scene(run_id, facts["complete_payload"], idem=facts["complete_idem"])
-            clear_recovery_state(cfg, run_id)
-    except Exception as exc:
-        print(f"scene finalization remains pending {run_id}: {exc}", flush=True)
+                work_root=work, error_step=facts.get("error_step"), error_detail=str(facts.get("error") or "")):
+            return False
+        if not _confirm_terminal(backend, run_id, state["lease_token"],
+                                 str(facts.get("target") or "SCENE_FAILED"), str(facts.get("error") or "")):
+            return False
+    elif work is not None:
+        if not _report_steps(backend, run_id=run_id, attempt=attempt, lease_token=state["lease_token"],
+                             work_root=work, terminal_step="REGISTER"):
+            return False
+        backend.complete_scene(run_id, facts["complete_payload"], idem=facts["complete_idem"])
+    else:
+        raise FinalizationBlocked("缺少已持久化的收尾工作根")
+    clear_recovery_state(cfg, run_id)
+    return True
+
+
+def _block_finalization(cfg: ProxyConfig, state: dict, reason: str) -> None:
+    state = {**state, "stage": "FINALIZATION_BLOCKED", "blocked_reason": reason,
+             "updated_at": time.time(), "identity": _process_identity()}
+    _write_json_atomic(state_path(cfg, state["pipeline_run_id"]), state)
+    print(f"scene finalization blocked {state['pipeline_run_id']}: {reason}", flush=True)
+
+
+def _finalization_loop(cfg: ProxyConfig, backend: Backend, state: dict,
+                       stop: threading.Event, reason: dict) -> None:
+    run_id = state["pipeline_run_id"]
+    # 三个租约周期内维持续租并尝试收尾；超窗保留证据，不无限补报。
+    deadline = time.monotonic() + max(60.0, 3 * cfg.lease_ttl_seconds)
+    try:
+        while True:
+            if stop.is_set() and reason.get("value") != "lease_terminal":
+                _block_finalization(cfg, state, f"收尾停写信号：{reason.get('value')}")
+                return
+            try:
+                if _try_finalization(cfg, backend, state):
+                    return
+            except FinalizationBlocked as exc:
+                _block_finalization(cfg, state, str(exc))
+                return
+            except Exception as exc:
+                print(f"scene finalization remains pending {run_id}: {exc}", flush=True)
+            if stop.is_set() or time.monotonic() >= deadline:
+                _block_finalization(cfg, state, f"收尾停止（{reason.get('value')}）或超出三个租约周期")
+                return
+            stop.wait(max(0.05, min(cfg.heartbeat_interval_seconds, 10.0)))
     finally:
+        stop.set()
+        _release_resource(cfg, state.get("resource_lease_token"))
         ACTIVE.remove(run_id)
 
 
+def _handoff_finalization(cfg, backend, run_id, stop, reason):
+    state = _read_json(state_path(cfg, run_id))
+    if not state:
+        raise RuntimeError("收尾意图未持久化，不能交接")
+    ACTIVE.add(run_id, {"stage": state["stage"], "attempt": state["attempt"], "pid": os.getpid()})
+    threading.Thread(target=_finalization_loop, args=(cfg, backend, state, stop, reason),
+                     daemon=True, name=f"scene-finalize-{run_id}").start()
+
+
+def _resume_finalization(cfg: ProxyConfig, backend: Backend, state: dict) -> None:
+    stop = threading.Event()
+    reason = {"value": "none"}
+    threading.Thread(target=_lease_watchdog,
+                     args=(cfg, backend, state["pipeline_run_id"], state["lease_token"],
+                           state.get("resource_lease_token"), stop, reason),
+                     daemon=True, name=f"scene-finalize-lease-{state['pipeline_run_id']}").start()
+    _finalization_loop(cfg, backend, state, stop, reason)
+
+
 def recover_pending_runs(cfg: ProxyConfig, backend: Backend) -> int:
     recovered = 0
     if not cfg.state_root.is_dir():
@@ -1050,6 +1136,9 @@ def recover_pending_runs(cfg: ProxyConfig, backend: Backend) -> int:
             # 旧写者仍存活 → 不接管，留痕等待下轮
             print(f"scene recovery skipped, writer still alive: {run_id} {identity}", flush=True)
             continue
+        if state.get("stage") == "FINALIZATION_BLOCKED":
+            print(f"scene recovery needs controlled reconciliation: {run_id}", flush=True)
+            continue
         if state.get("stage") in ("FINALIZING_FAILURE", "FINALIZING_SUCCESS"):
             if ACTIVE.try_reserve(run_id, {"stage": "RECOVERING_FINALIZATION", "attempt": state.get("attempt")}):
                 threading.Thread(target=_resume_finalization, args=(cfg, backend, state),
@@ -1164,6 +1253,10 @@ def build_server(cfg: ProxyConfig, backend: Backend):
                 return
             # 台账先落盘（进程身份+检查点）再返回 accepted——派发响应丢失也据此对账
             pending = _read_json(state_path(cfg, run_id)) or {}
+            if pending.get("stage") == "FINALIZATION_BLOCKED":
+                ACTIVE.remove(run_id)
+                self._reply(409, {"error": "finalization blocked; controlled reconciliation required"})
+                return
             if pending.get("stage") in ("FINALIZING_FAILURE", "FINALIZING_SUCCESS"):
                 if pending.get("attempt") != attempt or pending.get("lease_token") != token:
                     ACTIVE.remove(run_id)

```
