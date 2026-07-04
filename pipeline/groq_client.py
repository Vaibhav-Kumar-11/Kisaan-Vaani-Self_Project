from functools import lru_cache
from groq import Groq
from config import require_secret

MODEL = "llama-3.3-70b-versatile"


@lru_cache(maxsize=1)
def get_client() -> Groq:
    return Groq(api_key=require_secret("GROQ_API_KEY"))
