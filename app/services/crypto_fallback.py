"""
Sistema de fallback para cuando las fuentes de datos crypto fallan

Cuando CoinGecko y Binance no están disponibles (451, timeout, rate limit, etc.),
devolvemos una respuesta educativa válida en lugar de 500.
"""

from typing import Dict


class CryptoDataFallback(Exception):
    """
    Excepción para indicar que se debe usar fallback educativo.
    No es un error técnico, sino una señal para devolver JSON válido.
    """
    def __init__(self, symbol: str, timeframe: str, message: str = ""):
        self.symbol = symbol
        self.timeframe = timeframe
        super().__init__(message or f"Datos crypto no disponibles para {symbol}")


def get_crypto_fallback_response_data(symbol: str, timeframe: str) -> Dict:
    """
    Genera datos de respuesta de fallback cuando ninguna fuente crypto está disponible.

    Respuesta educativa con códigos técnicos para el frontend.

    Args:
        symbol: Símbolo del activo
        timeframe: Período de tiempo

    Returns:
        Diccionario con estructura de respuesta válida y códigos de fallback
    """
    return {
        "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
        "message_code": "DATA_SOURCE_ERROR",
        "confidence": "LOW",
        "precio_referencia": None,
        "disclaimer_code": "DISCLAIMER",
    }
