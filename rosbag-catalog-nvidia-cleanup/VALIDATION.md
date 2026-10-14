# NC-v1 文档校验记录

日期：2026-10-10（北京时间）。校验范围仅新专项及新增入口，不代表实现验收。

本轮已实际执行以下文档检查：

| 检查 | 结果 |
|---|---|
| 14 份 Markdown 的本地链接 | 45 个链接全部可解析，无失效目标。 |
| ROLE-BINDINGS JSON/绝对根/运行脚本/会话入口 | 解析通过；5 个角色的 session 存在，群/cron/worktree 均为 NULL，未伪造绑定。 |
| 需求/验收/任务卡 | NC-REQ-01～09、NC-AC-01～09 均存在并有任务映射，9 张任务卡齐全。 |
| DAG/状态 | NC-01/02/03→04→05→06→07→08→09 无环；NC-01～07 为 PLANNED，08/09 为 WAITING_AUTH，后续扩展 DEFERRED。 |
| 新增文档空白 | 15 个新增文件（含入口和 JSON）实际执行 `git diff --no-index --check /dev/null <file>`，无空白错误；UTF-8/尾换行检查通过。 |
| catalog 工作区保护 | `git diff --check` 通过；HEAD 仍为调查版本 `74ba3bfa5d75d87db5f38ba83a65d8b9f888da38`，已有未跟踪文件集合保留，无业务源码改动。 |
| 人工契约复核 | 校正实际批次页面 `/nvidia/batch/{batch_id}`、旧删除设计相对路径；明确单 Chunk 范围、NAS保留、新开关默认关闭、原计划恢复、run/item同事务和二次删除代次隔离。 |

检查使用开发机 Python 标准库对 Markdown 本地链接、JSON、任务表与 DAG 做断言；不是业务实现测试。`git diff --no-index --check` 的新增差异退出码 1 与错误文本分开判断，不把正常新增当空白失败。

业务 pytest/MySQL/浏览器、SSH、OCR、迁移、部署、删除均**未执行**：本轮是规划请求，没有改业务实现，也未获本专项运行授权。文档在非 Git 管理的仓库外 doc 根，未创建源码 commit 或推送。
