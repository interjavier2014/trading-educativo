# 🔄 Flujo Completo de la API Unificada - Paso a Paso

Este documento explica **paso a paso** cómo funciona el endpoint unificado `/api/analysis` que soporta múltiples mercados (crypto, stocks, cedears).

---

## 🎯 Resumen del Flujo

```
Cliente → Endpoint → Servicio Unificado → Servicio Específico → API Externa → 
Formato Unificado → Motor de Patrones → Respuesta con Códigos Técnicos → Cliente
```

---

## 📋 Paso a Paso Detallado

### **PASO 1: Cliente hace la petición**

**URL:**
```
GET /api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
```

**Parámetros:**
- `market=crypto` → Tipo de mercado
- `symbol=BTCUSDT` → Símbolo del activo
- `timeframe=1h` → Período de cada vela (opcional, por defecto: 1h)

**¿Dónde se procesa?**
- `app/api/analysis.py` → Función `analizar_activo()`

---

### **PASO 2: Validación de parámetros**

El endpoint valida que los parámetros sean correctos:

**Validaciones:**
1. **`market`** debe ser: `crypto`, `stocks`, o `cedears`
   - Si no es válido → Error 400: "Parámetro inválido"
   
2. **`symbol`** no puede estar vacío
   - Si está vacío → Error 400: "Parámetro inválido"
   
3. **`timeframe`** debe ser: `1h`, `4h`, o `1d`
   - Si no es válido → Error 400: "Parámetro inválido"
   - Por defecto: `1h`

4. **`limite`** debe estar entre 1 y 1000
   - Si está fuera de rango → Error 400: "Parámetro inválido"
   - Por defecto: 100

**Código:**
```python
# FastAPI valida automáticamente usando Query(..., regex="^(crypto|stocks|cedears)$")
# Si no pasa la validación, FastAPI devuelve error 422 antes de llegar a la función
```

---

### **PASO 3: Llamada al servicio unificado**

El endpoint llama al servicio unificado:

**Función:**
```python
velas = await obtener_velas(
    market=market,      # "crypto", "stocks", o "cedears"
    symbol=symbol,      # "BTCUSDT", "AAPL", "AAPL.BA"
    timeframe=timeframe, # "1h", "4h", "1d"
    limite=limite       # 1-1000
)
```

**¿Dónde se procesa?**
- `app/services/unified_price_service.py` → Función `obtener_velas()`

**¿Qué hace?**
- Recibe los parámetros
- Valida que el mercado sea válido
- **Selecciona el servicio apropiado** según el mercado

---

### **PASO 4: Selección del servicio específico**

El servicio unificado decide qué proveedor usar:

**Lógica de selección:**

```python
if market == "crypto":
    # → Usar Binance
    return await obtener_velas_bitcoin(...)
    
elif market in ["stocks", "cedears"]:
    # → Usar Yahoo Finance
    return await obtener_velas_yahoo_finance(...)
```

**Servicios específicos:**
- **Crypto** → `app/services/bitcoin_price_service.py`
- **Stocks/CEDEARs** → `app/services/yahoo_finance_service.py`

---

### **PASO 5A: Si market = crypto (Binance)**

**¿Qué servicio se ejecuta?**
- `app/services/bitcoin_price_service.py` → `obtener_velas_bitcoin()`

**¿Qué hace?**
1. **Valida timeframe** contra los permitidos por Binance
2. **Construye la URL:**
   ```
   https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100
   ```
3. **Hace petición HTTP GET** a Binance usando `httpx`
4. **Recibe respuesta JSON** de Binance con velas
5. **Convierte cada vela** al formato unificado OHLCV:
   ```python
   # De Binance:
   [timestamp, "50000", "51000", "49500", "50500", "1234.56", ...]
   
   # A formato unificado:
   {"open": 50000.0, "high": 51000.0, "low": 49500.0, "close": 50500.0, "volume": 1234.56}
   ```
6. **Devuelve lista de velas** en formato OHLCV unificado

---

### **PASO 5B: Si market = stocks o cedears (Yahoo Finance)**

**¿Qué servicio se ejecuta?**
- `app/services/yahoo_finance_service.py` → `obtener_velas_yahoo_finance()`

**¿Qué hace?**
1. **Valida timeframe** contra los permitidos por Yahoo Finance
2. **Calcula rango de fechas** necesario (Yahoo requiere start/end dates)
3. **Construye la URL:**
   ```
   https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&period1=1234567890&period2=1234567890
   ```
4. **Hace petición HTTP GET** a Yahoo Finance usando `httpx`
5. **Recibe respuesta JSON** de Yahoo Finance
6. **Extrae datos** de la estructura específica de Yahoo:
   ```python
   # Yahoo Finance estructura:
   chart.result[0].indicators.quote[0].{open, high, low, close, volume}
   ```
