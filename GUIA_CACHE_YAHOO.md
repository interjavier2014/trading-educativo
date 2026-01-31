# 💾 Guía del Sistema de Cache para Yahoo Finance

Esta guía explica cómo funciona el sistema de cache en memoria para consultas a Yahoo Finance.

---

## 🎯 ¿Por qué cachear?

### **Problemas que resuelve:**
1. **Rate Limiting (429):** Yahoo Finance tiene límites de peticiones por minuto
2. **Tiempo de respuesta:** Cada llamada tarda varios segundos
3. **Coste de API:** Evita llamadas innecesarias
4. **Resiliencia:** Si Yahoo falla, podemos usar datos cacheados

---

## 📍 Dónde vive el cache

### **Ubicación:**
- **Archivo:** `app/services/yahoo_finance_cache.py`
- **Variable global:** `_cache` (diccionario en memoria)

### **Estructura del cache:**
```python
_cache = {
    ("stocks", "AAPL", "1d"): {
        "data": [...],  # Lista de velas OHLCV
        "timestamp": datetime(2024, 1, 1, 10, 0, 0),
        "expires_at": datetime(2024, 1, 1, 10, 5, 0)  # 5 minutos después
    },
    ("cedears", "AAPL.BA", "1d"): {...},
    ...
}
```

### **Clave del cache:**
- **Formato:** Tupla `(market, symbol, timeframe)`
- **Ejemplo:** `("stocks", "AAPL", "1d")`
- **Normalización:** Todo en minúsculas/mayúsculas consistente

### **Características:**
- ✅ **En memoria:** No persiste entre reinicios del servidor
- ✅ **Global:** Compartido entre todas las peticiones
- ✅ **Thread-safe básico:** Python GIL maneja concurrencia básica

---

## ⏱️ Duración del cache

### **Configuración:**
- **Duración:** 5 minutos (300 segundos)
- **Constante:** `CACHE_DURATION_SECONDS = 300`

### **¿Cómo funciona la expiración?**
1. Cuando se guarda en cache, se calcula `expires_at = ahora + 5 minutos`
2. Cuando se consulta, se compara `ahora` con `expires_at`
3. Si `ahora > expires_at` → Cache expirado, se elimina automáticamente

### **Ejemplo:**
```
10:00:00 - Se guarda cache para AAPL
10:05:00 - Cache aún válido
10:05:01 - Cache expirado, se elimina automáticamente
```

---

## 🔄 Cómo se invalida el cache

### **1. Por tiempo (automático):**
- Después de 5 minutos, el cache expira
- La próxima consulta elimina el cache expirado
- No requiere acción manual

### **2. Por nueva consulta exitosa:**
- Si se obtienen nuevos datos de Yahoo Finance
- El cache anterior se sobrescribe con los nuevos datos
- Timestamp y expires_at se actualizan

### **3. Manualmente (funciones de utilidad):**
```python
# Limpiar todo el cache
clear_cache()

# Limpiar cache de un mercado específico
clear_cache(market="stocks")

# Limpiar cache de un símbolo específico
clear_cache(symbol="AAPL")

# Limpiar cache de un timeframe específico
clear_cache(timeframe="1d")
```

---

## 🔍 Flujo completo del cache

### **Escenario 1: Cache válido (no llamar a Yahoo)**

```
1. Cliente pide: AAPL, stocks, 1d
   ↓
2. get_from_cache("stocks", "AAPL", "1d")
   ↓
3. Cache encontrado y válido (< 5 minutos)
   ↓
4. Devolver datos del cache inmediatamente
   ↓
5. NO llamar a Yahoo Finance ✅
```

**Beneficio:** Respuesta instantánea, sin petición HTTP

---

### **Escenario 2: Cache expirado o no existe (llamar a Yahoo)**

```
1. Cliente pide: AAPL, stocks, 1d
   ↓
2. get_from_cache("stocks", "AAPL", "1d")
   ↓
3. Cache no existe o expirado
   ↓
4. Llamar a Yahoo Finance API
   ↓
5. Yahoo responde correctamente
   ↓
6. Guardar en cache: save_to_cache(...)
   ↓
7. Devolver datos al cliente
```

**Beneficio:** Datos actualizados, cache renovado

---

### **Escenario 3: Yahoo devuelve 429 (Rate Limit)**

```
1. Cliente pide: AAPL, stocks, 1d
   ↓
2. get_from_cache() → No hay cache válido
   ↓
3. Llamar a Yahoo Finance API
   ↓
4. Yahoo responde 429 (Rate Limit)
   ↓
5. get_last_cache() → Buscar cache aunque esté expirado
   ↓
6a. Si hay cache expirado:
    → Devolver cache expirado (mejor que fallar)
    → Incluir mensaje educativo (opcional)
    
6b. Si no hay cache:
    → Devolver error educativo claro
```

**Beneficio:** Resiliencia ante rate limiting de Yahoo

---

## ⚠️ Qué pasa si Yahoo falla

### **Caso 1: Error 429 (Rate Limit) con cache disponible**

**Comportamiento:**
1. Yahoo devuelve error 429
2. Se busca cache (incluso expirado)
3. Si existe cache, se devuelve con advertencia implícita
4. Cliente recibe datos (aunque no sean los más recientes)

**Mensaje (implícito en el código):**
- Los datos son del cache (pueden tener hasta 5+ minutos de antigüedad)
- Yahoo está limitando peticiones

---

### **Caso 2: Error 429 sin cache**

**Comportamiento:**
1. Yahoo devuelve error 429
2. No hay cache disponible (nunca se consultó antes)
3. Se devuelve error educativo claro

