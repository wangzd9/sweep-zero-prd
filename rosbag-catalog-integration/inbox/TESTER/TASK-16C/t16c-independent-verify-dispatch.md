# TESTER 派单：TASK-16C 独立验证（2026-10-13 10:2x，协调者 r142）

- **task/attempt**：TASK-16C / t16c-independent-verify（attempt-1 交付冻结后首验）
- **被测快照（固定，勿 rebase/追头）**：worktree `wt-04a-t16c` 分支 `b/task-16c-scene-ui-minimal`，head **`5c80857`**（协调者 rebase 到当前 main `6fb42c4` 后的接线 head；diff 与 B 原始交付 `4b9f30a..ad37ae1` 逐字节一致，协调者已独立复核）。**未合入 main**——以该 worktree 直接起服务验证，不得切 main。
- **交付回执**：`receipts/TASK-16C/attempt-1.md`（自测：15 新用例全绿 / 全仓 876 passed 4 failed 均 base 既有 / ruff 绿）。
- **范围（对应 DESIGN §8.4 自测/浏览器清单，逐项取证）**：
  1. **三类原始行**：含 NVIDIA 输入记录 NOT_APPLICABLE 角色的原始包在 originals 视图可见且正确标「英伟达原始」（data_kind=nvidia_original）；空 Topic/未知历史行不猜类型。
  2. **切片视图**：当前可用切片/历史/下架（withdraw 退出默认检索、all 可见）与 07B 语义一致。
  3. **双用途原包**：行级多标签 badge 两标并置；筛选走单值 CASE（scene_original 优先）。
  4. **data_kind 四类筛选 × 视图/来源组合**：不相容组合（如 self_built+nvidia_original）→ 200 `items=[]` 非 500 非静默丢条件。
  5. **`GET /api/v1/bags` 集合路由**：view=slices/originals/all、data_kind/dataset_type/purpose/vehicle_id/时间边界过滤、cursor 翻页（limit clamp 50..200 超限收敛、cursor 不一致 422、历史 cursor 兼容）、路由顺序先于 `/api/v1/bags/{bag_uid}`。
  6. **场景八步详情**：SUCCESS run 八步全真实完成；部分完成不伪标（未开始=未开始）；NO_MATCH→区间生成及之后「已跳过（无需）」且运行级展示 NO_MATCH 非 SUCCESS；FAILED→真实错误文本原样透出；**终态页无 10s 自动刷新**，非场景页面刷新行为不变。
  7. **场景运行环境区**：模型端点/处理机输入/场景 NAS 路径展示，**无 A100 面**；血缘降级（源 bag 行缺失不 500）。
  8. **旧界面兼容回归**：bags 列表页原有筛选/分页不回归；`dataset_type` 旧书签可用；pipeline 详情非场景面板（A100 环境/文件日志）scene 不渲染。
  9. **回归**：SQLite 全仓跑一遍，确认 4 个 base 既有 failed（test_devflow×3 + test_web 顺序污染族）无新增失败；如出现新 failed 二分归属。
- **MySQL 面口径**：本单无 DDL/迁移变更，仅 SELECT 谓词（回执已申报）；**不要求真 MySQL 独立验证**，SQLite 库取证即可，回执如实标注。
- **环境**：临时 SQLite 库（conftest DATABASE_URL 口径），DEMO_DATA=1；被测 worktree 只读不改动；**不得触碰 16B worktree `wt-03b-t16b` 与 `inbox/ocr.lock` 在途 OCR**。
- **交付**：报告 `test-receipts/TEST-TASK16C-independent/attempt-1.md`（逐项 1-9 证据：真实 HTTP/页面输出/命令与退出码、容器/进程 0 残留核对）+ event。
- **收口**：PASS → 协调者推进 16C OCR 裁决与合入；FAIL → 按文件 owner（B）回派最小返修。