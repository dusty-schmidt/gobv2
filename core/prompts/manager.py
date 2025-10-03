"""
Prompt manager for loading and managing centralized prompts across all GOB tiers
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A prompt template with metadata"""
    name: str
    content: str
    tier: str
    category: str = "system"
    variables: Optional[Dict[str, Any]] = None

    def format(self, **kwargs) -> str:
        """Format the prompt with variables"""
        if self.variables:
            kwargs = {**self.variables, **kwargs}
        return self.content.format(**kwargs)


class PromptManager:
    """Centralized prompt manager for all GOB tiers"""

    def __init__(self, prompts_dir: Optional[Path] = None):
        if prompts_dir is None:
            # Default to core/prompts relative to this file
            prompts_dir = Path(__file__).parent
        self.prompts_dir = prompts_dir
        self._cache: Dict[str, PromptTemplate] = {}
        self._loaded = False

    def _load_prompts(self):
        """Load all prompts from the filesystem"""
        if self._loaded:
            return

        for tier_dir in self.prompts_dir.iterdir():
            if not tier_dir.is_dir() or tier_dir.name.startswith('__'):
                continue

            tier = tier_dir.name
            self._load_tier_prompts(tier, tier_dir)

        self._loaded = True

    def _load_tier_prompts(self, tier: str, tier_dir: Path):
        """Load prompts for a specific tier"""
        for prompt_file in tier_dir.rglob("*.md"):
            if prompt_file.name.startswith('__'):
                continue

            # Extract category and name from path
            relative_path = prompt_file.relative_to(tier_dir)
            parts = relative_path.with_suffix('').parts

            if len(parts) == 1:
                category = "system"
                name = parts[0]
            else:
                category = parts[0]
                name = "_".join(parts[1:])

            # Read content
            try:
                content = prompt_file.read_text(encoding='utf-8').strip()
                prompt = PromptTemplate(
                    name=f"{tier}.{category}.{name}",
                    content=content,
                    tier=tier,
                    category=category
                )
                self._cache[prompt.name] = prompt
            except Exception as e:
                print(f"Warning: Failed to load prompt {prompt_file}: {e}")

    def get_prompt(self, name: str, **kwargs) -> Optional[str]:
        """Get a formatted prompt by name"""
        self._load_prompts()
        prompt = self._cache.get(name)
        if prompt:
            return prompt.format(**kwargs)
        return None

    def get_prompt_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        self._load_prompts()
        return self._cache.get(name)

    def list_prompts(self, tier: Optional[str] = None, category: Optional[str] = None) -> list[str]:
        """List available prompts, optionally filtered by tier/category"""
        self._load_prompts()
        prompts = list(self._cache.keys())

        if tier:
            prompts = [p for p in prompts if p.startswith(f"{tier}.")]
        if category:
            prompts = [p for p in prompts if f".{category}." in p]

        return sorted(prompts)

    def reload(self):
        """Reload all prompts from disk"""
        self._cache.clear()
        self._loaded = False
        self._load_prompts()


# Global instance
_prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager