# TASK-16R：已输出发现和水雾审查债收口

2026-10-14T11:25:19+08:00用户明确要求，owner协调者。本单先盘点和裁决，不开发代码。入口 [v0.4恢复](../../control/V04-UI-RESUME-20261014.md)，[原15项与生产覆盖债](../../../reviews/TASK-16C/OCR-LEGACY-20261014.md)。

先核15项原日志逐条与当前seed/待交付修复的对应，保持C4驳回、C3部分误报、C3/c05-03共修。真实缺陷必须对应原AC回原owner，验证缺口交TESTER；低风险项修复或有证据书面裁决，不无声丢弃。更新逐项修复SHA/证据，不用一份TESTER总PASS覆盖全部发现。

同时查direct-r3的timeout、r4/r5/r6 PREPARED、release8e538bb例外、NAS3c9c496增量，输出有效覆盖映射与真实未覆盖当前代码范围。已被后续替代的旧版本无需重复跑；已有R4-01/02/ad60e41、12S-B/S9b、16A、07B闭环不重开。只对必要当前未覆盖面经ocr_runtime.py唯一入口串行prepare/start/status，先冻结actual base/head/背景/入选排除，不能起全部prepared或复制旧runner。

与UI三路并行；开发/测试准备不等盘点。父16最终收口前明确遗留结论，未覆盖写未覆盖，生产接受不撤销、不伪造审查PASS。必要返修碰A/B/C在途文件先检查点交接单写。旧强审grant REVOKED，不自动付费审查。回执 reviews/TASK-16R/attempt-1-disposition.md，含范围映射/逐项裁决/原接受引用/最终覆盖门禁及下一步。
