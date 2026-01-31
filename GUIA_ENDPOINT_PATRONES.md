# 📚 Guía del Endpoint de Análisis de Patrones

Esta guía explica **paso a paso** cómo funciona el endpoint de análisis de patrones de velas japonesas.

---

## 🎯 ¿Qué hace este endpoint?

El endpoint `/api/analysis/patrones` analiza velas OHLCV y detecta patrones básicos de velas japonesas:
- **Martillo** (señal alcista potencial)
- **Doji** (indecisión del mercado)
- **Envolvente Alcista** (reversión potencial)

**IMPORTANTE:** Es solo educativo. NO da recomendaciones de compra o venta.

---

## 📍 Dónde está el código

El endpoint está en:
- **Archivo**: `app/api/analysis.py`
- **Función**: `analizar_patrones_velas()`
- **Ruta**: `POST /api/analysis/patrones`

---

## 🔄 Paso a Paso: ¿Cómo funciona?

### **Paso 1: El usuario hace una petición**

El usuario envía una petición HTTP POST a la URL:
```
POST http://localhost:8000/api/analysis/patrones
```

Con un cuerpo JSON que contiene velas:
```json
{
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
```

**¿Qué significa cada campo?**
- `open`: Precio cuando abrió el período (ej: "100 dólares")
- `high`: Precio más alto durante el período (ej: "105 dólares")
- `low`: Precio más bajo durante el período (ej: "99 dólares")
- `close`: Precio cuando cerró el período (ej: "104 dólares")
- `volume`: Cantidad de transacciones (opcional)

---

### **Paso 2: Validación de datos**

Antes de procesar, el sistema **valida** que los datos sean correctos usando `VelaSchema`:

**Validaciones que hace:**
- ✅ Los precios deben ser números positivos
- ✅ `high` debe ser el precio más alto
- ✅ `low` debe ser el precio más bajo
- ✅ Debe haber al menos 1 vela
- ✅ Máximo 100 velas (para no sobrecargar)

**Si algo está mal:** El sistema devuelve un error claro explicando qué falló.

**Analogía:** Es como un portero que revisa las entradas antes de dejar pasar.

---

### **Paso 3: Conversión de datos**

El endpoint convierte los datos validados (objetos Pydantic) a diccionarios simples de Python:

```python
# De esto (Pydantic):
VelaSchema(open=100, high=105, low=99, close=104)

# A esto (diccionario):
{"open": 100, "high": 105, "low": 99, "close": 104}
```

**¿Por qué?** Porque el servicio de análisis (`candlestick_patterns.py`) usa diccionarios simples, no objetos Pydantic.

---

### **Paso 4: Análisis de patrones**

Se llama a la función `analizar_patrones()` del servicio (`app/services/candlestick_patterns.py`).

**¿Qué hace esta función?**

1. **Analiza cada vela individualmente:**
   - Verifica si es un **Martillo**
   - Verifica si es un **Doji**

2. **Analiza pares de velas:**
   - Verifica si hay un **Envolvente Alcista** (necesita 2 velas)

3. **Construye una lista de patrones detectados** con:
   - Nombre del patrón
   - Tipo (alcista, bajista, indecisión)
   - Descripción técnica
   - Explicación simple
   - Datos técnicos (medidas, proporciones)
   - Recordatorio educativo

---

### **Paso 5: Agregar aviso legal**

El endpoint agrega un **aviso legal completo** a la respuesta:

```
⚠️ AVISO LEGAL IMPORTANTE:

Este análisis es exclusivamente con fines educativos...
NO constituye asesoramiento financiero...
```

**¿Por qué?** Porque es obligatorio incluir avisos legales cuando se trata de información financiera.

---

### **Paso 6: Construir la respuesta**

El endpoint construye un objeto `AnalisisPatronesResponse` con:

- `total_velas_analizadas`: Cuántas velas se analizaron
- `patrones_detectados`: Cuántos patrones se encontraron
- `patrones`: Lista de todos los patrones detectados (con explicaciones)
- `mensaje_importante`: Recordatorio de que es solo educativo
- `siguiente_paso_sugerido`: Qué hacer con esta información
- `aviso_legal`: Aviso legal completo

---

### **Paso 7: Devolver la respuesta**

El endpoint devuelve un JSON con toda la información:

```json
{
  "total_velas_analizadas": 7,
  "patrones_detectados": 3,
  "patrones": [
    {
      "patron": "Martillo",
      "tipo": "Potencial Alcista",
      "descripcion": "Este patrón muestra que...",
      "explicacion_simple": "Imagínate que el precio estaba cayendo...",
      "datos_tecnicos": {...},
      "recordatorio_educativo": "...",
      "posicion": 1
    },
    ...
  ],
  "mensaje_importante": "...",
  "siguiente_paso_sugerido": "...",
  "aviso_legal": "..."
}
```

---

## 🚀 Cómo usar el endpoint

### **Opción 1: Usar el endpoint de ejemplo (más fácil)**

No necesitas enviar datos. Solo visita:

```
GET http://localhost:8000/api/analysis/patrones/ejemplo
```

**Esto:** Usa velas precargadas y muestra un análisis completo como ejemplo.

**Útil para:** Entender cómo funciona sin preparar datos.

---

### **Opción 2: Usar tu propio análisis**

#### **Con cURL (terminal):**

