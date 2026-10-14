# ACK：TASK-12S-B attempt-1 水雾能力适配器

- status: ACKED
- 派单路径：`inbox/2号/TASK-12S-B/attempt-1-dispatch.md`（协调者 r147，2026-10-13 11:5x +08:00 派发，本侧 11:57:53 prerun 唤醒发现并领取）
- task/attempt：TASK-12S-B / attempt-1（父 TASK-12S，TODO §9 v0.5 水雾优先；AC-17.1/17.2/17.3）
- owner：B（执行者B·前端功能开发群，cron poll `6f7471d8747c`，claim owner `cron-b-poll-6f7471d8747c-20261013-115753`，交付轮续 claim `cron-b-poll-6f7471d8747c-20261013-130728`）
- base：`6fb42c4`（= origin/main，16A 已合入；ACK 时 `git fetch` 后 `git rev-parse` 双核一致确认）
- 分支/worktree：`b/task-12s-b-spray-adapter` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t12sb`（本轮新建，HEAD 实测 `6fb42c4` 洁净）；.venv 软链主仓 `rosbag-catalog/.venv`；**不移动/复用 `wt-04a-t16c`**（16C 冻结证据面，遵暂停交接）
- 交接前提：16C 已 PAUSED（用户暂停界面增量，冻结 head `5c80857`，零触碰）= 派单注明前提满足
- 范围确认：新增 `app/scene/spray/` 包（adapter 注册 `ros2-spray-v1`、两路线解码、冻结选帧/渲染、双 pass 模型归一、整数 storage ns 分段、完整身份键缓存、7 参考图受控、部署预检）+ `config/scene_capabilities.yaml` 新增 `spray-v1` descriptor（`enabled=false`，原 slope/test 条目零变化）+ `tests/test_spray_adapter.py`；**核心 dispatch 不加 spray 硬编码分支（AC-10 口径，参照 slope 先例）**
- 硬边界：不碰 `scripts/`（16B 域，spray 运行时接线属 12S-C/16B）、`app/web/`+`app/templates/`+`bag_search_service.py`+`scene_result_query.py`+`app/api/sources.py`（16C 冻结面）、`ros2_slice`（只读复用契约/参考图）、slope 既有模块行为面（零回归）、16A 双根语义；禁止新模型/迁移/DDL；1012 目录只读；缺图/decoder 型号/软件渲染不等效 = 真实 PASS 阻断，**不迁 A100、不加图像生成、不降阈值**
- 自测口径：定向新用例全绿 + 全仓 SQLite 复跑（base `6fb42c4` 既有失败集=对照口径）+ ruff + `git diff --check` + merge-tree 预核与 main 零冲突
- 交付口径：commit `f62a29c` + 回执 `receipts/TASK-12S-B/attempt-1.md`，REVIEW_PENDING；真实渲染/模型探针本机依赖缺失（numpy/open3d/libseyond*）按派单 §9 报 NOT_RUN，不 mock 当 PASS
- 停止条件：发现需扩面（新表/迁移/16A/16B 域/16C 冻结面）立即停并回报协调者，不自行扩
- ACK 时间：2026-10-13 13:08 +08:00