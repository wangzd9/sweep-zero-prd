# TASK-16C-C attempt-1 回执（执行者C，冻结交付）

owner：C；状态：REVIEW_PENDING（CC-R1 返修冻结 commit `ce5921d`，等协调者独立核 diff + TESTER 独立验证；C 不合入/不部署）。
初版交付时间：2026-10-14T12:12:00+08:00；CC-R1 返修交付时间：2026-10-14T13:15:00+08:00。

## CC-R1 返修段（2026-10-14，返修单 `inbox/3号/TASK-16C-C/cc-r1-rework-dispatch-20261014.md`，ACK `cc-r1-ack.md` 13:08 在案）

- 新 head：`ce5921dcd9df71b295f58404a8d74e0dbac9e6bd`，续 commit 于 `522bb3f`（不新开 attempt），分支 `c/task-16cc-pipeline-detail`，worktree `wt-c-16cc`，`git status` 干净（仅未跟踪 `.venv` 符号链接，不入 diff）
- 文件清单（`git diff --stat 522bb3f..ce5921d`，共 2 文件 +8/-2，无越界）：
  - `app/templates/pipeline_detail.html`（+1/-0）：数据血缘兜底 `{% else %}` 分支（scene_lineage 存在但 lineage/children 均空）补 `<ol class="lineage">` 开始标签，兜底 `<li class="muted">` 文案与 muted 类不变，`</ol>` 不再悬空
  - `tests/test_task16cc_scene_detail.py`（+7/-2，C 独占新文件）：`test_no_lineage_fallback_li_in_ol` 同步断言兜底 `<li>` 位于 `<ol class="lineage">` 开始标签之后（`before.rfind` 命中且该标签到 li 之间零 `</ol>`）、`</ol>` 之前（li 后 60 字符内），不再只断言 `</ol>` 存在
- RED→GREEN 证据（环境：wt-c-16cc `.venv` Python 3.10，pytest 8.4.1，SQLite 临时库）：
  - 新断言对旧模板（`git stash push -- app/templates/pipeline_detail.html` 还原 522bb3f 模板）实测 **FAILED**（`assert -1 != -1`，开始标签缺失被捕获）
  - 修复后单测 `test_no_lineage_fallback_li_in_ol` 实测 **1 passed**
- 复跑（返修单要求口径）：`.venv/bin/python -m pytest tests/test_task16cc_scene_detail.py tests/test_task16c_ui_minimal.py -q` → **31 passed**（16+15，零失败；seed 固有 test_devflow/test_web 失败不在本两文件内，原口径不计本账）
- 审查口径执行：diff 严格限定在模板血缘兜底分支 1 行 + C 测试断言 1 面两小面内，**按返修单不整叶重跑 OCR**，交协调者在 `ce5921d` 上独立核 diff 与实际文件；若协调者判定超面，转增量 OCR 由协调者按唯一入口处理
- 越界申报：无；未动 seed/旧 B 冻结树/主仓/A/B owner 文件，未部署未合入未起 OCR，未跑付费强审
- 状态：c05-04 修复闭环待核；C 叶 REVIEW_PENDING，16R 盘点对 c05-04 账可更新为「修复已交付待独立核」（协调者面）

---

（以下为初版 attempt-1 冻结回执，保留原文）

## base/head（初版）

- base（固定开发 seed，未接受、带已知缺陷）：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（分支 `plan/v04-ui-resume-20261014`）
- head（本叶冻结增量，初版）：`522bb3f`，分支 `c/task-16cc-pipeline-detail`，worktree `/home/wang/.local/state/rosbag-scene/wt-c-16cc`
- 父完整增量口径：`63bfcf8..集成候选` 由协调者生成固定候选时核；本叶只提交 seed 之后自己的增量。

## 文件清单（初版，diff --stat bd0db1d..522bb3f）

- `app/web/pipelines.py`（C 独占）：`SCENE_TERMINAL_STATUSES`+`scene_terminal(run)`（C3/c05-03）；`_scene_phase_summary` 删 NO_MATCH 不可达 elif（C1）；`_scene_environment_paths` 删未使用 run 参数（C2）；新增 `_scene_model_identity(run)`（C9）；`pipeline_page` 渲染上下文同步
- `app/templates/pipeline_detail.html`（C 独占）：刷新控制收敛到 `scene_terminal` 单一来源（c05-03）；retry-form DOM guard（C8）；NVIDIA 契约按 `pipeline_type`（c05-05）；血缘兜底 li 容器（c05-04，初版半修，CC-R1 收口）；模型身份「未登记」口径（C9）
- `tests/test_task16cc_scene_detail.py`（新增 359 行，C 独占新文件）

## 自测（初版，环境 wt-c-16cc）

- `tests/test_task16cc_scene_detail.py` → 16 passed
- `tests/test_task16c_ui_minimal.py tests/test_web.py tests/test_scene_slice_lineage.py tests/test_scene_result_storage.py` → 90 passed + 2 failed（seed worktree 同序复现，顺序敏感非本增量引入）
- 全仓 → 1144 passed, 4 failed（seed 固有），10 skipped

## 未执行项/缺证

- 真实浏览器 C8 无 JS 异常取证=TESTER 面
- 严格 MySQL 复现/联测=TESTER 16D 面
- 父 `63bfcf8..` 完整增量与三叶联合验收=协调者固定候选后
- 未部署、未合入、未起 OCR（C 无 OCR 权限）

## 越界申报（初版）

- 无：只写 C 独占三文件；`.venv` 为 worktree 内符号链接未入库
- 11S 只读观察面按 5 分钟巡检继续，与本单共用同一 C 租约单写