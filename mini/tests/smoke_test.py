#!/usr/bin/env python3
# File: tools/smoke_test.py
# Role: Lightweight smoke test that verifies a prompt roundtrip without external API calls

import sys
import os
import types
from types import SimpleNamespace
from typing import Tuple, Dict
import argparse

# Ensure project root is on sys.path when running scripts from tests/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Parse args to allow running a live test against real APIs
parser = argparse.ArgumentParser(description='Smoke test for chatbot')
parser.add_argument('--live', action='store_true', help='Run live test using real APIs from .env')
parser.add_argument('--no-save', action='store_true', help='Do not persist changes to disk (use in-memory DB)')
parser.add_argument('--use-llm', action='store_true', help='Force using the real LLM client even when not running full live mode')
args, _ = parser.parse_known_args()
NO_SAVE = args.no_save
USE_LLM = getattr(args, 'use_llm', False)

# Load .env from project root if available so environment keys become visible
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(ROOT, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
except Exception:
    # ignore missing dotenv package or .env file
    pass

# Decide whether to run live LLM:
# - explicit --live
# - explicit --use-llm
# - or if OPENROUTER_API_KEY & OPENAI_API_KEY are present in env
LIVE = bool(args.live or USE_LLM or (os.environ.get('OPENROUTER_API_KEY') and os.environ.get('OPENAI_API_KEY')))

# Insert lightweight shims for heavy external packages only if imports fail
if not LIVE:
    try:
        import numpy as np  # type: ignore
    except Exception:
        np = types.ModuleType('numpy')
        import math

        def _array(x, dtype=None):
            try:
                return list(x)
            except TypeError:
                return [x]

        def _zeros(shape, dtype=None):
            # Support scalar int or tuple shapes
            if isinstance(shape, int):
                return [0.0] * int(shape)
            if isinstance(shape, tuple):
                if len(shape) == 2:
                    return [[0.0] * int(shape[1]) for _ in range(int(shape[0]))]
                # support 1-D tuple
                if len(shape) == 1:
                    return [0.0] * int(shape[0])
            # Fallback: try to coerce to int
            try:
                return [0.0] * int(shape)
            except Exception:
                return []

        def _frombuffer(buf, dtype=None):
            return []

        def _dot(a, b):
            return sum(x * y for x, y in zip(a, b))

        class _linalg:
            @staticmethod
            def norm(v, axis=None):
                if axis is None:
                    return math.sqrt(sum(x * x for x in v))
                return [math.sqrt(sum(x * x for x in row)) for row in v]

        np.array = _array
        np.zeros = _zeros
        np.frombuffer = _frombuffer
        np.float32 = float
        np.linalg = _linalg
        np.dot = _dot
        np.ndarray = list
        sys.modules['numpy'] = np
else:
    # In live mode, prefer the real numpy available in the venv
    try:
        import numpy as np  # type: ignore
    except Exception:
        print('\nERROR: live LLM runs require numpy to be installed.')
        print("Install dependencies: pip install -r ../requirements.txt or pip install numpy requests python-dotenv")
        sys.exit(1)

# Minimal openai shim returning predictable embeddings only if openai not installed
if not LIVE:
    try:
        import openai  # type: ignore
    except Exception:
        openai = types.ModuleType('openai')

        class OpenAI:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.embeddings = SimpleNamespace()

                def create(input, model=None):
                    dim = 1536
                    def _one():
                        return SimpleNamespace(embedding=[0.0] * dim)

                    if isinstance(input, list):
                        data = [_one() for _ in input]
                    else:
                        data = [_one()]

                    return SimpleNamespace(data=data)

                self.embeddings.create = create

        openai.OpenAI = OpenAI
        sys.modules['openai'] = openai
else:
    import openai  # type: ignore

if not LIVE:
    # Provide dummy API keys so components that check them don't exit
    os.environ.setdefault('OPENAI_API_KEY', 'test')
    os.environ.setdefault('OPENROUTER_API_KEY', 'test')

    # Inject a mock embeddings_manager module to avoid real OpenAI calls during tests
    if 'embeddings_manager' not in sys.modules:
        mock_mod = types.ModuleType('embeddings_manager')
        try:
            import numpy as _np  # prefer real numpy from venv
        except Exception:
            _np = None

        class EmbeddingsManager:
            def __init__(self, api_key=None, model_name='text-embedding-3-small', embedding_dim=1536):
                self.api_key = api_key
                self.model_name = model_name
                self.embedding_dim = embedding_dim

            def encode(self, text, retry_count=3):
                if _np is not None:
                    return _np.zeros(self.embedding_dim, dtype=_np.float32)
                return [0.0] * self.embedding_dim

            def encode_batch(self, texts, batch_size=100):
                if _np is not None:
                    return _np.zeros((len(texts), self.embedding_dim), dtype=_np.float32)
                return [[0.0] * self.embedding_dim for _ in texts]

            def cosine_similarity(self, vec1, vec2):
                # safe fallback
                try:
                    if _np is not None:
                        n1 = _np.linalg.norm(vec1)
                        n2 = _np.linalg.norm(vec2)
                        if n1 == 0 or n2 == 0:
                            return 0.0
                        return float(_np.dot(vec1, vec2) / (n1 * n2))
                except Exception:
                    return 0.0
                return 0.0

            def find_most_similar(self, query_embedding, embeddings, top_k=5):
                return []

        mock_mod.EmbeddingsManager = EmbeddingsManager
        sys.modules['embeddings_manager'] = mock_mod

# We import modules from the project but patch LLMClient to avoid network calls
from src.core import LLMClient, Chatbot, ChatbotConfig
from src.utils import get_logger
logger = get_logger(__name__)


class MockLLMClient(LLMClient):
    """Mock LLM client that returns a deterministic response and token info"""

    def __init__(self, *args, **kwargs):
        # Do not call super to avoid API key checks
        self.model = kwargs.get('model', 'mock-model')

    def generate_response(self, messages, temperature=0.7, max_tokens=1000, stream=False) -> Tuple[str, Dict]:
        # Return a deterministic reply derived from the last user message
        user_msg = None
        if isinstance(messages, list) and len(messages) > 0:
            # Try to find the last user content
            for m in reversed(messages):
                if m.get('role') == 'user':
                    user_msg = m.get('content')
                    break

        reply = f"(mocked) Received: {user_msg or '<no-user-message>'}"
        token_info = {'input_tokens': 1, 'output_tokens': 1, 'total_tokens': 2}
        return reply, token_info


def run_smoke_test():
    logger.info('Running smoke test (live=%s no_save=%s)', LIVE, NO_SAVE)
    print('Running smoke test...')

    # Create chatbot config and set testing model to a free verification model
    cfg = ChatbotConfig()
    cfg.llm.model = "openai/gpt-oss-20b:free"

    # Use in-memory DB when --no-save is requested to avoid persisting changes
    if NO_SAVE:
        cfg.database.db_path = ':memory:'
        # Set environment flag so lower-level components refuse file-backed DBs
        os.environ['TEST_NO_SAVE'] = '1'

    bot = Chatbot(cfg)

    # Replace the LLM client with our mock to avoid network/API calls when not live
    if not LIVE:
        bot.llm_client = MockLLMClient()
        bot.chat_handler.llm_client = bot.llm_client

    test_prompt = 'tell me a joke about artificial intelligence'
    try:
        response, stats = bot.chat(test_prompt)
        logger.info('Smoke test response: %s', response)
        logger.info('Smoke test stats: %s', stats)

        # Basic assertions
        if not isinstance(response, str) or not response:
            logger.error('Smoke test failed: invalid response')
            return 1

        if not isinstance(stats, dict):
            logger.error('Smoke test failed: invalid stats')
            return 1

        logger.info('\u2705 Smoke test passed')
        return 0

    except Exception as e:
        logger.exception('Smoke test failed with exception: %s', e)
        return 1


if __name__ == '__main__':
    sys.exit(run_smoke_test())
