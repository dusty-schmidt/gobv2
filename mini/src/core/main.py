# File: chatbot_v2/main.py
# Role: Main entry point for the upgraded vector embeddings chatbot
# Enhanced with color-coded output and real-time memory statistics

# Import communal brain from core
import sys
from pathlib import Path
# Add workspace root to path for core imports
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))
from core import CommunalBrain, BrainConfig

from .embeddings_manager import EmbeddingsManager
from .chat_handler import ChatHandler
from core.llm import LLMClient, LLMConfig
from .config import ChatbotConfig
from ..utils import get_logger
logger = get_logger(__name__)
import os
import sys
from pathlib import Path
 
# Load environment variables from .env if present
# Check workspace root first, then mini directory
try:
    from dotenv import load_dotenv
    # Try workspace root .env first
    _workspace_env = Path(__file__).parent.parent.parent.parent / '.env'
    if _workspace_env.exists():
        load_dotenv(dotenv_path=_workspace_env)
    else:
        # Fallback to mini directory .env
        _mini_env = Path(__file__).parent / '.env'
        if _mini_env.exists():
            load_dotenv(dotenv_path=_mini_env)
except Exception:
    # Fallback: simple .env parsing
    # Try workspace root first
    _workspace_env = Path(__file__).parent.parent.parent.parent / '.env'
    if _workspace_env.exists():
        with open(_workspace_env, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    else:
        # Fallback to mini directory .env
        _mini_env = Path(__file__).parent / '.env'
        if _mini_env.exists():
            with open(_mini_env, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip())

# Terminal color codes for enhanced display
class Colors:
    """ANSI color codes for terminal output"""
    # Text colors
    USER = '\033[96m'      # Cyan for user
    BOT = '\033[92m'       # Green for bot
    STATS = '\033[93m'     # Yellow for statistics
    INFO = '\033[94m'      # Blue for info
    SUCCESS = '\033[92m'   # Green for success
    WARNING = '\033[93m'   # Yellow for warnings
    ERROR = '\033[91m'     # Red for errors
    HEADER = '\033[95m'    # Magenta for headers
    DIM = '\033[2m'        # Dimmed text

    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # Reset
    RESET = '\033[0m'

    @staticmethod
    def user(text):
        return f"{Colors.USER}{text}{Colors.RESET}"

    @staticmethod
    def bot(text):
        return f"{Colors.BOT}{text}{Colors.RESET}"

    @staticmethod
    def stats(text):
        return f"{Colors.STATS}{text}{Colors.RESET}"

    @staticmethod
    def dim(text):
        return f"{Colors.DIM}{text}{Colors.RESET}"

    @staticmethod
    def header(text):
        return f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.RESET}"

