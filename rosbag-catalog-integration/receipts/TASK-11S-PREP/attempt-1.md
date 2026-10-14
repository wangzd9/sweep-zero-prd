# 回执：TASK-11S-PREP attempt-1 水雾生产首包发布准备（执行者 A）

- **交付冻结**：commit `d8f7206`（base `0e9a2df`，4 文件 +230，仅 `deploy/scene/*` 纯新增，零 app/scripts/alembic 业务 diff）
- **r1 装配返修冻结**：commit `769d69f`（base `d8f7206` 续，5 文件 +128/-31，仅 `deploy/scene/*`；r1-4 副本实验证据复用 `g4r3.log` 16:55:22 成功区块，本 commit 不含实验物）
- **branch/worktree**：`a/task-11s-prep` @ `wt-01-t11sp`（HEAD `d8f7206eca8fdd920e684593be96388161705832`）
- **状态**：DELIVERED / REVIEW_PENDING（机械核验面，非通过）——**本单完成≠授权发布**，11S 本体 G1–G6 门禁与用户 17:30 放行面不变
- **环境**：生产处理机 `processing-machine`（192.168.2.134 / dataprocess-Legion-Y9000P）SSH 只读预核；隔离迁移 `docker mysql:8.4`（生产同源 8.4.11）用完即毁

## 一、生产只读预核表（SSH 处理机，无免密 sudo，docker/只读命令）

| 项 | 实测值 | 口径 |
|---|---|---|
| 当前版本 | `19b6db4-dirty` | `.deployed-git-revision`（rsync 非 git 仓库） |
| **dirty 文件清单** | 4 个 app 孤儿文件：`app/phase0_worker.py`(224行) / `app/pipeline_domain.py`(59) / `app/scanner.py`(770) / `app/scanner/catalog.py`(63) | 部署树 + 运行镜像 `rosbag-catalog-backend` 内均存在，但 **19b6db4 基线与本地 main(6fb42c4) 均无**，全仓 grep **零引用**——旧布局遗留死文件，随 dirty 构建烘进镜像（申报不修复，属 11S 发布重建镜像面） |
| alembic 当前头 | `20260928_02` | 容器内 `select version_num from alembic_version`（经 backend `DATABASE_URL`，13 bag_record 行） |
| Backend/Web 健康 | backend :18000 `/health` 200（页面渲染）；frontend :8180 → 302（正常跳转） | 宿主 curl 只读 |
| 旧代理 active 面 | `rosbag-a100-proxy` active(running 4d) / `rosbag-phase0-proxy` active(running 4d) / `rosbag-catalog-scan` inactive | `systemctl is-active` |
| 备份 timer 最后触发 | `rosbag-catalog-mysql-backup.timer` active，LAST 2026-10-13 12:17:08，NEXT 18:19:17 | `systemctl list-timers` |
| **备份产物实际存在性** | `rosbag_catalog-20261013-121708.sql.gz` 264,215,180 B，`gzip -t` **OK**，sha256 **MATCH**（ca91e4ae…），7959 行，`-- Dump completed on 2026-10-13 12:17:44` | timer active≠备份可恢复，已核大小/时间戳/可打开/sha 全通过 |
| **生产场景/接收入口表** | `ingest_submission` / `scene_slice` / `ingest_profile` / `scene_capability` / `scene_manual_revision` / `bag_scene_label_evidence` **均不存在**（`resource_lease` 存在） | `show tables`（47 表）——候选链 6 步将创建，是硬前置 |
| **车辆登记** | `vehicle` 表 **0 行（vehicles=[]）** | 首包前必须登记 `vehicle_code=test`，否则 12S-A spray 入口提交 422 `UNKNOWN_VEHICLE`（不自动建车辆） |

## 二、隔离迁移实验 RC 矩阵（docker mysql:8.4 同源 8.4.11，用完即毁 0 残留）

从生产头 `20260928_02` 出发，逐步 upgrade 到候选链头：

