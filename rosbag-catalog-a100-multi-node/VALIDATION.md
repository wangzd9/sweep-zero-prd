# MN-v1文档一致性验证

> 下文时间/摘要均为MN-v1原交付的历史快照。2026-10-12用户随后要求主线v0.4修订，专项入口新增“仅自建/NVIDIA、场景在处理机”的范围说明，因此这些摘要不代表当前文件；本轮文档检查以 [主线VALIDATION](/home/wang/work/doc/prd/rosbag-catalog-integration/VALIDATION.md)为准，未重新运行MN业务测试或改变其任务状态。

本文只记录本次文档验证，未来业务测试证据写对应任务回执，不把文档检查当作实现验收。

## 1. 验证范围

- 必需文件、五角色恢复入口、ROLE-BINDINGS JSON及实际脚本路径。
- MN-REQ-01～10、MN-AC-01～10、MN-01～10映射，任务依赖存在且无环，首波不超过三个。
- 首波共享文件owner及供应/消费顺序、事件接续、TASK/NC范围隔离。
- 相对文档链接/标题锚点、目录映射、两个节点各3槽、预算必填、UNKNOWN不释放、共享模型与历史兼容契约。
- 所有开发初始PLANNED，真实测试/生产WAITING_AUTH；control=UNBOUND，群/cron/worktree空，不存在派单或启动。
- 差异仅文档/JSON；无凭据、业务实现、部署快照或正式changelog变更。

## 2. 检查记录

实际检查时间：`2026-10-12T16:31:41+08:00`。结果：**DOCUMENT_CHECKS_PASS**。

执行一次性文档检查脚本 `python3 /tmp/a100-multi-node-check-docs.py`，并检查catalog的 `git diff --check`、差异范围和工作区。输出：

```text
PASS 必需文件 16 项
PASS 五角色入口/脚本引用，UNBOUND且无派单、cron或回执
PASS 10任务/10任务卡、完整无环依赖、三槽首波及阶段状态
PASS 10项REQ/AC定义和实现任务映射
PASS 72 个本地链接/锚点、尾随空白及私钥内容检查
PASS 5个上级文档与NC正文原始字节未改变，仅追加入口/补充
PASS catalog仅HANDOFF+文档入口，既有改动保留，git diff --check
PASS 手工契约核对：目录映射/同盘去重/每节点3槽/共享模型/预算必填/UNKNOWN不释放/NC条件能力与历史兼容
RESULT: DOCUMENT_CHECKS_PASS; BUSINESS_TESTS_NOT_RUN
```

检查脚本读取JSON、Markdown映射/链接、任务表并拓扑检查依赖；核对上级追加前的长度和SHA256以证明原正文保留；catalog HANDOFF去掉本次新增节后须与调查base原文逐字一致。文档修改不需要业务pytest、栈重建或代码OCR，均未执行。

首波文件owner、数据根与元数据根分离、历史副本旧键、UNKNOWN持久占用、源墓碑及NC条件能力还经过人工契约核对。静态检查不证明业务实现成立。仓库外文档没有Git，以下摘要作为本次内容快照。

## 3. 未执行项

MN-01～10实现及业务验收、MySQL迁移、真实A/B任务、峰值预算校准、SSH安装/远端目录写入、生产发布与本地栈重建均未执行。前序只读现场证据见[HANDOFF](HANDOFF.md)，不等于B具备运行依赖或已纳管。


## 4. 上级正文保留证据

仅追加入口/补充，追加前正文长度与SHA256：

| 相对上级根文件 | 原字节数 | 原SHA256 |
|---|---|---|
| `PRD.md` | 17666 | `45c1f3f2da18ac620a8c062b3aa90f40cd9ef34584688fa8ac7e5901fc793d09` |
| `DESIGN.md` | 39621 | `c240ef0351c7507ed5b620b9c871e7d301893d0a87f78bf1124348a8ac3011ba` |
| `TODO.md` | 82383 | `c7906c85c7e39f729c7b80ce306a666b877f4dbb8a2f2f4929ed653f34ecca9b` |
| `HANDOFF.md` | 147712 | `b1da16c7e4be16aee1f591873142b3fe6a529576bc8300672246c176acb5aa31` |
| `SESSION-START.md` | 2866 | `e378076d74d633c748bef58903cbc7d9dcd7b89132adc931fa709aed59073b14` |
| `nvidia-cleanup/DESIGN.md` | 21061 | `7743dc4fb1953cea3db189f20011440fc5f311f1e8f12f95bbabe22ed12ac897` |

