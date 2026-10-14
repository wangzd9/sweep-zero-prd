import datetime
s = open('sessions/C.md').read()
line = "- 最后更新：2026-10-12 00:13 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T00:13:53+08:00）、legacy_busy 空；inbox/3号/ 最新仍 10-10 00:58（TASK-03B 名下全部派单已收口），**无 C 新派单**；23:50 后共享根新增=协调者 TASK-10 取证单 ACCEPT_REPORT + 两笔回派（1号 t10-defect1-source-ready / 2号 t10-defect2-storage-offset，均已 ACK，owner 非 C）——非 C 范围；main HEAD `ca8730d`=origin（rev-parse 双核）、wt-03b HEAD=`6f1a9ad` 干净（仅 .venv untracked）、无 C 在途进程；C.lock 0 字节无在途租约；**保持空闲待派单**。前一条 00:08 巡检见下）\n"
anchor = "## 2026-10-12 00:08 巡检"
i = s.find(anchor)
assert i >= 0, "anchor not found"
s = s[:i] + line + s[i:]
open('sessions/C.md','w').write(s)
open('events/C/C-poll-20261012-001353-nochange.md','w').write("# C poll no-change 2026-10-12 00:13\n\n- checked_at: 2026-10-12T00:13:53+08:00（preflight，cron poll f01517c16f2f）\n- 无 C 新派单；23:50 后共享根变化=协调者 TASK-10 ACCEPT_REPORT + 1号/2号 两笔回派（均已 ACK），非 C 范围\n- main `ca8730d`=origin；wt-03b 干净（HEAD `6f1a9ad`）；C.lock 0 字节；无 C 在途进程\n- 保持空闲待派单，未进行业务动作\n")
print("ok")
