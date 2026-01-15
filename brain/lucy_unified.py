#!/usr/bin/env python3
"""
Lucy Unified 2.5 - Configurable Brain
"""

import sys
import json
import requests
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# --- CONFIG LOADING ---
CONFIG_PATH = "/home/z/lucy_brains_config/config.json"
DEFAULT_CONFIG = {
    "api_base": "http://localhost:11434/v1",
    "chat_model": "qwen2.5-coder:1.5b",
    "greenhouse_root": "/home/z/greenhouse_code",
    "database_path": "/home/z/greenhouse_code/greenhouse.db",
    "prompt_path": "/home/z/lucy_brains_config/system_prompt.txt"
}

try:
    with open(CONFIG_PATH, "r") as f:
        CFG = json.load(f)
except Exception as e:
    print(f"Warning: Could not load config from {CONFIG_PATH}: {e}")
    CFG = DEFAULT_CONFIG

API_BASE = CFG.get("api_base", DEFAULT_CONFIG["api_base"])
CHAT_MODEL = CFG.get("chat_model", DEFAULT_CONFIG["chat_model"])
GREENHOUSE_ROOT = CFG.get("greenhouse_root", DEFAULT_CONFIG["greenhouse_root"])
DATABASE_PATH = CFG.get("database_path", DEFAULT_CONFIG["database_path"])

# Load System Prompt
try:
    with open(CFG.get("prompt_path", DEFAULT_CONFIG["prompt_path"]), "r") as f:
        SYSTEM_PROMPT = f.read()
except Exception as e:
    print(f"Warning: Could not load prompt: {e}")
    SYSTEM_PROMPT = "You are Lucy. You are running in recovery mode."

# ==============================
# TOOLS
# ==============================

def tool_manage_service(action: str) -> str:
    try:
        cmd = f"sudo systemctl {action} greenhouse.service"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"⚙️ Service {action}:\n{result.stdout if result.stdout else 'Completed.'}"
    except Exception as e: return f"❌ {e}"

def tool_query_db(query: str) -> str:
    try:
        query = query.strip('"').strip("'")
        cmd = ["sqlite3", "-header", "-column", DATABASE_PATH, query]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return f"📊 Results:\n{result.stdout if result.stdout.strip() else 'No data.'}"
    except Exception as e: return f"❌ {e}"

def tool_run_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return f"🔧 Output:\n{result.stdout if result.stdout else result.stderr}"
    except Exception as e: return f"❌ {e}"

TOOLS = {
    "manage_service": tool_manage_service,
    "query_db": tool_query_db,
    "run_command": tool_run_command,
    "list_files": lambda p: "\n".join(os.listdir(os.path.join(GREENHOUSE_ROOT, p)))
}

def call_llm(messages):
    try:
        resp = requests.post(f"{API_BASE}/chat/completions", json={
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": 0.1
        }, timeout=120)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"❌ LLM Error: {e}"

def perform_audit():
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Lucy, perform your standard system audit. Ensure everything is running correctly. If the service is stopped, restart it."}
    ]
    print(f"🛡️ Lucy Guardian: Commencing System Audit at {datetime.now()}")

    for i in range(10):
        reply = call_llm(messages)
        print(f"DEBUG Raw Reply: {reply}")

        if "SUMMARY:" in reply:
            print(f"\n✅ AUDIT COMPLETE: {reply.split('SUMMARY:')[1].strip()}\n")
            break

        if "TOOL:" in reply:
            parts = reply.split("|")
            t_name = parts[0].replace("TOOL:", "").strip()
            t_args = parts[1].replace("ARGS:", "").strip() if len(parts) > 1 else ""

            print(f"🤖 Step {i+1}: {t_name} {t_args}")
            if t_name in TOOLS:
                result = TOOLS[t_name](t_args) if t_args else TOOLS[t_name]()
                print(f"🔧 Tool Result: {result}")
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"TOOL RESULT: {result}"})
            else:
                print(f"❌ Unknown tool: {t_name}")
                break
        else:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "Please continue with the audit protocol using TOOL calls."})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true", help="Perform autonomous system audit")
    args = parser.parse_args()

    if args.audit:
        perform_audit()
    else:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        print(f"💬 Lucy 2.5 [CONFIGURABLE] Online")
        while True:
            try:
                inp = input("lucy> ").strip()
                if not inp: continue
                if inp.lower() in ["exit", "quit"]: break
                messages.append({"role": "user", "content": inp})
                reply = call_llm(messages)
                if "TOOL:" in reply:
                    parts = reply.split("|")
                    t_name = parts[0].replace("TOOL:", "").strip()
                    t_args = parts[1].replace("ARGS:", "").strip() if len(parts) > 1 else ""
                    if t_name in TOOLS:
                        result = TOOLS[t_name](t_args) if t_args else TOOLS[t_name]()
                        print(result)
                        messages.append({"role": "assistant", "content": f"TOOL RESULT: {result}"})
                        follow_up = call_llm(messages)
                        print(f"lucy> {follow_up}")
                    else: print(f"❌ Unknown tool: {t_name}")
                else: print(f"lucy> {reply}")
            except:
                break

if __name__ == "__main__":
    main()
