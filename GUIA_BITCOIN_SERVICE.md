# 📊 Guía del Servicio de Precios de Bitcoin

Esta guía explica cómo funciona el servicio que obtiene velas reales de Bitcoin desde Binance.

---

## 🎯 ¿Qué hace este servicio?

El servicio `bitcoin_price_service.py` obtiene **datos reales de precios de Bitcoin** desde la API pública de Binance y los convierte al formato que usa nuestro motor de análisis de patrones.

**IMPORTANTE:** 
- Es completamente gratuito
- NO requiere cuenta en Binance
- Usa la API pública (no necesita autenticación)
- Los datos son en tiempo real

---

## 📁 Archivo

**Ubicación:** `app/services/bitcoin_price_service.py`

---

## 🔄 ¿Cómo funciona? (Paso a paso)

### **Paso 1: Configuración**

El servicio define:
- La URL de la API de Binance
- Los timeframes permitidos (1h, 1d, etc.)
- Formatos de conversión de datos

### **Paso 2: Función principal `obtener_velas_bitcoin()`**

Cuando llamas a esta función:

1. **Valida los parámetros:**
   - Verifica que el timeframe sea válido (ej: "1h", "1d")
   - Verifica que el límite esté entre 1 y 1000 velas

2. **Construye la URL:**
   ```
   https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100
   ```
   - `symbol`: El par de trading (BTCUSDT = Bitcoin/USDT)
   - `interval`: El timeframe (1h = 1 hora)
   - `limit`: Cuántas velas queremos

3. **Hace la petición HTTP:**
   - Usa `httpx` para hacer una petición GET a Binance
   - Espera la respuesta (async/await para no bloquear el servidor)

4. **Recibe los datos:**
   - Binance devuelve un JSON con las velas
   - Cada vela es una lista con muchos datos

5. **Convierte el formato:**
   - Binance devuelve: `[timestamp, "50000", "51000", "49500", "50500", "1234.56", ...]`
   - Convertimos a: `{"open": 50000.0, "high": 51000.0, "low": 49500.0, "close": 50500.0, "volume": 1234.56}`
   - Esto es necesario porque nuestro motor de patrones usa este formato

6. **Devuelve la lista de velas:**
   - Lista lista para usar en `analizar_patrones()`

---

## 📖 Cómo usar el servicio

### **Ejemplo básico:**

```python
from app.services.bitcoin_price_service import obtener_velas_bitcoin

# Obtener las últimas 100 velas de 1 hora
velas = await obtener_velas_bitcoin(
    timeframe="1h",    # Velas de 1 hora
    limite=100         # Últimas 100 velas
)

# Ahora puedes analizar estos datos reales
from app.services.candlestick_patterns import analizar_patrones
resultado = analizar_patrones(velas)
```

### **Con diferentes timeframes:**

```python
# Velas de 1 minuto (últimas 60 velas = última hora)
velas_1m = await obtener_velas_bitcoin(timeframe="1m", limite=60)

# Velas de 1 día (últimas 30 velas = último mes)
velas_1d = await obtener_velas_bitcoin(timeframe="1d", limite=30)

# Velas de 4 horas (últimas 50 velas = últimos ~8 días)
velas_4h = await obtener_velas_bitcoin(timeframe="4h", limite=50)
```

### **Formato completo (con información extra):**

```python
from app.services.bitcoin_price_service import obtener_velas_bitcoin_formato_analisis

resultado = await obtener_velas_bitcoin_formato_analisis(
    timeframe="1h",
    limite=100
)

# resultado contiene:
# {
#     "velas": [...],           # Lista de velas
#     "total": 100,             # Cantidad
#     "timeframe": "1h",        # Timeframe usado
#     "simbolo": "BTCUSDT",     # Par de trading
#     "ultima_vela": {...},     # Última vela (más reciente)
#     "descripcion": "..."      # Descripción
# }
```

---

## ⚙️ Parámetros disponibles

### **`obtener_velas_bitcoin()`**

- **`timeframe`** (str, opcional): Período de cada vela
  - Valores: `"1m"`, `"3m"`, `"5m"`, `"15m"`, `"30m"`, `"1h"`, `"2h"`, `"4h"`, `"6h"`, `"8h"`, `"12h"`, `"1d"`, `"3d"`, `"1w"`, `"1M"`
  - Por defecto: `"1h"` (1 hora)

- **`limite`** (int, opcional): Cantidad de velas a obtener
  - Mínimo: 1
  - Máximo: 1000
  - Por defecto: 100

- **`simbolo`** (str, opcional): Par de trading
  - Por defecto: `"BTCUSDT"` (Bitcoin/USDT)
  - Otros ejemplos: `"ETHUSDT"` (Ethereum), `"ADAUSDT"` (Cardano)

---

## 🔍 Timeframes disponibles

