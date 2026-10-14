"""T07B 真 MySQL 8.4 隔离库迁移 upgrade/downgrade 往返实测（派单三、T03/T04 教训）。

用临时 docker 客户端容器挂载 worktree 跑 alembic；隔离库 t07b_isolated + 独立用户，用完即毁。
"""

import subprocess

WORKTREE = "/home/wang/.local/state/rosbag-scene/wt-04a-t07b"
DB = "t07b_isolated"
USER = "t07b_iso"
PASS = "t07b_iso_pass_2026"
ROOT_PASS = "rosbag_catalog_root_local"
URL = f"mysql+pymysql://{USER}:{PASS}@mysql:3306/{DB}?charset=utf8mb4"


def run(*args, **kw):
    return subprocess.run(list(args), capture_output=True, text=True, cwd=WORKTREE, **kw)


def docker(*args):
    r = run("docker", *args)
    if r.returncode != 0:
        print("DOCKER FAIL", " ".join(args), r.stderr[-2000:])
        raise SystemExit(r.returncode)
    return r.stdout.strip()


def alembic_in_container(*cmd):
    r = run(
        "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
        "-v", f"{WORKTREE}:/wt", "-w", "/wt", "-e", f"ALEMBIC_DB={URL}",
        "docker.m.daocloud.io/python:3.10-slim", "/bin/sh", "-c",
        f"pip install -q pymysql alembic sqlalchemy=={open('/wt/pyproject.toml').read().split('sqlalchemy')[1][:40].split(chr(34))[1]} 2>/dev/null; python -m {cmd}",
    )
    print(f"$ alembic {cmd}")
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print(r.stderr[-3000:])
    return r.returncode


# 简化：直接用 backend 镜像跑 alembic（依赖齐全），只换 DATABASE_URL
def alembic_backend(*cmd):
    image = docker("images", "ls", "--format", "{{.Repository}}:{{.Tag}}")
    backend_img = [l for l in image.splitlines() if "rosbag-catalog" in l and "backend" in l]
    img = backend_img[0] if backend_img else "rosbag-catalog-local-backend:latest"
    r = run(
        "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
        "-v", f"{WORKTREE}:/wt", "-w", "/app",
        "-e", f"DATABASE_URL={URL}",
        img, "sh", "-c", f"alembic {cmd}",
    )
    print(f"$ [{img}] alembic {cmd}")
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print("STDERR:", r.stderr[-3000:])
    return r.returncode


# 1) 建隔离库+用户
docker(
    "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}",
    "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot",
    "-h", "mysql",
    f"-e",
    f"DROP DATABASE IF EXISTS {DB}; CREATE DATABASE {DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; "
    f"DROP USER IF EXISTS '{USER}'@'%'; CREATE USER '{USER}'@'%' IDENTIFIED BY '{PASS}'; "
    f"GRANT ALL PRIVILEGES ON {DB}.* TO '{USER}'@'%'; FLUSH PRIVILEGES;",
)
print("== isolated db created ==")

# STRICT 口径（对齐既有测试约定）
r = run(
    "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql",
    "-e", f"SET GLOBAL sql_mode='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';",
)
print("sql_mode set rc=", r.returncode)

# 2) 找 backend 镜像
r = run("docker", "ps", "--format", "{{.Image}}")
imgs = [l for l in r.stdout.splitlines() if "backend" in l]
print("backend image:", imgs)
img = imgs[0].strip() if imgs else ""
if not img:
    print("NO BACKEND IMAGE — abort")
    raise SystemExit(2)


def run_in(img, workdir, env, cmd):
    r = run(
        "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
        "-v", f"{WORKTREE}:/wt", "-w", workdir, f"-e", f"DATABASE_URL={URL}",
        img, "sh", "-c", cmd,
    )
    print(f"$ {cmd}")
    out = (r.stdout or "")[-2500:]
    err = (r.stderr or "")[-2500:]
    if out:
        print(out)
    if err and r.returncode != 0:
        print("STDERR:", err)
    return r.returncode


# 3) upgrade head（隔离库从空到 head，含新表+新索引）
rc = run_in(img, "/wt", None, "alembic upgrade head")
print("UPGRADE rc =", rc)
if rc != 0:
    raise SystemExit(1)

# 4) 核验新表+索引（STRICT 建表语义）
r = run(
    "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql", DB,
    "-e", "SHOW CREATE TABLE scene_manual_revision\\G SHOW INDEX FROM scene_manual_revision; SELECT version_num FROM alembic_version;",
)
print(r.stdout)

# 5) 插入边界行：全字段+边界长度（26/32/128/512/255）
boundary_ok = run(
    "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql", DB,
    "-e",
    f"INSERT INTO scene_manual_revision (bag_uid, scene_code, action, operator, reason, bag_row_version, idempotency_key, original_label_ref, created_at) "
    f"VALUES (REPEAT('A',26), REPEAT('B',32), 'REVISE', REPEAT('O',128), REPEAT('R',512), 7, REPEAT('K',255), REPEAT('L',255), NOW()); "
    f"SELECT id, CHAR_LENGTH(bag_uid), CHAR_LENGTH(operator), CHAR_LENGTH(reason), CHAR_LENGTH(idempotency_key) FROM scene_manual_revision;",
)
print(r.stdout if boundary_ok.returncode == 0 else boundary_ok.stderr)
print("BOUNDARY INSERT rc =", boundary_ok.returncode)

# 6) 写入超宽值 → 必须 1406（验证列宽语义真实生效）
r2 = run(
    "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql", DB,
    "-e",
    f"INSERT INTO scene_manual_revision (bag_uid, scene_code, action, operator, reason, bag_row_version, created_at) "
    f"VALUES (REPEAT('A',27), REPEAT('B',32), 'REVISE', 'O', 'R', 1, NOW());",
)
print("OVERSIZE INSERT rc =", r2.returncode, "(expect !=0, 1406)")
print((r2.stderr or r2.stdout)[-600:])

# 7) downgrade -1 → 表消失
rc = run_in(img, "/wt", None, "alembic downgrade -1")
print("DOWNGRADE rc =", rc)
if rc != 0:
    raise SystemExit(1)
r3 = run(
    "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql", DB,
    "-e", "SHOW TABLES LIKE 'scene_manual_revision'; SELECT version_num FROM alembic_version;",
)
print("after downgrade:", r3.stdout)

# 8) 再 upgrade head → 往返闭环
rc = run_in(img, "/wt", None, "alembic upgrade head")
print("RE-UPGRADE rc =", rc)
if rc != 0:
    raise SystemExit(1)
r4 = run(
    "docker", "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql", DB,
    "-e", "SHOW TABLES LIKE 'scene_manual_revision'; SELECT version_num FROM alembic_version;",
)
print("after re-upgrade:", r4.stdout)

# 9) 清理：drop 库+用户
docker(
    "run", "--rm", "--network", "rosbag-catalog-local_default",
    "-e", f"MYSQL_PWD={ROOT_PASS}", "docker.m.daocloud.io/mysql:8.4", "mysql", "-uroot", "-h", "mysql",
    "-e", f"DROP DATABASE {DB}; DROP USER '{USER}'@'%';",
)
print("CLEANUP DONE — t07b migration MySQL 8.4 roundtrip PASS")