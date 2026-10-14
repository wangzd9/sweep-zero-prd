# 协调者裁决：SR-07B-R4-20261013 强审 R4-01（契约负责人，范围澄清回冻结基线）

- 裁决时间：2026-10-13 07:4x +08:00（coord poll 14ae4556629a，r133，claim owner `cron-coord-poll-14ae4556629a-20261013-073053-r133-r4-delivery`）
- 裁决对象：强审查 `SR-07B-R4-20261013`（call `a8febf1a19444ef9bd456c508c94b397`，SUCCEEDED，结论 REWORK_REQUIRED，唯一问题 R4-01 medium CORRECTION）
- 裁决人：协调者（契约负责人，PROTOCOL v2「协调者单写…decision」；审查者自留口子「若全 no-op 原意仅指审计表依赖块，须先由契约负责人明确修正表述」）

## 一、事实（协调者独立探针，非复述强审）

探针 `~/.hermes/cache/scratch/coord_r133_r401_probe2.py`（SQLite 内存，最小原始 schema：evidence 表含 corrected_label 列+1 行 'flat'，审计表故意不建），三形态实测：

| 形态 | 「审计表缺失+evidence列存在」态 downgrade | evidence 列 | corrected_label 值 |
|---|---|---|---|
| R4 `62620a3` | **NO exception** | 被 drop | None（丢失） |
| R3 `4baf79f` | NoSuchTableError | 被 drop（事务回滚，实际 schema 不变） | flat |
| 原始 `68b5188` | NoSuchTableError | **保留** | flat |

upgrade 顺序独立核实（`git show <rev>:…/20261012_01_scene_manual.py` L54-92）：`op.create_table(审计表)`（L57，`TABLE not in` gate 内）**先于** `op.add_column(evidence, corrected_label)`（L90，`has_table` gate 内）。→「审计表缺失 但 evidence corrected_label 列已加」态**无法由正常 partial-upgrade 产生**（upgrade 中断在审计表建表后、evidence 列加之前=审计表已存在；中断在 evidence 列加前=evidence 列不存在）。该态为手工构造的合成 schema。

R4-2 docstring（`62620a3` 迁移 L20-30）已明确文档化：「downgrade 单独 drop 该列再重新 upgrade 时…原 MANUAL 行已持久的 corrected_label 值被静默清除且不可恢复…处置=操作者对受影响 MANUAL 记录重新执行纠错补记」= 该数据丢失语义为迁移自身**既定接受**，非 R4 新引入。

## 二、裁决

**R4-01 非冻结 AC 违例，不返修。**

1. **冻结的原始既定 AC**（R4 派单 `inbox/2号/TASK-07B/attempt-4-r4-dispatch.md` §三「SQLite 内存探针=表缺失态 downgrade 不抛异常（守卫生效断言）」）在 R4 交付上**已满足**——探针实测 `exception=NO`；R3/原始态同态 `NoSuchTableError` 即 r3-1 medium（R4-1）所修复对象，R4 修复有效。
2. 强审 R4-01 的阻塞依据是**协调者强审包 `SR-07B-R4-20261013-pack.md` §2 不变量 3 的「全 no-op」措辞**——该措辞为协调者生成 pack 时的过度精确表述，**不是** R4 派单/审查包 `SR-07B-A2R2-20261013-pack.md` §2 的冻结 AC（后者 6 条不变量无一要求 downgrade 在合成态零 schema 变更）。
3. 契约负责人澄清（按审查者自留口子）：**不变量 3 的范围=「审计表依赖块在表缺失态不抛异常」**（即 R4-1 的修复对象），**不**含「evidence 列 drop 在审计表缺失态不执行」。pack §2 不变量 3 已回改（见本裁决附注的实际改写）。
4. R4-01 所述「downgrade drop evidence 列」在澄清后**不构成缺陷**：
   - 该合成态无法由正常迁移流程产生（upgrade 顺序核实）；
   - evidence corrected_label 列由本迁移 upgrade 加，downgrade 逆其 drop 是**对称逆操作**（同对象 add↔drop），语义正确；
   - R4-2 docstring 已文档化该值丢失=既定接受语义；
   - 审查者建议的「审计表缺失时 early return（任何 drop 前）」会**留下孤立 evidence corrected_label 列**（upgrade 加了、downgrade 没删），造成与 upgrade 不对称的 schema 残留=**行为回归**，故不采纳。
5. R4-1 越界申报（守卫提升覆盖整个表依赖块，非派单 §一「仅移 drop_column」字面）：**核实成立且必要**——协调者独立探针（`coord_r133_probe.py`）已证原始 `68b5188` 与 R3 `4baf79f` 表缺失态均在 `_indexes_of`→`get_indexes` 抛 NoSuchTableError，仅移 drop_column 无法满足 §三探针；守卫提升是满足既定 AC 的最小正确形态，强审 R4 其余裁决（「越界申报成立，但没有发现它改变正常态顺序」）同向。

## 三、独立 VERIFICATION_GAP 维持（非 R4-01，属 07B 既定收口口径）

- **07B-SR-05**（R2 强审 `50c665e4…` 出的高 VERIFICATION_GAP，真 MySQL 双连接同版本无关联 200/409 并发 409 未验证）**不因本轮 R4 收口而消除**——它验证的是 service 守卫并发语义（SR-02 修复面），与 R4 迁移面独立。
- 维持既定链路：07B 合入门禁剩 TESTER `07B-post-r` 独立验证（SR-05 真 MySQL 双连接口径 + R4 迁移面正常态/表缺失态双库探针 + 定向回归），target 固定 `62620a3`。TESTER PASS 后 07B 整链合入（先于 16A rebase 双头）→ 07B DONE。
- **07B 当前不合入**（SR-05 独立验证为合入门禁一部分，未解除）。

## 四、收口

- R4 强审面：R4-01 澄清后**问题关闭**（非原 AC 违例），无新增 CORRECTION/VERIFICATION_GAP（R4-01 已归入本裁决）。强审 `SR-07B-R4-20261013` 收口，冻结原 AC 满足（迁移面：升级零改动/正常态逐语句一致/表缺失态不抛异常/docstring 同型先例/单头不变，均探针+OCR 独立核）。
- 强审额度：call `a8febf1a…` 计 1 次（滚动 60min 1/5，本授权累计 2 次），授权期限 2026-10-13 11:33:12 内。
- 下一步：TESTER `07B-post-r` 派单（target `62620a3`）→ 独立验证 PASS → 07B 整链合入（--no-ff，先于 16A rebase 双头）→ 07B DONE → 派 07C/16C。16A（交付冻结 `3aee4d1`）/16B（NEEDS_REVIEW 冻结）链路不受本轮影响。

（附注：pack §2 不变量 3 实际改写见 `SR-07B-R4-20261013-pack.md` §2 第 3 条，本 decision 与改写内容一致。）