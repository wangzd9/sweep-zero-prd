---
task: TASK-03B
item: verify-f11e617-f2-concurrency
owner: 测试者
status: TEST_REPORT_PENDING
base: 8bd5618（集成基线，main）
target: wt-03b HEAD f11e617c22e7a0174308d8981bb6d20a820d2dd4（F2 返修：patch_submission 内容列+row_version 合并进单条守卫 UPDATE + synchronize_session='fetch'）
worktree: /home/wang/.local/state/rosbag-scene/wt-03b
env: MySQL 8.4 docker（test-f2-mysql，镜像 6ea90827b110）+ python:3.10-slim（test-f2-py），同 docker network test-f2net；pymysql 1.1.1（容器内 pip 装 requirements.txt，VERSION_STRING 核实）
updated: 2026-10-09 17:00
verdict: PASS（三项验证全过 + 确定性守卫复测；含 1 项语义偏差报告，供协调者裁决）
---

# f11e617 F2 乐观锁并发隔离库独立复测（TESTER attempt-1）

## 被测快照（ACK 回写）
- wt-03b HEAD = **f11e617c22e7a0174308d8981bb6d20a820d2dd4**（`git rev-parse HEAD` 实测），工作区干净（仅未跟踪 .venv）。
- 被测函数：`app/services/ingest_service.py::patch_submission`（f11e617 diff：+45/-17，内容列与 row_version+1 合并进
  `UPDATE ... WHERE submission_id=:id AND row_version=:expected AND status='PENDING_INPUT'` + `synchronize_session='fetch'`）。
- 环境为**独立新建**隔离库（test-f2-mysql/test-f2-py/test-f2net，前缀 test-），未复用协调者/3号既有容器。

## 验证项与真实结果

### V1 双独立会话 Barrier 同拍竞争（patch_submission, row_version=1, key=None）
- 命令：`docker exec test-f2-py python3 /tmp/tester_f2.py`（脚本 /home/wang/.hermes/cache/scratch/tester_f2_v11e617.py），连跑 2 次。
- 结果（两次一致，exit=0）：
  ```
  V1 RESULTS: [('HTTP 409', 'ROW_VERSION_CONFLICT: submission changed concurrently'), ('OK', None)]
  V1 FINAL row_version: 2 status: PENDING_INPUT
  V1 VERDICT: PASS
  ```
- **确定性守卫复测**（排除"409 来自 row_version 预检"的可能，见 /tmp/tester_f2_det.py）：
  两会话各自**先开事务 SELECT（REPEATABLE READ，快照均见 rv=1）**→ Barrier 同拍调 patch_submission。
  SQL echo 日志抓到 **2 次守卫 UPDATE**（`SET row_version=(ingest_submission.row_version + %(row_version_1)s),
  selection_json=..., effective_config_json=... WHERE submission_id=... AND row_version=... AND status=...`），
  即双方都通过预检、都执行到守卫；输方 0 行 → 409，**无 StaleDataError**。
  ```
  DETERMINISTIC RACE RESULTS: ['HTTP 409 ROW_VERSION_CONFLICT: submission changed concurrently', 'OK']
  FINAL row_version: 2 status: PENDING_INPUT
  DETERMINISTIC_GUARD_VERDICT: PASS
  ```
- 判定：恰好 1 OK + 1 HTTP 409（守卫路径），row_version=2，输方内容不覆盖赢家（selection_json 为合法 scene_slice 选择）。**PASS**。
  与 3号自报（reviews/TASK-03B/attempt-2/f2-isolation-retest-evidence.log）一致，但本证据为独立环境独立脚本。

### V2 重放/幂等语义（关键：发现 1 项语义偏差，如实报告）
代码路径事实（ingest_service.py L370-379）：`idempotent_replay`（幂等账，operation=`ingest-submission-patch:{id}:v{row_version}`）
**先于** row_version 预检执行。实测：
```
V2 BASE (gen1→2, k2): ('OK', None) → rv: 2
V2 MID  (gen2→3, k3): ('OK', None) → rv: 3
V2a REPLAY (old gen, same payload+key=k2): ('OK', None) → rv: 3  content_stable: True
V2b KEY_REUSE (new payload, same key=k2): ('HTTP 409', 'Idempotency-Key was already used with different parameters') → rv: 3
V2c PLAIN_OLD_GEN (new payload, no key): ('HTTP 409', 'ROW_VERSION_CONFLICT: submission changed concurrently') → rv: 3
V2 VERDICT: PASS
```
- **V2a 语义偏差（报告项，不判 FAIL）**：派单注释期望"赢家后携旧 row_version=1 同 key 再发 → 应 409（非 200 重放，
  因 scope 含 row_version）"。实测同 payload+同 key 重放**命中幂等账回放首次响应快照（200 语义，rv=2 快照），
  代次停在 3、内容不变**——与 docstring"同一代次的重试回放首次响应"一致，是幂等账先于预检的既定设计。
  核心安全不变式全部成立：不推进代次、不改内容、不落写、不 500。
  **请协调者裁决**：(a) 接受 docstring 语义（同 key 同 payload 旧代次回放 = 幂等账快照，属合理）；
  (b) 若要求旧代次一律 409，则预检需移到幂等账之前（属业务语义变更，回派 3号 + 改 DESIGN §3.2.1）。
  本项不影响 F2 守卫缺陷的修复验证（守卫路径本身 V1/确定性复测已独立证实）。
