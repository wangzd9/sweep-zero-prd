# 16B-r3 独立故障验证（Codex 委派）

- 结论：**PASS；交主协调者裁决，不等于审查及生产放行。**
- 被测修复：`8500de0fc11b4456edcb61ec5a6a6ae91bd4dae7`，18:28冻结。
- 工作树：`/home/wang/.local/state/rosbag-scene/wt-codex-spray-release`。
- 本角色仅新增 `tests/test_scene_host_proxy_r3.py`，未改业务实现/既有fixture，未提交或合并。

## 修前独立反例

基线 `e152465` 上最初六例：**5 failed / 1 passed**。

- DONE/FAILED持续未提交：失败收尾将run切终态且清台账，步骤补报依据丢失。
- GET持续失败、失败status未提交：保留的旧EXECUTING台账重启后重入实际业务编排入口，模型边界新增调用1次。
- 已提交丢响应分支原本可收敛，作为正向对照保留。

日志：`/home/wang/work/.local/spray-runtime/proxy-r3-independent-before.log`。

## 修后验证

新增测试使用严格内存Backend表达真实步骤状态机、原attempt与租约；run终态清租约后拒绝任何新增steps写入。同步线程替身仅去除调度偶然性，恢复调用实际 `recover_pending_runs → _resume_finalization`。

最终 **11个独立故障用例全部通过**：

- DONE/FAILED各自持续未提交、GET持续失败，均保留恢复依据及有效租约，故障解除恢复后步骤精确收敛；恢复业务/模型新增调用0。
- DONE/FAILED已提交丢响应，对账确认且不重复终态写入。
- 失败状态持续未提交后恢复，只补原失败，不重新执行业务。
- 实际 `execute_run` 首次业务失败后重启：首次业务计数1，恢复新增0，原MODEL_FAILED事实保留。
- 成功路径七步持续未提交时阻止complete；complete未提交、已提交丢响应均保留成功收尾意图，恢复收敛且不重新执行模型/发布。
- 所有分支终态后steps尝试计数0；REGISTER由Backend complete原子DONE。

最终命令：

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_host_proxy.py tests/test_scene_host_proxy_r3.py tests/test_scene_host_orchestrator.py`

结果 **50 passed，29.65秒，rc=0**，日志 `proxy-r3-independent-after-final.log`；日志结束18:28:55。本轮包含本机假VLM HTTP fixture，无远端模型调用。Ruff新文件格式和检查通过。

新测试SHA256：`52af38e20b03aca7c1c96ec5f0828d745338a6a15d1f458fcc0d7c6e04d25e79`。

该组合结果对应r3修复；18:30之后 `0e4d0ed` 的12S-C接线增量需由协调者确认额外集成证据，不将旧测试结果冒充新候选已验证。未全仓测试、未OCR/强审、未生产写入；既有Skill已覆盖此次机械验证，不新增未经复用验证的Skill。

## 续验：默认提交参数正规化（真实链路发现项）

协调者修正代理 `effective_params(scene_code, None, version)` 为 `effective_params(scene_code, {}, version)` 后，本角色补真实Registry回归，不替换其参数验证/hash实现。临时从真实YAML仅启用spray；经Backend正式 `effective_params_by_capability(registry, scene_code, {}, version)` 生成冻结hash，再调用实际 `resolve_spec`，验证默认参数值、类型与hash全部一致。

- 修前证据：只在内存装载 `0e4d0ed` 已提交的旧 `resolve_spec`，不回滚业务文件。新两例 **spray FAIL / slope PASS**，失败为真实 `capability_config_hash` 不一致。
- 修后：新增默认spray/slope两例通过；原11故障恢复用例及接线11例共同 **24 passed，1.54秒，rc=0**。
- 按协调者授权，将旧接线 `TestProxyVehicleBindingConsumes12SA` 三处冻结快照fixture由 `None` 改为 `{}`，对应Backend真实正规化口径；未改变断言/业务实现/其余fixture。
- 命令：`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_host_proxy_r3.py tests/test_scene_spray_wiring.py`。
- 证据：`/home/wang/work/.local/spray-runtime/default-params-before.log`、`default-params-after-final.log`，修前只读内存装载脚本 `default-params-before-repro.py`。
- 两测试文件Ruff及`git diff --check`通过，测试完成时基线HEAD为`0e4d0ed`、修复未冻结；交协调者提交后补固定身份。未跑模型/全仓/生产。
