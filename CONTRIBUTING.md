# 贡献指南

感谢你对 AgentCraft 的关注！

## 如何贡献

### 提交 Bug

1. 确保 Bug 尚未在 [Issues](https://github.com/your-org/agentcraft/issues) 中报告
2. 使用 Bug 报告模板（如有）
3. 描述复现步骤、预期行为和实际行为
4. 附上 Python 版本和操作系统信息

### 提交功能建议

1. 在 Issues 中描述你的想法
2. 说明为什么它对 AgentCraft 有价值
3. 如果有原型代码更欢迎

### Pull Request 流程

1. Fork 本仓库
2. 创建你的特性分支：`git checkout -b feature/amazing-feature`
3. 提交你的更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 开启 Pull Request

### 开发环境

```bash
git clone https://github.com/your-org/agentcraft.git
cd agentcraft
pip install flask python-pptx
```

### 添加新模板

在 `agentcraft_skill/scripts/agentcraft.py` 的 `TEMPLATES` 字典中添加新条目：

```python
TEMPLATES["your_template"] = {
    "name": "YourAgent",
    "domain": "Education",  # Health / Law / Sustainability / FinTech
    "desc": "你的 Agent 描述",
    "skills": ["web_search", "reasoning"],
    "tools": ["read", "write"],
    "workflow": ["classify", "step1", "step2", "step3"],
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "gate": {"owner": ["*"], "guest": ["chat"]},
    "test": "测试输入"
}
```

然后在 `_generate_step_implementations()` 中添加对应的 step 实现。

## 代码风格

- Python 代码遵循 PEP 8
- 使用 UTF-8 编码
- 添加适当的中文/英文注释
