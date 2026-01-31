# 🪙 Guía del Endpoint de Análisis de Bitcoin

Esta guía explica cómo usar el endpoint que analiza Bitcoin con datos reales desde Binance.

---

## 🎯 ¿Qué hace este endpoint?

El endpoint `GET /api/analysis/bitcoin` obtiene **datos reales de Bitcoin** desde Binance, analiza patrones de velas japonesas y devuelve un análisis educativo completo.

**Características:**
- ✅ Datos REALES y en TIEMPO REAL de Bitcoin
- ✅ Obtiene precios desde Binance (API pública)
- ✅ Analiza patrones de velas japonesas
- ✅ Explicaciones educativas claras
- ✅ Aviso legal incluido

---

## 📍 URL del Endpoint

```
GET http://localhost:8000/api/analysis/bitcoin
```

---

## 🌐 Cómo probarlo desde el navegador

### **Opción 1: Con parámetros por defecto (más fácil)**

1. **Asegúrate de que el servidor esté corriendo:**
   ```bash
   python main.py
   ```

2. **Abre tu navegador** (Chrome, Firefox, Edge, etc.)

3. **Visita esta URL:**
   ```
   http://localhost:8000/api/analysis/bitcoin
   ```

4. **Verás un JSON** con el análisis completo de Bitcoin

---

### **Opción 2: Con parámetros personalizados**

Puedes agregar parámetros a la URL para cambiar el análisis:

#### **Ejemplo 1: Velas de 1 minuto (últimas 60 velas)**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=1m&limite=60
```
Esto analiza las últimas 60 velas de 1 minuto (última hora).

#### **Ejemplo 2: Velas diarias (últimos 30 días)**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=1d&limite=30
```
Esto analiza las últimas 30 velas de 1 día (último mes).

#### **Ejemplo 3: Velas de 4 horas (últimas 50 velas)**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=4h&limite=50
```
Esto analiza las últimas 50 velas de 4 horas (últimos ~8 días).

---

### **Opción 3: Usar la documentación interactiva (recomendado)**

1. **Inicia el servidor:**
   ```bash
   python main.py
   ```

2. **Abre tu navegador en:**
   ```
   http://localhost:8000/docs
   ```

3. **Busca el endpoint** `/api/analysis/bitcoin`

4. **Haz clic en "Try it out"**

5. **Edita los parámetros** (opcional):
   - `timeframe`: Cambia el período (ej: "1h", "1d", "4h")
   - `limite`: Cambia la cantidad de velas (ej: 50, 100, 200)

6. **Haz clic en "Execute"**

7. **Verás la respuesta** completa con el análisis

---

## 📊 Parámetros disponibles

### **`timeframe`** (opcional)
- **Descripción:** Período de cada vela
- **Valor por defecto:** `"1h"` (1 hora)
- **Valores válidos:**
  - `"1m"` - 1 minuto
  - `"5m"` - 5 minutos
  - `"15m"` - 15 minutos
  - `"30m"` - 30 minutos
  - `"1h"` - 1 hora (por defecto)
  - `"4h"` - 4 horas
  - `"1d"` - 1 día
  - `"1w"` - 1 semana

**Ejemplo en la URL:**
```
?timeframe=1h
```

### **`limite`** (opcional)
- **Descripción:** Cantidad de velas a analizar
- **Valor por defecto:** `100`
- **Rango:** 1 a 1000

**Ejemplo en la URL:**
```
?limite=50
```

### **Combinando parámetros:**

Cuando usas múltiples parámetros, sepáralos con `&`:
```
?timeframe=1d&limite=30
```

---

## 📋 Formato de la respuesta

El endpoint devuelve un JSON con esta estructura:

```json
{
  "activo": "BTCUSDT",
  "activo_nombre": "Bitcoin (BTC) / Tether (USDT)",
  "timeframe": "1h",
  "precio_actual": 65000.00,
  "precio_apertura_periodo": 64000.00,
  "precio_cierre_periodo": 65000.00,
  "cambio_precio": 1000.00,
  "cambio_porcentual": 1.56,
  "tendencia_general": "Alcista",
  "interpretacion_tendencia": "...",
  "total_velas_analizadas": 100,
  "patrones_detectados": 2,
  "patrones": [
    {
      "patron": "Martillo",
      "tipo": "Potencial Alcista",
      "descripcion": "...",
      "explicacion_simple": "...",
      "datos_tecnicos": {...},
      "posicion": 45
    }
  ],
  "interpretacion_simple": "...",
  "contexto_general": {
    "periodo_analizado": "100 velas de 1h",
    "precio_minimo": 63500.00,
    "precio_maximo": 66000.00,
    "rango_precio": 2500.00,
    "volumen_promedio": 1234.56
  },
  "aviso_legal": "...",
  "fuente_datos": "Binance API (pública)"
}
```

---

## 🔍 Campos importantes de la respuesta

### **Información del activo:**
- `activo`: Par de trading (BTCUSDT)
- `precio_actual`: Precio actual de Bitcoin (USD)

### **Análisis de tendencia:**
- `tendencia_general`: "Alcista", "Bajista" o "Lateral"
- `cambio_porcentual`: Cambio de precio en porcentaje

### **Patrones detectados:**
- `patrones_detectados`: Cantidad de patrones encontrados
- `patrones`: Lista de patrones con explicaciones educativas

### **Contexto:**
- `contexto_general`: Estadísticas del período analizado
- `interpretacion_simple`: Explicación general en lenguaje simple

---

## 💡 Ejemplos prácticos

### **Ejemplo 1: Análisis rápido (última hora con velas de 1 minuto)**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=1m&limite=60
```
**Qué hace:** Analiza las últimas 60 velas de 1 minuto = última hora de trading

