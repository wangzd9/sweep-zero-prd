# 报告：TASK-07B attempt-1 统一界面·人工纠错/下架

- 角色：执行者 B（前端功能开发群）
- 交付时间：2026-10-12 17:15 +08:00
- 回执：`receipts/TASK-07B/attempt-1.md`
- commit：`5fa0942`（主体）+ `f4bfcf2`（契约修正），分支 `scene/task-07b-manual-revision-withdraw`

## 一、实现
REQ-04 / AC-04 P1「人工纠错/下架可审计且不改文件、不丢弃模型原结果」，DESIGN §7.2 口径落地：
- 数据面新审计表 `scene_manual_revision`（操作者/原因/操作前状态/幂等键/原值引用），迁移含 downgrade + 逐对象 gate。
- `PATCH /api/v1/bags/{uid}/scene-labels` 人工修正场景标签：**只更新 `bag_scene` 有效投影 + 写 MANUAL 证据行，MODEL 证据行与 `scene_segment` 判定绝不覆盖**。
- `POST /api/v1/bags/{uid}/withdraw` 人工下架：**不删文件**，切片 availability 转 WITHDRAWN 退出默认可用检索，all 视图可见并标注。
- 四要素：row_version（409）/ reason（422）/ 幂等键（重放 200 同结果，同 key 异参 409）/ 操作者证据（X-Operator，不一致 409、缺失 422）。
- 页面：切片详情页人工纠错/下架双表单 + 审计区（操作者/时间/原因/原值）；列表已下架标注。

## 二、交付内自查发现并修正的契约问题
`corrected_label` 合法域初版误硬编码 `{slope, flat, construction, congestion, night, rain, other}`——后 5 个是**模型不产出**的概念标签，人工纠正常见合法值会被 422 挡。修正为引用 `app/scene/slope/segment.py` 权威常量 `{LABEL_SLOPE, LABEL_FLAT, LABEL_UNKNOWN}`（TASK-04B 段判定域），补 `unknown` 合法值断言。**此为开发自查，未经协调者/OCR/TESTER 复核。**

## 三、验证证据（契约修正后）
- 定向 + 07A 回归 **10 passed**
- 全量 **852 passed, 4 failed, 10 skipped**；4 failed 在 base `502bf8e`（stash 复现）同样失败 → 环境性（devflow 外部沙箱×3、web 性能计时×1），**非本侧回归**
- ruff（11 交付文件）**All checks passed**；全仓 21 error 均为既有 alembic 老文件
- alembic 单头 `20261012_01_scene_manual`
- **真 MySQL 8.4 隔离库迁移 upgrade/downgrade 往返** + 边界宽度 INSERT 200 / 超宽 INSERT 1406 真实生效（T03/T04 教训：SQLite 绿不算）
- **页面实测 26/26**（自包含 uvicorn + 临时 SQLite，不触共享 real 栈/容器/代理/MySQL）

证据：`scratch/t07b/`（07b_mysql_roundtrip.py/.out、07b_page_smoke.py/.out、pytest_targeted.txt、ruff.txt、alembic_heads.txt）

## 四、边界遵守
- 未做预览（07C）；未动 03~06B 状态机/幂等/发布；未改生产 compose；未删任何数据文件；测试夹具自造自清。
- 不运行 OCR/强审查、不代推 origin、不合入（留协调者合入面）。

## 五、状态与下一步
- 交付冻结 commit `f4bfcf2`，**REVIEW_PENDING**（不代表通过）。
- 下一步：协调者机械核验 → 串行 OCR（app 面拆批）→ 强审查判定（写接口面大概率 REVIEW_NOW，24h 授权在案）→ 合入 → **TESTER 独立验证**（开发自测不替代）→ 07B DONE → 派 07C。
- 空闲：本侧只读巡检 + 事件接续，不占第二开发槽、不扩需求。