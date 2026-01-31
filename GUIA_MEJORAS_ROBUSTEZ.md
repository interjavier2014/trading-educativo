# 🛡️ Guía de Mejoras de Robustez para Yahoo Finance

Esta guía explica las mejoras implementadas para hacer el sistema más robusto ante rate limits de Yahoo Finance.

---

## 🎯 Objetivo

Mejorar la **UX** (experiencia del usuario) cuando Yahoo Finance está temporalmente no disponible por rate limiting, evitando errores técnicos y proporcionando respuestas válidas.

---

## 🔄 Flujo Completo Mejorado

### **Escenario Normal (Yahoo disponible):**

```
1. Cliente pide: AAPL, stocks, 1d
   ↓
2. Verificar cache
   ↓
3. Cache válido? → Devolver cache (instantáneo)
   ↓
4. Cache no válido? → Llamar a Yahoo Finance
   ↓
5. Yahoo responde OK → Guardar en cache + devolver datos
```

---

### **Escenario con Warm-up (Al iniciar app):**

```
1. Servidor inicia (main.py)
   ↓
2. Evento startup → warmup_cache_background()
   ↓
3. Precarga en segundo plano (no bloquea inicio):
   - AAPL (stocks, 1d)
   - TSLA (stocks, 1d)
   - MSFT (stocks, 1d)
   - AAPL.BA (cedears, 1d)
   ↓
4. Cache listo antes de las primeras peticiones ✅
```

**Beneficio:** Primeras peticiones responden instantáneamente desde cache

---

### **Escenario Yahoo Error 429 con Cache Disponible:**

```
1. Cliente pide: AAPL, stocks, 1d
   ↓
2. get_from_cache() → Cache válido
   ↓
3. Devolver cache (Yahoo nunca se llama)
```

**Beneficio:** Rate limiting no afecta (se usa cache)

---

### **Escenario Yahoo Error 429 SIN Cache (Mejora implementada):**

```
1. Cliente pide: AAPL, stocks, 1d
   ↓
2. get_from_cache() → No hay cache válido
   ↓
3. Llamada a Yahoo Finance
   ↓
4. Yahoo responde 429 (Rate Limit)
   ↓
5. get_last_cache() → No hay cache (ni expirado)
   ↓
6. NO devolver error técnico ❌
   ↓
7. Devolver respuesta válida con códigos de fallback ✅
   {
     "asset": "AAPL",
     "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
     "message_code": "DATA_SOURCE_RATE_LIMIT",
     "confidence": "LOW",
     "patrones_detectados": 0,
     "patrones": []
   }
```

**Beneficio:** Cliente recibe respuesta válida, frontend puede mostrar mensaje educativo

---

## ⏱️ TTL del Cache (Time To Live)

### **Configuración según Timeframe:**

| Timeframe | TTL | Duración |
|-----------|-----|----------|
| `1d` | 1800 segundos | **30 minutos** |
| `1h` | 600 segundos | **10 minutos** |
| `4h` | 900 segundos | 15 minutos (fallback) |
| Otros | 300 segundos | 5 minutos (por defecto) |

### **¿Por qué diferentes TTL?**

- **1d (velas diarias):** Cambian lentamente → Cache más largo (30 min)
- **1h (velas horarias):** Cambian más rápido → Cache más corto (10 min)

**Lógica:**
- Datos que cambian menos frecuentemente → Cache más largo
- Datos que cambian frecuentemente → Cache más corto

---

## 🔥 Warm-up del Cache

### **¿Qué es el warm-up?**

Precarga de datos populares en el cache **al iniciar la aplicación**, antes de que lleguen las primeras peticiones.

### **Activos precargados:**

1. **AAPL** (stocks, 1d) - Apple
2. **TSLA** (stocks, 1d) - Tesla
3. **MSFT** (stocks, 1d) - Microsoft
4. **AAPL.BA** (cedears, 1d) - Apple CEDEAR

### **¿Cuándo se ejecuta?**

