# TASK-16R attempt-1 处置回执（盘点 + 裁决，不开发代码）

生成：2026-10-14T11:42:05+08:00，owner 协调者。方法=只读核 git 祖先链/commit 时间戳/现有 review 证据；不写业务代码、不开发。本回执是 TASK-16R 交付物，非第二任务表；动态状态仍以 TODO §8 为准。

父 16 收口前本单必须给出两类结论：① 15 条 UI OCR 未修项逐条对应原 AC 的归属与复验门禁；② 水雾发布审查债的有效覆盖映射与真实未覆盖范围。两类都不得"沉默留债"，也不得以"全部 OCR 已通过"概括。

---

## 1. UI OCR 15 条逐项处置

来源=16C 暂停交付 `5c80857`（已按字节一致搬运到 seed `bd0db1d`）在 7 个逐文件批（c01–c07）上的 15 条 findings：c01 pipelines.py 4 条、c02 bag_search_service.py 2 条、c03 scene_result_query.py 4 条、c05 pipeline_detail.html 5 条、c04/c06/c07 各 0 条。seed 含全部已知缺陷（未接受），**本轮全部由 A/C 叶派单（11:25）携带修复**，本表只做归属/裁决/复验门禁，不重派。

| 来源ID | 文件 | 级 | 初裁 | 16R 处置结论 | owner | 关闭条件（复验门禁） |
|---|---|---|---|---|---|---|
| C1 | pipelines.py | low | CONFIRMED 维护：不可达 `elif`（NO_MATCH） | 删除死分支，保持实际 outcome 映射 | C / 16C-C | 增量 OCR 复扫 + NO_MATCH/NOT_APPLICABLE 浏览器/单测 |
| C2 | pipelines.py | low | CONFIRMED 维护：`_scene_environment_paths(run)` 未用 run | 删无效参数或实际用于有证据路径读取，不伪造历史路径 | C / 16C-C | 增量 OCR 复扫 + 该函数单测 |
| C3 | pipelines.py | low | CONFIRMED 部分误报：`scene_terminal` 死 context | 与 16C-c05-03 **共用一处终态来源**；INPUT_INVALID 属 PHASE0，原 OCR 场景归类驳回，不扩状态机 | C / 16C-C | **同一修复 SHA** 关闭 C3+c05-03；全真实场景终态停止刷新回归 |
| C4 | pipelines.py | low | **REJECTED**（未开始→已终止建议，冲突 DESIGN §7.3.3） | **维持驳回**：真实未启动步骤保持"未开始" | C / 16C-C | 不派错误修复；候选回归确认即可，有据记录 |
| C5 | bag_search_service.py | medium | CONFIRMED CORRECTION：双用途展示双标却单值 CASE | 共享多成员谓词，两类筛选都命中且 UID 唯一；Web/API/交集/分页测试 | A / 16C-A | 增量 OCR 复扫 + TESTER 双用途筛选复测（谓词面） |
| C6 | bag_search_service.py | medium | CONFIRMED 维护：`data_kind_labels_for` 死代码且分叉 | 归一到共享分类真相或删死 helper，不复制第二分类规则 | A / 16C-A | 增量 OCR 复扫 + 四类/双用途标签一致性 |
| C7 | scene_result_query.py | medium | VERIFICATION_GAP→复现后最小修：日期原始串直入 DateTime（500）与截止日偏差 | 隔离严格 MySQL 复现，非法日期 422；日期全天边界/时区 aware-naive 与 Web 一致含端点 | A / 16C-A | 严格 MySQL 复现 PASS（SQLite 绿不宣 MySQL 过）+ TESTER 面 |
| 16C-c03-02 | scene_result_query.py | low | 待核实：cursor 上下文漏新增筛选字段 | owner 交付前先复现/核代码依据再确认或驳回，不得直接改业务 | A / 16C-A | 覆盖 dataset_type/started_from/to 换条件不漏/不重 + 依据记录 |
| 16C-c03-03 | scene_result_query.py | low | 待核实：旧 cursor scene_code None 与空串 | 同上（先复现/核依据） | A / 16C-A | 旧合法 cursor 归一验证 + 签名/筛选不匹配不放行 |
| 16C-c03-04 | scene_result_query.py | low | 待核实：Python 分类与 SQL 子包条件分叉 | 同上（先复现/核依据） | A / 16C-A | SCENE_SLICE 角色或有效 derivation 均识别子包（含无血缘历史切片） |
| C8 | pipeline_detail.html | medium | CONFIRMED CORRECTION：CANCELLED 无 retry-form→尾脚本 null.querySelector | 场景类型/DOM 存在性正确 guard，不露自建强制重试 | C / 16C-C | **真实浏览器**取消页无 JS 异常（BLOCKED_BROWSER 不可用 HTTP200 替代）+ TESTER |
| C9 | pipeline_detail.html | medium | VERIFICATION_GAP：model_endpoint/model_identity 历史写入证据不足 | 按当前已部署 snapshot/refs 核实际来源；有证据显示、无记录写"未登记"，不加 schema、不冒充历史 | C / 16C-C | 来源证据记录 + 不扩 schema |
| 16C-c05-03 | pipeline_detail.html | low | CONFIRMED（与 C3 共修）：模板终态硬编码 + 死变量重复 | **与 C3 同一修复 SHA**，保留两个来源 | C / 16C-C | 同 C3；全真实场景终态停止刷新回归 |
| 16C-c05-04 | pipeline_detail.html | low | CONFIRMED DOM：lineage `li` 缺 `ul/ol` 容器 | 最小 HTML 修正，父子跳转与可访问结构浏览器取证 | C / 16C-C | 真实浏览器取证 + TESTER |
| 16C-c05-05 | pipeline_detail.html | low | CONFIRMED 类型隔离：NVIDIA 契约块仅看 `bag.dataset_type` | 先按 pipeline_type 分流，NVIDIA 来源场景 run 不显旧契约，原 NVIDIA run 正常 | C / 16C-C | 类型×终态矩阵 + TESTER |