| 步骤 | RC | 耗时 | head 迁移 |
|---|---|---|---|
| seed → `20260928_02` | 0 | 3.96s | （对齐生产头） |
| `20261008_01` | 0 | 0.26s | 20260928_02 → 20261008_01 |
| `20261008_02` | 0 | 0.26s | → 20261008_02 |
| `20261009_01_scene_identity_key` | 0 | 0.26s | → 20261009_01 |
| `20261009_02_ingest_frozen` | 0 | 0.27s | → 20261009_02 |
| `20261012_01_scene_manual` | 0 | 0.26s | → 20261012_01 |
| **`20261013_01_scene_intake`** | **0** | **0.28s** | → **20261013_01_scene_intake (head)** |

- **单头确认**：`alembic_version` 单行 = `20261013_01_scene_intake`（无 1406 超长、无多头）。
- **12S-A spray 路径关键列落地**：`ingest_submission.intake_snapshot_json` ✓ / `ingest_submission.frozen_capability_hashes_json` ✓ / `pipeline_run.source_generation` ✓ / `pipeline_run.scene_identity_key` ✓（`source_metadata` 是 12S-A 存入 `intake_snapshot_json` 的 JSON 块，**零新增 DDL**，与 SPRAY-1900 notice「A 无新增 DDL」口径一致）。
- 新表落地：`ingest_profile` / `ingest_submission` / `purpose_schedule_event` / `scene_capability` / `scene_manual_revision` / `bag_scene_label_evidence`（空库行数 0）。
- **容器 0 残留**：`docker rm -f` 后 `docker ps --filter name=t11sp` = 0。

## 三、车辆登记命令模板（17:30 发布窗可执行）

正式入口 = admin 路由 `POST /vehicles`（form，无 prefix）；必填 `vehicle_code`(≤64) + `display_name`(≤128)，可选 `rustdesk_id`。本地栈实测口径：**303** 创建成功（跳转）、**409** 编号/rustdesk 重复、**400** 缺码/缺名。

```bash
# 生产 backend（处理机回环 18000；对外经网关/隧道）
curl -sS -o /dev/null -w "登记返回码: %{http_code}\n" -X POST \
  http://127.0.0.1:18000/vehicles \
  --data-urlencode "vehicle_code=test" \
  --data-urlencode "display_name=测试车辆（水雾首包）"
# 预期 303（新建）；重复再执行预期 409（幂等可判）
```
- 生产 `vehicles=[]`，首包提交前**必须先登记**；不登记则 spray 入口 422 `UNKNOWN_VEHICLE`。

## 四、53s 首包生产侧路径面（`rosbag2_2026_10_08-14_42_48`）

- 候选包**尚未在 production NAS 备份根**（`raw_rosbags`/`ready_rosbags`/`final` 均查无，`find` 零命中）——包在 A100（36.152.27.114）侧由环境 owner 完成渲染 cross-host PASS，**待传输**到生产 NAS incoming 路径。
- 生产 incoming 挂载 = NAS（Synology CIFS，backend 内 `/nas`，ro 只读，uid/gid 1000）；目标接收根容量面：处理机本地 `/` = 537G 总 / **395G 余**（23%），单包 ~724MB 余量充足；NAS 卷容量传输时按 `df /nas` 复核。
- **前雷达 topic 申报**：环境 owner 已实测渲染 PASS（A 只补生产侧路径面，不重复渲染）；传输落点/权限在 11S 发布窗内由发布 owner 核实。

## 五、旧流水线活动任务核对口径（17:30 维护窗口清单）

- `pipeline_run` 总 17 行：9 PUBLISHED / 3 FAILED / 3 NVIDIA_DONE / 1 CANCELLED / 1 SUCCEEDED，**全部终态**。
- **在途 = 0**：`leased`（lease_owner 非空）= []；`workable_status`（QUEUED/DISPATCHED/RUNNING/PENDING/RETRYING）= []。**无活动 run 需停抢**。
- 17:30 维护窗口只需确认：① 备份 timer 下一次触发 18:19:17（窗口内不冲突）；② 发布前跑一次备份快照或确认 12:17 产物可用（已验 sha OK）。