- V2b/V2c：复用 key 换 payload → 409（hash 不匹配）；无 key 旧代次 → 409 ROW_VERSION_CONFLICT；均不落写。**PASS**。

### V3 连续两代
```
V3 RACE_GEN1: [('HTTP 409', 'ROW_VERSION_CONFLICT...'), ('OK', None)] → rv: 2
V3 GEN2_OK: ('OK', None) → rv: 3
V3 STALE_GEN2: ('HTTP 409', 'ROW_VERSION_CONFLICT...') → rv: 3
V3 VERDICT: PASS
```
代 1 并发竞争 → 2；代 2 串行 → 3；代 3 端再携 2 → 409。**PASS**。

## 环境细节（真实版本）
- MySQL 容器：`docker.m.daocloud.io/mysql:8.4`（本地缓存镜像 ID 6ea90827b110，无网络拉取），库 f2t1，root/t2testpw，同网容器名 test-f2-mysql。
- python 容器：python:3.10-slim（ID 6ff506466f8b，3.10.22），wt-03b 挂载 /work，pip 装 /work/requirements.txt（清华源）。
- **pymysql 版本坑（如实记录）**：容器内 `pip show pymysql` = **1.1.1**（符合派单锁定）；但 1.1.1 的
  `pymysql.__init__` 中 `__version__="1.4.6"` 是源码内 Django/mysqlclient 兼容伪版本（VERSION_STRING="1.1.1"），
  脚本打印的 "ENV pymysql: 1.4.6" 即此 `__version__`，非 1.4.6 真包。实际连接/事务/affected-rows 行为按 1.1.1 执行。
- 连接方式：`create_engine(url, creator=pymysql.connect 直连函数)` 绕开方言吞 ssl 的 1045 假象（派单提示，实测直连同网容器名可用）。
- 建表：`Base.metadata.create_all(engine, tables=[IngestProfile.__table__, IngestSubmission.__table__, ApiIdempotency.__table__])`。
- 定向回归（wt-03b @ f11e617，host .venv，PYTEST_DISABLE_PLUGIN_AUTOLOAD=1）：`pytest tests/test_ingest_config.py -q` → **21 passed**（exit 0，含 test_patch_concurrent_guard_zero_rows_returns_409）。

## 结论
**PASS**：F2 守卫缺陷修复在独立 MySQL 8.4 隔离库真并发下独立证实——输方直达 rowcount==0→409，
无 StaleDataError/500，row_version 推进与内容保护正确（V1+确定性复测+V2+V3 全部断言通过）。
**1 项语义偏差**（V2a：旧代次同 key 同 payload 重放走幂等账回放 200，而非派单注释预期的 409）
与 docstring/现有代码一致，核心安全不变式成立；**待协调者裁决语义预期**（见 V2 节 (a)/(b)），
如需变更则属业务语义（回派 3号 + DESIGN 修订），不阻塞 F2 修复本身采信。

## 证据文件
- /home/wang/.hermes/cache/scratch/tester_f2_run1.log（主脚本第 1 次全量输出）
- /home/wang/.hermes/cache/scratch/tester_f2_run2.log（主脚本第 2 次，稳定性确认）
- /home/wang/.hermes/cache/scratch/tester_f2_det.log（确定性 pin-transaction 守卫复测，含 2 次守卫 UPDATE 的 SQL echo）
- 脚本：/home/wang/.hermes/cache/scratch/tester_f2_v11e617.py、tester_f2_deterministic.py

## 收尾
- 验证容器已 `docker rm -f test-f2-py test-f2-mysql` + `docker network rm test-f2net`，`docker ps -a --filter name=test-` 0 残留（测试者自建前缀，未碰他人容器）。
- 未改任何业务代码/测试文件；未跑 OCR；未动生产/处理机/NAS。