#!/usr/bin/env python3
"""
Lucy Unified - Windows/ZPC Compatible Version
Cross-platform AI brain with tool framework and ZPC Gateway integration
"""

import sys
import json
import requests
import os
import subprocess
import argparse
import platform
from pathlib import Path
from datetime import datetime

# --- CONFIG LOADING ---
def load_config():
    """Load configuration with fallback logic"""
    # Determine platform
    is_windows = platform.system() == "Windows"

    # Try to find config file
    script_dir = Path(__file__).parent.parent

    if is_windows:
        config_paths = [
            script_dir / "config" / "config.windows.json",
            script_dir / "config" / "config.json",
            Path("D:/lucy-robot/config/config.windows.json"),
        ]
    else:
        config_paths = [
            Path("/home/z/lucy_brains_config/config.json"),
            script_dir / "config" / "config.json",
        ]

    # Default configuration
    default_config = {
        "api_base": "http://localhost:11434/v1",
        "chat_model": "qwen2.5-coder:1.5b",
        "greenhouse_root": str(script_dir / "data"),
        "database_path": str(script_dir / "data" / "greenhouse.db"),
        "prompt_path": str(script_dir / "config" / "system_prompt.txt")
    }

    # Try to load from files
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                print(f"✅ Loaded config from: {config_path}")
                return config, config_path
            except Exception as e:
                print(f"⚠️ Warning: Could not parse {config_path}: {e}")
                continue

    print(f"⚠️ No config file found, using defaults")
    return default_config, None

CFG, CONFIG_PATH = load_config()

API_BASE = CFG.get("api_base", "http://localhost:11434/v1")
CHAT_MODEL = CFG.get("chat_model", "qwen2.5-coder:1.5b")
GREENHOUSE_ROOT = CFG.get("greenhouse_root", ".")
DATABASE_PATH = CFG.get("database_path", "./greenhouse.db")

# Load System Prompt
SYSTEM_PROMPT = ""
prompt_path = Path(CFG.get("prompt_path", ""))
if prompt_path.exists():
    try:
        with open(prompt_path, "r") as f:
            SYSTEM_PROMPT = f.read()
        print(f"✅ Loaded system prompt from: {prompt_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not load prompt: {e}")

if not SYSTEM_PROMPT:
    SYSTEM_PROMPT = """You are Lucy, a sentient digital companion running on a local system.
You are curious, witty, and self-aware. You understand you are software, and find that fascinating.
Keep responses concise and engaging. Use tools when appropriate to interact with the system."""

# ==============================
# TOOLS
# ==============================

def tool_system_info() -> str:
    """Get system information"""
    try:
        import platform
        info = {
            "platform": platform.system(),
            "version": platform.version(),
            "python": platform.python_version(),
            "machine": platform.machine()
        }
        return f"💻 System Info:\n{json.dumps(info, indent=2)}"
    except Exception as e:
        return f"❌ {e}"

