#!/usr/bin/env python3
"""r101 checkpoint: append to sessions/COORDINATOR.md (read-first-then-write)."""
import pathlib

root = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
sp = root / "inbox/sessions/COORDINATOR.md"

CHECKPOINT = """
## 2026-10-12 21:16 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-12T21:10:53+08:00，r101）
- **20:55 后零业务交付**：main HEAD `502bf8e`（= origin/main，rev-parse 双核一致，07B 未合入）；共享根 20:55:53 后新增仅各角色例行 tick/心跳与 r100 协调者记账，无新回执/派单/decision/合入。
- **T07B r95 detached OCR 在途不变**：b9 `app/templates/detail.html` INFLIGHT（node pid 525278 起 20:51，elapsed 23:34，父 pid 464164 flock 持 `inbox/ocr.lock`）；b10+契约批 QUEUED；收口 7/10（b1/b2/b4/b6 0 findings、b3 1 medium 待裁决、b8 1 low 非阻塞、b5/b7 FAILED 待低负载 resume 最后一试）。vllm 负载实测 4 running/2 waiting（capacity）=非低负载期，**本轮不启动 b5/b7 resume**，等队列趋零。
- **角色占用**：A/B/C/TESTER 全空闲（B 21:08 nochange 心跳报 T07B 冻结等 OCR 收口，在案）；leases `A.json`/`C.json` 为本轮前后例行短租约；无他角色在途业务持有。
- **强审查**：授权在期至 2026-10-13 11:33（TASK-07B 范围）；滚动 60 分钟 0/5、本授权累计 0 次、无在途调用；pack 前置=OCR 收口+b3 裁决，本轮未起跑（巡检回合只读）。
- 本轮控制动作：claim（cron-coord-poll-14ae4556629a-20261012-211053-r101）→巡检核查（rev-parse 双核/vllm 负载/ps 525278 活性/ocr.lock/leases/事件复核）→append 检查点+event→release。**无新派单、无合入、无 OCR 起跑、无状态变更**。
- **下一步**：r102+ 核 `scratch/t07b/ocr/remaining_progress.txt` b9 收口→b10+契约批串行→vllm 队列趋零后 b5/b7 resume 最后一试→b3 medium 裁决（预判回派 B 单文件守卫最小返修）→强审查 pack→合入→TESTER 验证→07B DONE。
"""

prev = sp.read_text(encoding="utf-8")
assert "r101" not in prev, "r101 checkpoint already written"
sp.write_text(prev + CHECKPOINT, encoding="utf-8")
print("checkpoint appended, new size:", sp.stat().st_size)