"""
Servicio para obtener velas reales de Bitcoin desde Binance

Este archivo se conecta a la API pública de Binance (no necesita cuenta)
y obtiene datos de precios de Bitcoin (BTCUSDT) en formato de velas OHLCV.

¿Qué es OHLCV?
- Open: Precio de apertura
- High: Precio más alto del período
- Low: Precio más bajo del período  
- Close: Precio de cierre
- Volume: Volumen de transacciones

Los datos se convierten al formato que usa nuestro motor de análisis de patrones.
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime


# URL base de la API pública de Binance
# Esta API es pública, NO requiere autenticación para obtener velas
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"


# Timeframes permitidos por Binance
# Son los períodos de tiempo que puedes pedir (1 minuto, 1 hora, 1 día, etc.)
TIMEFRAMES_PERMITIDOS = {
    "1m": "1 minuto",
    "3m": "3 minutos",
    "5m": "5 minutos",
    "15m": "15 minutos",
    "30m": "30 minutos",
    "1h": "1 hora",
    "2h": "2 horas",
    "4h": "4 horas",
    "6h": "6 horas",
    "8h": "8 horas",
    "12h": "12 horas",
    "1d": "1 día",
    "3d": "3 días",
    "1w": "1 semana",
    "1M": "1 mes",
}


def convertir_vela_binance_a_formato(vela_binance: List) -> Dict:
    """
    Convierte una vela de Binance a nuestro formato interno.
    
    Binance devuelve las velas como una lista con muchos datos:
    [Open time, Open, High, Low, Close, Volume, Close time, ...]
    
    Nosotros solo necesitamos: open, high, low, close, volume
    y los convertimos a números decimales (float).
    
    Args:
        vela_binance: Lista con los datos de la vela desde Binance
    
    Returns:
        Diccionario con el formato que usa nuestro motor de patrones:
        {"open": 50000.0, "high": 51000.0, "low": 49500.0, "close": 50500.0, "volume": 1234.56}
    """
    # Binance devuelve los precios como strings, los convertimos a float (números decimales)
    return {
        "open": float(vela_binance[1]),    # Posición 1: Precio de apertura
        "high": float(vela_binance[2]),    # Posición 2: Precio más alto
        "low": float(vela_binance[3]),     # Posición 3: Precio más bajo
        "close": float(vela_binance[4]),   # Posición 4: Precio de cierre
        "volume": float(vela_binance[5]),  # Posición 5: Volumen
    }


async def obtener_velas_bitcoin(
    timeframe: str = "1h",
    limite: int = 100,
    simbolo: str = "BTCUSDT"
) -> List[Dict]:
    """
    Obtiene velas reales de Bitcoin desde Binance.
    
    Esta función hace una petición a la API pública de Binance para obtener
    datos históricos de precios de Bitcoin. Los datos son REALES y ACTUALES.
    
    ¿Cómo funciona?
    1. Construye la URL con los parámetros necesarios
    2. Hace una petición HTTP GET a Binance
    3. Recibe los datos en formato JSON
    4. Convierte cada vela al formato que usa nuestro motor de análisis
    5. Devuelve una lista de velas listas para analizar
    
    Args:
        timeframe: Período de tiempo de cada vela (ej: "1h" = 1 hora, "1d" = 1 día)
                   Por defecto: "1h" (velas de 1 hora)
        limite: Cantidad de velas a obtener (máximo 1000, por defecto 100)
        simbolo: Par de trading (por defecto "BTCUSDT" = Bitcoin/USDT)
    
    Returns:
        Lista de diccionarios con velas OHLCV en nuestro formato:
        [
            {"open": 50000.0, "high": 51000.0, "low": 49500.0, "close": 50500.0, "volume": 1234.56},
            {"open": 50500.0, "high": 51500.0, "low": 50000.0, "close": 51000.0, "volume": 2345.67},
            ...
        ]
    
    Raises:
        ValueError: Si el timeframe no es válido
        Exception: Si hay un error al conectarse a Binance
    """
    # Validar que el timeframe sea válido
    if timeframe not in TIMEFRAMES_PERMITIDOS:
        timeframes_validos = ", ".join(TIMEFRAMES_PERMITIDOS.keys())
        raise ValueError(
            f'Timeframe "{timeframe}" no es válido. '
            f'Timeframes permitidos: {timeframes_validos}'
        )
    
    # Validar el límite (Binance acepta máximo 1000 velas)
    if limite < 1 or limite > 1000:
        raise ValueError("El límite debe estar entre 1 y 1000 velas")
    
    # Construir los parámetros para la petición
    # Estos son los "filtros" que le decimos a Binance qué datos queremos
    parametros = {
        "symbol": simbolo.upper(),  # Convertir a mayúsculas: "btcusdt" -> "BTCUSDT"
        "interval": timeframe,       # Período de tiempo (ej: "1h")
        "limit": limite,             # Cuántas velas queremos
    }
    
    try:
        # Hacer la petición HTTP GET a Binance
        # httpx es una librería para hacer peticiones HTTP de forma asíncrona
        # async/await permite que el servidor siga atendiendo otras peticiones
        # mientras espera la respuesta de Binance
        async with httpx.AsyncClient(timeout=10.0) as client:
            # client.get() hace la petición GET a la URL con los parámetros
            respuesta = await client.get(BINANCE_API_URL, params=parametros)
            
            # Verificar que la respuesta sea exitosa (código 200)
            # Si no es 200, significa que hubo un error
            respuesta.raise_for_status()
            
            # Convertir la respuesta JSON a una lista de Python
            velas_binance = respuesta.json()
            
            # Convertir cada vela de Binance a nuestro formato
            # Lista por comprensión: crea una nueva lista aplicando la función
            # convertir_vela_binance_a_formato() a cada elemento
            velas_convertidas = [
                convertir_vela_binance_a_formato(vela)
                for vela in velas_binance
            ]
            
            return velas_convertidas
    
    except httpx.TimeoutException:
        # Si Binance tarda demasiado en responder (más de 10 segundos)
        raise Exception(
            "Tiempo de espera agotado al conectarse a Binance. "
            "Intenta de nuevo más tarde."
        )
    
    except httpx.HTTPStatusError as e:
        # Si Binance devuelve un error HTTP (ej: 400, 404, 500)
        error_mensaje = f"Error al obtener datos de Binance: {e.response.status_code}"
        try:
            # Binance a veces incluye un mensaje de error más detallado
            error_detalle = e.response.json()
            if "msg" in error_detalle:
                error_mensaje += f" - {error_detalle['msg']}"
        except:
            pass
        raise Exception(error_mensaje)
    
    except Exception as e:
        # Cualquier otro error inesperado
        raise Exception(f"Error inesperado al obtener datos de Binance: {str(e)}")


async def obtener_velas_bitcoin_formato_analisis(
    timeframe: str = "1h",
    limite: int = 100
) -> Dict:
    """
    Obtiene velas de Bitcoin y las prepara para análisis.
    
    Esta es una función de conveniencia que obtiene las velas y las estructura
    en un formato más completo con información adicional.
    
    Útil cuando quieres obtener datos y mostrarlos con información extra,
    como la fecha de la última vela o estadísticas básicas.
    
    Args:
        timeframe: Período de tiempo (por defecto "1h")
        limite: Cantidad de velas (por defecto 100)
    
    Returns:
        Diccionario con:
        {
            "velas": [...],  # Lista de velas OHLCV
            "total": 100,    # Cantidad de velas
            "timeframe": "1h",
            "simbolo": "BTCUSDT",
            "ultima_vela": {...}  # Última vela (más reciente)
        }
    """
    # Obtener las velas
    velas = await obtener_velas_bitcoin(timeframe=timeframe, limite=limite)
    
    # Las velas de Binance vienen ordenadas desde la más antigua hasta la más reciente
    # La última vela es la más reciente
    ultima_vela = velas[-1] if velas else None
    
    return {
        "velas": velas,
        "total": len(velas),
        "timeframe": timeframe,
        "simbolo": "BTCUSDT",
        "ultima_vela": ultima_vela,
        "descripcion": f"{len(velas)} velas de Bitcoin (BTCUSDT) con timeframe {timeframe}",
    }


# Ejemplo de uso (solo para pruebas, no se ejecuta cuando importas el módulo)
if __name__ == "__main__":
    """
    Este bloque solo se ejecuta si ejecutas este archivo directamente:
    python app/services/bitcoin_price_service.py
    
    Es útil para probar que el servicio funciona correctamente.
    """
    import asyncio
    
    async def probar_servicio():
        """Función de prueba para verificar que el servicio funciona"""
        print("=" * 70)
        print("PRUEBA DEL SERVICIO DE PRECIOS DE BITCOIN")
        print("=" * 70)
        print()
        
        try:
            # Obtener las últimas 10 velas de 1 hora
            print("Obteniendo 10 velas de Bitcoin (BTCUSDT) con timeframe 1h...")
            velas = await obtener_velas_bitcoin(timeframe="1h", limite=10)
            
            print(f"\n✅ Se obtuvieron {len(velas)} velas correctamente")
            print()
            print("Primeras 3 velas (más antiguas):")
            for i, vela in enumerate(velas[:3], 1):
                print(f"  Vela {i}:")
                print(f"    Open:  ${vela['open']:,.2f}")
                print(f"    High:  ${vela['high']:,.2f}")
                print(f"    Low:   ${vela['low']:,.2f}")
                print(f"    Close: ${vela['close']:,.2f}")
                print(f"    Volume: {vela['volume']:,.2f}")
                print()
            
            if len(velas) > 3:
                print("Última vela (más reciente):")
                ultima = velas[-1]
                print(f"  Open:  ${ultima['open']:,.2f}")
                print(f"  High:  ${ultima['high']:,.2f}")
                print(f"  Low:   ${ultima['low']:,.2f}")
                print(f"  Close: ${ultima['close']:,.2f}")
                print(f"  Volume: {ultima['volume']:,.2f}")
                print()
            
            # Mostrar el formato completo
            print("=" * 70)
            print("Formato completo (útil para análisis):")
            resultado_completo = await obtener_velas_bitcoin_formato_analisis(
                timeframe="1h", limite=5
            )
            print(f"  Total de velas: {resultado_completo['total']}")
            print(f"  Timeframe: {resultado_completo['timeframe']}")
            print(f"  Símbolo: {resultado_completo['simbolo']}")
            print(f"  Última vela - Close: ${resultado_completo['ultima_vela']['close']:,.2f}")
        
        except ValueError as e:
            # Error de validación (ej: timeframe inválido)
            print(f"❌ Error de validación: {e}")
        
        except Exception as e:
            # Error al conectarse a Binance
            print(f"❌ Error al obtener datos: {e}")
            print()
            print("Posibles causas:")
            print("  - No tienes conexión a internet")
            print("  - Binance está temporalmente no disponible")
            print("  - El símbolo o timeframe no es válido")
    
    # Ejecutar la función de prueba
    # asyncio.run() es necesario porque usamos funciones async/await
    asyncio.run(probar_servicio())
