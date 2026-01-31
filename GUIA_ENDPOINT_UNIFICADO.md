# 🌐 Guía del Endpoint Unificado de Análisis

Esta guía explica cómo funciona el endpoint unificado `/api/analysis` que soporta múltiples mercados (crypto, stocks, cedears).

---

## 🎯 ¿Qué hace este endpoint?

El endpoint `GET /api/analysis` es un **punto de entrada único** que:
- Soporta múltiples mercados (criptomonedas, acciones, CEDEARs)
- Obtiene datos reales desde diferentes APIs según el mercado
- Usa el mismo motor de análisis para todos los mercados
- Devuelve respuestas con códigos técnicos (i18n)

---

## 📍 URL del Endpoint

```
GET /api/analysis
```

---

## 📋 Parámetros

### **`market`** (requerido)
- **Descripción:** Tipo de mercado
- **Valores válidos:**
  - `crypto` - Criptomonedas (Binance)
  - `stocks` - Acciones (Yahoo Finance)
  - `cedears` - CEDEARs (Yahoo Finance)
- **Ejemplo:** `market=crypto`

### **`symbol`** (requerido)
- **Descripción:** Símbolo del activo
- **Ejemplos:**
  - Crypto: `BTCUSDT`, `ETHUSDT`
  - Stocks: `AAPL`, `MSFT`, `GOOGL`
  - CEDEARs: `AAPL.BA`, `MSFT.BA`, `GOOGL.BA`
- **Ejemplo:** `symbol=BTCUSDT`

### **`timeframe`** (opcional)
- **Descripción:** Período de tiempo de cada vela
- **Valores válidos:** `1h`, `4h`, `1d`
- **Por defecto:** `1h`
- **Ejemplo:** `timeframe=1d`

### **`limite`** (opcional)
- **Descripción:** Cantidad de velas a analizar
- **Rango:** 1 a 1000
- **Por defecto:** 100
- **Ejemplo:** `limite=50`

---

## 🔄 Flujo del Endpoint (Arquitectura)

### **Paso 1: Recepción de la Petición**
```
Cliente → GET /api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
```

### **Paso 2: Validación de Parámetros**
- Verifica que `market` sea válido (crypto, stocks, cedears)
- Verifica que `timeframe` sea válido (1h, 4h, 1d)
- Valida que `limite` esté en el rango permitido

### **Paso 3: Delegación al Servicio Unificado**
El endpoint llama a `obtener_velas()` del servicio unificado:

```
obtener_velas(market="crypto", symbol="BTCUSDT", timeframe="1h", limite=100)
```

### **Paso 4: Selección del Proveedor**
El servicio unificado determina qué API usar:

```
if market == "crypto":
    → bitcoin_price_service.py → Binance API
elif market in ["stocks", "cedears"]:
    → yahoo_finance_service.py → Yahoo Finance API
```

### **Paso 5: Obtención de Datos**
- **Crypto (Binance):** `https://api.binance.com/api/v3/klines`
- **Stocks/CEDEARs (Yahoo Finance):** `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`

### **Paso 6: Conversión a Formato Unificado**
Ambos servicios devuelven velas en formato OHLCV estándar:
```python
{
    "open": 50000.0,
    "high": 51000.0,
    "low": 49500.0,
    "close": 50500.0,
    "volume": 1234.56
}
```

### **Paso 7: Análisis de Patrones**
El motor de patrones (`candlestick_patterns.py`) analiza las velas:
- Detecta patrones: Martillo, Doji, Envolvente Alcista
- Devuelve códigos técnicos (i18n): `pattern_code`, `context_code`, `confidence`

### **Paso 8: Construcción de Respuesta**
Se construye la respuesta con códigos técnicos:

```json
{
  "asset": "BTCUSDT",
  "market": "crypto",
  "timeframe": "1h",
  "precio_actual": 65000.00,
  "patrones_detectados": 2,
  "patrones": [...],
  "disclaimer_code": "DISCLAIMER"
}
```

---

## 📁 Arquitectura de Archivos

```
app/
├── api/
│   └── analysis.py              # Endpoint unificado GET /api/analysis
│
├── services/
│   ├── unified_price_service.py # Servicio unificado (punto de entrada)
│   ├── bitcoin_price_service.py # Servicio para crypto (Binance)
│   ├── yahoo_finance_service.py # Servicio para stocks/cedears (Yahoo Finance)
│   └── candlestick_patterns.py  # Motor de análisis (común a todos)
│
└── schemas/
    └── patterns.py              # Esquemas de validación
```

---

## 🔍 Flujo Detallado por Mercado

### **Crypto (Binance)**

