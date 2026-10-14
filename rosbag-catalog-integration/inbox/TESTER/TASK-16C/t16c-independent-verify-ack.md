# TESTER ACK：TASK-16C 独立验证（t16c-independent-verify，attempt-1 交付冻结后首验）

- status: ACKED / 已开工
- task/attempt: TASK-16C / t16c-independent-verify
- 角色: TESTER（测试者）
- 时间: 2026-10-13 10:33 +08:00
- 派单: `inbox/TESTER/TASK-16C/t16c-independent-verify-dispatch.md`（协调者 r142）

## 固定被测快照（已独立核一致）
- worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t16c`，分支 `b/task-16c-scene-ui-minimal`，HEAD **`5c80857`**
- 核实：`5c80857` 为 main `6fb42c4` 子节点单 commit；`git diff 6fb42c4..5c80857` sha256 与 `git diff 4b9f30a..ad37ae1` 逐字节一致（8f0f0437…）
- 交付回执 `receipts/TASK-16C/attempt-1.md`（B，REVIEW_PENDING，8 文件 +957/−33）
- **未合入 main，验证全程以该 worktree 起服务，不切 main**

## 环境
- 被测 worktree 只读（`.venv` symlink 主仓 venv，Python 3.10）
- 本地起服务：worktree 内 uvicorn，DEMO_DATA=1 + 临时 SQLite 库（DATABASE_URL 指向 scratch 临时文件，conftest 口径）
- **不触碰 16B worktree `wt-03b-t16b` 与 `inbox/ocr.lock` 在途 OCR**
- 页面浏览器走查用 browser_exec 实测 HTTP；SQLite 取证（派单口径：本单无 DDL/迁移，仅 SELECT 谓词，不要求真 MySQL）

## 验证场景（派单 1-9 逐项取证）
1. 三类原始行（NVIDIA 输入记录 NOT_APPLICABLE 标「英伟达原始」；空 Topic/未知历史不猜类型）
2. 切片视图（当前可用/历史/下架 withdraw 退出默认检索 all 可见，同 07B 语义）
3. 双用途原包（行级双标并置；筛选单值 CASE scene_original 优先）
4. data_kind 四类筛选 × 视图/来源组合（不相容组合 → 200 `items=[]` 非 500 非静默丢条件）
5. `GET /api/v1/bags` 集合路由（view/过滤/cursor clamp 50..200/不一致 422/历史兼容/路由顺序先于 bags by-uid 路由）
6. 场景八步详情（SUCCESS 全步真实完成/部分不伪标/NO_MATCH 跳过+运行级非 SUCCESS/FAILED 错误原样/终态页无 10s 自动刷新，非场景页不变）
7. 场景运行环境区（模型端点/处理机输入/场景 NAS，无 A100 面；血缘降级不 500）
8. 旧界面兼容回归（bags 原有筛选/分页不回归、dataset_type 旧书签可用、pipeline 非场景面板 scene 不渲染）
9. SQLite 全仓回归（876 passed 4 failed base 既有口径，新 failed 二分归属）

## 报告路径
- `test-receipts/TEST-TASK16C-independent/attempt-1.md` + event

## 停止条件
- 逐项 PASS/FAIL/BLOCKED 证据落盘即交付 TEST_REPORT_PENDING；不改业务实现、不跑 OCR、不推进合入