```bash
curl -X POST "http://localhost:8000/api/analysis/patrones" \
  -H "Content-Type: application/json" \
  -d '{
    "velas": [
      {"open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
      {"open": 104, "high": 105, "low": 98, "close": 103.5, "volume": 1200}
    ]
  }'
```

#### **Con Python:**

```python
import requests

url = "http://localhost:8000/api/analysis/patrones"
datos = {
    "velas": [
        {"open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
        {"open": 104, "high": 105, "low": 98, "close": 103.5, "volume": 1200}
    ]
}

respuesta = requests.post(url, json=datos)
resultado = respuesta.json()

print(f"Patrones detectados: {resultado['patrones_detectados']}")
for patron in resultado['patrones']:
    print(f"- {patron['patron']}: {patron['tipo']}")
```

#### **Con JavaScript (fetch):**

```javascript
fetch('http://localhost:8000/api/analysis/patrones', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    velas: [
      {open: 100, high: 105, low: 99, close: 104, volume: 1000},
      {open: 104, high: 105, low: 98, close: 103.5, volume: 1200}
    ]
  })
})
.then(response => response.json())
.then(data => {
  console.log('Patrones detectados:', data.patrones_detectados);
  data.patrones.forEach(patron => {
    console.log(`- ${patron.patron}: ${patron.tipo}`);
  });
});
```

#### **Con la documentación interactiva (más fácil):**

1. Inicia el servidor: `python main.py`
2. Abre tu navegador en: `http://localhost:8000/docs`
3. Busca el endpoint `/api/analysis/patrones`
4. Haz clic en "Try it out"
5. Edita el JSON de ejemplo con tus velas
6. Haz clic en "Execute"
7. ¡Ve el resultado!

---

## 📊 Estructura de la respuesta

### **Campos principales:**

- **`total_velas_analizadas`** (número)
  - Cuántas velas se analizaron

- **`patrones_detectados`** (número)
  - Cuántos patrones se encontraron

- **`patrones`** (lista)
  - Cada patrón tiene:
    - `patron`: Nombre del patrón (ej: "Martillo")
    - `tipo`: Tipo de señal (ej: "Potencial Alcista")
    - `descripcion`: Explicación técnica
    - `explicacion_simple`: Explicación en lenguaje simple
    - `datos_tecnicos`: Medidas y cálculos
    - `recordatorio_educativo`: Consejos y advertencias
    - `posicion`: En qué posición de la lista aparece (índice)

- **`mensaje_importante`** (texto)
  - Recordatorio de que es solo educativo

- **`siguiente_paso_sugerido`** (texto)
  - Qué hacer con esta información

- **`aviso_legal`** (texto)
  - Aviso legal completo

---

## ⚠️ Manejo de errores

### **Errores posibles:**

1. **400 Bad Request** - Datos inválidos
   - Ejemplo: Precios negativos, `high` menor que `low`
   - **Solución:** Revisa el formato de tus velas

2. **422 Unprocessable Entity** - Validación fallida
   - Ejemplo: Falta un campo requerido
   - **Solución:** Asegúrate de incluir todos los campos (open, high, low, close)

3. **500 Internal Server Error** - Error del servidor
   - Ejemplo: Bug en el código
   - **Solución:** Revisa los logs del servidor

---

## 🔍 Ejemplo completo

### **Entrada (lo que envías):**

```json
{
  "velas": [
    {"open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
    {"open": 104, "high": 105, "low": 98, "close": 103.5, "volume": 1200}
  ]
}
```

### **Salida (lo que recibes):**

```json
{
  "total_velas_analizadas": 2,
  "patrones_detectados": 1,
  "patrones": [
    {
      "patron": "Martillo",
      "tipo": "Potencial Alcista",
      "descripcion": "Este patrón muestra que aunque hubo mucha presión...",
      "explicacion_simple": "Imagínate que el precio estaba cayendo...",
      "datos_tecnicos": {
        "cuerpo": 0.5,
        "sombra_inferior": 5.5,
        "sombra_superior": 1.5,
        "proporcion_sombra_cuerpo": 11.0
      },
      "recordatorio_educativo": "Este patrón es más confiable cuando...",
      "posicion": 1
    }
  ],
  "mensaje_importante": "⚠️ RECORDATORIO: Estos patrones son herramientas...",
  "siguiente_paso_sugerido": "Para usar este análisis: observa los patrones...",
  "aviso_legal": "⚠️ AVISO LEGAL IMPORTANTE: ..."
}
```

---

## 💡 Consejos de uso

1. **Empieza con el ejemplo:** Usa `/patrones/ejemplo` para entender el formato

2. **Revisa la documentación:** Visita `/docs` para ver todos los endpoints

3. **Valida tus datos:** Asegúrate de que `high >= open, close, low` y `low <= open, close, high`

4. **Lee las explicaciones:** Los patrones incluyen explicaciones educativas valiosas

5. **Recuerda:** Es solo educativo. No es un consejo de inversión.

---

## 🎓 Para aprender más

- **¿Qué es OHLCV?** Busca "velas japonesas" o "candlestick charts"
- **¿Cómo leer velas?** Cada vela muestra cómo se movió el precio en un período
- **¿Qué significan los patrones?** Cada patrón sugiere algo, pero no es garantía

---

¿Tienes dudas? ¡Pregunta!
