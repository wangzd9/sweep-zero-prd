# 报告：TASK-07A attempt-1 统一界面·可见性与检索（页面实测 + 回归）

- 口径：自包含 uvicorn（worktree f94d006 代码，独立端口 18642，临时 SQLite，DEMO_DATA=0，场景夹具）；不触碰共享 real 栈/容器/宿主代理（有 1 RUNNING + 3 NVIDIA_DONE 在途，重建会 restart 代理，见回执越界申报）。
- 夹具：parent=0T07APARENT000000000000000（ORIGINAL）、cur=0T07ACUR0000000000000000（SCENE_SLICE AVAILABLE）、pend=0T07APEND0000000000000000（SCENE_SLICE PENDING）、run 0T07ARUNDONE（SCENE_DONE）/0T07ARUNQUEUE（SCENE_SLICE_QUEUE），scene_code=slope_t07a。

## 一、页面实测（12/12 段全 OK，逐段 needle 清单见下）

# TASK-07A 自包含页面实测证据
# base=http://127.0.0.1:18642 worktree=/home/wang/.local/state/rosbag-scene/wt-04a-t07a
# DB=/tmp/t07a_smoke.db DEMO_DATA=0 (临时 SQLite, 场景夹具)
# parent=0T07APARENT000000000000000 cur=0T07ACUR0000000000000000 pend=0T07APEND0000000000000000

== GET /bags (默认=当前可用切片) [200] expect_all=True
   OK  view-tabs
   OK  当前可用切片
   OK  原始包
   OK  全部/历史
   OK  0T07ACUR0000000000000000
   OK  data-label="场景"
   OK  slope_t07a
   OK  /bags/0T07APARENT000000000000000

== GET /bags?view=originals [200] expect_all=True
   OK  0T07APARENT000000000000000
   OK  slope_t07a
   OK  切片

== GET /bags?view=all [200] expect_all=True
   OK  0T07ACUR0000000000000000
   OK  0T07APEND0000000000000000
   OK  0T07APARENT000000000000000

== GET /bags?view=slices&scene_code=slope_t07a [200] expect_all=True
   OK  0T07ACUR0000000000000000
   OK  slope_t07a

== GET /pipelines?status=SCENE_DONE [200] expect_all=True
   OK  <option value="SCENE_SLICE_QUEUE"
   OK  <option value="SCENE_RUNNING"
   OK  <option value="SCENE_DONE"
   OK  场景切片
   OK  0T07ARUNDONE

== GET /pipelines?status=SCENE_SLICE_QUEUE (取消入口) [200] expect_all=True
   OK  0T07ARUNQUEUE
   OK  /pipelines/0T07ARUNQUEUE00000000000/cancel

== GET /api/v1/bags/<cur>/lineage (切片视角) [200] expect_all=True
   OK  "lineage"
   OK  "parent_bag_uid":"0T07APARENT000000000000000"
   OK  "slice_key"
   OK  "scene_code":"slope_t07a"
   OK  "analysis_version"

== GET /api/v1/bags/<parent>/lineage (原始包视角) [200] expect_all=True
   OK  "children"
   OK  "bag_uid":"0T07ACUR0000000000000000"
   OK  "bag_uid":"0T07APEND0000000000000000"

== GET /bags/<cur> (切片详情: 父包卡片+生成版本) [200] expect_all=True
   OK  父包追溯
   OK  /bags/0T07APARENT000000000000000
   OK  生成版本
   OK  cccccccccccc
   OK  获取数据

== GET /bags/<parent> (原始包详情: 场景状态区) [200] expect_all=True
   OK  场景结果
   OK  slope_t07a
   OK  切片数
   OK  SUCCESS
   OK  /bags?view=slices&scene_code=slope_t07a

== GET /nvidia (旧入口) [200] expect_all=True
   

== GET /ingest (旧入口) [200] expect_all=True
   

== GET /pipelines (旧入口) [200] expect_all=True
   


== /bags 默认视图 行片段 ==
…abel="Bag 名称"><a class="bag-link bag-name-cell" href="/bags/0T07ACUR0000000000000000?return_to=%2Fbags" title="0T07ACUR0000000000000000">0T07ACUR0000000000000000</a></td>
          <td data-label="场景"><div class="bag-scene-cell"><span class="badge bag-scene-badge">slope_t07a</span><span class="bag-scene-label" title="模…

== /bags?view=originals 场景列片段 ==
… value="">全部场景</option>
          
          <option value="slope_t07a" >slope_t07a</option>
          
        </select>
      </label>
      
      
      <label class="filter-field">
        <span>用途</span>
        <select name="purpose">
          <option value="">全部用途</option>
          <option value="scene_slice"…

== /pipelines 场景切片徽标片段 ==
… data-label="数据类型"><span class="badge pipeline-type" title="场景切片分析任务">场景切片</span></td>
          <td data-label="Bag"><a class="table-ellipsis" href="/bags/0T07APARENT000000000000000" title="0T07APARENT000000000000000">0T07APARENT000000000000000</a></td>
          <td data-label="队列"><span class="table-ellipsis" title=…

## 二、pytest / ruff（worktree f94d006）

- `pytest tests/test_task07a_visibility.py` → 6 passed RC=0
- `pytest tests -k "scene or web or bags or pipeline"` → 328 passed, 534 deselected RC=0
- `pytest tests -q` → 849 passed, 10 skipped, 3 failed（全部 test_devflow.py 沙箱用例 = worktree .git 文件态环境问题；主工作区同文件 24 passed RC=0，非本任务回归）
- `ruff check app tests` → All checks passed RC=0

## 三、关键行为核验（渲染片段）

（以下片段摘自证据文件对应段，needle 命中即真实渲染产物）

- /bags 默认视图：`view-tabs` 三 tab + 当前可用切片行含 `data-label="场景"`/`slope_t07a` + 父包链接 `/bags/0T07APARENT…`；PENDING 切片不在默认视图。
- /pipelines：`<option value="SCENE_SLICE_QUEUE"`/`SCENE_RUNNING`/`SCENE_DONE` 三选项 + 数据类型列 `场景切片` + 排队 run 行含 `/pipelines/0T07ARUNQUEUE…/cancel`。
- lineage API：切片视角 `"parent_bag_uid":"0T07APARENT…"` + `"scene_code":"slope_t07a"` + `slice_key` + `analysis_version`；原始包视角 `"children"` 含 cur/pend 两个 bag_uid。
- 切片详情：`父包追溯` + 父包链接 + `生成版本` + `cccccccccccc`（config_hash 前 12 位）+ `获取数据`（既有口径不回归）。
- 原始包详情：`场景结果` + `slope_t07a` + `切片数` + `SUCCESS` + 跳转链接 `/bags?view=slices&scene_code=slope_t07a`。
- 旧入口：/nvidia、/ingest、/pipelines 均 200；`view=all&dataset_type=self_built` 组合可用（AC-08）。

## 四、遗留/待核对

- 派单 2.3 列举的独立「角色（bag_role）」筛选下拉未做（三视图 tab 覆盖原始/切片维度、all+数据类型覆盖自建维度）——**待协调者裁决**，未改契约。
- 共享 real 栈复测（TESTER 独立验证口径）建议在无活动 run 窗口执行；本侧自包含实例已覆盖派单 2.5 三项。
