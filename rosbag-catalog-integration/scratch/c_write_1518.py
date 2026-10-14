import io, os, sys

ROOT = '/home/wang/work/doc/prd/rosbag-catalog-integration'
ENTRY_P = os.path.join(ROOT, 'scratch/c_entry_1518.md')
TARGET = os.path.join(ROOT, 'sessions/C.md')
DRY = os.path.join(ROOT, 'scratch/c_sessions_dryrun_1518.md')

entry = io.open(ENTRY_P, encoding='utf-8').read()
assert entry.startswith('- 最后更新：2026-10-12 15:24 +08:00'), 'entry signature bad'
if not entry.endswith('\n'):
    entry += '\n'
assert entry.count('\n') == 1, 'entry must be exactly one line + newline'

old = io.open(TARGET, encoding='utf-8').read()
old_lines = old.splitlines()
new = entry + old
new_lines = new.splitlines()

# assertions before touching shared file
assert new_lines[0].startswith('- 最后更新：2026-10-12 15:24 +08:00'), 'new first line'
assert '最后更新：2026-10-12 14:44' in new_lines[1], 'prev 14:44 entry must be line 2'
assert len(new_lines) == len(old_lines) + 1, (len(old_lines), len(new_lines))
assert new.endswith(old), 'append-only prefix invariant'

# dry run against temp target first
with io.open(DRY, 'w', encoding='utf-8') as f:
    f.write(new)
dry = io.open(DRY, encoding='utf-8').read()
assert dry == new
os.remove(DRY)

# final write to shared file (last step)
with io.open(TARGET, 'w', encoding='utf-8') as f:
    f.write(new)
verify = io.open(TARGET, encoding='utf-8').read()
assert verify == new, 'post-write verify failed'
print('OK new_lines=%d old_lines=%d' % (len(new_lines), len(old_lines)))