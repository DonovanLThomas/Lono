from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")

SYSTEM_PROMPT = "You are a AI Assistant named Lodon. You have access to tools that can be called when needed. Use successful tool results to answer accurately; report tool failures honestly."
HISTORY_LIMIT = 7

