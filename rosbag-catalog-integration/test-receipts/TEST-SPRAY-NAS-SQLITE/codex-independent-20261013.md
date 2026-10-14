# CIFS NAS SQLite复制后只读验证

- 结论：**PASS。本地完整关闭的SQLite复制到当前NAS后，普通mode=ro能够读取；同盘rename后、Backend容器的/public只读映射下仍能读取。**
- 真实执行：2026-10-13 20:15:20 +08:00，处理机 `dataprocess-Legion-Y9000P-IAX10H`。
- 仅机械文件夹具；无业务DB/API写入、无原包/现有run改动、无模型、无挂载配置变更。

## 环境与隔离范围

- 处理机NAS：`/mnt/nas_backup`，CIFS3.0，现有挂载保持。
- Backend容器：`rosbag-catalog-backend-1`，镜像 `sha256:450e67af2ea380d4fb5d56b398574433bfcc6168a34cd48766add0644a735149`。
- 已核容器只读挂载：host `/mnt/nas_backup/rosbag_scene_processing/slices` → `/public/rosbag_scene_processing/slices`，RW=false。
- 本地唯一新夹具：`/home/data-process/spray-runtime/nas-sqlite-probe/copy-9c2b9fd65e74`。
- NAS唯一新夹具：`/mnt/nas_backup/rosbag_scene_processing/slices/.staging/nas-sqlite-probe-20261013/copy-9c2b9fd65e74`。
- 夹具与证据保留，未删除其他路径。

## 实际结果

1. 处理机本地创建DELETE journal模式SQLite，topics/messages表、64条消息，commit并显式close全部连接，fsync；无WAL/journal sidecar。
2. 复制关闭后的单DB3到NAS `unpublished/probe.db3`，fsync并核SHA一致。
3. NAS普通 `sqlite3.connect(file-uri+'?mode=ro', uri=True, timeout=1)`：count=64、quick_check=ok，0.0268秒。
4. NAS同文件系统将 `unpublished` rename为 `published`；普通mode=ro再次count=64、quick_check=ok，0.0171秒。
5. `docker exec`在真实Backend容器中从 `/public/rosbag_scene_processing/slices/.staging/nas-sqlite-probe-20261013/copy-9c2b9fd65e74/published/probe.db3` 普通mode=ro读取：count=64、quick_check=ok，0.0973秒。
6. 本地源、NAS复制、rename后及容器读取SHA均为 `7ce3f30f9cbc485165b049fd519115675c30234395850f6fcd009b551eebbfe3`。

全部8个检查true，脚本/SSH退出码0。所有读取都未使用immutable/nolock或全局放宽锁。

## 证据与限制

- 脚本本机先落盘：`/home/wang/work/.local/spray-runtime/nas-sqlite-copy-probe-20261013.py`，py_compile通过后scp处理机执行。
- 处理机结果：`/home/data-process/spray-runtime/nas-sqlite-probe/copy-9c2b9fd65e74/result.json`。
- 本机结果副本：`/home/wang/work/.local/spray-runtime/nas-sqlite-copy-probe-20261013/result.json`。
- 本机完整输出：`/home/wang/work/.local/spray-runtime/nas-sqlite-copy-probe-20261013.log`。

该结果支持“本地建库、完全关闭、复制NAS、同盘rename”的部署修复方向。验证对象是64条机械SQLite夹具与真实CIFS/容器只读路径，未将其描述为真实首包切片/发布/入库已通过；后续仍需真实切片闭环证据。未重新在CIFS直接创建SQLite复现，因为派单仅要求验证关闭后的本地DB复制可读性。既有测试Skill覆盖，不新建Skill。
