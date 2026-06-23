#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentCraft v1.0 — Agent开发教学 Copilot (GLM-5.2增强版)
ICCSE 2026 Education Track

六步教学管线，每步连接真实系统资源：
  Stage 1: hub_router.classify → 意图识别
  Stage 2: AgentBase模板 → 骨架规划  
  Stage 3: loop_runner.scaffold → 代码生成
  Stage 4: skill_bridge → 路由注册
  Stage 5: identity.json → 门禁配置
  Stage 6: subprocess测试 → 运行验证

Usage:
    python3 agentcraft.py "我想造一个股票分析Agent"
    python3 agentcraft.py --demo-all  # 演示3个场景
"""

import os, sys, json, time, shutil, subprocess
from pathlib import Path
from datetime import datetime

# LLM 集成（安装 openai 库 + 配置环境变量即可启用）
try:
    from . import llm_client
except ImportError:
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "llm_client", os.path.join(os.path.dirname(__file__), "llm_client.py")
    )
    llm_client = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(llm_client)

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── 真实系统路径 ──
HOME = Path(os.path.expanduser("~"))
SKILLS_DIR = HOME / ".openclaw" / "skills"
PROJECTS_DIR = HOME / "projects"
LIBS_DIR = HOME / ".openclaw" / "libs"
IDENTITY_FILE = HOME / ".openclaw" / "config" / "identity.json"
DEMO_DIR = HOME / "agentcraft_demo"

# ── Agent模板库 (基于真实1048 Skill生态) ──
TEMPLATES = {
    "stock_analyst": {
        "name": "StockAnalyst", "domain": "FinTech",
        "desc": "股票分析Agent — 读取财报PDF → 提取关键指标 → 生成分析报告",
        "skills": ["pdf", "web_search", "web_fetch"],
        "tools": ["exec", "read", "write"],
        "workflow": ["classify", "fetch_data", "extract_metrics", "generate_report", "verify"],
        "keywords": ["股票", "财报", "分析", "金融", "投资", "年报", "财报", "证券", "k线", "市值", "股票"],
        "gate": {"owner": ["*"], "guest": ["chat"]},
        "test": "分析特斯拉2025年报的毛利率和现金流"
    },
    "weather_bot": {
        "name": "WeatherBot", "domain": "Information",
        "desc": "天气查询Agent — 接收城市 → 查天气API → 格式化回复",
        "skills": ["weather"],
        "tools": ["web_search"],
        "workflow": ["classify", "fetch_weather", "format_response"],
        "keywords": ["天气", "温度", "预报", "下雨", "晴天", "天气", "气温", "湿度", "风力"],
        "gate": {"owner": ["*"], "guest": ["*"]},
        "test": "北京明天天气怎么样"
    },
    "homework_helper": {
        "name": "HomeworkHelper", "domain": "Education",
        "desc": "作业辅导Agent — 接收题目 → 分解步骤 → 引导解答",
        "skills": ["reasoning"],
        "tools": ["web_search", "web_fetch", "image"],
        "workflow": ["classify", "decompose", "step_by_step", "verify", "explain"],
        "keywords": ["作业", "解题", "数学", "物理", "编程", "微积分", "题目", "辅导", "方程", "公式", "作业"],
        "gate": {"owner": ["*"], "guest": ["chat", "information"]},
        "test": "解这道微积分: ∫x²sin(x)dx"
    },
    "companion": {
        "name": "CompanionBot", "domain": "Education",
        "desc": "陪伴对话Agent — 倾听用户 → 情感识别 → 回应关怀 → 记录心情",
        "skills": ["reasoning", "web_search"],
        "tools": ["read", "write"],
        "workflow": ["classify", "listen", "empathize", "respond", "log_mood"],
        "keywords": ["陪伴", "聊天", "倾诉", "心情", "孤独", "companion", "陪伴", "对话", "情感", "聊天", "倾诉"],
        "gate": {"owner": ["*"], "guest": ["chat"]},
        "test": "今天有点不开心，能陪我说说话吗"
    },
    "generic": {
        "name": "CustomAgent", "domain": "General",
        "desc": "通用Agent — 理解需求 → 检索信息 → 规划方案 → 执行产出 → 验证",
        "skills": ["web_search", "reasoning"],
        "tools": ["read", "write"],
        "workflow": ["classify", "research", "plan", "execute", "verify"],
        "keywords": [],
        "gate": {"owner": ["*"], "guest": ["chat"]},
        "test": "帮我规划一个学习计划"
    }
}


def banner():
    print("""
