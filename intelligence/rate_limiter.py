import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


def check_groq_rate_limit(user_id, limit=10, window=60, scope="default"):
    """
    Retorna True se o usuário ainda pode fazer chamadas à API Groq.
    False se excedeu o limite de requisições na janela de tempo.

    scope: namespace para separar contadores (ex: "chat", "insight")
    """
    key = f"groq_rate_limit:{scope}:{user_id}"
    count = cache.get(key, 0)

    if count >= limit:
        logger.warning(
            "Rate limit excedido [%s] user %s: %d/%d em %ds",
            scope, user_id, count, limit, window,
        )
        return False

    cache.set(key, count + 1, window)
    return True