| Timeframe | Descripción | Ejemplo: 100 velas = |
|-----------|-------------|----------------------|
| `1m` | 1 minuto | Últimas 100 minutos |
| `5m` | 5 minutos | Últimas 500 minutos (~8 horas) |
| `15m` | 15 minutos | Últimas 1500 minutos (25 horas) |
| `1h` | 1 hora | Últimas 100 horas (~4 días) |
| `4h` | 4 horas | Últimas 400 horas (~16 días) |
| `1d` | 1 día | Últimos 100 días (~3 meses) |
| `1w` | 1 semana | Últimas 100 semanas (~2 años) |

---

## ⚠️ Manejo de errores

El servicio maneja errores de forma simple y clara:

### **Error 1: Timeframe inválido**
```python
# ❌ Esto dará error
velas = await obtener_velas_bitcoin(timeframe="2h")  # ❌ "2h" no existe, usa "1h" o "3h"

# ✅ Esto funciona
velas = await obtener_velas_bitcoin(timeframe="1h")  # ✅
```

**Mensaje:** `"Timeframe '2h' no es válido. Timeframes permitidos: 1m, 3m, ..."`

### **Error 2: Límite fuera de rango**
```python
# ❌ Esto dará error
velas = await obtener_velas_bitcoin(limite=2000)  # ❌ Máximo es 1000

# ✅ Esto funciona
velas = await obtener_velas_bitcoin(limite=500)  # ✅
```

**Mensaje:** `"El límite debe estar entre 1 y 1000 velas"`

### **Error 3: Sin conexión a internet**
```python
# Si no hay internet o Binance está caído
velas = await obtener_velas_bitcoin()

# Error: "Tiempo de espera agotado al conectarse a Binance..."
```

### **Error 4: Símbolo inválido**
```python
# ❌ Esto dará error si el símbolo no existe
velas = await obtener_velas_bitcoin(simbolo="BITCOIN123")  # ❌ No existe

# ✅ Esto funciona
velas = await obtener_velas_bitcoin(simbolo="BTCUSDT")  # ✅
```

---

## 🔗 Formato de datos

### **Entrada (lo que Binance devuelve):**
```json
[
  [
    1234567890000,        // Timestamp
    "50000.00",           // Open (string)
    "51000.00",           // High (string)
    "49500.00",           // Low (string)
    "50500.00",           // Close (string)
    "1234.56",            // Volume (string)
    // ... más datos que no usamos
  ],
  // ... más velas
]
```

### **Salida (lo que devuelve nuestro servicio):**
```python
[
  {
    "open": 50000.0,      # float (número decimal)
    "high": 51000.0,
    "low": 49500.0,
    "close": 50500.0,
    "volume": 1234.56
  },
  # ... más velas
]
```

**¿Por qué convertimos?**
- Binance devuelve strings (texto): `"50000.00"`
- Nuestro motor necesita floats (números): `50000.0`
- Es más fácil trabajar con números para hacer cálculos

---

## 🧪 Probar el servicio

Puedes probar el servicio directamente:

```bash
python app/services/bitcoin_price_service.py
```

Esto ejecutará una prueba que:
- Obtiene 10 velas de Bitcoin
- Muestra las primeras 3
- Muestra la última (más reciente)
- Muestra información adicional

---

## 💡 Ejemplos de uso real

### **Ejemplo 1: Análisis de última hora**
```python
# Obtener velas de la última hora (1 minuto cada una)
velas_1m = await obtener_velas_bitcoin(timeframe="1m", limite=60)

# Analizar patrones
resultado = analizar_patrones(velas_1m)
print(f"Patrones detectados: {resultado['patrones_detectados']}")
```

### **Ejemplo 2: Análisis diario**
```python
# Obtener velas del último mes (1 día cada una)
velas_1d = await obtener_velas_bitcoin(timeframe="1d", limite=30)

# Analizar tendencias a largo plazo
resultado = analizar_patrones(velas_1d)
```

### **Ejemplo 3: Combinar con análisis**
```python
# 1. Obtener datos reales
velas = await obtener_velas_bitcoin(timeframe="1h", limite=100)

# 2. Analizar patrones
from app.services.candlestick_patterns import analizar_patrones
analisis = analizar_patrones(velas)

# 3. Mostrar resultados
for patron in analisis['patrones']:
    print(f"Patrón: {patron['patron']}")
    print(f"Explicación: {patron['explicacion_simple']}")
```

---

## ⚡ Ventajas del servicio

1. **Datos reales:** No son datos de ejemplo, son precios reales de Bitcoin
2. **Tiempo real:** Los datos están actualizados constantemente
3. **Gratis:** No requiere cuenta ni API key
4. **Simple:** Solo necesitas especificar timeframe y cantidad
5. **Compatible:** El formato es compatible con nuestro motor de análisis
6. **Robusto:** Maneja errores de forma clara

---

## 🔐 Seguridad y privacidad

- ✅ **No requiere autenticación** para obtener velas públicas
- ✅ **No envía datos personales** a Binance
- ✅ **Solo lee datos públicos** (cualquiera puede ver estos precios)
- ✅ **No realiza transacciones** (solo lee información)

---

## 📚 Referencias

- **API de Binance:** https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
- **Documentación de httpx:** https://www.python-httpx.org/

---

¿Listo para usar datos reales de Bitcoin? ¡Integremos esto con un endpoint!
