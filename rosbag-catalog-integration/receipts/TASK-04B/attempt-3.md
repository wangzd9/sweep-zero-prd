---
task: TASK-04B
attempt: 3
item: strongmodel-rework-cdr-align
owner: 2号
status: REVIEW_PENDING
base: 8bd5618
output_commit: 34c380d
branch: hotfix/task-04b-cdr-align
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
updated: 2026-10-09 17:20
---
# TASK-04B attempt-3 交付（CDR 对齐 hotfix，强模型 #2 high）

## 交付内容（2 文件，+232/-30）
- `app/scene/slope/cdr.py`
  - 新增 `_align4(pos, base)`：把读指针**只向前**对齐到下一个 `base+4` 的倍数
    （`pos + (4-(pos-base))%4`），`base` = CDR 体起点（封装头后=4，裸 CDR=0），
    正是派单要求的"以 CDR 封装体/对象起点为对齐基准（不是相对当前读指针）"。
  - 解码端在**每个 32 位字段**读前对齐：header 的 Time(iI)、frame_id 字符串、
    height/width(II)、encoding 字符串、step(I)、两个 sequence 长度(I)。
    `_read_string` 改为"先对齐读指针再读长度"，保证字符串字节紧跟长度字段
    （旧实现 length 对齐读、字节未对齐读，padding 会混进字符串起点）。
  - 编码端 `encode_image` / `encode_compressed_image` 按**同一规范补 padding**，
    使本仓库 encode 的字节与真实 ROS2 序列化逐字节一致（此前只在特定 string
    长度下"碰巧对齐"，如 golden frame_id len=19 → 19+1=20 恰好对齐，掩盖了
    `height` 前的缺失对齐）。
- `tests/test_slope_adapter.py`
  - `_spec_raw_image` / `spec_raw_compressed`：**独立按 OMG CDR 规范构造**的
    golden 样本（不依赖本仓库 encode，规避自洽往返盲区）。
  - `test_padding_golden_image_1_2_3_bytes`：frame_id 长度（含 NUL）=2/3/5 →
    `height/width` 前 padding 分别 2/1/3 字节；断言 `end==len(blob)` 精确消费、
    各字段值正确，并断言 observed padding 覆盖 `{1,2,3}`。
  - `test_padding_golden_compressed_image`：同规范覆盖 CompressedImage 的 format
    字符串前 padding。
  - `test_old_unaligned_reader_misreads_padded_sample`：反向证明——对同一条
    含合法 padding 的样本，旧"顺序直读"在 padding 字节处读 height 得到垃圾值
    （≠480），锁定"无对齐=bug、样本确实触发 padding"。

## 验证（命令 + 真实退出码）
- `.venv/bin/python -m pytest tests/test_slope_adapter.py -q` → **35 passed**，exit 0
- `.venv/bin/python -m pytest tests/ -q -k "scene or slope"` → **179 passed**（含
  真实 A100 golden header 锚定 + 端到端 dispatch + writer CDR 抽验），exit 0
- `.venv/bin/ruff check app/scene/slope/cdr.py tests/test_slope_adapter.py` →
  **All checks passed!**，exit 0
- `git diff --check` → 无输出，exit 0
- 独立 probe（scratch）确认：`encode_image` 后 `decode_image` 对 fid len=2/3/5
  全部精确消费且 height/width/encoding/step/data 值正确；golden frame_id
  `camera_/dev/video2` 往返 `end==len`。
- 未执行项：全量 pytest（700+ 用例，非本 hotfix 范围；cdr 仅被 scene/slope
  的 bag_io/writer + 2 个测试文件引用，均已被 179 用例覆盖）。

## 待协调者验收的要点 / 契约选择说明
1. **对齐坐标系**：解码端在 `sub=data[pos:]` 切片上读，`base` 取"体起点在 sub 内的
   绝对偏移"（封装头后=4，裸=0），与 `_encap_candidates` 的 body_pos 一致；
   `pad=(4-(pos-base))%4` 恒 ≥0，只向前不回退。编码端同一坐标系（pos=base+len(body)）。
   两端公式完全一致，已用 probe 逐字节核对。
2. **编码端补了 padding**：这是必要的——真实 ROS2 序列化在 `height/width`、
   `encoding`、`step`、`sequence 长度`前都会按体起点对齐补 0~3 字节 `\x00`。
   旧编码只在特定 string 长度下恰好对齐，导致 writer 切片抽验对含 padding 的
   frame_id 会"编码不补、解码却跳过"而错位。现在编解码对称。
3. **越界申报 0**：只改 `cdr.py` + 其定向测试文件，未动 bag_io/writer 逻辑
   （它们调用接口签名不变）、未动 TODO/HANDOFF/DESIGN、无环境产物入 commit
   （.venv 为软链，已排除在 add 之外）。
4. hotfix 分支 `hotfix/task-04b-cdr-align` 自 main HEAD `8bd5618` 新建，
   未触碰 worktree 原分支 `scene/task-06b`（76d2958）与他人改动。
5. 派单提到"另发 TESTER 派单用真实采集 bag 的 Image 样本复跑"——本 hotfix 已让
   解码/编码对真实 ROS2 padding 逐字节一致，TESTER 复跑预期直接绿；如样本
   frame_id 长度触发 padding 而旧 golden 未覆盖，正是本次补的场景。