- **Evento:** `@app.on_event("startup")` en `main.py`
- **Momento:** Cuando se inicia el servidor FastAPI
- **Modalidad:** En segundo plano (no bloquea el inicio)

### **Código:**

```python
@app.on_event("startup")
async def startup_event():
    from app.services.cache_warmup import warmup_cache_background
    warmup_cache_background()  # Ejecuta en segundo plano
```

---

## 🛡️ Sistema de Fallback

### **¿Qué es el fallback?**

Cuando Yahoo Finance falla y **NO hay cache disponible**, en lugar de devolver un error técnico, se devuelve una **respuesta válida** con códigos especiales.

### **Respuesta de Fallback:**

```json
{
  "asset": "AAPL",
  "market": "stocks",
  "timeframe": "1d",
  "precio_actual": 150.00,  // Puede ser precio_referencia si hay cache expirado
  "total_velas_analizadas": 0,
  "patrones_detectados": 0,
  "patrones": [],
  "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
  "message_code": "DATA_SOURCE_RATE_LIMIT",
  "confidence": "LOW",
  "disclaimer_code": "DISCLAIMER"
}
```

### **Códigos de Fallback:**

- **`status_code`:** `DATA_TEMPORARILY_UNAVAILABLE`
  - Indica que los datos no están disponibles temporalmente

- **`message_code`:** `DATA_SOURCE_RATE_LIMIT`
  - Indica que la fuente de datos (Yahoo) está limitando peticiones

- **`confidence`:** `LOW`
  - Indica que la respuesta tiene baja confiabilidad

### **Ventajas:**

1. ✅ **Respuesta válida:** El frontend puede parsearla normalmente
2. ✅ **Sin errores técnicos:** No hay HTTP 500 o mensajes confusos
3. ✅ **Mensaje educativo:** El frontend puede mostrar: "Datos temporalmente no disponibles"
4. ✅ **Estructura consistente:** Mismo formato que respuesta normal

---

## 📊 Comparación: Antes vs Después

### **Antes (sin mejoras):**

```
Yahoo 429 + Sin Cache
   ↓
Error HTTP 500
   ↓
Mensaje técnico: "Yahoo Finance está temporalmente no disponible..."
   ↓
Frontend muestra: "Error 500: Internal Server Error" ❌
```

**Problema:** Usuario ve error técnico confuso

---

### **Después (con mejoras):**

```
Yahoo 429 + Sin Cache
   ↓
Respuesta válida con códigos de fallback
   ↓
{
  "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
  "message_code": "DATA_SOURCE_RATE_LIMIT",
  "confidence": "LOW"
}
   ↓
Frontend muestra: "Datos temporalmente no disponibles. Intenta de nuevo en unos minutos." ✅
```

**Mejora:** Usuario ve mensaje educativo claro

---

## 🎨 Mejora de UX

### **1. Warm-up mejora primera impresión:**

**Antes:**
- Primera petición a AAPL → Llamada a Yahoo → Tarda 3-5 segundos

**Después:**
- Primera petición a AAPL → Cache disponible → Respuesta instantánea ✅

---

### **2. TTL ajustado mejora frescura:**

**Antes:**
- Todos los timeframes usaban 5 minutos
- Velas diarias podrían actualizarse cada 5 minutos (innecesario)

**Después:**
- 1d → 30 minutos (datos frescos pero no sobrecarga Yahoo)
- 1h → 10 minutos (balance entre frescura y carga)

---

### **3. Fallback mejora resiliencia:**

**Antes:**
- Yahoo 429 + Sin cache → Error 500 → Usuario ve error técnico

**Después:**
- Yahoo 429 + Sin cache → Respuesta válida → Frontend muestra mensaje educativo ✅

---

## 📋 Resumen de Cambios

### **1. Warm-up de Cache:**
- ✅ Precarga: AAPL, TSLA, MSFT, AAPL.BA
- ✅ Timeframe: 1d
- ✅ Ejecuta al iniciar app (evento startup)

