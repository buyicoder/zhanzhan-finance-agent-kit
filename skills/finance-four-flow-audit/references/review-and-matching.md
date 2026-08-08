# Agent 审核与匹配规则

## 目录

1. 证据等级
2. 匹配硬约束
3. 合同视觉审核
4. 合同与银行流水匹配
5. 发票匹配
6. 履约凭证匹配
7. 特殊交易类型
8. 错误纠正

## 一、证据等级

Highest to lower weight:

1. 可见签字/印章的原始页面，以及银行或发票原始事实；
2. 已与页面版式相互核对的可读原文；
3. 带来源链接的专业集合结构化事实；
4. 相关审批、订单、报价、结算或项目链佐证；
5. 仅有 OCR 文本、文件名、路径、金额相似或旧分类器输出。

Lower evidence can recall a candidate but cannot override contradictory higher evidence.

## 二、匹配硬约束

Reject confirmation when:

- the audited company is not a contract party and no documented agency/payment-on-behalf chain exists;
- cash direction conflicts with company role;
- explicit receipt remarks identify another project/contract;
- counterparty cannot be the other contract party or a proven payor/payee;
- transaction timing is impossible for the contract lifecycle;
- one transaction or deduplicated cumulative pool exceeds the applicable contract amount/node without a documented explanation;
- project/category facts directly conflict.

The six internal companies must be modeled as related but distinct legal entities. Internal transfers do not justify attaching an unrelated external contract.

## 三、合同视觉审核

Inspect at least:

- cover/title and party page;
- amount and bill-of-material pages;
- payment clauses;
- delivery/acceptance/warranty clauses;
- signing/stamp page.

Record page ranges. State `原文未载明`, `页面不可读`, or `待找其它版本` instead of guessing. Confirm double stamps only when both parties’ stamps are visually present on the relevant contract version.

## 四、合同与银行流水匹配

Evaluate the whole payment pool, not just single equal amounts:

- exact legal entities and aliases;
- company account and counterparty account;
- incoming/outgoing direction;
- receipt purpose and bank serial;
- contract effective/performance dates;
- milestones and trigger dates;
- project/category and item models;
- cumulative receipts/payments;
- deposits, progress payments, retention, final payment;
- refunds, reversals, and mirrored transfers.

Use bold inference only after hard constraints pass. Record why the selected relation is stronger than rejected alternatives.

## 五、发票匹配

Confirm buyer/seller roles, tax IDs, invoice type, date, amount/tax, items, and project role. A cost invoice cannot satisfy an output-invoice requirement. Do not reuse a closed invoice across unrelated batches without a valid allocation.

## 六、履约凭证匹配

Confirm actual performance, not topical similarity. Require a credible event conclusion plus suitable parties/date/project/items and, where expected, signature or stamp. Treat technical documents and unsigned templates as support only.

## 七、特殊交易类型

- Bank interest: income; purchase/sale contract, invoice, and fulfillment usually not applicable, but retain bank evidence.
- Bank fee/service fee: expense; purchase/sale three-flow usually not applicable, but retain fee evidence.
- Same-entity transfer: non-operating cash movement; require account/transfer evidence.
- Intra-group transfer: classify as internal transfer candidate unless real purchase/sale evidence exists.
- Financing/loan: exclude from purchase/sale and project profit; require loan agreement, note, repayment plan, and interest evidence.
- Guarantee deposit: distinguish payment/return and require deposit/approval evidence.
- Refund/reversal: pair with original transaction and calculate net project effect.
- Payroll/tax/reimbursement: three-flow not applicable only after nature is established; preserve the appropriate supporting-evidence requirement.

## 八、错误纠正

When a confirmed link is wrong:

1. 在回滚证据中保留原关系。
2. 写明原关系违反了哪一条硬约束。
3. 撤销或降级确认关系，但保留真实候选。
4. 重新计算合同累计结算和项目汇总。
5. 把该错误加入回归样例，并在全表检查同类问题。
