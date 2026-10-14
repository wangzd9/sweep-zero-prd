# 16B-r5 独立机械故障验证

- 结论：**PASS，交协调者裁决，不替代强审或生产门禁。**
- 时间：2026-10-13 19:28–19:33 +08:00。
- 修前固定代理：`29af08a58819790fe6cc467603091817a5b705fb`。
- 测试树：`/home/wang/.local/state/rosbag-scene/wt-codex-spray-release`；修后组合完成时HEAD `fe17e8a765c7b6add2d809650822329463fbe079`，proxy修复仍待协调者提交冻结。不能将当前HEAD描述为已包含该修复。
- 本角色只新增 `tests/test_scene_host_proxy_r5.py`，不修改业务/此前冻结测试/证据，不提交、合并、OCR、强审或写生产。

## 修前与修后

同一17个新用例，对固定29af代理只读加载到进程内存（不回滚共享文件）执行：**16 failed / 1 passed，0.43秒，rc=1**。确定409冲突作为正向对照通过；其他反例失败符合两项审查缺陷。

当前修复：**17 passed，1.54秒，rc=0**。

覆盖：

- 同attempt SCENE_DONE且原complete已提交，以相同幂等键重放确认。
- TimeoutError、ConnectionError、真实Backend HTTP503翻译异常链，各一次或连续三次故障；同时覆盖未置位stop和`lease_terminal`已置位stop，共12例，窗口内最终正确确认、清台账。
- 持续通信故障在普通/lease_terminal两分支耗尽既定有界窗口后BLOCKED。用只替换proxy自身time对象的虚拟monotonic推进三倍120秒窗口，保留实际循环；不阻塞真实360秒，不改全局时间。
- 确定HTTP409使用真实`urllib.error.HTTPError`作为RuntimeError的`__cause__`，符合Backend `translate_http_error=True`边界；单次请求后明确BLOCKED。
- 直接实际 `_finish_failure` 入口，stop已置位且reason=lease_lost；有spec/无spec两分支都先保留失败事实后BLOCKED，零step/status/complete，零模型/业务重执行。
- 所有终态重放均零终态后步骤写入、零模型/业务重执行。

## 相关回归

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_host_proxy.py tests/test_scene_host_proxy_r3.py tests/test_scene_host_proxy_r5.py tests/test_scene_host_orchestrator.py tests/test_scene_spray_wiring.py`

**89 passed，0 failed，0 skipped，35.81秒，rc=0**。包含正常失败、成功/失败pending及重启resume三条跨TTL续租、默认参数正规化与接线。

新文件Ruff格式/检查与`git diff --check`通过。新文件SHA256：`870aa1e5af5374e144916f052a2c4f6e13a2be14a882d9fd2a93f7c16cbea674`。

证据根：`/home/wang/work/.local/spray-runtime/`：

- 修前固定代码复现脚本：`r5-legacy-repro.py`。
- 修前正式日志：`r5-independent-before-final.log`。
- 修后新例：`r5-independent-after.log`。
- 修后组合：`r5-proxy-orchestrator-wiring-final.log`。

仅本机确定性夹具与假VLM HTTP；未调用远端模型、未全仓、未执行生产或原包写入。现有独立测试Skill覆盖本次验证，不新建Skill。