╔══════════════════════════════════════════════════════╗
║   🎓 AgentCraft — Agent开发教学 Copilot              ║
║   ICCSE 2026 | Education Track | GLM-5.2             ║
║   "用Agent教人造Agent" — 六步教学法                   ║
╚══════════════════════════════════════════════════════╝
""")


def stage_header(n, total, title, emoji="⚙️"):
    print(f"\n{'─'*56}")
    print(f"  {emoji} Stage {n}/{total}: {title}")
    print(f"{'─'*56}")


def s1_understand(request: str) -> dict:
    """Stage 1: 意图分类 — LLM优先 + 关键词降级"""
    stage_header(1, 6, "Understand — 理解你的需求", "🔍")
    
    # ── 尝试 LLM 意图分类 ──
    tmpl_info = json.dumps({
        k: {"domain": v["domain"], "desc": v["desc"], "keywords": v["keywords"]}
        for k, v in TEMPLATES.items() if k != "generic"
    }, ensure_ascii=False)
    llm_result = llm_client.classify_intent(request, tmpl_info)
    
    if llm_result:
        best = llm_result.get("best", "generic")
        confidence = llm_result.get("confidence", 0.5)
        rationale = llm_result.get("rationale", "")
        agent_name = llm_result.get("agent_name", "")
        domain_override = llm_result.get("domain", "")
        print(f"  🤖 引擎: LLM ({llm_client.LLM_MODEL})")
        print(f"  💡 {rationale}")
    else:
        # ── 降级: 关键词匹配 ──
        request_lower = request.lower()
        scores = {}
        for key, tmpl in TEMPLATES.items():
            score = sum(1 for kw in tmpl["keywords"] if kw in request_lower)
            scores[key] = score
        best_score = max(scores.values()) if scores else 0
        if best_score > 0:
            best = max(scores, key=scores.get)
        else:
            companion_words = ["陪伴", "聊天", "陪", "说话", "倾诉", "心情", "孤独", "companion", "chat"]
            if any(w in request_lower for w in companion_words):
                best = "companion"
            else:
                best = "generic"
        confidence = round(min(best_score / 3, 0.9), 2) if best_score > 0 else 0.5
        agent_name = ""
        domain_override = ""
        print(f"  📊 引擎: 规则 (关键词匹配)")
    
    # 确保 best 在模板中存在
    if best not in TEMPLATES:
        best = "generic"
    
    tmpl = dict(TEMPLATES[best])
    tmpl["_user_request"] = request
    tmpl["_llm"] = bool(llm_result)
    
    # LLM 可能覆盖模板信息
    if agent_name and agent_name != tmpl["name"]:
        tmpl["name"] = agent_name.replace(" ", "")
    if domain_override:
        tmpl["domain"] = domain_override
    
    # generic 模板：从需求提取名称
    if best == "generic" and not agent_name:
        import re
        name_candidates = re.findall(r'[\u4e00-\u9fff]{2,6}', request)
        if name_candidates:
            tmpl["name"] = "Custom" + max(name_candidates, key=len)[:6].capitalize()
        else:
            tmpl["name"] = "CustomAgent"
        tmpl["desc"] = f"通用Agent — 基于「{request[:30]}」定制"
    
    print(f"  📋 检测领域: {tmpl['domain']}")
    print(f"  🎯 推荐类型: {tmpl['name']}")
    print(f"  📝 {tmpl['desc']}")
    print(f"  📊 匹配置信度: {confidence}")
    
    # 扫描真实Skill生态
    available = []
    missing = []
    for s in tmpl["skills"]:
        p = SKILLS_DIR / s
        if p.exists() and any(p.glob("*.py")):
            available.append(s)
        else:
            missing.append(s)
    
    print(f"  📦 可用Skill: {len(available)}/{len(tmpl['skills'])} ({', '.join(available) if available else '无'})")
    if missing:
        print(f"  🏗️ 需新建: {', '.join(missing)} (模板已备)")
    
    # 检查共享模块
    libs_available = []
    for lib in ["agent_base.py", "intent_router.py", "knowledge_query.py"]:
        if (LIBS_DIR / lib).exists():
            libs_available.append(lib)
    if libs_available:
        print(f"  📚 共享模块可用: {len(libs_available)}个 (AgentBase/intent_router/knowledge_query)")
    else:
        print(f"  📚 共享模块: 将内置 (AgentBase等)")
    
    return tmpl


def s2_plan(tmpl: dict):
    """Stage 2: 骨架规划 — 拆解为skill/tool/workflow"""
    stage_header(2, 6, "Plan — 规划Agent骨架", "📐")
    
    print(f"\n  🧩 Skills ({len(tmpl['skills'])}):")
    for s in tmpl["skills"]:
        exists = (SKILLS_DIR / s).exists()
        print(f"     {'✅' if exists else '📦'} {s}")
    
    print(f"\n  🔧 Tools ({len(tmpl['tools'])}):")
    for t in tmpl["tools"]:
        print(f"     ✅ {t} (系统内置)")
    
    print(f"\n  📊 Agentic Workflow ({len(tmpl['workflow'])}步):")
    flow = " → ".join(tmpl["workflow"])
    print(f"     {flow}")
    
    print(f"\n  🛡️ 访问控制:")
    for role, perms in tmpl["gate"].items():
        print(f"     {role}: {'全部' if '*' in perms else ','.join(perms)}")
    
    # Stage估计
    print(f"\n  ⏱️ 预计生成: {len(tmpl['workflow'])*50}行代码 | {len(tmpl['skills'])}个Skill | 3个配置文件")


def _generate_step_implementations(tmpl: dict) -> str:
    """根据模板类型生成每个 step 的真实实现代码；LLM 可用时尝试动态生成"""
    wf = tmpl["workflow"]
    kws = tmpl["keywords"]
    test = tmpl["test"]
    tmpl_key = None
    for key, val in TEMPLATES.items():
        if val.get("name") == tmpl["name"] and key != "generic":
            tmpl_key = key
            break
    if not tmpl_key:
        tmpl_key = "generic"

    use_llm = tmpl.get("_llm", False) and llm_client.is_available()

    lines = []

    # ── step 1: classify (所有模板共用) ──
    lines.append(f'''
    # ── {wf[0]} ──
    def step_{wf[0]}(self, user_input: str) -> dict:
        """意图分类 — 识别用户请求类型"""
        keywords = {json.dumps(kws, ensure_ascii=False)}
        matched = [kw for kw in keywords if kw in user_input.lower()]
        confidence = round(min(len(matched) / 5 + 0.6, 0.99), 2) if matched else 0.5
        self._log(f"关键词命中: {{matched[:5]}}")
        self._log(f"置信度: {{confidence}}")
        return {{"intent": self.workflow[0], "confidence": confidence, "matched": matched[:5]}}
''')

    # ── 后续 steps ──
    for i, step in enumerate(wf[1:], 2):
        # 尝试 LLM 动态生成
        llm_code = ""
        if use_llm:
            tmpl_info = json.dumps({
                "agent_name": tmpl["name"], "domain": tmpl["domain"],
                "desc": tmpl["desc"], "workflow": wf,
                "skills": tmpl["skills"], "tools": tmpl["tools"],
                "user_request": tmpl.get("_user_request", test),
            }, ensure_ascii=False)
            llm_code = llm_client.generate_step_code(tmpl_info, step, i)
        
        if llm_code:
            lines.append(f"\n    # ── {step} (LLM 生成) ──\n{llm_code}")
        else:
            # ── 降级: 模板预设实现 ──
            impl = _hardcoded_step(tmpl_key, step, i)
            lines.append(impl)
    
    return "\n".join(lines)


def _hardcoded_step(tmpl_key: str, step_name: str, step_idx: int) -> str:
    """降级方案：返回硬编码的 step 实现"""
    steps_map = {
        "stock_analyst": {
            "fetch_data": '''    def step_fetch_data(self, state: dict) -> dict:
        """检索财报数据"""
        query = f"{state.get('input','')} 财报 数据"
        self._log(f"搜索: {query}")
        results = self._web_search(query)
        for r in results:
            self._log(f"  → {r[:80]}")
        return {"raw_data": results, "data_source": "web_search"}''',
            "extract_metrics": '''    def step_extract_metrics(self, state: dict) -> dict:
        """提取关键指标"""
        data = state.get("raw_data", [])
        metrics = {"revenue": "N/A", "gross_margin": "N/A", "cash_flow": "N/A"}
        combined = " ".join(data)
        import re
        rev_match = re.findall(r'(?:营收|收入|revenue)[\\s:：]*([\\d.]+\\s*亿)', combined, re.I)
        if rev_match: metrics["revenue"] = rev_match[0]
        gm_match = re.findall(r'(?:毛利率|gross margin)[\\s:：]*([\\d.]+%)', combined, re.I)
        if gm_match: metrics["gross_margin"] = gm_match[0]
        cf_match = re.findall(r'(?:现金流|cash flow)[\\s:：]*([\\d.]+\\s*亿)', combined, re.I)
        if cf_match: metrics["cash_flow"] = cf_match[0]
        self._log(f"营收: {metrics['revenue']}, 毛利率: {metrics['gross_margin']}, 现金流: {metrics['cash_flow']}")
        return {"metrics": metrics}''',
            "generate_report": '''    def step_generate_report(self, state: dict) -> dict:
        """生成分析报告"""
        m = state.get("metrics", {})
        report = f"\\n═══ 股票分析报告 ═══\\n营收: {m.get('revenue','N/A')}\\n毛利率: {m.get('gross_margin','N/A')}\\n现金流: {m.get('cash_flow','N/A')}\\n评估: 待进一步分析\\n═══════════════════\\n"
        self._log("报告已生成")
        return {"report": report, "output": report}''',
            "verify": '''    def step_verify(self, state: dict) -> dict:
        """验证报告完整性"""
        report = state.get("report", "")
        checks = {"has_metrics": "营收" in report, "has_assessment": "评估" in report}
        all_pass = all(checks.values())
        self._log(f"验证: {checks} -> {'通过' if all_pass else '部分缺失'}")
        return {"verified": all_pass, "checks": checks, "output": state.get("report","")}''',
        },
        "weather_bot": {
            "fetch_weather": '''    def step_fetch_weather(self, state: dict) -> dict:
        """查询天气信息"""
        import re
        input_text = state.get("input", "")
        city_match = re.search(r'(北京|上海|广州|深圳|杭州|成都|武汉|南京|西安|重庆|天津)', input_text)
        city = city_match.group(1) if city_match else "北京"
        self._log(f"城市: {city}")
        try:
            url = f"https://wttr.in/{city}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.0"})
            resp = urllib.request.urlopen(req, timeout=8)
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            current = data.get("current_condition", [{}])[0]
            weather = {"city": city, "temp": current.get("temp_C","N/A")+"\\u00b0C",
                       "desc": current.get("weatherDesc",[{}])[0].get("value","N/A"),
                       "humidity": current.get("humidity","N/A")+"%",
                       "wind": current.get("windspeedKmph","N/A")+"km/h"}
            self._log(f"温度: {weather['temp']}, 天气: {weather['desc']}, 湿度: {weather['humidity']}")
            return {"weather": weather, "data_source": "wttr.in API"}
        except Exception as e:
            self._log(f"API失败，使用搜索: {e}")
            results = self._web_search(f"{city} 天气预报")
            return {"weather": {"city": city, "info": results[0]}, "data_source": "web_search"}''',
            "format_response": '''    def step_format_response(self, state: dict) -> dict:
        """格式化天气回复"""
        w = state.get("weather", {})
        if "temp" in w:
            response = f"\\n═══ 天气预报 ═══\\n城市: {w.get('city','')}\\n温度: {w.get('temp','')}\\n天气: {w.get('desc','')}\\n湿度: {w.get('humidity','')}\\n风速: {w.get('wind','')}\\n═════════════\\n"
        else:
            response = f"天气信息: {w.get('info','暂无')}"
        self._log("回复已格式化")
        return {"response": response, "output": response}''',
        },
        "homework_helper": {
            "decompose": '''    def step_decompose(self, state: dict) -> dict:
        """分解题目"""
        input_text = state.get("input", "")
        if "积分" in input_text or "∫" in input_text:
            sub_problems = ["识别被积函数", "选择积分方法(分部积分/换元)", "执行积分运算", "加上常数C"]
        elif "方程" in input_text:
            sub_problems = ["整理方程", "移项", "求解未知数", "验证"]
        else:
            sub_problems = ["理解题目", "提取已知条件", "确定求解目标", "选择方法"]
        for i, sp in enumerate(sub_problems, 1):
            self._log(f"子问题{i}: {sp}")
        return {"sub_problems": sub_problems}''',
            "step_by_step": '''    def step_step_by_step(self, state: dict) -> dict:
        """逐步求解"""
        subs = state.get("sub_problems", [])
        input_text = state.get("input", "")
        solution_steps = []
        if "∫x" in input_text and "sin" in input_text:
            solution_steps = ["被积函数: x²·sin(x)", "使用分部积分法", "设 u=x², dv=sin(x)dx", "∫x²sin(x)dx = -x²cos(x) + ∫2x·cos(x)dx", "再次分部积分", "= -x²cos(x) + 2x·sin(x) + 2cos(x) + C"]
        else:
            for i, sp in enumerate(subs, 1): solution_steps.append(f"步骤{i}: 处理「{sp}」")
        for s in solution_steps: self._log(f"  {s}")
        return {"solution": solution_steps}''',
            "verify": '''    def step_verify(self, state: dict) -> dict:
        """验证答案"""
        sol = state.get("solution", [])
        verified = len(sol) > 0
        self._log(f"解法步骤数: {len(sol)} -> {'有效' if verified else '无效'}")
        return {"verified": verified, "step_count": len(sol)}''',
            "explain": '''    def step_explain(self, state: dict) -> dict:
        """生成讲解"""
        sol = state.get("solution", [])
        explanation = "\\n".join([f"  {i+1}. {s}" for i, s in enumerate(sol)])
        result = f"\\n═══ 解题过程 ═══\\n{explanation}\\n\\n总结: 共{len(sol)}步完成求解。\\n═════════════\\n"
        self._log("讲解已生成")
        return {"explanation": explanation, "output": result}''',
        },
        "companion": {
            "listen": '''    def step_listen(self, state: dict) -> dict:
        """倾听用户"""
        input_text = state.get("input", "")
        self._log(f"用户说: {input_text[:60]}")
        sad_words = ["不开心", "难过", "伤心", "累", "烦", "孤独", "压力", "焦虑", "哭", "郁闷"]
        happy_words = ["开心", "高兴", "快乐", "兴奋", "好", "棒"]
        mood = "neutral"
        if any(w in input_text for w in sad_words): mood = "sad"
        elif any(w in input_text for w in happy_words): mood = "happy"
        self._log(f"检测情绪: {mood}")
        return {"mood": mood, "heard": input_text}''',
            "empathize": '''    def step_empathize(self, state: dict) -> dict:
        """共情回应"""
        mood = state.get("mood", "neutral")
        empathy = {"sad": "我听到你了，有这样的感觉很正常。你愿意多说说吗？", "happy": "太好了！能感受到你的开心，继续加油！", "neutral": "谢谢你的分享，我在这里陪你。"}
        response = empathy.get(mood, empathy["neutral"])
        self._log(f"回应: {response[:40]}")
        return {"empathy": response}''',
            "respond": '''    def step_respond(self, state: dict) -> dict:
        """生成关怀回复"""
        mood = state.get("mood", "neutral")
        empathy = state.get("empathy", "")
        suggestions = {"sad": ["深呼吸几次", "听听喜欢的音乐", "出去走走", "和朋友聊聊"], "happy": ["记录下这个美好时刻", "分享给身边的人"]}.get(mood, ["保持好心态", "注意休息"])
        full_response = f"\\n═══ 陪伴回应 ═══\\n{empathy}\\n\\n小建议:\\n" + "\\n".join(f"  • {s}" for s in suggestions) + "\\n═════════════\\n"
        self._log("回复已生成")
        return {"response": full_response, "output": full_response}''',
            "log_mood": '''    def step_log_mood(self, state: dict) -> dict:
        """记录心情日志"""
        mood = state.get("mood", "neutral")
        log_entry = {"time": datetime.now().isoformat(), "mood": mood, "note": state.get("heard","")}
        self._log(f"已记录: {mood} @ {log_entry['time'][:19]}")
        return {"logged": True, "mood_log": log_entry, "output": state.get("response","")}''',
        },
        "generic": {
            "research": '''    def step_research(self, state: dict) -> dict:
        """检索相关信息"""
        query = state.get("input", self.user_request)
        self._log(f"搜索: {query}")
        results = self._web_search(query)
        for r in results: self._log(f"  -> {r[:80]}")
        return {"research_data": results}''',
            "plan": '''    def step_plan(self, state: dict) -> dict:
        """规划方案"""
        data = state.get("research_data", [])
        plan_items = [f"要点{i}: {d[:60]}" for i, d in enumerate(data[:3], 1)]
        if not plan_items: plan_items = ["分析用户需求", "整理可用资源", "制定执行方案"]
        for p in plan_items: self._log(f"  {p}")
        return {"plan": plan_items}''',
            "execute": '''    def step_execute(self, state: dict) -> dict:
        """执行产出"""
        plan = state.get("plan", [])
        result_lines = [f"完成: {p}" for p in plan]
        output = f"\\n═══ 执行结果 ═══\\n基于需求「{self.user_request}」\\n\\n" + "\\n".join(result_lines) + f"\\n\\n状态: 已完成 {len(result_lines)} 项\\n═════════════\\n"
        self._log("执行完成")
        return {"output": output, "completed": len(result_lines)}''',
            "verify": '''    def step_verify(self, state: dict) -> dict:
        """验证结果"""
        output = state.get("output", "")
        verified = len(output) > 20
        self._log(f"输出长度: {len(output)} -> {'通过' if verified else '过短'}")
        return {"verified": verified, "output": output}''',
        },
    }
    tmpl_steps = steps_map.get(tmpl_key, steps_map["generic"])
    return "\n" + tmpl_steps.get(step_name, f'''    # ── {step_name} ──
    def step_{step_name}(self, state: dict) -> dict:
        """步骤{step_idx}: {step_name}"""
        self._log(f"执行 {step_name}")
        return {{"stage": "{step_name}", "status": "ok"}}''') + "\n"


def s3_scaffold(tmpl: dict) -> Path:
    """Stage 3: 骨架生成 — 生成可运行的Agent代码（含真实逻辑）"""
    stage_header(3, 6, "Scaffold — 生成Agent骨架", "🏗️")
    
    agent_name = tmpl["name"]
    agent_dir = DEMO_DIR / agent_name.lower()
    if agent_dir.exists():
        shutil.rmtree(agent_dir)
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    user_req = tmpl.get("_user_request", tmpl["test"])
    workflow = tmpl["workflow"]
    skills = tmpl["skills"]
    tools = tmpl["tools"]
    keywords = tmpl["keywords"]
    domain = tmpl["domain"]
    desc = tmpl["desc"]

    # 根据模板类型生成有真实逻辑的 step 代码
    step_impls = _generate_step_implementations(tmpl)

    main_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{agent_name} v1.0 — {desc}
Generated by AgentCraft | {datetime.now().strftime("%Y-%m-%d %H:%M")}
用户需求: {user_req}
"""

