# 直接修复回执（2026-10-14 10:23 +08:00 起）

- 三份待绑定提交已通过正式源登记与用途事件消费 API 恢复：`a65a25a7… → scene-a4824f1c…`（SUCCESS）、`87dfebaa… → scene-eb4397c3…`（NOT_APPLICABLE）、`518089ed… → scene-24ab78bb…`（NOT_APPLICABLE）。全部 SCHEDULED、generation=1、事件 CONSUMED；created_runs=0/reused_runs=3/errors=[]，全批仍为7条运行，原 attempt 未变。
- 首次携带快速指纹的恢复请求被409拒绝：父子共享快指纹触发登记接口的切片保护。未写入、未重试执行；后按精确原包 ready 路径恢复、保留已有指纹，源身份与冻结场景身份预检相同。证据：`doc/analysis/spray-batch-progress-20261014/binding-repair.jsonl`。
- 大包已用原租约经正式步骤 API 补报真实阶段：PRECHECK=DONE、EXTRACT=DONE、INFER=RUNNING，后续QUEUED。依据：预检 checkpoint、5373 PCD/1781 JPG、执行进程自身持有到模型8002的ESTABLISHED连接。不改checkpoint、不重启、不 cancel/retry；旧代理仍缺逐帧持久计数，完成帧数未知。
- 证据：`doc/analysis/spray-batch-progress-20261014/live-step-repair.json`。新进度与逐帧恢复能力仍在隔离树开发，未宣称生产已加载。
- 请协调者按本回执更新唯一 BATCH-STATUS，并由TESTER核复用结果及既有产物；A结束三份提交“等待绑定”，不要再上传/重提/retry。本批剩余：大包终态及跨DB3结果验收、空包正式状态改善；不能标全批DONE。
- 用户最新明确：大包优化由ros2_slice负责人先实施，平台待交付后适配，当前不要派平台流式/分批缓存/并发等优化任务。恢复回归c5d98d0，45项定向测试通过；仅测试无业务变更，OCR prepare无入选文件、NOT_EVALUATED零调用，不标PASS、不额外启动模型。隔离分支保留，不覆盖用户主仓改动。
