"""
Servicio unificado para obtener velas de diferentes mercados

Este servicio actúa como un punto de entrada único que delega
la obtención de datos al servicio apropiado según el mercado.

Arquitectura:
- crypto → CoinGecko (primario) / Binance (fallback si CoinGecko falla)
- stocks/cedears → Yahoo Finance
"""

from typing import List, Dict
from app.services.coingecko_price_service import (
    obtener_velas_coingecko,
    CoinGeckoError,
)
from app.services.bitcoin_price_service import obtener_velas_bitcoin
from app.services.yahoo_finance_service import obtener_velas_yahoo_finance
from app.services.yahoo_finance_fallback import (
    YahooFinanceFallback,
    get_fallback_response_data,
)
from app.services.crypto_fallback import CryptoDataFallback


async def obtener_velas(
    market: str,
    symbol: str,
    timeframe: str,
    limite: int = 100
) -> List[Dict]:
    """
    Obtiene velas OHLCV de cualquier mercado (crypto, stocks, cedears).

    Para crypto:
    - Primero intenta CoinGecko (funciona en Railway y entornos restringidos)
    - Si CoinGecko falla, intenta Binance
    - Si Binance falla (451, timeout, etc.), devuelve fallback educativo (no 500)

    Args:
        market: Tipo de mercado ("crypto", "stocks", "cedears")
        symbol: Símbolo del activo (ej: "BTCUSDT", "AAPL", "AAPL.BA")
        timeframe: Período de tiempo (ej: "1h", "4h", "1d")
        limite: Cantidad de velas a obtener

    Returns:
        Lista de diccionarios con velas OHLCV en formato unificado

    Raises:
        CryptoDataFallback: Si ambas fuentes crypto fallan (CoinGecko y Binance)
        YahooFinanceFallback: Si Yahoo Finance falla y no hay cache
    """
    mercados_validos = ["crypto", "stocks", "cedears"]
    if market.lower() not in mercados_validos:
        raise ValueError(
            f'Mercado "{market}" no es válido. '
            f'Mercados permitidos: {", ".join(mercados_validos)}'
        )

    market_lower = market.lower()

    if market_lower == "crypto":
        # 1. Intentar CoinGecko (primario, funciona en Railway)
        try:
            return await obtener_velas_coingecko(
                simbolo=symbol.upper(),
                timeframe=timeframe,
                limite=limite,
            )
        except CoinGeckoError:
            # Símbolo no soportado o error de CoinGecko
            # Intentar Binance por si el símbolo existe allí
            pass
        except Exception:
            # Error de red/API CoinGecko -> intentar Binance
            pass

        # 2. Fallback a Binance
        try:
            return await obtener_velas_bitcoin(
                timeframe=timeframe,
                limite=limite,
                simbolo=symbol.upper(),
            )
        except Exception:
            # Binance falló (451, timeout, etc.)
            raise CryptoDataFallback(symbol.upper(), timeframe)

    elif market_lower in ["stocks", "cedears"]:
        try:
            return await obtener_velas_yahoo_finance(
                symbol=symbol.upper(),
                timeframe=timeframe,
                limite=limite,
                market=market_lower,
            )
        except YahooFinanceFallback as fallback:
            raise fallback
        except Exception:
            raise YahooFinanceFallback(market_lower, symbol.upper(), timeframe)

    raise ValueError(f"Mercado '{market}' no está implementado")


async def obtener_info_activo(
    market: str,
    symbol: str
) -> Dict:
    """
    Obtiene información básica sobre un activo según su mercado.
    """
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
