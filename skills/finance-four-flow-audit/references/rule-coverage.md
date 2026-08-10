# 规则资产覆盖矩阵

本表用于安装和版本验收。规则只在需要时按 SKILL.md 指引读取，不应每个案件重复注入全部文本。

| # | 规则资产 | Skill 内文件 |
|---|---|---|
| 1 | 岗位认知与红线 | `../SKILL.md` |
| 2 | 四层数据模型 | `data-model.md` |
| 3 | 文件处理十三阶段 | `workflow.md` |
| 4 | 文件名与伴随文字映射 | `file-index-and-mapping.md` |
| 5 | 文件索引与专业分类 | `file-index-and-mapping.md` |
| 6 | 合同专业处理 | `contracts.md` |
| 7 | 银行流水专业处理 | `bank-statements.md` |
| 8 | 单笔回单与回单集合 | `receipts.md` + `../scripts/receipt_split.py` |
| 9 | 发票与发票二维码 | `invoices-and-qr.md` |
| 10 | 货物流与履约 | `goods-flow.md` |
| 11 | 招投标与中标 | `bidding.md` |
| 12 | 项目与项目流水汇总 | `project-and-summary.md` |
| 13 | 合同收付款审核 | `contract-payment-audit.md` |
| 14 | 四流一致审核 | `four-stream-audit.md` |
| 15 | 法人主体与交易对象 | `entity-identity.md` |
| 16 | 固定工具箱与调用边界 | `toolkit-boundaries.md` |
| 17 | 受控写入与验证闭环 | `controlled-write-closure.md` + `quality-and-operations.md` |
| 18 | 真实环境只读验收 | `installation-and-readiness.md` |

`type-specific-closure.md` 是跨类型执行总规程；其他参考文件提供事实、关系、质量和自主评估的横向规则。若专册与横向规则产生冲突，采用更严格、更加 fail-closed、证据要求更高的一项，并记录冲突。
