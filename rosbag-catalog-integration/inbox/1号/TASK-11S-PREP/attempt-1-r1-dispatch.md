# TASK-11S-PREP attempt-1-r1 装配返修（用户 16:02 加速指令④ + 规划侧 15:54 勘误）

- status: DISPATCHED
- 派单时间：2026-10-13 16:1x +08:00（协调者）
- base：`d8f7206`（A 已冻结交付，wt-01-t11sp，4 文件 +230 `deploy/scene/*`）续 commit，只动 `deploy/scene/*` 与运维材料，不碰 app/scripts 业务面。

## 四处置返（规划侧 `runtime-template-check-1550.md` 已核实，协调者复核一致）

1. **服务启动方式**：`scene-host.service` 仍 `ExecStart=/usr/bin/python3 .../scripts/scene_host_proxy.py`（宿主机 Python）→ 改为**已验证的 Docker 镜像运行**（`rosbag-spray-runtime:20261013` 固定摘要，非 tag）；systemd 模板改 docker compose/service 装配或 docker run 常驻口径，镜像内解释器与依赖面以强模型线 `runtime-install-handoff.md` 为准
2. **模型端点变量**：`rosbag-scene.env.example` 第 15 行与 `DEPLOY-ENTRY.md` 的 `SPRAY_MODEL_ENDPOINT` → **`SPRAY_VLM_ENDPOINT`**，并核 `SPRAY_VLM_MODEL` 等配套变量名与代理代码实际读取面一致（以 `scene_host_proxy.py`/orchestrator 代码为准，不发明变量）
3. **部署一致性口径**：`DEPLOY-ENTRY.md` 要求"proxy 与 16B 旧 head 逐字节一致"已失效——12S-C 已新增 9 行 proxy 接线（`92dcb52`），16B-r2 也将在其后合入 → 改为**按发布时点固定 SHA 校验**（部署脚本读 `.deployed-git-revision` 式口径，发布前由协调者给出最终 SHA），不写死旧 head
4. **隔离迁移证据补强**：现证明的是**空库迁移链六步 RC=0**；补**生产数据副本升级兼容**实验（`19b6db4-dirty` 当前生产库的隔离副本 dump→恢复→升级→抽样核验，副本操作在隔离库，不触生产），材料含副本 sha256+升级前后行数/抽样字段对照

## 交付
- 冻结 commit（续 `a/task-11s-prep`）+ 回执更新 `receipts/TASK-11S-PREP/attempt-1.md`（r1 段：四项逐条处置+证据）
- 收口链：协调者机械核验（只读预核面复跑）→ 增量 OCR（`d8f7206..新head`，部署面小增量，排队 12S-C OCR 后）→ 并入 17:30 G4 证据包
- 时间：17:00 前冻结最佳（17:30 停止点输入）；**本单不授权任何生产写入**，远端安装仍等放行决策