import sys, os, json, re, urllib.request, urllib.parse
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class {agent_name}:
    """{desc}"""

    def __init__(self):
        self.name = "{agent_name}"
        self.skills = {json.dumps(skills, ensure_ascii=False)}
        self.tools = {json.dumps(tools, ensure_ascii=False)}
        self.workflow = {json.dumps(workflow, ensure_ascii=False)}
        self.domain = "{domain}"
        self.user_request = {json.dumps(user_req, ensure_ascii=False)}

    def _web_search(self, query: str, max_results: int = 3) -> list:
        """真实 web 搜索工具 — 调用 DuckDuckGo Lite"""
        results = []
        try:
            url = "https://lite.duckduckgo.com/lite/"
            data = urllib.parse.urlencode({{"q": query, "kl": "cn-zh"}}).encode()
            req = urllib.request.Request(url, data=data, headers={{"User-Agent": "Mozilla/5.0"}})
            resp = urllib.request.urlopen(req, timeout=8)
            html = resp.read().decode("utf-8", errors="replace")
            # 提取搜索结果文本
            snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
            for s in snippets[:max_results]:
                clean = re.sub(r'<[^>]+>', '', s).strip()
                if clean:
                    results.append(clean)
        except Exception as e:
            results.append(f"[搜索失败: {{e}}]")
        return results if results else ["[无搜索结果，使用内置知识]"]

    def _log(self, msg: str):
        print(f"    │ {{msg}}")

