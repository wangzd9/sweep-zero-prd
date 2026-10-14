# 派单：TASK-16B attempt-1 处理机执行接线·本机场景代理（v0.4 最小闭环）

- status: REVIEW_PENDING
- 派单时间：2026-10-12 22:45 +08:00
- 任务：TASK-16B 处理机执行接线（REQ-15、REQ-06、REQ-07 / AC-15、AC-06、AC-07；DESIGN §7.3.2 冻结契约）
- 授权来源：**用户 2026-10-12 群内明确授权**（"开始分派干活"）+ v0.4 冻结契约（执行位置=处理机本机代理，A100 不运行场景代码）
- owner：C（执行者C·数据链路监控告警群，wt-03b 系；监控/代理/常驻执行域）
- base：main 本地 `c2018dd`（= origin `502bf8e`+1 纯文档；07B 未合入，本单不碰 07B 文件集）
- 依赖策略：**可先据 §7.3.2 冻结契约做代理/编排与模块自测**（本地测试根 `/home/wang/work/.local/rosbag-catalog/scene-work` + `proxy-state/scene`）；最终接线与冒烟**消费 16A 已接受产物**（profile `scene-isolated`/根上下文/登记 root_id），16A 未接受前不得抢写配置/models/迁移。

## 一、交付内容（严格按 DESIGN §7.3.2）
1. **常驻本机场景代理** `scripts/scene_host_proxy.py`（正式部署程序，**不得把 scratch E2E 脚本当部署程序**——t11/t11e 驱动仅作参考口径）：
   - `POST /run`：接收现有 Orchestrator `dispatch_payload`，先验证 SCENE_SLICE/run/源代次/任务及资源租约和受控配置，**持久记录 `(run_id, attempt)` 后立即返回 `accepted=true`**，后台执行；同身份重复请求返回同一接收结果、禁止第二个写者
   - `GET /health`：返回 active run 摘要；恢复文件记录进程身份和检查点
   - 派发响应丢失：先按原身份对账再重发/标失败，不假定未启动
   - 进程重启：先核验进程/已发布 manifest，终止旧写者后才能重试；持续续租；租约失效或收到取消→停止新写入/请求、对账后回报并释放许可
   - **执行代理不得直连数据库**（所有状态经 Backend API）
2. **八步执行编排**（处理机本机私有 run/attempt 目录）：`PRECHECK → EXTRACT → INFER(仅请求模型服务) → SEGMENT → WRITE → VALIDATE → PUBLISH → REGISTER`
   - EXTRACT/SEGMENT/WRITE/VALIDATE 复用现有 `app.scene` 适配器与 `scene_publish_service`（执行编排独立模块，不改 app.scene 行为面——若发现必须改 app.scene，申报越界不擅改）
   - **A100 不运行场景代码、不存场景原包/切片/整包工作副本**
3. **远端模型接线**：
   - `SLOPE_VLM_ENDPOINT` 指向受控远端模型服务；请求只含必要抽样帧、模型参数、最小关联 ID；**不传 ROS2 Bag/完整视频/发布产物/NAS 路径**
   - 帧采样沿用已接受 `front-camera-jpeg-1hz` 与真实验证参数；重试/超时复用现有 `HttpSlopeModelClient`；**连接失败/超时不当作 NO_MATCH**，保留步骤与证据按原 run/attempt 对账、有限重试
   - `VLM_PERMITS` 限额沿用同一既有 executor_id 口径（不换 executor_id 造第二套额度）；模型结果版本与请求身份可追踪；不记录凭据
4. **NAS 发布接线**（16A 消费点）：读受控 `SCENE_SLICE_PUBLISH_ROOT` 物理映射；跨盘先写 NAS 同文件系统 `.staging/<run_id>/<attempt>` 并校验再原子 rename；**不信任自选 publish_root**（回报给 Backend 用受控根）
5. **Orchestrator 侧接线**：`SCENE_PROXY_URL` 已有配置名指向本机代理（生产端口部署时核实，不猜占用）；确认现有 dispatch 对场景 run 的派发路径可打通（orchestrator 代码若需最小改动，限 `SCENE_PROXY_URL` 派发面，申报后改）
6. **资源预检**：本机磁盘/依赖 preflight + 有界并发（首期不建通用调度器）；工作根峰值空间覆盖记录
7. **带宽证据面**：测试可注入有带宽上限的 HTTP 服务记录实际请求 bytes/帧数/重试/持续时间（自包含测试面即可，不做系统级限速/批量网络压测）

## 二、测试与验收口径（TESTER 16D 前自测证据）
- 模块自测：八步编排单步失败→步骤/证据保留+有限重试；(run_id,attempt) 幂等（重复 /run 同结果）；取消/租约失效→停止写入+对账回报
- 进程崩溃恢复：kill -9 后重启→旧写者终止核验→对账→重试不产生第二个写者
- 模型侧：注入假 VLM HTTP（可断言请求体**不含**整包/NAS 路径，只含图像帧+参数）+ 带宽记录；超时/断连→非 NO_MATCH 口径验证
- 本地测试根冒烟：scene-work + proxy-state 落位、health 摘要真实
- 既有 orchestrator/scene 套件 0 红；ruff 绿
- 最终全链冒烟（16A 接受后）：本地 real 栈 + 本机代理替宿主脚本跑一袋坡道 → /bags 默认视图出 AVAILABLE 切片（与 t11e run8 同口径证据）

## 三、边界与禁止
- 不碰 07B 冻结文件集；不改 03~06B 场景状态机/幂等/发布行为（只消费其 API/模块）
- 不部署生产（TASK-11 门禁独立）；生产端口/挂载/容量核验属部署前置，本单只在契约+测试根层面交付
- 不改 `app/scene/slope/*` 算法面（帧判定/分段/切包逻辑 v0.4 不重做，沿用已真实验证参数）
- 与 16A 文件面冲突时（配置项/models/迁移）：16A 所有，本单只声明消费契约

## 四、交付物
- commit（base c2018dd 之上）+ 回执 `receipts/TASK-16B/attempt-1.md`（REVIEW_PENDING）+ 报告 `reports/TASK-16B/attempt-1.md`（八步/幂等/恢复/带宽证据/假 VLM 断言记录）
- 交付后：机械核验 → 串行 OCR（scripts+app 派发面）→ 合入 → 与 16A 产物接线冒烟 → TESTER 16D 候选