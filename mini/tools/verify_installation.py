#!/usr/bin/env python3
# File: tools/verify_installation.py
# Role: Verification script (moved from project root)

import sys
import os
from pathlib import Path

# Ensure project root is on sys.path when running scripts from tools/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def check_dependencies():
    required = ['openai', 'numpy', 'requests']
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        return False
    return True

def check_api_keys():
    openai_key = os.getenv('OPENAI_API_KEY')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    ok = True
    if not openai_key:
        print("OPENAI_API_KEY not set")
        ok = False
    if not openrouter_key:
        print("OPENROUTER_API_KEY not set")
        ok = False
    return ok

def main():
    print("Running basic checks...")
    deps_ok = check_dependencies()
    keys_ok = check_api_keys()
    files_ok = all(Path(p).exists() for p in [
        'config.py', 'database.py', 'embeddings_manager.py', 'memory_store.py',
        'knowledge_base.py', 'chat_handler.py', 'llm_client.py', 'main.py'
    ])
    if not files_ok:
        print('Some required files are missing')

    if deps_ok and files_ok:
        print('Basic installation checks passed (keys may be required for full tests)')
    else:
        print('Installation checks failed')

if __name__ == '__main__':
    main()
