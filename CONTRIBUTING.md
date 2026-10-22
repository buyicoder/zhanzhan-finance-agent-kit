# Contributing

规则、Schema 和工具变更必须保持租户无关。禁止提交真实 chat_id、folder token、Base token、人员 open_id、客户文件、原始表记录或访问凭证。

提交前运行：

```bash
python3 scripts/validate_project.py
python3 skills/finance-four-flow-audit/scripts/validate_decision.py \
  skills/finance-four-flow-audit/references/decision-manifest.example.json
```

对标准参考实现的修改必须注明语义变化、迁移建议和向后兼容影响。

