# 12S-B 帧映射（S9）契约补充通知（r159）
> 有效派单以 `inbox/2号/TASK-12S-B/attempt-1-rework-s9-dispatch.md`（r160）为准；本通知补充 TESTER 口径：B 侧 S9 帧映射面等 17 条返修新 head 后复验，其余面按原快照 `f62a29c` 继续；运行镜像 `rosbag-spray-runtime:20261013` 已就位（真实 decode/渲染不再 NOT_RUN）。

# 契约变更通知：12S-B 返修纳入 S9 帧映射（B 侧快照将更新）

- 时间：2026-10-13 14:5x +08:00（协调者 r159）
- 关联：`inbox/TESTER/TASK-12S-AB/attempt-1-dispatch.md`（13:5x 派单，固定快照 A=`77c395b`/B=`f62a29c`）

## 事实

- 独立运行环境（ROS2 Humble/PCL/Open3D 软件 EGL 镜像 `rosbag-spray-runtime:20261013`）14:3x 建好并 cross-host 验证 PASS；真实小包解码实测 packet 消息 1184 → PCD 帧 44（`is_last_scan` 边界），53s 候选包实跑渲染 PASS、原包不变。
- **B 冻结 `f62a29c` 的 `decode.py` 长度断言在真实包必失败（packet 路线不可用）**=新增 S9 [HIGH·CORRECTION]，已补入 B 返修单（`inbox/2号/TASK-12S-B/attempt-1-rework-addendum-S9.md`）。

## 对 TESTER 的口径调整

1. **12S-A 侧不变**：A=`77c395b` 快照、AC-18 验证面照旧推进，不受影响。
2. **12S-B 侧**：`f62a29c` 冻结验证中可继续完成不依赖 decode 帧映射的面（ns 映射/PCD 头/参考图/合成自洽等）；**packet 路线帧映射（S9 面）不要按 `f62a29c` 判定 FAIL 收口**——该项缺陷已确认且在返修，等 B 新 head 后由协调者发更新快照，按新 head 复验 S9 映射矩阵（多 DB3/重复/缺帧/首尾不完整 + 真实包 1184→44）。
3. **环境升级**：真实 decode/渲染从 NOT_RUN 转为可实跑——镜像 `rosbag-spray-runtime:20261013`（本机+处理机均 PASS 证据在 `analysis/spray-runtime-install-20261013/evidence/`）。独立验收阶段可用同镜像做真实解码探针（只读 bag、输出写 scratch/work），不 mock。
4. 15:15 推进目标：真实解码/渲染证据已由环境面产出（小包+53s 包 PASS），水雾阳性/正常段判定仍属算法 owner 面，TESTER 只取证不判识别质量。