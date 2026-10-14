# 派单：TASK-07B attempt-1 统一界面·人工纠错/下架（P1 提前，用户授权）

- status: ACKED
- 派单时间：2026-10-12 14:50 +08:00
- 任务：TASK-07 第二批 07B（REQ-04 / AC-04 P1「人工纠错/下架可审计且不改文件或丢弃模型原结果」）
- 授权来源：**用户 2026-10-12 群内明确授权**（"继续场景线开发，等待你裁决了"=07A 裁决后接续 07B；07 整体提前授权同 07A 口径）
- owner：B（前端功能开发群，wt-04a 系；07A 刚收口，文件面连续）
- base：main `502bf8e`（= origin/main；其上 caf385b=07A 合入态，TESTER 32/32 PASS 已裁决 DONE）
- 前置：07A DONE（三视图/lineage/双向跳转已在 main，详情页纠错入口挂 07A 的场景结果面板）
- 下游：07B 收口后派 07C（预览，REQ-05 P1）。本单不含预览。

## 一、既定设计口径（DESIGN §7.2，不得偏离）
- `PATCH /api/v1/bags/{uid}/scene-labels`：人工修正场景标签。带 **row_version + 原因 + 幂等键 + 可验证操作者证据**；**保留原始模型结果**（纠错不覆盖/不丢弃，模型证据可追溯——AC-04"采集意图不充当模型标签，证据可追溯"）。
- `POST /api/v1/bags/{uid}/withdraw`：人工下架。带同四要素；**不删除任何文件**（切片文件、发布产物、原始模型结果全保留）；下架后切片退出当前可用检索（availability 语义按 DESIGN §7.1：AVAILABLE=校验登记通过，默认查询匹配当前版本；下架单独审计）；**普通重试不能重新上架**——重新上架必须走新分析/新版本（独立新结果按新版本管理，保留原修订历史）。
- **不新增匿名可用写入口**：两个接口在本地测试栈可调用（供验证），生产启用随 TASK-11 门禁，本单不改生产 compose。
- 写身份：复用仓库既有操作者/身份口径（查现有 web 写接口如何带身份，如 ingest submission 的操作者字段；若无统一机制则用请求头操作者标识 + 审计留痕，**不发明账号体系**）。

## 二、交付内容（最小范围）
### 2.1 数据面（既有表优先，迁移必须最小且可回滚）
- 修订/下架审计记录：优先用既有 `bag_scene_label_evidence` + 新审计表 `scene_manual_revision`（bag_uid、scene_code、action=REVISIT/WITHDRAW、operator、reason、row_version、idempotency_key、original_label_ref、created_at）；若评估可用 pipeline_event 承载则免新表——**以最小一致为准，迁移文件含 downgrade**。
- 下架状态承载：不新增 bag_record.status 枚举值（会冲击既有状态机）；用审计表 + 切片 availability 语义（withdraw 后该 current 切片退出默认检索）。**不得改场景状态机/幂等/发布逻辑（03~06B 责任面）。**
### 2.2 API
- `PATCH /api/v1/bags/{uid}/scene-labels`：请求体 {scene_code, corrected_label, reason, row_version, idempotency_key}；row_version 冲突 409；幂等重放 200 同结果；非切片包 404/422 明确语义；审计落库。
- `POST /api/v1/bags/{uid}/withdraw`：请求体 {scene_code, reason, row_version, idempotency_key}；同四要素语义；重复 withdraw 幂等；withdraw 后 /bags 默认视图（当前可用切片）不再出现该切片、view=all 仍可见且标注"已下架"；GET 详情体现下架状态。
- 两个接口均只接受切片 uid（bag_role=SCENE_SLICE）；对 ORIGINAL 父包操作返回 422 明确拒绝（父包下架不在本 P1 范围）。
### 2.3 页面（07A 面之上增量）
- 切片详情页：人工纠错入口（修正标签+原因表单）与下架入口（原因表单），操作后展示审计记录（操作者/时间/原因/原值→新值）；
- 已下架切片：三视图标注、详情审计区；
- 旧入口/既有断言不回归。
### 2.4 测试
- 定向：row_version 冲突、幂等重放、保留模型原结果（withdraw/revisit 前后 scene_segment/evidence 原始值不变）、下架退出默认检索但 all 可见、审计可查、父包 422；
- 既有全量 0 红（基线 849 passed，3 failed devflow 环境性不算）；ruff 绿；页面实测证据（自包含 uvicorn 口径同 07A，或无活动 run 窗口用共享 real 栈）。

## 三、边界与禁止
- 不做预览（07C）；不动 03~06B 状态机/幂等/发布；不改生产 compose；
- 迁移若必要：真 MySQL 8.4 隔离库 upgrade+downgrade 往返实测（T03/T04 教训：SQLite 绿不算）；
- 不删除任何数据文件；测试夹具自造自清。

## 四、验收口径（TESTER 独立验证）
- API 四要素（row_version/原因/幂等/操作者证据）逐项实测；
- AC-04 核心：纠错/下架后**模型原结果仍在库可查**（原始证据未被覆盖/删除）；
- 下架检索语义：默认视图退出、all 视图可见且标注；
- 迁移 upgrade/downgrade 往返（如有迁移）；既有套件 0 红。

## 五、交付物
- commit（base 502bf8e 之上）+ 回执 `receipts/TASK-07B/attempt-1.md`（REVIEW_PENDING）+ 报告 `reports/TASK-07B/attempt-1.md`（含页面实测证据）。
- 交付后：协调者机械核验 → 串行 OCR（app 面拆批）→ 强审查判定（写接口面大概率 REVIEW_NOW，24h 授权在案，60min≤5 次）→ 合入 → TESTER 独立验证 → 07B DONE → 派 07C。