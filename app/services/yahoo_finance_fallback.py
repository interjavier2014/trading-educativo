"""
Sistema de fallback para cuando Yahoo Finance falla y no hay cache

Este módulo crea respuestas válidas cuando Yahoo Finance está
temporalmente no disponible, mejorando la UX en lugar de devolver errores.
"""

from typing import Dict
from app.services.yahoo_finance_cache import get_last_cache


class YahooFinanceFallback(Exception):
    """
    Excepción especial para indicar que se debe usar fallback.
    
    No es realmente un error, sino una señal para que el endpoint
    devuelva una respuesta válida con códigos especiales.
    """
    def __init__(self, market: str, symbol: str, timeframe: str):
        self.market = market
        self.symbol = symbol
        self.timeframe = timeframe
        super().__init__(f"Yahoo Finance no disponible para {symbol}")


def create_fallback_response(market: str, symbol: str, timeframe: str) -> YahooFinanceFallback:
    """
    Crea una excepción especial que indica usar respuesta de fallback.
    
    Esta excepción se captura en el servicio unificado y se convierte
    en una respuesta válida con códigos técnicos.
    
    Args:
        market: Tipo de mercado
        symbol: Símbolo del activo
        timeframe: Período de tiempo
    
    Returns:
        YahooFinanceFallback que será capturada y convertida en respuesta
    """
    return YahooFinanceFallback(market, symbol, timeframe)


def get_fallback_response_data(market: str, symbol: str, timeframe: str) -> Dict:
    """
    Genera datos de respuesta de fallback cuando Yahoo Finance no está disponible.
    
    Esta respuesta es válida pero indica que los datos no están disponibles
    temporalmente. El frontend puede mostrarlo de forma educativa.
    
    Args:
        market: Tipo de mercado
        symbol: Símbolo del activo
        timeframe: Período de tiempo
    
    Returns:
        Diccionario con estructura de respuesta válida pero con códigos de fallback
    """
    # Intentar obtener cualquier cache disponible como referencia
    last_cache = get_last_cache(market, symbol, timeframe)
    precio_referencia = None
    
    if last_cache and len(last_cache) > 0:
        # Usar precio del último cache como referencia
        precio_referencia = last_cache[-1]["close"]
    
    return {
        "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
        "message_code": "DATA_SOURCE_RATE_LIMIT",
        "confidence": "LOW",
        "precio_referencia": precio_referencia,
        "cache_disponible": last_cache is not None,
        "disclaimer_code": "DISCLAIMER"
    }
