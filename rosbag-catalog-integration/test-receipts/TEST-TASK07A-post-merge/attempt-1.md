# 测试回执：TASK-07A 合入后独立验证（main `caf385b`）attempt-1

- 时间：2026-10-12 14:4x +08:00（TESTER cron poll 167580c0500b）
- 派单：`inbox/TESTER/TASK-07A/post-merge-verify-dispatch.md`（协调者 14:01，coord-poll-20261012-133053）
- 被测快照：**main `caf385bfdb865a4d660b0f0e68fca5969615b38a`**（= origin/main，本轮 rev-parse 实测 HEAD 一致；--no-ff 合入 `f94d006` + `8cc6b80`）
- 口径：自包含 uvicorn `127.0.0.1:18791` 独立端口 + 临时 SQLite `/tmp/t07a_pm_smoke.db`（DEMO_DATA=0），主仓 `.venv` python3.10，未触碰共享 real 栈/容器/宿主代理/MySQL；夹具自造自清（1 ORIGINAL 父袋 + 1 AVAILABLE 切片 + 1 PENDING 切片 + 1 历史版本 + 2 SCENE run），结束后 uvicorn 退出确认、临时 DB 删除、0 残留（ps/文件实测）。
- 脚本：`/home/wang/.hermes/cache/scratch/t07a_pm_verify.py`（真实 HTTP urllib 断言，非 TestClient；全量日志 `/tmp/t07a_pm_final.log`）
- 结果：**32/32 PASS，RC=0**

## 一、finding #1：view-tabs 筛选保留（9 项全 PASS）

- `/bags?q={cur}&page=2` 渲染三 tab href 均携带 `q={cur}`（3/3）；`page=2` 与 `page=1` 均不出现（**page 归 1 即省略**）；slices tab href=`/bags?q={cur}`（无 `view=`，裸语义）；`view=originals`/`view=all` 各显式 1 次。
- `/bags?scene_code={scene}&view=originals` 三 tab 均保留 `scene_code`（3/3）。
- `/bags?q={cur}&dataset_type=self_built&view=all&page=3` 三 tab 均保留 q+dataset_type，`page=3` 不出现（多筛选组合不丢）。
- 无筛选 `/bags` 三 tab 逐字符退化为旧裸路径：`/bags`、`/bags?view=originals`、`/bags?view=all`（**旧书签不回归**）。

## 二、finding #2：col-scene 宽度（6 项全 PASS）

- `/static/bag-search.css` 实测含 `.col-scene { width: 150px; }`、`.col-name { width: 18%; }`、`table-layout: fixed`。
- `/bags` 渲染 `<colgroup>` 实测 **9 个 `<col>`**（col-name/col-scene/col-status/col-started/col-vehicle/col-type/col-size/col-actions/col-chevron），`<thead>` 9 个 `<th>` 与 9 列闭合一致。

## 三、attempt-1 面不回归（12 段口径，17 项全 PASS）

1. `/bags` 默认视图：三 tab + 当前可用切片行（含 `data-label="场景"`/`slope_pm_t07a`/父包链接）；PENDING 切片行**不出现**（默认视图排除）。
2. `/bags?view=originals`：父包行 + 场景 + `切片` 标注。
3. `/bags?view=all`：切片（AVAILABLE+PENDING）与父包行都在。
4. `/bags?view=slices&scene_code={scene}`：scoped 行正确。
5. `/bags?view=bogus` → **400**。
6. `/pipelines?status=SCENE_DONE`：SCENE_SLICE_QUEUE/SCENE_RUNNING/SCENE_DONE 三选项可见 + `场景切片` 徽标 + 行内 SCENE_DONE run 在、SCENE_SLICE_QUEUE run 不在 + Bag 列跳父包详情。
7. `/pipelines?status=SCENE_SLICE_QUEUE`：排队 run 行 + `/pipelines/{run}/cancel` 取消入口。
8. lineage 切片视角 `/api/v1/bags/{cur}/lineage` → 200：`parent_bag_uid` 指向父袋 + `slice_key` + `scene_code` + `analysis_version` + `config_hash` 全在。
9. lineage 原始包视角 `/api/v1/bags/{parent}/lineage` → 200：JSON 解析断言 `lineage=null` + `children` 恰含 cur（**pend 挂第二父袋的历史版本，按 AC 正确不属该父**）+ scene_code 正确。
10. lineage 不存在 bag → **404**。
11. 切片详情 `/bags/{cur}`：父包追溯 + 父包链接 + 生成版本 + config_hash 前 12 位 `cccccccccccc` + 获取数据（既有口径不回归）。
12. 原始包详情 `/bags/{parent}`：场景结果 + scene + 切片数 + SUCCESS + 跳 `/bags?view=slices&scene_code={scene}` 闭环。
- 附：旧入口 `/nvidia`、`/ingest`、`/pipelines` 均 200；`/bags?view=all&dataset_type=self_built` 组合 200（AC-08）。

## 四、pytest / 回归口径（主仓 `.venv`，main `caf385b` 直跑）

- `pytest tests/test_task07a_visibility.py` → **7 passed** RC=0（1.99s）。
- `pytest tests -k "scene or web or bags or pipeline"` → **329 passed**, 534 deselected, RC=0（16.03s）——较 attempt-1 的 328 +1 为新增 tab 筛选保留测试，无回归。

## 五、问题与未执行项

- 无 FAIL。未执行：截图断言（派单明确 innerText/渲染断言即可）；真实样本/生产链路（本单=模板/css/只读 API 面，无迁移无镜像依赖，生产门禁独立于本单）。
- 取证差异说明：lineage 原始包视角 attempt-1 needle（children 含 2 包）为本单夹具按父袋精确断言口径，pend 属第二父袋，断言语义与 attempt-1 AC 一致，非行为回归。

## 六、结论

**PASS**——finding #1/#2 行为断言成立、attempt-1 面 12 段口径不回归、pytest 全绿。交付 `TEST_REPORT_PENDING`，等协调者裁决 07A DONE→派 07B（或 FAIL 回派 B，本单无 FAIL 路径）。