**裁决汇总**：CONFIRMED CORRECTION 4（C5、C8 + C3/C4 家族）必须对应原 AC 回原 owner 最小修；待核实 5（C7 及 c03-02/03/04、C9）owner 交付前先复现/核代码依据再确认或驳回，不得照 OCR 建议直接改业务；C4 维持 REJECTED 有据不阻断；C3/c05-03 一处实现关两条来源不漏账不重复。**所有 15 条关闭均需经协调者唯一 ocr_runtime 串行增量 OCR + TESTER 逐面复验，不用一份 TESTER 总 PASS 覆盖全部发现。** 文件 owner 独占边界见 V04-UI-RESUME-20261014.md，本轮已入 A/B/C 派单，协调者不代开发。

---

## 2. 水雾发布审查债——有效覆盖映射（git 实测）

### 2.1 生产链 first-parent `4b9f30a..3c9c496`（本单只读核 rev-parse + merge-base）

```
3c9c496  Write scene SQLite slices locally before verified NAS staging   [生产业务, CIFS SQLite 锁真实修复]
8e538bb  Expose scene publication evidence read-only to the backend      [catalog-scene.yaml +5]
ad60e41  Retry uncertain terminal replies and honor failure stop signals [R4-02 修复, proxy +24]
fe17e8a  Stage scene slices on the publication filesystem                [orchestrator +9]
29af08a  fix: renew leases during finalization and preserve successful intent  [强审 R4 target]
6e91c3b  fix: inherit slice metadata and preserve independent NAS paths
6ddcbcb  fix: normalize default scene parameters before checking frozen hashes [直接替代 direct-r3 的 15e4ef9]
0e4d0ed  TASK-12S-C attempt-1: 水雾正式接线
(中间 merge b8437ad/8500de0/e152465/40ab818/0208a73 = 16B 尝试链)
```

关键祖先实测：`15e4ef9`（direct-r3 head）**非** `3c9c496` 祖先；`6ddcbcb`→`ad60e41`→`8e538bb`→`3c9c496` 逐级祖先；`29af08a`（强审 R4 target）是 `3c9c496` 祖先；`main 63bfcf8` 是 `3c9c496` 之后的纯文档 commit。

### 2.2 逐项债处置

| 原记录 | 已知事实 | 16R 覆盖结论 |
|---|---|---|
| TASK-16B/direct-r3 (`e152465..15e4ef9`) | NOT_EVALUATED / rc=1 / HARD_DEADLINE（弱 OCR 超时，无完整 manifest，零 findings） | **被后续替代**：15e4ef9 非生产祖先；其"normalize default scene parameters"修复在生产链以 `6ddcbcb` 重新落地并经强审 R4 读全文件覆盖 → 不重跑旧 prepared/timeout run |
| final-r4 / r5 / r6 | 均 PREPARED 零模型消耗（r6 spec = `6ddcbcb..8e538bb`） | **被后续替代**：r4-correction-verdict 已记 `29af08a` 强审 R4 → `ad60e41` 最小修（17 项修前 16FAIL/1PASS→修后全 PASS，相关 89 PASS），`fe17e8a` 跨 FS 发布 3 项/编排 15 PASS 无剩余强审缺口 NOT_REQUIRED → 不重启全部 prepared |
| release-8e538bb-acceptance | 用户"ocr 卡点可不等待"，仅当次生产固定候选例外 | **保留已接受上线事实**（非永久豁免）：8e538bb = catalog-scene.yaml +5 只读证据暴露；覆盖靠强审 R4 读全文件 + 真实 e2e |
| r4-correction-verdict | R4-01/02 已修 `ad60e41`，17 红绿 + 89 关联 PASS | **已关闭不重开**，核当前未回退（ad60e41 在 3c9c496 祖先链内，未回退） |
| production-nas-write-correction | 3c9c496 CIFS SQLite 锁修复，19 测试 + 真实探针 + 两次 reconcile 幂等 + SCENE_DONE | **真实 e2e 覆盖**，保留生产接受；当次 OCR 例外不撤销 |

