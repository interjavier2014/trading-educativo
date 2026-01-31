"""
Warm-up del cache al iniciar la aplicación

Este módulo precarga datos populares en el cache para mejorar
la experiencia del usuario y reducir llamadas a Yahoo Finance
al inicio de la aplicación.
"""

import asyncio
from typing import List, Dict
from app.services.yahoo_finance_service import obtener_velas_yahoo_finance
from app.services.yahoo_finance_cache import get_cache_info


# Activos a precargar al iniciar la aplicación
WARMUP_ASSETS = [
    {"market": "stocks", "symbol": "AAPL", "timeframe": "1d"},   # Apple
    {"market": "stocks", "symbol": "TSLA", "timeframe": "1d"},   # Tesla
    {"market": "stocks", "symbol": "MSFT", "timeframe": "1d"},   # Microsoft
    {"market": "cedears", "symbol": "AAPL.BA", "timeframe": "1d"},  # Apple CEDEAR
]


async def warmup_cache_async() -> Dict:
    """
    Precarga el cache con activos populares de forma asíncrona.
    
    ¿Qué hace?
    1. Para cada activo en WARMUP_ASSETS
    2. Intenta obtener datos de Yahoo Finance
    3. Guarda en cache automáticamente (el servicio lo hace)
    4. Si falla, no rompe el inicio (solo registra el error)
    
    Returns:
        Diccionario con estadísticas del warm-up:
        {
            "total": 4,
            "exitosos": 3,
            "fallidos": 1,
            "detalles": [...]
        }
    """
    resultados = {
        "total": len(WARMUP_ASSETS),
        "exitosos": 0,
        "fallidos": 0,
        "detalles": []
    }
    
    for asset in WARMUP_ASSETS:
        market = asset["market"]
        symbol = asset["symbol"]
        timeframe = asset["timeframe"]
        
        try:
            # Obtener velas (se cachean automáticamente en el servicio)
            await obtener_velas_yahoo_finance(
                symbol=symbol,
                timeframe=timeframe,
                limite=100,
                market=market
            )
            
            resultados["exitosos"] += 1
            resultados["detalles"].append({
                "asset": symbol,
                "market": market,
                "status": "success"
            })
        
        except Exception as e:
            # No romper el inicio si falla un activo
            # Solo registrar el error
            resultados["fallidos"] += 1
            resultados["detalles"].append({
                "asset": symbol,
                "market": market,
                "status": "failed",
                "error": str(e)
            })
    
    return resultados


def warmup_cache() -> Dict:
    """
    Precarga el cache de forma síncrona.
    
    Wrapper para ejecutar warmup_cache_async() desde código síncrono.
    
    Returns:
        Estadísticas del warm-up
    """
    try:
        # Crear nuevo event loop si no existe
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop corriendo, crear tarea
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, warmup_cache_async())
                return future.result()
        else:
            return loop.run_until_complete(warmup_cache_async())
    except RuntimeError:
        # No hay event loop, crear uno nuevo
        return asyncio.run(warmup_cache_async())


async def warmup_cache_background() -> None:
    """
    Precarga el cache en segundo plano sin bloquear el inicio.
    
    Útil para FastAPI startup events donde queremos que la app
    inicie rápido y el warm-up se haga en paralelo.
    """
    # Ejecutar warm-up en segundo plano
    # No esperar por el resultado (fire and forget)
    asyncio.create_task(warmup_cache_async())