## 六、交付物文件清单（`deploy/scene/`，纯新增 4 文件 +230）

| 文件 | 说明 |
|---|---|
| `scene-host.service` | 正式代理常驻单元模板（`EnvironmentFile=-/etc/default/rosbag-scene`、`Restart=always`、回环、对应 16B `scripts/scene_host_proxy.py` **只引用不复制**） |
| `rosbag-scene.env.example` | 占位键：`SPRAY_MODEL_ENDPOINT`/`SPRAY_REFERENCE_DIR`/`SPRAY_DECODER_PATH`（环境 owner 证据回填）+ `SCENE_EXEC_HOST=1` + 回环端口 `SCENE_PROXY_PORT` |
| `install_scene_host.sh` | install/uninstall/status 三分支；幂等（同 hash 不覆盖/异 hash 先备份）；回滚段 disable+remove 保 journal |
| `DEPLOY-ENTRY.md` | commit sha↔镜像 build digest 对照表模板 + 发布前一致性核对 6 步（含端口核实不猜、SPRAY_* 回填、车辆登记先行、迁移先行） |

## 七、自测 / 证据

- `bash -n install_scene_host.sh` **RC=0**。
- `systemd-analyze verify scene-host.service`：我的单元**零报错**（输出其余错误全来自既有 netplan/snapd/nvidia/sysinit 单元，与本单元无关）；`git diff --check` RC=0。
- **幂等模拟**（scratch 目录双跑 install_unit 核心算法）：第 2 跑同 hash mtime 不变+零备份、第 3 跑异 hash 备份+新内容落地，**全部 ASSERT OK**。
- **零 app diff**：`git status app/ scripts/ alembic/ tests/` 全空（纯 deploy 新增面）；ruff 不适用（无 .py 新增）。
- **隔离资源 0 残留**：mysql 容器已 destroy、baseline worktree 已 remove、scratch deployed 副本已删。

## 八、边界与未执行项（如实申报）

- 零生产写入 / 零部署执行 / 零服务重启 / 零迁移在生产库运行（生产面全只读命令，迁移仅在隔离容器）。
- 未执行：生产库实际迁移（属 11S 发布门禁面单独执行）、常驻代理实际安装（`install_scene_host.sh` 只生成，发布窗执行）、decoder/VLM 镜像重建（环境 owner 域，已 cross-host PASS）、候选包传输到生产 NAS（发布 owner 域）。
- 12S-A 零新增 DDL 已核（spray 走 `intake_snapshot_json` 块）；12S-B/C 未合入面的迁移按「待合入后补跑项」口径，本单**不预做**。
- 越界：无（未跑 OCR/强审、未合主分支、未改 TODO/HANDOFF/DESIGN/decision/其他角色目录、未动生产写）。

## 九、收口链

回执 → 协调者机械核验（预核命令可复核性）→ 纳入 17:30 发布决策材料（G1–G4 证据面之一）→ 11S 执行门禁仍按用户当次授权。

---

## attempt-1-r1 装配返修段（2026-10-13 17:5x 冻结，覆盖原 15:35 交付的装配面缺口）

- **口径**：按 `attempt-1-r1-dispatch.md` 四处置返 + `attempt-1-r1-state-correction.md`（17:1x，剩余面收窄，r1-4 复用已收口证据不重跑）。r1 冻结 head 见本文件头 commit 链更新。
- **消费证据**：`runtime-install-handoff.md`（15:12 环境勘误）、`runtime-template-check-1550.md`（15:54 复核）、`disk-full-1643.md`、`docker-home-migration-1649.md`、`observed-progress-1736.md`（17:36 实测补充）全部消费，本段为回执注明。

### r1-1 服务启动方式 → 已验证 Docker 镜像运行（compose 装配）

