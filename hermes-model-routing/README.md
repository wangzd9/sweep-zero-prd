# Hermes 本地／云端模型切换

2026-10-15：已实现并启用，网关已安全重启、飞书重新连接；证据见[实施记录](../../analysis/hermes-model-routing-20261015/REPORT.md)。

当前持久模式为**自动**，选定云端为 **x-coding / gpt-6.1-sol / High**。

## 飞书怎么用

在已绑定的协调者、执行者或测试者群中发送以下完整消息（遵守该群原有 @机器人触达规则）：

| 消息 | 效果 |
|---|---|
| `查看模型状态` 或 `/llm status` | 查看当前模式、选择原因、云端模型和供应商 |
| `切换到云端模型` 或 `/llm cloud` | 全部已绑定角色的后续推理请求走当前云端供应商 |
| `切换到DeepSeek` 或 `/llm cloud sub2api` | 选择 Sub2API DeepSeek，并进入云端模式 |
| `切换到GPT` 或 `/llm cloud xcoding` | 选择 x-coding 已配置模型，并进入云端模式；其可用性见实施记录 |
| `恢复自动切换` 或 `/llm auto` | 恢复"只看本地队列"的自动判断；保留已选择的云端供应商 |
| `切换到本地模型` 或 `/llm local` | 本地优先，只看本地等待队列；忙时走云端 |

统一切换请使用上述消息或`/llm`指令；原生`/model`不会更新本插件共享选路状态，也不会同步OCR。

控制指令由程序处理，不调用模型、不进入业务待办；群模型忙时也直接处理。设置在本机持久化，影响同一 Hermes home 中全部已绑定角色的群会话、后台 poll 和能追溯到该角色的子会话。普通未绑定会话沿用原设置。不能通过在业务描述中引用指令触发切换。

已发出的单次请求允许结束；每次后续主推理请求（含工具循环和重试）重新选路，保留会话、冻结 system 前缀和已经执行的工具结果。指令回执确认设置和当前判断，不等同于供应商推理成功。

## 自动规则

自动模式只看本地 vLLM 等待队列：`waiting=0` 且 `running` 可读时使用本地，不再受时间窗口或流水线状态约束；`running` 占用并发槽不阻止准入，但 `running`／`waiting` 任一未知仍走云端。其余情况使用选定云端。人工云端模式跳过负载探测。

本地准入只做一次 GET（超时2秒），只读本地等待队列。没有常驻推理监控、GPU调度平台或让模型判断模型的步骤。

这是请求前检查，不能消除检查与提交之间的竞态，也不会抢占已经发出的请求。需要稳定跑云端时用 `切换到云端模型`。云端故障不会绕过本地准入或沿旧 fallback 链抢占本地；按原有有限重试返回错误。

## 供应商与配置

默认云端供应商为 **Sub2API DeepSeek**，模型以`查看模型状态`的当前配置为准：`https://sub.vankit.top/v1`，Responses，`store:false`。真实原生 Agent 的流式请求、一次终端工具及结果接续已验证。

另保留 `numenume-cloud`，地址 `https://sub.numenume.site/v1`；模型目录有 `deepseek-v4-flash` 与 `deepseek-v4-pro`，现场推理502／超时，不作为默认。新增 `xcoding-cloud`，地址 `https://x-coding.net/v1`，按用户最终选择使用 **gpt-6.1-sol / High**，Responses；gpt-5.5虽在目录中但实测不支持。原生OCR真实审查已完成，详见实施记录。

本地沿用 `qwen-a100`，Chat Completions。所有云端凭据只放在 `~/.hermes/.env`，文件权限600，分别为 `SUB2API_API_KEY`、`NUMENUME_API_KEY`、`XCODING_API_KEY`。文档、spec和群回执不包含密钥。

原生命名供应商在 `~/.hermes/config.yaml` 的 `providers`；选路设置在 `plugins.entries.role-workflow-runtime.settings.model_routing`；模式和云端选择在 `~/.hermes/runtime/model-routing-state.json`。配置由原生原子写入口维护，保留注释。`cloud_profiles` 提供 `sub2api`、`xcoding`、`numenume` 三个名字，`default_cloud_profile` 为 `sub2api`。

用户给出的 Codex TOML 只用于提取端点、模型和协议，不更改本机 Codex 配置；`review_model`、goals、WSL等不是 Hermes 选路配置。OCR是OpenCodeReview代码审查，已另外接入同一设置：新run每批启动前选择同一供应商/模型，保留在途批次、串行双锁、固定快照、全覆盖及真实结果门禁；每批记录实际身份并核对manifest。旧1.5冻结run仍保留旧行为和可读性。独立强模型审查、数据流水线及独立辅助调用沿用原配置。

## 实现与验证

策略位于 `hermes-role-runtime/model_routing.py`；两个通用核心 hook 为 `resolve_model_route` 与 `pre_gateway_busy_dispatch`。前者在构造每个物理主推理请求前运行，复用原生供应商解析与 `switch_model`；后者在原生忙碌入口鉴权后、排队前处理控制。无策略插件时保留原行为；选路策略异常／超时阻止原请求。

回归包括时间边界、忙／未知保护、身份与群隔离、模式／供应商持久化、真实 A→B→A 配置凭据隔离、忙碌入口、原生工具循环本地→云端→本地、Responses流式和参数不串线。原生本地HTTP桩验证脚本为 `hermes-role-runtime/scripts/validate_model_routing.py`。真实飞书收发未通过主动测试消息验证；用户自然使用与原生入口测试分别记证。

重启部署只在在途任务自然结束、原生聚合工作数为零时进行。等待期间保持聊天开放，确认空闲后才短暂排空重启，防止长时间出现 maintenance/draining 提示。
