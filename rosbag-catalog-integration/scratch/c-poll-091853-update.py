import pathlib

p = pathlib.Path('sessions/C.md')
s = p.read_text()
anchor = '- 最后更新：2026-10-11 00:19 +08:00'
entry = (
    '- 最后更新：2026-10-11 09:18 +08:00（v2 cron 巡检：preflight ACTIVE'
    '（checked_at 2026-10-11T09:18:53+08:00）、legacy_busy 空、leases 空'
    '（仅本轮 C 巡检短占用）；00:19 后共享根变更=2号 codex-r6 返修单 '
    'attempt-1-r2-rework-6（09:03，TASK-06B 范围，非 C）+ codex 裁决 '
    'reviews/codex-r6-fullchain-20261010-verdict.md（09:03）+ TODO 09:15 '
    '协调者刷新 + 各角色 ticks/sessions 巡检刷新，均非 C 范围；inbox/3号/ '
    '仍仅已收口 TASK-03B（最新单 10-10 00:58），**无 C 新派单**；main HEAD '
    '仍 `6d30a68`、wt-03b HEAD=`6f1a9ad` 干净（仅 .venv untracked）、无 C '
    '在途进程；**保持空闲待派单**。前一条 00:19 巡检见下）\n'
)
assert anchor in s
s = s.replace(anchor, entry + anchor, 1)
p.write_text(s)
print('updated')