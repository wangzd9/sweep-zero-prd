# TASK-12S-E OCR 裁决（retry1，协调者 2026-10-15 08:52 更正版）

> **更正与撤销声明**：08:36 首发版本裁决"findings=0/零 CORRECTION 级"系误判——只核了各批 `b0*-diagnosis.json` 的 coverage 字段，漏读 `b0*.log` 的 comments。retry1 三批日志实际含 **11 条 findings（2 HIGH / 4 MEDIUM / 5 LOW；7+2+2 分列 b01/b02/b03）**，其中 **6 条 CONFIRMED CORRECTION（E-R1/R2/R3/R4/R7/R8）** + 2 条 LOW 非阻塞改进 + 1 条 LOW REJECTED（ruff W292 指控依据错误：项目 ruff select=E,F,I,UP 未启用 W 族）+ 1 条 LOW 防御分支注释已含于 E-R4。**首发版"OCR 面收口=零 findings"及据此的 TASK-12S-E 接受登记全部撤销**，原首发文本保留在文末"已撤销首发版"节，不重写历史。根因教训已补入协调者 Skill OCR 参考（裁决前必须逐批解析 log comments，diagnosis 的 coverage_complete 不等于零 findings）。

- **run**：`reviews/TASK-12S-E/ocr-run-20261014-retry1`（run `3480a161`，AWAITING_DECISION；b01/b02/b03 全 REVIEW_COMPLETE、rc=0、coverage_complete=true、identity 匹配、范围 `16a154f..b39a3ec`）
- **裁决人**：协调者（2026-10-15 08:52 +08:00，逐条对照冻结代码 `b39a3ec` 核实）

## 逐条裁决（E-R1～E-R8，编号供返修引用）

### b01 `app/services/pending_binding.py`（7 findings）

- **E-R1【HIGH，CONFIRMED CORRECTION】对账绑定行 `bound_ready_path` 重复拼接物理段**（第 216 行）。核实：`upsert_bag` 落库 `relative_path = directory.removeprefix(storage_root)`（catalog_ingest.py:30）恒为 storage 相对段；而 `ready_root` 是冻结绝对根。`f"{ready_root}/{bag.relative_path}"` 产出 `/test/scene/ready/scene/ready/pfx/bag` 类不存在路径；主 bind 路径（ingest_service.py:1184）存的是 scanner 传入真实物理 `ready_path`。"精确原包身份证据"字段在恢复登记行上与登记行不一致，违反 AC-20.2 证据契约。修复口径：`bound_ready_path = f"{storage_root}/{bag.relative_path}"`（OCR 建议同）或等价物理路径口径，并补断言测试。
- **E-R2【MEDIUM，CONFIRMED CORRECTION】`bound_incoming_path` 丢失 `incoming_prefix` 段**（第 215 行）。核实：`sub.relative_path` 是入口相对路径（match_profile_for_incoming 已剥前缀），主路径存物理 `incoming_path`（含前缀）。凡非空前缀入口（场景入口全部适用）对账行落错路径。修复：`prefix` 非空时拼回前缀段。
- **E-R3【MEDIUM，CONFIRMED CORRECTION】对账绑定漏持久化 `bound_purposes_json`**（第 212 行）。核实：主路径 ingest_service.py:1187 持久化用途集合；恢复登记短路（:1125）读该字段回显 `scheduled_purposes/self_built`。对账绑定（SCHEDULED）的提交在后续 MOVING/MOVED 再登记时回显 `[]/False`，破坏"同一 bag 两次登记用途一致"不变式。修复：与主路径同口径 `json.dumps(sorted({e.purpose for e in events}))`。
- **E-R4【MEDIUM，CONFIRMED CORRECTION】防御分支注释声称的身份防线实际为空操作**（第 162-165 行注释 + 第 181-183 行 guard）。核实：`ready_root` 不在受控根下时 `derive_root_id_for_ready(ready_root)` 返回 None，`configured is not None and ...` guard 恒假；短段候选可命中任意路径登记的同名 bag 行而无根身份校验。生产配置下 ready 根恒在 storage 根下（config 校验），风险限于配置异常场景，但注释不得断言不存在的防线。修复：更正注释；裸短段候选命中绑定时要求根身份非 None（或 snapshot_root 匹配）再放行。
- **E-R5【LOW，CONFIRMED CORRECTION】PENDING_INPUT 选取无 ORDER BY**（第 99-101 行）。核实：>50 条时批次组成 DB 自由裁量，SQLite/MySQL 行为不一致，未绑提交可长期饥饿。修复：`order_by(IngestSubmission.created_at)` FIFO。
- **【LOW，REJECTED】文件尾缺换行"ruff W292"指控**（第 218-220 行）。核实：项目 ruff 配置 `select = ["E","F","I","UP"]`，**W 族未启用**，WT-01 实测 `ruff check` All checks passed——findings 的 ruff 指控依据错误，不作门禁；补尾换行可在返修中顺手做（零成本），不作为 CORRECTION。
- （第 2 条 file_read 失败=OCR 自身工具误用行区间，无业务影响，coverage 完整。）

### b02 `app/services/scene_schedule_consumer.py`（2 findings）

