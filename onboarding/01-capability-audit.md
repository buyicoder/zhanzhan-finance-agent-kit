# 能力审计

逐项以 `PASS / PARTIAL / MISSING / UNKNOWN` 评级。只有真实样本端到端执行并保存证据才可标记 PASS。

## 飞书能力

- 读取客户指定群及真实 chat_id；
- 读取文件、图片、伴随文字、多附件和回复引用；
- 下载消息资源；
- 列出、递归读取和写入授权对象库；
- 读取 Base 表、字段、选项、关联、公式和视图；
- 创建和更新 Wiki；
- 配置事件监听、通知和历史补扫。

## 文件能力

- SHA-256；
- PDF 全页/指定页渲染、文本辅助提取、切割、裁剪和验证；
- Excel 全部非空 sheet；
- Word/PPT 全部非空页；
- 压缩包安全解包；
- 图片视觉阅读、二维码解码和 OCR 辅助。

## 随项目交付的工具验收

回单切割不是外部能力假设。部署 Agent 必须安装项目依赖并执行：

```bash
python3 scripts/receipt_split.py --help
python3 -m pytest -q tests/test_receipt_splitter.py
```

只有命令可调用且测试通过，才可将 `receipt_split` 标为 AVAILABLE。真实租户验收还必须选择一份经视觉确认边界的回单集合 PDF，执行切割并逐页查看工具生成的 PNG 预览。未完成真实原件验收时只能标记 PARTIAL，不能宣称生产可用。

## 写入闭环

- 动作清单校验；
- 写前 fresh-read 和快照；
- 人工字段保护；
- 稳定业务键和幂等键；
- 限定表/记录/字段的写入；
- 写后 fresh-read；
- 远程结果不明时停止盲目重试；
- 补偿、回滚、checkpoint 和回执。

存在任意写入保护缺口时，最终结论必须为 NOT READY。
