# 派单：TASK-16A attempt-1 场景接收隔离（v0.4 最小闭环·第一刀）

- status: DISPATCHED
- 派单时间：2026-10-12 22:40 +08:00
- 任务：TASK-16A 场景接收隔离（REQ-14、REQ-08 / AC-14、AC-08；DESIGN §7.3.1 冻结契约）
- 授权来源：**用户 2026-10-12 群内明确授权**（"查看相关文档，应该已经更新，最小链路需要增加新的开发任务，开始分派干活"）+ 用户已确认 `/public/rosbag_scene_processing/{incoming,ready,slices}` 生产目标逻辑树（见 v0.4 规划节）
- owner：A（执行者A·数据处理链路，wt-01 系；接收/调度/扫描域=A 的 03B 责任面连续）
- base：main 本地 `c2018dd`（= origin `502bf8e` + 1 纯文档 commit；07B `f4bfcf2` 未合入——**本单不得包含 07B 文件**，若 merge-tree 冲突以 07B 先行合入为假设 rebase）
- 下游：16B 最终接线消费本单产物（profile/根上下文/登记 root_id）；16C 查询面消费 `intake_snapshot_json`；16D 联合验收。

## 一、交付内容（严格按 DESIGN §7.3.1 冻结契约，最小一致改动）
1. **三个新配置项**（backend settings + compose 环境变量透传，生产值/测试值按契约表）：
   - `SCENE_NAS_SCAN_ROOT`（测试 `/test/scene/incoming`、生产 `/public/rosbag_scene_processing/incoming`）
   - `SCENE_NAS_READY_ROOT`（测试 `/test/scene/ready`）
   - `SCENE_SLICE_PUBLISH_ROOT`（测试 `/test/scene/slices`）
   - 校验：绝对逻辑路径、物理映射存在、**根不重叠**（新三根互不嵌套 + 与旧 NAS_* 根不重叠）；旧 `NAS_*` 校验逻辑不替换
2. **Scanner 双根上下文**（现有单 Scanner 进程，不新起服务）：
   - 每轮分别扫旧自建根 + 场景根；一根故障不阻断另一根
   - 每根独立 journal、独立统计/ScanJob、独立 incoming→ready 映射
   - 全局 Settings 不得在扫描循环中改写；原路径工具函数改为**显式接收根上下文参数**（缺省仅兼容旧自建调用，不改旧行为）
   - 场景根的 incoming→ready：同文件系统原子 rename 整个已校验 Bag；目录穿越/符号链接越界拒绝；ready/切片/旧根互不嵌套
3. **IngestProfile 扩展**（迁移，含 downgrade）：
   - 新增 `intake_root_id`：枚举 `self_built|scene`；**缺字段的历史 profile 回填 `self_built`**；不修改原 profile ID/version/hash
   - 新 profile `scene-isolated`（version=1）：默认仅 `scene_slice+slope`；同根内按 `incoming_prefix` 匹配，跨根空前缀不得兜底
   - profile 具体版本的 root_id 不可变
4. **IngestSubmission 接收快照**（迁移）：新增 nullable `intake_snapshot_json`（`schema_version=scene-intake/v1`、environment、root_id、逻辑 scan/ready 根、profile ID/version）；接受提交时写入，绑定时补 `bound_incoming_path/bound_ready_path`，恢复读快照；**与 EffectiveConfig/config_hash 分离，不重算已接受业务 hash**
5. **登记身份防线**（backend 侧）：register 请求携 `root_id` + 原 incoming_path + ready path + 接收证据；Backend 按受控根重新验证（不只信 Scanner 上报路径）；**场景 ready 即使缺 incoming_path 也不得落入自建默认**；未知/矛盾根返回明确错误（不猜测）；旧客户端缺 root_id 时仅已验证旧根走旧兼容
6. **用途路由边界**（AC-14 核心）：
   - 场景根默认提交只触发 scene_slice+slope；**不隐式并集**（不因新根给旧自建任务新增场景任务，反之亦然）
   - 显式 self_built/双用途在场景根的兼容：只接受已登记且冻结用途含 self_built 的源，不把任意 /public 路径放白名单；纯 scene_slice 不调用 Phase0（Phase0 代理受控 ready 根扩展如涉 A 域 03B 外文件，申报不越界改）
   - 场景根无 profile/配置无效 → 返回可恢复 `CONFIG_REQUIRED`/配置错误并停在接收/登记待处理；`SCENE_INGEST_ENABLED=0` 只暂停场景自动调度，**不得作为默认触发 Phase0 的理由**
7. **历史兼容**：已有 submission/run/文件保留原路径与 hash；不因开启新根重建运行；启用前清点旧 PENDING_INPUT/活动场景任务/Scanner journal（测试栈清点结果写入报告）
8. **staging 契约供应**：场景 staging 位于 slices 同文件系统 `.staging/<run_id>/<attempt>`；发布侧（16B 消费）只读核对同一受控物理根；**不信任回报者自选 publish_root**（backend 侧 complete/reconcile 校验口径如已有 06B 代码承载则不动，仅声明契约点）

## 二、测试与验收口径（TESTER 独立验证）
- 双根独立：场景根故障（路径不存在/权限）时旧自建根扫描正常（反向同理）
- 根不重叠校验：构造重叠配置拒绝启动/登记
- 场景默认提交→只建 SCENE_SLICE run（不建 Phase0/自建）；显式双用途→两 run 各自独立
- 旧 profile 回填 self_built、原 hash 不变（迁移前后对比）
- register 防线：伪造 root_id 矛盾/场景路径缺 incoming_path → 明确 4xx，不入自建
- 真 MySQL 8.4 隔离库：新迁移 upgrade+downgrade+re-upgrade 往返（T03/T04 教训，SQLite 绿不算）
- 既有 Scanner/ingest 套件 0 红；ruff 绿
- 本地 real 栈冒烟：`/test/scene/incoming` 放一个真实袋副本（或 fixture）→ Scanner 双根各扫一轮 → 场景袋登记 scene 根、旧袋登记 self_built 根，两条 journal 独立

## 三、边界与禁止
- 不碰 07B 冻结文件集（`app/api/scene_manual_revision*.py`、`app/services/scene_manual_revision_service.py`、`bag-detail.css`、`detail.html` 的 07B hunks、`20261012_01_scene_manual` 迁移）——本单新迁移 revision 命名独立（如 `20261013_01_scene_intake`），down_revision 指向届时 alembic 单头（若 07B 先合入则链在其后，报告说明）
- 不实现 16B 代理/执行面、不实现 16C 页面（查询面只供字段）
- 不改生产 compose 实际值（生产三根部署核验属 TASK-11 前置；本单只保证配置契约+测试根可用）
- 不搬历史文件、不改原 UID、不退回复用 raw_rosbags

## 四、交付物
- commit（base c2018dd 之上）+ 回执 `receipts/TASK-16A/attempt-1.md`（REVIEW_PENDING）+ 报告 `reports/TASK-16A/attempt-1.md`（含迁移往返证据、双根冒烟证据、历史清点）
- 交付后：机械核验 → 串行 OCR → 合入 → TESTER 独立验证 → 16A 接受 → 16B 接线消费 / 16D 候选