#!/usr/bin/env python3
"""
Lucy Web Interface - Cross-Platform Browser-Based UI
FastAPI + WebSocket for real-time chat and animated face
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import sys
import asyncio
from datetime import datetime
from typing import List

# Add brain to path
sys.path.insert(0, str(Path(__file__).parent.parent / "brain"))

try:
    from lucy_unified_windows import (
        call_llm, TOOLS, SYSTEM_PROMPT, TOOL_DESCRIPTIONS,
        CFG, CHAT_MODEL, API_BASE
    )
    # Try to import ZPC integration
    try:
        from zpc_integration import create_zpc_tools, ZPC_TOOL_DESCRIPTIONS
        ZPC_AVAILABLE = True
    except:
        ZPC_AVAILABLE = False
        ZPC_TOOL_DESCRIPTIONS = ""
except ImportError:
    print("Error: Could not import Lucy brain modules")
    sys.exit(1)

app = FastAPI(title="Lucy Web Interface")

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversation_history = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Combine tools
all_tools = TOOLS.copy()
tool_descriptions = TOOL_DESCRIPTIONS

if ZPC_AVAILABLE:
    zpc_tools = create_zpc_tools()
    all_tools.update(zpc_tools)
    tool_descriptions += "\n" + ZPC_TOOL_DESCRIPTIONS

@app.get("/")
async def get_root():
    """Serve the main HTML interface"""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text())
    return HTMLResponse(content=get_default_html())

@app.get("/api/status")
async def get_status():
    """Get Lucy's status"""
    return {
        "status": "online",
        "model": CHAT_MODEL,
        "api_base": API_BASE,
        "tools_available": list(all_tools.keys()),
        "zpc_integration": ZPC_AVAILABLE,
        "active_connections": len(manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time chat"""
    await manager.connect(websocket)

    # Initialize conversation
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + tool_descriptions}
    ]

    # Send welcome message
    welcome = {
        "type": "system",
        "content": f"Connected to Lucy ({CHAT_MODEL})",
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_message(welcome, websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if data.get("type") == "chat":
                user_message = data.get("message", "").strip()

                if not user_message:
                    continue

                # Echo user message back
                await manager.send_message({
                    "type": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                }, websocket)

                # Add to conversation
                messages.append({"role": "user", "content": user_message})

                # Get Lucy's response (with tool support)
                for _ in range(5):  # Max 5 tool uses per turn
                    # Send "thinking" indicator
                    await manager.send_message({
                        "type": "thinking",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)

                    reply = call_llm(messages)

                    # Check for tool use
                    if "TOOL:" in reply:
                        parts = reply.split("|")
                        tool_name = parts[0].replace("TOOL:", "").strip()
                        tool_args = parts[1].replace("ARGS:", "").strip() if len(parts) > 1 else ""

                        # Send tool use notification
                        await manager.send_message({
                            "type": "tool",
                            "tool": tool_name,
                            "args": tool_args,
                            "timestamp": datetime.now().isoformat()
                        }, websocket)

                        if tool_name in all_tools:
                            # Execute tool
                            result = all_tools[tool_name](tool_args) if tool_args else all_tools[tool_name]()

                            # Send tool result
                            await manager.send_message({
                                "type": "tool_result",
                                "tool": tool_name,
                                "result": result,
                                "timestamp": datetime.now().isoformat()
                            }, websocket)

                            messages.append({"role": "assistant", "content": reply})
                            messages.append({"role": "user", "content": f"TOOL RESULT: {result}"})
                        else:
                            # Unknown tool
                            error_msg = f"❌ Unknown tool: {tool_name}"
                            await manager.send_message({
                                "type": "error",
                                "content": error_msg,
                                "timestamp": datetime.now().isoformat()
                            }, websocket)
                            messages.append({"role": "assistant", "content": reply})
                            messages.append({"role": "user", "content": f"ERROR: {error_msg}"})
                            break
                    else:
                        # Regular response
                        await manager.send_message({
                            "type": "assistant",
                            "content": reply,
                            "timestamp": datetime.now().isoformat()
                        }, websocket)
                        messages.append({"role": "assistant", "content": reply})
                        break

                # Trim conversation history
                if len(messages) > 20:
                    messages = [messages[0]] + messages[-18:]

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

def get_default_html():
    """Default HTML if index.html not found"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lucy - AI Companion</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 5px; }
        .header p { opacity: 0.9; }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 70%;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background: #667eea;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        .assistant-message {
            background: #f0f0f0;
            color: #333;
            align-self: flex-start;
        }
        .system-message {
            background: #e8f5e9;
            color: #2e7d32;
            align-self: center;
            font-size: 0.9em;
            max-width: 90%;
        }
        .tool-message {
            background: #fff3e0;
            color: #e65100;
            align-self: flex-start;
            font-family: monospace;
            font-size: 0.85em;
        }
        .thinking {
            background: #f0f0f0;
            color: #666;
            align-self: flex-start;
            font-style: italic;
        }
        .input-container {
            padding: 20px;
            background: #f9f9f9;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s;
        }
        input:focus { border-color: #667eea; }
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        button:active { transform: scale(0.95); }
        .status {
            padding: 10px;
            background: rgba(102, 126, 234, 0.1);
            text-align: center;
            font-size: 0.9em;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Lucy</h1>
            <p>Your AI Companion</p>
        </div>
        <div class="status" id="status">Connecting...</div>
        <div class="chat-container" id="chat"></div>
        <div class="input-container">
            <input type="text" id="input" placeholder="Talk to Lucy..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let ws = null;
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const status = document.getElementById('status');

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onopen = () => {
                status.textContent = 'Connected to Lucy';
                status.style.background = 'rgba(76, 175, 80, 0.1)';
                status.style.color = '#4caf50';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };

            ws.onclose = () => {
                status.textContent = 'Disconnected. Reconnecting...';
                status.style.background = 'rgba(244, 67, 54, 0.1)';
                status.style.color = '#f44336';
                setTimeout(connect, 2000);
            };
        }

        function handleMessage(data) {
            const msg = document.createElement('div');
            msg.className = 'message';

            switch(data.type) {
                case 'user':
                    msg.classList.add('user-message');
                    msg.textContent = data.content;
                    break;
                case 'assistant':
                    msg.classList.add('assistant-message');
                    msg.textContent = data.content;
                    break;
                case 'system':
                    msg.classList.add('system-message');
                    msg.textContent = `ℹ️ ${data.content}`;
                    break;
                case 'tool':
                    msg.classList.add('tool-message');
                    msg.textContent = `🔧 Using tool: ${data.tool} ${data.args || ''}`;
                    break;
                case 'tool_result':
                    msg.classList.add('tool-message');
                    msg.textContent = data.result;
                    break;
                case 'thinking':
                    msg.classList.add('thinking');
                    msg.textContent = '💭 Thinking...';
                    msg.id = 'thinking';
                    break;
                case 'error':
                    msg.classList.add('system-message');
                    msg.style.background = '#ffebee';
                    msg.style.color = '#c62828';
                    msg.textContent = `⚠️ ${data.content}`;
                    break;
            }

            // Remove previous thinking indicator
            const thinking = document.getElementById('thinking');
            if (thinking && data.type !== 'thinking') {
                thinking.remove();
            }

            chat.appendChild(msg);
            chat.scrollTop = chat.scrollHeight;
        }

        function sendMessage() {
            const message = input.value.trim();
            if (!message) return;

            ws.send(JSON.stringify({
                type: 'chat',
                message: message
            }));

            input.value = '';
        }

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        connect();
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("Lucy Web Interface Starting...")
    print("="*60)
    print(f"Config: {CFG}")
    print(f"Model: {CHAT_MODEL}")
    print(f"Tools: {len(all_tools)} available")
    print(f"ZPC Integration: {'✅ Enabled' if ZPC_AVAILABLE else '❌ Disabled'}")
    print("="*60)
    print("\nOpen your browser to: http://localhost:8080")
    print("Press Ctrl+C to stop\n")

    uvicorn.run(app, host="0.0.0.0", port=8080)
