"""Общий лимитер запросов — защита от подбора паролей, спама писем и
перерасхода бесплатных лимитов Gemini/SMTP на публично доступных эндпоинтах.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
