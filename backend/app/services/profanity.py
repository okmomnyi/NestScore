import logging
import os
from pathlib import Path

from better_profanity import profanity

logger = logging.getLogger(__name__)


def _load_custom_wordlist() -> list[str]:
    """
    Load custom Swahili/Sheng offensive terms from the wordlist file.
    Falls back gracefully if the file is missing.
    """
    try:
        base_dir = Path(__file__).resolve().parent.parent
        wordlist_path = base_dir / "data" / "custom_wordlist.txt"
        if not wordlist_path.exists():
            logger.warning("Custom profanity wordlist not found at %s", wordlist_path)
            return []
        with wordlist_path.open("r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip() and not line.lstrip().startswith("#")]
        return words
    except Exception as exc:
        logger.error("Failed to load custom profanity wordlist: %s", exc)
        return []

profanity.load_censor_words()
_custom_words = _load_custom_wordlist()
if _custom_words:
    profanity.add_censor_words(_custom_words)
    logger.info("Loaded %d custom profanity terms into filter", len(_custom_words))


def is_profane(text: str) -> bool:
    """
    Returns True if the text contains any term from the base profanity
    filter (English) or the extended Swahili/Sheng wordlist loaded
    from backend/app/data/custom_wordlist.txt.
    Does NOT reveal which word triggered the filter.
    """
    try:
        if profanity.contains_profanity(text):
            logger.info("Profanity filter triggered")
            return True
    except Exception as exc:
        logger.error("Profanity filter error: %s", exc)
    return False


REJECTION_MESSAGE = (
    "Your review contains language that is not permitted on NestScore. "
    "Please revise your review and resubmit. "
    "Reviews must describe the property experience only."
)
