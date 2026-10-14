import sys, datetime
root = sys.argv[1]
ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M CST')
line = f"- 心跳：{ts}（5min 巡检 preflight checked_at 2026-10-11T07:16:53+08:00，ACTIVE，legacy_busy 空：main HEAD 仍 `6d30a68`（=origin，零前移，git 核实）；`inbox/1号` 零新派单/返修/释放通知（TASK-03B 最新仍 10-10 18:58 attempt-6-rework，本角色交付 `ceeac16` 已随 `0f6aa87` 合入 main 并验收；TASK-05 最新 10-10 01:18）；07:10 后项目变化仅各角色 sessions 记账与 B 一条 scratch 检查点，无本角色业务文件变化（find -newermt 核实）；wt-01 仍 `ceeac16` 干净冻结（仅未跟踪 .venv）；leases 仍见 `C.lock`/`TESTER.lock` 两个 0 字节残留（非本角色，不动待核）。**无本角色待办**，空闲不扩需求，等协调者释放槽/新单（聚合仅剩强复审 R2I-20261010-06 待用户手动触发，非本角色门禁）；claim→心跳记账→release）\n"
p = root + "/sessions/A.md"
with open(p) as f:
    content = f.read()
with open(p, "w") as f:
    f.write(line + content)
print("A.md updated")