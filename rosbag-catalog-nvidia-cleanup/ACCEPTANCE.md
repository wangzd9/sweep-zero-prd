# NVIDIA 删除独立验收契约

版本：NC-v1，2026-10-10。**以下全是待实施验证场景，本轮未跑业务测试。**
需求来源 [PRD](PRD.md)，任务状态只读 [TODO](TODO.md)。

## 1. 快照和数据

TESTER 收到固定 catalog SHA、迁移 head、worker/helper 协议版本、实际 Compose 项目名/隔离库和批准测试路径；缺失任一项先补输入，不能在移动 main 上取证。远端真实测试额外要明确授权，仅对生成临时数据操作。

最小数据集：同一批次三个 Chunk（例如 33、34、330），33 有两个终态 run、帧和完整 origin/infer；34 正在运行；330 是名称相近的保留哨兵。再准备多个批次引用同 run、部分 SUBMITTING、孤儿帧/未知目录、NAS 原始/final 哨兵及目录外共享缓存。重新导入测试始终使用新的请求键并保存第一次操作审计。

## 2. 验收矩阵

| AC | 必须观察的行为 | 最低证据 |
|---|---|---|
| NC-AC-01 | 两开关分别控制自建/NVIDIA；NVIDIA 预览身份准确，取消零删除；跨会话/过期 nonce/摘要错/路径字段拒绝；刷新继续同操作。 | 开关矩阵、API 请求响应、浏览器截图、预览前后 DB/目录对比。 |
| NC-AC-02 | 33 的 origin/infer/全部 run/目录内 partial 与缓存清除；34/330/NAS/共享根保留。目标本来 ABSENT 正常处理。 | 冻结 plan、逐目标真实 lstat、前后目录树、保留哨兵 SHA256、source 业务 SQL 计数。 |
| NC-AC-03 | owner 缺失/错 revision/chunk/run、跨源引用、孤儿未知、非法历史根、祖先或树内 symlink、mount、inode 替换、权限错误全部阻断。 | 各反例的 blocker/HTTP/退出码，未删数据摘要；未检查项不能写 ABSENT。 |
| NC-AC-04 | preview 后新 run 使确认失效；confirm 与单/批 create 竞争有且仅一边可推进；自动重试/claim/资源/回报不绕过围栏；锁前目录不存在，孤儿子进程存活时不得删除。 | 两个独立 DB session 交错时间线；实际进程树/PID-start/flock/session；首次 mkdir 观测与目录保留。 |
| NC-AC-05 | 双完成才 SUCCEEDED；全部源业务/孤儿帧策略正确，共享对象保留；DB 故障使所有业务删除与 batch CLEANED 标记回滚；审计删除后可查。 | MySQL真实 finalize/故障注入、按source/run双向SQL核对、清理查询响应、保留快照。 |
| NC-AC-06 | 33 已清理、34 运行的批次不误报完成；多批同 run 都标 CLEANED；全部清理正确汇总；缺失未知显式对账；旧 batch key 和 SUBMITTING 恢复不能新建 33；run提交/item落账之间故障不能遗留无条目业务提交。 | 批次API/页面、条目数/原 JSON 快照、重放前后run/源/目录计数；事务故障注入、GET/link与finalize竞争不覆盖新结果。 |
| NC-AC-07 | origin 删完/infer失败不成功；SSH启动/删除结果未知先对账；worker重启续原计划；DB失败只重试DB；重试新目录/owner冲突拒绝扩大计划。 | 故障前后status链、不可变digest、executor记录、实际逐目录事实、重复执行次数。 |
| NC-AC-08 | 默认重导入拒绝；新键+成功cleanup_id生成g+1；错误/未成功编号拒绝；旧键即使有新代仍报SOURCE_CLEANED；旧run回调拒绝；同UID二次清理成功，两次审计互不覆盖。 | 两轮cleanup与源代次SQL、签名/锁meta证据、旧请求重放及新旧run对照、原审计摘要。 |
| NC-AC-09 | 自建清理、派生血缘保护、自建/NVIDIA正常任务/批次/帧导入不回归；旧helper拒绝新协议；生产默认新开关关闭，真实/模拟证据分开。 | 定向与适用质量门禁日志、Compose闭环、版本/能力矩阵、未执行项和环境界限。 |

## 3. 验证顺序与工具事实

开发者先完成定向 pytest、Ruff、compileall；涉及 config/Compose 做真实解析。NC-06 使用本地隔离 MySQL 和浏览器，对实际服务 API 驱动完整闭环；SQLite 单测不替代 MySQL 行锁、唯一竞争、外键与事务。

已有可读的 pytest 测试族为 `test_bag_cleanup_*`、`test_nvidia_control_plane.py`、`test_nvidia_batch.py`、`test_nvidia_pipeline.py`，已有本地入口 `scripts/local_stack.sh`、`scripts/run_bag_cleanup_mysql_test.py`、`scripts/run_bag_cleanup_browser_test.py`。它们当前只证明已有功能，新增 NVIDIA 场景需按任务实现；不能把“脚本存在”写成新能力验收通过，也不能把既有 A100 acceptance 脚本直接用于生产 NVIDIA 数据。

真实本地子进程生命周期测试是 NC-03/06 必须项；A100 真删为 NC-08 独立授权项。NC-06 可用映射临时目录实现端到端逻辑验证，报告明确标模拟传输。缺浏览器/MySQL/挂载权限时写 NOT_RUN 和影响 AC，不吞断言或缩小成功标准。

## 4. 交付与问题收口

报告包含 task/attempt、固定 SHA、环境、fixture身份、命令/退出码、期望/实际、日志/截图/SQL/目录摘要路径、失败恢复、未执行项。使用 PASS/FAIL/NOT_RUN，不以 HTTP200、目录空、全量pytest计数或文件存在单独判断成功。

失败按 NC-AC 与稳定问题 ID 回原任务，TESTER 不改实现、不跑 OCR、不批准合入。协调者收口后准备一份已有功能纠错审查包；审查者只纠正上述 AC，范围外性能平台或新功能建议不转本期必做。
