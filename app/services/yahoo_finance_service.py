"""
Servicio para obtener velas de acciones y CEDEARs desde Yahoo Finance

Este servicio se conecta a Yahoo Finance para obtener datos de precios
de acciones (stocks) y CEDEARs en formato OHLCV.

Nota: Yahoo Finance es una API pública y gratuita para datos históricos.
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.services.yahoo_finance_cache import (
    get_from_cache,
    save_to_cache,
    get_last_cache
)


# URL base de Yahoo Finance API
YAHOO_FINANCE_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"


async def obtener_velas_yahoo_finance(
    symbol: str,
    timeframe: str = "1d",
    limite: int = 100,
    market: str = "stocks"
) -> List[Dict]:
    """
    Obtiene velas de acciones o CEDEARs desde Yahoo Finance con cache en memoria.
    
    Esta función usa un sistema de cache para evitar llamadas repetidas a Yahoo Finance.
    El cache dura 5 minutos y solo se aplica a stocks y cedears.
    
    Flujo del cache:
    1. Verifica si hay cache válido (menos de 5 minutos)
    2. Si existe, devuelve datos del cache (no llama a Yahoo)
    3. Si no existe, llama a Yahoo Finance
    4. Si Yahoo responde bien, guarda en cache
    5. Si Yahoo devuelve error 429 (rate limit), usa cache aunque esté expirado
    
    Args:
        symbol: Símbolo del activo (ej: "AAPL" para Apple, "AAPL.BA" para CEDEAR)
        timeframe: Período de tiempo (ej: "1h", "4h", "1d")
        limite: Cantidad de velas a obtener (máximo recomendado: 250)
        market: Tipo de mercado ("stocks" o "cedears") - usado para el cache
    
    Returns:
        Lista de diccionarios con velas OHLCV en nuestro formato
    
    Raises:
        ValueError: Si el timeframe no es válido o el símbolo es inválido
        Exception: Si hay un error al conectarse a Yahoo Finance
    """
    # Paso 1: Verificar cache antes de llamar a Yahoo Finance
    cached_data = get_from_cache(market, symbol, timeframe)
    if cached_data is not None:
        # Cache válido encontrado, devolver sin llamar a Yahoo
        # Limitamos al número de velas solicitadas
        return cached_data[:limite] if limite < len(cached_data) else cached_data
    
    # Mapeo de timeframes a intervalos de Yahoo Finance
    # Yahoo Finance usa intervalos específicos diferentes a Binance
    timeframe_mapping = {
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1wk",
        "1M": "1mo"
    }
    
    if timeframe not in timeframe_mapping:
        raise ValueError(
            f'Timeframe "{timeframe}" no es válido para Yahoo Finance. '
            f'Valores permitidos: {list(timeframe_mapping.keys())}'
        )
    
    # Convertir timeframe al formato de Yahoo Finance
    interval = timeframe_mapping[timeframe]
    
    # Calcular el rango de fechas necesario
    # Yahoo Finance requiere un rango de fechas (start/end)
    end_date = datetime.now()
    
    # Estimar cuántos días atrás necesitamos basado en el timeframe y límite
    if timeframe == "1h":
        days_back = max(30, limite // 24 + 7)  # 1 vela/hora, agregar buffer
    elif timeframe == "4h":
        days_back = max(60, limite // 6 + 14)  # 1 vela/4 horas
    elif timeframe == "1d":
        days_back = max(365, limite + 30)  # 1 vela/día
    else:
        days_back = 365
    
    start_date = end_date - timedelta(days=days_back)
    
    # Construir los parámetros para la petición
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "period1": int(start_date.timestamp()),
        "period2": int(end_date.timestamp()),
        "events": "history",
        "includeAdjustedClose": "true"
    }
    
    try:
        # Hacer la petición HTTP GET a Yahoo Finance
        async with httpx.AsyncClient(timeout=15.0) as client:
            url = f"{YAHOO_FINANCE_API_URL}{symbol.upper()}"
            respuesta = await client.get(url, params=params)
            
            respuesta.raise_for_status()
            data = respuesta.json()
            
            # Yahoo Finance devuelve datos en una estructura específica
            chart_result = data.get("chart", {}).get("result", [])
            
            if not chart_result or len(chart_result) == 0:
                raise Exception(f"No se encontraron datos para el símbolo {symbol}")
            
            result = chart_result[0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [])
            
            if not indicators or len(indicators) == 0:
                raise Exception(f"No se encontraron datos de precios para {symbol}")
            
            quote = indicators[0]
            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            closes = quote.get("close", [])
            volumes = quote.get("volume", [])
            
            # Convertir los datos a nuestro formato OHLCV
            velas = []
            data_count = len(timestamps)
            
            # Tomar solo las últimas 'limite' velas
            start_index = max(0, data_count - limite)
            
            for i in range(start_index, data_count):
                # Yahoo Finance puede devolver None para algunos valores
                # Si hay datos faltantes, los saltamos
                if (opens[i] is not None and highs[i] is not None and 
                    lows[i] is not None and closes[i] is not None):
                    velas.append({
                        "open": float(opens[i]),
                        "high": float(highs[i]),
                        "low": float(lows[i]),
                        "close": float(closes[i]),
                        "volume": float(volumes[i]) if volumes[i] is not None else 0.0
                    })
            
            if not velas:
                raise Exception(f"No se pudieron extraer velas válidas para {symbol}")
            
            # Paso 2: Guardar en cache después de obtener datos exitosamente
            save_to_cache(market, symbol, timeframe, velas)
            
            return velas
    
    except httpx.TimeoutException:
        # Timeout: intentar usar cache aunque esté expirado
        last_cache = get_last_cache(market, symbol, timeframe)
        if last_cache is not None:
            return last_cache[:limite] if limite < len(last_cache) else last_cache
        else:
            # No hay cache - lanzar fallback
            from app.services.yahoo_finance_fallback import YahooFinanceFallback
            raise YahooFinanceFallback(market, symbol, timeframe)
    
    except httpx.HTTPStatusError as e:
        # Cualquier error HTTP de Yahoo Finance (429, 404, 500, etc.)
        # Primero intentar usar cache aunque esté expirado
        last_cache = get_last_cache(market, symbol, timeframe)
        if last_cache is not None:
            # Hay cache disponible (aunque expirado), usarlo
            return last_cache[:limite] if limite < len(last_cache) else last_cache
        else:
            # No hay cache disponible - lanzar excepción especial de fallback
            # Esto permite que el endpoint maneje el fallback de forma elegante
            from app.services.yahoo_finance_fallback import YahooFinanceFallback
            raise YahooFinanceFallback(market, symbol, timeframe)
    
    except Exception as e:
        # Cualquier otro error de Yahoo Finance
        # No capturar YahooFinanceFallback aquí - debe propagarse
        from app.services.yahoo_finance_fallback import YahooFinanceFallback
        if isinstance(e, YahooFinanceFallback):
            raise  # Re-lanzar sin modificar
        
        # Para cualquier otro error, intentar cache y luego fallback
        last_cache = get_last_cache(market, symbol, timeframe)
        if last_cache is not None:
            return last_cache[:limite] if limite < len(last_cache) else last_cache
        else:
            # No hay cache - lanzar fallback
            raise YahooFinanceFallback(market, symbol, timeframe)


# Ejemplo de uso (solo para pruebas)
if __name__ == "__main__":
    import asyncio
    
    async def probar_servicio():
        print("=" * 70)
        print("PRUEBA DEL SERVICIO DE YAHOO FINANCE")
        print("=" * 70)
        print()
        
        try:
            # Obtener velas de Apple (AAPL)
            print("Obteniendo velas de Apple (AAPL) con timeframe 1d...")
            velas = await obtener_velas_yahoo_finance(symbol="AAPL", timeframe="1d", limite=10)
            
            print(f"\n✅ Se obtuvieron {len(velas)} velas correctamente")
            print()
            print("Últimas 3 velas:")
            for i, vela in enumerate(velas[-3:], 1):
                print(f"  Vela {i}:")
                print(f"    Open:  ${vela['open']:,.2f}")
                print(f"    High:  ${vela['high']:,.2f}")
                print(f"    Low:   ${vela['low']:,.2f}")
                print(f"    Close: ${vela['close']:,.2f}")
                print(f"    Volume: {vela['volume']:,.0f}")
                print()
        
        except ValueError as e:
            print(f"❌ Error de validación: {e}")
        
        except Exception as e:
            print(f"❌ Error al obtener datos: {e}")
    
    asyncio.run(probar_servicio())
