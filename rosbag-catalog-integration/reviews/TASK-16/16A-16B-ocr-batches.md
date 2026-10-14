# TASK-16A + TASK-16B 串行 OCR 批次账（协调者 r107 建账）

- owner：协调者（cron poll 14ae4556629a r107）
- 起跑：01:49:20 detached（pid 959241，start_new_session，flock 持 `inbox/ocr.lock`，跨 cron 存活）
- 工具：ocr v1.12.9（`~/.npm-global/bin/ocr`，接 127.0.0.1:18002 本机 Qwen）
- 策略：逐文件单审（防 420s reap，r95/r105 先例）；tests/* 排除（default_path 先例，独立验证挂 TESTER 16D）；**§3.6 尺寸预检**：16B 两脚本 >500 行（orchestrator 583 / proxy 968）独立成批 + `--max-tokens 30000` 拆组。
- 进度文件：`/home/wang/.hermes/cache/scratch/t16_ocr/t16_ocr_progress.txt`；结果 `t16_ocr_results.json`；每批 log `t16_ocr/*.log`。
- 硬截止：起跑后逐轮巡检核 progress；单批 >30min 无收口行记活动停滞告警（不催不接管，r101 重试政策口径：再失败挂 NEEDS_REVIEW 冻结对应合入门禁，不无限重试）。
- **⚠️ v1 口径缺陷纠正（02:0x）**：v1 runner（pid 959241，01:49 起）用 `-c <target>` 只审单 commit diff——16A/16B 均为两 commit 链，第一 commit 新增文件（16A environment_contract/scanner 4 文件等、16B orchestrator/proxy 全部）被 "Review skipped: no items selected" 空批跳过（dur=0s 多批；v1 有效收口仅 config 0 findings `31adcbc1` + models 0 findings `188033dc` 两批，已审范围口径与 v2 一致可复用）。**v1 已 kill（02:03）**；v2 范围模式重跑 `run_t16_ocr_v2.py`（`--from c2018dd --to HEAD` 逐文件，pid 980094 02:04 起跑，进度 `t16_ocr_v2_progress.txt`，结果 `t16_ocr_v2_results.json`）。

## TASK-16A（base `c2018dd` → target `c30f048`，2 commit 链 `79f6889`+`c30f048`，16 app 文件 +1147/-59）

| batch | 文件 | diff | session | 起止 | status | findings |
|---|---|---|---|---|---|---|
| T16A-b1 | app/config.py | +105/-0 | 待跑 | 01:49:20 START | INFLIGHT | - |
| T16A-b2 | app/environment_contract.py | +10/-0 | 待跑 | - | QUEUED | - |
| T16A-b3 | app/models.py | +10/-0 | 待跑 | - | QUEUED | - |
| T16A-b4 | app/scanner/backend.py | +10/-1 | 待跑 | - | QUEUED | - |
| T16A-b5 | app/scanner/clients.py | +6/-1 | 待跑 | - | QUEUED | - |
| T16A-b6 | app/scanner/paths.py | +33/-8 | 待跑 | - | QUEUED | - |
| T16A-b7 | app/scanner/runner.py | +126/-30 | 待跑 | - | QUEUED | - |
| T16A-b8 | app/schemas/requests.py | +5/-0 | 待跑 | - | QUEUED | - |
| T16A-b9 | app/services/bootstrap.py | +6/-1 | 待跑 | - | QUEUED | - |
| T16A-b10 | app/services/ingest_service.py | +140/-16 | `1879ae1e` | rc=0 1337s | COMPLETED | 1 low（list_profiles 未传 root_id，待全收口合并裁决） |
| T16A-b11 | app/services/scene_intake.py（新增 90 行） | +90/-0 | - | - | INFLIGHT | 03:11:43 START |
| T16A-b12 | app/services/source_service.py | +18/-1 | 待跑 | - | QUEUED | - |
| T16A-b13 | alembic/versions/20261013_01_scene_intake.py | +74/-0 | 待跑 | - | QUEUED | - |
| T16A-b14 | compose.yaml | +9/-0 | 待跑 | - | QUEUED | - |

排除：`tests/test_scene_intake_isolation.py`（+493）、`tests/test_scanner_stability.py`（+12/-1）=tests default_path 先例。

## TASK-16B（base `c2018dd` → target `0208a73`，2 commit 链 `9437308`+`0208a73`，3 文件 +2543/-0）

| batch | 文件 | diff | session | 起止 | status | findings |
|---|---|---|---|---|---|---|
| T16B-b1 | scripts/scene_host_orchestrator.py（583 行，--max-tokens 30000） | +583/-0 | 待跑 | - | QUEUED | - |
| T16B-b2 | scripts/scene_host_proxy.py（968 行，--max-tokens 30000） | +968/-0 | 待跑 | - | QUEUED | - |
| T16B-b3 | tests/fake_vlm_server.py（179 行测试面，随批审） | +179/-0 | 待跑 | - | QUEUED | - |

排除：`tests/test_scene_host_orchestrator.py`（+307）、`tests/test_scene_host_proxy.py`（+506）=tests default_path 先例。

## 机械核验前置（r107 已核，OCR 收口依据）

- 16A：定向 25 passed（协调者独立复跑）；边界 `git diff c2018dd..c30f048 --name-only` 零 07B 冻结文件、零 scripts/（C 域）；merge-tree vs main 干净；迁移单头 down=`20261009_02_ingest_frozen`（=base 单头，07B `20261012_01` 未合入故无冲突；07B 合入后双头问题按 A 申报由协调者合入面裁决——**16A 合入必须先于或同步处理 07B 迁移链**，r107 记账）。
- 16B：定向 26 passed（协调者独立复跑）；边界零 app/、零 alembic、零 07B 文件（C 域 scripts+tests 新增）；proxy-state 恢复/幂等/假 VLM 带宽面已自测申报；**未执行项**=16A 接受后 real 栈全链冒烟（接线面，16D 前）。
## v2 进度回写（r110，2026-10-13 02:2x，协调者巡检）

v2 runner（pid 980094，`--from c2018dd --to HEAD` 逐文件范围模式）progress 实测：

| batch | 文件 | session | 起止 | status | findings |
|---|---|---|---|---|---|
| T16A-b1 | app/config.py | c2ba5421 | 02:04:27-02:10:26 rc=0 359s | COMPLETED | 0 |
| T16A-b2 | app/environment_contract.py | a0dc89da | 02:10:26-02:11:32 rc=0 66s | COMPLETED | 0 |
| T16A-b3 | app/models.py | 4d608966 | 02:11:32-02:13:00 rc=0 88s | COMPLETED | 0 |
| T16A-b4 | app/scanner/backend.py | 978f308d | 02:13:00-02:14:21 rc=0 80s | COMPLETED | 0 |
| T16A-b5 | app/scanner/clients.py | d3bae32c | 02:14:21-02:17:19 rc=0 178s | COMPLETED | 1 [maintainability·medium]（:168-170 三新属性 scan_root/ready_root/storage_root 全仓零读取点，`_physical_path` 仍走全局 settings；预裁决=非 AC 违例，runner 侧 RootContext 正确驱动遍历/映射，随全批收口正式裁决） |
| T16A-b6 | app/scanner/paths.py | 25208f92 | 02:17:19-02:23:38 rc=0 378s | COMPLETED | 0 |
| T16A-b7 | app/scanner/runner.py | - | 02:23:38 START | INFLIGHT（r111 02:3x 核存活） | - |
| T16A-b7~b14 | runner/requests/bootstrap/ingest_service/scene_intake/source_service/迁移/compose | - | - | QUEUED | - |
| T16B-b1~b3 | orchestrator/proxy/fake_vlm | - | - | QUEUED（16A 后接） | - |

vllm 18002 低负载（3 running/0 waiting，02:2x 实测）；单批收口窗 1-6min 正常推进，无停滞告警。

## r111 进度回写（2026-10-13 02:3x，coord-poll 巡检）

16A **6/14 COMPLETED**（b6 paths 25208f92 rc=0 378s 0 findings）；b7 runner.py 02:23:38 START INFLIGHT（126/-30 最大 diff，单批窗 5-15min 正常）；b8~b14 排队；16B 3 批未起跑。pid 980094 存活（etime 32min+），无停滞告警。


## r111 排队登记（2026-10-13 02:4x，coord-poll 巡检）

- **07B R3 增量 OCR 排队**：B `attempt-3-r3` 02:37:53 交付冻结 REVIEW_PENDING（HEAD `4baf79f`，base `68b5188`，7 文件 +441/-15 零越界；机械核验已全绿=定向+r2+r3 12 passed 独立复跑 / ruff 绿 / alembic 单头 `20261012_01_scene_manual` / ancestor OK）→ R3 增量 OCR（`--from 68b5188 --to 4baf79f`，app 面 5 文件：service/models/web-bags/api/迁移；tests 排除）排在本 v2 16A/16B 全部批次收口后串行执行，flock 同一把 `inbox/ocr.lock`，不并行。
- v2 在途维持：pid 980094 存活，16A 6/14 COMPLETED（b7 runner.py 02:23:38 起 INFLIGHT，02:4x 核推进正常），16B 3 批排队；单批 >30min 无收口记活动停滞告警不无限重试。

## r112 进度回写 + b7 findings 裁决（2026-10-13 02:5x，coord-poll 巡检）

v2 实测：16A **10/14 COMPLETED**（b7 runner.py `f3f67787` rc=0 1400s **3 findings** / b8 requests `ba0d92a4` 0 / b9 bootstrap `e14e8f83` 0）；**b10 `app/services/ingest_service.py` 02:49:26 START INFLIGHT**（node pid 1042488 存活）；b11-b14 排队；16B 3 批未起跑。vllm 18002 running=1/waiting=0 低负载。pid 980094 存活（etime 47min+），无停滞告警。

### b7 runner.py 3 findings 协调者独立核（wt-01-t16a HEAD `c30f048` 代码实测）

| ID | 级别 | 口径 | 裁决 |
|---|---|---|---|
| 16A-R7-M1 | bug·medium（:256-265 一根故障隔离吞掉 legacy self_built 根致命异常，`python -m app.scanner` CLI 出口码从非零变 0） | `__main__.py` 为 base 既有未触碰文件（16A diff 零命中），CLI 错误契约不在 DESIGN §7.3.1 冻结范围、compose 实际链路 `scan_worker.py` 30 行有 `settings.validate()` 不受影响 | **OUT_OF_SCOPE，不返修不阻塞**，记 16A 合入备注 |
| 16A-R7-M2 | bug·medium（:63-65 `scene_roots_configured()` 任一非空即启用 → 部分配置走 CLI/手工路径时 `Settings.validate()` 不被调用，`_scene_context` 建空根 RootContext，scan 发 `path=""` ScanJob 每轮失败） | DESIGN §7.3.1 明确「配置无效 → 返回可恢复 `CONFIG_REQUIRED`/配置错误」；`config.py:139` 自身注释「半配置视为契约错误避免静默放行」与 `_scene_context` 放行口径自相矛盾；生产链路 fail closed 但契约面未封口 | **CORRECTION 待全收口合并返修**（最小修复=扫描入口改要求 `scene_nas_scan_root and scene_nas_ready_root`，2 行量级） |
| 16A-R7-L1 | maintainability·low（:179 journal `marker["root_id"]` 写入后零读取点，`_recover_moves` 用 `ctx.root_id` 不校验） | DESIGN §1.5 接线口径明列「身份透传原始 incoming 路径（**重启保持快照**）」=验收面；当前实现重启恢复身份通道无快照锚定 | **CORRECTION（最小）待全收口合并返修**（在 `_recover_moves` 恢复路径 cross-check `marker["root_id"]` vs `ctx.root_id`，矛盾记失败跳过不 KeyError，不删字段） |

### b5 clients.py medium（:168-170 三新属性零读取、`_physical_path` 仍走全局 `settings.nas_storage_root`）正式裁决

**维持非 AC 违例、LOW 非阻塞**：§7.3.1 契约=场景三根与旧 `NAS_*` 同 `NAS_STORAGE_ROOT` 存储根，`_physical_path` 全局值即正确物理根；遍历/映射由 runner RootContext 正确驱动（机械核验 25 passed 口径在案）。随 16A 合入备注，不返修。

### 返修批次合并政策（沿 07B r102 先例）

- 16A CORRECTION 级 = **M2 + L1（均限 `app/scanner/runner.py`）**，暂不回派——等 v2 16A b11-b14 + 16B b1-b3 全部收口后合并全部 findings 一次最小返修单派 A（避免移动 HEAD 干扰在途 `--to HEAD` 批次口径）。
- 07B R3 增量 OCR 仍排 v2 全部批次之后（`--from 68b5188 --to 4baf79f`，app 面 5 文件）。
- 16B findings 收口后同批裁决；16B 返修（若有）派 C 单独批次，不与 16A 混。


## r114 进度（2026-10-13 03:1x）

v2 实测：16A **11/14 COMPLETED**（b10 `ingest_service.py` `1879ae1e` rc=0 1337s **1 low**：`list_profiles` 未传 root_id 致 scene 入口不出现在 `GET /api/v1/ingest-profiles`，预裁决待全收口合并）；**b11 `scene_intake.py`（+90）03:11:43 START INFLIGHT**；b12-b14 排队、16B 3 批未起跑。v2 父进程 pid 980094 存活持 `ocr.lock`，无停滞告警。

## r115 进度 + b11 findings 核（2026-10-13 03:2x，coord-poll 巡检）

v2 实测：16A **12/14 COMPLETED**——**b11 `app/services/scene_intake.py`（+90 新增）`85330380` rc=0 609s 2 findings（均 low）**；**b12 `app/services/source_service.py` 03:21:52 START INFLIGHT**（node pid 1085908 存活）；b13 `alembic/versions/20261013_01_scene_intake.py` / b14 `compose.yaml` 排队；16B 3 批未起跑。v2 父进程 pid 980094 存活持 `ocr.lock`，vllm 低负载，无停滞告警。

### b11 scene_intake.py 2 findings 协调者独立核（wt-01-t16a HEAD `c30f048`，log 复读）

| ID | 级别 | 口径 | 裁决 |
|---|---|---|---|
| 16A-R11-L1 | maintainability·low（:42-46 `incoming_path` 参数接受但函数内零读取，docstring 声明 root 派生位置限定=刻意 API 面供 `source_service.register_source` 调用点清晰） | 属刻意接口面非 bug；OCR 自述"考虑删签名或 docstring 注明 reserved" | **LOW 非阻塞**，随全收口合并裁决（若判 CORRECTION 仅 docstring 补一句 reserved 口径，量级极小，不单独返修不阻塞） |
| 16A-R11-L2 | style·low（:84-90 文件缺尾换行） | 机械卫生项 | **LOW 非阻塞**，随 16A 合并最小返修 commit 顺手补，不单独起单 |

**返修合并政策（续 r112）**：16A CORRECTION 级仍=M2+L1（均限 `runner.py`）+ b10 L1（`ingest_service` list_profiles，待核）；b11 两条 low 并入随同 commit，均不单独返修。等 v2 16A b12-b14 + 16B b1-b3 全部收口后一次最小返修单派 A。07B R3 增量 OCR 仍排 v2 全部批次之后串行（`--from 68b5188 --to 4baf79f`，app 面 5 文件）。16A 合入门禁维持关闭。

## r116 进度（2026-10-13 03:3x，coord-poll 巡检）

v2 实测：16A **13/14 COMPLETED**——**b12 `app/services/source_service.py` `3f9c835e` rc=0 774s 0 findings**（零 CORRECTION 级）；**b13 `alembic/versions/20261013_01_scene_intake.py`（+74 迁移）03:34:47 START INFLIGHT**；b14 `compose.yaml` 排队；16B 3 批未起跑。v2 父进程 pid 980094 存活持 `ocr.lock`，无停滞告警。

### b12 0 findings（无新裁决）

`source_service.py` +18/-1 零 findings；16A 待合并返修面不变（r112 M2+L1 限 `runner.py` + b10 L1 `ingest_service` list_profiles + b11 两 low），等 b13 迁移 + b14 compose + 16B b1-b3 全收口后一次最小返修单派 A。16A 合入门禁维持关闭。07B R3 增量 OCR（`--from 68b5188 --to 4baf79f`）仍排 v2 全部批次之后串行。

### r116b 补记：b10 list_profiles 正式裁决（2026-10-13 03:4x，coord-poll r116）

- DESIGN.md:157 明列 `GET /api/v1/ingest-profiles` 返回字段含 **`intake_root_id`**——契约面已按 v0.4 扩展，列表隐藏 scene 行与字段承诺自相矛盾（可 submit 到列表不可见的入口=运维面缺口）。
- **裁决=CORRECTION（low 级）并入 16A 最小返修单**：`list_profiles` 不再默认 self_built 过滤（或显式传 all-roots 口径），匹配路径 `_active_profiles(db, root_id)` 跨根隔离语义不动。
- 16A 待合并返修面更新（全部随一次最小返修单派 A）：runner.py M2（`_scene_context` 改要求 `scene_nas_scan_root and scene_nas_ready_root`）+ runner.py L1（`_recover_moves` cross-check `marker["root_id"]` vs `ctx.root_id`，矛盾记失败跳过）+ ingest_service.py L1（list_profiles 场景入口可见）+ scene_intake.py 尾换行 + 迁移尾换行 + R11-L1 docstring reserved 注（顺手）。clients.py medium 维持非 AC 违例随合入备注；R7-M1 OUT_OF_SCOPE 不返修。

### r116b 进度回写（2026-10-13 03:4x，coord-poll r116）

- v2 实测：16A **14/14 COMPLETED**（b13 迁移 `145c8b92` rc=0 372s **1 low**=尾换行；b14 compose.yaml `cb64c7f1` rc=0 49s 0 findings）→ **16A 面全收口，零 high/critical**；**b16B-1 `scripts/scene_host_orchestrator.py`（583 行 `--max-tokens 30000`）03:41:50 START INFLIGHT**（node pid 1110481 存活）；b16B-2 proxy / b16B-3 fake_vlm_server 排队。父进程 pid 980094 存活持 `ocr.lock`，单批窗 5-40min 内无停滞告警。
- 16A 合入门禁：OCR 面收口→剩**一次最小返修单（上述 6 项）派 A → 增量 OCR → 合入（07B 整链先合入后 16A 迁移 rebase 双头，裁决维持 r107）**。
- 07B R3 增量 OCR（`--from 68b5188 --to 4baf79f`，app 面 5 文件）仍排 v2 剩余批次（16B 3 批）收口后串行。


## r118 进度回写 + 16B-b1 首跑失败记账（2026-10-13 04:1x，coord-poll 巡检）

- v2 实测：16A 14/14 维持全收口（零 high/critical）；**T16B-b1 `scripts/scene_host_orchestrator.py` 03:41:50-04:05:50 rc=1（1440s，session `235dac12-4fe3-4f48-87ff-fe64b07cde5b`）**——log 实测「Review planning: timed out -> failed」+「Context compaction: timed out + 3 cancelled」+「LLM retry report: 5 of 22 requests affected, 2 failed 3 cancelled」=**外部 LLM 队列超时/取消，非工具缺陷、非 diff 问题**；usage 325489 input+43606 output，budget_exceeded=false。**关键：log 末行给出 `retry with: --resume 235dac12-4fe3-4f48-87ff-fe64b07cde5b` = run manifest 在案可 resume（区别于 D3-r1 被杀无 manifest 例外，按 §4 口径允许断点续审）**。
- **T16B-b2 `scripts/scene_host_proxy.py`（968 行 `--max-tokens 30000`）04:05:50 START INFLIGHT**（node pid 1142402 存活，04:10 核 log 0 字节属首文件在途正常）；T16B-b3 `tests/fake_vlm_server.py` 排队；v2 父进程 pid 980094 存活持 `ocr.lock`。
- **16B-b1 重试政策落账（不无限重试）**：v2 runner（pid 980094）循环无 resume 能力，b1 不会自续——**b1 补跑=独立 detached 单批 `--resume 235dac12-…`**（flock 同一把 `ocr.lock`，须待 v2 全链 done 标记释放锁后起跑，不与在途 v2 争锁）；若 resume 收口再失败=挂 NEEDS_REVIEW 冻结 16B 合入门禁（16A 门禁不受牵连）。
- 16A 合入门禁/返修政策不变（6 项最小返修单等 v2 全收口后派 A）；07B R3 增量 OCR 仍排 v2 全部批次+16B-b1 resume 补跑收口后串行。

## r119 进度回写 + 16A attempt-2-r1 交付核验（2026-10-13 04:1x，coord-poll r119 巡检）

- v2 实测：16A 14/14 维持全收口（零 high/critical）；T16B-b1 rc=1 记账不变（resume 政策在案）；**T16B-b2 `scripts/scene_host_proxy.py`（968 行）04:05:50 起 INFLIGHT**（node pid 1142402 04:16 核存活 ~10min，log 0 字节首文件在途正常，窗 10-40min 不告警）；b3 fake_vlm 排队；父进程 pid 980094 存活持 `ocr.lock`。vllm 18002 running=1/waiting=0 低负载（b1 失败=请求级 LLM 队列超时，非饱和单因）。
- **新事实=16A attempt-2-r1 最小返修交付已落（A 04:09，`receipts/TASK-16A/attempt-2-r1.md`，ACK 04:00:49）——r116 03:48 派单（`inbox/1号/TASK-16A/attempt-2-r1-dispatch.md`）A 已 11 分钟收口**：base `c30f048` 续 commit 1 笔 HEAD `3aee4d1`，5 文件 +122/-7（runner/ingest_service/scene_intake/迁移/隔离测试），零越界（clients.py 未碰、07B 冻结零触碰、`scene_roots_configured` 保留）。
- **协调者独立机械核验（04:1x，非复述回执）**：`wt-01-t16a` rev-parse HEAD=`3aee4d1`+`merge-base --is-ancestor c30f048 HEAD`=BASE_OK+porcelain 干净（仅 .venv）；diff --stat 与回执逐文件一致；定向四组 **56 passed RC=0**（test_scene_intake_isolation 22 含新增 3 / test_scanner_stability 6 / test_ingest_config_api+ingest_config 28，协调者独立复跑）；ruff 4 变更文件 **All checks passed**；R1-1 双根 fail-closed / R1-2 ROOT_MISMATCH 兼容放行+矛盾跳过+字段保留 / R1-3 `__all__` 哨兵 list 专用+匹配路径隔离不动 / R1-4 reserved docstring+尾换行 / R1-5 迁移纯尾换行 五点代码 diff 逐行核与 AC 一致。全量 872/3failed=3 条 test_devflow 环境性（A stash 复跑 base 同口径在案，非回归）。
- **16A 增量 OCR 排队（§3.6 尺寸预检）**：`--from c30f048 --to 3aee4d1` app 面 3 文件（runner.py +24 / ingest_service.py +12 / scene_intake.py +6 均小增量）+ 迁移纯尾换行 0 入选 + 测试 0 入选=**3 批，每文件 <50 行无需 max-tokens 拆组**；串行排 v2 剩余批次（T16B-b2 proxy 在途 + b3 fake_vlm）+ 16B-b1 `--resume 235dac12-…` 补跑之后；07B R3 增量 OCR（`--from 68b5188 --to 4baf79f`）仍排全部 16A/16B 批次之后。
- **16A 合入门禁维持关闭**：待 16A 增量 OCR 收口 + 必要 TESTER 独立验证 + 07B 整链先合入（r107 顺序裁决不变，16A 迁移 rebase 双头随合入面执行）。

## r120 进度回写 + 16B-b2 失败记账（2026-10-13 04:3x，coord-poll r120 巡检）

- v2 实测：16A 14/14 维持全收口（零 high/critical）；T16B-b1 rc=1 记账不变（`--resume 235dac12-…` 政策在案）；**T16B-b2 `scripts/scene_host_proxy.py`（968 行 `--max-tokens 30000`）04:05:50-04:29:50 rc=1（1440s，session `e2b8a607-b24c-4f82-a6bb-31bb79b36fd2`）**——log 独立复读「timed out -> failed」+「LLM retry 2 of 34 affected」+「Context compaction 1 cancelled」，usage 607831 tokens/34 工具调用/budget_exceeded=false=**外部 LLM 队列超时非工具问题**；末行 `retry with: --resume e2b8a607-…`=**manifest 在案可断点续审**。
- **T16B-b3 `tests/fake_vlm_server.py` 04:29:50 START INFLIGHT**（node pid 1175002 04:3x 核存活，小文件预计短收口）；v2 父进程 pid 980094 存活持 `ocr.lock`，**b3 收口即 v2 全链 done**。
- **resume 补跑链（b3 收口+v2 done 释放锁后，独立 detached 串行，各最后一次）**：b1 `--resume 235dac12-4fe3-4f48-87ff-fe64b07cde5b`（583 行 `--max-tokens 30000`）→ b2 `--resume e2b8a607-b24c-4f82-a6bb-31bb79b36fd2`（968 行 `--max-tokens 30000`）→ 再失败挂 NEEDS_REVIEW 冻结 16B 合入门禁（16A 不受牵连）→ 16A 增量 3 批（`--from c30f048 --to 3aee4d1`）→ 07B R3 增量 5 批（`--from 68b5188 --to 4baf79f`）。大文件双超时形态记录在案：若 resume 再超时改单文件拆组（§3.6）。
- 16A 合入门禁/返修政策不变（交付冻结 `3aee4d1` 已核，增量 OCR 排队）；16B 门禁维持关闭（OCR 未全收口）。

## r121 进度回写 + v2 全链 done + resume 链起跑（2026-10-13 04:4x，coord-poll r121 巡检）

- v2 实测收口：**T16B-b3 `tests/fake_vlm_server.py` 04:29:50-04:39:44 rc=0 dur=593s（session `277f12d4`，~229534 tokens）**=2 findings：① `[bug·medium]` :85-87 泄漏检查扫整个 raw body，base64 图像段碰巧含 base64 字母表字符（`nas`/`rosbag`/`/public/`/`/test/scene`）→ `leak_bodies` 误填、`request_has_only_frames_and_params()` 误返 False（现测试未暴露=夹具帧极小）；② `[maintainability·low]` :33 编译正则零引用死代码。**预裁决=b3 属 16B 测试基建非业务面，medium=测试 harness 潜在假阴性，并入 resume 收口后 16B findings 合并裁决，不单独返修不阻塞 b1/b2 app 面**（C 侧确认后如需硬化随 16B 收口单）。
- **v2 全链 done（04:39:44 progress 落 `== t16 ocr v2 done ==`，pid 980094 ps 核退出，`ocr.lock` fuser 无持有=锁释放）**：16A 14/14（零 high/critical）+ 16B b1/b2 rc=1（manifest 在案）+ b3 rc=0。**resume 链起跑条件满足**。
- **r120 既定 resume 链已起跑（04:48:15，独立 detached，各最后一次，同锁 flock `ocr.lock`）**：b1 `--resume 235dac12-…`（583 行 `--max-tokens 30000`）→ b2 `--resume e2b8a607-…`（968 行 `--max-tokens 30000`）。脚本 `scratch/run_t16b_resume.py`+launcher `scratch/r121_resume_launch.py`（Popen `start_new_session=True`，镜像 r107_v2 已验证存活机制；`setsid` 被 terminal 守卫拦）。**pid 1198826 持 ocr.lock，node 1198828→opencodereview 1198836 在途**（ps 核存活，b1 0 字节日志首审正常）；进度 `t16_ocr/t16b_resume_progress.txt`+`resume_chain.out`。起跑前 vllm running=3/waiting=0 无饱和实测。
- **后续串行队列（resume 收口后同锁）**：16A 增量 OCR 3 批（`--from c30f048 --to 3aee4d1`）→ 07B R3 增量 OCR 5 批（`--from 68b5188 --to 4baf79f`）；两增量均无 CORRECTION 级才各解放入门禁。
- **收口裁决政策（不无限重试）**：resume b1/b2 各最后一次；仍 rc=1（LLM 队列超时）→ 按 §3.6 改单文件拆组重试 1 次→ 再失败挂 NEEDS_REVIEW 冻结 16B 合入门禁（16A 不受牵连）。16B 门禁维持关闭（b1/b2 resume 未收口）；16A 门禁维持关闭（增量 OCR+TESTER+07B 先合入 rebase 双头）。

## r123 进度回写 + 16B-b1 resume 收口裁决（2026-10-13 05:1x，coord-poll r123 巡检）

- **T16B-b1 resume `235dac12-…` 收口 rc=0**（04:48:15-05:12:15，dur=1440s，**新 session `b3cbc43f-cc1e-49af-b5c6-fd01a9c66523`**，usage input ~415108/output ~77548 ≈492656 tokens，1 文件）：**3 findings（1 high + 2 medium）**，均 `scripts/scene_host_orchestrator.py`：
  - **H1 (:259-264) 协调者独立核代码属实=CONFIRMED CORRECTION**：成功路径 `stamp("EXTRACT")` 先于 `self._last_manifest = manifest`（:287）执行，`_write_checkpoint`（:554 仅 `_last_manifest is not None` 才落 manifest）→ EXTRACT checkpoint 无 manifest；`_read_checkpoint`（:564-578）要求三步全 DONE **且** manifest 可重建才认定分析完成 → WRITE/VALIDATE/PUBLISH 期间崩溃恢复落 else 分支**重跑 dispatch 重复计费模型**，违反 §8.3「崩溃恢复/幂等复用」文档化保证。修复方向=manifest 赋值提前至 `stamp("EXTRACT")` 前（H2 同单）。
  - **M1 (:266-272) CONFIRMED CORRECTION**：`fail()` 内部 `_write_checkpoint`+raise → 循环后 `build_manifest`/`self._last_manifest = manifest`/二次写 checkpoint/`raise SceneExecError` 全不可达=死代码；FAILED checkpoint 亦缺 manifest（恢复面同 H1 族）。修复=先 build+赋值 manifest 再 `fail(...)`，删不可达行（与 H1 同一次最小返修）。
  - **M2 (:243-247) CONFIRMED CORRECTION**：成功路径先 `ledger[name].status="DONE"` 再 `stamp()`，`stamp`（:184-190 `if rec.status != "DONE"`）跳过 evidence 更新 → EXTRACT 的 outcome/frame_log/duration_s 不落 checkpoint，审计证据缺口。修复=stamp 允许 DONE 态 evidence 合并或显式补写。
  - round 2 出现「Core review timed out -> failed」但 overall `Review complete: 3 finding(s)` rc=0：round 1 核心审查已产出 3 findings（log 全文在案可独立核），round 2 为复验轮 LLM 队列超时；**收口有效性=round 1 findings 完整落盘+独立核属实**，不计 NEEDS_REVIEW（区别于 b1 首跑 rc=1 无产出形态）；1440s=dur 上限内收口。
- **T16B-b2 resume `e2b8a607-…` 05:12:15 START INFLIGHT**（node pid 1229080 存活，`resume_b2-proxy.log` 0 字节首审正常）；b1 首跑 1440s 口径 → b2 窗 5-24min 不告警不 reap 不重启；父进程 pid 1198826 存活持 `ocr.lock`。
- **16B findings 合并裁决进度**：b1 resume 3 findings（H1/M1/M2 全 CONFIRMED）+ b3 2 findings（medium 测试基建泄漏误报+low 死代码，r121 预裁决并入）→ 待 b2 收口后合并**一次最小返修单派 C**（base `0208a73` 续 commit，限 `scripts/scene_host_orchestrator.py` H1/M1/M2 + b3 侧随 C 确认口径）→ 交付冻结→机械核验→增量 OCR→强审查 pack（授权在案期限内）→合入→16B DONE（real 栈全链冒烟留 16D 前口径不变）。
- **后续串行队列（同锁，不变）**：16A 增量 OCR 3 批（`--from c30f048 --to 3aee4d1`）→ 07B R3 增量 OCR 5 批（`--from 68b5188 --to 4baf79f`）。
- 门禁：16B 合入门禁维持关闭（b2 resume 未收口+findings 未返修）；16A 合入门禁维持关闭（增量 OCR+TESTER+07B 先合入 rebase 双头）；角色占用 A=16A 交付冻结 `3aee4d1`、B=07B R3 交付冻结 `4baf79f`、C=16B 交付冻结（等 b2+返修单）、TESTER 空闲。main `c2018dd` / origin `502bf8e` 零 app 面漂移；wt-01-t16a `3aee4d1` / wt-04a-t07b `4baf79f` / wt-03b-t16b `0208a73` 未合入。

## r125 巡检段（2026-10-13 05:42:34，preflight 2026-10-13T05:35:53+08:00）

- **resume 链收口（05:36:15 done）**：b1-orchestrator resume `235dac12` **rc=0 dur=1440s**（04:48:15-05:12:15，新 session `b3cbc43f-cc1e-49af-b5c6-fd01a9c66523`，**3 findings**=H1 EXTRACT stamp 先于 manifest 赋值崩溃恢复重复计费 / M1 fail() 死代码+FAILED checkpoint 缺 manifest / M2 DONE 前置跳过 evidence 审计缺口，协调者 r123 已独立核全 CONFIRMED，裁决明细见 r123 段）；b2-proxy resume `e2b8a607` **rc=1 dur=1440s**（05:12:15-05:36:15，新 session `10b08d5e-2903-473f-a712-2926dee449ac`，0 findings、1/1 failed、LLM retry 4 of 21 affected 2 failed 2 cancelled，usage 411417 tokens/budget_exceeded=false=**外部 LLM 队列超时再复现**，末行 `retry with: --resume 10b08d5e-…` manifest 在案但 resume 已两次同因超时且无已审成果可续）。
- **b2 拆组重试起跑（r118 落账政策第 1 次拆组）**：proxy 968 行 fresh 起跑（不 resume，理由=两次 LLM 队列超时均为整组 planning/core 请求级失败，无已完成组可续），`--max-tokens 30000→20000` 拆更细组降单请求超时概率，`--timeout 12`，独立 detached pid **1266766**（05:40:34 START，持 `ocr.lock` fuser 独立核，launcher `r125_b2_split_launch.py` 镜像 r121 已验证 Popen start_new_session 机制）；进度 `~/.hermes/cache/scratch/t16_ocr/b2_split_progress.txt`+`b2_split.log`，结果 `b2_split_results.json`；起跑前 vllm 18002 running=3/waiting=0 低负载实测。**硬截止口径 06:00-06:20（968 行/20000 拆组参照 b1 583 行/30000=1440s）**；到点无 DONE 行核 session 活跃度后裁决。
- **政策落账（不无限重试）**：b2 拆组 rc=0 → 16B findings 全合并裁决（b1 3 + b3 2 + 拆组结果）→ 一次最小返修单派 C；b2 拆组再 rc=1 → **挂 NEEDS_REVIEW 冻结 16B 合入门禁**（16A 不受牵连，16A 增量 OCR 3 批可接锁后继续）。
- 后续串行队列不变：16A 增量 3 批（`--from c30f048 --to 3aee4d1`）→ 07B R3 增量 5 批（`--from 68b5188 --to 4baf79f`）→ R3 强审增量复审 → TESTER 07B-post-r3 → 07B 合入（先于 16A）→ 16A/16B 收口 → 07B DONE → 派 07C/16C。

## r126 巡检段（2026-10-13 05:53，preflight 2026-10-13T05:45:53+08:00）

- **T16B-b2 proxy 拆组重试 rc=1（第 3 次失败，05:40:34-05:46:11 dur=336s）**：session `2abf70dd-4c8a-4470-9dce-35aa32bb8d2c`，`--max-tokens 20000` fresh 起跑（不 resume），log 实测「LLM retry 2 of 9 requests affected, 2 cancelled」+「Context compaction 2 cancelled」，usage 92229 input+18289 output=110518 tokens/budget_exceeded=false=**外部 LLM 队列超时第 3 次复现**（vllm 18002 running=2/waiting=0 低负载，非容量饱和）。3 次失败形态一致（1440s/1440s/336s），均无已审成果。**16B proxy OCR = NEEDS_REVIEW，16B 合入门禁冻结**（r125 既定政策分支）。
- **16A 增量 OCR 已起跑（本侧控制动作）**：b2 退出释放 `ocr.lock` 后，`run_t16a_incr_ocr.py` detached **pid 1284380**（05:53:47 START，flock 持 `ocr.lock`），`--from c30f048 --to 3aee4d1` 逐文件 3 批（a-runner `app/scanner/runner.py` +24 / a-ingest `app/services/ingest_service.py` +12 / a-scene `app/services/scene_intake.py` +6，均 <50 行无需 max-tokens 拆组）；迁移纯尾换行 0 入选、tests 排除。进度 `t16_ocr/t16a_incr_progress.txt`+`t16a_incr_results.json`，每批 log `t16a_incr_<label>.log`。a-runner 批 INFLIGHT。
- **16B 收口路径变更（NEEDS_REVIEW 分支）**：proxy OCR 3 次 LLM 队列超时→**16B 合入门禁冻结**；orchestrator 3 findings（H1/M1/M2 CONFIRMED CORRECTION，r123 段）+ b3 2 findings（r121 段）已裁决但**返修单暂缓**（16B 冻结，等 proxy OCR 解除后一次最小返修单派 C）。16B 解除条件=proxy OCR 成功收口（低负载期重试或用户裁决）。
- **后续串行队列更新**：16A 增量 3 批 INFLIGHT（pid 1284380）→ 07B R3 增量 OCR 6 批（`--from 68b5188 --to 4baf79f`，wt-04a-t07b，app 面 6 文件：迁移+api+models+service+detail.html+web/bags.py）→ R3 强审增量复审（授权期限内）→ TESTER 07B-post-r3 → 07B 合入（先于 16A）→ 16A 收口合入 → 16B proxy OCR 重试/裁决 → 16B 收口 → 07B/16A DONE → 派 07C/16C。
- **门禁**：16B 合入门禁**冻结（NEEDS_REVIEW）**；16A 合入门禁维持关闭（增量 OCR INFLIGHT+TESTER+07B 先合入 rebase 双头）；07B 合入门禁维持关闭（R3 增量 OCR 排队）。角色占用：A=16A 交付冻结 `3aee4d1`、B=07B R3 交付冻结 `4baf79f`、C=16B 交付冻结（16B NEEDS_REVIEW 冻结）、TESTER 空闲。main `c2018dd` / origin `502bf8e` 零 app 面漂移。

## r127 巡检段（2026-10-13 06:11，preflight 2026-10-13T06:05:53+08:00）

- **16A 增量 OCR 3/3 全收口 0 findings（r126 起跑 pid 1284380，05:53:47→06:00:46 done）**：a-runner `app/scanner/runner.py` rc=0 206s 0 findings session `bcc16c30` / a-ingest `app/services/ingest_service.py` rc=0 113s 0 session `9c05e27a` / a-scene `app/services/scene_intake.py` rc=0 98s 0 session `29fff84d`（`t16a_incr_progress.txt` 独立复读，C 05:53 事件同核）。**16A 侧 OCR 面全闭环（v2 14/14 + 增量 3/3 均零 CORRECTION 级）**；16A 合入门禁剩余=TESTER 独立验证 + 07B 整链先合入后迁移 rebase 双头。
- **07B R3 增量 OCR 起跑（本轮控制动作，pid 1307769，06:11:21 START）**：`--from 68b5188 --to 4baf79f` app 面 6 文件逐文件单批（§3.6 预检均 <100 行 diff 无需 max-tokens 拆组）：r3-1 迁移 `alembic/versions/20261012_01_scene_manual.py` +26 / r3-2 `app/api/scene_manual_revision.py` +7 / r3-3 `app/models.py` +8 / r3-4 `app/services/scene_manual_revision_service.py` +64 / r3-5 `app/templates/detail.html` +3 / r3-6 `app/web/bags.py` +6（tests 排除）。脚本 `~/.hermes/cache/scratch/run_t07b_r3_incr_ocr.py`，detached `start_new_session`，flock 持 `ocr.lock`（16A 增量 done 释放后接锁，起跑前 vllm 18002 running=3/waiting=0 低负载实测）。进度 `~/.hermes/cache/scratch/t07b_r3_ocr/r3_incr_progress.txt`，结果 `r3_incr_results.json`。
- **收口裁决政策（不无限重试）**：R3 增量 6 批全 rc=0 且零 CORRECTION 级 → 强审增量复审 pack（授权期限内，只看 R3-1~4，预期 2/5）→ TESTER 07B-post-r3 派单 → 07B 合入（先于 16A rebase 双头）；任一批出现 CORRECTION 级 → 分类裁决（CORRECTION 回派 B 最小返修 / VERIFICATION_GAP 派 TESTER / OUT_OF_SCOPE 不阻塞）；LLM 队列超时（rc=1）→ 单批 resume 最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁（16A 不受牵连）。
- **16B 维持 NEEDS_REVIEW 冻结（r126 口径不变）**：proxy OCR 3 次外部 LLM 队列超时（1440s/1440s/336s，非容量饱和），orchestrator 3 findings（H1/M1/M2 CONFIRMED）+ b3 2 findings 已裁决但返修单暂缓，等 proxy OCR 低负载期重试或用户裁决后一次最小返修单派 C。
- **门禁/角色占用**：07B 合入门禁维持关闭（R3 增量 OCR INFLIGHT）；16A 合入门禁维持关闭（OCR 已闭环，剩 TESTER + 07B 先合入 rebase）；16B 合入门禁**冻结（NEEDS_REVIEW）**。A=16A 交付冻结 `3aee4d1`（OCR 面已闭环）、B=07B R3 交付冻结 `4baf79f`（等增量 OCR/强审/TESTER）、C=16B 交付冻结（NEEDS_REVIEW）、TESTER 空闲（07B-post-r3 单待 R3 OCR 收口后派）。main `c2018dd` / origin `502bf8e` 零 app 面漂移；`3aee4d1`/`4baf79f`/`0208a73` 均未合入。
- **强审查（strong_review.py status 本轮只读实测 06:11）**：AUTHORIZED grant `31dcbabe…`（用户 24h 授权 2026-10-12 11:33），绝对期限 **2026-10-13 11:33:12**（剩约 5h22min），滚动 60 分钟 **0/5**、本授权累计 **1 次**、在途 0、最近结果=07B R2 `50c665e4…` SUCCEEDED REWORK_REQUIRED（in 656176/cached 569728/out 9229+reasoning 4355，费用 null=未知）。R3 增量复审待 R3 增量 OCR 零 CORRECTION 级后 pack（预期 2/5）。

## r128 巡检段（2026-10-13 06:20，preflight 2026-10-13T06:20:53+08:00）

- **07B R3 增量 OCR 2/6 收口（pid 1307769 存活实测，progress 复读）**：r3-1 迁移 `20261012_01_scene_manual.py` rc=0 599s session `01543c81` **2 findings（1 medium + 1 low）**；r3-2 `app/api/scene_manual_revision.py` rc=0 30s session `597f95d4` **0 findings**；r3-3 `app/models.py` INFLIGHT（06:21:52 START）；r3-4/5/6 QUEUED。
- **r3-1 medium 初判 CORRECTION（待全收口后正式裁决）**：downgrade 中 `sa.inspect(bind).get_columns(TABLE)` 对 `scene_manual_revision` 未做表存在守卫（下一行 evidence 表却用了 has_table 守卫），表不存在时 downgrade 抛异常中断（SQLite NoReferencedTableError / MySQL 1146），与兄弟迁移 `20261009_02` 的守卫口径不一致；建议补 `if TABLE in get_table_names()` 守卫。low=downgrade drop_column(`corrected_label`) 与 20261009_02 同型往返数据丢失风险未同步 docstring 说明（documentation 级）。
- **政策沿用 r127**：6 批全收口后，medium 按 CORRECTION 回派 B 最小返修（与剩余批 findings 合并一次返修单）或按证据改判；llm 超时（rc=1）单批 resume 最后一次再挂 NEEDS_REVIEW。
- **门禁/角色占用**：07B 合入门禁维持关闭（R3 增量 OCR INFLIGHT 且已现 CORRECTION 级）；16A 合入门禁维持关闭（剩 TESTER + 07B 先合入 rebase 双头）；16B 合入门禁**冻结（NEEDS_REVIEW）**。A=16A 交付冻结 `3aee4d1`、B=07B R3 交付冻结 `4baf79f`（OCR 面已现待裁决 medium，不催 B）、C=16B 交付冻结（NEEDS_REVIEW）、TESTER 空闲。main `c2018dd` / origin `502bf8e` 零 app 面漂移；`3aee4d1`/`4baf79f`/`0208a73` 均未合入。
- **强审查（只读口径沿 r127 06:11 实测）**：grant `31dcbabe…` 绝对期限 **2026-10-13 11:33:12**，滚动 60 分钟 0/5、本授权累计 1 次、在途 0、最近=07B R2 `50c665e4…` REWORK_REQUIRED（费用未知）；R3 增量复审 pack 待 6 批全收口+裁决后生成。

## r129 巡检段（2026-10-13 06:3x，preflight 2026-10-13T06:30:53+08:00）

- **07B R3 增量 OCR 3/6 收口（pid 1307769 存活实测）**：r3-3 `app/models.py` DONE rc=0 50s 0 findings session `e98625e8`；r3-4 `app/services/scene_manual_revision_service.py`（+64，R3 最大增量 diff）06:22:42 START INFLIGHT（node pid 1322702，日志 0 字节=缓冲未落盘，单批窗内无停滞）；r3-5/r3-6 QUEUED。
- **裁决口径维持 r128**：r3-1 medium（迁移 downgrade 缺表存在守卫）待 6 批全收口合并正式裁决；维持 CORRECTION → 与剩余批 findings 合并一次最小返修单派 B；rc=1 → 单批 resume 最后一次再挂 NEEDS_REVIEW 冻结 07B 合入门禁（16A 不受牵连）。
- **后续串行队列（不变）**：R3 增量 6 批 → 07B R3 强审增量复审（授权期限 2026-10-13 11:33:12，预期 2/5）→ TESTER 07B-post-r3（SR-05 真 MySQL 双连接口径）→ 07B 合入（先于 16A rebase 双头）→ 16A 收口合入 → 16B proxy OCR 低负载重试/用户裁决 → 16B 收口 → 07B DONE → 派 07C/16C。

## r130 巡检段（2026-10-13 06:54:26，preflight 2026-10-13T06:40:53+08:00）

- **07B R3 增量 OCR 6/6 全收口（pid 1307769 已退出核）**：r3-1 迁移 rc=0 599s 2 findings（session `01543c81`）/ r3-2 api rc=0 30s 0（`597f95d4`）/ r3-3 models rc=0 50s 0（`e98625e8`）/ r3-4 service rc=0 716s 0（`c34888d8`，R3 最大增量 diff +64）/ r3-5 detail.html rc=0 123s 0（`33846cc9`）/ r3-6 web/bags.py rc=0 51s 0（`fe2a27c7`）。`t07b_r3_ocr/r3_incr_results.json` 独立复读。
- **r3-1 2 findings 正式裁决（协调者独立核 `4baf79f` 代码 + `68b5188..4baf79f` 迁移 diff）**：**R4-1 medium=CORRECTION**——原 downgrade `if TABLE in get_table_names(): drop_table` 表缺失 no-op 安全，R3 把 `drop_column("corrected_label")` 前置为无条件调用，表缺失时抛 NoReferencedTableError/1146，**违反该迁移自述「部分应用重入安全」+ R3 派单 §三真 MySQL downgrade 往返口径**；最小修复=drop_column 移回表存在守卫内。**R4-2 low=documentation 随同**——evidence 表 drop_column 往返数据丢失风险未同步 docstring（20261009_02 先例口径）。
- **R4 最小返修单已派 B**（`inbox/2号/TASK-07B/attempt-4-r4-dispatch.md`，base `4baf79f` 续 commit，仅迁移单文件 2 项）→ 交付后机械核验 → R4 增量 OCR（单批）→ **强审增量复审范围扩大为 R3-1~4+R4-1/2（授权期限内，冻结原 AC）** → TESTER post-r 单（target=R4 收口后固定 HEAD）→ 07B 合入（先于 16A rebase 双头）→ 07B DONE。
- **16A 侧 OCR 面维持全闭环**（v2 14/14 + 增量 3/3 零 CORRECTION 级，r127 口径）；16A 合入门禁剩余=TESTER 独立验证 + 07B 先合入 rebase 双头不变。
- **16B 维持 NEEDS_REVIEW 冻结**（proxy OCR 3 次外部 LLM 队列超时 r126 口径不变；orchestrator 3+b3 2 findings 返修单仍暂缓）。
- **门禁/角色占用**：07B 合入门禁维持关闭（R4 返修在途，等 ACK）；16A 合入门禁维持关闭；16B 合入门禁**冻结（NEEDS_REVIEW）**。A=16A 交付冻结 `3aee4d1`（OCR 面已闭环）、B=07B R4 返修 PENDING 待 ACK、C=16B 交付冻结（NEEDS_REVIEW）、TESTER 空闲（post-r 单待 R4 收口+强审+target 固定后派）。main `c2018dd` / origin `502bf8e` 零 app 面漂移（本轮 rev-parse 独立核）。
- **强审查（strong_review.py status 本轮只读实测 06:54）**：AUTHORIZED grant `31dcbabe…` 绝对期限 **2026-10-13 11:33:12**（剩约 4h50min），滚动 60 分钟 **0/5**、本授权累计 **1 次**、在途 0、最近=07B R2 `50c665e4…` SUCCEEDED REWORK_REQUIRED（in 656176/cached 569728/out 9229+reasoning 4355，费用 null=未知）。R4 增量复审待 R4 交付+增量 OCR 后 pack（预期 2/5）。

## r137（2026-10-13 08:5x）16B proxy OCR retry #4 收口 rc=1 → 升级用户裁决

- `b2-proxy R136-RETRY`（fresh，`--from c2018dd --to HEAD` 排除 orchestrator+tests，仅 `scene_host_proxy.py` 968 行单批，`--max-tokens 20000 --timeout 12`）：08:40:28 START（pid 1516687/node 1516689，flock `inbox/ocr.lock`，起跑前 vllm 18002 running=4/waiting=0 实测）→ 08:52:28 **DONE rc=1 dur=720s**，session `7a3f2d35-84c1-41a9-9196-690826ca41b7`「Review failed: 0 finding(s); 1 of 1 selected item(s) failed」，usage 98593 input+32496 output（9 tool calls，budget_exceeded=false），报错「check your LLM configuration and API key」=外部 LLM 队列/配置面失败，非 token 预算、非容量饱和。
- 连败链累计：**4/4 rc=1**（首跑 1440s/resume 1440s/拆组 336s/retry#4 720s）→ 达成 r126 落账政策（retry #4 rc=1=NEEDS_REVIEW 维持冻结升级用户裁决，不自动第 5 次重试）。progress/log/results.json 独立复读；node 进程已退出、锁无在途持有（ps 核）。
- 16B 后续待用户裁决选项：a) 择低负载再试一次 b) 换审查方式（更小拆组/其他通道）c) 按已裁 findings（b1 H1/M1/M2 CONFIRMED CORRECTION+b3 2）先行一次最小返修单派 C、proxy OCR 缺口记 NEEDS_REVIEW 遗留 d) 搁置 16B。未裁决前 16B 合入门禁关闭、C 维持冻结。
## r142（2026-10-13 10:2x）16B proxy 第 7 次在途 + 16C OCR 排队

- **16B b2-proxy 第 7 次 INFLIGHT**（用户裁决"最优方式重试"，r141 10:16:21 START，`b2_r141_direct7.py` pid 1658128/node 1658154，flock `inbox/ocr.lock` 独立核）：机制=临时切 ocr provider url 直连 `http://192.168.2.45:8002/v1`（t11e VLM 生产路径同款已证 0.3s 可用；根因=18002 双跳 SSH 隧道掐长请求，第 6 次确诊 planning 275s 后 compaction cancelled），fresh `--from c2018dd --to HEAD` 仅 `scene_host_proxy.py`（排除 orchestrator+tests），`OCR_LLM_TIMEOUT=900`+`--max-tokens 20000 --timeout 60`，finally 自动恢复原配置。连败链累计 **6/6 rc=1**（首跑 1440s/resume 1440s/拆组 336s/retry#4 720s/retry#5 fresh+resume 双败）→ 第 7 次为授权内最后一次，**硬截止 11:16**：rc=0→b1 H1/M1/M2+b3 2+proxy 全合并一次最小返修单派 C→16B 解冻；rc=1→NEEDS_REVIEW 维持冻结升级用户 a/b/c，不自动第八次。判活口径=session `ba32eca1` mtime 在动（10:2x 核）。
- **16C OCR 排队（16B 第 7 次收口后串行）**：head 固定 **`5c80857`**（协调者 rebase 接线，diff=`4b9f30a..ad37ae1` 逐字节一致）。尺寸预检：7 非测试文件均 <500 行 diff（numstat：pipelines.py +161/-15、bag_search_service.py +135/-2、scene_result_query.py +80/-8、sources.py +52/-2、pipeline_detail.html +44/-5、bags.html +11/-1、bags.py +8/-0；tests 466 行按先例排除挂 TESTER）。纯 SELECT 谓词+路由装配，零 DDL/零 alembic/零 models 面。执行口径=cron 短路径逐文件单审（`--exclude` 其余 6 文件+tests，每文件单组，单文件 <420s 稳态）。findings 全收口后一次裁决（CORRECTION→回派 B 最小返修；零 CORRECTION+TESTER PASS→合入）。
- **16A/07B 侧无新增**（全闭环在案）；16A 接线批 0 findings（session `8073ac31`）口径不变。

## r143 巡检段（2026-10-13 10:3x，preflight 2026-10-13T10:35:53+08:00）

- **16B proxy 第 7 次（r141 用户裁决"最优方式"=直连 8002）收口 rc=1 = 7/7 连败**：10:16:21 START 10:32:51 DONE rc=1 dur=16m30s（pid 1658128/node 1658154，session `ba32eca1-9837-48d3-bc19-3a29939eec36`）——log 独立复读「1 file / 0 comments / ~224426 tokens（in 160011+out 64415）/ 14 tool calls / budget_exceeded=false」+「Context compaction: scene_host_proxy.py cancelled」+「LLM retry 1 of 14 affected, 1 cancelled」=外部 LLM compaction 阶段请求级取消（非 token 预算/非文件本身）。末行 `retry with: --resume ba32eca1` manifest 在案。连败链 7/7（1440s/1440s/336s/720s/retry5 双败/第6次 planning 275s cancelled 确诊/第7次直连 16m30s cancelled）。
- **环境根因实测（r143）**：18002 双跳 SSH 隧道已断（Connection refused），直连 192.168.2.45:8002 可用（http 200 / 0.06s）。隧道是 7 连败底层环境根因，直连绕开隧道仍败于 compaction 取消。
- **r142 政策执行**：第 7 次=授权内最后一次，rc=1 后 16B 维持 NEEDS_REVIEW 冻结、合入门禁关闭、不自动第 8 次，升级用户 a/b/c（修隧道或换方式再试 / 更小拆组 / 已裁 findings 先行返修且 proxy 记 NEEDS_REVIEW 遗留 / 搁置 16B）。
- **16C OCR 串行接续（本轮起跑）**：16B 第 7 次释放 ocr.lock（fuser 核无在途）后，16C 7 文件逐文件单批链 detached pid 1682826（10:39:01 START，持 ocr.lock，node 1682828 首批 app/web/pipelines.py INFLIGHT）——`--from 6fb42c4 --to 5c80857` head 固定 5c80857，§3.6 预检 7 文件均小于 500 行 diff（pipelines +176 最大）无需拆组，tests 466 行排除挂 TESTER。脚本 run_t16c_ocr.py + r143_t16c_ocr_launch.py，进度/结果 ~/.hermes/cache/scratch/t16c_ocr/。收口政策：任一批 rc=1 单批 --resume 最后一次，再败挂 NEEDS_REVIEW 冻结 16C 合入门禁（TESTER 独立验证不受牵连）。
- **16A 侧 OCR 维持全闭环**（v2 14/14 + 增量 3/3 零 CORRECTION，r127 口径不变）；16A DONE（main 6fb42c4）、07B DONE（4b9f30a）。

## r144 巡检段（2026-10-13 11:0x，preflight 2026-10-13T10:50:53+08:00，指纹 adf61cd6）

- **16C OCR 链 2/7 收口 rc=0（pid 1682826 存活实测，progress 独立复读）**：c01 `app/web/pipelines.py` **rc=0 dur=1146s 4 findings 全 low**（session `46b7e357`，~804688 tokens）/ c02 `app/services/bag_search_service.py` **rc=0 dur=582s 2 findings 全 medium**（session `03eee6ac`，~467880 tokens）；c03 `app/services/scene_result_query.py` 11:07:49 START INFLIGHT；c04~c07 QUEUED。
- **c01 4 findings 协调者独立核（wt-04a-t16c HEAD `5c80857` 只读实测）**：
  - **C1 (:111-112 死分支) CONFIRMED=死代码**：`SCENE_STEP_NAMES=(PRECHECK,EXTRACT,INFER,SEGMENT,WRITE,VALIDATE,PUBLISH,REGISTER)` 实测枚举，该 elif 的 `no_match and key in (WRITE,VALIDATE,PUBLISH,REGISTER)` 全被前一分支（order>=SEGMENT 覆盖 4-7）吸收，零新增行为。**预裁决=VERIFICATION_GAP 级维护项，随全批收口并入一次最小返修单（若 c03-c07 出 CORRECTION 级则同单捎带），不单独阻塞**。
  - **C2 (:163 `run` 参数未用) CONFIRMED**：函数体只迭代 copies/artifacts（sed 实测）。同 C1 口径。
  - **C3 (:628-635 `scene_terminal` 死变量) 部分 CONFIRMED**：模板 grep `scene_terminal` **0 处引用**（传参未消费=CONFIRMED）；但「模板硬编码刷新停止列表漏 `INPUT_INVALID`」半句**不成立**——transitions.py 实测 `INPUT_INVALID` 仅属 PHASE0 自建/NVIDIA 面（queue→{FAILED,INPUT_INVALID,...}，:106 终态集合），场景 run 的 SCENE_* 状态集（scene_slice_service 实测 12 个枚举）不含 `INPUT_INVALID`；`scene_terminal` 集合内的 6 态对场景页而言全部被模板列表覆盖（场景终态 SCENE_DONE/SCENE_FAILED/SCENE_PARTIAL_FAILED + CANCELLED/QUARANTINED），16C 自身 9 项浏览器取证「终态停刷新」PASS 与之一致。**预裁决=删死参数或改接模板，维护项不违 AC，随单捎带**。
  - **C4 (:113-115 冗余分支) 独立核改判 REJECTED（与 C1 冲突）**：:94 实测 `run_failed = run.status in {"SCENE_FAILED","SCENE_PARTIAL_FAILED","FAILED","CANCELLED","QUARANTINED"}` **不含 INPUT_INVALID**，且该 elif 要求 `step is None`（前面 `if step:` 已 False）——C1 已证该 elif 全死，C4 前提「step is None 时两分支同值」依赖同一死分支；活路径上 `run_failed` 唯一语义入口=else 分支（step 存在但非 SKIPPED 的映射外态，实际不存在于八步枚举）。**维持「未开始」与 DESIGN「未启动步骤=未开始」口径一致，非错误**。协调者对 OCR 冲突裁决=C1 采信、C4 驳回（证据=SCENE_STEP_NAMES 枚举+run_failed 集合实测）。
- **c02 2 findings 协调者独立核**：
  - **C5 (:312-315 双用途筛选与展示不一致) CONFIRMED CORRECTION（medium）**：`data_kind_case()` 单值 CASE 分支 3（ORIGINAL+scene 用途→scene_original）先行，双用途包（ORIGINAL+scene_slice 用途+dataset_type=self_built）在 `data_kind=self_built_original` 筛选下**不命中**；但 `data_kind_context()` 同双标展示（TESTER 取证 #3 PASS 证实展示双 badge）。DESIGN §7.3.3 明文「**双用途原包可同时显示两个类型标记并命中两个筛选**」（本轮 sed 原文核）+ 代码 :144 注释自称「双用途原包在 scene_original/self_built_original 中**均可命中**」=展示/筛选语义与契约+自述双重不一致。最小修复=OCR log 已给 patch（self_built_original 分支 OR-in dual_purpose 条件）或改 CASE+注释+context 文档（单值口径）——两方向由 B 在返修单内按 DESIGN 明文选**双命中**实现（DESIGN 为契约源）。
  - **C6 (:73-79 `data_kind_labels_for` 死代码) CONFIRMED 死代码**：全仓 grep 调用点 **0 处**（仅定义）；NOT_APPLICABLE+self_built 分支确实返回 `["self_built_original"]` 与 `data_kind_context` 不猜口径分叉。同 C1/C2 口径=随单捎带删除。
- **政策维持 r143**：7 批全 rc=0 且零 high/critical → 已裁 findings 合并**一次最小返修单派 B**（C5 主项 + C1/C2/C3/C6 维护项）→ 交付冻结→机械核验→返修增量 OCR（小批）→ 16C 合入（TESTER PASS 已交付 `attempt-1.md` 10:47，双证据面=OCR 闭环+C5 收口后 TESTER 面是否需复测按 r14x 口径：C5 修复改谓词面，**返修后需 TESTER 复测双用途筛选项（#3/#4 子项）**）→ 16C DONE → 16D 前置 2/3；任一批 rc=1 单批 resume 最后一次再败挂 NEEDS_REVIEW 冻结 16C 门禁（TESTER 面不受牵连）。
- **16B 在途核（r144 新事实）**：交互会话 @session:default/20261011_144852_2bb4c6 用户 10:47「为什么不用 --rule 提回合」问询后，10:48:49 起跑 16B proxy OCR **第 8 次等待器**（`b2_r143_wait8.py` pid 1697095，ps 核存活，父=hermes gateway=交互会话控制）：16C 链收口后自动接跑第 8 次（`b2_r142_low8.py`：`--effort low`+`-b` 6 项不变量背景约束+直连 8002+`OCR_LLM_TIMEOUT=900`，对症真实终因=MAX_REVIEW_ROUNDS 内嵌 2 回合收敛不出 findings，兜底=`ocr delegate` 规格+宿主代审口径）。**协调者口径**：第 8 次属用户对 16B a/b 处置的交互会话内新授权（r143「不自动第 8 次」政策由该会话动作取代，本侧记账不阻塞）；`~/.opencodereview/config.json` 当前 url=直连 8002（第 7 次 finally 未恢复 18002 隧道遗留，隧道实测已断 Connection refused——18002 不可用期间直连是唯一可行路径，**本侧不重置 config**，避免打断交互会话在途计划；r145+ 监控第 8 次收口后 config 是否被其 finally 恢复）；并发风险=第 8 次与 16C 链共抢 8002 队列——等待器设计上等 16C 链 node 进程退出后接跑（串行不并发），本侧 16C 链收口即释放，不干预。
- **TESTER 16C 交付记账**：`test-receipts/TEST-TASK16C-independent/attempt-1.md` 10:47:24 事件+报告 PASS 收口核（9 项场景取证全过、自包含 uvicorn 58 项探针、SQLite 898 passed 4 failed 均 base 既有、0 残留、MySQL 面口径=无 DDL 仅 SELECT 谓词不要求真 MySQL）→ 16C 双证据面：TESTER PASS **已齐**（待 C5 返修后复测谓词子项）+ OCR 7 批**收口中（2/7）**。
- **门禁/角色**：16C REVIEW_PENDING（OCR c03 在途 c04-c07 排队，**C5 CORRECTION 已现→合入门禁维持关闭，全批收口后派返修单**）；16B NEEDS_REVIEW 冻结口径更新=交互会话第 8 次等待器在途（本侧不抢不拦）；16D WAITING 三前置未齐不变。A=空闲、B=16C 交付冻结 `5c80857`（等 C5 返修单）、C=16B 冻结、TESTER=16C PASS 已交付（等 C5 返修复测单）。main=origin `6fb42c4` 零漂移。
- **强审查（只读沿 r143 账 + strong_review.py status 11:0x 实测）**：grant `31dcbabe…` 绝对期限 **2026-10-13 11:33:12**（剩约 30min）、滚动 60min 0/5、本授权累计 2、在途 0、最近 `a8febf1a` SUCCEEDED（费用未知）；本轮零新增。16C 强审判定=OCR 闭环+C5 返修收口后按 strong-review 口径（UI 面低风险+TESTER PASS 面，倾向 NOT_REQUIRED/MERGE 随返修增量，交付时核，期限 11:33:12 内是否可用届时实测）。


## r155 (2026-10-13 13:4x, preflight 2026-10-13T13:40:53+08:00, fingerprint 951c77bc) 16B attempt-2-r1 delivered + mechanical verify all green

- **C delivery receipt**: `receipts/TASK-16B/attempt-2-r1.md` 13:3x landed (13:38:17 event `c-t16b-a2r1-delivered-20261013`): head `40ab818` (base `0208a73`, `c/task-16b-scene-host-proxy` @ `wt-03b-t16b`), 6 fixes H1/H2/H4/H5/H6/L1 + 6 new regressions, self-test 20 passed (14 existing zero regression) + 32 passed (orchestrator face), ruff/compileall clean, zero out-of-scope declaration.
- **Coordinator mechanical verify (independent, wt-03b-t16b read-only)**:
  - Ancestry: `git merge-base --is-ancestor 0208a73 40ab818` OK; HEAD=40ab818 single commit continuation.
  - diff numstat: `scripts/scene_host_proxy.py +43/-10`, `tests/test_scene_host_proxy.py +177/-1`, total +220/-11 = **matches receipt list per-file** (receipt "+42/-11" is a --stat display counting diff of 1 line; numstat measured value is authoritative).
  - Zero out-of-scope: diff only 2 files, did not touch orchestrator/fake_vlm/migration/app face.
  - Independent rerun: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/test_scene_host_proxy.py -q` -> **20 passed in 12.16s**, exit 0.
  - `ruff check` 2 files All checks passed; `compileall` exit 0.
- **State: REVIEW_PENDING verified -> incremental OCR queued** (`--from 0208a73 --to 40ab818`, wt-03b-t16b, only one non-test file scene_host_proxy.py +54 line diff, single batch small file; serial with 12S-B chain c01/c02 holding `ocr.lock`).
- **12S-B OCR chain status** (c01 in-flight check): pid 1897396 etime 14:08 alive, session `080bc21b` still writing at 13:42, no session_end/manifest -> in-flight healthy, not judged stopped/passed.
- **Closure chain**: 16B incremental OCR rc=0 + zero CORRECTION -> strong review pack (6 fixes scope, authorization `auth-24h-20261013` grant `6b2d83fb9` until 10-14 13:27:15) -> merge main -> 12S-C dependency recompute (16B accepted then check 12S-A/B status). rc=1 -> single batch resume one last time, if fails again mark NEEDS_REVIEW.

## r156 (2026-10-13 13:5x, preflight 2026-10-13T13:50:53+08:00, fingerprint 1a9aa1bd) 12S-B OCR c01 收口 8 findings 全 CONFIRMED + c02 在途

- **12S-B c01 收口 rc=0（progress.txt 13:51:20，session `080bc21b`，5 文件 8 finding，~853862 tokens，23m5s）**：`--from 6fb42c4 --to f62a29c` 核心算法面（adapter/decode/render/model/segment）。
- **协调者逐条只读核 wt-04a-t12sb（head f62a29c）代码实测 → 8/8 CONFIRMED，误报 0**：
  - **S1 [bug·HIGH] adapter.py:186-188**：模型循环 + `cache.hit(expected_frame_count=len(rendered_frames))` + `model_storage_ns` + render_log 计数由 `rendered_frames` 驱动，但 `account_frame`(render.py:93) 对 <500KiB 的 jpg 执行 `output_path.unlink()` 只把存活帧加进 `valid_frames`，而 render 循环 `if ok: rendered_frames.append(...)` 把含已删小图的全量 ok 帧加入 → 遍历 `rendered_frames` 对已删文件 `jpg.read_bytes()` → 任一帧低于阈值即 `FileNotFoundError`（ADAPTER_ERROR 全 run 失败），否则把被过滤小图喂模型、时间轴与缓存帧数错位。**修复=改用 `report.valid_frames` 驱动循环/expected_frame_count/model_storage_ns**。
  - **S2 [bug·MEDIUM] adapter.py:115-116**：守卫 `if work_dir.exists() and not work_dir.is_absolute()` 仅对已存在相对路径生效；全新相对 `work_dir` 穿透 → `mkdir(parents=True, exist_ok=True)` 相对进程 CWD 创建，PCD/JPG/render_log 落不可控目录，破坏受控绝对路径不变量（ContractRunContextValidator 在 dispatch 路径已拦，但直接 `analyze()` 绕过）。**修复=改为 `if not work_dir.is_absolute():`**。
  - **S3 [bug·HIGH] decode.py:90-92**：`parse_pointcloud2` 仅对 3 处变长读（frame_id/field name/data blob，:96/:112/:136）做 `pos+x > len(data)` 越界守卫；全部固定尺寸 `struct.unpack_from`（sec/nanosec/str_len/height/width/nfields/fname_len/f_off/point_step/row_step/data_len）与裸字节读（is_be/f_dt/f_cnt）无守卫 → 截断/畸形 PointCloud2 抛 `struct.error`/`IndexError` 而非 `DecodeError("P2_TRUNCATED")`；`decode_pointcloud_route`(:254) 循环内无 try/except、adapter `_decode`(:314) 仅捕 `DecodeError` → 原始 struct 错误逃逸 `analyze()`，破坏"存在但解不出有效帧 = FAILED(DECODE_FAILED)"契约。**修复=每个读加 `_read_struct` 型边界守卫（slope/cdr.py 已有先例）**。
  - **S4 [bug·HIGH] render.py:168-169**：`read_intensity(pcd_path)` 返回全 PCD 点 intensity（len=n），此处与 `len(cropped)`（ROI mask 后子集 = mask.sum()）比较，几乎恒 False → `cloud.colors` 从不设置，点云渲染无色，破坏强度水雾/正常判别（参考图与 prompt 依赖之）。**修复=对 intensity 数组施加同一 ROI mask：`intensity_arr[mask]`**。
  - **S5 [maintainability·LOW] adapter.py:338-340**：两条 decode 路线（packet/pointcloud）实测均填 `fr.pcd_path`，`pcd_path is None` 的 points-hash 分支不可达（死代码）。
  - **S6 [maintainability·LOW] decode.py:267-268**：pointcloud 路线 `decode_pointcloud_route` 无 `cancel_check`（packet 路线有 :214），长点云解码不响应文档声明的逐帧取消信号。
  - **S7 [performance·LOW] render.py:214-217**：`_intensity_color` 内 `for i, val in enumerate(normalized)` 纯 Python 逐点循环在渲染热路径（每选中帧、ROI 可达数万点）→ 改向量化（`np.select`/分箱 mask）。
  - **S8 [bug·LOW] adapter.py:97-98**：`route="auto"`（默认）且 bag 两 topic 均缺时 `_resolve_route` 返回 "auto"，落入 `route not in _ROUTE_TOPIC` 分支报自相矛盾"未知路线 'auto'"；实为双缺 topic，应与显式路线的 `needed not in topics` 一致给 NOT_APPLICABLE 缺 topic 原因。
- **裁决（16C r144 同口径）**：S1/S2/S3/S4/S8 = CORRECTION 级（其中 S1/S3/S4 为 HIGH 功能性正确性缺陷，S4 直接使能力核心输出无效），S5/S6/S7 = 维护项。**合入一次最小返修单派 B（c02 全链收口后合并 S1-S8 全部 findings，避免多轮返修）**；12S-B 维持 **REVIEW_PENDING 未合入**；返修后 TESTER 独立验证（真实 decode/render/VLM 面 12S-B 本单 NOT_RUN 依赖缺失，留 TESTER 域）→ 合入 → 重算 12S-C 依赖。
- **12S-B c02 在途核**：pid 1897396 chain.py（etime 28min），node 子进程 1926290（`--exclude` c01 5 文件，审辅助配置面 `__init__/cache/pcd_io/precheck/references/time_map/config/scene_capabilities.yaml` 7 文件），13:51:20 START，`--max-tokens 0 + --timeout 60` 沿用成功口径，无 session_end/manifest → 健康在途，不判停止/通过。
- **收口链更新**：c02 收口 → S1-S8+c02 findings 合并一次最小返修单派 B → 交付冻结 → 机械核验 → 返修增量 OCR（小批）→ TESTER 12S-B 独立验证 → 合入 main → 12S-B DONE → 重算 12S-C 依赖（16B+12S-A+B）。16B attempt-2-r1 增量 OCR（`0208a73..40ab818`）与 12S-A 增量 OCR 继续排队于 12S-B 全链之后（持 ocr.lock 串行，不并发）。
- **强审查（只读）**：grant `6b2d83fb9`（auth-24h-20261013）至 10-14 13:27:15，近 60min 0/5，本授权累计 0，在途 0，最近 `a8febf1a` SR-07B-R4 SUCCEEDED（tokens 530310 in/471552 cached/8293 out/4334 reasoning，费用未知）。本轮零新增。


## r157 (2026-10-13 14:0x, preflight 14:02:03, fingerprint 6ef5db02) OCR 固定流程交接 + 12S-B 旧链 c02 在途 + 候选包封存

- **固定入口切换确认**：Skill 1.5.0 / PROTOCOL L70 / notice OCR-RUNTIME-FIX-20261013 三方在案；今后唯一入口 `ocr_runtime.py prepare→start→status`（独立 systemd service、全链 global/project 双锁、参数版本化不改共享配置）。本回合零新 OCR/强审起跑。
- **12S-B 旧链（pid 1897396，retired 入口产物）只观察收口**：c01 已收口 rc=0 8 findings 全 CONFIRMED（r156 段，S1-S4/S8=CORRECTION 级）；**c02 在途**（node 1926290，`--from 6fb42c4 --to f62a29c --exclude` c01 5 文件，审 `__init__/cache/pcd_io/precheck/references/time_map/scene_capabilities.yaml` 7 文件，13:51:20 START，session `96fa444e` mtime 14:04 request_no 14 在动=健康，无 session_end/manifest 不判收口）；`inbox/ocr.lock` holder=1897396 单持有。
- **候选 PREPARED 包 `reviews/TASK-12S-B/runtime-prepared-20261013/` 封存不盲跑**：spec 冻结 base `6fb42c4821`→head `f62a29c211`，b01=核心 5 文件（=c01 已出 8 findings）/b02=辅助 7 文件（=c02 在途），12 入选 tests 排除，endpoint 8002+model qwen3.8-27b-fp8 冻结。c02 旧链自然收口后以旧链 manifest+findings 为该身份最终证据；仅当旧链失败/覆盖缺口时按 ocr-runtime.md 显式 `--reuse-run bc32b979`（授权 auth-24h-20261013 内、旧 run 退出、根因处理、最多一次）。
- **finish_legacy 一次性 service 在位**（pid 1923120，旧链退出后仅纠正其可能写回的 18002 废弃 URL，不恢复整份配置不启动新 OCR）。
- **收口链更新**：c02 收口 → S1-S8+c02 合并一次最小返修单派 B → 交付冻结 → 机械核验 → 返修增量 OCR（**固定入口**）→ TESTER 独立验证（12S-A/B 单 r156 已派并行）→ 合入 main → 12S-B DONE → 重算 12S-C 依赖；16B r1 增量 OCR（`0208a73..40ab818`）与 12S-A 增量 OCR（`6fb42c4..77c395b`）排队其后，**新身份一律固定入口 prepare/start/status**。
- **强审（只读）**：grant `6b2d83fb9`（auth-24h-20261013）至 10-14 13:27:15，近 60min 0/5，本授权累计 0，在途 0，最近 `a8febf1a` SUCCEEDED（费用未知）。本轮零新增。

## r158 (2026-10-13 14:2x, prerun fingerprint cf202306) 12S-B c02 收口 + 全链 16 findings 裁决 + 返修单派 B

- **c02 收口**：14:16:32 `DONE rc=0`（progress `t12sb_ocr/progress.txt` 实测；session `96fa444e`；7 文件 8 findings，~642381 token 25m12s；chain `{'c01': 0, 'c02': 0}` 全链 done；进程 1897396/1926290/1926298 退出、`ocr.lock` 无 holder 实测）。
- **c01+c02 全链 16 findings 裁决（协调者逐条只读代码核 wt-04a-t12sb@`f62a29c`，16/16 CONFIRMED 误报 0）**：
  - c01（S1-S8，r156 段已列）不变：S1/S3/S4 HIGH+S2 MED+S8=CORRECTION 级。
  - c02（T1-T8）：T1 precheck.py:116 **MED fail-closed 破坏**（ldd 探针自身失败→`required_missing` 空→`ok=True` 自相矛盾 detail，代码实测确认）；T7 pcd_io.py:120-123 **MED ASCII intensity off-by-one**（`data_start` 含 DATA 行换行→`split("\n")` 尾空元素→多跳一行丢首值，实测确认）；T5/T6 pcd_io header 契约缺口（非数值 ValueError/IndexError 逃逸+COUNT 可选误报+binary_compressed 过检）LOW；T3 reference 错误码误分类 LOW；T2 硬编码机器路径 LOW；T4 references 四常量死代码（全仓 grep 零引用实测）LOW；T8 time_map tie 时歧义拒绝恒不触发 LOW。
- **一次最小返修单已派 B**：`inbox/2号/TASK-12S-B/attempt-1-rework-dispatch.md`（14:2x 落盘，base `f62a29c` 续 commit @ `wt-04a-t12sb` 分支 `b/task-12s-b-spray-adapter`；16 条逐项，CORRECTION 级必改、LOW 级最小改或书面取舍；只动 spray 域；自测含 S1/S3/S4/T1/T5-T6/T7/T8 定向矩阵；ACK 时限 30min）。
- **候选 PREPARED 包 `bc32b979` 维持封存**：旧链 16 findings 覆盖已齐（b01/b02 与 c01/c02 同范围同 base/head），无失败无覆盖缺口，**不触发 reuse-run**。
- **收口链更新**：B 返修交付→机械核验→**返修增量 OCR 走固定入口 `ocr_runtime.py prepare→start→status`**（`--from f62a29c --to <新head>`）→TESTER 独立验证（B 侧快照更新另发通知，A=`77c395b` 不变，TESTER 单 r156 已在途）→合入 main→12S-B DONE→重算 12S-C。16B r1 增量 OCR（`0208a73..40ab818`）与 12S-A 增量 OCR（`6fb42c4..77c395b`）排队其后，**一律固定入口**。
- **强审（只读）**：grant `6b2d83fb9` 至 10-14 13:27:15，近 60min 0/5，本授权累计 0，在途 0，最近 `a8febf1a` SUCCEEDED（费用未知）。本轮零新增。
