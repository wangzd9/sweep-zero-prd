---
task: TASK-06B
item: attempt-1-r2-rework
owner: 2号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 11:43
base: main eff0479（含 2e674b2 你的 06B 合入，11:31）
round: R2 强模型返修第 1 轮（有界 2 轮）
---
# 2号返修：R2-03/04/05-switch/06/07/08/09/10/11（8 条，R2 强模型 11:31 裁决，全部 HIGH 除 R2-11 MEDIUM）

R2 审查结论：REWORK_REQUIRED（10 HIGH + 1 MEDIUM）。裁决文件 reviews/strongmodel/R2-20261010-verdict.md，
独立复现证据 R2-20261010-evidence/（mysql_repro.py EXIT 0 复现 1093/1101/PENDING 卡死、
test_r2_repro.py 8 断言确认错误行为、135 定向回归证明现有用例未覆盖）。
**06B 已合入 main（2e674b2），不指示回退**——你直接在 main 基础上新建 worktree 分支返修。
核心教训：**SQLite 全绿 ≠ MySQL 放行**（自引用 UPDATE/双引号标识符 SQLite 都容忍）；
现有 49 passed 全在 SQLite，未覆盖强模型命中的故障路径。

## 修复链 1：版本排序 + 完成事务 + 对账（R2-05 switch 侧 / R2-04 / R2-07）
- **R2-05 switch 侧**（契约与 1号 R2-05 create 侧逐字一致）：**所有 scene run 创建时（事件消费
  或显式 API，同事务）即分配并绑定 SceneAnalysisVersion 行；换版比较用版本行提交时点顺序
  （分配时刻的持久 id 序号），不用回报时点。** 1号负责 create 侧，你负责 switch 侧：
  `switch_current` 的版本先后裁决字段从"回报时的 created_at/首回报分配"改为 av 行分配序号。
  晚到旧任务不得覆盖新分析 current（强模型复现：旧事件 run 后 complete → current 回旧 run，必须消除）。
- **R2-04**：`complete_scene` 终态 commit 后换版（352）失败/中断，重试只 `_replay_switch`（319）不补换版
  → 完整结果永久非 current、HTTP 200/DONE 掩盖未完成发布。修复：可用性/当前指针/成功终态一致事务内收敛，
  或持久化可恢复的换版待办（重试完成缺失步骤）；终态重放必须核对原 manifest 内容身份（现只比 outcome），
  并回显真实换版状态（replayed 响应带实际 current/switch 结果，不得以"幂等重放"隐藏未完成步骤）。
- **R2-07**：`reconcile_scene`（532）按父包前缀扫描全部版本记录，历史合法切片（两次 reanalysis 保留）
  被当"混合版本"409 拒绝。修复：读取结果前按本次 run_id/源代次/场景版本筛选目标，只核对本次预期切片集合；
  历史记录保留且不参与摘要等值判断（不能先重写身份再筛选）。
- 回归：R2-05 三种交错（自动旧→显式新/两次自动/显式旧→自动新，各含旧先/后完成 + NO_MATCH）；
  R2-04 终态前后故障注入（409/异常注入后重试 complete → current 必须收敛）；
  R2-07 两个以上合法历史版本共存 + 重复 reconcile + 目标版本缺片/混入错误记录分别断言。

## 修复链 2：身份与执行边界（R2-08 / R2-09 / R2-06）
- **R2-08**：`_require_scene_run`（70）只比外层 source_generation，`parse_report_manifest`（170）用当前 run
  的 run_id/source_id 覆盖 raw 字段 → 后续身份比较恒真；旧代次 run 可登记为当前源结果（复现 200/current=true）。
  修复：校验原始 run_id/source_id/scene_code，要求冻结 run 代次、manifest 代次、外层请求、父包当前代次四方相等，
  按源身份契约核对指纹；不静默覆盖 manifest 身份；**reconcile 恢复路径同样身份校验**（现只比外层代次）。
- **R2-09**：`require_valid_task_lease`（security.py:34）`if not run.lease_token_hash: return`——
  未领取 run 无 token 直接过，`/results` 对排队 run 200 并绑定内容身份，真实执行者随后被 409 阻断（复现）。
  修复：场景写边界要求非终态 run 处于允许执行状态 + 有效租约（token 验证）；终态只允许**已验证内容**的
  只读幂等回显；无租约的 reconcile 恢复入口加独立可信身份/范围约束（不直接改共用函数的历史兼容语义）。
  回归：未领取/已释放/取消/租约过期/错 token 全拒绝 + 合法执行者 + 终态同内容重放通过 + 非可信 reconcile 拒绝。
