# 16B-r2 增量OCR裁决（Codex用户纠正轮）

固定40ab818..e152465；run4492b7f6，session d56113ca-0ca7-4042-829e-f5fc15154f65。17:42:30独立服务收口rc=0，manifest完整selected1/completed1/failed0、指纹一致；已核完整base/head及provider/model。3条findings逐项裁决，不能报告零发现。

1. M1 目录fsync应吞EINVAL/ENOTSUP：OUT_OF_SCOPE（支持范围扩展）。原R1-05明确掉电保证限于受支持文件系统，本次实现docstring同样限制ext4/xfs等POSIX；没有要求不支持持久化的文件系统也接受任务。吞掉错误会在未证明耐久时接受运行，不能为统一另一个辅助函数而弱化此契约。正式部署须验证私有state/work实际文件系统支持fsync；这个部署证明留在G4，不将新兼容需求派返修。一般I/O故障的恢复仍按原H4审查，若强审证明既定可达缺陷则另行裁决，不把本项解释为所有I/O故障均已验证。
2. L1 建议新增errno import：关联M1假设补丁的依赖，现有实现不引用errno，无实际NameError；NOT_A_DEFECT，不派单。
3. L2 日志cur未赋DONE：当前输出是原状态->目标状态，打印RUNNING->DONE并不自相矛盾。FAILED分支的日志准确性可作非阻塞维护，未证明状态转移受损；NON_BLOCKING，不因日志格式重烧整文件OCR。

结论：本轮OCR无已确认阻塞CORRECTION，OCR门禁解除；强审R1-01～05复核和独立测试仍待完成，未批准合入、更未放行生产。目录FS支持在部署核验，不增加通用兼容开发。
