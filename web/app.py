from flask import Flask, render_template, request, jsonify, Response
import subprocess, sys, os, json, re, time

app = Flask(__name__)

AGENTCRAFT_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "agentcraft_skill", "scripts", "agentcraft.py")
)

def stream_agentcraft(user_input: str):
    """流式运行 agentcraft.py，实时 yield 输出行"""
    try:
        proc = subprocess.Popen(
            [sys.executable, AGENTCRAFT_SCRIPT, user_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True,
        )
        for line in proc.stdout:
            yield line
        proc.wait()
        yield f"\n__EXIT_CODE__:{proc.returncode}"
    except Exception as e:
        yield f"❌ 异常: {e}\n__EXIT_CODE__:1"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/build")
def api_build():
    user_input = request.args.get("input", "").strip()
    if not user_input:
        return jsonify({"error": "请输入你的需求"}), 400
    return Response(stream_agentcraft(user_input), mimetype="text/plain; charset=utf-8")

@app.route("/api/files")
def api_files():
    """读取最近生成的 Agent 目录中的文件"""
    demo_dir = os.path.expanduser("~/agentcraft_demo")
    if not os.path.isdir(demo_dir):
        return jsonify({"files": []})
    dirs = sorted([d for d in os.listdir(demo_dir) if os.path.isdir(os.path.join(demo_dir, d))], reverse=True)
    if not dirs:
        return jsonify({"files": []})
    agent_dir = os.path.join(demo_dir, dirs[0])
    files = []
    for name in os.listdir(agent_dir):
        path = os.path.join(agent_dir, name)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                content = ""
            files.append({
                "name": name,
                "size": os.path.getsize(path),
                "content": content
            })
    return jsonify({"files": files, "dir": agent_dir})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
