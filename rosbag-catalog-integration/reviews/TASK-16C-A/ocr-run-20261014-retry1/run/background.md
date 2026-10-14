# TASK-16C-A attempt-1 OCR 背景（协调者冻结）

- 任务：TASK-16C-A（查询/API 叶，父 TASK-16C）；REQ-16/05、AC-16/05。
- 授权来源：用户 2026-10-14 恢复 v0.4 最小界面闭环（见 inbox/control/V04-UI-RESUME-20261014.md）。
- base/head：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（未接受开发 seed，含已知缺陷）→ `ff2a005`（A 叶最终冻结 head，13:18 勘误续 commit）。
- 本叶业务文件：`app/services/bag_search_service.py`（共享多成员分类谓词+展示标签，Web/API 同源）、`app/services/scene_result_query.py`（切片/原始数据/全部三视图查询）。**tests 排除**（test_task16ca_query_api.py + test_web.py 归 TESTER 16D）。
- 关键不变量：
  - DESIGN §7.3.3 视图语义：data_kind 枚举不变，集合 GET 路径不变；双用途用多成员谓词，两类都命中且 UID 只一条。
  - OCR C5：共享多成员谓词，两个 data_kind 均命中并去重（勿回归单值 CASE）。
  - OCR C6：data_kind_labels_for 归一到共享分类真相。
  - OCR C7：日期原始字符串直入 DateTime 须容错，非法值不得 500。
  - 16C-c03-02/03/04：cursor 上下文须含实际筛选字段；旧 cursor scene_code None 与空串按旧编码契约归一；Python 分类与 SQL 子包条件一致（SCENE_SLICE 角色）。
- 测试证据（A 回执在案）：定向全绿 + 六文件合跑 108 passed + 全仓 1163 passed（4 failed 均为 seed 固有环境性，非候选回归）。
- 待核实风险：严格 MySQL 关键行为与浏览器取证归 TESTER 16D，本 OCR 不替代。