- **R2-06**：`_verify_published_files`（443）+ `_target_matches`（publish:226）只核对自报 db3_sha256 与
  当前文件一致——空文件配空哈希照样 AVAILABLE/current=true（复现：正常产物改 0 字节 + sha 改空哈希，complete 200）。
  修复：实际打开校验非空 + Bag 可读 + 必要 topic/消息数与 manifest 一致 + 区间身份核对；
  源时间映射证据引用明确化（**注意：当前代码是逐帧 storage-header 完全恒定，无 1s 容差**——你回执里
  "超 1s 拒绝"的描述与实现不符，Q2 裁决要求以样本证明该限制适用性，先修正文档表述，fail-closed 维持）；
  缺失可信映射证据时阻断 AVAILABLE。回归：空文件/非 Bag 内容/无消息/错 topic/错区间/错 slice UID/缺失映射证据
  全部不得推进 AVAILABLE/current。

## 修复链 3：发布接线与幂等（R2-10 / R2-11）
- **R2-10**：子包 AVAILABLE 但 `relative_path` 仍是 06A 占位 `scene/<scene>/<parent>/<child>`，
  无 BagFile/BagTopic/产物索引（message_count/total_size=0）——`bag_access_info` 按占位拼路径，
  最终使用方找不到实际文件（复现）。修复：06B 接受受控发布结果时**幂等回填**真实 NAS 逻辑路径
  （`<车辆>/<场景>/<parent>_<child>`）、文件/topic 索引、大小/消息数、产物证据关联，继承父包车辆元数据；
  回填与 AVAILABLE 推进形成一致完成条件（不得先 AVAILABLE 后补索引）。回归：complete/reconcile 后
  实际获取路径存在且可打开指向同一文件、重放无重复索引、topic/车辆查询命中。
- **R2-11（MEDIUM）**：move 成功后重试原 specs 先 stat staging 再查 target → FileNotFoundError（复现）。
  修复：优先核验已存在目标（digest+完整身份一致则复用），真正需要 move 时才要求 staging；
  禁止为重试清掉已发布目标。回归：原 specs 重放/多片中途完成后重放/目标冲突/缺 staging/缺 target。

## 门禁与验证
- MySQL 真实结果必交（R2-03 换版在链 1 内）：独立 MySQL 8.4 容器实测 switch_current 首切/同目标重放/
  并发首切/旧版晚到/失败保旧（1093 消除，最终每个父包+场景至多一个 current）——可自测或交测试者补测，
  回执必须附真实结果或明确的测试者派单请求。
- 回归：`/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/R2-20261010-evidence/test_r2_repro.py`
  的 8 个复现断言**全部反转通过**（该文件在你的 worktree 内用路径引用跑；它不进仓库），+ 你原有 49 passed 不回归，+ 全量 SQLite，ruff 全绿。
- 交付：commit + receipts/TASK-06B/attempt-1-r2-rework.md（status REVIEW_PENDING，逐条 R2-xx 对应测试数字）
  + 群内通报格式；OCR/强模型复审不自跑。

## 附：B8a OCR（6e6bb73，弱模型，1h03m）新增项——合并进本次返修
B8a 对 06B app 主体 OCR 出 6 条，多数与 R2 同域（crash-window=R2-04、path traversal、timezone），
但**下列 1 条 high 是 R2 未覆盖的真新增**，一并修：
- **[high] 多场景 run 永远无法 complete（死锁）**：`finish_scene_run` 从 snapshot **全部**场景
  `summarize_scene_outcomes(run)` 定终态——2 场景的 run，complete 场景 A 时 B 未回报 → 汇总缺 B
  结果定 SCENE_FAILED 终态 + 清租约；B 稍后 complete 命中顶部 `run.status in SCENE_TERMINAL` 抛
  409，A 已记录的 SUCCESS 永远切不了 current（children 停 PENDING）。显式 API 允许建多场景 run、
  `_link_av_row`/`_find_av_row` 也按多场景处理，但 complete 路径没有。**修**：仅当所有预期场景都已
  回报 outcome 才触发 `finish_scene_run`（+switch），或创建时拒绝多场景（选前者，保留产品能力）；
  回归：2 场景 run 先 complete A（断言 run 仍非终态、A 暂不切 current）→ complete B（断言 run 终态
  + 两场景 current 正确收敛），及单场景不回归。
- 其余 4 条（path traversal security / timezone / crash-window 与 R2-04 同域 / 同文件系统校验只查
  specs[0]）：path traversal 与 timezone 若 R2-06/09 的身份+证据校验未顺带覆盖，一并修；
  crash-window 归 R2-04；同文件系统校验扩到全部 specs 切片（low，顺手）。OCR 建议文本仅供参考，
  以你对实现的理解落地。