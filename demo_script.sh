#!/bin/bash
# AgentCraft 演示录制脚本
# 用法: bash demo_script.sh | tee demo_output.txt
echo "=== AgentCraft Demo — ICCSE 2026 ==="
echo "=== 场景1: 股票分析Agent ==="
python agentcraft_skill/scripts/agentcraft.py "我想造一个能分析股票财报的Agent"
echo ""
echo "=== 场景2: 天气机器人 ==="
python agentcraft_skill/scripts/agentcraft.py "帮我做个天气预报机器人"
echo ""
echo "=== 场景3: 作业辅导 ==="
python agentcraft_skill/scripts/agentcraft.py "我要一个数学作业辅导助手"
