import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Dummy secrets so importing/using client factories in tests never hits
# the "missing secret" error path — tests mock the actual API calls.
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("SARVAM_API_KEY", "test-sarvam-key")