**Mensaje:**
```
"Yahoo Finance está temporalmente no disponible por exceso de peticiones 
(rate limit). No hay datos en cache para AAPL. 
Intenta de nuevo en unos minutos."
```

---

### **Caso 3: Otro error (404, 500, timeout)**

**Comportamiento:**
1. Yahoo devuelve error (404, 500, timeout)
2. **NO se usa cache automáticamente** (solo para 429)
3. Se propaga el error al cliente

**Razón:**
- Error 404: Símbolo no existe (cache no ayudaría)
- Error 500: Problema del servidor (puede ser temporal)
- Timeout: Problema de conexión (cache no sería útil si la conexión falló)

---

## 🔐 Scope del cache

### **Solo aplica a:**
- ✅ `market="stocks"` → Cache activado
- ✅ `market="cedears"` → Cache activado

### **NO aplica a:**
- ❌ `market="crypto"` → Binance no usa cache
  - Binance tiene mejor rate limiting
  - Datos de crypto cambian muy rápido
  - Cache podría ser contraproducente

---

## 📊 Ejemplo práctico

### **Primera consulta (sin cache):**

```
10:00:00 - GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
   ↓
10:00:02 - get_from_cache() → None (no hay cache)
   ↓
10:00:03 - Llamada a Yahoo Finance
   ↓
10:00:05 - Yahoo responde con datos
   ↓
10:00:05 - save_to_cache() → Guarda cache hasta 10:05:05
   ↓
10:00:05 - Devuelve datos al cliente
```

**Resultado:** Cache creado, expira a las 10:05:05

---

### **Segunda consulta (mismo activo, dentro de 5 minutos):**

```
10:02:00 - GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
   ↓
10:02:00 - get_from_cache() → Datos encontrados (válidos hasta 10:05:05)
   ↓
10:02:00 - Devuelve datos del cache inmediatamente
   ↓
NO se llama a Yahoo Finance ✅
```

**Resultado:** Respuesta instantánea, 0 peticiones a Yahoo

---

### **Tercera consulta (después de 5 minutos):**

```
10:06:00 - GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
   ↓
10:06:00 - get_from_cache() → Cache expirado (10:05:05 < 10:06:00)
   ↓
10:06:00 - Cache eliminado automáticamente
   ↓
10:06:01 - Llamada a Yahoo Finance (renovar cache)
   ↓
10:06:03 - Yahoo responde
   ↓
10:06:03 - save_to_cache() → Nuevo cache hasta 10:11:03
   ↓
10:06:03 - Devuelve datos al cliente
```

**Resultado:** Cache renovado, nuevo período de 5 minutos

---

### **Cuarta consulta (Yahoo devuelve 429):**

```
10:08:00 - GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
   ↓
10:08:00 - get_from_cache() → Cache válido hasta 10:11:03
   ↓
10:08:00 - Devuelve datos del cache (Yahoo nunca se llama)
```

**Resultado:** Cache protege contra rate limiting

---

### **Quinta consulta (Yahoo devuelve 429, cache expirado pero existe):**

```
10:12:00 - GET /api/analysis?market=stocks&symbol=AAPL&timeframe=1d
   ↓
10:12:00 - get_from_cache() → Cache expirado (se elimina)
   ↓
10:12:01 - Llamada a Yahoo Finance
   ↓
10:12:02 - Yahoo responde 429 (Rate Limit)
   ↓
10:12:02 - get_last_cache() → Busca cache aunque expirado
   ↓
10:12:02 - Cache encontrado (aunque expirado)
   ↓
10:12:02 - Devuelve cache expirado al cliente
```

**Resultado:** Resiliencia - datos antiguos mejor que error

---

## 🛠️ Funciones del cache

### **1. `get_from_cache(market, symbol, timeframe)`**
- Busca cache válido (no expirado)
- Retorna datos o `None`

### **2. `save_to_cache(market, symbol, timeframe, data)`**
- Guarda datos en cache
- Calcula expiración (ahora + 5 minutos)
- Sobrescribe cache anterior si existe

### **3. `get_last_cache(market, symbol, timeframe)`**
- Busca cache aunque esté expirado
- Útil para error 429

### **4. `clear_cache(...)`**
- Limpia cache según filtros
- Útil para mantenimiento

### **5. `get_cache_info()`**
- Información del estado del cache
- Útil para debugging

---

## 📝 Resumen

### **Dónde vive el cache:**
- **Módulo:** `app/services/yahoo_finance_cache.py`
- **Variable:** `_cache` (diccionario global en memoria)
- **Clave:** Tupla `(market, symbol, timeframe)`

### **Cómo se invalida:**
- **Automáticamente:** Después de 5 minutos (expiración por tiempo)
- **Automáticamente:** Cuando se obtienen nuevos datos (sobrescritura)
- **Manualmente:** Función `clear_cache()` para limpieza

### **Qué pasa si Yahoo falla:**
- **Error 429 + Cache disponible:** Devuelve cache (incluso expirado)
- **Error 429 + Sin cache:** Error educativo claro
- **Otros errores:** Se propagan normalmente (sin usar cache)

---

## ✅ Beneficios del cache

1. **Reducción de peticiones:** Menos llamadas a Yahoo Finance
2. **Mejor performance:** Respuestas instantáneas desde cache
3. **Resiliencia:** Funciona aunque Yahoo tenga rate limiting
4. **Simplicidad:** Cache en memoria, fácil de entender y mantener
5. **Selectivo:** Solo aplica a stocks/cedears, no afecta crypto

---

**El cache hace la API más rápida y resiliente ante problemas de Yahoo Finance.** 🚀
