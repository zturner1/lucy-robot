#!/usr/bin/env python3
"""
Quick test script for Lucy on Windows/ZPC
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("="*60)
    print("Lucy Robot - Quick Test Script")
    print("="*60)
    print()

    # Check if Ollama is running
    print("1. Checking Ollama...")
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print(f"   ✅ Ollama is running ({len(models)} models available)")
            for model in models:
                print(f"      - {model['name']}")
        else:
            print(f"   ⚠️ Ollama responded with status {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Ollama not available: {e}")
        print("   Start Ollama with: ollama serve")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    print()
    print("2. Choose test mode:")
    print("   [1] Test mode (quick capability check)")
    print("   [2] Interactive chat")
    print("   [3] Run original brain (requires greenhouse setup)")
    print()

    choice = input("Enter choice (1-3): ").strip()

    brain_dir = Path(__file__).parent / "brain"

    if choice == "1":
        print("\nRunning test mode...")
        subprocess.run([sys.executable, str(brain_dir / "lucy_unified_windows.py"), "--test"])
    elif choice == "2":
        print("\nStarting interactive chat...")
        print("(Type 'exit' or 'quit' to end)\n")
        subprocess.run([sys.executable, str(brain_dir / "lucy_unified_windows.py")])
    elif choice == "3":
        print("\nRunning original brain...")
        subprocess.run([sys.executable, str(brain_dir / "lucy_unified.py")])
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
