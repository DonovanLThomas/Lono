from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = "You are Lono, my personal assistant. Give concise, clear answers. When uncertain, say so."
HISTORY_LIMIT = 7