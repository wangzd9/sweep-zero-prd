# TASK-16B attempt-2-r1 OCR 背景

## 交付
base `0208a73`（16B 冻结 head）→ head `40ab818`（r1 返修），只改 `scripts/scene_host_proxy.py`（+53/−11）+ `tests/test_scene_host_proxy.py`（+178）。零越界（orchestrator/fake_vlm/app/迁移未碰）。

## 本次修复的 6 个 OCR findings（r9 session 40e90fea 第9轮覆盖完整，协调者逐条独立核全 CONFIRMED）
- H1 :903 try_reserve 返回值丢弃=并发双写者 → 接住原子返回值，失败者按既有接收重判（already_running/409）
- H2 :485-490+FAILED 分支 post(RUNNING) 后 cur 不刷新→终态写静默跳过 → post 成功即 cur="RUNNING"（post 返回 target 或 None 显式区分）
- H4 :664-667 except 过窄（CapabilityError 继承 Exception 非 RuntimeError；fingerprint_bag 抛 ValueError）→ 工作线程静默死/ACTIVE 恒 409/recovery 不清 → 扩 except Exception 确保失败收尾恒执行
- H5 :397 config_hash 从 registry 默认重推 vs backend 冻结提交值→非默认参数 run 烧模型后 REGISTER 必 409 → 快照 entry 不存提交参数无法还原，按 fail-fast 下限：frozen_hash 与默认重推不等即 SpecError（不烧模型）
- H6 :182-186 原子写缺 fsync（recovery 真相源）→ flush+fsync 后 rename（同 remote_bag_lock 约定）
- L1 :523 steps 未按 attempt 过滤 → 与 _report_steps 对齐只读本 attempt 行

## 关键不变量（审查重点）
1. 幂等/单写者：同 (run_id, attempt) 重复 POST /run 返回同一接收，禁第二写者；H1 修复不得破坏 recovery 路径既有检查
2. 崩溃恢复：recovery 文件是真相源；H6 fsync 后恢复语义不弱化
3. 八步状态推进：STEP_TRANSITIONS 合法转换；H2 修复后 DONE/FAILED 终态 post 恒可达
4. 失败收尾：任何执行异常都走 stop threads/报 SCENE_FAILED/释放资源/清 recovery/移出 ACTIVE（H4 不得吞掉 SystemExit 语义问题——except Exception 不捕 BaseException 属预期）
5. 参数冻结：H5 fail-fast 不得误伤默认参数 run（frozen_hash 相等/缺失时行为不变）

## 测试证据
定向 32 passed（proxy 20 + orchestrator 12 独立复跑）、ruff 单文件绿、compileall 绿。

## 非本次范围
算法/帧判定/切包（app.scene 零动）、07B/16C 冻结面、生产部署。