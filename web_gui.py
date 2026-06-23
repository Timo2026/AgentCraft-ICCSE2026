#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentCraft 桌面 GUI（Tkinter）
用于本地演示，无需浏览器。
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess, sys, os, json, threading

AGENTCRAFT_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "agentcraft_skill", "scripts", "agentcraft.py")
)

class AgentCraftGUI:
    def __init__(self, root):
        self.root = root
        root.title("AgentCraft — Agent开发教学 Copilot")
        root.geometry("900x700")
        root.configure(bg="#0f172a")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0f172a")
        style.configure("TLabel", background="#0f172a", foreground="#e2e8f0")
        style.configure("TButton", font=("Microsoft YaHei", 11))

        # 顶部标题
        header = ttk.Frame(root)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        ttk.Label(header, text="🎓 AgentCraft", font=("Microsoft YaHei", 24, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text="Agent开发教学 Copilot — ICCSE 2026", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0))

        # 输入区
        input_frame = ttk.Frame(root)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(input_frame, text="描述你想造的 Agent：").pack(anchor=tk.W)
        self.entry = ttk.Entry(input_frame, font=("Microsoft YaHei", 12))
        self.entry.pack(fill=tk.X, pady=(5, 10))
        self.entry.bind("<Return>", lambda e: self.start_build())
        btn = ttk.Button(input_frame, text="🚀 开始构建", command=self.start_build)
        btn.pack(anchor=tk.E)

        # 六步进度
        self.steps_frame = ttk.Frame(root)
        self.steps_frame.pack(fill=tk.X, padx=20, pady=10)
        self.step_labels = []
        steps = [
            ("🔍", "Understand"),
            ("📐", "Plan"),
            ("🏗️", "Scaffold"),
            ("🔌", "Wire"),
            ("🛡️", "Gate"),
            ("🧪", "Test"),
        ]
        for idx, (icon, title) in enumerate(steps, 1):
            f = ttk.Frame(self.steps_frame)
            f.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.step_labels.append(ttk.Label(f, text=f"{icon}\n{title}", font=("Microsoft YaHei", 9), anchor=tk.CENTER))

        # 终端输出
        self.terminal = scrolledtext.ScrolledText(root, bg="#0b1220", fg="#cbd5e1", font=("Consolas", 10), wrap=tk.WORD)
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        self.terminal.insert(tk.END, "等待输入...\n")
        self.terminal.configure(state=tk.DISABLED)

    def log(self, text, tag=None):
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.insert(tk.END, text + "\n", tag)
        self.terminal.see(tk.END)
        self.terminal.configure(state=tk.DISABLED)

    def set_step(self, idx):
        for i, lbl in enumerate(self.step_labels, 1):
            if i < idx:
                lbl.configure(foreground="#22c55e")
            elif i == idx:
                lbl.configure(foreground="#60a5fa")
            else:
                lbl.configure(foreground="#94a3b8")

    def start_build(self):
        user_input = self.entry.get().strip()
        if not user_input:
            messagebox.showwarning("提示", "请输入你的需求")
            return
        self.entry.configure(state=tk.DISABLED)
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.delete("1.0", tk.END)
        self.terminal.configure(state=tk.DISABLED)
        self.set_step(1)
        self.log("🚀 启动 AgentCraft...", "info")

        threading.Thread(target=self.run, args=(user_input,), daemon=True).start()

    def run(self, user_input):
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
                self.root.after(0, self.log, line.rstrip())
                if "Stage" in line and "/6:" in line:
                    m = line.split("Stage")[1].split(":")[0].split("/")[0].strip()
                    try:
                        self.root.after(0, self.set_step, int(m))
                    except Exception:
                        pass
            proc.wait()
            if proc.returncode == 0:
                self.root.after(0, self.log, "✅ 构建完成！", "success")
            else:
                self.root.after(0, self.log, f"⚠️ 异常，返回码: {proc.returncode}", "error")
        except Exception as e:
            self.root.after(0, self.log, f"❌ 异常: {e}", "error")
        finally:
            self.root.after(0, lambda: self.entry.configure(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    gui = AgentCraftGUI(root)
    root.mainloop()