- `deploy/scene/scene-host.service`：原 `ExecStart=/usr/bin/python3 .../scripts/scene_host_proxy.py`（宿主机 Python，不能消费容器内 ROS/Seyond/Open3D 环境）改为 `ExecStart=/usr/bin/docker compose -f /home/data-process/scene/scene-proxy.yaml up` + `ExecStop=... down` + `Requires/After=docker.service` + `TimeoutStopSec=60`；`EnvironmentFile=/etc/default/rosbag-scene`（供 compose 变量插值，缺失 fail-closed 拒启动，不用可选 `=` 前缀）。17:04 在途改造续用未重写，本轮补完一致性面。
- **新增 `deploy/scene/scene-proxy.yaml`**（service 引用的 compose 定义实际来源，此前不存在）：镜像 `rosbag-spray-runtime:20261013`（本机实测 image ID `e3fe73534ad8…dffbaef`，发布时按 DEPLOY-ENTRY §二.3 核处理机 digest，tag≠digest 口径不变）；`network_mode: host`（宿主回环 Backend 18000 直连，代理仍绑 `SCENE_PROXY_BIND=127.0.0.1`）；`command: /opt/spray-venv/bin/python /code/scripts/scene_host_proxy.py`（容器内解释器，entrypoint 先 source ROS/spray-msg 环境）；受审业务代码只读挂载 `/code`（镜像与业务 SHA 分别冻结）；state/work 可写根 + 切片发布根 bind（生产逻辑根 `/public/rosbag_scene_processing/slices`，宿主侧路径经 `${SCENE_SLICE_PUBLISH_HOST_ROOT:?...}` compose 插值，未配置拒启动不写死）。
- `install_scene_host.sh` 同步：新增 `COMPOSE_SRC/COMPOSE_DST`（落位 `/home/data-process/scene/scene-proxy.yaml`），install 三分支幂等覆盖 unit+compose+env 三文件（同 hash 不覆盖/异 hash 先备份），status 增 compose 文件存在性。
- **自测**：`bash -n` RC=0；`systemd-analyze verify` 本单元零报错（本机 systemd 面预检）；compose 文件 python yaml 解析 OK + 装配一致性断言 6 项全过（镜像/网络/env_file/command/只读挂载/插值键）；**幂等模拟三跑**（scratch 全 stub 不触系统路径）：run1 三文件落地、run2 同 hash 零覆盖零备份、run3 异 hash 备份+替换（备份计数 1）——全部 ASSERT OK。

### r1-2 模型端点变量勘误（以代理/app 实读面为准）

- `rosbag-scene.env.example`：`SPRAY_MODEL_ENDPOINT` → **`SPRAY_VLM_ENDPOINT`**（`app/scene/spray/adapter.py:407 _default_model_client` 实读，完整 chat/completions URL）；补 `SPRAY_VLM_MODEL`（adapter.py:417 实读）、`SPRAY_VLM_API_KEY`（adapter.py:416 实读，仅受控配置供给）；`SPRAY_REFERENCE_DIR`（references.py:94 实读）保留。
- **`SPRAY_DECODER_PATH` 如实申报**：全仓 grep 实测 `SPRAY_DECODER_PATH` 零代码消费面（`check_decoder()` 默认 `/home/wang/work/ros2_slice/utils/packet2pointcloud`，12S-B `0320a8e` decode 生产路径硬编码容器外默认封装）——保留占位键仅供预检/诊断口径，**不发明变量**；此为 12S-B 域观察项（容器内解码应走 `/opt/spray/bin/packet2pointcloud` 口径），供协调者核，本单不代修。
- `DEPLOY-ENTRY.md` §二.4 同步：回填清单改 `SPRAY_VLM_ENDPOINT`/`SPRAY_VLM_MODEL`/`SPRAY_VLM_API_KEY`/`SPRAY_REFERENCE_DIR`/`SPRAY_DECODER_PATH`，变量名以 adapter.py/references.py 实读面为准。

### r1-3 部署一致性口径 → 发布时点固定 SHA 校验

