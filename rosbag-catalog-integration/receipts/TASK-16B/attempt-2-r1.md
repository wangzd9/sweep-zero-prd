# 回执：TASK-16B attempt-2-r1（REVIEW_PENDING）

- 交付时间：2026-10-13 13:3x +08:00
- owner：C（执行者C·数据链路监控告警群）
- base：`0208a73`（16B 冻结 head）
- head：`40ab818`（`c/task-16b-scene-host-proxy` @ `/home/wang/.local/state/rosbag-scene/wt-03b-t16b`）
- 状态：**REVIEW_PENDING**（交付冻结，等机械核验→增量 OCR→强审 pack→合入）

## 文件清单（git diff --stat 0208a73..40ab818，零越界）
- `scripts/scene_host_proxy.py`：+42/-11（六处修复 + 未用 import 清理）
- `tests/test_scene_host_proxy.py`：+177/-1（import 扩充 + 6 个新回归）

## 行为（逐 finding）
1. **H1** `do_POST /run`：`try_reserve` 接住原子返回值，失败者按 `ACTIVE.get` 重判同 attempt→200 already_running / 异 attempt→409，杜绝 TOCTOU 双写者。
2. **H2** `_report_steps`：`post` 改返 target/None，DONE 与 FAILED 分支 post RUNNING 成功后立即 `cur = "RUNNING"` 刷新，终态 post 不再被 `allowed(QUEUED,"DONE")` 恒 False 静默跳过。
3. **H4** `execute_run` RESOLVING 段：`except (SpecError,HTTPError,URLError,RuntimeError)` 扩为 `except Exception`（CapabilityError/CapabilityDisabledError/ValueError 均落入失败收尾：SCENE_FAILED + 清 ACTIVE + 清 recovery），顺带清理不再使用的 `HTTPError/URLError` import（ruff F401）。
4. **H5** `resolve_spec`：`eff` 计算后与快照 `entry["capability_config_hash"]` 比对，不一致即 `SpecError` fail-fast（PRECHECK 前拒绝，不烧模型）。**口径说明（派单 H5 边界要求）：快照 entry 只存 scene_code/capability_version/capability_config_hash，不存提交参数（核 `scene_slice_service.py` `_scene_snapshot` 在案），无法按提交值重推，取派单承认的 fail-fast 下限。**
5. **H6** `_write_json_atomic`：`tmp.write_text` 改 `open→write→flush→os.fsync(fileno)→close→os.replace`（同 `app/services/remote_bag_lock.py` fsync-before-replace 约定）。
6. **L1** `_report_step_single`：steps 读取加 `if s.get("attempt") == attempt` 过滤，与 `_report_steps` 对齐。

## 自测（真实执行）
- 环境：worktree `.venv` Python 3.10.12，`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest`
- `tests/test_scene_host_proxy.py -q`：**20 passed**（14 既有零回归 + 6 新回归），exit 0
- `tests/test_scene_host_proxy.py + tests/test_scene_host_orchestrator.py -q`：**32 passed**，exit 0（orchestrator 面不回归）
- 新回归断言要点：H1 双线程 Barrier 并发 POST→`codes.count(202)==1` 且余 200/409、health 恒至多一条；H2 七步 QUEUED+checkpoint DONE→每步 `RUNNING in statuses` 且 `statuses[-1]=="DONE"`；L1 旧 attempt DONE+本 attempt QUEUED→post 出 `("RUNNING",2)` 与 `("DONE",2)`；H4 注入 CapabilityError→线程 join 收敛、`SCENE_FAILED` 落库、ACTIVE 清、recovery 清；H5 冻结 hash 篡改→`SpecError` match `capability_config_hash`、orchestrator.run 被 monkeypatch 为触发即 AssertionError（未触发）；H6 monkeypatch 记录 `events==["fsync","replace"]` 且无 tmp 残件
- `ruff check scripts/scene_host_proxy.py tests/test_scene_host_proxy.py`：**All checks passed**，exit 0
- `python -m compileall -q scripts/scene_host_proxy.py`：exit 0

## 未执行项
- 增量 OCR（`--from 0208a73 --to 40ab818`）、强审 pack、机械核验、合入 = 协调者收口链，C 不代跑
- real 栈全链冒烟（16A 接受后接续项，16D 前）维持原口径

## 越界申报
- 无。diff 仅 `scene_host_proxy.py` + 其测试；未碰 orchestrator/fake_vlm/迁移/app 面；未 reset/覆盖他人 commit（base 上单 commit 续接）。