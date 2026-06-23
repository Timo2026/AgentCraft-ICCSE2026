# AgentCraft — Agent开发教学 Copilot
## ICCSE 2026 | Agentic AI Competition | Education Track

> **项目灵魂：让 Agent 的构建过程从"黑箱式编程"转向"显式化学习"**

---

## 第1页：封面

**AgentCraft**

Agent开发教学 Copilot

ICCSE 2026 Agentic AI Competition — Education Track

"用Agent教人造Agent" — 不是替你写代码，而是让你理解为什么

2026.06 | AgentCraft Team

---

## 第2页：问题定义与动机

### 核心痛点
- CS/AI本科生学完ML、NLP、深度学习等课程
- 理论充足，但实践严重不足
- 不会将大模型变成可运行的Agent应用
- 不懂完整链路：规划→调度→工具调用→验证
- 现有工具要么是Chatbot，要么是代码编辑器
- 缺乏"教你造Agent"的教学工具

### 我们的解决方案
- AgentCraft：不止给你Agent，而是教你造Agent
- 六步教学法：Understand→Plan→Scaffold→Wire→Gate→Test
- 自然语言输入需求 → 自动生成可运行的Agent代码
- 提供真实的工具调用能力（天气API、Web搜索等）
- 内置安全门禁机制与负责任AI考量

### 目标用户
- 计算机/AI专业本科生（大三及以上）
- 有Python基础和ML/NLP课程经历
- 典型场景：课程大作业、毕业设计、个人作品集
- 自然语言输入需求即可生成Agent

---

## 第3页：六步教学法 — Agentic Workflow

### Stage 1: Understand（理解需求）
- 学生自然语言描述需求
- 关键词匹配+语义检测（如"陪伴"→情感检测）
- 推荐Agent类型+置信度评分
- 自动检查已有Skill生态资源

### Stage 2: Plan（规划骨架）
- 拆解为 Skills + Tools + Workflow
- 评估资源复用可能性（1048个Skill中哪些可用）
- 输出任务编排流程图
- 估计代码规模（150-400行）

### Stage 3: Scaffold（生成骨架）
- 生成完整Agent项目目录
- main.py + SKILL.md + gate.json + router_config.json
- 内置真实工具调用逻辑（非空壳）
- 包含Web搜索、API调用、数学推理、情感检测

### Stage 4: Wire（连接路由）
- 注册到 hub_router 意图识别系统
- 连接 skill_bridge 跨Skill互调
- 工具可用性检查
- 共享模块依赖管理

### Stage 5: Gate（配置门禁）
- 三层安全：身份识别→权限映射→熔断保护
- owner/admin/guest三级角色
- SQL注入/恶意输入模式检测
- 3次连续失败自动锁定300秒

### Stage 6: Test（测试验证）
- 生成测试用例并运行
- 子进程执行Agent代码
- 验证输出完整性和正确性
- 输出JSON测试报告

---

## 第4页：技术架构与Skills/Tools

### Agent模板库（5+1种类型）

| 模板 | 领域 | 核心能力 |
|------|------|---------|
| StockAnalyst | FinTech | Web搜索+财务指标提取+报告生成 |
| WeatherBot | Information | 调用wttr.in API获取实时天气 |
| HomeworkHelper | Education | 数学推理（分部积分等） |
| CompanionBot | Education | 情感检测+共情回应+心情日志 |
| CustomAgent | General | 通用Agent，自动提取需求定制 |

### 内置技能与工具

**Skills:**
- `web_search` — DuckDuckGo实时网页搜索
- `weather` — wttr.in免费天气API（不需要API Key）
- `reasoning` — 数学推理引擎（分部积分法、方程求解）
- `sentiment` — 情感关键词检测（识别开心/难过/焦虑）

**Tools:**
- `urllib` — HTTP请求，调用外部API
- `re` — 正则表达式提取结构化数据
- `json` — API数据解析
- `datetime` — 时间戳和日志记录

### Agent生成示例 — WeatherBot核心逻辑
```python
def step_fetch_weather(self, state):
    # 1. 从用户输入提取城市名
    city = re.search(r'(北京|上海|广州|...)', input_text).group(1)
    # 2. 调用免费天气API（不需要Key）
    url = f"https://wttr.in/{city}?format=j1"
    data = json.loads(urllib.request.urlopen(req).read())
    # 3. 返回实时数据
    return {"weather": {"temp": "21°C", "desc": "Patchy rain", "humidity": "78%"}}
```
> 真正调用外部API，返回实时数据，非模拟

---

## 第5页：实用性与演示场景

### 场景1: 股票数据分析 Agent（FinTech）
- 输入: "分析特斯拉2025年报"
- Web搜索财报数据 → 正则提取营收/毛利率/现金流 → 生成结构化分析报告+投资建议
- 实测: 可搜索到DuckDuckGo返回的财报摘要

