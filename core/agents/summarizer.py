#!/usr/bin/env python3
"""
SummarizerAgent - Background agent that summarizes conversation logs to manage token bloat
Uses meta-llama/llama-3.3-8b-instruct:free for cost-effective summarization
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from ..llm.llm_client import LLMClient
from ..logging import get_logger

logger = get_logger(__name__)

class SummarizerConfig:
    """Configuration for the SummarizerAgent"""

    def __init__(self):
        # Model settings
        self.model = "meta-llama/llama-3.3-8b-instruct:free"
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key_env = "OPENROUTER_API_KEY"

        # Summarization triggers
        self.max_file_size_bytes = 50 * 1024  # 50KB per conversation file
        self.max_context_tokens = 6000  # Summarize when context exceeds this
        self.monitoring_interval_seconds = 300  # Check every 5 minutes

        # Summarization settings
        self.max_summary_tokens = 500  # Maximum tokens per summary
        self.temperature = 0.3  # Low temperature for consistent summaries
        self.keep_originals = True  # Archive originals after summarization

class SummarizerAgent:
    """Background agent that summarizes conversation logs to manage token bloat"""

    def __init__(self, data_dir: Path, config: Optional[SummarizerConfig] = None):
        self.data_dir = data_dir
        self.config = config or SummarizerConfig()
        self.conversations_dir = data_dir / "conversations"
        self.archive_dir = data_dir / "archive" / "conversations"
        self.summaries_dir = data_dir / "summaries"

        # Create directories
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

        # Initialize LLM client for summarization
        self.llm_client = LLMClient(
            api_key=os.getenv(self.config.api_key_env),
            model=self.config.model,
            base_url=self.config.base_url
        )

        # Background task tracking
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False

        logger.info(f"🤖 SummarizerAgent initialized with model: {self.config.model}")

    async def start_background_monitoring(self):
        """Start background monitoring for files that need summarization"""
        if self.is_running:
            logger.warning("SummarizerAgent is already running")
            return

        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("📊 Started background conversation monitoring")

    async def stop_background_monitoring(self):
        """Stop background monitoring"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Stopped background conversation monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop that checks for files needing summarization"""
        while self.is_running:
            try:
                await self._check_and_summarize_files()
                await asyncio.sleep(self.config.monitoring_interval_seconds)
            except Exception as e:
                logger.error(f"Error in summarizer monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def _check_and_summarize_files(self):
        """Check all conversation files and summarize those that exceed size limits"""
        if not self.conversations_dir.exists():
            return

        conversation_files = list(self.conversations_dir.glob("*.json"))
        logger.debug(f"📁 Checking {len(conversation_files)} conversation files")

        for filepath in conversation_files:
            try:
                if await self._should_summarize_file(filepath):
                    logger.info(f"📝 Summarizing large conversation file: {filepath.name}")
                    await self._summarize_conversation_file(filepath)
            except Exception as e:
                logger.error(f"Error processing conversation file {filepath}: {e}")

    async def _should_summarize_file(self, filepath: Path) -> bool:
        """Check if a conversation file should be summarized"""
        # Check file size
        file_size = filepath.stat().st_size
        if file_size > self.config.max_file_size_bytes:
            logger.debug(f"File {filepath.name} size {file_size} > {self.config.max_file_size_bytes}")
            return True

        # Check if file is older than a week (periodic cleanup)
        file_age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
        if file_age > timedelta(days=7):
            logger.debug(f"File {filepath.name} is {file_age.days} days old")
            return True

        return False

    async def _summarize_conversation_file(self, filepath: Path):
        """Summarize a conversation file and archive the original"""
        try:
            # Read the conversation data
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)

            # Format conversation for summarization
            conversation_text = self._format_conversation_for_summary(conversation_data['messages'])

            # Generate summary
            summary = await self._generate_summary(conversation_text)

            # Create summary data structure
            summary_data = {
                "original_session_id": conversation_data["session_id"],
                "device": conversation_data["device"],
                "original_timestamp": conversation_data["timestamp"],
                "original_message_count": len(conversation_data["messages"]),
                "summary": summary,
                "summarized_at": datetime.now().isoformat(),
                "summarizer_model": self.config.model,
                "file_size_bytes": filepath.stat().st_size
            }

            # Save summary
            summary_filename = f"{conversation_data['session_id']}_summary.json"
            summary_filepath = self.summaries_dir / summary_filename

            with open(summary_filepath, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)

            # Archive original if configured
            if self.config.keep_originals:
                archive_filepath = self.archive_dir / filepath.name
                filepath.rename(archive_filepath)
                logger.info(f"📦 Archived original conversation to: {archive_filepath}")
            else:
                # Delete original if not keeping archives
                filepath.unlink()

            logger.info(f"✅ Summarized conversation {conversation_data['session_id']}: {len(conversation_data['messages'])} messages → {len(summary)} chars")

        except Exception as e:
            logger.error(f"Failed to summarize conversation file {filepath}: {e}")

    def _format_conversation_for_summary(self, messages: List[Dict]) -> str:
        """Format conversation messages for summarization input"""
        formatted_lines = []

        for msg in messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            content = msg["content"]
            formatted_lines.append(f"**{role}**: {content}")

        return "\n\n".join(formatted_lines)

    async def _generate_summary(self, conversation_text: str) -> str:
        """Generate a summary of the conversation using the LLM"""
        summary_prompt = f"""
        Please provide a comprehensive but concise summary of this conversation. Focus on:

        1. **Key topics and themes** discussed
        2. **Important user information** (name, preferences, requirements)
        3. **Decisions or conclusions** reached
        4. **Action items** or follow-ups mentioned
        5. **Emotional context** or user sentiment

        Keep the summary informative but not verbose. Capture the essence of the conversation while preserving important details.

        Conversation to summarize:
        ---
        {conversation_text}
        ---
        """

        try:
            response, token_info = await self.llm_client.generate_response(
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_summary_tokens,
                stream=False
            )

            logger.debug(f"📊 Summary generated: {token_info.get('input_tokens', 0)} input tokens, {token_info.get('output_tokens', 0)} output tokens")
            return response.strip()

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return f"Summary generation failed: {str(e)}"

    async def summarize_on_startup(self):
        """Summarize files that need it on system startup"""
        logger.info("🔄 Running startup summarization check...")
        await self._check_and_summarize_files()
        logger.info("✅ Startup summarization check complete")

    async def manual_summarize_file(self, filepath: Path) -> bool:
        """Manually trigger summarization of a specific file"""
        try:
            if filepath.exists() and filepath.suffix == '.json':
                logger.info(f"🔧 Manually summarizing: {filepath.name}")
                await self._summarize_conversation_file(filepath)
                return True
            else:
                logger.warning(f"File not found or not a JSON file: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Manual summarization failed: {e}")
            return False

    async def check_context_size(self, context_text: str) -> Tuple[bool, Optional[str]]:
        """Check if context is too large and return suggested summary if needed"""
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(context_text) // 4

        if estimated_tokens > self.config.max_context_tokens:
            logger.info(f"📏 Context too large: {estimated_tokens} tokens > {self.config.max_context_tokens}")

            # Generate a quick summary of the current context
            summary_prompt = f"""
            This conversation context is too long for the AI model. Please create a concise summary that captures:
            - Current conversation topic
            - Key points discussed so far
            - User's main questions or requests
            - Important context to maintain

            Keep it under 200 words.

            Context to summarize:
            {context_text[-8000:]}  # Last 8000 chars to focus on recent content
            """

            try:
                summary, _ = await self.llm_client.generate_response(
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=self.config.temperature,
                    max_tokens=300,
                    stream=False
                )

                return True, summary.strip()

            except Exception as e:
                logger.error(f"Failed to generate context summary: {e}")
                return True, f"Context too long ({estimated_tokens} tokens). Consider clearing history."

        return False, None

    def get_stats(self) -> Dict:
        """Get summarization statistics"""
        stats = {
            "model": self.config.model,
            "is_running": self.is_running,
            "monitoring_interval": self.config.monitoring_interval_seconds,
            "max_file_size_kb": self.config.max_file_size_bytes // 1024,
            "max_context_tokens": self.config.max_context_tokens
        }

        # Count files in each directory
        if self.conversations_dir.exists():
            stats["conversation_files"] = len(list(self.conversations_dir.glob("*.json")))

        if self.summaries_dir.exists():
            stats["summary_files"] = len(list(self.summaries_dir.glob("*.json")))

        if self.archive_dir.exists():
            stats["archived_files"] = len(list(self.archive_dir.glob("*.json")))

        return stats