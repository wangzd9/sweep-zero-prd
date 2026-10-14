# 16B-r4 独立机械故障验证

- 结论：**PASS，交协调者裁决；不代替强审、MySQL、真实模型或生产门禁。**
- 时间：2026-10-13 19:04–19:14 +08:00。
- 测试根：`/home/wang/.local/state/rosbag-scene/wt-codex-spray-release`；基线HEAD `6e91c3b78660b2541b8e25e36473921a7e243d58`，r4修复未提交时验证。协调者随后冻结实际SHA。
- 本角色只修改两个测试文件；未修改业务、OCR/强审、合并、生产、真实模型。组合仅本机确定性夹具/假VLM HTTP。

## 修前反例

- 成功后首GET一次/持续故障：实际execute收尾被写成FINALIZING_FAILURE，**2 failed**。日志 `.local/spray-runtime/r4-first-get-before.log`。
- 将原强审目标 `15e4ef9094c7b51ec6f38832533c670d2664b985` 的完整proxy代码只读加载到进程内存（不回滚文件），运行同一TTL测试：原执行成功待补报、失败待补报、重启resume均未维持续租；过期/新attempt/缺租约未明确BLOCKED。**6 failed，16 deselected，3.58秒**。日志 `r4-ttl-legacy-before.log`；脚本 `r4-ttl-legacy-repro.py`。
- 文件 `r4-ttl-before.log` 是编写测试时恰逢业务修复落地后的初验（3 passed），不能当修前失败证据；修前证据以固定旧SHA内存复现日志为准。

## 修后确认

新文件 `tests/test_scene_host_proxy_r3.py` 共 **22用例**，保留已有恢复/默认参数检查，新增：

- 完整execute边界的首GET一次/持续失败：先持久成功意图，绝不写错误SCENE_FAILED；故障解除后正确complete，模型/发布不重执行。
- 真实时间推进租约替身：每次步骤、status、complete、heartbeat都检查原token/attempt/expiry；heartbeat真正延长有效期。为快速稳定测试，TTL加速为0.5秒，心跳间隔0.03秒；保持真实过期语义，不声称跑了生产120秒。
- 原执行成功待补报、原执行失败待补报、重启resume三个入口，持续步骤失败跨过 **2.2倍初始TTL**，仍维持心跳/ACTIVE/原attempt；解除故障后成功或原失败正确收敛，业务/模型不增加，终态后步骤写入0。
- 已过期、新attempt、`lease_expires_at=None`：有限停止，保留FINALIZATION_BLOCKED事实；零步骤/status/complete写入，零业务/模型。
- watchdog明确lease_lost停写信号：先BLOCKED，零收尾写入。

旧 `tests/test_scene_host_proxy.py` 的持续失败用例改为事件控制真实pending，断言台账和ACTIVE保留；解除故障后后台只补报原失败、清台账和ACTIVE。finally设置释放/停止事件并等ACTIVE退出，避免永久daemon；没有删除或削弱原失败断言。

单次恢复夹具只暂停后台线程调度，以便观察持久pending再模拟进程重启；真实TTL三入口使用实际线程及实际watchdog，不受该替身影响。

## 最终命令和结果

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_host_proxy.py tests/test_scene_host_proxy_r3.py tests/test_scene_host_orchestrator.py tests/test_scene_spray_wiring.py`

**72 passed，0 failed，0 skipped，33.88秒，rc=0**。

- 日志：`/home/wang/work/.local/spray-runtime/r4-proxy-orchestrator-wiring-final.log`。
- Ruff两测试文件及`git diff --check`通过。
- `test_scene_host_proxy_r3.py` SHA256：`93a268a8b9bb80567b9d7776805cb05719d248e6c31a7c7f6e38bba4527d0c4b`。
- `test_scene_host_proxy.py` SHA256：`eb050f916376e1eb2c6a3cda1b9a986129dda6e3f3436e51f0509f25962f96ff`。

本轮未全仓，未触碰NAS原包/生产库/真实模型。现有独立测试Skill覆盖本次验证，无新Skill。
