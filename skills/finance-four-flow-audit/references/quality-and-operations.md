# 质量控制与生产操作规范

## 目录

1. 脚本能力边界
2. 安全写入规程
3. 分轮执行与汇报
4. 全局质量审计
5. 阶段停止条件

## 一、脚本能力边界

Scripts may:

- enumerate and download metadata;
- compute hashes and duplicate groups;
- extract OCR/text candidates;
- rank and batch candidate queues;
- calculate totals, dates, and missing fields;
- perform CAS/idempotent writes and fresh-read verification;
- generate rollback manifests.

Scripts may not make the final judgment for contract parties, stamps, contract-to-flow confirmation, invoice role, or actual fulfillment. The Agent must inspect the evidence and record a reasoned decision.

## 二、安全写入规程

Before writing:

1. 重新读取目标记录和表结构。
2. 对受保护字段、人工字段和原关联值生成快照。
3. 建立有界变更清单，包含记录 ID、写前值、拟写值、证据和回滚值。
4. 未经明确授权，拒绝覆盖与人工字段冲突的变更。

After writing:

1. 重新读取全部已变更记录或完整的有界记录集。
2. 做幂等复跑，并要求第二次运行不再产生变更。
3. 重新计算受保护字段哈希。
4. 重新计算受影响的合同和项目汇总。
5. 保存不含凭据和大段业务原文的回滚材料。

## 三、分轮执行与汇报

At each module/50–100 records/30–60 minutes/production write/blocker report:

- `round_name`
- `before → after`
- `evidence_processed`
- `value_created`
- `corrections`
- `verification`
- `remaining_high_value_gaps`
- `next_round`
- `blocked / parent_decision_needed`

Do not stop after reporting when `blocked=false` and useful work remains.

## 四、全局质量审计

Regularly scan for:

- blank or generic pending core states;
- candidate links displayed as confirmed;
- wrong company party or direction;
- single/cumulative amount over contract;
- contract later than payment without explanation;
- project/category conflict;
- duplicate versions inflating totals;
- invoice role mismatch;
- fulfillment support masquerading as direct proof;
- internal/financing/refund transactions entering operating profit;
- duplicate project business keys;
- files or specialist facts not linked back to audit rows.

Prioritize by amount × business risk × tractability × “only one flow missing”.

## 五、阶段停止条件

Stop automatic searching only when:

- the high-progress queue is empty;
- core states contain no unexplained blanks;
- display conflicts are zero;
- every unresolved item is genuine ambiguity, confirmed missing, business not applicable, or exhausted evidence;
- each unresolved item has searched scope and an exact supplement action;
- regression cases pass;
- new files or a changed audit rule are required for further progress.

Resume only for new evidence, human supplements, or a new user-approved audit criterion.