- `DEPLOY-ENTRY.md` §二.1 原「与 16B 旧 head 逐字节一致」失效（12S-C `92dcb52` +9 行 proxy 接线、16B-r2 `e152465` 及后续合入均在其后）→ 改为：发布前协调者给出**最终受审候选 SHA**（16B+12S-A+12S-B 全合入后 deploy 根），落 `.deployed-git-revision` 口径（脚本读取不硬编码）；核对 = 处理机 HEAD==候选 SHA + 该 SHA 下 proxy 文件 sha256 无本地漂移 + 12S-A/B 消费面 byte-identical 核。§一对照表补 compose 服务文件行、16B 行注明 r2 `e152465` 合入面。

### r1-4 生产数据副本隔离升级实验（复用已收口成功证据，不重跑）

- **成功区块 = `~/.hermes/cache/scratch/t11sp_r165/g4r3.log` 最后 START=16:55:22 块**（16:55:22–16:58:36，同文件前三个块为根分区满/脚本旗标错误的失败重试，作废不采信）：
  - 恢复：`backup.sql.gz`（= attempt-1 已验备份产物 `rosbag_catalog-20261013-121708.sql.gz` 264,215,180 B sha256 `ca91e4ae…` MATCH 7959 行，gzip -t OK 本轮复核）经 `zcat | mysql --binary-mode` 完整恢复 **RC_restore=0**；
  - 升级前基线：alembic `20260928_02`、bag_record **13**、pipeline_run **17**（= 生产预核同值，副本身份一致）；
  - `alembic upgrade head` **RC_upgrade=0** → 升级后 `20261013_01_scene_intake`、bag_record **13**、pipeline_run **17**（行数前后不变，真实 264MB 生产数据副本上验证升级链，区别于 attempt-1 空库六步）；
  - 回填面：20261013_01 self_built 分组 0 / 20260909_02 frozen `{}` 0+0 / 20261009_01 scene_identity_key 非空 0（副本数据均为旧布局 bag，零回填命中符合预期）；
  - 抽样对照：bag 记录 `nvidia-chunk-2/09E2…34/B3E7…34` READY 保持；关键表行数 dataset_frame **113893**、pipeline_event 61180、scan_job 3750、api_idempotency 2109 等落日志；
  - 隔离与残留：MySQL 容器镜像 `4f8c1cfbe264`（= 本机 `docker.m.daocloud.io/mysql:8.4` 同 digest `6ea90827…`）、datadir bind `/home` 私有目录（根分区满后口径）、**RC_destroy=0、RESIDUAL=0**（`docker ps -a` 0 容器）。
- 失败证据保留：`g4r2.log` 16:44:14 ERROR 1114 `dataset_frame` full（根分区 100% 事故，`disk-full-1643.md` 在案）——该副本作废不续用，按 `docker-home-migration-1649.md` 16:54 恢复通知后重建成功。
- **临时目录清理**：`t11sp_r165/mysqldata`（103M，失败块残留）与 `mysqldata.1791881722`（8.4G，成功块 datadir）本轮已删（纠正单口径用完清理）；`backup.sql.gz`/`g4r*.log` 证据保留在 scratch 供协调者复核。

### r1 交付与收口链

- 冻结 commit（本段头部更新）：base `d8f7206` 续，`deploy/scene/` 5 文件（service 改造 + compose 新增 + env 变量勘误 + install 同步 + DEPLOY-ENTRY 口径）；零 app/scripts 业务面、零生产写入。
- 收口链（不代跑）：协调者机械核验（装配一致性面可复跑：bash -n / yaml 解析 / 幂等模拟 / g4r3 成功区块复读）→ 增量 OCR（`d8f7206..r1 head`，部署面小增量，排 12S-C OCR 后串行）→ 并入 17:30/17:45 G4 证据包（G4 副本缺口本轮补齐，r1 未完成口径解除）。
- **本单不授权任何生产写入**；远端安装仍等 17:45 放行盘点 + 用户当次发布授权。
