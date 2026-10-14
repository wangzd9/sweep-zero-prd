---
task: TASK-03B
item: strongmodel-#1-critical-ruling
owner: 协调者裁决
status: DECIDED
updated: 2026-10-09 21:29
---
# 强模型 #1 critical 裁决：03B 迁移 TEXT server_default —— **误报，迁移完好**

## 证据（测试者 20:54 交付，协调者已复核）
- 干净 MySQL 8.4 完整升级链（base→head，非单独 02）**两遍 RC=0**，31 张表落地含三张新表
- general_log 实抓 `CREATE TABLE ingest_profile`：三个 TEXT 列真实 DDL = **`TEXT NOT NULL`，无 DEFAULT 子句**，未触发 1101
- 功能 INSERT 佐证：省略三列 → 1364（DB 层确无默认值，与 DDL 一致）
- 协调者独立复核业务路径：ingest_service.py L197-199 创建显式赋值、L85-87/222 读取 `or "[]"` 兜底 → **无裸 INSERT 依赖 DB 默认，无功能回归**
- 容器/网络/volume 0 残留

## 结论
强模型 "fresh compile 得 `TEXT NOT NULL DEFAULT '[]'`" 是对 `literal_binds`/方言编译路径的过读，
真实执行 DDL 未下发 TEXT 默认值。#1 critical = **误报**（与协调者 a8fac99 时期旧 general_log 实验结论一致，
本次由测试者在合入后 main 版本独立复测，证据闭环）。**03B 迁移（20261008_02）在 DDL 层面完好，#1 gate 解除。**

## 遗留观察（不阻塞，记录）
测试者发现：02 迁移 create_table 的所有 server_default 列真实 DDL 均未渲染 DEFAULT（01 迁移 add_column 的
bag_role 则保留 DEFAULT）——SQLAlchemy 2.0.41 MySQL 方言 create_table 路径行为。当前业务全部走 ORM 显式赋值，
无影响。若未来需要 DB 层列默认（防御 ORM 外直 SQL），属迁移变更，另行评估，不在本裁决范围。

## 对 03B 验收的影响
03B 剩余收口条件从「#1 gate + 3 条 high 返修 + F2」减为「3 条 high 返修（3号 attempt-4 开发中）+ OCR 补审」。
F2 并发（f11e617）已合入 9506457 且测试者独立 PASS。