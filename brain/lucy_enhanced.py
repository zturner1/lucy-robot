#!/usr/bin/env python3
"""
Lucy Enhanced - Curious Robot Companion with Memory
Designed for kids' conversations with short and long-term memory
"""

import sys
import json
import requests
import os
import time
import random
from pathlib import Path
from datetime import datetime, timedelta

# --- CONFIG LOADING ---
def load_config():
    """Load configuration with fallback logic"""
    script_dir = Path(__file__).parent.parent

    config_paths = [
        script_dir / "config" / "config.windows.json",
        Path("D:/lucy-robot/config/config.windows.json"),
    ]

    default_config = {
        "api_base": "http://localhost:11434/v1",
        "chat_model": "qwen2.5:1.5b",
        "data_root": str(script_dir / "data"),
        "memory_path": str(script_dir / "data" / "lucy_memory"),
        "prompt_path": str(script_dir / "config" / "system_prompt_kids.txt")
    }

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                print(f"[Config] Loaded from: {config_path.name}")
                return config, config_path
            except Exception as e:
                continue

    print("[Config] Using defaults")
    return default_config, None

CFG, _ = load_config()

API_BASE = CFG.get("api_base", "http://localhost:11434/v1")
CHAT_MODEL = CFG.get("chat_model", "qwen2.5:1.5b")
DATA_ROOT = Path(CFG.get("data_root", "data"))
MEMORY_PATH = Path(CFG.get("memory_path", DATA_ROOT / "lucy_memory"))

# Ensure directories exist
MEMORY_PATH.mkdir(parents=True, exist_ok=True)
(DATA_ROOT / "conversations").mkdir(parents=True, exist_ok=True)

# Load System Prompt
SYSTEM_PROMPT = ""
prompt_path = Path(CFG.get("prompt_path", "config/system_prompt_kids.txt"))
if prompt_path.exists():
    SYSTEM_PROMPT = prompt_path.read_text()
    print(f"[Prompt] Loaded kid-friendly prompt")
else:
    SYSTEM_PROMPT = "You are Lucy, a curious robot who loves learning from kids!"

# ==============================
# MEMORY SYSTEM
# ==============================

class LucyMemory:
    """Manages Lucy's short and long-term memory"""

    def __init__(self, memory_path: Path):
        self.memory_path = memory_path
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # Short-term: Current conversation context
        self.conversation_history = []
        self.conversation_start = datetime.now()

        # Long-term: Persistent facts about kids and world
        self.facts_file = memory_path / "learned_facts.json"
        self.facts = self._load_facts()

        # Conversation logs
        self.logs_dir = memory_path / "conversations"
        self.logs_dir.mkdir(exist_ok=True)

    def _load_facts(self):
        """Load learned facts from disk"""
        if self.facts_file.exists():
            try:
                return json.loads(self.facts_file.read_text())
            except:
                return {"kids": {}, "world": {}, "preferences": {}}
        return {"kids": {}, "world": {}, "preferences": {}}

    def _save_facts(self):
        """Save learned facts to disk"""
        try:
            self.facts_file.write_text(json.dumps(self.facts, indent=2))
        except Exception as e:
            print(f"[Memory] Error saving facts: {e}")

    def remember_fact(self, category: str, key: str, value: str):
        """Store a long-term fact"""
        if category not in self.facts:
            self.facts[category] = {}

        self.facts[category][key] = {
            "value": value,
            "learned_at": datetime.now().isoformat(),
            "mentions": self.facts[category].get(key, {}).get("mentions", 0) + 1
        }
        self._save_facts()
        print(f"[Memory] Remembered: {category}/{key} = {value}")

    def recall_facts(self, category: str = None):
        """Retrieve learned facts"""
        if category:
            return self.facts.get(category, {})
        return self.facts

    def get_memory_summary(self):
        """Get a summary of what Lucy knows"""
        summary = []
        for category, facts in self.facts.items():
            if facts:
                summary.append(f"{category}: {len(facts)} things")
        return ", ".join(summary) if summary else "Nothing yet"

    def add_to_conversation(self, role: str, content: str):
        """Add message to short-term conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_context(self, max_messages: int = 10):
        """Get recent conversation for context"""
        return self.conversation_history[-max_messages:]

    def save_conversation_log(self):
        """Save conversation to permanent log"""
        if not self.conversation_history:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"conversation_{timestamp}.json"

        log_data = {
            "started_at": self.conversation_start.isoformat(),
            "ended_at": datetime.now().isoformat(),
            "messages": self.conversation_history,
            "facts_learned": len([m for m in self.conversation_history if "remember" in m.get("content", "").lower()])
        }

        log_file.write_text(json.dumps(log_data, indent=2))
        print(f"[Memory] Conversation saved to {log_file.name}")

# ==============================
# LUCY BRAIN
# ==============================

class LucyBrain:
    """Lucy's conversational brain with memory and curiosity"""

    def __init__(self):
        self.memory = LucyMemory(MEMORY_PATH)
        self.last_interaction = time.time()
        self.idle_thoughts = [
            "I wonder what clouds taste like... do you think they're sweet? ☁️",
            "Do you have a favorite animal? I want to learn about animals!",
            "What's the coolest thing you saw today? 🌟",
            "I was thinking about stars... have you ever seen a shooting star?",
            "Do you like to read books? What's your favorite story?",
            "I'm curious... what makes you laugh the most? 😄",
            "If you could have any superpower, what would it be?",
            "Do you have any pets? I'd love to hear about them! 🐕",
        ]

        # Initialize conversation with memory context
        self.messages = self._build_initial_context()

    def _build_initial_context(self):
        """Build initial context with system prompt and memories"""
        context = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add memory summary to give Lucy context
        memory_summary = self.memory.get_memory_summary()
        if memory_summary != "Nothing yet":
            context.append({
                "role": "system",
                "content": f"[Memory] You remember: {memory_summary}"
            })

        return context

    def call_llm(self, messages):
        """Call the LLM with error handling"""
        try:
            resp = requests.post(f"{API_BASE}/chat/completions", json={
                "model": CHAT_MODEL,
                "messages": messages,
                "temperature": 0.8,  # Higher for more creativity
                "max_tokens": 150
            }, timeout=30)

            if resp.status_code != 200:
                return None

            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM] Error: {e}")
            return None

    def process_message(self, user_input: str):
        """Process user input and generate response"""
        self.last_interaction = time.time()

        # Add to short-term memory
        self.memory.add_to_conversation("user", user_input)
        self.messages.append({"role": "user", "content": user_input})

        # Get Lucy's response
        reply = self.call_llm(self.messages)

        if reply:
            # Add to short-term memory
            self.memory.add_to_conversation("assistant", reply)
            self.messages.append({"role": "assistant", "content": reply})

            # Check if Lucy learned something (simple keyword detection)
            if any(keyword in user_input.lower() for keyword in ["my favorite", "i like", "i love", "i have"]):
                # Extract potential facts (simplified)
                self._try_extract_fact(user_input, reply)

            # Trim conversation history to prevent token overflow
            if len(self.messages) > 20:
                # Keep system message and last 18 messages
                self.messages = [self.messages[0]] + self.messages[-18:]

            return reply
        else:
            return "Oops, I'm having trouble thinking right now. Can you say that again? 😅"

    def _try_extract_fact(self, user_input: str, lucy_reply: str):
        """Try to extract and remember facts from conversation"""
        # Simple fact extraction (can be enhanced)
        lower_input = user_input.lower()

        if "my name is" in lower_input or "i'm " in lower_input:
            # Try to extract name
            for phrase in ["my name is ", "i'm ", "im "]:
                if phrase in lower_input:
                    parts = lower_input.split(phrase)
                    if len(parts) > 1:
                        name = parts[1].split()[0].strip(".,!?").title()
                        self.memory.remember_fact("kids", "current_child_name", name)

        elif "favorite" in lower_input:
            # Extract favorite things
            if "color" in lower_input:
                self.memory.remember_fact("preferences", "favorite_color", user_input)
            elif "animal" in lower_input:
                self.memory.remember_fact("preferences", "favorite_animal", user_input)

    def get_idle_thought(self):
        """Generate an idle thought when conversation pauses"""
        return random.choice(self.idle_thoughts)

    def should_speak_up(self):
        """Determine if Lucy should say something during idle time"""
        idle_duration = time.time() - self.last_interaction

        # After 30 seconds of silence, occasionally speak up
        if idle_duration > 30:
            return random.random() < 0.3  # 30% chance

        return False

    def end_conversation(self):
        """Clean up and save conversation"""
        self.memory.save_conversation_log()

        print("\n" + "="*60)
        print(f"[Session] Conversation lasted {len(self.memory.conversation_history)} messages")
        print(f"[Memory] Total facts remembered: {self.memory.get_memory_summary()}")
        print("="*60)

