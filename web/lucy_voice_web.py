#!/usr/bin/env python3
"""
Lucy Voice Web Interface - Complete voice-enabled robot companion
FastAPI server with animated face, voice input/output via browser
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys
import json
from datetime import datetime

# Add brain to path
sys.path.insert(0, str(Path(__file__).parent.parent / "brain"))

from lucy_enhanced import LucyBrain, CHAT_MODEL, API_BASE

app = FastAPI(title="Lucy Voice Web Interface")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except:
            pass

manager = ConnectionManager()

@app.get("/")
async def get_root():
    """Serve the voice-enabled interface"""
    html_file = Path(__file__).parent / "lucy_voice_toggle.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
    return HTMLResponse(content=get_voice_interface_html())

@app.get("/api/status")
async def get_status():
    """Get Lucy's status"""
    return {
        "status": "online",
        "model": CHAT_MODEL,
        "api_base": API_BASE,
        "voice_enabled": True,
        "active_connections": len(manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time voice-enabled chat"""
    await manager.connect(websocket)

    # Create Lucy instance for this connection
    lucy = LucyBrain()

    # Send welcome
    await manager.send_message({
        "type": "system",
        "content": f"Lucy is ready to chat! (Model: {CHAT_MODEL})",
        "timestamp": datetime.now().isoformat()
    }, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "chat":
                user_message = data.get("message", "").strip()

                if not user_message:
                    continue

                # Echo user message
                await manager.send_message({
                    "type": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                }, websocket)

                # Send thinking state
                await manager.send_message({
                    "type": "thinking",
                    "timestamp": datetime.now().isoformat()
                }, websocket)

                # Get Lucy's response
                reply = lucy.process_message(user_message)

                # Send response
                await manager.send_message({
                    "type": "assistant",
                    "content": reply,
                    "timestamp": datetime.now().isoformat(),
                    "speak": True  # Signal to browser to speak this
                }, websocket)

            elif data.get("type") == "get_idle_thought":
                # Request idle thought
                idle = lucy.get_idle_thought()
                await manager.send_message({
                    "type": "idle",
                    "content": idle,
                    "timestamp": datetime.now().isoformat(),
                    "speak": True
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        lucy.end_conversation()
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        lucy.end_conversation()

def get_voice_interface_html():
    """Complete voice-enabled interface with animated face"""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lucy - Voice Robot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            touch-action: manipulation;
        }

        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }

        /* Lucy's Face */
        .face-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 0 30px 30px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        #face-canvas {
            width: 100%;
            max-width: 300px;
            height: 300px;
            border-radius: 20px;
        }

        .face-status {
            margin-top: 10px;
            font-size: 0.9em;
            color: #667eea;
            font-weight: 500;
        }

        /* Chat Area */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .message {
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            animation: fadeIn 0.3s;
            word-wrap: break-word;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            align-self: flex-end;
            margin-left: auto;
        }

        .assistant-message {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            align-self: flex-start;
            border: 2px solid #667eea;
        }

        .system-message {
            background: rgba(255, 255, 255, 0.8);
            color: #666;
            align-self: center;
            font-size: 0.85em;
            text-align: center;
        }

        /* Controls */
        .controls {
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            display: flex;
            gap: 10px;
            align-items: center;
            border-radius: 30px 30px 0 0;
        }

        .voice-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s;
            flex-shrink: 0;
        }

        #mic-btn {
            background: #667eea;
            color: white;
        }

        #mic-btn:active {
            transform: scale(0.95);
        }

        #mic-btn.listening {
            background: #ff4757;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .text-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }

        .text-input:focus {
            border-color: #667eea;
        }

        .send-btn {
            padding: 15px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
            flex-shrink: 0;
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        /* Status Bar */
        .status-bar {
            background: rgba(102, 126, 234, 0.9);
            color: white;
            padding: 8px;
            text-align: center;
            font-size: 0.85em;
        }

        .status-bar.connected { background: rgba(76, 175, 80, 0.9); }
        .status-bar.error { background: rgba(244, 67, 54, 0.9); }

        /* Responsive */
        @media (max-width: 600px) {
            #face-canvas {
                max-width: 200px;
                height: 200px;
            }

            .message {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Status -->
        <div class="status-bar" id="status">Connecting...</div>

        <!-- Lucy's Face -->
        <div class="face-container">
            <canvas id="face-canvas" width="300" height="300"></canvas>
            <div class="face-status" id="face-status">😊 Ready to chat!</div>
        </div>

        <!-- Chat Messages -->
        <div class="chat-container" id="chat"></div>

        <!-- Controls -->
        <div class="controls">
            <button class="voice-btn" id="mic-btn" title="Hold to speak">🎤</button>
            <input type="text" class="text-input" id="text-input" placeholder="Type or hold mic to speak...">
            <button class="send-btn" id="send-btn">Send</button>
        </div>
    </div>

    <script>
        // ==========================================
        // LUCY'S ANIMATED FACE
        // ==========================================
        const canvas = document.getElementById('face-canvas');
        const ctx = canvas.getContext('2d');

        let faceState = {
            mood: 'happy',
            talking: false,
            listening: false,
            blinking: false,
            blinkTimer: 0,
            eyeX: 0,
            eyeY: 0,
            mouthPhase: 0
        };

        function drawFace() {
            // Clear
            ctx.fillStyle = '#87CEEB';  // Sky blue background
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            // Draw eyes
            drawEye(centerX - 50, centerY - 20);
            drawEye(centerX + 50, centerY - 20);

            // Draw mouth
            drawMouth(centerX, centerY + 50);

            // Update blink
            if (Math.random() < 0.01) {
                faceState.blinking = true;
                faceState.blinkTimer = 5;
            }

            if (faceState.blinkTimer > 0) {
                faceState.blinkTimer--;
                if (faceState.blinkTimer === 0) {
                    faceState.blinking = false;
                }
            }

            // Update mouth animation if talking
            if (faceState.talking) {
                faceState.mouthPhase += 0.3;
            }

            requestAnimationFrame(drawFace);
        }

        function drawEye(x, y) {
            if (faceState.blinking) {
                // Closed eye (line)
                ctx.strokeStyle = '#FF69B4';
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(x - 20, y);
                ctx.lineTo(x + 20, y);
                ctx.stroke();
            } else {
                // Open eye
                ctx.fillStyle = '#FF69B4';  // Hot pink
                ctx.beginPath();
                ctx.ellipse(x, y, 30, faceState.listening ? 40 : 35, 0, 0, Math.PI * 2);
                ctx.fill();

                // Pupil
                ctx.fillStyle = '#6495ED';  // Cornflower blue
                ctx.beginPath();
                ctx.arc(x + faceState.eyeX, y + faceState.eyeY, 15, 0, Math.PI * 2);
                ctx.fill();

                // Sparkle
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(x - 5 + faceState.eyeX, y - 5 + faceState.eyeY, 5, 0, Math.PI * 2);
                ctx.fill();

                // Listening glow
                if (faceState.listening) {
                    ctx.strokeStyle = 'rgba(255, 105, 180, 0.5)';
                    ctx.lineWidth = 8;
                    ctx.beginPath();
                    ctx.ellipse(x, y, 35, 45, 0, 0, Math.PI * 2);
                    ctx.stroke();
                }
            }
        }

        function drawMouth(x, y) {
            ctx.strokeStyle = '#9370DB';  // Medium purple
            ctx.lineWidth = 8;
            ctx.lineCap = 'round';

            if (faceState.talking) {
                // Animated talking mouth
                const openAmount = Math.abs(Math.sin(faceState.mouthPhase));
                const mouthHeight = 20 + openAmount * 20;

                ctx.beginPath();
                ctx.arc(x, y, 40, 0.2, Math.PI - 0.2);
                ctx.stroke();

                // Open mouth
                ctx.fillStyle = '#9370DB';
                ctx.beginPath();
                ctx.ellipse(x, y + 10, 30, mouthHeight, 0, 0, Math.PI * 2);
                ctx.fill();
            } else {
                // Smile
                ctx.beginPath();
                ctx.arc(x, y, 40, 0.2, Math.PI - 0.2);
                ctx.stroke();
            }
        }

        // Start animation
        drawFace();

        // ==========================================
        // WEBSOCKET CONNECTION
        // ==========================================
        let ws = null;
        const status = document.getElementById('status');
        const chat = document.getElementById('chat');
        const faceStatus = document.getElementById('face-status');

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onopen = () => {
                status.textContent = 'Connected';
                status.className = 'status-bar connected';
                faceStatus.textContent = '😊 Ready to chat!';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };

            ws.onclose = () => {
                status.textContent = 'Disconnected. Reconnecting...';
                status.className = 'status-bar error';
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
                    faceState.talking = false;
                    faceStatus.textContent = '😊 Ready!';

                    // Speak response
                    if (data.speak) {
                        speakText(data.content);
                    }
                    break;

                case 'system':
                    msg.classList.add('system-message');
                    msg.textContent = data.content;
                    break;

                case 'thinking':
                    faceState.talking = true;
                    faceStatus.textContent = '🤔 Thinking...';
                    return;

                case 'idle':
                    msg.classList.add('assistant-message');
                    msg.textContent = data.content;
                    if (data.speak) {
                        speakText(data.content);
                    }
                    break;
            }

            chat.appendChild(msg);
            chat.scrollTop = chat.scrollHeight;
        }

        // ==========================================
        // VOICE INPUT (Web Speech API)
        // ==========================================
        let recognition = null;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('text-input').value = transcript;
                sendMessage(transcript);
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                faceState.listening = false;
                faceStatus.textContent = '😅 Try again!';
            };

            recognition.onend = () => {
                document.getElementById('mic-btn').classList.remove('listening');
                faceState.listening = false;
            };
        }

        // Mic button - hold to speak
        const micBtn = document.getElementById('mic-btn');
        let micPressed = false;

        micBtn.addEventListener('mousedown', startListening);
        micBtn.addEventListener('touchstart', startListening);
        micBtn.addEventListener('mouseup', stopListening);
        micBtn.addEventListener('touchend', stopListening);
        micBtn.addEventListener('mouseleave', stopListening);

        function startListening(e) {
            e.preventDefault();
            if (!recognition) {
                alert('Voice input not supported in this browser. Use Chrome on Android or iOS Safari.');
                return;
            }

            micPressed = true;
            micBtn.classList.add('listening');
            faceState.listening = true;
            faceStatus.textContent = '🎤 Listening...';
            recognition.start();
        }

        function stopListening(e) {
            e.preventDefault();
            if (micPressed && recognition) {
                recognition.stop();
                micPressed = false;
            }
        }

        // ==========================================
        // VOICE OUTPUT (Speech Synthesis API)
        // ==========================================
        function speakText(text) {
            // Strip emojis for cleaner speech
            const cleanText = text.replace(/[\u{1F600}-\u{1F64F}]/gu, '')
                                 .replace(/[\u{1F300}-\u{1F5FF}]/gu, '')
                                 .replace(/[\u{1F680}-\u{1F6FF}]/gu, '')
                                 .replace(/[\u{2600}-\u{26FF}]/gu, '');

            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.0;
            utterance.pitch = 1.2;  // Slightly higher pitch for kid-friendly voice
            utterance.volume = 1.0;

            utterance.onstart = () => {
                faceState.talking = true;
                faceStatus.textContent = '🗣️ Speaking...';
            };

            utterance.onend = () => {
                faceState.talking = false;
                faceStatus.textContent = '😊 Ready!';
            };

            window.speechSynthesis.speak(utterance);
        }

        // ==========================================
        // TEXT INPUT
        // ==========================================
        function sendMessage(text = null) {
            const input = document.getElementById('text-input');
            const message = text || input.value.trim();

            if (!message || !ws) return;

            ws.send(JSON.stringify({
                type: 'chat',
                message: message
            }));

            input.value = '';
        }

        document.getElementById('send-btn').addEventListener('click', () => sendMessage());
        document.getElementById('text-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // ==========================================
        // STARTUP
        // ==========================================
        connect();

        // Periodic idle thoughts (optional)
        setInterval(() => {
            if (Math.random() < 0.1 && ws) {  // 10% chance every 30s
                ws.send(JSON.stringify({ type: 'get_idle_thought' }));
            }
        }, 30000);
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("Lucy Voice Web Interface")
    print("="*60)
    print(f"Model: {CHAT_MODEL}")
    print(f"API: {API_BASE}")
    print("\nFeatures:")
    print("  [+] Animated robot face")
    print("  [+] Voice input (hold mic button)")
    print("  [+] Voice output (automatic)")
    print("  [+] Text chat")
    print("  [+] Mobile-friendly")
    print("\n" + "="*60)
    print("\nOpen in browser: http://localhost:8080")
    print("Or from phone: http://YOUR_PC_IP:8080")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(app, host="0.0.0.0", port=8080)
