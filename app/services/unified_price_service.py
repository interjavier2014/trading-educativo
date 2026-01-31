"""
Servicio unificado para obtener velas de diferentes mercados

Este servicio actúa como un punto de entrada único que delega
la obtención de datos al servicio apropiado según el mercado.

Arquitectura:
- crypto → bitcoin_price_service (Binance)
- stocks/cedears → yahoo_finance_service (Yahoo Finance)
"""

from typing import List, Dict
from app.services.bitcoin_price_service import obtener_velas_bitcoin
from app.services.yahoo_finance_service import obtener_velas_yahoo_finance
from app.services.yahoo_finance_fallback import (
    YahooFinanceFallback,
    get_fallback_response_data
)


async def obtener_velas(
    market: str,
    symbol: str,
    timeframe: str,
    limite: int = 100
) -> List[Dict]:
    """
    Obtiene velas OHLCV de cualquier mercado (crypto, stocks, cedears).
    
    Esta función unifica el acceso a datos de diferentes mercados,
    delegando al servicio apropiado según el tipo de mercado.
    
    Args:
        market: Tipo de mercado ("crypto", "stocks", "cedears")
        symbol: Símbolo del activo (ej: "BTCUSDT", "AAPL", "AAPL.BA")
        timeframe: Período de tiempo (ej: "1h", "4h", "1d")
        limite: Cantidad de velas a obtener
    
    Returns:
        Lista de diccionarios con velas OHLCV en formato unificado
    
    Raises:
        ValueError: Si el mercado no es válido
        Exception: Error al obtener datos del servicio correspondiente
    """
    # Validar mercado
    mercados_validos = ["crypto", "stocks", "cedears"]
    if market.lower() not in mercados_validos:
        raise ValueError(
            f'Mercado "{market}" no es válido. '
            f'Mercados permitidos: {", ".join(mercados_validos)}'
        )
    
    market_lower = market.lower()
    
    # Delegar al servicio apropiado según el mercado
    if market_lower == "crypto":
        # Mercado de criptomonedas: usar Binance
        return await obtener_velas_bitcoin(
            timeframe=timeframe,
            limite=limite,
            simbolo=symbol.upper()
        )
    
    elif market_lower in ["stocks", "cedears"]:
        # Mercado de acciones o CEDEARs: usar Yahoo Finance
        # Nota: CEDEARs se identifican con sufijo .BA (ej: AAPL.BA)
        # Pasamos 'market' para que el cache funcione correctamente
        try:
            return await obtener_velas_yahoo_finance(
                symbol=symbol.upper(),
                timeframe=timeframe,
                limite=limite,
                market=market_lower  # Necesario para el cache (stocks o cedears)
            )
        except YahooFinanceFallback as fallback:
            # Yahoo Finance no disponible y no hay cache
            # Propagar la excepción para que el endpoint la maneje
            raise fallback
        except Exception as e:
            # Cualquier otro error de Yahoo Finance también debe convertirse en fallback
            # Esto asegura que NUNCA se devuelva un error 500 por problemas de Yahoo
            raise YahooFinanceFallback(market_lower, symbol.upper(), timeframe)
    
    else:
        # No debería llegar aquí por la validación anterior, pero por seguridad
        raise ValueError(f"Mercado '{market}' no está implementado")


async def obtener_info_activo(
    market: str,
    symbol: str
) -> Dict:
    """
    Obtiene información básica sobre un activo según su mercado.
    
    Útil para validar que un símbolo existe y obtener metadatos.
    
    Args:
        market: Tipo de mercado
        symbol: Símbolo del activo
    
    Returns:
        Diccionario con información del activo
    """
    # Por ahora, obtener una vela es suficiente para validar
    # En el futuro se puede expandir para obtener más metadatos
    velas = await obtener_velas(market, symbol, timeframe="1d", limite=1)
    
    if not velas:
        raise ValueError(f"No se encontraron datos para {symbol} en el mercado {market}")
    
    ultima_vela = velas[-1]
    
    return {
        "market": market.lower(),
        "symbol": symbol.upper(),
        "precio_actual": ultima_vela["close"],
        "es_valido": True
    }
