# zhanzhan-finance-agent-kit

让具备飞书工具能力的 Agent 通过一个 GitHub 链接完成财务文件系统入职、环境适配和上线验收。

本项目不要求客户拥有固定数量的群、文件夹或完全相同的多维表格。Agent 先审计客户现状，再选择：

- 复制标准参考实现；
- 将现有 Base 映射到标准语义模型；
- 保留现有结构并补齐缺失能力。

## 给 Agent 的唯一入口

如果你是负责部署本项目的 Agent，请从 [AGENT-ONBOARDING.md](AGENT-ONBOARDING.md) 开始，严格按阶段执行。不得跳过只读审计、人工确认、单文件验收或写后验证。

## 产品闭环

```text
群文件/图片/伴随文字
  -> 原件归档与证据包
  -> 文件索引
  -> 专业文件集合
  -> 唯一业务事实
  -> 合同收付款与四流审核
  -> 群内处理回执、异常通知和飞书 Wiki
```

## 核心原则

1. Agent 掌握语义判断，工具只执行确定性操作。
2. 文件可以重复存在，业务事实不能重复计数。
3. 先读原件，再分类和写表。
4. 文件名和伴随文字中的 `[键=值]` 是强映射信号，但不能推翻原件硬冲突。
5. 所有写入必须经过动作清单、fresh-read、人工字段保护、幂等和回执验证。
6. 客户现场配置与通用规则分离，任何 token、人员和表 ID 都不得硬编码进公共仓库。

## 仓库结构

- `AGENT-ONBOARDING.md`：Agent 自主入职总控。
- `manifest.yaml`：版本、能力和阶段声明。
- `onboarding/`：从权限审计到生产启用的阶段门。
- `schemas/`：租户配置和状态文件的机器契约。
- `skills/`：专业判断手册。
- `protocols/`：映射、证据包、写入和完成标准。
- `reference-implementation/`：现有财务四流一致 Base 的标准参考实现。
- `adapters/`：不同 Agent/Harness 的适配说明。
- `tools/`：随项目交付、由 Agent 调用的确定性工具；当前包含受计划约束的回单切割器。
- `wiki/`：客户飞书 Wiki 模板。

## 当前状态

`0.4.0` 提供自包含的 Aily SkillHub 发布包：完整入职门、18 条规则覆盖矩阵、分类专业手册、脱敏 Base 参考实现、决策校验器和可移植回单切割工具。Agent 必须先视觉确认边界并提交切割计划，工具只执行、校验和生成证据清单；它不会自行认定回单边界，也不会直接写客户 Base。进入生产前仍需客户确认租户配置、字段映射和单文件验收结果。

## 回单切割工具

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/receipt_split.py source.pdf plan.json output-directory
```

计划格式见 `examples/receipt-split-plan.example.json`。坐标采用页面左上角为原点的归一化 `[x0, y0, x1, y1]`；一个页面可切出多张回单，一张回单也可由多个页面区域组成。成功输出包含派生 PDF、逐页 PNG 预览和 `receipt-split-manifest.json`。该清单是后续上传和受控写入的证据，不代表生产写入授权。

## Aily SkillHub 发布包

`skills/finance-four-flow-audit/` 已是自包含 Skill：包括主 `SKILL.md`、18 条规则覆盖矩阵、类型专册、受控写入规程、决策校验器和回单切割器。发布前运行：

```bash
python3 scripts/validate_aily_skill.py
python3 scripts/package_aily_skill.py
```

生成物位于本地 `dist/`，不提交客户配置或运行产物。Aily 安装后仍须按 `references/installation-and-readiness.md` 对真实权限、沙箱依赖、群触发和单文件闭环逐项验收；成功读取 Skill 不等于生产能力已经部署。
