import sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agentcraft_skill", "scripts"))
from llm_client import classify_intent, chat, LLM_MODEL

templates = json.dumps({
    "stock_analyst": {"domain": "FinTech", "desc": "股票财报分析", "keywords": ["股票", "财报"]},
    "weather_bot": {"domain": "Information", "desc": "天气查询", "keywords": ["天气", "温度"]},
    "homework_helper": {"domain": "Education", "desc": "数学作业辅导", "keywords": ["作业", "数学"]},
    "companion": {"domain": "Education", "desc": "情感陪伴对话", "keywords": ["陪伴", "聊天"]},
}, ensure_ascii=False)

prompt = "你是一个Agent教学系统。用户需求: 做一个陪伴agent\n候选模板: " + templates + "\n请返回JSON格式: {best,confidence,rationale,agent_name,domain}\n只返回JSON。"
raw = chat(prompt, max_tokens=500)
print("Raw:", repr(raw[:300] if raw else None))

result = classify_intent("做一个陪伴agent", templates)
print("Result:", result)
