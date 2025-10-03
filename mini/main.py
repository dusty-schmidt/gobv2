#!/usr/bin/env python3
# main.py - Entry point for the chatbot application
# Imports the main Chatbot class from the reorganized src structure

import asyncio
from src.core import main

if __name__ == "__main__":
    asyncio.run(main())