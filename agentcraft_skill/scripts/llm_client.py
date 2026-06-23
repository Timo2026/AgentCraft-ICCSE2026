#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentCraft LLM 客户端
支持 OpenAI 兼容 API（含 ollama/LM Studio），不可用时自动降级为规则引擎。

配置方式（环境变量或 .env 文件）:
  AGENTCRAFT_LLM_BASE_URL  — API 地址
  AGENTCRAFT_LLM_API_KEY   — API Key
  AGENTCRAFT_LLM_MODEL     — 模型名

本地模型示例（LM Studio / vLLM / text-generation-webui）:
  AGENTCRAFT_LLM_BASE_URL=http://127.0.0.1:1234/v1
  AGENTCRAFT_LLM_API_KEY=not-needed
  AGENTCRAFT_LLM_MODEL=google/gemma-4-26b-a4b-qat

Ollama 示例:
  AGENTCRAFT_LLM_BASE_URL=http://localhost:11434/v1
  AGENTCRAFT_LLM_API_KEY=ollama
  AGENTCRAFT_LLM_MODEL=qwen2.5:1.5b
"""

import os, json, sys, time

# ── 环境变量 ──
LLM_BASE_URL = os.environ.get("AGENTCRAFT_LLM_BASE_URL", "")
LLM_API_KEY  = os.environ.get("AGENTCRAFT_LLM_API_KEY", "")
LLM_MODEL    = os.environ.get("AGENTCRAFT_LLM_MODEL", "")

# ── 如果设置了本地地址但没有 API Key，自动补一个占位值 ──
if LLM_BASE_URL and not LLM_API_KEY:
    LLM_API_KEY = "not-needed"

_llm_available = None    # None=未检测, True/False
_openai_client = None
_tested_base_url = None  # 记录上次检测的 URL，URL 变化时重新检测

def _load_env_file():
    """从项目根目录 .env 加载配置（可选）"""
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        ".env",
    ]
    for p in env_paths:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip(); v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v
    # 重新读取（可能被 .env 覆盖）
    global LLM_BASE_URL, LLM_API_KEY, LLM_MODEL
    LLM_BASE_URL = os.environ.get("AGENTCRAFT_LLM_BASE_URL", LLM_BASE_URL)
    LLM_API_KEY  = os.environ.get("AGENTCRAFT_LLM_API_KEY", LLM_API_KEY)
    LLM_MODEL    = os.environ.get("AGENTCRAFT_LLM_MODEL", LLM_MODEL)
    if LLM_BASE_URL and not LLM_API_KEY:
        LLM_API_KEY = "not-needed"

_load_env_file()

def _get_client():
    """懒加载 OpenAI 客户端"""
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    if not LLM_BASE_URL or not LLM_API_KEY:
        return None
    try:
        import openai
        _openai_client = openai.OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=15)
        return _openai_client
    except Exception as e:
        print(f"    ⚠️ OpenAI 客户端初始化失败: {e}", file=sys.stderr)
        return None

def is_available() -> bool:
    """检测 LLM 是否可用（有配置且能连通）"""
    global _llm_available, _tested_base_url
    if not LLM_BASE_URL or not LLM_MODEL:
        return False
    # URL 变了就重新检测
    if _llm_available is not None and _tested_base_url == LLM_BASE_URL:
        return _llm_available
    client = _get_client()
    if client is None:
        _llm_available = False
        _tested_base_url = LLM_BASE_URL
        return False
    try:
        # 发一个真实请求验证连通性（大模型首次推理可能慢，给足超时）
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "Say: ok"}],
            max_tokens=20, temperature=0,
        )
        # 只要请求不报错就算可用，空响应也可能是模型还在加载
        _llm_available = True
        _tested_base_url = LLM_BASE_URL
    except Exception as e:
        _llm_available = False
        _tested_base_url = LLM_BASE_URL
        print(f"    ⚠️ LLM ({LLM_BASE_URL}) 不可达: {e}", file=sys.stderr)
    return _llm_available

def chat(prompt: str, max_tokens: int = 1000) -> str:
    """调用 LLM 并返回文本。失败返回空字符串。"""
    if not is_available():
        return ""
    client = _get_client()
    if client is None:
        return ""
    try:
        # Gemma 等模型有 reasoning tokens 开销，max_tokens 不能太小
        effective_max = max(max_tokens, 500)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=effective_max,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"    ⚠️ LLM 调用失败: {e}", file=sys.stderr)
        return ""


# ── AgentCraft 专用 Prompt ──

def classify_intent(user_request: str, templates_info: str) -> dict:
    """LLM 意图分类 → 返回 {"best": "template_key", "confidence": 0.9, "rationale": "..."}
    失败返回 None，触发规则引擎降级
    """
    prompt = f"""你是一个 Agent 教学系统。用户想要构建一个 AI Agent，请根据他的需求分类。

候选模板:
{templates_info}

用户需求: {user_request}

请只返回一个 JSON 对象，格式：
{{"best": "模板的key", "confidence": 0.0~1.0, "rationale": "一句话理由", "agent_name": "给Agent起个英文名", "domain": "FinTech/Education/Information/General"}}

如果需求不匹配任何现有模板，best 设为 "generic"。
只返回 JSON，不要其他内容。"""

    text = chat(prompt, max_tokens=800)
    if not text:
        return None
    try:
        # 提取 JSON（可能包裹在 ```json``` 中）
        if "```" in text:
            text = text.split("```json")[-1].split("```")[0] if "```json" in text else text.split("```")[1].split("```")[0]
        elif "{" in text:
            text = text[text.index("{"):text.rindex("}")+1]
        result = json.loads(text.strip())
        if "best" in result:
            return result
    except Exception:
        pass
    return None


def generate_step_code(template_info: str, step_name: str, step_index: int, max_tokens: int = 800) -> str:
    """LLM 动态生成一个 step 的 Python 代码。失败返回空字符串。"""
    prompt = f"""你是一个 Agent 教学系统的代码生成器。根据以下模板信息，为 Agent 生成一个步骤的 Python 方法。

模板信息:
{template_info}

需要生成的方法: step_{step_name}（第{step_index}步）

要求:
1. 方法签名: def step_{step_name}(self, state: dict) -> dict:
2. 方法体内要有真实的 Python 逻辑（调用 self._web_search、self._log 等）
3. 返回一个字典，包含有用的结果数据
4. 只返回 Python 代码（def 开头），不要 import，不要 class
5. 代码要简洁，10-30 行即可
6. 必须用 self._log() 输出关键信息

Agent 已有的工具: self._web_search(query) 返回搜索结果列表, self._log(msg) 打印日志

只返回代码块："""

    text = chat(prompt, max_tokens=max_tokens)
    if not text:
        return ""
    code = text.strip()
    if "```" in code:
        code = code.split("```python")[-1].split("```")[0] if "```python" in code else code.split("```")[1].split("```")[0]
    code = code.strip()
    if not code.startswith("def "):
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                code = "\n".join(lines[i:])
                break
    return code if code.startswith("def step_") else ""
