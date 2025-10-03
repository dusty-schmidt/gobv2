#!/usr/bin/env python3
"""
GOB (Grid Overwatch Bridge) - Communal Intelligence System
CLI entry point to select and run different chatbots/agents
"""

import sys
import os
from pathlib import Path

def main():
    print("🤖 GOB - Communal Intelligence System")
    print("=" * 50)

    # Available chatbots/agents
    options = {
        "1": {
            "name": "Mini v3.0",
            "description": "Enhanced chatbot with communal brain",
            "path": "mini",
            "command": "main.py"
        },
        "2": {
            "name": "Nano v1.0",
            "description": "Simple chatbot for testing",
            "path": "nano",
            "command": "main.py"
        }
    }

    print("Available Chatbots:")
    for key, option in options.items():
        print(f"  {key}. {option['name']} - {option['description']}")

    print("\n  0. Exit")
    print()

    while True:
        try:
            choice = input("Select chatbot to run (0-2): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                sys.exit(0)

            if choice in options:
                selected = options[choice]
                print(f"\n🚀 Starting {selected['name']}...")
                print(f"   Description: {selected['description']}")
                print()
        
                # Change to the chatbot directory and run it
                chatbot_path = Path(__file__).parent / selected['path']
                print(f"   Path: {chatbot_path}")
        
                if chatbot_path.exists():
                    os.chdir(chatbot_path)
                    print(f"   Changed to directory: {os.getcwd()}")
        
                    # Use python3 explicitly and full path
                    command = f"python3 {selected['command'].replace('python ', '')}"
                    print(f"   Running: {command}")
                    result = os.system(command)
        
                    if result != 0:
                        print(f"❌ Command failed with exit code: {result}")
                        print(f"   Try running manually: cd {selected['path']} && python3 {selected['command']}")
                else:
                    print(f"❌ Chatbot directory not found: {chatbot_path}")
        
                break

            else:
                print("❌ Invalid choice. Please select 0-2.")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()