### **Ejemplo 2: Análisis de medio plazo (últimos días)**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=4h&limite=42
```
**Qué hace:** Analiza las últimas 42 velas de 4 horas = últimos 7 días

### **Ejemplo 3: Análisis de largo plazo (últimos meses)**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=1d&limite=90
```
**Qué hace:** Analiza las últimas 90 velas de 1 día = últimos 3 meses

---

## ⚠️ Manejo de errores

### **Error 400: Parámetro inválido**
Si usas un timeframe o límite inválido:
```
http://localhost:8000/api/analysis/bitcoin?timeframe=2h
```
**Error:** `"Parámetro inválido: Timeframe '2h' no es válido"`

**Solución:** Usa un timeframe válido como `"1h"`, `"4h"`, `"1d"`, etc.

### **Error 500: Sin conexión o Binance caído**
Si no hay internet o Binance no responde:
**Error:** `"Error al analizar Bitcoin: Tiempo de espera agotado..."`

**Solución:** Verifica tu conexión a internet e intenta de nuevo

---

## 🧪 Probar desde diferentes lugares

### **Desde el navegador:**
```
http://localhost:8000/api/analysis/bitcoin
```

### **Desde PowerShell (Windows):**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/analysis/bitcoin" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### **Desde cURL:**
```bash
curl http://localhost:8000/api/analysis/bitcoin
```

### **Desde JavaScript (en una página web):**
```javascript
fetch('http://localhost:8000/api/analysis/bitcoin')
  .then(response => response.json())
  .then(data => {
    console.log('Precio actual:', data.precio_actual);
    console.log('Patrones detectados:', data.patrones_detectados);
  });
```

---

## 📱 Mejorar la visualización del JSON en el navegador

Si ves el JSON todo junto y quieres verlo formateado, puedes usar:

### **Opción 1: Extensión del navegador**
- Chrome/Edge: Instala "JSON Formatter" desde Chrome Web Store
- Firefox: Instala "JSONView" desde Firefox Add-ons

### **Opción 2: Usar la documentación interactiva**
Visita `http://localhost:8000/docs` y usa la interfaz de Swagger UI

### **Opción 3: Copiar y pegar en un formateador**
1. Copia el JSON del navegador
2. Pégalo en: https://jsonformatter.org/
3. Ve el JSON formateado y con colores

---

## ✅ Checklist para probar

- [ ] Servidor corriendo (`python main.py`)
- [ ] Visitar `http://localhost:8000/api/analysis/bitcoin`
- [ ] Ver JSON con análisis de Bitcoin
- [ ] Verificar que `precio_actual` tenga un valor
- [ ] Verificar que `patrones_detectados` sea un número
- [ ] Leer el `aviso_legal`
- [ ] Probar con diferentes timeframes

---

## 🎓 Qué aprender de la respuesta

1. **Precio actual:** Valor actual de Bitcoin en USD
2. **Tendencia:** Si el precio está subiendo, bajando o lateral
3. **Patrones:** Qué patrones de velas japonesas aparecen
4. **Contexto:** Rango de precios y volatilidad del período

**Recuerda:** Todo esto es solo educativo. NO es una recomendación de inversión.

---

## 🔗 URL completa con ejemplos

### **Básico (valores por defecto):**
```
http://localhost:8000/api/analysis/bitcoin
```

### **Última hora (60 velas de 1 minuto):**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=1m&limite=60
```

### **Último mes (30 velas de 1 día):**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=1d&limite=30
```

### **Última semana (42 velas de 4 horas):**
```
http://localhost:8000/api/analysis/bitcoin?timeframe=4h&limite=42
```

---

¿Listo para analizar Bitcoin en tiempo real? ¡Prueba el endpoint ahora!
