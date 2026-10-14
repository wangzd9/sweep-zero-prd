# 报告：TASK-16B attempt-1 处理机本机场景代理（八步/幂等/恢复/带宽证据/假 VLM 断言）

- task/attempt: TASK-16B / attempt-1
- owner: C
- 交付 commit: `0208a73`（在 `9437308` 之上）
- base: main 本地 `c2018dd`
- 报告时间: 2026-10-13 01:0x +08:00

## 1. 八步执行编排（scene_host_orchestrator）

`PRECHECK → EXTRACT → INFER → SEGMENT → WRITE → VALIDATE → PUBLISH → REGISTER`，全部在处理机本机私有 run/attempt 目录（`work_root`），A100 不运行场景代码。

- **复用不改**：EXTRACT/INFER/SEGMENT 经 `app.scene.adapter.dispatch`（内部按 capability 选 SlopeAdapter：抽帧解码→逐帧模型→整数纳秒分段）；WRITE/VALIDATE 用 `app.scene.slope.writer.slice_bag_to_staging`（staging 写出 + 非空/可打开/topic/时间/CDR 抽验）；PUBLISH 用 `app.services.scene_publish_service.publish_scene_slices`（同文件系统原子 move）。**不改 app.scene 行为面**。
- **失败归因到步骤**（dispatch 一次完成 EXTRACT+INFER+SEGMENT，失败时按 `SceneRunResult.error_code` 取最先失败的步）：DECODE_FAILED/BAG_READ_FAILED/NO_VALID_INPUT→EXTRACT；MODEL_UNAVAILABLE/ADAPTER_ERROR/CAPABILITY_ERROR→INFER；SEGMENT_RULE_ERROR/INVALID_MODEL_OUTPUT→SEGMENT。
- **连接失败/超时不当 NO_MATCH**：模型异常→INFER FAILED（带步骤+证据），有限重试复用 `HttpSlopeModelClient`；storage_offset 不可推导→VALIDATE fail-closed 阻塞发布。
- **NOT_APPLICABLE**：EXTRACT 适用性判定即终止（无识别结论），正常终态非失败。
- **幂等/恢复**：child_bag_uid 由 (run_id, attempt, slice_key) 确定性派生（≤26 字符）；每步写 `checkpoint.json`（步骤+证据+进程身份），崩溃恢复据此判断已完成步，不重做、不产生半截发布物；模型结果走 run 私有 `ModelResultCache`（内容键），重试不重复计费。
- **不直连库**：REGISTER 只经注入的 `SceneBackendReporter`（真实实现 = POST /results + POST /complete-scene；测试用确定性 fake）。

## 2. 常驻代理（scene_host_proxy）幂等 / 恢复

- **(run_id, attempt) 幂等**：POST /run 先持久台账（进程身份+检查点）再返回 accepted；同身份重发命中 `already_running` 返回同一接收结果，**禁第二写者**；不同 attempt 撞车 409。派发响应丢失→台账对账后安全。
- **进程崩溃恢复（kill -9 等价）**：恢复文件记 pid + starttime；重启先核验旧写者终止（PID 不存在 或 启动时刻不同→PID 复用防御）再按原身份续跑；run 已终态丢弃清状态。测试用真实子进程死亡身份验证。
- **续租**：心跳续租任务租约 + SCENE_EXEC_HOST 资源租约；连续失败先对账 run 详情（终态→收尾；非终态→停写）。
- **取消协作**：轮询 SCENE_CANCELLING→停写→确认 CANCELLED；完成态不确认（防 409 覆盖）；停写确认失败→SCENE_FAILED。停写信号经 `SceneExecSpec.stop_event` 注入 adapter `Cancellation`（协作式）。
- **受控根 / fail-closed**：发布根 `SCENE_SLICE_PUBLISH_ROOT` 配置注入、回报恒受控根；源路径 = `SCENE_NAS_READY_ROOT` + bag `relative_path` 物理映射；缺根/不可写→`CONFIG_REQUIRED` 拒启动。

## 3. 带宽证据面（fake_vlm_server）+ 假 VLM 断言

自包含测试面（非系统级限速/批量压测，派单三节排除）：
- 与生产 `HttpSlopeModelClient` 同协议（OpenAI chat/completions）；帧分类由服务端 `label_policy` 确定性返回。
- 记录**实际传输量**：请求 bytes、帧数、重试次数、单请求时长。
- **断言无整包/NAS 泄漏**：请求体 forbidden-marker 检查（`.db3`/`rosbag`/`/public/`/`nas`/`slice_manifest`/`metadata.yaml` 绝不应出现），只含图像帧(base64 jpeg)+模型参数+最小关联 ID。
- 可注入失败（`fail_first_n`/`timeout_after`）验证连接失败**不当 NO_MATCH**。

## 4. 自测结果（命令/退出码/环境）

环境：wt-03b-t16b，`.venv`（Python 3.10），`SLOPE_VLM_ENDPOINT` 注入假 VLM，确定性 `tests/scene_fixture` CompressedImage bag（真 ROS2 CDR 封装）。

| 命令 | 退出码 | 结果 |
|---|---|---|
| `pytest tests/test_scene_host_orchestrator.py tests/test_scene_host_proxy.py -q` | 0 | **26 passed**（编排 12 + 代理 14） |
| `pytest tests/ -q -k "scene or slope"` | 0 | **276 passed, 612 deselected**（场景既有套件 0 回归） |
| `pytest tests/ -q`（全量） | — | **876 passed, 3 failed, 10 skipped**；3 failed 全在 `tests/test_devflow.py`（**既有失败**，`git stash` 还原干净 HEAD 后同样 3 failed，与本单零关联） |
| `ruff check scripts/scene_host_proxy.py scripts/scene_host_orchestrator.py tests/test_scene_host_proxy.py` | 0 | **All checks passed** |

代理 14 用例覆盖：全链 SUCCESS 冒烟（/run→八步→Backend 收 /results + /complete-scene→恢复文件清除→资源租约释放→health 收敛）、幂等重发、坏身份 422、health 空、崩溃恢复（死亡续跑/存活不接管/终态丢弃）、配置 fail-closed、load_config env。

## 5. 未执行项
- 最终 real 栈全链冒烟（/bags 出 AVAILABLE 切片，t11e run8 同口径）：**待 16A 接受产物后接续**（16A 未接受前不抢写 config/models/迁移）。
- 生产端口/挂载/容量核验：TASK-11 部署前置（PRODUCTION BLOCKED）。