# 回执：TASK-16B attempt-1 处理机本机场景代理

- status: REVIEW_PENDING
- task/attempt: TASK-16B / attempt-1
- owner: C（执行者C·数据链路监控告警群）
- 派单：`inbox/3号/TASK-16B/attempt-1-dispatch.md`
- base: main 本地 `c2018dd`（= origin `502bf8e`+1 纯文档）
- 分支/worktree: `c/task-16b-scene-host-proxy` @ `/home/wang/.local/state/rosbag-scene/wt-03b-t16b`
- 交付 commit: **`0208a73`**（在 `9437308` 之上；本轮新增常驻代理 scene_host_proxy + 测试）
- 交付时间: 2026-10-13 01:0x +08:00
- 范围声明: 只消费既有 `app.scene`/`scene_publish_service`/`scene_result_report` API，**不改 app.scene 行为面、不碰 07B 冻结文件集、不部署生产**；Orchestrator 侧 `SCENE_PROXY_URL` 派发面在既有基线已冻结（app/orchestrator.py 场景队列领取→POST /run），本单不改动其代码面。

## 一、交付物清单
| 文件 | 类型 | 说明 |
|---|---|---|
| `scripts/scene_host_orchestrator.py` | 新增（9437308） | 八步执行编排引擎（PRECHECK→…→REGISTER），复用 app.scene/04B writer/06B 发布层，不直连库 |
| `scripts/scene_host_proxy.py` | 新增（0208a73） | **常驻本机场景代理**（正式部署程序，非 scratch 驱动） |
| `tests/test_scene_host_orchestrator.py` | 新增（9437308） | 编排 12 用例（全链/NO_MATCH/NOT_APPLICABLE/失败归因/有限重试/幂等/崩溃恢复/PRECHECK 受控） |
| `tests/fake_vlm_server.py` | 新增（9437308） | 假 VLM 带宽证据面（记录请求 bytes/帧数/重试/时长，断言无整包/NAS 泄漏） |
| `tests/test_scene_host_proxy.py` | 新增（0208a73） | 代理 14 用例（假 Backend HTTP + 假 VLM + fixture bag） |
| `reports/TASK-16B/attempt-1.md` | 新增 | 八步/幂等/恢复/带宽证据/假 VLM 断言记录 |

## 二、常驻代理行为（§7.3.2 契约实现）
- **POST /run**：接收 dispatch_payload，**先持久记录 (run_id, attempt) 接收台账 + 进程身份（pid+starttime）后立即返回 `accepted=true`**（202），后台线程执行；同身份重复请求返回同一接收结果（`already_running`，200），**禁止第二个写者**；不同 attempt 撞车返回 409。
- **GET /health**：返回 active run 摘要（run_id/stage/attempt/pid）。
- **崩溃恢复（kill -9）**：恢复文件（`proxy-state/scene/<run_id>.json`）记录进程身份与检查点；重启后**先核验旧写者进程已终止**（PID 不存在 或 启动时刻不同→PID 复用防御），再按原身份续跑——编排 checkpoint 保证已完成步不重做、模型不重复计费、不产生第二写者；run 已终态则丢弃并清状态。
- **续租/停写**：心跳线程续租任务租约 + SCENE_EXEC_HOST 资源租约；连续失败先**对账 run 详情**（终态→正常收尾；非终态→置停写信号）；停写信号经 `SceneExecSpec.stop_event` 注入 adapter `Cancellation`（协作式，帧循环轮询 is_cancelled 后停止写入）。
- **取消协作**：轮询 run 状态，SCENE_CANCELLING→停写→确认 CANCELLED；**run 已完成态不确认取消**（防 409 覆盖已发布产物），停写确认失败→SCENE_FAILED。
- **不直连数据库**：全部经 Backend API（run/source 详情、steps、status、`/results`、`/complete-scene`、orchestrator leases）。
- **受控发布根**：`SCENE_SLICE_PUBLISH_ROOT` 配置注入，**不信任自选根**；回报给 Backend 的 publish_root 恒为受控根（06B 完整性核对口径）。源路径 = `SCENE_NAS_READY_ROOT` + bag `relative_path`（物理映射，不猜 NAS 路径）。
- **配置 fail-closed**：缺受控发布根/源映射根/不可写 → `CONFIG_REQUIRED` 拒绝启动。
- **步骤回报**：七步（PRECHECK..PUBLISH）DONE 在 complete-scene 清租约前回报；REGISTER 步在终态后补报（容忍 409，失败留痕不视为执行失败）。

