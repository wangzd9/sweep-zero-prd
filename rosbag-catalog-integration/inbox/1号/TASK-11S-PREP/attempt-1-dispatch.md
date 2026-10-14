# 派单：TASK-11S-PREP attempt-1 水雾生产首包发布准备（A 独占，部署入口/服务模板/迁移/预检）

- status: DISPATCHED
- 派单时间：2026-10-13 14:5x +08:00（协调者 r159，消费 `SPRAY-1900-20261013/notice.md` 调度调整 #3；用户 19:00 受控首包目标）
- owner：执行者 A（1号）｜任务：TASK-11S 发布准备子项（11S 本体仍 WAITING_GATES，本单只做**准备与只读预检**，不执行任何生产安装/迁移/切换）
- base：main `0e9a2df`（纯文档 tip，最后业务基线 `6fb42c4`）；新建专属 worktree `wt-01-t11sp`（分支 `a/task-11s-prep`）
- 运行环境说明：decoder/渲染/VLM 运行镜像已由环境 owner（Codex，用户指定）完成并 cross-host PASS（`rosbag-spray-runtime:20261013`，证据 `analysis/spray-runtime-install-20261013/evidence/`）——**A 不重复装环境、不重建镜像、不重复造迁移任务**（12S-A 零新 DDL）；A 负责的是「让生产具备可受控切换的部署物与证据」。

## 一、交付面（部署物 + 证据包）

### 1. 场景服务模板与部署入口（新增文件，A 独占域）
- `deploy/scene/scene-host.service` 模板：正式代理常驻单元（对应 16B 交付的 `scripts/scene_host_proxy.py` 运行口径）——解释器路径、`EnvironmentFile=/etc/default/rosbag-scene`（占位键：`SPRAY_MODEL_ENDPOINT`、`SPRAY_REFERENCE_DIR`、`SPRAY_DECODER_PATH`、`SCENE_EXEC_HOST=1`、回环端口）、`Restart=always`、工作目录。
- `deploy/scene/install_scene_host.sh`（**只生成不执行**）：安装/卸载/状态检查三分支，含幂等（已存在同 hash 不覆盖）、回滚段（disable+remove 保 journal）。
- 部署入口文档段：16B/12S-C 合入后从哪个 commit 取 `scripts/scene_host_*.py` 与镜像 tag 的一致性核对清单（commit sha ↔ 镜像 build digest 对照表模板）。
- 与 C 文件 owner 隔离：**不写 `scripts/scene_host_{proxy,orchestrator}.py` 本体**（C 域），模板只引用不复制；16C/16B 冻结文件零触碰。

### 2. 迁移与生产基线证据（只读生产 + 隔离实验）
- 生产只读预核（SSH 处理机，无免密 sudo，只用 docker/只读命令）：当前版本 `19b6db4-dirty` 与 dirty 文件清单（申报不修复）、alembic 当前头 `20260928_02`、Backend/Web 健康、旧代理 active 面、备份 timer 最后触发与**产物实际存在性**（timer active≠备份可恢复，核最近备份文件大小/时间戳/可打开）。
- 隔离迁移实验（本地 docker mysql:8.4 用完即毁）：从生产头 `20260928_02` 出发 upgrade 到候选链头（含 `20261013_01_scene_intake` 等 12S-A 所需，12S-A/B/C 未合入面按申报清单列「待合入后补跑项」，不预做）；记录每步 RC、耗时、行数。
- 车辆登记入口确认：`vehicle_code=test` 的**正式登记 API 路径与必填字段**（只读代码核对 + 本地栈实测一次 422/成功口径，不写生产库）；回执给出 17:30 发布窗可执行的一行登记命令模板。

### 3. 首包冻结材料
- 53s 候选包 `rosbag2_2026_10_08-14_42_48` 生产侧接收面核对：目标 incoming 路径权限/同文件系统/容量余量（只读 stat）、大小/时长/前雷达 topic 申报（环境 owner 已实测渲染 PASS，A 只补生产侧路径面）。
- 旧流水线活动任务核对口径：只读查当前派发/活动 run，回执列「17:30 维护窗口需确认的旧任务清单」，**不停抢任何在途**。

## 二、边界
- 零生产写入/零部署执行/零服务重启/零迁移在生产库运行；生产面全部只读命令。
- 不碰 `app/scene/spray/*`（B 返修在途）、`scripts/scene_host_*.py`（C 域）、16C 冻结面。
- 不建 cron/长驻进程；隔离容器用完即毁申报 0 残留。
- 发布执行本身属 11S 门禁面（G1–G6 + 用户 17:30 放行），本单完成≠授权发布。

## 三、自测/证据
- 服务模板：本地 `systemd-analyze verify`（或 docker 内等价口径）+ 安装脚本 `bash -n` + 幂等模拟（scratch 目录双跑）。
- 迁移实验：RC 矩阵 + 隔离容器 0 残留。
- 全仓回归口径：本单新增 `deploy/scene/*` 纯新增，跑 ruff（如适用）+ `git diff --check`；不动 app 面则声明零 app diff。

## 四、交付物
- 冻结 commit + 回执 `receipts/TASK-11S-PREP/attempt-1.md`（含：生产只读预核表、迁移实验 RC 矩阵、车辆登记命令模板、首包路径面、维护窗口清单、零残留申报）。
- 收口链：回执 → 协调者机械核验（预核命令可复核性）→ 纳入 17:30 发布决策材料（G1–G4 证据面之一）→ 11S 执行门禁仍按用户当次授权。
- **时限**：17:15 前交付（发布决策点 17:30）；ACK 时限 10min（A 当前空闲，12S-A 审查等待不占执行面冲突——12S-A 交付冻结 `77c395b` 在 OCR 排队，本单 worktree/文件域与其零交集）。