- **E-R6【LOW，CONFIRMED CORRECTION】poll docstring"03B outbox 未合入时无副作用"已过时**（第 383-384 行）。核实：新增对账步骤在每次 consume 调用执行，outbox 恒空时仍会绑定 PENDING_INPUT 提交、写业务库、出用途事件。修复：更正 docstring（outbox 空仅意味消费统计全零，不意味无对账副作用）。
- **【LOW，CONFIRMED（非阻塞改进）】全零 stats 字面量双分支重复**（第 398-411 行）。核实属实：两分支仅差 `pending_reconciled` 一 key，新增统计 key 有漂移风险。同批顺手修，不作独立门禁。

### b03 `app/services/source_service.py`（2 findings）

- **E-R7【HIGH，CONFIRMED CORRECTION】tier-2 incoming 侧检测恒空，incoming→ready 移动恢复（12S-C 语义）在真实数据上失效**（第 207-216 行）。核实：`incoming_roots` 用绝对配置根（`/test/incoming`、`/test/scene/incoming`，config.py 校验恒在 storage 根下且以 `/` 开头），而 `r.relative_path` 是 storage 相对段（如 `incoming/bag`）——`== root`/`startswith(root+"/")` 恒 False。现有测试 `test_source_registration_reuses_source_id_after_incoming_to_ready_move` 以异常口径行（relative_path 存绝对段 `/test/incoming/bag-moved`）侥幸通过，掩盖真实数据失效。修复：比对前把 incoming 根归一到 storage 相对形式（OCR 建议 `_to_rel` 同），并以**真实 storage 相对行**补夹具测试。
- **E-R8【MEDIUM，CONFIRMED CORRECTION】409 栅栏先于移动恢复身份评估触发**（第 199-206 行）。核实：注释规则为"无准确身份（1/2 均无）且存在同指纹切片 → 409"，但代码在 tier-2 判定前就 `slice_share and not exact_originals → 409`。合法 12S-C 恢复场景（incoming 侧恰 1 原包行 + 本次注册落在受控 ready 根 + 同指纹切片兄弟行）被永久 409——scanner 重放每轮重试、SOURCE_CLEANED 前非终态=本任务要消灭的"误拒→永不自愈"在 tier-2 上复现。修复：先算 `incoming_side`/`registered_under_ready`，`len(incoming_side)==1 and registered_under_ready` 时豁免 409 走移动恢复；切片兄弟行不参与豁免判定（血缘不动）。

## 结论与门禁处置

- **OCR 面：不通过。** 6 条 CONFIRMED CORRECTION（E-R1/R2/R3/R4/R5/R7/R8 中除 LOW 顺手项外均强制）+ 2 条 LOW 非阻塞改进 + 1 条 REJECTED。
- **TASK-12S-E 状态：接受撤销 → REWORK**。TESTER attempt-1 PASS 证据保留有效（针对 `b39a3ec` 的既有行为面），但 E-R1/R2/R3/R7/R8 是 `b39a3ec` 上的代码缺陷，TESTER 夹具未覆盖真实 storage 相对路径口径（E-R7 被异常口径夹具掩盖）——返修交付后 TESTER 须对修复项增量复验（重点：真实口径移动恢复夹具 + 对账行三字段断言 + 409 豁免两路）。
- **返修**：attempt-2 最小返修派原 owner A（`inbox/1号/TASK-12S-E/attempt-2-r1-rework-dispatch.md`，base `b39a3ec` 续 commit，只修 E-R1～E-R8 对应点+用例，不扩需求）。
- **TASK-12S-F**：08:38 派单前提"E 已接受"失效；已发 supplement 给 B——base 改为 E attempt-2 冻结 head（B 开发中按文件边界继续，交付前 rebase 到新 head），B 已 ACK/开工事实保留。
- **OCR 增量**：A 交付 attempt-2 后走唯一入口对新 commit 增量审查（新交付身份，不消耗 retry 额度）。
- **强审查**：24h 授权（grant 9827cf8f，至 2026-10-15 22:24）0 调用保留；E/F 返修批次收口后按 strong-review 判定，不预启动。

---

## 已撤销首发版（2026-10-15 08:36，保留原始错误记录）

> 首发版全文如下，其"零 findings"结论与 OCR 原始日志矛盾，已按上方更正版处置。**不得再引用首发版口径。**

```text
# TASK-12S-E OCR 裁决（retry1，协调者 2026-10-15 08:36 +08:00）

- **run**：`reviews/TASK-12S-E/ocr-run-20261014-retry1`（retry1 唯一额度，01:04 经固定入口 prepare --reuse-run + start）
- **状态**：AWAITING_DECISION，b01/b02/b03 全 REVIEW_COMPLETE；manifest 完整。
- **findings**：0（各批报告零 CORRECTION/零 SEVERITY 条目）。
- **裁决**：**OCR 面收口=零 findings，12S-E 代码审查门禁满足**。
- **接受条件核对**（双证）：
  1. TESTER attempt-1 独立验证 **PASS**（00:43 回执 `test-receipts/TASK-12S-E/attempt-1.md`：冻结 `b39a3ec`，真 MySQL 8.4.11 隔离库五面全过、12+154 passed、8/8 探针、零越界、隔离资源自毁归零）；
  2. OCR 初审（HARD_DEADLINE，vllm 槽被 1012 大包 INFER 争抢所致，非代码问题）→ retry1 补审 **0 findings**。
- **结论**：TASK-12S-E 接受门禁证据齐，协调者做接受登记（E DONE，冻结 `b39a3ec` 随后续集成候选合入，不单独合 main——E 属水雾线，合入口径按 12S 父任务集成节奏）。
- **后续**：12S-F（异常输入拒绝恢复）前置（E 接受释放公共文件）转满足，下轮巡检派单。
```