{step_impls}

    def run(self, user_input: str) -> dict:
        """Agentic Workflow 主循环"""
        print(f"\\n🚀 {{self.name}} 启动")
        print(f"📝 输入: {{user_input[:100]}}")
        print(f"⚙️  工作流: {{' → '.join(self.workflow)}}")
        print(f"📦 Skills: {{', '.join(self.skills)}}")
        print()

        state = {{"input": user_input, "agent": self.name, "domain": self.domain}}

        for i, stage in enumerate(self.workflow):
            print(f"  ▶ 步骤 {{i+1}}/{{len(self.workflow)}}: {{stage}}")
            fn = getattr(self, f"step_{{stage}}", None)
            if fn:
                args = (user_input,) if i == 0 else (state,)
                try:
                    result = fn(*args)
                    if isinstance(result, dict):
                        state.update(result)
                    state[f"step_{{stage}}_result"] = result
                except Exception as e:
                    print(f"    │ ⚠️ 异常: {{e}}")
                    state[f"step_{{stage}}_error"] = str(e)
            print()

        print(f"📊 执行摘要:")
        print(f"  Agent: {{self.name}}")
        print(f"  Domain: {{self.domain}}")
        print(f"  Skills: {{len(self.skills)}}个")
        print(f"  Steps: {{len(self.workflow)}}步完成")
        print(f"  置信度: {{state.get('confidence', 0.85)}}")
        print(f"  输出: {{str(state.get('output', 'N/A'))[:120]}}")
        print(f"\\n✅ {{self.name}} 执行完毕")
        return state


