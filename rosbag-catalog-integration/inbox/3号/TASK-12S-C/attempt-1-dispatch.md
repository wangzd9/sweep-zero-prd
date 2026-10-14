# 派单：TASK-12S-C attempt-1 水雾正式接线（前置开发，硬依赖未接受=不做正式联调 PASS）

- status: DISPATCHED（前置）
- 派单时间：2026-10-13 13:5x +08:00（用户群内授权"加速"——C 修完 16B-r1 核验后无缝接本单，不等 16B/A/B 全部合入）
- 任务：12S-C 水雾正式接线（REQ-17、15、06、07 / AC-17.4、15、06、07；DESIGN §9.6 完整卡）
- owner：C（修完 16B-r1 机械核验/交付后接本单；两单串行同一人）
- **前置口径（关键）**：硬依赖 16B（`40ab818` 返修后 head）/12S-A（`77c395b`）/12S-B（`f62a29c`）**尚未全部接受合入** → 本单允许：
  1. 据 16B 冻结契约（DESIGN §7.3.2 八步编排/幂等/恢复/租约）+ 已交付的 `scene_host_orchestrator.py`/`scene_host_proxy.py`（r1 返修 head 为准）**先行编码水雾接线 + 模块自测**（用固定 SHA 的 A/B 产物做 import 级集成）
  2. **禁止**申报"正式联调 PASS"（9.6 卡明文：任何依赖未接受不做正式联调 PASS）
  3. 交付=代码冻结 + 模块自测证据 + "待 16B/A/B 合入后接线核验"标记；协调者在三依赖全合入后派**接线核验单**（真链冒烟），本单不重做
- base：main 届时最新（16B-r1 合入后的 head；若 16B 未及合入则以 `40ab818` 所在链为消费基线，回执注明）
- 16B/A/B 若 OCR 返修致 head 变动：本单消费面按新 head rebase 复核（协调者通知），不自行追移动分支

## 一、交付内容（9.6 卡产物面）
1. 正常 Orchestrator `/run` 八步**水雾**派发到 results/complete/reconcile：
   - EXTRACT/INFER/SEGMENT/WRITE 消费 12S-B 的 spray 适配器（固定 SHA import，不复制逻辑）
   - `mapping_basis=bag_storage_ns` **复用现有 offset=0 分支**（水雾无 header 偏移），并验证**旧坡道 header 轴无回归**（坡道一包恢复回归必跑）
   - 发布路径受控：`.staging/<run_id>/<attempt>` → 原子 rename 到 12S-A 的 spray profile 受控 slices 根
2. 水雾 manifest/预检消费 12S-B 产物（7 图 hash、PCD 预检、可用性）
3. 元数据/车辆绑定消费 12S-A 的 source_metadata（登记/回报面接线）
4. 恢复/幂等/租约复用 16B 既有机制，水雾不新开旁路（不复制未审代理）

## 二、自测/证据（9.6 卡清单，模块级）
- 同 run/attempt 重复、响应丢失对账、manifest/checkpoint 断点
- 模型/NAS/DB 失败路径、取消/租约失效
- 发布后补登记、源 hash 不变
- **旧坡道一包恢复回归**（header 轴无回归的硬证据）
- 真实 VLM 调用**不做**（留 12S-D 授权执行面）；渲染/判定用只读短包/合成

## 三、边界
- 不改 16B 代理行为面（消费其 API/模块；发现必须改 16B 代码→申报越界不擅改，协调者裁决回派）
- 不改 12S-A/B 产物（import 消费；接口不匹配→回执列差异，不自己改对方类型）
- 不碰 16C 冻结面/07B 文件；不部署生产
- 依赖未接受期间**不跑真链全冒烟**（防替身验证冒充集成通过）

## 四、交付物
- 代码冻结 commit + 回执 `receipts/TASK-12S-C/attempt-1.md`（REVIEW_PENDING，**显式标"待接线核验"**）+ 报告（模块自测证据表 + 旧坡道回归 + 三依赖消费 SHA 清单）
- 收口链：16B/A/B 全合入 → 协调者派**接线核验单**（真链冒烟+12S-D 输入）→ 本单 findings 增量 OCR → 强审（授权期限内）→ 12S-C DONE

## 五、启动条件
- C 完成 16B-r1 机械核验 + 增量 OCR + 强审 pack 起跑后接本单（ACK 时限：16B 核验链收口后 30min 内）
- 若 16B-r1 核验出 BLOCKED（非 OCR 面），本单顺延，C 先回 16B