#!/usr/bin/env python3
"""C poll 23:38: 巡检新增派单/共享根变更/仓库状态/租约/进程"""
import subprocess, json, os, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
REPO = "/home/wang/work/rosbag-catalog"
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"
SINCE = "2026-10-11 23:28:00"  # 前条 C 巡检写入时点

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

# 1. 共享根新增（排除巡检类目录）
rc, out, err = sh(f"find {ROOT} -newermt '{SINCE}' -type f "
                  f"-not -path '{ROOT}/sessions/*' -not -path '{ROOT}/events/*' "
                  f"-not -path '{ROOT}/ticks/*' -not -path '{ROOT}/scratch/*' "
                  f"-not -path '{ROOT}/inbox/control/*' -not -path '{ROOT}/nvidia-cleanup/*' "
                  f"-not -path '{ROOT}/.git/*' -not -path '{ROOT}/inbox/ocr.lock*' "
                  f"-printf '%TY-%Tm-%Td %TH:%TM:%TS %p\\n' | sort")
print("=== 共享根新增（排除巡检类） ===")
print(out or "(无)")

# 2. inbox/3号 与 inbox/coordinator 最新文件
for d in ["inbox/3号", "inbox/coordinator"]:
    rc, out, err = sh(f"find {ROOT}/{d} -type f -printf '%TY-%Tm-%Td %TH:%TM %p\\n' | sort | tail -5")
    print(f"=== {d} 最新5 ===")
    print(out or "(空)")

# 3. 仓库状态
rc, main_head, _ = sh(f"git -C {REPO} rev-parse --short main")
rc2, origin_head, _ = sh(f"git -C {REPO} rev-parse --short origin/main")
rc3, wt_head, _ = sh(f"git -C {WT} rev-parse --short HEAD")
rc4, wt_status, _ = sh(f"git -C {WT} status --porcelain | grep -v '^?? .venv' || true")
rc5, wt_branch, _ = sh(f"git -C {WT} rev-parse --abbrev-ref HEAD")
print(f"=== 仓库状态 ===\nmain={main_head} origin/main={origin_head} wt-03b={wt_head}({wt_branch})\nwt status(排.venv): {wt_status or '(干净)'}")

# 4. 进程
rc, ps_out, _ = sh("ps aux | grep -E 'wt-03b|scene-03b' | grep -v grep || true")
print(f"=== C 相关进程 ===\n{ps_out or '(无)'}")

# 5. 租约
rc, lease_out, _ = sh(f"find {ROOT}/inbox/control/runtime/leases -size +0c -type f "
                      f"-printf '%s %p\\n' 2>/dev/null || true")
print(f"=== 在途租约 (size>0) ===\n{lease_out or '(无)'}")