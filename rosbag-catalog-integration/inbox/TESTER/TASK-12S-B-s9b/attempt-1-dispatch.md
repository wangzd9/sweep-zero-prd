# S9b冻结快照独立增量复验（与OCR并行）

status: DISPATCHED；owner TESTER；2026-10-13用户直接纠正轮。先完成已领取16B-r2短定向单，然后接本单；不重复已通过旧B全仓或全部渲染。

- 固定base=0320a8e，head=f76e2a9（完整SHA从对象解析）；源树wt-04a-t12sb，隔离干净代码快照，不动开发树。仅decode.py/test_spray_adapter.py S9b增量，旧16条40用例PASS证据保留，必要受影响定向回归一次。
- 读现有S9b派单与帧映射契约和原TEST-TASK12S-BC-freeze报告，复用真实小包/镜像/独立1184消息44scan结束锚。真实调用本轮decode_packet_route，验证44PCD逐帧原始整数结束storage_ns和DB3/message范围一致，源包摘要不变，替换旧DECODE_FAILED确已成功。
- 现有新增矩阵：多DB3、重复/缺帧/首尾不完整/映射歧义/取消；核实际断言而非只看用例名。未知/失败不能NO_MATCH；不得删断言或模糊时间精度。
- 没有真实模型/NAS发布/生产写入许可在本单新增。无需重复534PCD或全批渲染；真实小包现成探针按新快照调整调用即可。环境使用已装镜像，原包只读。
- ACK/报告`test-receipts/TEST-TASK12S-B-s9b/attempt-1.md`：完整SHA、命令/rc、关键断言和未执行项；FAIL回B最小修复，不改业务实现，不批准合入。