7. **Convierte cada vela** al formato unificado OHLCV
8. **Filtra datos faltantes** (Yahoo puede devolver None)
9. **Toma las últimas N velas** según el límite
10. **Devuelve lista de velas** en formato OHLCV unificado

---

### **PASO 6: Formato unificado OHLCV**

Ambos servicios (Binance y Yahoo Finance) devuelven **el mismo formato**:

```python
[
    {
        "open": 50000.0,    # Precio de apertura
        "high": 51000.0,    # Precio más alto
        "low": 49500.0,     # Precio más bajo
        "close": 50500.0,   # Precio de cierre
        "volume": 1234.56   # Volumen
    },
    # ... más velas
]
```

**¿Por qué es importante?**
- El motor de patrones puede trabajar con **cualquier mercado**
- No necesita saber si viene de Binance o Yahoo Finance
- Mismo formato = misma lógica de análisis

---

### **PASO 7: Verificación de velas**

El endpoint verifica que se obtuvieron velas:

```python
if not velas or len(velas) == 0:
    raise HTTPException(
        status_code=404,
        detail=f"No se pudieron obtener velas para {symbol} en el mercado {market}..."
    )
```

**Errores posibles:**
- Símbolo no encontrado (ej: `INVALID123`)
- Activo no existe en el mercado especificado
- Problemas de conexión con la API externa

---

### **PASO 8: Ejecución del motor de patrones**

El endpoint llama al motor de patrones con las velas unificadas:

**Función:**
```python
resultado_analisis = analizar_patrones(velas)
```

**¿Dónde se procesa?**
- `app/services/candlestick_patterns.py` → Función `analizar_patrones()`

**¿Qué hace el motor?**
1. **Analiza cada vela individualmente:**
   - Detecta **Martillo** (HAMMER)
   - Detecta **Doji** (DOJI_STANDARD, DOJI_DRAGONFLY, DOJI_GRAVESTONE)

2. **Analiza pares de velas:**
   - Detecta **Envolvente Alcista** (BULLISH_ENGULFING)

3. **Calcula índices:**
   - `posicion`: Índice 0-based (0 = primera vela)
   - `pattern_index`: Índice desde el final (-1 = última vela)

4. **Construye resultado:**
   ```python
   {
       "total_velas_analizadas": 100,
       "patrones_detectados": 2,
       "patrones": [
           {
               "pattern_code": "HAMMER",
               "context_code": "POTENTIAL_BULLISH",
               "confidence": "MEDIUM",
               "datos_tecnicos": {...},
               "posicion": 45,
               "pattern_index": -56
           }
       ],
       "disclaimer_code": "DISCLAIMER"
   }
   ```

**Importante:**
- El motor de patrones **NO sabe** de qué mercado vienen las velas
- Funciona igual para crypto, stocks y cedears
- **No hay duplicación de lógica de análisis**

---

### **PASO 9: Extracción del precio actual**

El endpoint obtiene el precio actual del activo:

```python
ultima_vela = velas[-1]  # La última vela es la más reciente
precio_actual = round(ultima_vela["close"], 2)
```

**¿Por qué?**
- Para mostrarlo en la respuesta
- Es información útil para el usuario

---

### **PASO 10: Construcción de la respuesta**

El endpoint construye la respuesta con códigos técnicos (i18n):

```python
respuesta = {
    "asset": symbol.upper(),           # "BTCUSDT"
    "market": market.lower(),          # "crypto"
    "timeframe": timeframe,            # "1h"
    "precio_actual": precio_actual,    # 65000.00
    "total_velas_analizadas": len(velas),  # 100
    "patrones_detectados": resultado_analisis["patrones_detectados"],  # 2
    "patrones": resultado_analisis["patrones"],  # [...]
    "disclaimer_code": "DISCLAIMER"    # Código para traducción
}
```

**Validación del schema:**
```python
return AnalisisUnificadoResponse(**respuesta)
```
- FastAPI valida que la respuesta coincida con el schema
- Si falta algún campo o es incorrecto → Error 500

---

### **PASO 11: Manejo de errores**

El endpoint maneja diferentes tipos de errores:

**1. Error de validación (400):**
```python
except ValueError as e:
    raise HTTPException(status_code=400, detail=f"Parámetro inválido: {str(e)}")
```
- **Causa:** Market inválido, timeframe inválido, límite fuera de rango
- **Ejemplo:** `market=invalid` → Error 400

**2. Error de activo no encontrado (404):**
```python
if "no fue encontrado" in error_message or "No se encontraron datos" in error_message:
    status_code = 404
```
- **Causa:** Símbolo no existe en el mercado especificado
- **Ejemplo:** `symbol=INVALID123` → Error 404

