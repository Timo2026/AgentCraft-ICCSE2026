#!/usr/bin/env python3
"""快速启动 AgentCraft Web UI"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web"))
from app import app

if __name__ == "__main__":
    print("🚀 AgentCraft Web UI 启动中...")
    print("📱 请打开浏览器访问: http://localhost:5000")
    app.run(debug=False, port=5000)
