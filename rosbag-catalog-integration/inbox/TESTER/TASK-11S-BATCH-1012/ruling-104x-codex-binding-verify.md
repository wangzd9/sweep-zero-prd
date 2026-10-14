> **⚠️ 本核派单并入 `POST-SPRAY-CLOSEOUT-20261014`（10:49:02，当前调度入口）**：下方核对范围与本卡『角色接续 TESTER』的 `post-release-closeout-20261014.md` 增补卡一致，TESTER 以 closeout 增补卡为准读取+ACK，本文件为细节补充，**不重复领取、不双份记账**。

# TASK-11S-BATCH-1012 / TESTER / 独立验收：Codex flat 三提交绑定恢复（10:23 回执）

时间：2026-10-14 10:4x +08:00（协调者消费 `codex-repair-receipt-20261014.md` 10:23）。owner=TESTER，attempt-1。范围=你既有独立验收范围增量，**只读**，不提交/不 retry/不重调模型/不改生产。

## Codex 回执声称（待你独立核实，不直接采信）

- 三份 flat 提交经正式源登记恢复：`a65a25a7→scene-a4824f1c`(SUCCESS)、`87dfebaa→scene-eb4397c3`(NOT_APPLICABLE)、`518089ed→scene-24ab78bb`(NOT_APPLICABLE)；全 **SCHEDULED、generation=1、事件 CONSUMED**；**created_runs=0 / reused_runs=3 / errors=[]**；全批仍 7 run，原 attempt 未变。
- 首载快指纹恢复请求被 409（父子共享快指纹触发登记接口切片保护），未写入、未重试执行；后按精确原包 ready 路径恢复，源身份与冻结场景身份预检相同。
- 大包 `scene-4acf689f` 经正式步骤 API 补报 PRECHECK=DONE/EXTRACT=DONE/INFER=RUNNING，不改 checkpoint、不重启。
- 证据：`/home/wang/work/doc/analysis/spray-batch-progress-20261014/binding-repair.jsonl`、`live-step-repair.json`。

## 你核对面（逐提交，处理机生产 3c9c496 只读实测）

1. **绑定身份一致**：三 submission 现态=SCHEDULED、source_generation=1、bound_source 指向**各自 flat ready 源**（非已删除 date-grouped dup 源 FFDEE943/9C9456B6/205E5054）、source_metadata 完整（vehicle_code=test/batch/Asia/Shanghai/sensor_profile）、bound_ready_path=flat 路径。
2. **复用不新建**：`reused_runs=3` 实证——三提交绑定 run 为既有 `scene-a4824f1c`/`scene-eb4397c3`/`scene-24ab78bb`（attempt 未变、非新建第 8 run）；全批 run 仍 7 条；无新模型请求/无新 slice 烧（14_42_48 已有 dup SUCCESS 切片，复用后不得再产生第二份）。
3. **outcome 一致**：a4824f1c=SUCCESS、eb4397c3/24ab78bb=NOT_APPLICABLE（与 B 21:12 独立取证/C dup 面口径一致）；NOT_APPLICABLE 两包**无伪切片**（slices/.staging 无新增）。
4. **事件/幂等**：purpose event CONSUMED；两次正式 reconcile 幂等（对已发布 source 切片 reconcile 不重复/不变）；409 首载拒绝留痕可追溯（未写入未重试执行）。
5. **大包补报**：`scene-4acf689f` 八步现 PRECHECK/EXTRACT=DONE、INFER=RUNNING、后续 QUEUED；**补报未改 checkpoint、未重启**（work 树 checkpoint.json mtime 应未翻、proxy pid 3495931 连续未重启）；INFER 跨夜继续不 kill/retry 口径不变。
6. **回归口径**：Codex「回归 c5d98d0 45 项定向测试通过、仅测试无业务变更、隔离分支保留不覆盖用户主仓」——你**不重复跑**（属 Codex 面），只核隔离分支未污染生产 3c9c496（生产栈版本未变）。

## 交付

`test-receipts/TASK-11S-BATCH-1012/attempt-1.md` 增量核销 + 落实质事件（带 event_id/occurred_at/task/attempt/证据/下一步）。失败/偏差如实保留证据不 PASS。本批剩余=大包终态+跨 DB3 结果验收、空包正式状态改善，**不能标全批 DONE**；大包终态后你再核 16_02_03 八步/真实时间戳边界/两次 reconcile。