# TASK-16B R3直接修复增量复核

固定base=e152465，target=15e4ef9094c7b51ec6f38832533c670d2664b985。用户要求Codex直接修复收尾上线，grant6b2d83fb仍有效。仅核原R1-02/03未关闭问题及必要Backend事务链；R1-01/04/05已关闭，不重审全量。审查树含部署只读挂载修复，由常规OCR覆盖；本强审重点恢复/租约/后端终态。

R1-02：_report_steps返回最终确认；失败/GET持续错不删恢复台账。R1-03：先持久FINALIZING_FAILURE/SUCCESS意图，恢复仅补报不再执行业务。成功七步先确认，Backend complete同事务将REGISTER推进DONE后清租约；新增flush支持缺REGISTER且autoflush=False。

另真实E2E发现正常默认提交hash与proxy不一致，因registry(None)默认15整数绕过正规化，Backend空参数正规化成15.0；proxy最小改为{}，保留hash failclosed；不改全局registry或旧坡道hash。新增真实Registry默认参数回归修前spray FAIL/slope PASS，修后13恢复/参数+11接线共24PASS，生产无写入。

独立验证：修前5失败→修后11严格Backend故障注入PASS，proxy/orchestrator50PASS；Backend真实事务新增8例，相关组94PASS；终态后step拒绝、恢复新增模型调用0、回滚不留半成品。报告test-receipts/TEST-TASK16B-r3/codex-independent-20261013.md。最终集成候选6ddcbcb含已审B f76e2a9、main6c7d983及已审C接线92dcb52；真实模型全链另行执行，不预报PASS。

请仅裁原两问题是否关闭及本变更必需调用链中可复现的CORRECTION/VERIFICATION_GAP；给触发步骤和最小修复。风格/文件大小/新可用性标准不扩本期需求。本强审不替代弱OCR或真实全链。


部署装配保持原生产边界：不可变镜像ID、pull_policy never；业务源码/ready/7图只读挂载，state/work宿主home可写；decoder实际容器路径受控注入；env root:data-process0640。原包不可变、模型仅远端图片请求、不改算法阈值/抽样/旧路线。Compose解析及bash语法已过。Markdown/tests由机械独立验证，业务和运行配置全审。
