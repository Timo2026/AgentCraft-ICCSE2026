# 🎓 AgentCraft — Agent开发教学 Copilot

> **"用 Agent 教人造 Agent"** — 六步教学法，帮助大学生从零搭建可运行的 AI 助手

<p align="center">
  <img src="https://img.shields.io/badge/ICCSE-2026-blue?style=flat-square" alt="ICCSE 2026">
  <img src="https://img.shields.io/badge/Track-Education-8b5cf6?style=flat-square" alt="Education Track">
  <img src="https://img.shields.io/badge/Python-3.8+-3b82f6?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Cost-¥0-success?style=flat-square" alt="Cost">
</p>

---

## 📖 概述

AgentCraft 是 ICCSE 2026 Agentic AI Competition（Education 赛道）的参赛作品，核心命题为 **"教大学生从零搭建自己的 AI Agent"**。

不同于 ChatGPT 式的对话机器人，AgentCraft 是一个 **agentic copilot**：学生用自然语言描述想要构建的 Agent，系统通过六步教学法自动规划、生成、连接并测试完整的 Agent 代码。

### 它解决了什么问题？

CS 本科生学完 ML/NLP 课程后，**仍然不会把大模型变成可运行的应用**。AgentCraft 填补了"理论→实践"的鸿沟。

---

## ✨ 特性

- 🔍 **六步教学法**：Understand → Plan → Scaffold → Wire → Gate → Test
- 🧩 **5+1 个预设模板**：股票分析、天气查询、作业辅导、情感陪伴、通用定制
- 🌐 **真实工具调用**：wttr.in 天气 API、DuckDuckGo Web 搜索、数学推理引擎
- 🛡️ **三层安全门禁**：身份识别 → 权限映射 → 熔断保护
- 💰 **零成本本地运行**：无需 GPU，无需付费 API，单次教学 ¥0
- 🖥️ **双形态界面**：Web UI (Flask) + 桌面 GUI (Tkinter)

---

## 🚀 快速开始

### 前提条件

- Python 3.8+
- 无需任何 API Key 或 GPU

### 安装

```bash
git clone https://github.com/your-org/agentcraft.git
cd agentcraft
pip install flask python-pptx  # Web UI 和 PPT 生成依赖
```

### 命令行运行

```bash
# 单个场景
python agentcraft_skill/scripts/agentcraft.py "帮我做天气预报机器人"

# 演示三个预设场景
python agentcraft_skill/scripts/agentcraft.py --demo-all
```

### Web UI 运行

```bash
python run_web.py
# 浏览器打开 http://localhost:5000
```

### 桌面 GUI 运行

```bash
python web_gui.py
```

---

## 🏗️ 架构

```
                      ┌─────────────────────────────┐
                      │   学生输入自然语言需求         │
                      └─────────────┬───────────────┘
                                    │
            ┌───────────────────────┼───────────────────────────┐
            ▼                       ▼                           ▼
    ┌──────────────┐      ┌──────────────┐          ┌──────────────┐
    │  Stage 1     │      │  Stage 2     │          │  Stage 3     │
    │  Understand  │ ───► │  Plan        │ ──────► │  Scaffold    │
    │  意图分类     │      │  骨架规划     │          │  代码生成     │
    └──────────────┘      └──────────────┘          └──────────────┘
                                                            │
                                    ┌───────────────────────┤
                                    ▼                       ▼
                            ┌──────────────┐      ┌──────────────┐
                            │  Stage 4     │      │  Stage 5     │
                            │  Wire        │ ───► │  Gate        │
                            │  路由连接     │      │  安全门禁     │
                            └──────────────┘      └──────────────┘
                                                            │
                                                            ▼
                                                    ┌──────────────┐
                                                    │  Stage 6     │
                                                    │  Test        │
                                                    │  运行验证     │
                                                    └──────────────┘
```

### Agent 模板

| 模板 | 领域 | 真实工具 |
|------|------|---------|
| `StockAnalyst` | FinTech | DuckDuckGo 搜索 + 财务指标提取 |
| `WeatherBot` | Information | wttr.in 实时天气 API |
| `HomeworkHelper` | Education | 数学推理引擎（分部积分等） |
| `CompanionBot` | Education | 情感关键词检测 + 心情日志 |
| `CustomAgent` | General | Web 搜索 + 自动方案规划 |

---

## 📊 演示场景实测

```
$ python agentcraft_skill/scripts/agentcraft.py "帮我做天气预报机器人"

🚀 WeatherBot 启动
📝 输入: 北京明天天气怎么样
⚙️  工作流: classify → fetch_weather → format_response

  ▶ classify       → 置信度 0.99
  ▶ fetch_weather  → 城市: 北京 | 温度: 21°C | 天气: Patchy rain | 湿度: 78%
  ▶ format_response → 格式化中文天气报告

✅ 通过 | 耗时 1.7s | 成本 ¥0
```

```
$ python agentcraft_skill/scripts/agentcraft.py "我要数学作业辅导"

📝 输入: 解∫x²sin(x)dx
  ▶ classify     → 识别为微积分类型
  ▶ decompose    → 拆分为4个子问题
  ▶ step_by_step → 7步分部积分完整推导
                   = -x²cosx + 2x·sinx + 2cosx + C

✅ 通过 | 耗时 0.1s | 成本 ¥0
```

---

## 📁 项目结构

```
agentcraft/
├── README.md                           # 项目说明
├── .gitignore
├── LICENSE
├── run_web.py                          # Web UI 一键启动
├── web_gui.py                          # 桌面 GUI 启动
├── generate_ppt.py                     # PPT 生成脚本
├── demo_script.sh                      # Linux 演示脚本
│
├── agentcraft_skill/                   # 核心引擎
│   ├── skill.json                      # Skill 元信息
│   ├── SKILL.md                        # Skill 说明文档
│   └── scripts/
│       └── agentcraft.py               # 主程序 (~620 行)
│
├── web/                                # Web UI
│   ├── app.py                          # Flask 后端
│   └── templates/
│       └── index.html                  # 前端页面
│
└── scheme/                             # 参赛文档
    └── AgentCraft_参赛方案.md           # 比赛方案书
```

---

## 🔒 负责任 AI

AgentCraft 内置三层安全防线：

| 层级 | 机制 | 说明 |
|------|------|------|
| L1 | 身份识别 | SHA256 user_id → owner/admin/guest 角色 |
| L2 | 权限映射 | 按角色限制可访问的意图范围 |
| L3 | 熔断保护 | 3 次连续失败 → 自动锁定 300s |

此外：**全本地推理，数据不上传云端**。

---

## 🛣️ 路线图

- [x] 六步教学管线
- [x] 5 个预设模板 + 通用模板
- [x] 真实 API 调用（天气、搜索）
- [x] Web UI + 桌面 GUI
- [x] 三层安全门禁
- [ ] 接入真实 LLM（Qwen/Llama）做意图理解
- [ ] 多 Agent 协作：Student Agent × Teacher Agent
- [ ] Agent 能力市场（学生发布/共享自建 Agent）

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 许可

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [wttr.in](https://wttr.in) - 免费天气 API
- [DuckDuckGo](https://duckduckgo.com) - 隐私搜索引擎
- ICCSE 2026 组织方 - 新加坡南洋理工大学、清华大学、山东大学、新疆大学、UBC、阿里巴巴

---

<p align="center">
  <sub>Built with ❤️ for ICCSE 2026 | "用 Agent 教人造 Agent"</sub>
</p>
