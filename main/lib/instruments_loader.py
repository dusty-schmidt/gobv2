import os
import importlib.util
from typing import Dict, Any, Callable

def load_instruments_from_directory(directory_path: str) -> Dict[str, Callable]:
    instruments = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            file_path = os.path.join(directory_path, filename)
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None: continue
            module = importlib.util.module_from_spec(spec)
            if spec.loader is None: continue
            spec.loader.exec_module(module)
            
            # Assuming each instrument file defines a single main callable (function or class)
            # with the same name as the module for simplicity in barebones setup.
            # For a more robust system, we would iterate module members and apply decorators/annotations.
            if hasattr(module, module_name) and callable(getattr(module, module_name)):
                instruments[module_name] = getattr(module, module_name)
            elif len(dir(module)) > 6: # Heuristic: if module has more than typical boilerplate members, look for callables
                for attribute_name in dir(module):
                    if not attribute_name.startswith('__') and callable(getattr(module, attribute_name)):
                        instruments[attribute_name] = getattr(module, attribute_name)
    return instruments