**3. Error de conexión (500):**
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al analizar {symbol}...")
```
- **Causa:** Problemas de conexión, API externa caída, timeout
- **Ejemplo:** Sin internet → Error 500

---

### **PASO 12: Respuesta final al cliente**

La respuesta se devuelve como JSON:

```json
{
  "asset": "BTCUSDT",
  "market": "crypto",
  "timeframe": "1h",
  "precio_actual": 65000.00,
  "total_velas_analizadas": 100,
  "patrones_detectados": 2,
  "patrones": [
    {
      "pattern_code": "HAMMER",
      "context_code": "POTENTIAL_BULLISH",
      "confidence": "MEDIUM",
      "datos_tecnicos": {
        "cuerpo": 0.5,
        "sombra_inferior": 5.5,
        "sombra_superior": 1.5,
        "proporcion_sombra_cuerpo": 11.0
      },
      "posicion": 45,
      "pattern_index": -56
    },
    {
      "pattern_code": "DOJI_STANDARD",
      "context_code": "INDECISION",
      "confidence": "LOW",
      "datos_tecnicos": {...},
      "posicion": 99,
      "pattern_index": -1
    }
  ],
  "disclaimer_code": "DISCLAIMER"
}
```

---

## 📊 Diagrama de Flujo Visual

```
┌─────────┐
│ Cliente │
└────┬────┘
     │ GET /api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
     ↓
┌─────────────────────────────────────┐
│  1. Endpoint: analizar_activo()    │
│     app/api/analysis.py             │
│  • Valida parámetros                │
└────┬────────────────────────────────┘
     │ await obtener_velas(...)
     ↓
┌─────────────────────────────────────┐
│  2. Servicio Unificado              │
│     app/services/                   │
│     unified_price_service.py        │
│  • Selecciona proveedor             │
└────┬────────────────────────────────┘
     │
     ├─ market="crypto" ───────────────┐
     │                                  ↓
     │                    ┌──────────────────────────────┐
     │                    │ 3a. Bitcoin Service          │
     │                    │ app/services/                │
     │                    │ bitcoin_price_service.py     │
     │                    │ • Conecta a Binance API      │
     │                    └─────┬────────────────────────┘
     │                          │
     │                          ↓
     │                    Formato OHLCV Unificado
     │
     └─ market in ["stocks", "cedears"] ─┐
                                          ↓
                          ┌──────────────────────────────┐
                          │ 3b. Yahoo Finance Service    │
                          │ app/services/                │
                          │ yahoo_finance_service.py     │
                          │ • Conecta a Yahoo Finance API│
                          └─────┬────────────────────────┘
                                │
                                ↓
                          Formato OHLCV Unificado
                                 │
                                 ↓
┌──────────────────────────────────────────────────────────┐
│  4. Motor de Patrones                                    │
│     app/services/candlestick_patterns.py                 │
│  • Analiza velas (independiente del mercado)            │
│  • Detecta patrones: HAMMER, DOJI, BULLISH_ENGULFING    │
│  • Devuelve códigos técnicos (i18n)                     │
└────┬─────────────────────────────────────────────────────┘
     │ resultado_analisis
     ↓
┌─────────────────────────────────────┐
│  5. Construcción de Respuesta       │
│     app/api/analysis.py             │
│  • Agrega asset, market, timeframe  │
│  • Agrega precio_actual             │
│  • Devuelve AnalisisUnificadoResponse│
└────┬────────────────────────────────┘
     │ JSON Response
     ↓
┌─────────┐
│ Cliente │
└─────────┘
```

---

## 🔑 Puntos Clave del Flujo

### **1. Separación de Responsabilidades:**
- **Endpoint:** Validación y construcción de respuesta
- **Servicio Unificado:** Selección del proveedor
- **Servicios Específicos:** Comunicación con APIs externas
- **Motor de Patrones:** Análisis (independiente del mercado)

### **2. Formato Unificado:**
- Todos los servicios devuelven el mismo formato OHLCV
- El motor de patrones no necesita saber el origen
- **No hay duplicación de lógica de análisis**

### **3. Extensibilidad:**
Para agregar un nuevo mercado:
1. Crear servicio en `app/services/nuevo_mercado_service.py`
2. Agregar caso en `unified_price_service.py`
3. El endpoint ya funciona automáticamente

### **4. Manejo de Errores:**
- Errores de validación → 400
- Activo no encontrado → 404
- Errores de conexión → 500
- Mensajes claros en cada caso

### **5. Códigos Técnicos (i18n):**
- Respuesta usa códigos (HAMMER, INDECISION, etc.)
- Frontend traduce según el idioma del usuario
- No hay textos hardcodeados en la API

---

## ✅ Resumen del Flujo

1. **Cliente** hace petición con parámetros
2. **Endpoint** valida parámetros
3. **Servicio Unificado** selecciona proveedor (Binance o Yahoo Finance)
4. **Servicio Específico** obtiene datos de la API externa
5. **Conversión** a formato OHLCV unificado
6. **Motor de Patrones** analiza (sin saber el origen)
7. **Construcción** de respuesta con códigos técnicos
8. **Cliente** recibe respuesta JSON

---

**La arquitectura está diseñada para ser limpia, extensible y sin duplicación de lógica.** 🎯
