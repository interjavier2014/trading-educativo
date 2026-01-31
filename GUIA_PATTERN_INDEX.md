# 📍 Guía de pattern_index para Visualización

Esta guía explica cómo usar `pattern_index` en el frontend para visualizar patrones en gráficos de velas.

---

## 🎯 ¿Qué es pattern_index?

`pattern_index` es un índice relativo que indica la posición de un patrón dentro de la serie de velas, usando **indexación desde el final**.

- **`-1`** = Última vela (más reciente)
- **`-2`** = Penúltima vela
- **`-3`** = Antepenúltima vela
- etc.

---

## 📊 Comparación: posicion vs pattern_index

### **`posicion` (índice 0-based):**
- `0` = Primera vela (más antigua)
- `99` = Última vela (en una serie de 100 velas)

### **`pattern_index` (índice desde el final):**
- `-100` = Primera vela (en una serie de 100 velas)
- `-1` = Última vela (siempre la misma, independiente del total)

---

## 💡 ¿Por qué es útil pattern_index?

### **Ventajas:**
1. **Visualización simplificada:** Saber que `-1` es "la última vela" sin calcular
2. **Índices consistentes:** Un patrón en `-1` siempre es reciente, sin importar cuántas velas hay
3. **Marcado en gráficos:** Fácil marcar patrones recientes en la visualización
4. **Lógica clara:** `-1` es más intuitivo que calcular `total - 1`

---

## 📋 Estructura de datos

### **Ejemplo de respuesta:**
```json
{
  "total_velas_analizadas": 100,
  "patrones_detectados": 2,
  "patrones": [
    {
      "pattern_code": "HAMMER",
      "context_code": "POTENTIAL_BULLISH",
      "confidence": "MEDIUM",
      "datos_tecnicos": {...},
      "posicion": 45,        // Índice 0-based: vela 45 de 100
      "pattern_index": -56   // Índice desde el final: 45 - 100 = -56
    },
    {
      "pattern_code": "DOJI_STANDARD",
      "context_code": "INDECISION",
      "confidence": "LOW",
      "datos_tecnicos": {...},
      "posicion": 99,        // Índice 0-based: última vela (99 de 100)
      "pattern_index": -1    // Índice desde el final: 99 - 100 = -1
    }
  ]
}
```

---

## 🔧 Cómo usar pattern_index en el frontend

### **Ejemplo 1: JavaScript/TypeScript**

```javascript
// Obtener el índice absoluto para acceder al array de velas
function getAbsoluteIndex(patternIndex, totalVelas) {
  // pattern_index es negativo, convertir a índice positivo
  return totalVelas + patternIndex;
}

// Ejemplo: Si pattern_index = -1 y total_velas = 100
const absoluteIndex = getAbsoluteIndex(-1, 100); // Resultado: 99

// Acceder a la vela en el array
const vela = velasArray[absoluteIndex]; // Última vela
```

### **Ejemplo 2: React/Visualización**

```javascript
// Marcar patrones recientes en un gráfico
function renderPatterns(patrones, totalVelas) {
  return patrones.map(patron => {
    // Convertir pattern_index a posición absoluta
    const absoluteIndex = totalVelas + patron.pattern_index;
    
    // Determinar si es un patrón reciente (últimas 5 velas)
    const isRecent = patron.pattern_index >= -5;
    
    return (
      <PatternMarker
        key={patron.pattern_index}
        index={absoluteIndex}
        patternCode={patron.pattern_code}
        confidence={patron.confidence}
        isRecent={isRecent}
        style={isRecent ? { opacity: 1 } : { opacity: 0.5 }}
      />
    );
  });
}
```

### **Ejemplo 3: Detectar patrones recientes**

```javascript
// Filtrar solo patrones en las últimas 10 velas
function getRecentPatterns(patrones) {
  return patrones.filter(patron => patron.pattern_index >= -10);
}

// Detectar si hay un patrón en la última vela (más reciente)
function hasPatternInLastCandle(patrones) {
  return patrones.some(patron => patron.pattern_index === -1);
}
```

---

## 📍 Casos de uso prácticos

### **Caso 1: Resaltar patrones recientes**
```javascript
// Dar mayor importancia visual a patrones en las últimas 5 velas
patrones.forEach(patron => {
  if (patron.pattern_index >= -5) {
    // Patrón reciente: usar color más intenso, animación, etc.
    highlightRecentPattern(patron);
  }
});
```

### **Caso 2: Tooltip con distancia temporal**
```javascript
// Mostrar cuántas velas atrás está el patrón
function getPatternDistanceText(patternIndex) {
  const distance = Math.abs(patternIndex);
  
  if (distance === 1) return "Hace 1 vela (más reciente)";
  if (distance === 2) return "Hace 2 velas";
  return `Hace ${distance} velas`;
}

// pattern_index = -3 → "Hace 3 velas"
```