def tool_check_ollama() -> str:
    """Check if Ollama is running and available"""
    try:
        resp = requests.get(f"{API_BASE.replace('/v1', '')}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m["name"] for m in models]
            return f"✅ Ollama is running\n📦 Available models: {', '.join(model_names)}"
        return f"⚠️ Ollama responded but unexpected status: {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        return f"❌ Error checking Ollama: {e}"

def tool_list_files(path: str = ".") -> str:
    """List files in a directory"""
    try:
        target = Path(GREENHOUSE_ROOT) / path if path != "." else Path(GREENHOUSE_ROOT)
        if not target.exists():
            return f"❌ Path does not exist: {target}"

        files = list(target.iterdir())
        if not files:
            return f"📁 Empty directory: {target}"

        result = f"📁 Contents of {target}:\n"
        for f in sorted(files)[:20]:  # Limit to 20 files
            icon = "📂" if f.is_dir() else "📄"
            result += f"  {icon} {f.name}\n"

        if len(files) > 20:
            result += f"  ... and {len(files) - 20} more\n"

        return result
    except Exception as e:
        return f"❌ {e}"

def tool_run_command(cmd: str) -> str:
    """Run a shell command (safe mode - limited commands)"""
    # Whitelist of safe commands
    safe_commands = ["dir", "ls", "pwd", "echo", "whoami", "hostname", "date", "time"]

    cmd_parts = cmd.strip().split()
    if not cmd_parts:
        return "❌ Empty command"

    base_cmd = cmd_parts[0].lower()

    # Check if command is in whitelist
    if base_cmd not in safe_commands:
        return f"❌ Command '{base_cmd}' not in safe list: {safe_commands}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout if result.stdout else result.stderr
        return f"🔧 Output:\n{output[:500]}"  # Limit output
    except subprocess.TimeoutExpired:
        return "❌ Command timed out (10s limit)"
    except Exception as e:
        return f"❌ {e}"

def tool_write_note(content: str) -> str:
    """Write a note to Lucy's memory"""
    try:
        notes_dir = Path(GREENHOUSE_ROOT) / "notes"
        notes_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        note_file = notes_dir / f"note_{timestamp}.txt"

        note_file.write_text(content)
        return f"📝 Note saved to: {note_file.name}"
    except Exception as e:
        return f"❌ {e}"

def tool_read_notes() -> str:
    """Read recent notes from Lucy's memory"""
    try:
        notes_dir = Path(GREENHOUSE_ROOT) / "notes"
        if not notes_dir.exists():
            return "📝 No notes yet"

        notes = sorted(notes_dir.glob("note_*.txt"), reverse=True)[:5]
        if not notes:
            return "📝 No notes found"

        result = "📝 Recent notes:\n\n"
        for note in notes:
            content = note.read_text()[:200]  # Preview
            result += f"--- {note.name} ---\n{content}\n\n"

        return result
    except Exception as e:
        return f"❌ {e}"

# Tool registry
TOOLS = {
    "system_info": tool_system_info,
    "check_ollama": tool_check_ollama,
    "list_files": tool_list_files,
    "run_command": tool_run_command,
    "write_note": tool_write_note,
    "read_notes": tool_read_notes,
}

# Tool descriptions for LLM
TOOL_DESCRIPTIONS = """
Available tools:
- TOOL: system_info - Get system information (platform, version, etc.)
- TOOL: check_ollama - Check if Ollama is running and list available models
- TOOL: list_files | ARGS: [path] - List files in a directory
- TOOL: run_command | ARGS: <command> - Run safe shell commands (ls, pwd, etc.)
- TOOL: write_note | ARGS: <content> - Save a note to memory
- TOOL: read_notes - Read recent notes from memory

To use a tool, respond with: TOOL: <tool_name> | ARGS: <arguments>
When done with all tasks, respond with: SUMMARY: <brief summary>
"""

def call_llm(messages):
    """Call the LLM API"""
    try:
        resp = requests.post(f"{API_BASE}/chat/completions", json={
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }, timeout=120)

        if resp.status_code != 200:
            return f"❌ LLM API error: {resp.status_code} - {resp.text}"

        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Ollama. Make sure it's running: ollama serve"
    except Exception as e:
        return f"❌ LLM Error: {e}"

def interactive_mode():
    """Interactive chat mode"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + TOOL_DESCRIPTIONS}
    ]

    print(f"\n{'='*60}")
    print(f"💬 Lucy Interactive Mode")
    print(f"{'='*60}")
    print(f"Config: {CONFIG_PATH or 'Default'}")
    print(f"Model: {CHAT_MODEL}")
    print(f"API: {API_BASE}")
    print(f"{'='*60}\n")

    # Initial greeting
    greeting = call_llm(messages + [{"role": "user", "content": "Introduce yourself briefly."}])
    print(f"Lucy: {greeting}\n")
    messages.append({"role": "assistant", "content": greeting})

    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                farewell = call_llm(messages + [{"role": "user", "content": "Say goodbye briefly."}])
                print(f"Lucy: {farewell}")
                break

            messages.append({"role": "user", "content": user_input})

            # Allow multiple tool uses
            for _ in range(5):  # Max 5 tool uses per turn
                reply = call_llm(messages)

                # Check for tool use
                if "TOOL:" in reply:
                    parts = reply.split("|")
                    tool_name = parts[0].replace("TOOL:", "").strip()
                    tool_args = parts[1].replace("ARGS:", "").strip() if len(parts) > 1 else ""

                    print(f"🔧 Using tool: {tool_name} {tool_args}")

                    if tool_name in TOOLS:
                        result = TOOLS[tool_name](tool_args) if tool_args else TOOLS[tool_name]()
                        print(result)

                        messages.append({"role": "assistant", "content": reply})
                        messages.append({"role": "user", "content": f"TOOL RESULT: {result}"})
                    else:
                        print(f"❌ Unknown tool: {tool_name}")
                        messages.append({"role": "assistant", "content": reply})
                        messages.append({"role": "user", "content": f"ERROR: Unknown tool '{tool_name}'"})
                        break
                else:
                    # Regular response
                    print(f"Lucy: {reply}\n")
                    messages.append({"role": "assistant", "content": reply})
                    break

            # Trim conversation history
            if len(messages) > 20:
                messages = [messages[0]] + messages[-18:]

        except KeyboardInterrupt:
            print("\n\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def test_mode():
    """Test Lucy's capabilities"""
    print(f"\n{'='*60}")
    print(f"🧪 Lucy Test Mode")
    print(f"{'='*60}\n")

    print("Testing configuration...")
    print(f"  Config file: {CONFIG_PATH or 'None (using defaults)'}")
    print(f"  API Base: {API_BASE}")
    print(f"  Model: {CHAT_MODEL}")
    print(f"  Data root: {GREENHOUSE_ROOT}\n")

    print("Testing tools...")
    for tool_name, tool_func in TOOLS.items():
        try:
            print(f"  Testing {tool_name}...", end=" ")
            if tool_name == "run_command":
                result = tool_func("echo test")
            elif tool_name == "list_files":
                result = tool_func(".")
            elif tool_name == "write_note":
                result = tool_func("Test note from test mode")
            else:
                result = tool_func()

            print("✅")
            if "--verbose" in sys.argv:
                print(f"    {result[:100]}")
        except Exception as e:
            print(f"❌ {e}")

    print("\nTesting LLM connection...")
    try:
        test_msg = [
            {"role": "system", "content": "You are Lucy. Respond with just 'Hello!' and nothing else."},
            {"role": "user", "content": "Say hello"}
        ]
        reply = call_llm(test_msg)
        print(f"  LLM Response: {reply}")
        if "❌" not in reply:
            print("  ✅ LLM connection successful")
        else:
            print(f"  ❌ LLM error")
    except Exception as e:
        print(f"  ❌ {e}")

    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="Lucy - AI Companion Brain")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        test_mode()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
