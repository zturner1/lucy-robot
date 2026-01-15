# Lucy Robot - Voice-Interactive AI Companion

Lucy is a friendly AI companion designed for children, featuring a customizable animated face and voice interaction capabilities. Built for Raspberry Pi with touchscreen display and USB microphone support.

## Features

- **Voice Interaction**: Natural conversation using speech recognition and text-to-speech
- **Animated Face**: Expressive face with multiple themes and animations
- **Child-Friendly**: Specially designed for answering children's questions about animals, computers, and nature
- **Real-time Animations**: Eyes that glow when listening, mouth that moves when talking
- **Multiple Face Themes**: Retro, Glitch, RPG, and custom Felicity theme
- **Touchscreen Support**: Interactive touch interface

## Project Structure

```
lucy-robot/
├── brain/               # AI brain and voice interaction
│   ├── lucy_unified.py  # Main brain system with LLM integration
│   ├── lucy_voice.py    # Voice recognition and speech synthesis
│   └── face_updater.py  # Face state communication module
├── face/                # Visual interface
│   ├── main.py          # Main face display (Felicity theme)
│   └── themes/          # Alternative face themes
│       ├── felicity.py  # Custom child-friendly theme
│       ├── retro.py     # Retro terminal aesthetic
│       ├── glitch.py    # Cyberpunk glitch theme
│       └── rpg.py       # Game Boy-style pixel art
├── config/              # Configuration files
│   ├── config.json      # Brain configuration
│   └── system_prompt.txt # AI personality and behavior
├── docs/                # Documentation
└── requirements.txt     # Python dependencies
```

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- Touchscreen display (800x480 recommended)
- USB microphone (or USB headset with microphone)
- Speakers (USB headset or HDMI audio output)
- Internet connection (for speech recognition)

## Software Requirements

- Python 3.13+
- Pygame 2.6+
- SpeechRecognition 3.14+
- espeak (text-to-speech)
- Ollama (for local LLM)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/lucy-robot.git
cd lucy-robot
```

2. **Install system dependencies:**
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio espeak
```

3. **Create virtual environment and install Python packages:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Set up Ollama (for AI brain):**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull qwen2.5-coder:1.5b
```

5. **Configure Lucy:**
Edit `config/config.json` to set your preferences:
- API endpoint
- Model selection
- Voice settings

## Usage

### Start Lucy with Auto-Conversation Mode:
```bash
DISPLAY=:0 python3 face/main.py
```

Lucy will automatically start listening for voice input. Just start talking!

### Start Individual Components:

**Face only:**
```bash
DISPLAY=:0 python3 face/main.py
```

**Voice interaction only:**
```bash
python3 brain/lucy_voice.py
```

**Brain only (text interface):**
```bash
python3 brain/lucy_unified.py
```

## Face Themes

Switch between different visual themes by copying theme files:

```bash
# Felicity theme (child-friendly, colorful)
cp face/themes/felicity.py face/main.py

# Retro theme (terminal-style)
cp face/themes/retro.py face/main.py

# Glitch theme (cyberpunk)
cp face/themes/glitch.py face/main.py

# RPG theme (pixel art)
cp face/themes/rpg.py face/main.py
```

## Customization

### Create Your Own Face Theme

Face themes are Python files that use Pygame. See `face/themes/felicity.py` for a complete example.

Key components:
- `draw_eye()` - Eye rendering and animations
- `draw_smile()` - Mouth rendering
- `draw_clouds()` or background elements
- State management for talking/listening

### Customize AI Personality

Edit `config/system_prompt.txt` to change Lucy's personality, knowledge focus, and response style.

### Add New Features

The modular design makes it easy to extend:
- Add new face expressions
- Integrate additional sensors
- Connect to smart home systems
- Add new conversation capabilities

## API for HTTP-Based Robots

The face state system uses a simple socket-based protocol on port 5555:

```python
import socket
import json

# Update face state
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5555))
sock.send(json.dumps({
    'talking': True,  # or False
    'listening': False  # or False
}).encode())
sock.close()
```

This makes it easy to control Lucy's face from web applications or other services.

## Troubleshooting

**No audio input detected:**
- Check USB microphone is connected: `arecord -l`
- Test microphone: `arecord -D plughw:CARD,DEV -d 5 test.wav`

**Face not displaying:**
- Ensure DISPLAY environment variable is set: `echo $DISPLAY`
- Check X11 permissions

**Voice recognition not working:**
- Verify internet connection (Google Speech Recognition requires internet)
- Check microphone levels: `alsamixer`

**LLM not responding:**
- Ensure Ollama is running: `systemctl status ollama`
- Check model is downloaded: `ollama list`

## Contributing

Contributions are welcome! This project is designed to be educational and fun. Feel free to:
- Add new face themes
- Improve voice recognition
- Add new conversation topics
- Create additional robot personalities

## License

MIT License - Feel free to use this project to create robot friends for your kids!

## Credits

Created with love for Felicity and all kids who want to learn about the world through conversation with friendly AI companions.

Built using:
- Pygame for graphics
- SpeechRecognition for voice input
- espeak for text-to-speech
- Ollama for local LLM inference

## Future Ideas

- Multiple character personalities
- Web interface for remote interaction
- Smart home integration
- Educational games and quizzes
- Story-telling mode
- Multi-language support
- Raspberry Pi auto-start on boot