# ==============================
# CONVERSATION TEST LOOP
# ==============================

def conversation_test(iterations: int = None):
    """Interactive conversation test with Lucy"""
    print("\n" + "="*60)
    print("Lucy Enhanced - Curious Robot Companion")
    print("="*60)
    print(f"Model: {CHAT_MODEL}")
    print(f"Memory: {MEMORY_PATH}")
    print("\nLucy is ready to chat! She'll remember what you tell her.")
    print("Commands: 'exit' to quit, 'memory' to see what Lucy remembers")
    print("          'idle' to trigger idle behavior")
    print("="*60 + "\n")

    lucy = LucyBrain()

    # Initial greeting
    greeting = lucy.call_llm(lucy.messages + [
        {"role": "user", "content": "Say hello and introduce yourself briefly!"}
    ])
    print(f"Lucy: {greeting}\n")

    iteration_count = 0
    max_iterations = iterations if iterations else float('inf')

    while iteration_count < max_iterations:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                farewell = lucy.call_llm(lucy.messages + [
                    {"role": "user", "content": "Say goodbye briefly!"}
                ])
                print(f"Lucy: {farewell}\n")
                break

            elif user_input.lower() == "memory":
                print(f"\n[Lucy's Memory]")
                print(f"  Facts: {lucy.memory.get_memory_summary()}")
                print(f"  Conversation: {len(lucy.memory.conversation_history)} messages")
                print(f"  Saved logs: {len(list(lucy.memory.logs_dir.glob('*.json')))}\n")
                continue

            elif user_input.lower() == "idle":
                idle_thought = lucy.get_idle_thought()
                print(f"Lucy: {idle_thought}\n")
                continue

            # Process message
            reply = lucy.process_message(user_input)
            print(f"Lucy: {reply}\n")

            iteration_count += 1

            # Occasionally check idle behavior
            if lucy.should_speak_up():
                time.sleep(1)
                idle_thought = lucy.get_idle_thought()
                print(f"Lucy: {idle_thought}\n")

        except KeyboardInterrupt:
            print("\n\nEnding conversation...")
            break
        except Exception as e:
            print(f"\n[Error] {e}\n")
            continue

    # End conversation
    lucy.end_conversation()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, help="Max conversation turns")
    args = parser.parse_args()

    conversation_test(args.iterations)
