"""
API Key Rotation Manager
Supports multiple comma-separated API keys for Gemini and Groq.
Automatically rotates to the next key when a quota/rate-limit error is hit.
"""
import logging
import threading

logger = logging.getLogger(__name__)


class KeyRotator:
    """Thread-safe API key rotator that cycles through multiple keys."""
    
    def __init__(self, name: str, keys_csv: str):
        self.name = name
        self.keys = [k.strip() for k in keys_csv.split(",") if k.strip()] if keys_csv else []
        self._index = 0
        self._lock = threading.Lock()
        logger.info(f"KeyRotator [{name}]: Loaded {len(self.keys)} key(s)")
    
    @property
    def current(self) -> str:
        """Get the current active key."""
        if not self.keys:
            return ""
        with self._lock:
            return self.keys[self._index % len(self.keys)]
    
    def rotate(self) -> str:
        """Rotate to the next key and return it."""
        if len(self.keys) <= 1:
            return self.current
        with self._lock:
            old_idx = self._index
            self._index = (self._index + 1) % len(self.keys)
            logger.warning(
                f"KeyRotator [{self.name}]: Rotated from key #{old_idx + 1} "
                f"to key #{self._index + 1} of {len(self.keys)}"
            )
            return self.keys[self._index]
    
    @property
    def has_keys(self) -> bool:
        return len(self.keys) > 0
    
    @property
    def count(self) -> int:
        return len(self.keys)


# --- Singleton instances (initialized from settings) ---

_gemini_rotator = None
_groq_rotator = None
_grok_rotator = None


def init_rotators(gemini_csv: str, groq_csv: str, xai_csv: str = ""):
    """Initialize the global key rotators from config values."""
    global _gemini_rotator, _groq_rotator, _grok_rotator
    _gemini_rotator = KeyRotator("Gemini", gemini_csv or "")
    _groq_rotator = KeyRotator("Groq", groq_csv or "")
    _grok_rotator = KeyRotator("Grok", xai_csv or "")


def get_gemini_rotator() -> KeyRotator:
    global _gemini_rotator
    if _gemini_rotator is None:
        _gemini_rotator = KeyRotator("Gemini", "")
    return _gemini_rotator


def get_groq_rotator() -> KeyRotator:
    global _groq_rotator
    if _groq_rotator is None:
        _groq_rotator = KeyRotator("Groq", "")
    return _groq_rotator


def get_grok_rotator() -> KeyRotator:
    global _grok_rotator
    if _grok_rotator is None:
        _grok_rotator = KeyRotator("Grok", "")
    return _grok_rotator

