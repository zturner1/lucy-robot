# Lucy Voice Web Interface Setup Guide

## Quick Start

### 1. Start the Server (on your PC)

```bash
cd D:/lucy-robot
run_lucy_voice_web.bat
```

Or manually:
```bash
python web/lucy_voice_web.py
```

The server will start on port **8080** and display your PC's IP address.

### 2. Connect from Phone

**On PC:**
- Open: `http://localhost:8080`

**On Phone (same WiFi network):**
- Open Chrome or Safari
- Go to: `http://YOUR_PC_IP:8080`
- Example: `http://192.168.0.100:8080`

### 3. Grant Permissions

First time:
1. Browser will ask for **microphone permission** - Click "Allow"
2. That's it! You're ready to talk to Lucy

## Features

### 🎙️ Voice Mode (Default)
- **Hold** the microphone button to speak
- Lucy listens while you hold
- Release when done speaking
- Lucy responds with **voice and text**

### ⌨️ Text Mode
- Click "Text" toggle at top
- Type messages
- Lucy responds with text only

### 🤖 Animated Face
- Eyes blink naturally
- Eyes glow when listening
- Mouth animates when speaking
- Curious expressions

### 💾 Memory System
- Lucy remembers conversations
- Recalls names, favorites, pets
- Builds knowledge over time
- All saved to `data/lucy_memory/`

## Browser Compatibility

### ✅ Supported (Voice + Text)
- **Android**: Chrome, Edge
- **iOS**: Safari
- **Desktop**: Chrome, Edge, Safari, Firefox (text only)

### ⚠️ Voice Requirements
- **Microphone input**: Web Speech API (Chrome/Safari)
- **Voice output**: Speech Synthesis API (all modern browsers)
- **Must use HTTPS** for voice (or localhost)

## Network Setup

### Find Your PC's IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter

**Example:**
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.0.100
```

### Firewall Settings

If phones can't connect, allow port 8080:

**Windows Firewall:**
1. Windows Security → Firewall & network protection
2. Advanced settings → Inbound Rules → New Rule
3. Port → TCP → Specific local port: 8080
4. Allow the connection → All profiles
5. Name: "Lucy Robot"

## Tips for Kids

### Voice Mode
- Speak clearly after holding the mic
- Wait for the "listening" animation
- Say complete thoughts (Lucy listens for pauses)
- If Lucy doesn't hear, try again!

### What to Say
- "Hi Lucy! My name is..."
- "I have a dog named..."
- "My favorite color is..."
- "Tell me about dolphins!"
- "What do you want to know?"

### Lucy Remembers!
- She'll ask about things you mentioned before
- "How's your dog Buddy doing?"
- "You said you like purple!"
- Conversations build over time

## Troubleshooting

### Voice Not Working

**Check microphone permission:**
1. Browser address bar → 🔒 or ℹ️ icon
2. Permissions → Microphone → Allow

**Try different browser:**
- Android: Chrome works best
- iOS: Safari works best
- Desktop: Chrome or Edge

**Check microphone:**
- Test in another app (camera, voice recorder)
- Make sure it's not muted
- Try restarting browser

### Can't Connect from Phone

**Check WiFi:**
- Phone and PC on same network
- Not on guest network
- Check IP address is correct

**Check firewall:**
- Port 8080 allowed (see above)
- Temporarily disable to test

**Check server:**
- Server running on PC (window should be open)
- No errors in server window

### Lucy Not Responding

**Check Ollama:**
```bash
ollama list
```
Should show `qwen2.5:1.5b` or similar

**Restart Ollama:**
```bash
ollama serve
```

**Check model:**
Edit `config/config.windows.json`:
```json
{
    "chat_model": "qwen2.5:1.5b"
}
```

### Face Not Animating

**Refresh browser:**
- Hard refresh: Ctrl+F5 (PC) or Cmd+Shift+R (Mac)

**Check browser console:**
- F12 → Console tab
- Look for errors

**Try different browser:**
- Canvas animations work in all modern browsers

## Advanced

### Change Port

Edit `web/lucy_voice_web.py` (bottom):
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change 8080
```

### Adjust Voice

In browser console (F12):
```javascript
// Change voice speed
speechSynthesis.rate = 1.2;

// Change pitch
speechSynthesis.pitch = 1.0;
```

### Custom Face Colors

Edit `web/lucy_voice_toggle.html`:
```javascript
ctx.fillStyle = '#87CEEB';  // Sky blue background
ctx.fillStyle = '#FF69B4';  // Hot pink eyes
ctx.fillStyle = '#6495ED';  // Cornflower blue pupils
ctx.strokeStyle = '#9370DB'; // Purple mouth
```

### Enable HTTPS (for voice on non-localhost)

1. Generate self-signed certificate:
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

2. Update server:
```python
uvicorn.run(app, host="0.0.0.0", port=8080,
            ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

3. Access via: `https://YOUR_IP:8080`
4. Accept browser security warning (self-signed cert)

## Multiple Kids

Each phone connection gets its own Lucy instance with separate memory.

To share memory across devices:
- Use same phone
- Or manually merge `data/lucy_memory/learned_facts.json`

## Privacy

- All conversations stored locally on your PC
- No data sent to external servers (except speech recognition to Google)
- Speech uses Google's Web Speech API (only during voice input)
- Text-to-speech happens entirely in browser
- Memory files: `D:/lucy-robot/data/lucy_memory/`

## Files & Folders

```
D:/lucy-robot/
├── web/
│   ├── lucy_voice_web.py        # Server
│   └── lucy_voice_toggle.html   # Interface
├── data/
│   └── lucy_memory/
│       ├── learned_facts.json   # What Lucy knows
│       └── conversations/       # Chat logs
├── config/
│   ├── config.windows.json      # Server config
│   └── system_prompt_kids.txt   # Lucy's personality
└── run_lucy_voice_web.bat       # Quick launcher
```

## Next Steps

1. **Start server**: `run_lucy_voice_web.bat`
2. **Test on PC**: http://localhost:8080
3. **Connect phone**: http://YOUR_PC_IP:8080
4. **Grant mic permission**
5. **Start talking!**

Lucy is ready to learn about your kids and the world! 🤖✨
