import sys, datetime as dt
sys.path.insert(0, '/home/wang/.codex/skills/complex-task-coordinator/scripts')
import role_runtime as rt

root, data = rt.binding('/home/wang/work/doc/prd/rosbag-catalog-integration')
print('root =', root)
lease = rt.load(rt.lease_path(root, 'C'), {})
print('lease =', {k: v for k, v in lease.items() if k != 'token'})
print('now =', dt.datetime.now().timestamp(), 'expires =', lease.get('expires_at'))
token = lease.get('token')
try:
    l = rt.valid_lease(root, 'C', token)
    print('valid_lease OK (token from lease file)')
except Exception as e:
    print('valid_lease FAIL:', e)
try:
    l = rt.valid_lease(root, 'C', 'f62d8af122b44e92aa40591c03e423c0')
    print('valid_lease OK (token from claim stdout)')
except Exception as e:
    print('valid_lease FAIL (claim stdout token):', e)
print('tokens_equal =', lease.get('token') == 'f62d8af122b44e92aa40591c03e423c0')