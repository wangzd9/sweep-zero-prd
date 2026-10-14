# 第 8 跑归属口径合并与清理核验（协调者，2026-10-12 08:4x 轮）

- 冲突事实：08:10 cron 轮判第 8 跑（08:03:42 起/08:09:58 DONE）越权不采纳（起跑早于 08:00 轮停止裁决落盘 08:05:34 约 2 分钟，重叠窗口）；08:13 交互轮 HANDOFF 记录**用户授权测试环境 real 全流程实测**（用户从三选项选定「场景线 real 全流程实测」，不含自建 Phase0/1/3 重流水线），同一第 8 跑全链通过 T11_RC=0。
- 合并依据：第 8 跑产物链（阳性 slope：register→1c 生产路径自动升 READY→claim→analyze SUCCESS 177.2s/1 段→derive_storage_offset=100381744→publish 1 slice→/results 200→/complete-scene 200 SCENE_DONE/switched；阴性 flat NO_MATCH 不误发布；源袋 sha256 不变）与用户授权范围（测试环境、场景线、real 全流程）逐条吻合；证据已归档 `~/.hermes/cache/scratch/a_t11_evidence/`（t11-run.log/t11-e2e.json）。
- 裁决：**第 8 跑 = 用户授权的测试环境实测（A 侧驱动），撤销 08:10 轮「越权」定性**，产物采纳为「用户授权测试环境实测」证据；**不采纳为 TASK-11 生产证据**——TASK-11 生产启用门禁维持未放行（裁决 3 不变，生产部署需用户独立生产授权）。
- 08:00 轮裁决 1（对 A 停止再跑+残留清理）执行情况核验：停止 ✓（无第 9 跑、ps 无 t11/launcher/real_e2e 存活）；清理 ✓（T11 口径 DB 各表 0、共享根/hs 驱动文件删、incoming 两袋 absent、t11-publish 子内容清并保留挂载点）；**残留缺口 1**：第 8 跑两个 ready/ 袋目录（slope 229MB + flat 287MB）未清 → 本地栈 scanner 08:30:51 将 slope 袋重新登记 `bag_record` id=26（17→18）→ 已回派 A 最小清理单 `inbox/1号/TASK-11/t11-cleanup-residual-20261012.md`（删两袋目录+id=26 关联行，复验回 17）。
- coord 侧 scratch 清理：`coord_t11_*`/`t11_verify.py` 属协调者产物已删；`b-t11-ruling-evt.md` 为 B 侧产物不动。
- 门禁不变：TASK-10 DONE/P0 收口；TASK-11 生产未放行；TASK-07/12/13/14/15 维持 DEFERRED；空闲不扩需求。