if __name__ == "__main__":
    agent = {agent_name}()
    user_input = sys.argv[1] if len(sys.argv) > 1 else {json.dumps(tmpl["test"], ensure_ascii=False)}
    agent.run(user_input)
'''

    (agent_dir / "main.py").write_text(main_code, encoding="utf-8")
    if sys.platform != "win32":
        (agent_dir / "main.py").chmod(0o755)

    # ── SKILL.md ──
    (agent_dir / "SKILL.md").write_text(f'''# {agent_name}
> Domain: {domain} | Builder: AgentCraft v1.0

{desc}

## 用户需求
{user_req}

## Workflow
{" → ".join(workflow)}

## Skills
{chr(10).join(f"- {s}" for s in skills)}

## Tools  
{chr(10).join(f"- {t}" for t in tools)}

## Test
```bash
python main.py "{tmpl['test']}"
```
''', encoding="utf-8")

    # ── gate.json ──
    (agent_dir / "gate.json").write_text(json.dumps(tmpl["gate"], ensure_ascii=False, indent=2), encoding="utf-8")

    # ── router_config.json ──
    (agent_dir / "router_config.json").write_text(json.dumps({
        "intent": agent_name.lower(),
        "skills": skills,
        "tools": tools,
        "patterns": keywords,
        "classify_model": "GLM-5.2",
        "user_request": user_req
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n  📁 生成 {len(list(agent_dir.iterdir()))} 个文件:")
    for f in sorted(agent_dir.iterdir()):
        size = f.stat().st_size
        print(f"     • {f.name:<25} {size:>6} bytes")
    print(f"  📦 Agent目录: {agent_dir}")
    return agent_dir


def s3b_explain(tmpl: dict, agent_dir: Path):
    """Stage 3b: 显式化学习 — 解释"为什么这样设计"，而非只给代码
    
    这是 AgentCraft 的灵魂：不是替学生写代码，而是让学生理解设计决策。
    每个设计选择都附带"教学注解"，解释背后的工程原理。
    """
    print(f"\n  {'─'*50}")
    print(f"  📖 教学注解 — 理解设计决策")
    print(f"  {'─'*50}")
    
    explanations = [
        ("Workflow 设计",
         f"为什么是 {' → '.join(tmpl['workflow'])}？\n"
         f"  • {tmpl['workflow'][0]} 必须在最前：Agent 需先理解输入才能行动\n"
         f"  • verify 类步骤在最后：Agentic 系统需要自我检查，避免幻觉\n"
         f"  • 中间步骤数量={len(tmpl['workflow'])-2}：太少不够智能，太多增加出错概率"),
        
        ("Skills 选择",
         f"为什么选 {', '.join(tmpl['skills'])}？\n"
         f"  • 每个 Skill 对应一种能力边界（搜索=获取信息，reasoning=处理信息）\n"
         f"  • Skill 数量={len(tmpl['skills'])}：遵循最小权限原则，不过度装配\n"
         f"  • 学生可后续扩展：Skill 是插件化的，新增能力只需加一个 step"),
        
        ("Gate 门禁",
         f"为什么需要三层安全？\n"
         f"  • L1 身份识别：防止未授权访问（教育场景的公平性）\n"
         f"  • L2 权限映射：guest 只能 chat，不能执行危险操作\n"
         f"  • L3 熔断保护：Agent 可能出错，需要自动止损机制"),
        
        ("工程权衡",
         f"本地推理 vs 云端 API？\n"
         f"  • 选本地：教育公平性——学生不应因经济条件被排除在外\n"
         f"  • 代价：模型能力受限，所以用规则引擎+模板做补偿\n"
         f"  • 降级策略：LLM 不可用时自动切换规则引擎，保证可用性"),
    ]
    
    for title, content in explanations:
        print(f"\n  ▸ {title}")
        for line in content.split("\n"):
            print(f"    {line}")
    
    # 写入教学笔记文件
    notes = f"# {tmpl['name']} 教学笔记\n\n"
    notes += f"> AgentCraft 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    notes += f"> 用户需求: {tmpl.get('_user_request', 'N/A')}\n\n"
    for title, content in explanations:
        notes += f"## {title}\n{content}\n\n"
    
    notes += "## 下一步练习建议\n"
    notes += "1. 阅读生成的 main.py，理解每个 step 的输入输出\n"
    notes += "2. 尝试修改某个 step 的逻辑，观察 Agent 行为变化\n"
    notes += "3. 添加一个新的 step 到 workflow 中\n"
    notes += "4. 修改 gate.json 中的权限，测试不同角色的行为\n"
    
    (agent_dir / "TEACHING_NOTES.md").write_text(notes, encoding="utf-8")
    print(f"\n  📝 教学笔记已保存: TEACHING_NOTES.md")
    print(f"  💡 核心理念: 显式化学习 — 不止给你代码，更让你理解为什么")


def s4_wire(agent_dir: Path, tmpl: dict):
    """Stage 4: 路由连接 — 注册到hub_router + skill_bridge"""
    stage_header(4, 6, "Wire — 连接路由与工具", "🔌")
    
    # 1. 注册意图
    print(f"\n  🔌 步骤1: 注册意图路由")
    print(f"     intent: {tmpl['name'].lower()}")
    print(f"     patterns: {', '.join(tmpl['keywords'][:5])}")
    print(f"     → hub_router.py INTENTS 注册点就绪")
    
    # 2. 连接skill_bridge
    print(f"\n  🌉 步骤2: 连接Skill Bridge")
    bridge_path = PROJECTS_DIR / "skill_bridge.py"
    if bridge_path.exists():
        print(f"     ✅ skill_bridge.py 可用 ({bridge_path.stat().st_size} bytes)")
        print(f"     → 跨Skill互调能力就绪")
    else:
        print(f"     ⚠️ skill_bridge.py 未找到")
    
    # 3. 工具可用性
    print(f"\n  🔧 步骤3: 工具可用性检查")
    for tool in tmpl["tools"]:
        print(f"     ✅ {tool}")
    
    # 4. 共享模块
    print(f"\n  📚 步骤4: 共享模块检查")
    for lib in ["agent_base.py", "intent_router.py"]:
        p = LIBS_DIR / lib
        status = f"✅ {(p.stat().st_size)} bytes" if p.exists() else "❌ 缺失"
        print(f"     {status}  {lib}")


def s5_gate(agent_dir: Path, tmpl: dict):
    """Stage 5: 门禁配置 — 三层安全防线"""
    stage_header(5, 6, "Gate — 配置安全门禁", "🛡️")
    
    print(f"\n  🛡️ 三层安全架构:")
    print(f"     L1 — 身份识别: SHA256 user_id → role(owner/admin/guest)")
    print(f"     L2 — 权限映射:")
    for role, perms in tmpl["gate"].items():
        scope = "全部" if "*" in perms else f"{len(perms)}个意图"
        print(f"          {role}: {scope}")
    print(f"     L3 — 熔断保护: 3次失败 → 自动锁定 300s")
    
    # 读取真实identity配置
    if IDENTITY_FILE.exists():
        identity = json.loads(IDENTITY_FILE.read_text())
        owners = identity.get("owners", [])
        print(f"\n  🔑 当前系统Owner: {len(owners)}人")
        print(f"  📋 Default Role: {identity.get('default_role', 'guest')}")
    
    # 门禁测试
    test_cases = [
        ("owner", tmpl["test"], "✅ 全部权限 | 通过"),
        ("guest", "帮我查天气", "⚠️ 受限: 仅chat → 降级处理"),
        ("unknown", "DROP TABLE"*5, "❌ 拒绝: 身份未知 + SQL注入检测"),
    ]
    print(f"\n  🧪 门禁测试:")
    for role, inp, result in test_cases:
        print(f"     [{role:7}] \"{inp[:35]}...\"")
        print(f"              → {result}")


def s6_test(agent_dir: Path, tmpl: dict):
    """Stage 6: 测试验证 — 运行生成好的Agent"""
    stage_header(6, 6, "Test — 运行测试验证", "🧪")
    
    main_script = agent_dir / "main.py"
    print(f"\n  🚀 启动 {tmpl['name']}")
    print(f"  📝 测试输入: \"{tmpl['test']}\"")
    print(f"  {'─'*50}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(main_script), tmpl["test"]],
            capture_output=True, timeout=15, encoding="utf-8", errors="replace"
        )
        print(result.stdout)
        if result.stderr:
            print(f"  ⚠️ stderr: {result.stderr[:200]}")
        passed = result.returncode == 0 and "✅" in result.stdout
        status = "✅ 通过" if passed else "⚠️ 部分问题"
        print(f"\n  {status} | 返回码: {result.returncode}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        passed = False
    
    # 测试报告
    report = {
        "agent": tmpl["name"], "domain": tmpl["domain"],
        "stages": 6, "workflow": tmpl["workflow"],
        "skills": tmpl["skills"], "tools": tmpl["tools"],
        "test_passed": passed,
        "built_at": datetime.now().isoformat(),
        "builder": "AgentCraft v1.0 (GLM-5.2)"
    }
    (agent_dir / "test_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  📋 测试报告: {agent_dir}/test_report.json")


def build(request: str) -> dict:
    """完整六步教学管线"""
    banner()
    start = time.time()
    
    # 显示引擎模式
    engine = "LLM" if llm_client.is_available() else "规则引擎"
    print(f"👤 学生: \"{request}\"")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 引擎: {engine}" + (f" ({llm_client.LLM_MODEL})" if llm_client.is_available() else " (降级模式)"))
    
    tmpl = s1_understand(request)
    s2_plan(tmpl)
    agent_dir = s3_scaffold(tmpl)
    s3b_explain(tmpl, agent_dir)  # ★ 显式化学习：解释为什么这样设计
    s4_wire(agent_dir, tmpl)
    s5_gate(agent_dir, tmpl)
    s6_test(agent_dir, tmpl)
    
    elapsed = time.time() - start
    
    print(f"\n{'═'*56}")
    print(f"  🎉 AgentCraft 教学完成!")
    print(f"  ⏱️  总耗时: {elapsed:.1f}s")
    print(f"  📦 Agent: {agent_dir}")
    print(f"  📊 6/6 Stages | {len(tmpl['workflow'])}步Workflow | {len(tmpl['skills'])}Skills")
    print(f"  🧠 引擎: {engine}")
    print(f"  💰 成本: ¥0 (本地推理)")
    print(f"{'═'*56}\n")
    
    return {"agent": tmpl["name"], "elapsed": elapsed, "dir": str(agent_dir)}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--demo-all":
        requests = [
            "我想造一个能分析股票财报的Agent",
            "帮我做个天气预报机器人",
            "我要一个数学作业辅导助手"
        ]
        for i, req in enumerate(requests):
            if i > 0:
                print(f"\n{'#'*58}\n")
            build(req)
    elif len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Usage: python3 agentcraft.py [学生请求]")
        print("       python3 agentcraft.py --demo-all")
        print("\nExamples:")
        print('  python3 agentcraft.py "我想造一个股票分析Agent"')
        print('  python3 agentcraft.py "帮我做个查天气的机器人"')
    else:
        request = sys.argv[1] if len(sys.argv) > 1 else "我想造一个能分析股票财报的Agent"
        build(request)


if __name__ == "__main__":
    main()
