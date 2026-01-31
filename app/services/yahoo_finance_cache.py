"""
Sistema de cache en memoria para consultas a Yahoo Finance

Este módulo implementa un cache simple en memoria para evitar
llamadas repetidas a Yahoo Finance API dentro de un corto período.

¿Por qué cachear?
- Yahoo Finance tiene límites de rate limiting (error 429)
- Las consultas tienen un costo de tiempo de respuesta
- Los datos históricos no cambian frecuentemente

Duración del cache: 5 minutos (300 segundos)
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json


# Estructura del cache en memoria
# Clave: (market, symbol, timeframe) como tupla
# Valor: {
#     "data": [...],  # Lista de velas OHLCV
#     "timestamp": datetime,  # Cuándo se guardó en cache
#     "expires_at": datetime  # Cuándo expira el cache
# }
_cache: Dict[Tuple[str, str, str], Dict] = {}

# Duración del cache en segundos según timeframe
# TTL (Time To Live) dinámico basado en el timeframe
CACHE_TTL = {
    "1d": 1800,   # 30 minutos (30 * 60)
    "1h": 600,    # 10 minutos (10 * 60)
    "4h": 900,    # 15 minutos (fallback para otros timeframes)
}

# Duración por defecto (si el timeframe no está en CACHE_TTL)
DEFAULT_CACHE_DURATION_SECONDS = 300  # 5 minutos


def get_cache_duration(timeframe: str) -> int:
    """
    Obtiene la duración del cache en segundos según el timeframe.
    
    Args:
        timeframe: Período de tiempo (1h, 4h, 1d)
    
    Returns:
        Duración en segundos
    """
    return CACHE_TTL.get(timeframe.lower(), DEFAULT_CACHE_DURATION_SECONDS)


def _make_cache_key(market: str, symbol: str, timeframe: str) -> Tuple[str, str, str]:
    """
    Crea una clave única para el cache.
    
    Args:
        market: Tipo de mercado (stocks, cedears)
        symbol: Símbolo del activo
        timeframe: Período de tiempo
    
    Returns:
        Tupla que sirve como clave del cache
    """
    return (market.lower(), symbol.upper(), timeframe.lower())


def get_from_cache(market: str, symbol: str, timeframe: str) -> Optional[list]:
    """
    Obtiene datos del cache si existen y no han expirado.
    
    ¿Cómo funciona?
    1. Construye la clave del cache
    2. Busca si existe en el diccionario
    3. Verifica si el cache aún es válido (no expirado)
    4. Si es válido, devuelve los datos
    5. Si expiró o no existe, devuelve None
    
    Args:
        market: Tipo de mercado
        symbol: Símbolo del activo
        timeframe: Período de tiempo
    
    Returns:
        Lista de velas OHLCV si existe cache válido, None en caso contrario
    """
    key = _make_cache_key(market, symbol, timeframe)
    
    # Verificar si existe en el cache
    if key not in _cache:
        return None
    
    cached_entry = _cache[key]
    now = datetime.now()
    
    # Verificar si el cache expiró
    if now > cached_entry["expires_at"]:
        # Cache expirado, eliminarlo
        del _cache[key]
        return None
    
    # Cache válido, devolver los datos
    return cached_entry["data"]


def save_to_cache(market: str, symbol: str, timeframe: str, data: list) -> None:
    """
    Guarda datos en el cache con TTL dinámico según el timeframe.
    
    TTL según timeframe:
    - 1d → 30 minutos
    - 1h → 10 minutos
    - Otros → 5 minutos (por defecto)
    
    Args:
        market: Tipo de mercado
        symbol: Símbolo del activo
        timeframe: Período de tiempo
        data: Lista de velas OHLCV a cachear
    """
    key = _make_cache_key(market, symbol, timeframe)
    now = datetime.now()
    duration = get_cache_duration(timeframe)
    expires_at = now + timedelta(seconds=duration)
    
    _cache[key] = {
        "data": data,
        "timestamp": now,
        "expires_at": expires_at
    }


def get_last_cache(market: str, symbol: str, timeframe: str) -> Optional[list]:
    """
    Obtiene el último cache disponible aunque haya expirado.
    
    Útil cuando Yahoo Finance devuelve error 429 (rate limit)
    y queremos usar datos antiguos en lugar de fallar.
    
    Args:
        market: Tipo de mercado
        symbol: Símbolo del activo
        timeframe: Período de tiempo
    
    Returns:
        Lista de velas OHLCV si existe (aunque expirado), None si nunca hubo cache
    """
    key = _make_cache_key(market, symbol, timeframe)
    
    if key not in _cache:
        return None
    
    # Devolver datos aunque estén expirados
    return _cache[key]["data"]


def clear_cache(market: Optional[str] = None, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> int:
    """
    Limpia el cache según los filtros especificados.
    
    Si no se especifican filtros, limpia todo el cache.
    
    Args:
        market: Si se especifica, solo limpia este mercado
        symbol: Si se especifica, solo limpia este símbolo
        timeframe: Si se especifica, solo limpia este timeframe
    
    Returns:
        Cantidad de entradas eliminadas
    """
    if market is None and symbol is None and timeframe is None:
        # Limpiar todo el cache
        count = len(_cache)
        _cache.clear()
        return count
    
    # Limpiar según filtros
    keys_to_remove = []
    for key in _cache.keys():
        cache_market, cache_symbol, cache_timeframe = key
        
        should_remove = True
        if market and cache_market != market.lower():
            should_remove = False
        if symbol and cache_symbol != symbol.upper():
            should_remove = False
        if timeframe and cache_timeframe != timeframe.lower():
            should_remove = False
        
        if should_remove:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del _cache[key]
    
    return len(keys_to_remove)


def get_cache_info() -> Dict:
    """
    Obtiene información sobre el estado del cache.
    
    Útil para debugging o monitoreo.
    
    Returns:
        Diccionario con información del cache:
        - total_entries: Cantidad de entradas en cache
        - expired_entries: Cantidad de entradas expiradas
        - valid_entries: Cantidad de entradas válidas
    """
    now = datetime.now()
    total = len(_cache)
    expired = sum(1 for entry in _cache.values() if now > entry["expires_at"])
    valid = total - expired
    
    return {
        "total_entries": total,
        "expired_entries": expired,
        "valid_entries": valid,
        "cache_ttl": CACHE_TTL
    }
