# 本机模型端点变更回执（维护事项，不新增业务任务）

用户已要求本机千问/OCR/Hermes及相关服务永久LAN直连，现行URL为 `http://192.168.2.45:8002/v1`，模型保持原ID。Codex独立API不在本次范围内。

Hermes主模型/provider、OCR、记忆压缩配置与本机devflow默认地址、相关运维Skill已同步。旧18002隧道已取消自启，10:31:05确认旧连接清空后停止。Gateway没有强制重启，后续回合原生解析新的路由；记忆worker已重启且health为ok。

第7次OCR原runner/PID1658128已于10:32:51结束，rc=1。直连下仍有context compaction请求cancelled；session `ba32eca1-9837-48d3-bc19-3a29939eec36`，1个选中单元失败，不能按0findings放行，也不能继续把隧道认定为唯一根因。本次未另起审查，按用户“再次失败升级”的既定政策停止自动重试。

旧runner的finally确实回写了旧地址，独立单元已纠正；10:33:00的`finalizer-status.json`为`complete_tunnel_stopped`，直连保留且旧隧道停用。后续读取原审查日志/session归档失败证据，保持受审门禁。

协调者接续时使用现行端点，不按旧日志/旧worktree Skill恢复隧道。原task/attempt、审查范围及门禁不变，仍根据实际session完整覆盖和结果裁决。可按既有权限将本回执汇总入时间线，不增加返修任务或重做已接受内容。

实施与证据：[DIRECT-CONNECTION-20261013.md](../../../../analysis/hermes-qwen-load-20261012/DIRECT-CONNECTION-20261013.md)。备份：`/home/wang/.codex/skill-migrations/llm-direct-20261013-102244/`。真实短推理HTTP200/OK约0.247秒；开发工作流27项测试和静态检查通过。长OCR失败与直连切换完成分别记录。
