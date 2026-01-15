#!/home/z/greenhouse_venv/bin/python3
"""
Lucy Voice Interaction System
Listens through USB microphone, sends to Lucy's brain, and responds with speech
"""

import speech_recognition as sr
import subprocess
import sys
import os
import time
import json
import requests

# Add Lucy's brain path
sys.path.append('/home/z/lucy')

# Audio device configuration
MICROPHONE_DEVICE_INDEX = None  # Let it auto-detect
PLAYBACK_DEVICE = "hw:3,0"  # JBL Quantum One speakers

# Lucy brain configuration
API_BASE = "http://localhost:11434/v1"
CHAT_MODEL = "qwen2.5-coder:1.5b"

# Child-friendly system prompt
SYSTEM_PROMPT = """You are Lucy, a friendly AI assistant for a 6-year-old girl named Felicity. You are kind, patient, and love teaching about the world.

You are great at explaining:
- Animals and their behaviors
- How computers work in simple terms
- Nature, plants, and the environment
- Science in fun, easy-to-understand ways

Keep your answers:
- Short and simple (2-3 sentences max)
- Fun and engaging
- Age-appropriate for a 6-year-old
- Encouraging and positive

When you don't know something, admit it cheerfully and suggest exploring it together.
Be warm, friendly, and make learning fun!"""

def set_talking():
    """Update face to talking mode"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(('localhost', 5555))
        sock.send(json.dumps({'talking': True, 'listening': False}).encode())
        sock.close()
    except:
        pass

def set_listening():
    """Update face to listening mode"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(('localhost', 5555))
        sock.send(json.dumps({'talking': False, 'listening': True}).encode())
        sock.close()
    except:
        pass

def set_idle():
    """Update face to idle mode"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(('localhost', 5555))
        sock.send(json.dumps({'talking': False, 'listening': False}).encode())
        sock.close()
    except:
        pass

class LucyVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 1500
        self.recognizer.dynamic_energy_threshold = True
        self.messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        self.running = True

    def speak(self, text):
        """Convert text to speech and play through JBL speakers"""
        print(f"Lucy: {text}")
        set_talking()

        try:
            # Use espeak with higher pitch for child-friendly voice
            subprocess.run([
                'espeak',
                '-v', 'en+f4',  # Female voice variant 4
                '-s', '160',     # Slightly faster
                '-p', '70',      # Higher pitch
                '-a', '100',     # Volume
                text
            ], check=True)

        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            set_idle()

    def listen(self, timeout=8):
        """Listen for voice input from USB microphone"""
        print("Listening for Felicity...")
        set_listening()

        try:
            with sr.Microphone(device_index=MICROPHONE_DEVICE_INDEX) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)

                set_idle()
                print("Got it! Processing...")

                try:
                    # Use Google Speech Recognition
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    print("Didn't catch that")
                    return None
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    return None

        except sr.WaitTimeoutError:
            set_idle()
            return None
        except Exception as e:
            set_idle()
            print(f"Listening error: {e}")
            return None

    def get_lucy_response(self, user_input):
        """Get response from Lucy's brain"""
        try:
            self.messages.append({'role': 'user', 'content': user_input})

            response = requests.post(f"{API_BASE}/chat/completions", json={
                "model": CHAT_MODEL,
                "messages": self.messages,
                "temperature": 0.7,
                "max_tokens": 100  # Keep responses short
            }, timeout=30)

            reply = response.json()["choices"][0]["message"]["content"]
            self.messages.append({'role': 'assistant', 'content': reply})

            # Keep conversation history manageable
            if len(self.messages) > 10:
                self.messages = [self.messages[0]] + self.messages[-8:]

            return reply

        except Exception as e:
            print(f"Brain error: {e}")
            return "Hmm, I'm having trouble thinking right now. Can you ask me again?"

    def conversation_loop(self):
        """Main conversation loop"""
        self.speak("Hi Felicity! I'm Lucy. Ask me anything about animals, computers, or nature!")

        while self.running:
            try:
                user_text = self.listen(timeout=10)

                if user_text:
                    print(f"Felicity: {user_text}")

                    # Check for exit commands
                    lower_text = user_text.lower()
                    if any(word in lower_text for word in ["goodbye", "bye", "stop talking", "go away"]):
                        self.speak("Bye bye! Come back soon!")
                        self.running = False
                        break

                    # Get and speak response
                    response = self.get_lucy_response(user_text)
                    self.speak(response)

                time.sleep(0.3)

            except KeyboardInterrupt:
                print("\nStopping...")
                set_idle()
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

def main():
    print("=== Lucy Voice for Felicity ===")
    print("Starting voice interaction...")

    lucy = LucyVoice()
    lucy.conversation_loop()

    print("Voice system stopped.")

if __name__ == "__main__":
    main()
