---
task: TASK-04B
item: strongmodel-rework-cdr-align
owner: 2号
status: ACCEPTED
dispatched_by: 协调者（强模型审查 #2 high）
updated: 2026-10-09 16:5x
target: app/scene/slope/cdr.py（04B 已合入 main eaf632a，需返修 hotfix）
round: 1
---
# 04B 返修：CDR 解码未实现对齐（强模型 #2 high，已代码核实成立）

## 问题（我已核实）
`app/scene/slope/cdr.py:18` 注释明确"无对齐要求"，整个解码器所有字段**顺序直接读取，无任何 align(4)**。
但 CDR 规范里每个 uint32、字符串长度、sequence 长度字段都要求其**起始地址 4 字节对齐**（从封装体/CDR 对象起点算）。
强模型构造了 frame_id 长度触发 1/2/3 字节 padding 的合法 Image 与 CompressedImage，两者均复现：
`CdrError CDR string 长度越界：1280`（读到了错位后的长度值）。
现有 golden 样本只解析到 Header 尾部，没覆盖 header 之后 string 前的 padding，所以 58 passed 也拦不住。

## 修复要求
1. 以 **CDR 封装体/对象起点为对齐基准**（不是相对当前读指针），在每个 32 位字段、字符串长度、sequence 长度读取前 `align(4)`。
   - 注意：对齐基准应是 CDR 数据起始偏移（header 之后的 body 起点或整个封装起点，按你现有 header 解析的 body offset 定），
     padding 长度 = (4 - (current_pos - base) % 4) % 4。
2. 加入会产生 **1/2/3 字节 padding** 的独立 golden fixture（frame_id 长度分别为触发 1/2/3 字节的值，例如长度 1/2/3 的字符串），
   断言解码出的字段值正确、且 padding 被正确跳过。
3. 现有 58 定向测试 + 新 padding 测试全绿；`ruff check app/scene/slope/cdr.py`；`git diff --check`。
4. 你从 main 当前 HEAD 新建 hotfix 分支（勿动主工作区他人改动），改完 commit 到 worktree wt-04a，报 REVIEW_PENDING 给我。

## 验收（协调者）
- 我独立核实 align 逻辑 + padding golden 真实覆盖 1/2/3 字节；
- 派测试者用真实采集 bag 的 Image 样本复跑（你修完我会另发 TESTER 派单）；
- 合入 main + push origin。