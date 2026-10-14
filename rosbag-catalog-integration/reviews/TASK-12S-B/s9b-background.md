# TASK-12S-B 首轮返修及S9b增量背景

固定base=f62a29c，head=f76e2a9；仅审本次修复增量，原模块已完成初审，不重新审未变化历史。不新增算法/并发/文件系统兼容/UI需求。原REQ17/AC17及整数storage_ns、原包只读、双pass/参考图/过滤/抽样参数冻结不变。

本次16条修复：S1模型读取有效图而非已过滤删除的路径；S2work_dir绝对路径守卫；S3截断PointCloud2收敛；S4强度ROI mask与点一致；S5死分支注释；S6取消透传；S7颜色向量化等价；S8auto缺topic分类。T1 ldd失败fail-closed；T2decoder路径环境化；T3参考图错误归一；T4资产来源常量复用；T5/T6 PCD字段解析/缺省COUNT/拒compressed；T7 ASCII首值不丢；T8时间最近tie拒绝。对应40定向用例已在0320a8e由TESTER独立验证，真实渲染上色也通过，S9尚未被旧PASS覆盖。

S9b将packet消息数==PCD数的错误假设改为完整SeyondScan的is_last_scan帧边界映射；真实小包1184packet→44PCD。必须保持完整DB3/message范围、原整数结束消息storage_ns、顺序与源血缘；多DB3/重复/缺帧/首尾残缺按已冻结契约处理，不删校验冒成功，不从文件名ms*1e6替代原ns。原派单inbox/2号/TASK-12S-B/attempt-1-rework-s9b-dispatch.md及frame映射合同为依据，原包始终只读。

冻结工作树wt-04a-t12sb仅.venv未跟踪，无已跟踪改动；f76e2a9已提交，开发回执S9增补待owner落盘，不将缺回执当已测试。TESTER并行补新快照S9矩阵；OCR只负责代码/契约，本次测试文件由TESTER，不要求OCR重复跑昂贵环境。旧全仓失败devflow3/web1与base一致，不能因旧失败增加无关返修。

按共同调用链分两批完整文件：adapter/render/decode/time_map（筛选后的帧和时间轴传递）；pcd_io/precheck/references（格式、资产与前置失败）。每批保留相关上下游取证，完整diff与入选由固定入口冻结。真实问题须给原AC、触发和后果，偏好不阻塞。
