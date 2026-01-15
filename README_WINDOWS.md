# Lucy Robot - Windows Setup Guide

## Quick Start

1. **Install Ollama**
   ```
   Download from: https://ollama.com/download
   ```

2. **Pull a model**
   ```bash
   ollama pull qwen2.5:1.5b
   ```
   Or for better quality (larger):
   ```bash
   ollama pull qwen3:4b
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run Lucy Web Interface**
   ```bash
   run_lucy.bat
   ```
   Or manually:
   ```bash
   python web/lucy_web.py
   ```

5. **Open your browser**
   ```
   http://localhost:8080
   ```

## Configuration

Edit `config/config.windows.json` to customize:
- `chat_model`: Which Ollama model to use
- `api_base`: Ollama API endpoint
- `prompt_path`: System prompt file location

## Features

- **Web Interface**: Cross-platform browser-based UI
- **Real-time Chat**: WebSocket-based instant messaging
- **Tool Use**: Lucy can use tools to interact with the system
- **Kid-Friendly**: Designed for children's conversations
- **Customizable**: Adjust personality via system prompt

## Available Tools

- `system_info` - Get system information
- `check_ollama` - Verify Ollama status
- `list_files` - Browse directories
- `write_note` - Save notes to memory
- `read_notes` - Read previous notes

## Troubleshooting

### Ollama not found
Make sure Ollama is running:
```bash
ollama serve
```

### Port 8080 in use
Edit `web/lucy_web.py` and change the port number at the bottom.

### Model not found
List available models:
```bash
ollama list
```
Then update `config/config.windows.json` with an available model name.

## Development

### Console Mode (no web interface)
```bash
python brain/lucy_unified_windows.py
```

### Test Mode
```bash
python brain/lucy_unified_windows.py --test
```

## Kid-Friendly Configuration

Lucy is designed as a conversational companion for children. To customize:

1. Edit `config/system_prompt.txt` to adjust personality
2. Use smaller, faster models like `qwen2.5:1.5b` for quick responses
3. For voice interaction (Raspberry Pi), see the original `lucy_voice.py`

## Next Steps

- Set up voice interaction (requires microphone + speakers)
- Add custom tools for home automation
- Create kid-specific conversation topics
- Deploy to Raspberry Pi for physical robot

## Support

This is a personal project for creating a kid-friendly AI companion.
See the main README.md for full project details and Raspberry Pi setup.
