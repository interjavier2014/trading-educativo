"""
Endpoints para análisis técnico educativo

Aquí definiremos las rutas que combinan todo:
- Datos de precios
- Patrones detectados
- Análisis de tendencia
- Señal educativa completa

Ejemplo: /api/analysis/crypto/btc-usdt?interval=1h
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict
from app.services.candlestick_patterns import analizar_patrones, EJEMPLO_VELAS
from app.services.bitcoin_price_service import obtener_velas_bitcoin
from app.services.unified_price_service import obtener_velas
from app.services.yahoo_finance_fallback import (
    YahooFinanceFallback,
    get_fallback_response_data
)
from app.services.crypto_fallback import (
    CryptoDataFallback,
    get_crypto_fallback_response_data
)
from app.schemas.patterns import (
    AnalisisPatronesRequest,
    AnalisisPatronesResponse,
    AnalisisUnificadoResponse,
    PatronDetectadoResponse,
    VelaSchema
)

router = APIRouter(prefix="/api/analysis", tags=["Análisis Educativo"])

# Códigos técnicos para tendencias (i18n)
TREND_BULLISH = "BULLISH"
TREND_BEARISH = "BEARISH"
TREND_SIDEWAYS = "SIDEWAYS"

# Código de aviso legal
DISCLAIMER_CODE = "DISCLAIMER"


@router.get("/health")
async def analysis_health():
    """Verifica que el módulo de análisis funciona"""
    return {"status": "analysis module ready"}


@router.post(
    "/patrones",
    response_model=AnalisisPatronesResponse,
    summary="Analizar patrones de velas japonesas",
    description=(
        "Este endpoint analiza una lista de velas OHLCV y detecta patrones "
        "básicos de velas japonesas como Martillo, Doji y Envolvente Alcista. "
        "El análisis es puramente educativo y NO constituye una recomendación "
        "de inversión."
    )
)
async def analizar_patrones_velas(
    request: AnalisisPatronesRequest = Body(
        ...,
        description="Lista de velas OHLCV para analizar",
        example={
            "velas": [
                {
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 104.0,
                    "volume": 1000
                },
                {
                    "open": 104.0,
                    "high": 105.0,
                    "low": 98.0,
                    "close": 103.5,
                    "volume": 1200
                }
            ]
        }
    )
):
    """
    Analiza patrones de velas japonesas en una lista de velas OHLCV.
    
    **¿Qué hace este endpoint?**
    
    1. Recibe una lista de velas (datos OHLCV)
    2. Analiza cada vela individualmente para detectar patrones
    3. Analiza pares de velas para detectar patrones de múltiples velas
    4. Devuelve todos los patrones encontrados con explicaciones educativas
    
    **Patrones que detecta:**
    - **Martillo**: Cuerpo pequeño arriba, sombra inferior larga (señal alcista potencial)
    - **Doji**: Open y close casi iguales (indecisión del mercado)
    - **Envolvente Alcista**: Vela alcista grande que envuelve una vela bajista pequeña
    
    **Formato de respuesta:**
    - Lista de patrones detectados
    - Explicación educativa de cada patrón
    - Datos técnicos del patrón
    - Avisos legales y recordatorios educativos
    
    **IMPORTANTE:**
    - Este análisis es solo educativo
    - NO es una recomendación de compra o venta
    - Siempre confirma con múltiples indicadores
    - Consulta con profesionales antes de tomar decisiones financieras
    
    **Ejemplo de uso:**
    ```json
    POST /api/analysis/patrones
    {
        "velas": [
            {"open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
            {"open": 104, "high": 105, "low": 98, "close": 103.5, "volume": 1200}
        ]
    }
    ```
    """
    try:
        # Convertir los schemas de Pydantic a diccionarios simples
        # para que funcionen con nuestro servicio de análisis
        velas_dict = [vela.model_dump() for vela in request.velas]
        
        # Ejecutar el análisis de patrones
        resultado = analizar_patrones(velas_dict)
        
        # Construir la respuesta con códigos técnicos (i18n para frontend)
        respuesta = {
            "total_velas_analizadas": resultado["total_velas_analizadas"],
            "patrones_detectados": resultado["patrones_detectados"],
            "patrones": [
                PatronDetectadoResponse(**patron) 
                for patron in resultado["patrones"]
            ],
            "disclaimer_code": resultado.get("disclaimer_code", "DISCLAIMER")
        }
        
        return AnalisisPatronesResponse(**respuesta)
    
    except Exception as e:
        # Si hay un error, devolver un mensaje claro
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar patrones: {str(e)}"
        )


@router.get(
    "/patrones/ejemplo",
    response_model=AnalisisPatronesResponse,
    summary="Ver análisis de ejemplo con velas precargadas",
    description=(
        "Este endpoint muestra un análisis de ejemplo usando velas precargadas. "
        "Útil para entender cómo funciona el análisis sin tener que enviar datos."
    )
)
async def analizar_patrones_ejemplo():
    """
    Analiza patrones usando velas de ejemplo precargadas.
    
    **¿Qué hace este endpoint?**
    
    - Usa datos de ejemplo ya incluidos en el sistema
    - Ejecuta el análisis completo
    - Devuelve el resultado como ejemplo educativo
    
    **Útil para:**
    - Entender cómo funciona el análisis
    - Ver qué formato tiene la respuesta
    - Probar el endpoint sin tener que preparar datos
    
    **No requiere parámetros:** Solo visita la URL y obtienes el análisis.
    
    **Ejemplo de uso:**
    ```
    GET /api/analysis/patrones/ejemplo
    ```
    """
    try:
        # Usar las velas de ejemplo del servicio
        resultado = analizar_patrones(EJEMPLO_VELAS)
        
        # Construir la respuesta con códigos técnicos (i18n para frontend)
        respuesta = {
            "total_velas_analizadas": resultado["total_velas_analizadas"],
            "patrones_detectados": resultado["patrones_detectados"],
            "patrones": [
                PatronDetectadoResponse(**patron) 
                for patron in resultado["patrones"]
            ],
            "disclaimer_code": resultado.get("disclaimer_code", "DISCLAIMER")
        }
        
        return AnalisisPatronesResponse(**respuesta)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar patrones de ejemplo: {str(e)}"
        )


@router.get(
    "/bitcoin",
    summary="Analizar patrones de Bitcoin con datos reales",
    description=(
        "Este endpoint obtiene velas reales de Bitcoin (BTCUSDT) desde Binance "
        "y analiza patrones de velas japonesas. Los datos son en tiempo real "
        "y el análisis es puramente educativo."
    )
)
async def analizar_bitcoin(
    timeframe: str = Query(
        default="1h",
        description="Período de tiempo de cada vela (1m, 5m, 15m, 1h, 4h, 1d, etc.)",
        example="1h"
    ),
    limite: int = Query(
        default=100,
        description="Cantidad de velas a analizar (máximo 1000)",
        ge=1,
        le=1000,
        example=100
    )
):
    """
    Analiza patrones de velas japonesas en Bitcoin usando datos reales de Binance.
    
    **¿Qué hace este endpoint?**
    
    1. Obtiene velas reales de Bitcoin (BTCUSDT) desde la API pública de Binance
    2. Convierte los datos al formato que usa nuestro motor de análisis
    3. Ejecuta el análisis de patrones de velas japonesas
    4. Devuelve un análisis educativo completo con explicaciones
    
    **Parámetros opcionales:**
    - `timeframe`: Período de cada vela (por defecto: "1h" = 1 hora)
      - Ejemplos: "1m", "5m", "15m", "1h", "4h", "1d", "1w"
    - `limite`: Cantidad de velas a analizar (por defecto: 100, máximo: 1000)
    
    **Ejemplos de uso:**
    ```
    # Análisis con valores por defecto (últimas 100 velas de 1 hora)
    GET /api/analysis/bitcoin
    
    # Análisis de velas de 1 minuto (últimas 60 = última hora)
    GET /api/analysis/bitcoin?timeframe=1m&limite=60
    
    # Análisis de velas diarias (últimos 30 días)
    GET /api/analysis/bitcoin?timeframe=1d&limite=30
    
    # Análisis de velas de 4 horas (últimas 50 = últimos ~8 días)
    GET /api/analysis/bitcoin?timeframe=4h&limite=50
    ```
    
    **Respuesta incluye:**
    - Activo analizado (BTCUSDT)
    - Timeframe usado
    - Precio actual de Bitcoin
    - Patrones detectados con explicaciones
    - Contexto general del mercado
    - Aviso legal completo
    
    **IMPORTANTE:**
    - Los datos son REALES y en TIEMPO REAL desde Binance
    - El análisis es solo educativo, NO es una recomendación de inversión
    - Requiere conexión a internet para obtener datos de Binance
    """
    try:
        # Paso 1: Obtener velas reales de Bitcoin desde Binance
        # Esta función hace una petición HTTP a Binance y obtiene los datos más recientes
        velas = await obtener_velas_bitcoin(
            timeframe=timeframe,
            limite=limite,
            simbolo="BTCUSDT"
        )
        
        # Verificar que se obtuvieron velas
        if not velas or len(velas) == 0:
            raise HTTPException(
                status_code=500,
                detail="No se pudieron obtener velas de Bitcoin. Intenta de nuevo más tarde."
            )
        
        # Paso 2: Ejecutar el análisis de patrones
        # Esta función analiza las velas y detecta patrones como Martillo, Doji, etc.
        resultado_analisis = analizar_patrones(velas)
        
        # Paso 3: Obtener información de contexto
        # La última vela es la más reciente (Binance ordena desde antigua a reciente)
        ultima_vela = velas[-1]
        primera_vela = velas[0]
        
        # Calcular cambio de precio durante el período analizado
        cambio_precio = ultima_vela["close"] - primera_vela["open"]
        cambio_porcentual = (cambio_precio / primera_vela["open"]) * 100
        
        # Determinar tendencia general (códigos técnicos para i18n)
        if cambio_porcentual > 2:
            trend_code = TREND_BULLISH
        elif cambio_porcentual < -2:
            trend_code = TREND_BEARISH
        else:
            trend_code = TREND_SIDEWAYS
        
        # Paso 4: Construir la respuesta con códigos técnicos (i18n para frontend)
        # Los patrones ya vienen con posicion y pattern_index del servicio
        respuesta = {
            "activo": "BTCUSDT",
            "timeframe": timeframe,
            "precio_actual": round(ultima_vela["close"], 2),
            "precio_apertura_periodo": round(primera_vela["open"], 2),
            "precio_cierre_periodo": round(ultima_vela["close"], 2),
            "cambio_precio": round(cambio_precio, 2),
            "cambio_porcentual": round(cambio_porcentual, 2),
            "trend_code": trend_code,
            "total_velas_analizadas": len(velas),
            "patrones_detectados": resultado_analisis["patrones_detectados"],
            "patrones": resultado_analisis["patrones"],
            "contexto_general": {
                "precio_minimo": round(min(v["low"] for v in velas), 2),
                "precio_maximo": round(max(v["high"] for v in velas), 2),
                "rango_precio": round(max(v["high"] for v in velas) - min(v["low"] for v in velas), 2),
                "volumen_promedio": round(sum(v["volume"] for v in velas) / len(velas), 2) if velas else 0,
            },
            "disclaimer_code": DISCLAIMER_CODE,
            "fuente_datos": "BINANCE_API_PUBLIC"
        }
        
        return respuesta
    
    except ValueError as e:
        # Error de validación (ej: timeframe inválido, límite fuera de rango)
        raise HTTPException(
            status_code=400,
            detail=f"Parámetro inválido: {str(e)}"
        )
    
    except HTTPException:
        # Re-lanzar errores HTTP (como los que ya manejamos)
        raise
    
    except Exception as e:
        # Error inesperado (conexión a Binance, etc.)
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error al analizar Bitcoin: {str(e)}. "
                "Verifica tu conexión a internet o intenta de nuevo más tarde."
            )
        )


@router.get(
    "",
    response_model=AnalisisUnificadoResponse,
    summary="Análisis técnico unificado para múltiples mercados",
    description=(
        "Este endpoint obtiene velas reales de cualquier mercado (crypto, stocks, cedears) "
        "y analiza patrones de velas japonesas. Los datos son en tiempo real y el análisis "
        "es puramente educativo."
    )
)
async def analizar_activo(
    market: str = Query(
        ...,
        description="Tipo de mercado: crypto, stocks, cedears",
        example="crypto",
        regex="^(crypto|stocks|cedears)$"
    ),
    symbol: str = Query(
        ...,
        description="Símbolo del activo (ej: BTCUSDT para crypto, AAPL para stocks, AAPL.BA para cedears)",
        example="BTCUSDT"
    ),
    timeframe: str = Query(
        default="1h",
        description="Período de tiempo de cada vela: 1h, 4h, 1d",
        example="1h",
        regex="^(1h|4h|1d)$"
    ),
    limite: int = Query(
        default=100,
        description="Cantidad de velas a analizar (1-1000)",
        ge=1,
        le=1000,
        example=100
    )
):
    """
    Analiza patrones de velas japonesas en cualquier mercado usando datos reales.
    
    **Flujo del endpoint:**
    
    1. **Validación de parámetros**: Verifica que market, symbol y timeframe sean válidos
    2. **Obtención de velas**: Delega al servicio unificado que selecciona el proveedor apropiado:
       - `crypto` → Binance API
       - `stocks` / `cedears` → Yahoo Finance API
    3. **Conversión a formato unificado**: Todos los datos se convierten a formato OHLCV estándar
    4. **Análisis de patrones**: Usa el motor de patrones existente (sin cambios)
    5. **Construcción de respuesta**: Devuelve códigos técnicos (i18n) para traducción en frontend
    
    **Parámetros:**
    - `market`: Tipo de mercado (crypto, stocks, cedears) - REQUERIDO
    - `symbol`: Símbolo del activo - REQUERIDO
    - `timeframe`: Período de cada vela (1h, 4h, 1d) - Opcional, por defecto: 1h
    - `limite`: Cantidad de velas a analizar (1-1000) - Opcional, por defecto: 100
    
    **Ejemplos:**
    ```
    # Criptomoneda (Bitcoin)
    GET /api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
    
    # Acción (Apple)
    GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
    
    # CEDEAR (Apple CEDEAR en Argentina)
    GET /api/analysis?market=cedears&symbol=AAPL.BA&timeframe=1d
    ```
    
    **Respuesta:**
    - `asset`: Símbolo del activo
    - `market`: Mercado utilizado
    - `timeframe`: Período de tiempo
    - `precio_actual`: Precio actual del activo
    - `patrones`: Lista de patrones detectados con códigos técnicos
    - `disclaimer_code`: Código para traducción del aviso legal
    
    **IMPORTANTE:**
    - Los datos son REALES y en TIEMPO REAL
    - El análisis es solo educativo, NO es una recomendación de inversión
    - Requiere conexión a internet para obtener datos
    """
    try:
        # Paso 1: Obtener velas del mercado especificado usando el servicio unificado
        velas = await obtener_velas(
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            limite=limite
        )
        
        # Verificar que se obtuvieron velas
        if not velas or len(velas) == 0:
            # stocks/cedears: fallback Yahoo
            if market.lower() in ["stocks", "cedears"]:
                fallback_data = get_fallback_response_data(
                    market.lower(),
                    symbol.upper(),
                    timeframe
                )
                precio_referencia = fallback_data.get("precio_referencia")
                precio_actual = precio_referencia if precio_referencia is not None else 0.0
                return AnalisisUnificadoResponse(
                    asset=symbol.upper(),
                    market=market.lower(),
                    timeframe=timeframe,
                    precio_actual=precio_actual,
                    total_velas_analizadas=0,
                    patrones_detectados=0,
                    patrones=[],
                    disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
                    status_code=fallback_data.get("status_code"),
                    message_code=fallback_data.get("message_code"),
                    confidence=fallback_data.get("confidence")
                )
            # crypto: fallback educativo (nunca 500)
            fallback_data = get_crypto_fallback_response_data(
                symbol.upper(),
                timeframe
            )
            return AnalisisUnificadoResponse(
                asset=symbol.upper(),
                market=market.lower(),
                timeframe=timeframe,
                precio_actual=0.0,
                total_velas_analizadas=0,
                patrones_detectados=0,
                patrones=[],
                disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
                status_code=fallback_data.get("status_code"),
                message_code=fallback_data.get("message_code"),
                confidence=fallback_data.get("confidence")
            )
        
        # Paso 2: Ejecutar el análisis de patrones (mismo motor para todos los mercados)
        resultado_analisis = analizar_patrones(velas)
        
        # Paso 3: Obtener precio actual (última vela es la más reciente)
        ultima_vela = velas[-1]
        precio_actual = round(ultima_vela["close"], 2)
        
        # Paso 4: Construir la respuesta con códigos técnicos (i18n para frontend)
        respuesta = {
            "asset": symbol.upper(),
            "market": market.lower(),
            "timeframe": timeframe,
            "precio_actual": precio_actual,
            "total_velas_analizadas": len(velas),
            "patrones_detectados": resultado_analisis["patrones_detectados"],
            "patrones": resultado_analisis["patrones"],
            "disclaimer_code": resultado_analisis.get("disclaimer_code", "DISCLAIMER")
        }
        
        return AnalisisUnificadoResponse(**respuesta)
    
    except CryptoDataFallback as fallback:
        # Crypto: CoinGecko y Binance fallaron (451, timeout, etc.)
        # Nunca devolver 500, siempre JSON educativo válido
        fallback_data = get_crypto_fallback_response_data(
            fallback.symbol,
            fallback.timeframe
        )
        precio_referencia = fallback_data.get("precio_referencia")
        precio_actual = precio_referencia if precio_referencia is not None else 0.0
        return AnalisisUnificadoResponse(
            asset=symbol.upper(),
            market=market.lower(),
            timeframe=timeframe,
            precio_actual=precio_actual,
            total_velas_analizadas=0,
            patrones_detectados=0,
            patrones=[],
            disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
            status_code=fallback_data.get("status_code"),
            message_code=fallback_data.get("message_code"),
            confidence=fallback_data.get("confidence")
        )

    except YahooFinanceFallback as fallback:
        # Yahoo Finance no disponible y no hay cache válido
        # Devolver respuesta de fallback válida (no error)
        # ESTO NUNCA DEBE DEVOLVER 500 - siempre devuelve JSON válido
        fallback_data = get_fallback_response_data(
            fallback.market,
            fallback.symbol,
            fallback.timeframe
        )
        
        # Asegurar que precio_actual sea un float válido (no None)
        precio_referencia = fallback_data.get("precio_referencia")
        precio_actual = precio_referencia if precio_referencia is not None else 0.0
        
        return AnalisisUnificadoResponse(
            asset=symbol.upper(),
            market=market.lower(),
            timeframe=timeframe,
            precio_actual=precio_actual,
            total_velas_analizadas=0,
            patrones_detectados=0,
            patrones=[],
            disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
            status_code=fallback_data.get("status_code"),
            message_code=fallback_data.get("message_code"),
            confidence=fallback_data.get("confidence")
        )
    
    except ValueError as e:
        # Error de validación: devolver fallback educativo (nunca 500)
        if market.lower() in ["stocks", "cedears"]:
            fallback_data = get_fallback_response_data(
                market.lower(),
                symbol.upper(),
                timeframe
            )
            precio_referencia = fallback_data.get("precio_referencia")
            precio_actual = precio_referencia if precio_referencia is not None else 0.0
            return AnalisisUnificadoResponse(
                asset=symbol.upper(),
                market=market.lower(),
                timeframe=timeframe,
                precio_actual=precio_actual,
                total_velas_analizadas=0,
                patrones_detectados=0,
                patrones=[],
                disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
                status_code=fallback_data.get("status_code"),
                message_code=fallback_data.get("message_code"),
                confidence=fallback_data.get("confidence")
            )
        # crypto: fallback educativo para símbolo inválido u otro ValueError
        fallback_data = get_crypto_fallback_response_data(symbol.upper(), timeframe)
        return AnalisisUnificadoResponse(
            asset=symbol.upper(),
            market=market.lower(),
            timeframe=timeframe,
            precio_actual=0.0,
            total_velas_analizadas=0,
            patrones_detectados=0,
            patrones=[],
            disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
            status_code=fallback_data.get("status_code"),
            message_code=fallback_data.get("message_code"),
            confidence=fallback_data.get("confidence")
        )
    
    except HTTPException:
        # Re-lanzar errores HTTP que ya manejamos (solo para crypto)
        raise
    
    except Exception as e:
        # Error inesperado
        # IMPORTANTE: Nunca devolver 500 por fuentes externas - siempre fallback
        if market.lower() in ["stocks", "cedears"]:
            fallback_data = get_fallback_response_data(
                market.lower(),
                symbol.upper(),
                timeframe
            )
            precio_referencia = fallback_data.get("precio_referencia")
            precio_actual = precio_referencia if precio_referencia is not None else 0.0
            return AnalisisUnificadoResponse(
                asset=symbol.upper(),
                market=market.lower(),
                timeframe=timeframe,
                precio_actual=precio_actual,
                total_velas_analizadas=0,
                patrones_detectados=0,
                patrones=[],
                disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
                status_code=fallback_data.get("status_code"),
                message_code=fallback_data.get("message_code"),
                confidence=fallback_data.get("confidence")
            )

        # crypto: fallback educativo (nunca 500 por fuentes externas)
        fallback_data = get_crypto_fallback_response_data(symbol.upper(), timeframe)
        return AnalisisUnificadoResponse(
            asset=symbol.upper(),
            market=market.lower(),
            timeframe=timeframe,
            precio_actual=0.0,
            total_velas_analizadas=0,
            patrones_detectados=0,
            patrones=[],
            disclaimer_code=fallback_data.get("disclaimer_code", "DISCLAIMER"),
            status_code=fallback_data.get("status_code"),
            message_code=fallback_data.get("message_code"),
            confidence=fallback_data.get("confidence")
        )
