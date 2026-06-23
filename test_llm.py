#!/usr/bin/env python3
"""测试 LLM 意图分类"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agentcraft_skill", "scripts"))
from llm_client import chat, classify_intent, is_available, LLM_MODEL

print("Available:", is_available())
print("Model:", LLM_MODEL)

templates = json.dumps({
    "stock_analyst": {"domain": "FinTech", "desc": "股票财报分析", "keywords": ["股票", "财报"]},
    "weather_bot": {"domain": "Information", "desc": "天气查询", "keywords": ["天气", "温度"]},
    "homework_helper": {"domain": "Education", "desc": "数学作业辅导", "keywords": ["作业", "数学"]},
    "companion": {"domain": "Education", "desc": "情感陪伴对话", "keywords": ["陪伴", "聊天"]},
}, ensure_ascii=False)

# 直接看 raw 输出
prompt = """你是一个 Agent 教学系统。用户想要构建一个 AI Agent，请根据他的需求分类。

候选模板:
""" + templates + """

用户需求: 做一个陪伴agent

请只返回一个 JSON 对象，格式：
{"best": "模板的key", "confidence": 0.9, "rationale": "理由", "agent_name": "英文名", "domain": "Education"}

只返回 JSON，不要其他内容。"""

raw = chat(prompt, max_tokens=200)
print("\n=== Raw LLM response ===")
print(repr(raw))

# 用 classify_intent
print("\n=== classify_intent ===")
result = classify_intent("做一个陪伴agent", templates)
print("Result:", result)