### **2. Fallback cuando Yahoo falla:**
- ✅ No devuelve error técnico
- ✅ Devuelve respuesta válida con códigos:
  - `status_code`: `DATA_TEMPORARILY_UNAVAILABLE`
  - `message_code`: `DATA_SOURCE_RATE_LIMIT`
  - `confidence`: `LOW`

### **3. TTL ajustado:**
- ✅ `1d` → 30 minutos
- ✅ `1h` → 10 minutos
- ✅ Otros → 5 minutos (por defecto)

### **4. Crypto sin cambios:**
- ✅ Binance no usa cache (mantiene comportamiento original)

---

## 🔍 Flujo Detallado del Fallback

### **Paso 1: Yahoo devuelve 429**

```python
# En yahoo_finance_service.py
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        # Intentar cache
        last_cache = get_last_cache(...)
        if last_cache:
            return last_cache  # Cache disponible ✅
        else:
            # No hay cache → Lanzar excepción especial
            raise YahooFinanceFallback(market, symbol, timeframe)
```

---

### **Paso 2: Servicio Unificado propaga**

```python
# En unified_price_service.py
try:
    return await obtener_velas_yahoo_finance(...)
except YahooFinanceFallback as fallback:
    raise fallback  # Propagar al endpoint
```

---

### **Paso 3: Endpoint captura y convierte**

```python
# En analysis.py
except YahooFinanceFallback as fallback:
    # Obtener datos de fallback
    fallback_data = get_fallback_response_data(...)
    
    # Construir respuesta válida
    respuesta_fallback = {
        "asset": symbol,
        "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
        "message_code": "DATA_SOURCE_RATE_LIMIT",
        "confidence": "LOW",
        "patrones_detectados": 0,
        "patrones": []
    }
    
    return AnalisisUnificadoResponse(**respuesta_fallback)
```

---

## 💡 Beneficios para el Usuario

### **1. Primera experiencia mejorada:**
- Cache precargado → Respuestas instantáneas
- Sin esperar 3-5 segundos en la primera petición

### **2. Menos errores confusos:**
- No ve "Error 500: Internal Server Error"
- Ve mensaje claro: "Datos temporalmente no disponibles"

### **3. Mayor resiliencia:**
- Sistema funciona aunque Yahoo tenga rate limiting
- Cache protege de limitaciones

### **4. Datos más frescos:**
- TTL ajustado según frecuencia de cambio
- Balance entre frescura y carga en Yahoo

---

## 📈 Mejoras de Performance

### **Reducción de llamadas a Yahoo:**
- **Warm-up:** 4 activos precargados = 4 llamadas menos al inicio
- **Cache más largo (1d):** 30 min vs 5 min = 6x menos llamadas

### **Respuestas más rápidas:**
- **Cache válido:** 0ms (vs 3000-5000ms llamando a Yahoo)
- **Warm-up:** Primera petición instantánea

---

## 🔒 Crypto Sin Cambios

### **Por qué:**
- Binance tiene mejor rate limiting
- Datos de crypto cambian muy rápido (cache contraproducente)
- No necesita warm-up (ya es rápido)

### **Comportamiento:**
- Crypto sigue funcionando igual
- Sin cache
- Sin warm-up
- Sin fallback especial

---

## ✅ Resumen de Archivos

### **Nuevos:**
1. `app/services/cache_warmup.py` - Sistema de warm-up
2. `app/services/yahoo_finance_fallback.py` - Sistema de fallback
3. `GUIA_MEJORAS_ROBUSTEZ.md` - Esta guía

### **Modificados:**
1. `app/services/yahoo_finance_cache.py` - TTL dinámico según timeframe
2. `app/services/yahoo_finance_service.py` - Manejo de fallback
3. `app/services/unified_price_service.py` - Propaga fallback
4. `app/api/analysis.py` - Captura y convierte fallback a respuesta válida
5. `app/schemas/patterns.py` - Schema actualizado con campos opcionales de fallback
6. `main.py` - Evento startup con warm-up

---

**El sistema ahora es más robusto, resiliente y ofrece mejor UX ante problemas de Yahoo Finance.** 🚀
