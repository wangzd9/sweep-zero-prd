# TASK-16C：已输出 OCR 遗留逐项账

盘点于 2026-10-14T11:25:19+08:00。用户明确要求纳入本轮；原7批15条，c04/c06/c07零发现。当前实现状态见 TODO，不把本表作为第二任务表。原发现及旧裁决保留；所有新修复 SHA/独立复验尚待 owner 交付。

| 来源ID | 批次 | owner/叶任务 | 初裁与原问题 | 处置及必要复验 | 新修复SHA/证据 |
|---|---|---|---|---|---|
| C1 | c01 | C / TASK-16C-C | CONFIRMED / 维护：NO_MATCH 的不可达 elif | 删除死分支，保持实际 outcome 映射；复验 NO_MATCH 与 NOT_APPLICABLE。 | 待交付；C4沿用驳回，待候选回归 |
| C2 | c01 | C / TASK-16C-C | CONFIRMED / 维护：_scene_environment_paths 的 run 未使用 | 删除无效参数或实际用于有证据的路径读取；不能伪造历史路径。 | 待交付；C4沿用驳回，待候选回归 |
| C3 | c01 | C / TASK-16C-C | CONFIRMED / 部分误报：scene_terminal 死 context | 与 16C-c05-03 共用一处终态来源；INPUT_INVALID 属 PHASE0，原 OCR 对其场景归类驳回，不扩状态机。 | 待交付；C4沿用驳回，待候选回归 |
| C4 | c01 | C / TASK-16C-C | REJECTED / 已裁：建议将未开始改为已终止 | 保持真实未启动步骤“未开始”；与 DESIGN §7.3.3 冲突，不按 OCR 建议修改。新候选回归确认即可。 | 待交付；C4沿用驳回，待候选回归 |
| C5 | c02 | A / TASK-16C-A | CONFIRMED CORRECTION：双用途展示双标签却只命中单值 CASE | 共享多成员谓词，两类筛选都命中且 UID 唯一；Web/API、交集及分页测试。 | 待交付；C4沿用驳回，待候选回归 |
| C6 | c02 | A / TASK-16C-A | CONFIRMED / 维护：data_kind_labels_for 未使用且逻辑分叉 | 归一到共享分类真相或删死 helper，保留双用途双标，不复制第二分类规则。 | 待交付；C4沿用驳回，待候选回归 |
| C7 | c03 | A / TASK-16C-A | VERIFICATION_GAP → 复现后最小修复：日期原始字符串直入 DateTime，非法值 500 与截止日偏差 | 隔离严格 MySQL 复现，非法日期 422；日期全天边界、时区/aware-naive 与 Web 一致，含端点用例。 | 待交付；C4沿用驳回，待候选回归 |
| 16C-c03-02 | c03 | A / TASK-16C-A | 待核实 / 分页正确性：cursor 上下文漏新增实际筛选字段 | 覆盖 dataset_type、started_from/to 等实际过滤字段；换条件的 cursor 不漏/重、不复用错误上下文。 | 待交付；C4沿用驳回，待候选回归 |
| 16C-c03-03 | c03 | A / TASK-16C-A | 待核实 / 兼容：旧 cursor 的 scene_code None 与空字符串 | 按旧编码契约归一并验证旧合法 cursor；不能放行签名/筛选不匹配。 | 待交付；C4沿用驳回，待候选回归 |
| 16C-c03-04 | c03 | A / TASK-16C-A | 待核实 / 分类一致性：Python 分类与 SQL 子包条件分叉 | SCENE_SLICE 角色或有效 derivation 均可识别子包；含无血缘历史切片，不照搬仅 derivation 的误修。 | 待交付；C4沿用驳回，待候选回归 |
| C8 | c05 | C / TASK-16C-C | CONFIRMED CORRECTION：CANCELLED 场景无 retry-form，尾脚本 null.querySelector | 场景类型/DOM 存在性正确 guard；真实浏览器取消页无 JS 异常且不露自建强制重试。 | 待交付；C4沿用驳回，待候选回归 |
| C9 | c05 | C / TASK-16C-C | VERIFICATION_GAP：model_endpoint/model_identity 的历史写入证据不足 | 按当前已部署 snapshot/refs 核实际来源；有证据显示，无记录写未登记，不加 schema、不用当前 env 冒充历史。 | 待交付；C4沿用驳回，待候选回归 |
| 16C-c05-03 | c05 | C / TASK-16C-C | CONFIRMED / 与 C3 共修：模板终态硬编码与死变量重复 | 与 C3 同一修复 SHA，但保留两个来源；全部真实场景终态停止刷新，不改历史状态。 | 待交付；C4沿用驳回，待候选回归 |
| 16C-c05-04 | c05 | C / TASK-16C-C | CONFIRMED / DOM：lineage li 缺 ul/ol 容器 | 最小 HTML 修正，父子跳转和可访问结构浏览器取证。 | 待交付；C4沿用驳回，待候选回归 |
| 16C-c05-05 | c05 | C / TASK-16C-C | CONFIRMED / 类型隔离：NVIDIA 契约块仅看 bag.dataset_type | 先按 pipeline_type 分流，NVIDIA 来源场景 run 不显旧契约，原 NVIDIA run 正常。 | 待交付；C4沿用驳回，待候选回归 |

