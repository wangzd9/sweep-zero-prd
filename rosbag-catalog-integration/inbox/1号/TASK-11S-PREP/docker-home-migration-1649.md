# 当前机Docker迁移维护窗口

用户要求Codex将Docker存储移到home释放根分区，现将短暂停当前机Docker/containerd，迁移全部镜像和数据卷并恢复原五容器。请暂勿新建副本MySQL；迁移完成后会追加通知。处理机生产服务不变。

g4r2于16:44:14结束：restore ERROR1114，随后缺表ERROR1146，RC_upgrade=1。RC_destroy=0只是销毁成功，不能作为实验PASS。请保留此失败证据，恢复阶段非零必须立即停止后续迁移/抽样，完整恢复成功后才升级。既有backup sha校验可复用。

**16:54恢复通知**：Docker及containerd已恢复，数据已迁到/home；原五容器healthy/运行中，原卷名保留。已见你的t11sp_g4按/home私有datadir重新启动，可继续完整恢复及副本升级，不再需要等待维护窗口。仍按restore rc=0再升级、升级rc=0再抽样执行。
