# AgentCraft — Agent开发教学 Copilot
## ICCSE 2026 参赛方案 | Education 赛道

---

## 一、问题定义

**痛点**：CS/AI本科生学完课程后，仍无法将大模型变成可用的Agent应用。
- 理论过剩：机器学习、NLP、深度学习学了一圈
- 实践为零：不会规划→调度→工具调用→验证的完整链路
- 现有工具要么是聊天机器人（ChatGPT），要么是代码编辑器（Cursor），没有"教你造Agent"的工具

**AgentCraft 解决**：不是给你一个Agent，而是教你一步步造出自己的Agent。

---

## 二、目标用户

- 计算机/AI专业本科生（大三以上）
- 有Python基础，学过ML/NLP课程
- 欲将理论知识转化为可运行系统
- 典型场景：课程项目、毕业设计、个人作品集

---

## 三、技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    AgentCraft 教学 Copilot               │
├─────────┬─────────┬─────────┬─────────┬────────────────┤
│ Stage 1 │ Stage 2 │ Stage 3 │ Stage 4 │  Stage 5-6     │
│Understand│  Plan  │Scaffold │  Wire   │ Gate + Test    │
├─────────┼─────────┼─────────┼─────────┼────────────────┤
│意图分类  │骨架规划  │代码生成  │路由连接  │ 门禁+测试      │
│hub_router│agent_  │loop_   │skill_  │ gate.json      │
│classify │templates│runner  │bridge  │ test_verify    │
└─────────┴─────────┴─────────┴─────────┴────────────────┘
          ▲                   ▲                   ▲
          │                   │                   │
    ┌─────┴─────┐      ┌─────┴─────┐      ┌─────┴─────┐
    │ 1048 Skills│      │ libs/     │      │ rewind-   │
    │ 制造/金融/  │      │ agent_base│      │ cache     │
    │ 教育/系统   │      │ intent_   │      │ compact-  │
    │            │      │ router    │      │ micro     │
    └───────────┘      └───────────┘      └───────────┘
```

---

## 四、六步教学法 (Agentic Workflow)

### Stage 1: Understand（理解需求）
- 学生自然语言描述想造的Agent
- hub_router 意图分类 → 匹配Agent模板
- 输出：推荐Agent类型 + 置信度

### Stage 2: Plan（规划骨架）
- 拆解为 skills + tools + workflow
- 检查已有资源（1048 skill中哪些可直接复用）
- 输出：任务编排流程图 + 资源清单

### Stage 3: Scaffold（生成骨架）
- 生成 agent 目录（main.py + SKILL.md + gate.json）
- 基于 AgentBase 共享模块（237行基类）
- 输出：可运行的最小Agent骨架

### Stage 4: Wire（连接路由）
- 注册到 hub_router 意图系统
- 连接 skill_bridge 跨Skill互调
- 输出：可接收外部请求的Agent

### Stage 5: Gate（配置门禁）
- 三层安全：身份识别 → 权限映射 → 熔断保护
- 支持 owner/admin/guest 三级角色
- 输出：安全配置完成

### Stage 6: Test（运行验证）
- 测试用例驱动验证
- 失败的步骤回显诊断信息
- 输出：测试报告 + 部署建议

---

## 五、核心技术优势

| 维度 | AgentCraft | 竞品（ChatGPT教编程） |
|------|-----------|---------------------|
| **真实执行** | 生成可运行的Python Agent | 只给文字建议 |
| **技能复用** | 从1048个Skill中组合 | 从零开始 |
| **安全门禁** | 三层访问控制 | 无安全机制 |
| **成本控制** | 本地Ollama压缩 + rewind-cache | 全云端付费 |
| **循环优化** | OPC Loop自反馈改进 | 一次性输出 |

---

## 六、演示场景（3个预设）

| 场景 | 学生输入 | AgentCraft输出 |
|------|---------|---------------|
| 股票分析Agent | "我想造个能分析财报的助手" | StockAnalyst (pdf+web_search+web_fetch) |
| 天气机器人 | "我要个查天气的bot" | WeatherBot (weather+web_search) |
| 作业辅导Agent | "帮我做个数学题讲解工具" | HomeworkHelper (reasoning+web_search) |

---

## 七、创新点

1. **自指教学**：Agent教人造Agent（元叙事）
2. **零成本本地推理**：Ollama qwen2.5:1.5b 处理教学编排
3. **共享模块层**：AgentBase(237行) + intent_router(288行) + knowledge_query(267行)
4. **压缩缓存双引擎**：compact-micro + rewind-cache 节省80%+ token
5. **全链路可观测**：6步教学每步有状态日志

---

## 八、负责任AI考量

- **安全门禁**：3层访问控制，guest用户受限
- **熔断机制**：3次失败自动锁定，防止滥用
- **透明度**：每步输出置信度+理由
- **隐私**：本地推理，数据不上传云端

---

## 九、效率与成本

| 项目 | 成本 |
|------|------|
| AgentCraft编排 | 本地qwen2.5:1.5b（¥0） |
| 知识检索 | FAISS本地索引（¥0） |
| 上下文压缩 | compact-micro每30min自动（¥0） |
| 输入去重 | rewind-cache命中率~15%节省（¥0） |
| **单次教学总成本** | **¥0** |

---

## 十、未来改进

- Phase 2: 多Agent协作教学（学生Agent × 教师Agent）
- Phase 3: 自适应学习路径（根据学生错误调整教学）
- Phase 4: Agent市场（学生发布/共享自建Agent）
- Phase 5: 开源社区 + 竞赛平台
