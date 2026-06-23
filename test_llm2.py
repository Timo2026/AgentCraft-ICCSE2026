#!/usr/bin/env python3
"""直接测试 LLM 调用"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agentcraft_skill", "scripts"))
from llm_client import _get_client, LLM_MODEL, LLM_BASE_URL

print(f"URL: {LLM_BASE_URL}")
print(f"Model: {LLM_MODEL}")

client = _get_client()
print(f"Client: {client}")

try:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": "Say exactly: companion"}],
        temperature=0,
        max_tokens=10,
    )
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")
