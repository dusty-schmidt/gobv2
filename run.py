#!/usr/bin/env python3
"""
GOB (Grid Overwatch Bridge) - Communal Intelligence System
CLI entry point to select and run different chatbots/agents

Usage:
    python3 run.py                # Interactive mode
    python3 run.py --mini         # Run Mini chatbot
    python3 run.py --main         # Run Main agent
    python3 run.py --max          # Run Max agent
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="GOB - Communal Intelligence System")
    parser.add_argument('--mini', action='store_true', help='Run Mini chatbot')
    parser.add_argument('--main', action='store_true', help='Run Main agent')
    parser.add_argument('--max', action='store_true', help='Run Max agent')

    args = parser.parse_args()

    # Available chatbots/agents
    options = {
        "mini": {
            "name": "Mini v3.0",
            "description": "Enhanced chatbot with communal brain",
            "path": "mini",
            "command": "main.py"
        },
        "main": {
            "name": "Main v1.0",
            "description": "Agent with basic tools and capabilities",
            "path": "main",
            "command": "agent.py"
        },
        "max": {
            "name": "Max v1.0",
            "description": "Advanced self-improving agent framework",
            "path": "max",
            "command": "agent.py"
        }
    }

    # Check command line arguments
    if args.mini:
        selected = options["mini"]
        chatbot_key = "mini"
    elif args.main:
        selected = options["main"]
        chatbot_key = "main"
    elif args.max:
        selected = options["max"]
        chatbot_key = "max"
    else:
        # Interactive mode
        print("🤖 GOB - Communal Intelligence System")
        print("=" * 50)

        print("Available Chatbots:")
        for key, option in options.items():
            print(f"  --{key}: {option['name']} - {option['description']}")

        print("\n  0. Exit")
        print()

        while True:
            try:
                choice = input("Select chatbot to run (mini/main/max or 0 to exit): ").strip().lower()

                if choice in ["0", "exit", "quit"]:
                    print("👋 Goodbye!")
                    sys.exit(0)

                if choice in options:
                    selected = options[choice]
                    chatbot_key = choice
                    break
                else:
                    print("❌ Invalid choice. Please select 'mini', 'main', 'max', or '0' to exit.")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)

    # Run the selected chatbot
    print(f"🤖 GOB - Communal Intelligence System")
    print("=" * 50)
    print(f"🚀 Starting {selected['name']}...")
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
            sys.exit(result)
    else:
        print(f"❌ Chatbot directory not found: {chatbot_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()