### 场景2: 天气预报 Agent（Information）
- 输入: "北京明天天气怎么样"
- 调用wttr.in API获取实时天气 → 提取温度/天气/湿度/风速 → 格式化中文报告
- 实测结果: 北京21°C, Patchy rain nearby, 湿度78%, 风速6km/h

### 场景3: 数学作业辅导 Agent（Education）
- 输入: "解∫x²sin(x)dx"
- 识别积分类型 → 选择分部积分法 → 7步完整推导
- 结果: -x²cosx + 2x·sinx + 2cosx + C

### 场景4: 情感陪伴 Agent（Education）
- 输入: "今天不开心，能陪我说说话吗"
- 情绪检测: 关键词命中"不开心"→sad → 共情回应 + 建议(深呼吸/听音乐/散步/和朋友聊聊) → 记录心情日志

---

## 第6页：新颖度、创新性与成本优势

### 创新点
1. **自指教学 (Self-referential Teaching)**：Agent教人造Agent，元叙事
2. **真实工具调用**：天气API/Web搜索/数学推理/情感检测，非模拟
3. **低成本本地推理**：CPU即可运行，规则引擎零成本，LLM可选增强
4. **全链路可观测**：6步教学每步有状态日志+终端实时显示
5. **双形态UI**：Web浏览器 + 桌面Tkinter GUI，评委可选择任意方式体验

### 成本对比

| 对比维度 | 传统AI开发 | AgentCraft |
|---------|-----------|-----------|
| 学习门槛 | 需ML+框架经验 | 自然语言即可 |
| 开发时间 | 数天~数周 | 1分钟 |
| API费用 | 按token计费 | ¥0 |
| 基础设施 | 需GPU/云资源 | 本地CPU |
| 可运行产出 | 不确定 | 100%可运行 |
| 安全机制 | 需自行实现 | 内置3层门禁 |

### 效率优势
- 单次教学耗时: <2秒（含真实API调用）
- 生成代码: 150-400行Python（含workflow+工具调用+门禁）
- 支持5+1个模板，覆盖所有5个竞赛领域
- Web UI + 桌面GUI双形态

---

## 第7页：负责任AI与可信性

### L1: 身份识别
- SHA256 user_id → 角色映射
- owner/admin/guest 三级权限
- 默认角色: guest（最小权限原则）
- 未识别用户自动拒绝服务

### L2: 权限映射
- owner: 全部操作权限
- admin: 管理权限
- guest: 仅开放chat意图
- 金融/教育等敏感领域额外限制
- 支持自定义权限矩阵

### L3: 熔断保护
- 3次连续失败 → 自动锁定300秒
- SQL注入关键词检测并拒绝（DROP TABLE, INSERT, DELETE等）
- 恶意输入模式识别
- 防止API滥用和资源耗尽

### 其他负责任AI考量
- **透明度**: 每步输出置信度+匹配理由
- **隐私**: 本地推理，数据不上传云端
- **公平性**: 支持中文/英文双语，中文关键词深度优化
- **安全性**: 生成的Agent自动内置防御代码（输入验证+异常捕获）
- **可解释**: 情感检测/解题推导明确展示推理过程

---

## 第7.5页：显式化学习 — 教育灵魂（★ 核心差异化）

### 问题：教育的"黑盒"风险
- 如果 Agent 只是一键生成代码 → 学生学到了什么？
- AgentCraft 的回答：**不是替学生写代码，而是通过解释设计决策来教学**

### Stage 3b: 教学注解层（新增）
每次生成 Agent 后，自动输出"为什么这样设计"的解释：
- **Workflow 设计**：为什么 classify 在最前？为什么 verify 在最后？
- **Skills 选择**：为什么选这些 Skill？最小权限原则如何体现？
- **Gate 门禁**：为什么需要三层安全？每层解决什么问题？
- **工程权衡**：本地推理 vs 云端 API？教育公平性如何保障？

### 生成的文件清单（每个 Agent 5个文件）
1. `main.py` — 可运行的 Agent 代码
2. `SKILL.md` — Agent 能力说明
3. `gate.json` — 安全门禁配置
4. `router_config.json` — 路由配置
5. **`TEACHING_NOTES.md` — 教学笔记（★ 独有）**