### **Caso 3: Filtrado en UI**
```javascript
// Botones de filtro para el usuario
const filters = {
  all: () => true,
  recent: (patron) => patron.pattern_index >= -10,
  veryRecent: (patron) => patron.pattern_index >= -3,
  lastCandle: (patron) => patron.pattern_index === -1
};
```

---

## 🔢 Conversión entre índices

### **De pattern_index a posicion:**
```javascript
function patternIndexToPosicion(patternIndex, totalVelas) {
  return totalVelas + patternIndex;
}

// Ejemplo: pattern_index = -5, total = 100
// Resultado: posicion = 95
```

### **De posicion a pattern_index:**
```javascript
function posicionToPatternIndex(posicion, totalVelas) {
  return posicion - totalVelas;
}

// Ejemplo: posicion = 95, total = 100
// Resultado: pattern_index = -5
```

---

## 📊 Ejemplo completo de visualización

```javascript
// Componente React para mostrar patrones
function CandlestickChart({ velas, patrones, totalVelas }) {
  return (
    <Chart>
      {velas.map((vela, index) => {
        // Buscar patrones en esta vela
        const patronesEnVela = patrones.filter(
          patron => (totalVelas + patron.pattern_index) === index
        );
        
        return (
          <Candle
            key={index}
            data={vela}
            isRecent={index >= totalVelas - 5}
            patterns={patronesEnVela}
          >
            {patronesEnVela.map(patron => (
              <PatternBadge
                patternCode={patron.pattern_code}
                confidence={patron.confidence}
                isVeryRecent={patron.pattern_index >= -3}
              />
            ))}
          </Candle>
        );
      })}
    </Chart>
  );
}
```

---

## ✅ Reglas de interpretación

1. **`pattern_index === -1`** → Siempre la última vela (más reciente)
2. **`pattern_index < -1`** → Velas más antiguas (cuanto más negativo, más antiguo)
3. **`pattern_index` siempre negativo** → Nunca será 0 o positivo
4. **Valores absolutos mayores** → Patrones más antiguos

### **Fórmula:**
```
pattern_index = posicion - total_velas_analizadas
```

### **Ejemplos con 100 velas:**
- Posición 0 (primera) → pattern_index = 0 - 100 = **-100**
- Posición 50 (mitad) → pattern_index = 50 - 100 = **-50**
- Posición 99 (última) → pattern_index = 99 - 100 = **-1**

---

## 🎨 Recomendaciones para UI

### **1. Visualización por proximidad:**
```javascript
// Mayor opacidad para patrones recientes
const opacity = Math.max(0.3, 1 + (pattern_index / 10));
```

### **2. Colores por recencia:**
```javascript
function getPatternColor(patternIndex) {
  if (patternIndex >= -3) return '#FF0000';  // Rojo: muy reciente
  if (patternIndex >= -10) return '#FFA500'; // Naranja: reciente
  return '#808080';                          // Gris: antiguo
}
```

### **3. Tamaño de marcadores:**
```javascript
// Patrones recientes más grandes
const markerSize = pattern_index >= -5 ? 'large' : 'small';
```

---

## 🔍 Patrones de dos velas (Envolvente Alcista)

Para patrones como `BULLISH_ENGULFING` que involucran dos velas:

```json
{
  "pattern_code": "BULLISH_ENGULFING",
  "posicion": 99,                    // Vela actual (envolvente)
  "pattern_index": -1,               // Vela actual
  "vela_anterior_posicion": 98,      // Vela anterior (envuelta)
  "vela_anterior_pattern_index": -2  // Vela anterior
}
```

**Uso en frontend:**
```javascript
// Dibujar líneas entre las dos velas del patrón
function drawEngulfingPattern(patron) {
  const currentIndex = totalVelas + patron.pattern_index;        // -1 → 99
  const previousIndex = totalVelas + patron.vela_anterior_pattern_index; // -2 → 98
  
  drawConnectionLine(
    velas[previousIndex],
    velas[currentIndex]
  );
}
```

---

## 📝 Resumen

- **`pattern_index`**: Índice relativo desde el final (-1 = última vela)
- **`posicion`**: Índice absoluto 0-based (0 = primera vela)
- **Conversión**: `posicion = totalVelas + pattern_index`
- **Uso principal**: Visualización y filtrado de patrones recientes
- **Siempre negativo**: Valores -1, -2, -3, etc.

---

**El frontend puede usar `pattern_index` para:**
- Identificar rápidamente patrones recientes
- Resaltar visualmente patrones en las últimas velas
- Filtrar patrones por recencia
- Mostrar tooltips con información temporal
- Optimizar renderizado (solo mostrar patrones recientes)