### 2.3 真实未覆盖当前代码范围（唯一弱 OCR 全扫缺口）

**`fe17e8a..3c9c496`** = 唯一从未被弱 OCR 全扫的生产增量：`scripts/scene_host_orchestrator.py`(+70/9)、`scripts/scene_host_proxy.py`(+24)、`deploy/scene/catalog-scene.yaml`(+5)，~108 行代码插入（tests 除外）。

- **已有覆盖**：强审 R4 覆盖了高风险的恢复/收尾面（29af08a）；真实 e2e 覆盖了单包正向全链行为（3c9c496 SCENE_DONE / 19 测试 / CIFS 探针 / reconcile 两次幂等）。
- **缺口性质**：**弱 OCR 全扫未执行**——不是强审未覆盖，也不是行为未验证，仅是代码质量全扫缺口。
- **处置（不沉默留债、不伪称 PASS、不自动重启旧 prepared）**：登记为**低优先补审候选**。待 UI 叶（A/C）增量 OCR 完成且 `ocr.lock` 空窗后，由协调者按唯一入口 `ocr_runtime.py prepare → start → status` 补：先冻结 base `fe17e8a` / head `3c9c496` / 入选 2 py / 排除 tests+deploy yaml + 背景约束，不复制旧 runner、不重启 direct-r3/r4/r5/r6。
- **不阻塞父 16 收口、不撤销 3c9c496 生产接受**；proxy 文件较大且有 16B 弱 OCR 超时前科（3× rc=1），故不放在本轮 cron 回合自动起长扫，列为 UI 叶 OCR 后的显式补审动作。

---

## 3. 原接受引用（不撤销，仅查漏）

- **12S-B/S9b 算法弱 OCR 全覆盖 0 findings 已接受**（f76e2a9 已合入 3c9c496 祖先链，真实 S9b 1184→44 源时间/血缘/尾 20 不发布 PASS）。
- **16A** OCR 闭环（v2 14/14 + 增量 3/3 零 CORRECTION）+ TESTER post-merge 独立验证 09:32 PASS（真 MySQL 8.4 全链迁移三趟 RC=0），main `6fb42c4`。
- **07B** OCR 全批收口无 CORRECTION 级 + 强审 R2 四条 CORRECTION 已修(R3)/R4 增量复审 R4-01 裁决非违例 + TESTER post-r PASS 4/4，main `4b9f30a`。
- **16B** b1/b3 OCR findings 已裁（H1/M1/M2 orchestrator + fake_vlm 2 项），恢复缺陷面经强审 R4→ad60e41 关闭。
- 上述只查漏项，**不重开已接受工程闭环**。

---

## 4. 最终覆盖门禁（父 16 收口前必须满足）

1. **15 条 UI findings 全部对应原 AC 回原 owner 修复**（A：C5/C6/C7/c03-02/03/04；C：C1/C2/C3/C4/C8/C9/c05-03/04/05），且经协调者唯一 `ocr_runtime` 串行增量 OCR + TESTER 逐面复验关闭；C4 维持驳回有据、待核实 5 条有复现/代码依据。
2. **水雾债五类分列、不概括**：direct-r3/final-r4/r5/r6 = 后续替代；release-8e538bb/3c9c496 = 真实 e2e 覆盖 + 保留接受；`fe17e8a..3c9c496` = **未覆盖，低优先补审**（不伪称 OCR PASS）。
3. 真实代码缺陷回原模块 owner（单写冲突先检查点交接），验证缺口交 TESTER，不借审查扩充需求。
4. 生产 3c9c496 接受保留，本轮 UI 恢复不是生产切换授权；强审 grant `6b2d83fb…` 已 REVOKED，不自动付费调用。

---

## 5. 下一步

- 等 A/B/C 安全点 ACK 新叶单 → 各叶从 seed `bd0db1d` 建专属树开发 → 交付冻结 → 协调者机械核验 → **串行增量 OCR（唯一入口）** → TESTER 逐面复验 → 接受叶 → 三叶齐 → 生成含 seed 的固定集成候选 → TESTER 16D 联合验收 → 父 16C 聚合接受。
- TESTER 16D 环境/复现已知缺陷准备**并行推进，不等开发**。
- `fe17e8a..3c9c496` 弱 OCR 补审：UI 叶 OCR 后 `ocr.lock` 空窗时按唯一入口 prepare/start（**低优先，不阻塞收口**）。

本回执不构成任何生产切换、迁移、算法或付费审查授权。