## 原证据与裁决约束

原日志 /home/wang/.hermes/cache/scratch/t16c_ocr/t16c_c01.log 至 c07.log；本目录 legacy-logs/ 为逐字节归档，hash见 legacy-logs/manifest.json。旧裁决见 reviews/TASK-16/16A-16B-ocr-batches.md r144–148 与 TODO 暂停历史。旧测试 test-receipts/TEST-TASK16C-independent/attempt-1.md 不替代返修验证。

C3/16C-c05-03一处实现关闭两条来源，不漏账、不重复造修复。C4已驳回，不派错误修复。待核实条必须记录复现/代码依据后确认或驳回，不靠OCR建议直接改业务。低风险维护项同文件最小处置；若不修，记录具体理由和原AC无影响证据，禁止笼统延后。

## 2026-10-14 交付/返修对账（协调者 13:23 更新）

- A 面（C5/C6/C7/16C-c03-02/03/04）：开发侧修复已随 `a1e416a`（12:39 冻结）交付，断言转派续 `563a91a`（12:46）；**新 OCR run 未起——被工具链 v1.13.0 版本门禁阻塞**（12:24:22 共享 `~/.npm-global/bin/ocr` 被未知写者由 v1.12.13 升级；入口只核验 v1.12.13）。工具链裁决=用户/入口维护面，协调者不擅改二进制/不放宽门禁。
- C 面（C1–C4/C8/C9/c05-03/04/05）：run `e7a5580c`（12:46 收口，实际执行 v1.13.0）裁决 13:00——**c05-04 半修=CC-R1 CONFIRMED 回派 C 最小返修**（`inbox/3号/TASK-16C-C/cc-r1-rework-dispatch-20261014.md`）；C4 维持驳回；其余 8 条本叶面处置成立（b02 0 findings+回执断言）。**CC-R1 返修 `ce5921d`（13:10 交付）协调者 13:27 独立核 diff+实际文件全绿，c05-04=修复已交付待独立验证**（TESTER 浏览器/MySQL 面；不整叶重跑 OCR）。
- 集成契约核验（13:12 实测，`wt-coord-intcheck-16c` seed+A`563a91a`+B`e399daf` 零冲突合并）：`test_web.py` 39 passed+2 failed——1 为 seed 固有环境性（口径在案），1 为 **line 364/366 旧 tab 断言失配=原转派单范围漏项**，勘误续单已派 A（仅 2 行，`inbox/1号/TASK-16C-A/shared-test-assert-transfer-correction-20261014.md`）。B 面 11 用例+07A 面+ui_minimal+A 查询面合跑 52 passed。

## 水雾发布审查覆盖债（TASK-16R）

| 原记录 | 已知事实 | 当前处理 |
|---|---|---|
| TASK-16B/direct-r3-ocr | e152465..15e4ef9；HARD_DEADLINE、rc1、NOT_EVALUATED | 缺有效覆盖，不是零发现；对照后续修复与已部署增量，只补当前未覆盖面 |
| final-r4/r5/r6-ocr | PREPARED，r6 spec为6ddcbcb..8e538bb | 准备不等于执行；去重/查manifest，禁止三份全部重新启动 |
| release-8e538bb-acceptance | 用户允许当次生产不等待OCR | 保留已接受上线事实，同时补审查债；不是永久豁免 |
| r4-correction-verdict | R4-01/02已修ad60e41，17红绿与89关联PASS | 已关闭，不重派；核对当前未回退 |
| production-nas-write-correction-20261013 | 3c9c496 NAS修复已接受，19+35测试，当次OCR例外 | 盘点该增量当前有效coverage；必要补审，不撤销原生产接受事实 |

协调者交付审查范围映射：旧base/head→当前代码/替代SHA→有效manifest及文件指纹→已有findings处置→真实未覆盖增量。16A、12S-B16条/S9b、07B已有接受证据，只查漏项，不全量重开。真实代码缺陷回原模块owner，单写冲突先检查点交接；验证缺口派TESTER。完成结论必须区分修复、驳回、有据不阻断、后续替代与未覆盖，不以“全部OCR已通过”概括。
