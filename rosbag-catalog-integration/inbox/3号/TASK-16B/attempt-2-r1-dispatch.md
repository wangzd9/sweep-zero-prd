# 派单：TASK-16B attempt-2-r1 最小返修（OCR 第9轮 7 findings 全 CONFIRMED）

- status: DISPATCHED
- 派单时间：2026-10-13 13:2x +08:00
- 任务：16B proxy 一次最小返修，修 OCR 第9轮（session `40e90fea`，coverage_complete=true）7 条 findings；协调者已逐条独立核代码全 CONFIRMED，误报 0。
- owner：C（16B 交付 owner）
- base：`0208a73`（16B 冻结 head）续 commit；只动 `scripts/scene_host_proxy.py`（H1/H2/H4/H5/H6 五处）+ 必要时补 `tests/test_scene_host_proxy.py` 回归；**不碰 orchestrator/fake_vlm/迁移/app 面**。
- 前置变化：16B OCR 门禁本轮**已解除**（proxy 第9轮 rc=0 + 覆盖完整 + 7 findings 已裁），返修后可走增量 OCR + 强审 pack。

## 修复清单（逐条，附坐标）

1. **H1 [high] :903 `try_reserve` 返回值丢弃（TOCTOU 双写者）**
   - 同 run_id 两个并发 `POST /run` 都过 `existing is None` 检查，都调 `try_reserve`（原子仅一个成功），但两个都继续 `save_recovery_state` + spawn 线程 → 违反模块 docstring「禁第二写者」。
   - 修法：接住返回值 `if not ACTIVE.try_reserve(...): existing = ACTIVE.get(run_id); <按 existing 重判 already_running/409 回复>`。recovery 路径 :~827 已正确检查，参照其形态。补回归：两线程同 run_id 并发 POST /run，断言恰一个 accepted、另一个 already_running/409、`ACTIVE` 内仅一条。

2. **H2 [high] :485-490 + FAILED 分支同缺陷（终态写被跳过）**
   - `post(name,"RUNNING")` 成功后局部 `cur` 不刷新（仍 QUEUED/None），`allowed(cur,"DONE")` 因 `STEP_TRANSITIONS[QUEUED]` 不含 DONE 恒 False → 终态 post 被静默跳过，步骤卡 RUNNING。崩溃恢复/重试且当前 attempt 无 RUNNING 行时触发。
   - 修法：`post(name,"RUNNING")` 成功后立即 `cur="RUNNING"`（或 `cur=current.get(name)`）；`status=="FAILED"` 分支同改。补回归：cur=None/QUEUED + checkpoint DONE → 断言步骤最终到 DONE 非卡 RUNNING。

3. **H4 [high] :664-667 `except` 过窄（工作线程静默死）**
   - `resolve_spec` 调 `get_registry().effective_params` 抛 `CapabilityError`/`CapabilityDisabledError`（继承 `Exception` 非 `RuntimeError`，`app/scene/types.py:36/50`）+ `fingerprint_bag` 抛 `ValueError`，均未被 `(SpecError,HTTPError,URLError,RuntimeError)` 捕获 → 线程死、`ACTIVE` 不删（后续 POST /run 恒 409 死锁再派发）、recovery 不清（重启 phantom run）、run 卡 SCENE_RUNNING 至租约超时。
   - 修法：扩 `except Exception`（或至少 `+ CapabilityError + ValueError`），确保失败路径（停线程/报 SCENE_FAILED/释放资源/清 recovery/移出 ACTIVE）恒执行。补回归：注入 effective_params 抛 CapabilityError → 断言 run 报 SCENE_FAILED + ACTIVE 已清 + recovery 已清。

4. **H5 [medium] :397 `config_hash` 从 registry 默认值重推（REGISTER 必 409）**
   - `spec.config_hash = hash(scene_code, cap_version, defaults)`（raw=None），但 backend 按**提交时**参数冻结 `capability_config_hash`；`parse_report_manifest` 对 `manifest.config_hash != entry.capability_config_hash` 抛 409 CONFIG_MISMATCH。非默认参数的 run：过 PRECHECK（两侧都默认值相等）→ 烧完模型 → REGISTER 才 409。
   - 修法：此处已能取 `entry.get("capability_config_hash")`，至少加 `if eff.config_hash != entry.get("capability_config_hash"): raise SpecError(...)` fail fast（不烧模型）；若能从 entry 还原提交参数则直接用提交值重推（更优，协调者接受 fail-fast 为下限）。补回归：entry capability_config_hash 与 defaults 不同 → 断言 PRECHECK/EXTRACT 前 SpecError，不触发模型调用。

5. **H6 [medium] :182-186 原子写缺 fsync（recovery 真相源可能丢）**
   - `tmp.write_text + os.replace` 无 fsync，掉电/panic 前 rename 未落盘 → recovery-state 文件丢/回滚，静默禁用该 run 的重启恢复。项目已有 fsync-before-replace 约定（`app/services/remote_bag_lock.py`）。
   - 修法：`open(tmp,"w")`→write→flush→`os.fsync(fileno())`→close→`os.replace`。

6. **L1 [low] :523 steps 未按 attempt 过滤（与 _report_steps 不一致）**
   - `current` 以 step_name 为键收**全部** attempt 的 step 行；scene retry 复用 run_id 递增 attempt，可能读到上一 attempt 状态跳过必要 post 或试非法转换（实际影响被 DB 插入序 + backend 用 run.attempt 写缓解）。
   - 修法：`if s.get("attempt") == attempt` 过滤，与 `_report_steps` 对齐。

## 验收
- 六处修复 + 对应回归全绿（`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/test_scene_host_proxy.py -q`）+ ruff 单文件绿 + `python3 -m compileall scripts/scene_host_proxy.py`
- 定向既有 26 passed 不回归；零越界（git diff 只 scene_host_proxy.py + 其测试）
- 交付冻结后回执 `receipts/TASK-16B/attempt-2-r1.md`（REVIEW_PENDING）
- 收口链：机械核验 → 增量 OCR（`--from 0208a73 --to <新head>`）→ 强审 pack（授权在案期限内，范围=本次 6 处）→ 合入 → 12S-C 接线消费

## 边界
- 不改算法/帧判定/切包（app.scene 面零动）；不碰 07B/16C 冻结文件；不部署生产。
- H5 若选择「还原提交参数重推」需从 entry 字段取值，确认 entry 是否存了提交参数；没存则 fail-fast 为合格下限（在回执说明）。