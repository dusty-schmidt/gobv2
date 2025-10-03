#!/usr/bin/env python3
# main.py - Entry point for the chatbot application
# Imports the main Chatbot class from the reorganized src structure

import asyncio
import sys
from pathlib import Path

# Add workspace root to path for core imports
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from core import CommunalBrain, BrainConfig
from mini.src.core import main

if __name__ == "__main__":
    asyncio.run(main())