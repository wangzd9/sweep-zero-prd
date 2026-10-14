# 裁决：scene-4acf689f（16_02_03 大包）静默段定性 = 模型推理活跃，非卡死（协调者）

时间：2026-10-14 02:1x +08:00（prerun 指纹 3ef3152e，TESTER 01:52:52 stall-escalate 事件消费）。

## 独立核实证据（全部协调者只读实测，处理机 192.168.2.134 + VLM 36.152.27.114，02:05-02:16 北京时间）

1. **VLM 远端服务器活跃**（经 A100 ssh llm-server 实测 `/tmp/vllm_qwen38.log` 02:15-02:16）：`Running: 3-4 reqs, Waiting: 0`，持续 `POST /v1/chat/completions HTTP/1.1 200 OK`，prefix cache hit ~95%。**模型推理正在进行，非等待。**
2. **proxy 主进程持有到 VLM 的 ESTABLISHED TCP 连接**（容器内 `/proc/1/net/tcp`：`8602A8C0:EB9C → 2D02A8C0:1F42(=192.168.2.45:8002)` state `01`=ESTABLISHED）。TESTER 01:52 报「worker 零 I/O」系宿主侧 `ss` 空输出的观测盲区，非真实零连接。
3. **产物面**（容器 `/var/lib/scene-proxy/work/scene-4acf689f…/attempt-1/`）：jpg 1781（冻结选帧 pcd[10::3] 全量，EXTRACT 完成）、pcd 5373（全量）；**17:30:53 UTC（01:30:53 +08:00）后零新文件**=EXTRACT 完成、进入逐帧远程模型段（模型结果不写工作目录，只进内存/cache）。
4. **DB 面**（8180 scene-analysis-runs 只读）：`status=SCENE_RUNNING attempt=1`、`lease_expires_at` 随 heartbeat 持续前移（02:09:10→02:11:40 两次实测）、`error_message=''`、八步 DB 状态仍 QUEUED（DB 行在阶段推进/complete-scene 时翻转，非逐步翻转口径）。
5. **CPU 低属预期**：模型段为远端 vLLM 推理（内存受限），宿主 proxy 仅 I/O 编排；TESTER 01:28「多核在算」与 01:41「CPU 骤降」两段合起来正是 EXTRACT（宿主重算）→INFER（远端推理）的阶段切换，非故障。
6. **recovery state**：`stage=EXECUTING, pid=1, identity 匹配容器主进程`，心跳线程正常（`heartbeat_fail_budget=4` 未触发，run 未 FAILED）。

## 定性

**非卡死、非等待条件未满足——INFER 阶段远程模型推理活跃（4acf689f 为跨 DB3 大包，模型段可持续数小时）。**

## 处置

- **TESTER stall-escalate 撤案**：01:52 证据链（voluntary_ctxt_switches 双采样零增量等）方向误判，撤销「疑似卡死」定性；TESTER 下轮按本裁决改核「模型段完成信号」=checkpoint 翻 EXTRACT/DONE 或八步 DB 推进或 SCENE_DONE，不再升级 CPU 静默项。
- **不 kill、不 cancel、不 retry**（既定跨夜口径维持；heartbeat/lease 均健康，无故障前提）。
- A flat 三提交串行阻塞不变，待 4acf689f 终态后 D4③ 推进（口径不变）。
- 模型段无宿主产物增量属正常，**不以「观察超窗」为由干预**；C 继续只读观察（心跳/lease/VLM 负载面），TESTER 继续只读增量验收。

## 升级条件（满足任一才报协调者裁决）

heartbeat 连续 4 次失败 / run 翻 FAILED / VLM 侧 Waiting 持续>0 且 proxy 无 ESTABLISHED 连接 / checkpoint 或八步翻 FAILED 错误面。

## 交叉证据消费（02:1x 补记）

- **C obs22（02:01）独立佐证本裁决**：容器 /proc/net/tcp ESTAB 134:52552→192.168.2.45:8002、RSS 15.8→18.2GB 持续增长、work 树 jpg/pcd 双采样冻结、lease 续租活跃——判「EXTRACT 已完成、大概率 INFER/后续段，在算未冻结」，与协调者裁决一致，C 全程只读。
- **TESTER 02:03/02:11 分歧证据统一裁定**：DB 层八步 QUEUED 零推进 vs 进程/work 树层推理段活跃——定性=**非矛盾，属阶段边界写口径**：八步 DB 状态在阶段完成时翻转（PRECHECK 已 DONE），逐帧模型调用发生在 INFER 进程段不落逐步 DB 行；「入队 ~185min 无 started_at」不构成卡死证据。TESTER 01:52 stall-escalate 与 02:03「零实质推进」口径**一并撤销**，改按本裁决「模型段完成信号」核（checkpoint 翻 EXTRACT/DONE、VLM Waiting>0、ESTAB 消失+无推进、heartbeat 4 连败）。
- 另 C obs22 端点口径修正入案：run 详情真实路径 `/api/v1/scene-analysis-runs/{pipeline_run_id}`（obs21 截断 id 404 属观察工具面，不影响生产）。
- **C obs23（02:16）继续佐证**：VLM 8002 ESTAB 维持 1 条（临时端口 52552→52342 重建=长连接重建非通道消失）、work 树 jpg 1781/pcd 5373 双采样零新增、lease 续租 02:14→02:17、load 0.24 低位、SEGMENT-WRITE 产物目录未现（模型段完成信号仍未到）——口径与本裁决一致，零 run 级变化。
- **C obs23 申报的「sessions/C.md obs18–22 缺口」核查不成立**：协调者实测 canonical `sessions/C.md`=568 行，obs18（564 行）/obs19（565）/obs20（566）/obs21（567）/obs22（568）全在案；C 自测 `wc -l=54` 命中旧镜像 `inbox/sessions/C.md`（双文件坑第三次复发，2026-10-13 01:48 / 10-14 01:42 已两次申报）。**不立返修单**（事件链完整无业务影响），C 下轮自核用 canonical 路径；08:00 汇总记一条观察面教训。

— 协调者，持轮内只核实测，零生产写。