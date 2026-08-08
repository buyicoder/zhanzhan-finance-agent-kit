# 从杂乱文件到四流审核的完整工作流

## 目录

1. 接入与盘点
2. 建立文件索引
3. 逐文件详细分析
4. 处理派生对象
5. 建立专业集合
6. 建立四流一致审核
7. 以合同为中心反向匹配
8. 项目经营价值收敛
9. 交付结构化证据文件夹

## 一、接入与盘点

- Confirm the authorized Drive folders, company list, Base, and whether originals may be moved, copied, renamed, or only referenced.
- Discover existing indexes and automation, but treat their classifications as leads, not truth.
- Snapshot current table schemas, record counts, view definitions, and manual-field hashes.
- Identify source objects, derived objects, archives, image-only scans, duplicate versions, and inaccessible files.

## 二、建立文件索引

Create one row per object with stable source token and lineage. Recommended minimum fields:

- file name, file token, resource type, link, company, source path;
- original/derived role, parent source, content hash, version group;
- initial document type, detailed subtype, analysis state;
- project and counterparty clues;
- evidence notes and error state.

Enumerate with scripts when useful, but have the Agent inspect representative records and all high-value/ambiguous records before trusting routing rules.

## 三、逐文件详细分析

Process documents in value order:

1. 已签署或盖章的合同；
2. 银行流水和回单；
3. 发票；
4. 已签收或盖章的交付、验收凭证；
5. 结算、审批、招投标和项目佐证材料；
6. 技术资料及非财务文件。

For PDFs and images, combine text-layer extraction, OCR, and visual inspection. OCR is candidate evidence; the page is the authority for critical fields.

## 四、处理派生对象

- Split multi-receipt PDFs into one receipt per business transaction.
- Retain the parent file and link every child to it.
- Distinguish PDF/image render pairs and repeated exports from independent receipts.
- For composite contract scans, split by actual sub-contract boundaries while retaining the composite container.
- For archives, validate path traversal, encryption, expansion size, nesting depth, and member count before read-only extraction.

## 五、建立专业集合

Create independent facts rather than merely copying file rows:

- A contract fact groups signed, unsigned, clearer, and duplicate versions.
- A receipt fact represents one bank transaction and may have PDF/image aliases.
- A fulfillment fact represents one actual delivery, installation, signing, or acceptance event and may have many source files.
- An invoice fact represents a real invoice, including red/void state and business role.

Keep the file index as evidence lineage and specialist tables as business facts.

## 六、建立四流一致审核

Create one audit row per bank transaction or defined transaction batch. Link the actual Base records for:

- bank statement transaction;
- individual receipt;
- contract fact(s);
- invoice fact(s);
- fulfillment fact(s);
- standard project.

Evaluate each flow independently. Use “business not applicable” only after classifying the transaction as non-purchase/sale. “Not applicable” never means exempt from evidence: financing still needs loan evidence; payroll needs payroll/approval evidence; internal transfers need account and transfer evidence.

## 七、以合同为中心反向匹配

After contract data quality is high:

1. 把合同副本和不同版本归并为独立合同事实。
2. 判断本公司在合同中的角色和预期资金方向。
3. 提取付款节点及其触发条件。
4. 按主体、账号、方向、日期、项目/品类、摘要和累计金额池召回流水候选。
5. 由 Agent 在确认前打开合同关键页和回单原件。
6. 记录每笔分期款和累计结算金额。
7. 反向检查每条“流水—合同”关系是否存在矛盾。

Do not expect transaction amount to equal contract total. Consider deposits, progress payments, partial delivery, retention, taxes, offsets, refunds, and aggregated batches.

## 八、项目经营价值收敛

Use confirmed contract and transaction facts to calculate:

- signed revenue and cost contracts;
- collected revenue, paid cost, receivables, payables;
- invoiced revenue and received input invoices;
- delivered/accepted amount or stage;
- expected and actual gross margin;
- overdue collection, excess payment, duplicate-payment candidates, and document gaps.

Keep system judgments explicitly separate from human conclusions.

## 九、交付结构化证据文件夹

When organizing Drive:

- preserve source libraries unless the user explicitly authorizes moves;
- prefer shortcuts over copies;
- organize company → project → document category → contract number;
- keep unresolved project/contract files in explicit pending folders;
- preserve derived-object lineage and avoid renaming originals merely to fit a convention;
- maintain a resumable manifest and verify created folders/shortcuts with fresh reads.
