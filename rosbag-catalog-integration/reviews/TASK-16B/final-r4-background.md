# 固定最终修复增量：29af08a58819790fe6cc467603091817a5b705fb

用户要求Codex直接解决收尾上线；原grant6b2d83fb有效。本次base=6ddcbcb，target=29af08a58819790fe6cc467603091817a5b705fb，仅上轮22189dc…两项CORRECTION及真实全链暴露的必要索引/部署映射修复。不是全量审查，不扩UI或模型要求。

原R1-02：待收尾不再停止心跳/释放ACTIVE，移交后台finalization_loop续租并仅补报；恢复线程自己续租。有效身份跨TTL后可收敛；实际过期/缺租约/attempt变化/明确停写时持久FINALIZATION_BLOCKED，禁止旧身份重写/重执行业务。三个租约周期有界收尾，超窗保留证据交现有受控reconcile，不全局放宽Backend租约。ACTIVE防重复写者，状态分支不回模型。

原R3-01：reporter从resolve_spec冻结attempt（直接构造时从持久台账读），成功意图保存前无Backend GET；后续GET/step/complete失败保持FINALIZING_SUCCESS。

独立机械验证：先以实际旧函数复现首GET两例FAIL；修后proxy/orchestrator/wiring共72PASS，其中22参数/故障例。真实单调时钟有效期Backend逐写核token/attempt/expiry，成功pending、失败pending、重启resume三支均跨2.2倍原TTL保持续租再解除故障，正确outcome且模型/业务不增加；过期/新attempt/无租约/stop先block均零补写。旧单次夹具暂停后台调度用于精确断点，新TTL族真实线程/心跳/时钟验证，并清理daemon，不用布尔lease伪证。日志.local/spray-runtime/r4-proxy-orchestrator-wiring-final.log。

真实VLM已完成：6ddcbcb固定正式Scanner/Orchestrator/proxy/MySQL，12次请求、1非空3.302s水雾切片、1752消息/43MB、8步DONE，原包SHA不变。独立验收发现child.vehicle为空、relative_path漏scene/slices、started_at UTC naive错8h。6e91c3b最小修复：继承父车，按服务端场景根相对NAS_STORAGE_ROOT登记，epoch整秒转业务Asia/Shanghai naive，原零UPDATE幂等保护保留。新增3例修前FAIL→相关50PASS；同真实产物用正式reconcile两次200，车辆test/路径指到真实DB3/时间15:58正确、current及8步不变、零新模型。证据real-e2e-6ddcbcb02004/reconcile-result.json。

部署只补必需装配：bag.relative_path相对存储根，proxy只挂ready子树到/nas/rosbag_scene_processing/ready并前缀/nas；独立发布slices。Backend/proxy同一只读受控能力配置，catalog-scene overlay显式开启且默认INGEST0/CONSUMER0/URL空；源码默认spray仍禁用。Compose真实解析逐服务比较旧NAS/NVIDIA/A100环境/挂载不变，固定imageID/refs只读/home工作根。零生产迁移/服务切换（仅用户授权准备空目录及staging预构建）。

请确认原两项是否关闭，并仅报告以上真实需求范围内可复现问题。不要重审已关闭R1-01/03/04/05、B算法或提出新可用性标准。若存在缺陷给准确触发和最小修复；此强审不替代弱OCR及生产验收。最终生产尚未执行。