## 5. 文件摘要快照

下表排除VALIDATION自身以避免自引用；最终交接更新后重新生成。SHA256只用于识别本次文档内容，不代表实现验证或Git托管。

<!-- mn-document-sha256 -->
| 文件（相对专项根） | SHA256 |
|---|---|
| `../A100-MULTI-NODE.md` | `a6aa269f600a74786c1320e58b431cdd85ee6f7b383297bbc80efe111ea6f6e3` |
| `../DESIGN.md` | `99269631581d80c8d096f61de30e87297614c7107859cfc0d5ba3f0c6e4e0cca` |
| `../HANDOFF.md` | `0856702cede64b024ac0a39aa23b39353c00eaf66dfd95268d384b271ef901f9` |
| `../PRD.md` | `196c7a44b4176897698faa70d3941d36273dd7b9ac89adb18edb923673b2e237` |
| `../SESSION-START.md` | `d7b0ed98ce38dd291dc384407c4e9dbce787bf0970f66e4c3f1998f660890da4` |
| `../TODO.md` | `670fa1b3d57111844113baa89b813e92ecc3a3bb0637d21b7c16ceed22e9d510` |
| `ACCEPTANCE.md` | `de9a121637bb956167b0900528322df3766297241ccb5bc525697ff85a796fd6` |
| `DESIGN.md` | `b69da5864a346cc0f3a51eec34b64c3230436d0241e9c978754a42105c0a361a` |
| `DEVELOPMENT-LOG.md` | `8ec1d4949960a565877ed352fa2dd44c61c94a4f8a7fa4aaecab03f4cbcc94d4` |
| `HANDOFF.md` | `1eae116b847226c4d38e3fef762401a78e5d65aa9384438e3e0adf934d9d7bbc` |
| `PRD.md` | `8fed2e2da0be4bd37ec960369baba8cc1d2f11c12da78710a4f143789145bb1a` |
| `ROLE-BINDINGS.json` | `b88df165c4469c2b6391e6126edb8ad7ab3e12c792ed9a4d370745866ea947b1` |
| `SESSION-START.md` | `3f57df927854799bd49620d369428240f0e8fa092a386e152ebe0e9acc234ae9` |
| `TIMELINE.md` | `35675df2943d6cd05680c2b3250623da79d1741cc905d2883ce702fe2fdf799b` |
| `TODO.md` | `3d206951eef7dcb01fdf427cce9aa4fbe86e9313fd2da4745e8993931c757be6` |
| `inbox/PROTOCOL.md` | `ffd6f99c088114db329fba64a6f1192725325e60205a9a248f85e839c41cc1bf` |
| `sessions/A.md` | `3649bf94891c4ad62c7b913ffb266b24a3a2d98fb06a571c476084fdf3ac74d9` |
| `sessions/B.md` | `50d05ca413627b847d99c1773dad509d278f2d07f5b0ab3857ee04ee73aafadd` |
| `sessions/C.md` | `68ca0a54336a104a72f3023bb63d40170209f435a1e273ad211f19408e65e911` |
| `sessions/COORDINATOR.md` | `75d9fb9a5df1c74222d424f3ea49539a7dd05ea0a36b698a9c0464e46ad33c29` |
| `sessions/TESTER.md` | `fc9b84559098c1c240a3b2b8b100034cffef484296b3e266b5664518b2a85008` |
| `../nvidia-cleanup/DESIGN.md` | `9d25386ac3db39e829fad01c5e86ec783cae57aba0c3fa14c834ba5c69be3d16` |
| `../../../../rosbag-catalog/HANDOFF.md` | `97053c85359e65b7390f25ba38347cbc554b40cbac47fe8e0ea658ff322d7414` |
| `../../../../rosbag-catalog/docs/a100-multi-node-planning.md` | `98aff330aa85db796d14d2768e459a97e2884523f8eff7ec9ca953ece76ed510` |

最终复核时间：`2026-10-12T16:42:00+08:00`。上述文档检查再次全部通过；摘要覆盖24份文件。catalog文档commit `30e55a368688376bb35be58f4d6e69bc3568bf8c`已同步github/main，业务代码/任务状态/绑定未变化。
