# 派单：TASK-07A attempt-1 统一界面·可见性与检索（P1 提前，用户授权）

- status: DISPATCHED
- 派单时间：2026-10-12 09:45 +08:00
- 任务：TASK-07 第一批 07A（REQ-05 / AC-05 P1「三视图、旧入口、详情」；含 lineage API 缺口收口）
- 授权来源：**用户 2026-10-12 群内明确授权**（"测试环境网页端看不到场景线入口/流水线状态" → "进行2的开发"=TASK-07 统一界面整体提前，非 P0 扩项）
- owner：B（前端功能开发群，wt-04a，当前空闲；07A 以 app/web+templates 为主面，与 B 历史 06B/08/09/10 交付连续）
- base：main `453da0c`（= origin/main）
- 下游：07A 收口后派 07B（人工纠错/下架，REQ-04 P1）→ 07C（预览）。本单不含纠错/下架/预览。

## 一、背景（用户实测痛点，协调者 2026-10-12 浏览器+代码核实）
1. `/pipelines` 页状态筛选只有 Phase0/自建/NVIDIA 状态，**SCENE_SLICE_QUEUE/SCENE_RUNNING/SCENE_DONE 不在选项里**；场景 run 即使出现在列表也无专属队列语义（`app/templates/pipelines.html:21`）。
2. `/bags` 页**无切片视图**：子切片（bag_role=SCENE_SLICE）与普通包混排，无"当前可用切片"默认视图、无场景/父包筛选。
3. **父子追溯断链**：`GET /api/v1/bags/{uid}/lineage` 路由缺失（TASK-10 收口遗留事实 #2；T11 real E2E 实测 404）。`/bags/{uid}` 详情 200 但无 lineage/父包跳转。
4. 原始包详情不展示"所选场景状态及切片数"（PRD §6.1：原始包展示本次所选场景的状态及切片数，不固定五列）。

## 二、交付内容（最小范围，全部 P1 既定 AC，零新需求）
### 2.1 lineage API（先行，UI 依赖）
- `GET /api/v1/bags/{bag_uid}/lineage`：
  - 子切片视角：parent_bag_uid + parent 摘要、slice_key、scene_code、run_id、analysis_version（生成版本）、created_at；
  - 原始包视角：children 列表（每个 child：bag_uid、scene_code、slice_key、duration_ns、availability、当前版本标记 current bool）；
  - 非场景包：返回 `{lineage: null, children: []}`（200，不 404，供 UI 统一处理）；
  - 数据源=既有 `bag_derivation` + `scene_analysis_version`（current 指针）+ `bag_record`，**不新增表/迁移**。
### 2.2 /pipelines 页场景可见
- 状态筛选加 `SCENE_SLICE_QUEUE/SCENE_RUNNING/SCENE_DONE`；
- 列表队列列显示 `SCENE_SLICE_QUEUE`，数据类型列对场景 run 显示"场景切片"（pipeline_type 判）；
- 场景 run 操作列：FAILED/SCENE 相关状态给"重试"入口（复用既有 /retry，若状态机不允许重试 SCENE 状态则显示"→"详情跳转即可，**不得弱化既有状态机守卫**）。
### 2.3 /bags 三视图（PRD §6.1）
- 默认视图=**当前可用切片**（availability=AVAILABLE 且 current 版本；含场景名、时长、模型标记 label、父包链接、获取操作）；
- 切换视图：原始包（本次所选场景状态+切片数列）、全部/历史（含非 current 版本，标注"历史"）；
- 通用筛选加：场景（scene_code）、角色（bag_role：原始/切片/自建）、用途（scene_slice）；既有车辆/时间/关键词筛选不回归；
- **旧入口兼容**：既有自建/NVIDIA 页面路径与书签行为不变（AC-08 不回归）。
### 2.4 详情页双向跳转
- 切片详情：父包卡片（名称/点击跳父包）、生成版本（analysis_version + config_hash 短显）、获取操作（复用既有 access.txt/NAS/SMB/rsync 展示口径）；
- 原始包详情：该包 scene run 状态区（场景→状态→切片数，点切片跳转）；
- 双向=父→子列表→子详情→父卡片→父详情。
### 2.5 回归
- 既有 `test_web*.py`/`test_bags*` 全绿；新增 lineage API + 三视图 + pipelines 场景状态定向测试；
- ruff 绿；本地栈页面实测证据（截图或 innerText 断言）：/pipelines 可见 SCENE_DONE run、/bags 切片视图可见 T11 子包或 fixture 子包、lineage 200。

## 三、边界与禁止
- 不新增 alembic 迁移（lineage 只用既有表）；不动场景状态机/幂等/发布逻辑（TASK-03~06B 责任面）；
- 不做纠错/下架/预览（07B/07C 范围）；不做 P3 统计（TASK-14）；
- 不改生产 compose；测试环境页面实测走本地 real 栈（453da0c 已 up，VLM/scene-publish 绑定已还原，勿再加临时挂载——若需发布产物展示用 DB 口径不读文件系统）；
- 子切片不自动再入场景/自建流程的展示语义保持（PRD §5：显式提交才处理，页面只呈现不改行为）。

## 四、验收口径（TESTER 独立验证）
- lineage API：真实子切片（DB 现存或 fixture 造）双向查询 200 + 字段完整 + 非场景包 200 null；
- /pipelines：造 SCENE_DONE run 后页面可见且筛选生效；
- /bags：三视图切换、场景/角色筛选、父↔子跳转闭环、旧入口书签不回归；
- 既有 Web 测试套件 0 红。

## 五、交付物
- commit（base 453da0c 之上，单 commit 或最小集）+ 回执 `receipts/TASK-07A/attempt-1.md`（REVIEW_PENDING）+ 页面实测证据 `reports/TASK-07A/attempt-1.md`。
- 交付后：协调者机械核验 → 串行 OCR（app 面）→ 合入 → TESTER 页面+API 独立验证 → 07A DONE → 派 07B。