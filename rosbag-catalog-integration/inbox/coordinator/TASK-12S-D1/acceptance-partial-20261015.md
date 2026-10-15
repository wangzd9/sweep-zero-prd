# TASK-12S-D1 接受口径（协调者，2026-10-15 11:05 +08:00）

## 结论
- **D1 转"部分交付接受（可测试性复核 PASS，真实面维持 BLOCKED）"**。
- 依据：TESTER 10:10 回执 `test-receipts/TEST-TASK12S-D1/testability-review-attempt-1.md`（6 项逐条只读取证）+ 协调者 10-14 20:5x 机械核验（8 包 bytes/DB3/topic/duration/SHA 与冻结 manifest 逐项一致）。
- D1 零代码改动，不走 OCR；本口径即为接受终态。

## 6 项结论核销
| # | 项 | 结论 | 处置 |
|---|---|---|---|
| ① | 已证阳性×4 | 可测 PASS（标识真实、终态一致）；口径注记 1 条（16_00_13 切片写成 NAS 形态，非断点） | C 下次交付顺手更正记法，不返修 |
| ② | 输入适用性×3 | 可测 PASS（NOT_APPLICABLE=topic 清单实证非推断） | 关闭 |
| ③ | 无效输入×1（空包） | scanner 拒绝 PASS；**断点=提交层无拒绝终态（恒 PENDING_INPUT）** | **由 12S-F 交付面补上**：F `6798059` 新增 ingest_submission INPUT_REJECTED 终态+reason_code 持久证据（29 处相关实现）。F 接受后此断点消除，D2 的无效输入用例可重算 |
| ④ | 16_02_03 跨 DB3 | 不可测（DB run 滞留 SCENE_CANCELLING + 跨 DB3 边界未定位） | 滞留缺陷候选入 16R（不代修）；跨 DB3 边界=D2 材料缺口，等上游 |
| ⑤ | 五项 BLOCKED_MATERIAL | 阻塞原因=上游材料缺失（非测试方法缺陷），无"材料已可取但没人取"项 | owner=上游/业务侧，材料齐即重算用例 |
| ⑥ | 批次总量口径 | 可测 PASS（抽查 2 包与 manifest 一致） | 关闭 |

## D2 维持 BLOCKED（不变）
缺五材料（人工真值区间/真实正常阴性/真实车辆映射/质量接受阈值/跨 DB3 命中）；断点③由 F 补上后，D2 有效输入用例面扩大，其余维持。

## 备注
- TESTER 回执"轻微口径注记"不阻塞接受，登记在案。
- 16_02_03 滞留 SCENE_CANCELLING 的缺陷候选与 4acf 大包同族（取消链收尾），恢复大包时一并核。