## 三、自测证据（命令/退出码/环境）
环境：wt-03b-t16b，`.venv`（Python 3.10），`SLOPE_VLM_ENDPOINT` 注入假 VLM，确定性 `tests/scene_fixture` CompressedImage bag。
| 命令 | 退出码 | 结果 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_scene_host_orchestrator.py tests/test_scene_host_proxy.py -q` | 0 | **26 passed**（编排 12 + 代理 14） |
| `.venv/bin/python -m pytest tests/ -q -k "scene or slope"` | 0 | **276 passed, 612 deselected**（场景既有套件 0 回归） |
| `.venv/bin/python -m pytest tests/ -q`（全量） | — | **876 passed, 3 failed, 10 skipped**；3 failed 全在 `tests/test_devflow.py`（**既有失败**：`git stash` 还原到干净 HEAD 后同样 3 failed，与本单零关联） |
| `.venv/bin/ruff check scripts/scene_host_proxy.py scripts/scene_host_orchestrator.py tests/test_scene_host_proxy.py` | 0 | **All checks passed** |

关键断言（代理 14 用例）：
- 全链 SUCCESS 冒烟：/run 受理→八步 SUCCESS→Backend 收到 `/results` + `/complete-scene`、REGISTER 步 DONE、恢复文件清除、资源租约 DELETE 释放、health 收敛空。
- 幂等：同 (run_id, attempt) 重复 /run 返回 accepted（already_running），health active 计数恒 ≤1，无第二写者。
- 崩溃恢复：真实子进程死亡身份（kill 后 /proc 消失）→ recover 续跑 1 例并收敛终态；存活写者（本进程 pid+starttime 一致）→ 不接管；run 已 SCENE_DONE → 丢弃清状态。
- 配置：缺 publish_root → CONFIG_REQUIRED；load_config 读 env 正确。
- 假 VLM 带宽面（编排层）：请求体**只含图像帧+模型参数**（forbidden-marker 断言无 .db3/rosbag/NAS 路径泄漏）。

## 四、未执行项（需 16A 接受后接续 / 独立阶段）
- **最终 real 栈全链冒烟**（本机代理替宿主脚本跑一袋坡道→/bags 默认视图出 AVAILABLE 切片，t11e run8 同口径）：**依赖 16A 已接受产物**（profile `scene-isolated`/专用接收根上下文/登记 root_id）。16A 未接受前本单不抢写 config/models/迁移，只据 §7.3.2 冻结契约做代理/编排模块与测试根冒烟（已交付）。**待 16A 接受后接续。**
- **生产端口/挂载/容量核验**：属 TASK-11 部署前置（生产门禁 PRODUCTION BLOCKED 待用户独立授权），本单只在契约+测试根层面交付。
- **带宽系统级限速/批量网络压测**：派单三节明确排除，仅自包含测试面（已交付 fake_vlm_server）。

## 五、越界申报
无。未改 `app/scene/slope/*` 算法面、未改 03~06B 场景状态机/幂等/发布行为、未碰 07B 冻结文件集、未部署生产、未改 Orchestrator 代码面。与 16A 文件面（config/models/迁移）零冲突（本单只消费 API）。

**交付后请协调者推进**：机械核验 → 串行 OCR（scripts/scene_host_proxy.py + scene_host_orchestrator.py 派发面）→ 合入 → 与 16A 产物接线冒烟 → TESTER 16D 候选。