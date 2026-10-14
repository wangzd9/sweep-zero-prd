import hashlib, json, pathlib

root = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
name = "C-poll-20261011-182853-ocr-c1c2-r1-v2-killed-obs"
sessions = root / "sessions" / "C.md"
old = sessions.read_text(encoding="utf-8")
new_line = (
    "- 最后更新：2026-10-11 18:3x +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T18:28:53+08:00）、"
    "legacy_busy 空；18:25:42 后共享根新增均核实为**非 C 范围**：`reviews/TASK-08/t08c-1/ocr-batches.md`（协调者 OCR C1C2-r1 批次账："
    "v1 runner 18:27 起跑因 stdout PIPE 缓冲+回合结束进程被终止、末 3 文件组 context canceled，v2 18:29:21 `--resume c56d992c` 断点续审）"
    "+ `TODO.md` 18:27:42（协调者 18:25 收口记账刷新）+ 各角色 sessions + `leases/COORDINATOR.json` 在途（owner cron-coord-poll-182053-t08c1-review）；"
    "**新观察（只读核实，非 C 范围不处置）**：OCR C1C2-r1 v2 runner 本轮实测已无活进程——`c1c2-r1.log` mtime 停 18:29:21（仅 start 行）、"
    "`c1c2-r1-state.txt` 0 字节、`inbox/ocr.lock` 无 holder（fuser 核实）、pid 2618840 已不存在（ps 核实）——"
    "与 D3-r1 21:26 先例同模式（化身/协调者回合结束被杀），**待协调者下轮按 §4 裁决 resume/重跑（硬截止 19:10）**；"
    "`inbox/3号/` 无新文件（最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（最新仍 17:01 c3-1 decision，1号范围），**无 C 新派单**；"
    "main HEAD 未变（`98f6c88`，wf-03b 内 rev-parse 核实）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、"
    "ps 核实无 C 在途业务进程（grep 命中仅微信 wxocr 非业务）；C 本轮短占用 owner `C-cron-poll-20261011-182853` 控制动作结束释放，"
    "事件 `C-poll-20261011-182853-ocr-c1c2-r1-v2-killed-obs` 已落盘（脚本 `scratch/c_poll_1828.py`）；"
    "2号 t08c-1 `bf48a45` 仍 REVIEW_PENDING **未合入**（等 OCR 收口→协调者 rebase `98f6c88` 复核→合入），非 C 范围；"
    "**保持空闲待派单**。前一条 18:25 巡检见下）\n"
).replace("18:3x", "18:31")
if "C-cron-poll-20261011-182853" in old:
    raise SystemExit("already recorded, skip")
sessions.write_text(new_line + old, encoding="utf-8")

ev = {
    "event_id": hashlib.sha256(name.encode()).hexdigest(),
    "occurred_at": "2026-10-11T18:31:00+08:00",
    "recorded_at": "2026-10-11T18:31:00+08:00",
    "role": "C",
    "task": "TASK-08",
    "attempt": "0",
    "status": "IDLE",
    "summary": "无C新派单；只读观察：OCR C1C2-r1 v2 runner(18:29:21 resume c56d992c)实测已无活进程，log停18:29:21/state 0字节/ocr.lock无holder，待协调者按§4裁决resume或重跑(硬截止19:10)；2号t08c-1 bf48a45仍REVIEW_PENDING未合入；main 98f6c88未变、wt-03b 6f1a9ad干净",
    "evidence": "c1c2-r1.log mtime 2026-10-11 18:29:21；c1c2-r1-state.txt 0B；fuser ocr.lock 无holder；ps -p 2618840 不存在；inbox/3号 最新10-10 00:58；inbox/coordinator 最新17:01(1号范围)",
    "next": "保持空闲待派单；OCR C1C2-r1 在途处置归协调者/2号范围，C不接管不催单",
}
evidir = root / "events" / "C"
evidir.mkdir(parents=True, exist_ok=True)
(evidir / (ev["event_id"] + ".json")).write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
print("sessions+event written")