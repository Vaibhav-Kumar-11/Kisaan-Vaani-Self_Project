from functools import lru_cache
from sarvamai import SarvamAI
from config import require_secret


@lru_cache(maxsize=1)
def get_client() -> SarvamAI:
    return SarvamAI(api_subscription_key=require_secret("SARVAM_API_KEY"))
