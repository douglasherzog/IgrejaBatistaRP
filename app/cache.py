from functools import wraps
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional

# Cache simples em memória
_cache = {}
_cache_times = {}

def cache_key(*args, **kwargs) -> str:
    """Gera uma chave de cache baseada nos argumentos"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def cache(expire_minutes: int = 30):
    """Decorator para cache simples"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            now = datetime.now()
            
            # Verificar se cache existe e não expirou
            if key in _cache:
                cache_time = _cache_times.get(key, datetime.min)
                if now - cache_time < timedelta(minutes=expire_minutes):
                    return _cache[key]
            
            # Executar função e cache resultado
            result = func(*args, **kwargs)
            _cache[key] = result
            _cache_times[key] = now
            
            return result
        return wrapper
    return decorator

def clear_cache(pattern: Optional[str] = None):
    """Limpa cache"""
    global _cache, _cache_times
    if pattern:
        keys_to_remove = [k for k in _cache.keys() if pattern in k]
        for key in keys_to_remove:
            _cache.pop(key, None)
            _cache_times.pop(key, None)
    else:
        _cache.clear()
        _cache_times.clear()

def get_cache_stats() -> dict:
    """Retorna estatísticas do cache"""
    return {
        'total_items': len(_cache),
        'keys': list(_cache.keys())
    }
