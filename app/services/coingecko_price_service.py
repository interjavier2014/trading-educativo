"""
Servicio para obtener velas OHLC de criptomonedas desde CoinGecko

CoinGecko es el proveedor principal para producción porque Binance
devuelve 451 (restricted location) en Railway y otros entornos cloud.

API: https://api.coingecko.com/api/v3/coins/{id}/ohlc
Formato respuesta: [[timestamp_ms, open, high, low, close], ...]
Nota: CoinGecko OHLC NO incluye volumen (se usa 0).
"""

import httpx
from typing import List, Dict

# Mapeo símbolo Binance -> CoinGecko ID
SYMBOL_TO_COINGECKO_ID = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "SOLUSDT": "solana",
    "BNBUSDT": "binancecoin",
    "XRPUSDT": "ripple",
}

# Timeframe -> días para CoinGecko
# Valores permitidos: 1, 7, 14, 30, 90, 180, 365, max
# Granularidad: 1-2d=30min, 3-30d=4h, 31+d=4d
TIMEFRAME_TO_DAYS = {
    "1h": 1,   # 30-min candles (~48 velas para 1 día)
    "4h": 30,  # 4h candles (~180 velas)
    "1d": 90,  # 4-day candles (~22 velas)
}

BASE_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoError(Exception):
    """Error al obtener datos de CoinGecko (símbolo no soportado o API fallida)"""
    def __init__(self, symbol: str, message: str = ""):
        self.symbol = symbol
        super().__init__(message or f"Símbolo no soportado o datos no disponibles: {symbol}")


def _coingecko_id_from_symbol(symbol: str) -> str:
    """Obtiene el CoinGecko ID a partir del símbolo Binance."""
    s = symbol.upper().strip()
    if s not in SYMBOL_TO_COINGECKO_ID:
        raise CoinGeckoError(
            symbol,
            f"Símbolo '{symbol}' no soportado. "
            f"Símbolos válidos: {', '.join(SYMBOL_TO_COINGECKO_ID.keys())}"
        )
    return SYMBOL_TO_COINGECKO_ID[s]


def _convert_ohlc_to_vela(punto: List) -> Dict:
    """Convierte [timestamp, open, high, low, close] a formato interno OHLCV."""
    return {
        "timestamp": int(punto[0]),
        "open": float(punto[1]),
        "high": float(punto[2]),
        "low": float(punto[3]),
        "close": float(punto[4]),
        "volume": 0.0,  # CoinGecko OHLC no incluye volumen
    }


async def obtener_velas_coingecko(
    simbolo: str,
    timeframe: str = "1h",
    limite: int = 100,
) -> List[Dict]:
    """
    Obtiene velas OHLC desde CoinGecko.

    Args:
        simbolo: Símbolo Binance (ej: BTCUSDT, ETHUSDT)
        timeframe: 1h, 4h o 1d
        limite: Máximo de velas a devolver (post-recorte)

    Returns:
        Lista de velas con open, high, low, close, volume (0 si no existe)

    Raises:
        CoinGeckoError: Si el símbolo no es válido o la API falla
    """
    coingecko_id = _coingecko_id_from_symbol(simbolo)
    days = TIMEFRAME_TO_DAYS.get(timeframe, 2)
    url = f"{BASE_URL}/coins/{coingecko_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if not data or not isinstance(data, list):
        raise CoinGeckoError(simbolo, "Respuesta vacía o inválida de CoinGecko")

    velas = [_convert_ohlc_to_vela(p) for p in data]
    # Formato esperado por motor de patrones: open, high, low, close, volume
    resultado = [
        {
            "open": v["open"],
            "high": v["high"],
            "low": v["low"],
            "close": v["close"],
            "volume": v["volume"] if v["volume"] else 0.0,
        }
        for v in velas
    ]

    # Recortar al límite solicitado (últimas N velas)
    if len(resultado) > limite:
        resultado = resultado[-limite:]
    return resultado


def listar_simbolos_soportados() -> List[str]:
    """Devuelve la lista de símbolos soportados."""
    return list(SYMBOL_TO_COINGECKO_ID.keys())
