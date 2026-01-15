#!/usr/bin/env python3
"""
Automated conversation tester for Lucy
Simulates kid conversations to test memory and curiosity
"""

import sys
import time
from pathlib import Path

# Add brain to path
sys.path.insert(0, str(Path(__file__).parent / "brain"))

from lucy_enhanced import LucyBrain

# Sample kid conversations to test Lucy
SAMPLE_CONVERSATIONS = [
    {
        "name": "First Meeting - Felicity",
        "exchanges": [
            "Hi! My name is Felicity",
            "I'm 6 years old",
            "My favorite animal is a dolphin",
            "I like the color purple",
            "I have a dog named Buddy",
            "What do you like to do?",
            "Do you have friends?",
            "Bye!"
        ]
    },
    {
        "name": "Second Chat - Felicity Returns",
        "exchanges": [
            "Hi Lucy! It's me again",
            "Yes, it's Felicity!",
            "Buddy is good! He learned a new trick",
            "He can roll over now",
            "I went to the park today",
            "I saw real dolphins at the aquarium last week!",
            "They were so cool!",
            "Do you remember my favorite color?",
            "Goodbye Lucy!"
        ]
    },
    {
        "name": "Topic Exploration - Space",
        "exchanges": [
            "Hi Lucy!",
            "I learned about space at school today",
            "Did you know there are billions of stars?",
            "My teacher said some stars are bigger than the sun",
            "What do you think about space?",
            "Do you wonder what's out there?",
            "I want to be an astronaut when I grow up",
            "See you later!"
        ]
    },
    {
        "name": "Quiet Day - Testing Idle",
        "exchanges": [
            "Hi",
            "[pause]",
            "I'm just thinking",
            "[pause]",
            "Nothing much",
            "[pause]",
            "okay bye"
        ]
    },
    {
        "name": "Learning Session - Teaching Lucy",
        "exchanges": [
            "Hey Lucy, I want to teach you something",
            "Butterflies come from caterpillars!",
            "First they make a cocoon",
            "Then they transform inside",
            "And then they come out with wings!",
            "It's called metamorphosis",
            "Have you heard of that before?",
            "Thanks for listening! Bye!"
        ]
    }
]

def run_automated_conversation(conversation, lucy, delay=1.5):
    """Run a simulated conversation with delays"""
    print("\n" + "="*60)
    print(f"Test: {conversation['name']}")
    print("="*60 + "\n")

    for i, user_msg in enumerate(conversation['exchanges'], 1):
        # Handle pause commands
        if user_msg == "[pause]":
            print(f"[Simulating 5 second pause...]")
            time.sleep(5)

            # Check if Lucy wants to speak during idle
            if lucy.should_speak_up():
                idle_thought = lucy.get_idle_thought()
                print(f"Lucy: {idle_thought}\n")
            else:
                print("[Lucy waits comfortably]\n")
            continue

        # Send message
        print(f"Child ({i}): {user_msg}")

        if user_msg.lower() in ["bye", "bye!", "goodbye", "goodbye!"]:
            farewell = lucy.call_llm(lucy.messages + [
                {"role": "user", "content": "Say goodbye briefly!"}
            ])
            print(f"Lucy: {farewell}\n")
            break

        # Get Lucy's response
        reply = lucy.process_message(user_msg)
        print(f"Lucy: {reply}\n")

        # Natural delay between messages
        time.sleep(delay)

def run_all_tests():
    """Run all automated conversation tests"""
    print("\n" + "="*70)
    print("LUCY CONVERSATION TEST SUITE")
    print("="*70)
    print(f"Running {len(SAMPLE_CONVERSATIONS)} test conversations")
    print("Testing: Memory, Curiosity, Idle Behavior, Question Asking")
    print("="*70)

    # Create fresh Lucy instance
    lucy = LucyBrain()

    # Initial greeting
    print("\n[Initializing Lucy...]")
    greeting = lucy.call_llm(lucy.messages + [
        {"role": "user", "content": "Say hello and introduce yourself in one sentence!"}
    ])
    print(f"Lucy: {greeting}\n")

    # Run each conversation
    for i, conversation in enumerate(SAMPLE_CONVERSATIONS, 1):
        print(f"\n[Test {i}/{len(SAMPLE_CONVERSATIONS)}]")
        run_automated_conversation(conversation, lucy, delay=1.0)

        # Save state between conversations
        lucy.memory.save_conversation_log()

        # Brief pause between conversations
        if i < len(SAMPLE_CONVERSATIONS):
            print("\n[Waiting 3 seconds before next conversation...]\n")
            time.sleep(3)

    # Final summary
    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)
    lucy.end_conversation()

    print("\n[Results]")
    print(f"  Total messages: {len(lucy.memory.conversation_history)}")
    print(f"  Facts learned: {lucy.memory.get_memory_summary()}")
    print(f"  Conversation logs saved: {len(list(lucy.memory.logs_dir.glob('*.json')))}")

    # Show what Lucy learned
    print("\n[Lucy's Memory Bank]")
    for category, facts in lucy.memory.recall_facts().items():
        if facts:
            print(f"  {category.upper()}:")
            for key, data in facts.items():
                print(f"    - {key}: {data.get('value', 'N/A')[:50]}")

    print("\n" + "="*70)

def interactive_mode():
    """Run interactive conversation with Lucy"""
    lucy = LucyBrain()

    print("\n" + "="*60)
    print("Interactive Mode - Talk with Lucy")
    print("="*60)
    print("Commands:")
    print("  'exit' - End conversation")
    print("  'memory' - View Lucy's memory")
    print("  'idle' - Trigger idle behavior")
    print("  'facts' - Show learned facts")
    print("="*60 + "\n")

    # Greeting
    greeting = lucy.call_llm(lucy.messages + [
        {"role": "user", "content": "Greet the user warmly!"}
    ])
    print(f"Lucy: {greeting}\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                farewell = lucy.call_llm(lucy.messages + [
                    {"role": "user", "content": "Say goodbye warmly!"}
                ])
                print(f"Lucy: {farewell}\n")
                break

            elif user_input.lower() == "memory":
                print(f"\n[Memory Status]")
                print(f"  Messages: {len(lucy.memory.conversation_history)}")
                print(f"  Facts: {lucy.memory.get_memory_summary()}")
                print()
                continue

            elif user_input.lower() == "facts":
                print(f"\n[Learned Facts]")
                for category, facts in lucy.memory.recall_facts().items():
                    if facts:
                        print(f"  {category}:")
                        for key, data in facts.items():
                            print(f"    {key}: {data.get('value', '')[:60]}")
                print()
                continue

            elif user_input.lower() == "idle":
                idle = lucy.get_idle_thought()
                print(f"Lucy: {idle}\n")
                continue

            # Regular conversation
            reply = lucy.process_message(user_input)
            print(f"Lucy: {reply}\n")

        except KeyboardInterrupt:
            print("\n")
            break

    lucy.end_conversation()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Lucy's conversation abilities")
    parser.add_argument("--auto", action="store_true", help="Run automated test suite")
    parser.add_argument("--interactive", action="store_true", help="Interactive conversation")

    args = parser.parse_args()

    if args.auto:
        run_all_tests()
    elif args.interactive:
        interactive_mode()
    else:
        # Default: show menu
        print("\nLucy Conversation Tester")
        print("="*40)
        print("1. Run automated test suite")
        print("2. Interactive conversation")
        print("="*40)
        choice = input("\nChoice (1 or 2): ").strip()

        if choice == "1":
            run_all_tests()
        elif choice == "2":
            interactive_mode()
        else:
            print("Invalid choice")
