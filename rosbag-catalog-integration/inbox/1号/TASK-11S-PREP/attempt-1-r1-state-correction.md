# 状态纠正：r1 剩余面收窄 + 停止重跑副本实验（17:1x，协调者）

- 依据：`inbox/coordinator/SPRAY-1900-20261013/a-status-check-1705.md`（只读核查）+ g4r3.log 磁盘证据；**协调者此前"卡死"判断错误，A 17:04 前持续活跃，kill 已致一轮上下文损失，本单纠正剩余面**
- 协调者责任落账：误判原因=采样撞大模型调用间隙（无子进程+无写入≠挂起）；后续巡检口径已修正（见 COORDINATOR.md）

## 立即执行（覆盖 `attempt-1-r1-resume-note.md` 的第 2/3 步）

1. **停止重跑 g4r3 副本实验**——16:55:22 轮已成功：RC_restore=0、RC_upgrade=0，升级前 `20260928_02` → 后 `20261013_01_scene_intake`，Bag 13/流水线 17 不变（证据 `~/.hermes/cache/scratch/t11sp_r165/g4r3.log` 按最后一个 START=16:55:22 区块判，此前连接失败区块作废）；刚建的 `mysqldata`/`mysqldata.*` 临时目录用完清理，**r1-4 视为已完成，回执直接引用该日志区块+前后对照值**
2. 剩余只做三项：
   - r1-1：续用在途 `scene-host.service`（17:04 已改 Docker Compose 装配，核完整后提交；核查提示：service 已改但**所有引用处变量名一致性**要顺带核）
   - r1-2：`rosbag-scene.env.example` 第 15 行 + DEPLOY-ENTRY.md 的 `SPRAY_MODEL_ENDPOINT` → `SPRAY_VLM_ENDPOINT`（以代理代码实读变量为准）
   - r1-3：DEPLOY-ENTRY.md "与 16B 旧 head 逐字节比较" → **发布时点固定 SHA 校验**（r2 `e152465` 及后续合入 SHA 以协调者 17:30 后给出的最终候选为准，脚本化不写死）
3. 写 r1 ACK（`attempt-1-r1-ack.md`，此前未落）+ 回执 r1 段（引用 g4r3 成功区块，不重跑）+ 一次冻结 commit
4. **新目标 17:30 前冻结**（三项都是配置/文档面小改+已有实验证据，无需新实验；若 17:30 未到，17:40 硬线——17:45 生产放行盘点）

## 首包样本口径同步（first-bag-runtime-window-1700.md）
- 44 帧小包 topic span **仅 4.38s**（TESTER 固定快照实测），12 帧选中 span 3.3s——短包可裁剪窗口不补帧（SPRAY-INTEGRATION §4，B `0320a8e` segment 按有效帧边界裁剪）
- 样本决策不再是 A/B 二选一：**小包做功能闭环首包**（12~24 次模型请求，参数/抽样全保持）；53s 长包做后续质量/性能验证（可另批观察窗口，不挤首包）
- 17:30 仍是证据盘点停止点（G1~G4 不齐不放行），延长观察≠生产许可