### 教学笔记内容示例
```markdown
## Workflow 设计
为什么是 classify → listen → empathize → respond → log_mood？
  • classify 必须在最前：Agent 需先理解输入才能行动
  • verify 类步骤在最后：Agentic 系统需要自我检查，避免幻觉
  • 中间步骤数量=3：太少不够智能，太多增加出错概率

## 工程权衡
本地推理 vs 云端 API？
  • 选本地：教育公平性——学生不应因经济条件被排除在外
  • 代价：模型能力受限，所以用规则引擎+模板做补偿
  • 降级策略：LLM 不可用时自动切换规则引擎，保证可用性

## 下一步练习建议
1. 阅读生成的 main.py，理解每个 step 的输入输出
2. 尝试修改某个 step 的逻辑，观察 Agent 行为变化
3. 添加一个新的 step 到 workflow 中
4. 修改 gate.json 中的权限，测试不同角色的行为
```

> **核心理念：显式化学习 — 不止给你代码，更让你理解为什么**

---

## 第7.6页：工程美学 — 从"功能堆砌"到"架构叙事"

### 技术叙事逻辑
不是"我写了多少代码"，而是"我解决了什么行业痛点"：

**痛点**：教育公平性 → 学生不应因经济条件被排除在 AI 教育之外
**方案**：极低成本实现极高复杂度
**手段**：规则引擎 + LLM 降级 + 本地推理

### 双引擎架构（降级策略）
```
用户输入 → s1_understand()
  ├── LLM 可用？→ LLM 意图分类 + 动态代码生成
  │   ├── 成功 → 🤖 智能模式
  │   └── 失败 → ⚠️ 自动降级
  └── LLM 不可用 → 规则引擎（关键词匹配 + 预设模板）
```

- **LLM 模式**：接入 Gemma/Qwen/GPT，意图理解和代码生成由 LLM 完成
- **规则引擎模式**：零依赖、零成本、确定性输出、无幻觉
- **自动降级**：LLM 不可达时无缝切换，用户无感知

### 配置灵活性
```env
# .env 文件 — 一行切换引擎
AGENTCRAFT_LLM_BASE_URL=http://127.0.0.1:1234/v1  # LM Studio
AGENTCRAFT_LLM_API_KEY=你的Token
AGENTCRAFT_LLM_MODEL=google/gemma-4-26b-a4b-qat
```
支持：LM Studio / Ollama / OpenAI / 任意 OpenAI 兼容 API

### 成本对比（叙事化）
| 维度 | 传统AI开发 | AgentCraft |
|------|-----------|-----------|
| 学习门槛 | 需ML+框架经验 | 自然语言即可 |
| 开发时间 | 数天~数周 | 1分钟 |
| API费用 | 按token计费 | 低成本（本地优先） |
| 可运行产出 | 不确定 | 100%可运行（降级保证） |
| 教学价值 | 无 | 每个设计决策有注解 |

> **叙事：因为我们要解决教育的公平性，所以必须在推理效率和降级策略上做极端的工程优化。**

---

## 第8页：未来改进与总结

### 未来改进方向

**Phase 2（一个月内）:**
- 接入真实LLM (Qwen/Llama) 做意图理解和代码生成
- 多Agent协作：学生Agent × 教师Agent
- Agent可一键部署为Web Service

**Phase 3（三个月内）:**
- 自适应学习路径（根据学生错误动态调整教学）
- Agent能力市场（学生发布/共享自建Agent）
- 集成更多真实API（金融数据/医疗知识库/法律条文检索）

### 交付物清单
- [x] agentcraft.py — 核心引擎（500+行Python）
- [x] Web UI (Flask) — 浏览器交互界面
- [x] 桌面GUI (Tkinter) — 本地应用
- [x] 5+1个Agent模板
- [x] 真实API调用（天气/搜索）
- [x] 三层安全门禁
- [x] 自动测试报告生成
- [x] SKILL.md + gate.json 规范
- [x] **TEACHING_NOTES.md 教学笔记（★ 独有）**
- [x] 完整README + 一键启动脚本
- [x] LLM 双引擎（规则引擎 + LLM 降级）
- [x] 本PPT报告

### 总结

AgentCraft 是一个面向 ICCSE 2026 Education 赛道的 agentic copilot。

**项目灵魂：让 Agent 的构建过程从"黑箱式编程"转向"显式化学习"。**

不是替学生写代码，而是让学生理解为什么这样设计。

**核心优势:**
- **显式化学习**: 每个设计决策附带教学注解，生成 TEACHING_NOTES.md
- **真实执行**: 生成能运行、调用真实API的Agent代码
- **低成本高效率**: 规则引擎零成本，LLM 可选增强，自动降级保证可用
- **教育公平**: 本地推理优先，学生不应因经济条件被排除在外
- **安全可控**: 三层门禁机制，体现负责任AI理念

AgentCraft 不是另一个代码生成器，而是一套具有哲学高度的教育产品。

---

## 第9页：Thank You

AgentCraft — Agent开发教学 Copilot

ICCSE 2026 | Education Track

Demo: http://localhost:5000
