import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY não configurada")
        return None
    return Groq(api_key=api_key)
