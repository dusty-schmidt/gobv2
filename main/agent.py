import fire
import os
from typing import Dict, Any

# Ensure the base directory is in the path for imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompts import DEFAULT_SYSTEM_PROMPT
from lib.instruments_loader import load_instruments_from_directory

class Agent:
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.system_prompt = system_prompt
        # Dynamically load instruments
        self.instruments = load_instruments_from_directory(os.path.join(os.path.dirname(__file__), 'instruments'))
        
        print(f"Agent Initialized with System Prompt: '{self.system_prompt}'")
        print(f"Available Instruments: {list(self.instruments.keys())}")

    def run(self, task: str = "default", **kwargs): 
        print(f"\nAgent received task: '{task}' with kwargs: {kwargs}")
        if task == "greet":
            print(self.instruments['hello_world'](kwargs.get('name', 'AgentZero')))
        elif task == "calculate" and 'calculator' in self.instruments:
            num1 = kwargs.get('num1', 0)
            num2 = kwargs.get('num2', 0)
            print(f"Calculation result: {self.instruments['calculator'].add(num1, num2)}")
        else:
            print(f"Agent processed task '{task}' using its internal logic. No new instrument called for this, but showing capabilities.")


def main():
    fire.Fire(Agent)

if __name__ == '__main__':
    main()
