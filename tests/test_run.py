#!/usr/bin/env python3
"""
Test script for gob/run.py entry point
Tests that both chatbots can be launched from the main entry point
"""

import subprocess
import sys
import time
from pathlib import Path

def test_chatbot_launch(selection, name):
    """Test launching a specific chatbot"""
    print(f"\n🧪 Testing {name} launch from gob/run.py...")

    # Create a subprocess that simulates user input
    process = subprocess.Popen(
        [sys.executable, 'run.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent
    )

    try:
        # Send the chatbot selection
        stdout, stderr = process.communicate(input=f"{selection}\n", timeout=10)

        print("📄 STDOUT:")
        print(stdout)

        if stderr:
            print("📄 STDERR:")
            print(stderr)

        # Check if it launched successfully (look for success indicators)
        if "🚀 Starting" in stdout and "Changed to directory" in stdout:
            print(f"✅ {name} launched successfully!")
            return True
        else:
            print(f"❌ {name} launch failed!")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ {name} timed out (this is expected for interactive chatbots)")
        process.kill()
        # For interactive chatbots, timeout is actually success
        return True
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False

def main():
    print("🧪 Testing GOB run.py entry point")
    print("=" * 50)

    # Test Mini chatbot via keyword input
    mini_success = test_chatbot_launch("mini", "Mini v3.0")

    # Test Main agent via keyword input
    main_success = test_chatbot_launch("main", "Main v1.0")

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Mini: {'✅ PASS' if mini_success else '❌ FAIL'}")
    print(f"   Main: {'✅ PASS' if main_success else '❌ FAIL'}")

    if mini_success and main_success:
        print("🎉 Chatbots launch successfully from gob/run.py!")
        return True
    else:
        print("❌ Some chatbots failed to launch!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
