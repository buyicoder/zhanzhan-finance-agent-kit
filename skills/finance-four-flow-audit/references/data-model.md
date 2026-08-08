# 数据模型与状态口径

## 目录

1. 文件索引
2. 合同集合
3. 发票集合
4. 银行流水与回单集合
5. 履约凭证集合
6. 四流一致审核
7. 项目与合同结算输出
8. 审核视图

## 一、文件索引

Core fields: source token, file name, type, URL, company, source path, original/derived role, parent token, content hash, version group, initial type, detailed subtype, analysis state, project clue, counterparty clue, evidence note, specialist-record links.

## 二、合同集合

Core fields:

- independent contract fact ID and version group;
- contract number/name;
- party A, party B, company role, counterparty;
- project and category;
- total amount, tax treatment, currency;
- signing date, performance period, validity;
- payment milestones and trigger conditions;
- delivery, acceptance, warranty, and retention clauses;
- party-A stamp, party-B stamp, double-stamp conclusion;
- source files and verified page ranges;
- structure state and missing-field reason.

Do not use source library company as a contracting party. Do not treat list subtotal, tax, fee, sales target, return value, or project number as contract total/number.

## 三、发票集合

Core fields: invoice number/code, type, issue date, seller, buyer, tax IDs, amount excluding tax, tax, total, line items/category, output/input role for the company, red/void state, project, contract links, source files.

## 四、银行流水与回单集合

Core fields: company, account, bank, transaction time, direction, amount, balance, counterparty, counterparty account, bank serial/reference, remarks/purpose, source statement, receipt sources, duplicate/alias group, business type, project, contract candidates/confirmed links.

Split bank interest as income and bank fees as expense. Treat same-entity cross-bank transfers and intra-group transfers as non-operating unless purchase/sale evidence proves otherwise.

## 五、履约凭证集合

Core fields: stable fulfillment fact ID, stage, business date, sender/service party, receiver/acceptance party, project, signer/acceptor, stamp strength, item/service details, quantity/amount, conclusion, contract links, evidence-source collection, duplicate group.

Stages: shipment, arrival, receipt, installation, commissioning, trial run, training, acceptance, warranty/service.

Templates, catalogues, construction plans, applications, test certificates, and ordinary project documents may be useful support but are not direct fulfillment proof.

## 六、四流一致审核

Core relations: statement transaction, receipt, contract(s), invoice(s), fulfillment fact(s), project.

Core states for receipt/contract/invoice/fulfillment:

- `已关联` — confirmed by direct evidence;
- `已关联候选` / `多候选待确认` — real candidates remain;
- `业务不适用` — transaction nature makes purchase/sale evidence inapplicable;
- `确认缺失` — evidence should exist but is absent after defined search;
- `证据不足` — existing evidence cannot support a conclusion.

Never leave a core state blank. Add candidate explanation, searched scope, missing reason, and supplement action.

## 七、项目与合同结算输出

Prefer one project master plus related contract/transaction facts. Calculate:

- revenue contract value, cost contract value;
- received, paid, receivable, payable;
- output invoices, input invoices, invoice gaps;
- fulfillment stage, acceptance date, warranty end;
- next due date, overdue days, collection/payment action;
- confirmed and expected gross margin;
- risks and evidence gaps.

For contract installments, retain a normalized payment-detail relation even if user-facing views also expose `第1笔…第N笔` columns.

## 八、审核视图

Provide views for:

- each company;
- confirmed links;
- candidate/ambiguous links;
- only one flow missing;
- confirmed missing and required supplement;
- non-purchase/sale evidence requirements;
- signed contracts with unpaid balance;
- overdue receivables and upcoming due dates;
- project income/cost/margin;
- high-risk contradictions and duplicate-payment candidates.

Put decision, amount, parties, project, due date, status, and clickable evidence first. Hide irrelevant receipt columns on payment-contract views and vice versa.