1. **Petición:**
   ```
   GET /api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
   ```

2. **Servicio unificado** → `bitcoin_price_service.py`

3. **Llamada a Binance:**
   ```
   GET https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100
   ```

4. **Conversión** → Formato OHLCV unificado

5. **Análisis** → Motor de patrones

6. **Respuesta** → Códigos técnicos

---

### **Stocks (Yahoo Finance)**

1. **Petición:**
   ```
   GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
   ```

2. **Servicio unificado** → `yahoo_finance_service.py`

3. **Llamada a Yahoo Finance:**
   ```
   GET https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&period1=...&period2=...
   ```

4. **Conversión** → Formato OHLCV unificado

5. **Análisis** → Motor de patrones (mismo motor que crypto)

6. **Respuesta** → Códigos técnicos

---

### **CEDEARs (Yahoo Finance)**

1. **Petición:**
   ```
   GET /api/analysis?market=cedears&symbol=AAPL.BA&timeframe=1d
   ```

2. **Servicio unificado** → `yahoo_finance_service.py` (mismo servicio que stocks)

3. **Llamada a Yahoo Finance:**
   ```
   GET https://query1.finance.yahoo.com/v8/finance/chart/AAPL.BA?interval=1d&...
   ```

4. **Conversión** → Formato OHLCV unificado

5. **Análisis** → Motor de patrones (mismo motor)

6. **Respuesta** → Códigos técnicos

---

## 💡 Ventajas de la Arquitectura Unificada

### **1. Punto de Entrada Único**
- Un solo endpoint para todos los mercados
- Misma interfaz, diferentes proveedores detrás

### **2. Separación de Responsabilidades**
- **Endpoint:** Validación y construcción de respuesta
- **Servicio unificado:** Selección del proveedor
- **Servicios específicos:** Comunicación con APIs externas
- **Motor de patrones:** Análisis (independiente del mercado)

### **3. Extensibilidad**
Para agregar un nuevo mercado:
1. Crear servicio específico (ej: `forex_service.py`)
2. Agregar caso en `unified_price_service.py`
3. El endpoint ya funciona automáticamente

### **4. Reutilización**
- El motor de patrones es **completamente reutilizable**
- No necesita cambios para nuevos mercados
- Formato OHLCV es estándar en todos los mercados

### **5. Mantenibilidad**
- Cambios en Binance → Solo afecta `bitcoin_price_service.py`
- Cambios en Yahoo Finance → Solo afecta `yahoo_finance_service.py`
- Lógica de análisis → Centralizada en `candlestick_patterns.py`

---

## 📊 Ejemplo de Respuesta

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
      "datos_tecnicos": {...},
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

## 🧪 Ejemplos de Uso

### **Crypto - Bitcoin**
```
GET /api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h&limite=100
```

### **Stocks - Apple**
```
GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d&limite=30
```

### **CEDEAR - Apple CEDEAR**
```
GET /api/analysis?market=cedears&symbol=AAPL.BA&timeframe=1d&limite=30
```

### **Crypto - Ethereum**
```
GET /api/analysis?market=crypto&symbol=ETHUSDT&timeframe=4h&limite=50
```

---

## 🔧 Mantenimiento de la Arquitectura

### **Agregar nuevo mercado:**
1. Crear servicio en `app/services/nuevo_mercado_service.py`
2. Agregar caso en `unified_price_service.py`:
   ```python
   elif market == "nuevo_mercado":
       return await obtener_velas_nuevo_mercado(...)
   ```
3. Actualizar validación del endpoint para incluir el nuevo mercado

### **Modificar lógica de análisis:**
- Solo editar `candlestick_patterns.py`
- Todos los mercados se benefician automáticamente

### **Cambiar proveedor:**
- Solo editar el servicio específico (ej: `bitcoin_price_service.py`)
- El endpoint y el análisis no cambian

---

## ✅ Resumen del Flujo

```
Cliente
  ↓
GET /api/analysis?market=crypto&symbol=BTCUSDT
  ↓
Endpoint (analysis.py)
  ↓ Validación
  ↓
Servicio Unificado (unified_price_service.py)
  ↓ Selección de mercado
  ↓
[ crypto → bitcoin_price_service.py → Binance API ]
[ stocks/cedears → yahoo_finance_service.py → Yahoo Finance API ]
  ↓
Formato OHLCV Unificado
  ↓
Motor de Patrones (candlestick_patterns.py)
  ↓
Respuesta con Códigos Técnicos (i18n)
  ↓
Cliente
```

---

**La arquitectura está diseñada para ser limpia, extensible y mantenible.** 🎯
