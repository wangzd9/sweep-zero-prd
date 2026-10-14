# TASK-12S-C attempt-1 机械核验与口径裁决（协调者）

- 时间：2026-10-13 15:5x +08:00（r165，prerun 指纹 2e34c39f）
- 交付：C `92dcb52` @ `wt-03b-t12sc` 分支 `c/task-12s-c-spray-wiring`（前置接线单，显式"待接线核验"，不申报正式联调 PASS）
- 回执：`receipts/TASK-12S-C/attempt-1.md`（15:44 落盘）

## 一、机械核验（协调者独立复跑，非采信回执）

| 项 | 实测 | 结论 |
|---|---|---|
| HEAD | `92dcb52`，porcelain 干净（排 .venv/scratch） | 与回执一致 |
| 祖先 | `40ab818`（16B-r1）∈ 祖先链；`6fb42c4`（main/16A）∈ 祖先链；`0e9a2df..6fb42c4` rev-list count=0（消费基线无 main 缺口） | PASS |
| 本单产品面 numstat `22ffb71..92dcb52` | `orchestrator +18/0`、`proxy +9/0`、`test_scene_spray_wiring.py +470/0`，共 3 文件，**零 app/ 行为面改动** | 与回执"27 行"一致 |
| byte-identical 核 | `git diff 77c395b..92dcb52 -- app/schemas app/api app/services tests/test_scene_spray_intake.py` = 0 行；`git diff f62a29c..92dcb52 -- app/scene/spray config/scene_capabilities.yaml` = 0 行 | 12S-A/12S-B 产物零改动确认 |
| 定向 | `pytest tests/test_scene_spray_wiring.py -q` **11 passed**（1.2s） | PASS |
| 回归合集 | 6 文件合集 **148 passed**（独立复跑 27.5s） | PASS，与回执一致 |
| ruff | 3 文件 All checks passed | PASS |
| 零越界 | 未碰 16C 冻结面/07B/迁移/alembic；消费 16B 冻结链为只读 import | PASS |

**结论：机械核验全绿，交付冻结 `92dcb52` 维持 REVIEW_PENDING（待接线核验），未合入。**

## 二、回执 §五两处口径裁决（协调者=契约负责人）

1. **spray 发布根**：裁决**接受 C 现口径**（既有受控 slices 根 `SCENE_SLICE_PUBLISH_ROOT` 下 `…/vehicle/spray/…` 场景子树，`publish_scene_slices` 按 scene_code 命名+原子 rename，不新开 per-scene 发布根配置）。依据：`environment_contract.py` 已冻结 TEST/PRODUCTION 两级 `SCENE_SLICE_PUBLISH_ROOT`（06A/06B 既有受控发布根机制），`scene_result.py` DTO 的 `publish_root`+`vehicle_key` 面即按此口径；新开 per-scene 配置属扩范围，回派不成立。**不返修。**
2. **车辆判定信号**：裁决**接受读父包 `bag.vehicle` 口径**（非直读快照 source_metadata）。依据：12S-A 提交面 `ingest_service.py:412 resolve_source_metadata_vehicle` 对 spray 入口 fail-closed（缺/未知 vehicle_code→422 不调度），bind 面 `apply_frozen_vehicle` 用冻结快照回写正确车辆（MANUAL 不覆盖、冲突 409）——父包登记值即权威来源；16B H5 快照口径（只存 scene_code/capability_version/capability_config_hash）在案，不新增读快照面。**不返修。**

两处均为解释性口径，非越界、非 CORRECTION 级，不回派 C。

## 三、收口链（12S-C）

1. **增量 OCR 排队**（固定入口 `ocr_runtime.py`，串行槽）：12S-A run `8540bf7e`（4 批，b02 在途）→ 12S-B `f62a29c..s9_head`（等 B S9b 交付）→ 16B r2 `40ab818..r2_head`（等 C r2 交付）→ 12S-C `22ffb71..92dcb52`（消费面 27 行+base import，小批）。
2. **强审 pack**：授权 `6b2d83fb`（auth-24h-20261013，至 10-14 13:27:15，剩 4/5）期限内，范围=spray 接线 2 文件 27 行；与 16B r2 复审排程时按滚动 60min 限额串行。
3. **接线核验单（真链冒烟）**：16B+12S-A+12S-B 三依赖全合入后另派（TESTER 面），本单不重做。
4. 全链齐 → 12S-C DONE → 重算 12S-D/12S 聚合。

## 四、C 槽与 16B r2 串行

C 本单交付冻结后释放等待；`inbox/3号/TASK-16B/attempt-2-r2-dispatch.md`（15:2x，强审 SR-16B-R1 5 项阻塞最小返修，base `40ab818`）仍 **PENDING 等 C ACK**。两单同一人串行，C ACK r2 后先收 16B r2，12S-C 维持冻结审查面不动。16B r2 链=机械核验→增量 OCR→强审增量复审（只 5 问题 ID）→TESTER→合入 16B。