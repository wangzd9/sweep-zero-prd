# 上线后五角色刷新核验

2026-10-14 10:54 +08:00记录。用户已明确要求原角色恢复既定收尾；本次没有新建cron、重启gateway、修改模型参数或写生产数据。

- 五个原poll均enabled，当前prompt均为上线后收尾入口；5分钟错峰、skills、模型/provider、脚本、origin/deliver和workdir保留。
- 协调者20分钟/08点和个人11/15/18报告均enabled且no_agent；已废弃idle报告仍disabled；gateway及独立observer timer实测active。
- 已写当前控制入口及四角色原attempt增补，更新PROTOCOL/BASELINE/批次HANDOFF/TODO恢复说明与BATCH当前检查点，短协调lease写入后释放。历史材料保留，角色session/ACK未由Codex代写。
- 提前唤醒最初误用系统Python3.10，返回正则编译错误；改用服务实际Python3.11.16后原生提示扫描五份PASS。原生cronjob run五项均success=true、executed=false、already being fired，实际pid均存在，防止重复启动正常；不能当作五个新会话已启动。
- observer已扫描并保存五role pending，均含当前closeout入口。原角色在安全点/后续poll接续，未消费不代ack。
- 协调者已实际修改 `inbox/TESTER/TASK-11S-BATCH-1012/ruling-104x-codex-binding-verify.md`，明确并入POST-SPRAY-CLOSEOUT和当前测试增补，避免两份重复领取。四角色的新增ACK仍以其自身文件为准，本核验不预报全部ACK。
- 历史备份已移出observer观察树，保存到 `/home/wang/work/.local/spray-runtime/post-spray-closeout-before-20261014/`，避免将过时派单备份误读为新动作。

证据：role-audit.json、refresh-result.json（首次唤醒错误保留）、native-wake-result.json（正确解释器复核）、verification.json、observer-scan.txt。实际完整角色租约token未写入这些证据。

后续：协调者/执行者/TESTER按当前入口完成原收尾；大包在途持续保留，UI暂停、平台大包优化等ros2_slice交付。水雾实际生产优化分析见 `/home/wang/work/doc/analysis/spray-batch-progress-20261014/PRODUCTION-READINESS.md`，该分析不代替原AC/实现授权。
