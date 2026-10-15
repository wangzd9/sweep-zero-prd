# TASK-16R 水雾债补审 fe17e8a..3c9c496 审查背景（协调者 2026-10-14 20:1x +08:00）

## 范围与授权

- 审查身份：`ocr-fe17e8a-r1`，base=`fe17e8a765c7b6add2d809650822329463fbe079`，head=`3c9c4964c2a2a89201cfde5ed747e9fd05d4c6bc`（=生产业务基线，已在 main 祖先链，16a154f 已含）。
- 授权来源：`inbox/control/V04-UI-RESUME-20261014.md`（原 OCR 未修项进入任务）+ `reviews/TASK-16R/attempt-1-disposition.md` §处置（fe17e8a..3c9c496 为唯一从未被弱 OCR 全扫的生产增量，低优先补审候选，待 ocr.lock 空窗经唯一入口补）。16C 已合入 main 16a154f，OCR 空窗成立。
- 本区间 = 3 个生产 commit：ad60e41（uncertain 回报重试+失败停止信号）、8e538bb（场景发布证据只读暴露给 backend）、3c9c496（本地 SQLite 切片先写、NAS staging 校验后落盘）。

## 入选/排除

- 入选（全部 app/scripts 生产代码变更）：`scripts/scene_host_orchestrator.py`（+70/−9）、`scripts/scene_host_proxy.py`（+24）。
- 排除：`tests/test_scene_host_proxy_r5.py`、`tests/test_scene_local_write_nas_stage.py`（测试归 TESTER/既有 e2e 覆盖口径：r5 181 行、local_write 134 行已由 12S-C 正式接线 e2e 与生产原 run SCENE_DONE 实证覆盖，不强审不复跑）。`deploy/scene/catalog-scene.yaml` 因解析规则自动入选，单列第三批只读审（+5 行 Compose 描述：env/挂载/端口面，无业务逻辑，findings 按部署配置口径裁决）。

## 关键契约与不变量（审查重点）

1. **回报重试（ad60e41）**：uncertain 终态回报（complete/fail/ack）重试必须幂等——同一 run 同一终态重复回报不得产生新的副作用（不重烧模型、不重复发布、不改业务状态机终态）；失败停止信号（stop signal）必须被编排器遵守并落持久证据，不能只打日志。
2. **证据只读暴露（8e538bb）**：向 backend 暴露的发布证据接口必须只读（无写端点、无删除/覆盖路径）；证据文件缺失/损坏时返回受控错误，不得伪造证据内容。
3. **本地先写 + NAS staging（3c9c496）**：切片 SQLite 先落本地、经校验（完整/可读）后再 staging 到 NAS；本地副本与 NAS 副本一致性由校验保证；校验失败必须使 run 进入可追溯失败态而不是静默跳过；不得出现只落本地不发布且状态为 DONE 的分支。
4. 跨文件契约：orchestrator 与 proxy 之间 run 状态/终态语义一致（pending_failure 保留、终态清租约后步骤写恒过的约束来自 16B 已接受口径，本区间不得回退）。

## 既有验收口径（不替代本补审，仅背景）

- 12S-C 正式接线 92dcb52 已合入 main，生产原 run 八步 DONE/SCENE_DONE；恢复 89 例与 NAS 修复 19 例 PASS（TASK-16B 收尾口径在案）。
- 强审 R4（29af08a→ad60e41 最小修）17 项修前 16FAIL/1PASS→修后全 PASS，相关 89 PASS（final-r4-correction 在案）；fe17e8a 跨 FS 发布 3 项/编排 15 PASS，无剩余强审缺口 NOT_REQUIRED。
- 本补审仅补「弱 OCR 从未全扫」的审查债，findings 按既有流程裁决：真实缺陷对应原 AC 回原 owner（16B 域），误报注明依据；不因范围外建议扩需求。

## 版本

代码版本 fe17e8a..3c9c496（生产业务基线，已随 main 16a154f 前在案）；审查窗口 2026-10-14 20:1x +08:00。