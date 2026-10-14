import io
root = '/home/wang/work/doc/prd/rosbag-catalog-integration'
hb = io.open(root + '/scratch/tester-heartbeat-1315.md', encoding='utf-8').read()
p = root + '/sessions/TESTER.md'
s = io.open(p, encoding='utf-8').read()
if s.startswith(hb.strip().splitlines()[0]):
    print('already-prepended')
else:
    io.open(p, 'w', encoding='utf-8').write(hb.rstrip('\n') + '\n' + s)
    print('prepended')