class Chatbot:
    """Chatbot with OpenAI embeddings and SQLite persistence"""

    def __init__(self, config: ChatbotConfig = None):
        """Initialize chatbot with configuration"""
        self.config = config or ChatbotConfig()

    async def initialize(self):
        """Async initialization of chatbot components"""
        await self.setup_components()

    async def setup_components(self):
        """Initialize all chatbot components"""
        logger.info("Initializing Enhanced Chatbot")
        logger.info("%s", "=" * 60)
        logger.info("🤖 Initializing Enhanced Chatbot")
        logger.info("%s", "=" * 60)

        # Validate API keys
        if not self.config.embeddings.api_key:
            logger.error('OPENAI_API_KEY not found')
            print("\n❌ ERROR: OPENAI_API_KEY not found!")
            print("   Please set it: export OPENAI_API_KEY='your-key-here'")
            sys.exit(1)

        if not self.config.llm.api_key:
            logger.error('OPENROUTER_API_KEY not found')
            print("\n❌ ERROR: OPENROUTER_API_KEY not found!")
            print("   Please set it: export OPENROUTER_API_KEY='your-key-here'")
            sys.exit(1)
        # Initialize embeddings manager with OpenAI (still needed for generating embeddings)
        logger.info('Initializing embeddings manager')
        logger.info("🧠 Initializing OpenAI embeddings...")
        self.embeddings_mgr = EmbeddingsManager(
            api_key=self.config.embeddings.api_key,
            model_name=self.config.embeddings.model_name,
            embedding_dim=self.config.embeddings.embedding_dim
        )
        logger.info('Embeddings model: %s dims=%d', self.config.embeddings.model_name, self.config.embeddings.embedding_dim)

        # Initialize communal brain
        logger.info('Initializing communal brain')
        logger.info("🧠 Initializing Communal Brain...")
        brain_config = BrainConfig()
        # Use communal database in gob/core/ instead of individual chatbot directories
        import os
        workspace_root = Path(__file__).parent.parent.parent.parent
        communal_db_path = workspace_root / "core" / "communal_brain.db"
        brain_config.storage.local_db_path = str(communal_db_path)
        brain_config.device_name = "Mini Chatbot"
        brain_config.device_location = "local"

        self.brain = CommunalBrain(brain_config)
        await self.brain.initialize()

        # Show brain stats
        stats = await self.brain.get_memory_stats()
        logger.info('Communal brain stats: %s', stats)
        logger.info("   ✓ Memories: %d", stats['memory_count'])
        logger.info("   ✓ Knowledge chunks: %d", stats['knowledge_count'])
        logger.info("   ✓ Devices: %d", stats['device_count'])

        # Load knowledge documents if directory exists (using communal brain)
        docs_dir = Path(self.config.knowledge.docs_directory)
        if docs_dir.exists() and any(docs_dir.glob('*.txt')):
            # Check if knowledge is already loaded
            if stats['knowledge_count'] == 0:
                logger.info("📖 Loading knowledge documents from %s", self.config.knowledge.docs_directory)
                await self._load_knowledge_documents(docs_dir)
            else:
                logger.info("ℹ️  Knowledge already loaded (%d chunks)", stats['knowledge_count'])
        else:
            logger.info("ℹ️  No knowledge documents found in %s", self.config.knowledge.docs_directory)

        # Initialize LLM client
        logger.info("🤖 Initializing LLM client...")
        llm_config = LLMConfig()
        self.llm_client = LLMClient(
            api_key=llm_config.api_key,
            model=llm_config.model,
            base_url=llm_config.base_url
        )
        logger.info("   ✓ Model: %s", llm_config.model)

        # Initialize chat handler with communal brain
        self.chat_handler = ChatHandler(
            llm_client=self.llm_client,
            brain=self.brain,
            embeddings_mgr=self.embeddings_mgr,
            memory_config=self.config.memory,
            knowledge_config=self.config.knowledge,
            llm_config=self.config.llm
        )

        print("\n" + "="*60)
        print("✅ Chatbot ready!")
        print("="*60 + "\n")

    async def _load_knowledge_documents(self, docs_dir: Path):
        """Load knowledge documents into communal brain"""
        import asyncio

        for txt_file in docs_dir.glob('*.txt'):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Split into chunks
                chunks = self._chunk_text(content, self.config.knowledge.chunk_size)

                for i, chunk in enumerate(chunks):
                    # Generate embedding for the chunk
                    embedding = await asyncio.get_event_loop().run_in_executor(
                        None, self.embeddings_mgr.encode, chunk
                    )

                    # Store in communal brain
                    await self.brain.store_knowledge(
                        content=chunk,
                        embedding=embedding,
                        source=str(txt_file),
                        chunk_index=i,
                        total_chunks=len(chunks)
                    )

                logger.info("Loaded %d chunks from %s", len(chunks), txt_file.name)

            except Exception as e:
                logger.error("Failed to load %s: %s", txt_file.name, e)

    def _chunk_text(self, text: str, chunk_size: int) -> list[str]:
        """Split text into chunks of approximately chunk_size characters"""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            current_text = ' '.join(current_chunk)

            if len(current_text) >= chunk_size:
                chunks.append(current_text)
                current_chunk = []

        # Add remaining words
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    async def chat(self, user_message: str):
        """
        Process a user message and return bot response with statistics

        Args:
            user_message: User's input message

        Returns:
            Tuple of (response, memory_stats_dict)
        """
        # Get memory count before
        stats_before = await self.brain.get_memory_stats()
        memories_before = stats_before['memory_count']

        # Generate response using ChatHandler (which now handles context, memories, and knowledge)
        response, token_info = await self.chat_handler.generate_response(user_message)

        # Get memory count after
        stats_after = await self.brain.get_memory_stats()
        memories_after = stats_after['memory_count']

        # Get conversation context info for stats
        conversation_turns = len(self.chat_handler.context_manager.conversation_history)
        conversation_context_used = conversation_turns > 1  # True if we have conversation history

        # Build statistics including token usage and conversation context
        stats = {
            'memories_retrieved': 0,  # ChatHandler handles this internally now
            'knowledge_retrieved': 0,  # ChatHandler handles this internally now
            'conversation_context_used': conversation_context_used,
            'memories_saved': memories_after - memories_before,
            'total_memories': memories_after,
            'retrieved_memory_scores': [],  # Would need to expose from ChatHandler if needed
            'retrieved_knowledge_scores': [],  # Would need to expose from ChatHandler if needed
            'conversation_turns': conversation_turns,
            'input_tokens': token_info.get('input_tokens', 0),
            'output_tokens': token_info.get('output_tokens', 0),
            'total_tokens': token_info.get('total_tokens', 0),
            'model': self.config.llm.model
        }

        return response, stats

    async def run_interactive(self):
        """Run interactive chat loop with enhanced display"""
        print(Colors.header("💬 Interactive chat mode"))
        print(Colors.dim("   Commands: 'exit', 'quit', 'bye' to end | 'stats' for brain info | 'clear' to reset conversation | 'debug' to toggle context inspection"))
        print()

        conversation_count = 0

        while True:
            try:
                # Get user input with color
                user_input = input("You: ").strip()  # Simple prompt without emoji

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\n" + Colors.header("👋 Goodbye!"))
                    break

                # Special commands
                if user_input.lower() == 'stats':
                    await self.show_stats()
                    continue

                if user_input.lower() == 'clear':
                    self.chat_handler.clear_conversation()
                    print("🧹 Conversation history cleared. Starting fresh!")
                    continue

                if user_input.lower() == 'debug':
                    debug_state = self.chat_handler.toggle_debug()
                    status = "ENABLED" if debug_state else "DISABLED"
                    print(f"🔍 Debug mode {status}. Full LLM prompts will be displayed.\n")
                    continue

                # Echo user input with color for readability
                # User input already displayed, no echo needed  # User icon for clarity

                # Add spacing before bot response
                print()

                # Show thinking indicator
                print(Colors.dim("💭 Thinking..."), end="", flush=True)

                # Generate response with statistics
                response, stats = await self.chat(user_input)

                # Clear the thinking indicator line (overwrite with spaces and return)
                print("\r" + " " * 60 + "\r", end="", flush=True)

                # Display bot response with full color
                print(Colors.bot(f"🤖 Bot: {response}"))  # Bot icon for clarity

                # Display memory statistics
                print()
                self._display_exchange_stats(stats)

                # Add spacing after exchange
                print()

                conversation_count += 1

            except KeyboardInterrupt:
                print("\n\n" + Colors.header("👋 Interrupted. Goodbye!"))
                break
            except Exception as e:
                print(f"\n{Colors.ERROR}❌ Error: {e}{Colors.RESET}\n")

        # Show final stats
        if conversation_count > 0:
            print(Colors.stats(f"\n📊 This session: {conversation_count} exchanges"))
            await self.show_stats()

    def _display_exchange_stats(self, stats):
        """Display memory statistics for the current exchange"""
        # Build stats line
        parts = []

        # Conversation context used
        if stats.get('conversation_context_used', False):
            parts.append(f"💬 Conversation context active ({stats.get('conversation_turns', 0)} turns)")
        else:
            parts.append("💬 New conversation started")

        # Memories used (simplified since ChatHandler handles this internally)
        parts.append("📝 Memories accessed via communal brain")

        # Knowledge used (simplified since ChatHandler handles this internally)
        parts.append("📚 Knowledge accessed via communal brain")

        # Memories saved
        if stats['memories_saved'] > 0:
            parts.append(f"💾 {stats['memories_saved']} new memory saved")

        # Total memories
        parts.append(f"Total: {stats['total_memories']} memories")

        # Model used
        if 'model' in stats:
            # Extract just the model name for display (remove provider prefix if present)
            model_name = stats['model'].split('/')[-1] if '/' in stats['model'] else stats['model']
            parts.append(f"🤖 Model: {model_name}")

        # Token usage
        if stats.get('total_tokens', 0) > 0:
            parts.append(f"🎫 Tokens: {stats['input_tokens']}in + {stats['output_tokens']}out = {stats['total_tokens']} total")

        # Display with color
        stats_line = Colors.stats(" | ".join(parts))
        print(Colors.dim("─" * 80))
        print(stats_line)
        print(Colors.dim("─" * 80))

    async def show_stats(self):
        """Display chatbot statistics"""
        brain_stats = await self.brain.get_memory_stats()

        print("\n" + "="*60)
        print(Colors.header("📊 Communal Brain Statistics"))
        print("="*60)
        print(f"Total memories: {brain_stats['memory_count']}")
        print(f"Knowledge chunks: {brain_stats['knowledge_count']}")
        print(f"Connected devices: {brain_stats['device_count']}")
        print(f"Embedding model: {self.config.embeddings.model_name}")
        print(f"LLM model: {self.config.llm.model}")
        print("="*60 + "\n")

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'database'):
            self.database.close()

async def main():
    """Main entry point"""
    try:
        # Create chatbot instance
        bot = Chatbot()

        # Initialize async components
        await bot.initialize()

        # Run interactive mode
        await bot.run_interactive()

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.brain.close()  # Close communal brain

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
