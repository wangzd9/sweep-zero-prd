# 续接声明：TASK-11S-PREP r1 卡死会话的磁盘进度保全（17:0x，协调者）

- 背景：A 上一轮巡检会话（16:06 起，53min）卡在 VLM 模型调用被协调者强制终止（`executions.db` 标 failed）。**卡死点在 r1 四项的第 1 项进行中**，磁盘进度如下，**新会话必须续用，禁止重写/回滚**：

## 已落盘的 r1 进度（wt-01-t11sp，未提交）

| 项 | 状态 | 位置 |
|---|---|---|
| r1-1 服务改 Docker compose 装配 | **代码已写完未提交**：`deploy/scene/scene-host.service`（约 +40 行改造，docker compose 受审代码只读挂载 /code、镜像 entrypoint source ROS 环境、宿主/容器依赖面修正，r165 勘误已消费进注释） | worktree 未提交 diff（`git diff` 可见） |
| r1-2 端点变量 SPRAY_VLM_ENDPOINT | 未见改动 | env.example/DEPLOY-ENTRY 待改 |
| r1-3 发布时点固定 SHA 口径 | 未见改动 | DEPLOY-ENTRY.md 待改 |
| r1-4 生产数据副本隔离升级实验 | 未见证据产物 | 待做（17:40 前最佳） |

## 新会话指令

1. **开工第一步**：`git -C wt-01-t11sp diff deploy/scene/scene-host.service` 读在途改造，核其正确性（对照 `runtime-install-handoff.md`/`runtime-template-check-1550.md` 勘误），**续用不重写**；若改造不完整则补完同一文件
2. 然后做 r1-2、r1-3（配置面小改），再 r1-4（副本迁移实验，隔离库操作，不触生产）
3. 一次冻结 commit（r1 四项+在途改造合并），回执 r1 段；17:15 目标已失，新目标 **17:40 前冻结**（17:30 停止点按"预核表+备份核验+维护窗口"放行、r1 作发布后首验补强——用户已知会）
4. 执行纪律：单个长命令（docker/ssh/迁移实验）必须带 timeout（≤300s），超 5min 无输出立即拆分；避免再次挂 VLM 长调用（拆步骤小步提交文档进度）