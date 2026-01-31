"""
Análisis de Patrones de Velas Japonesas - Versión Educativa

Este archivo detecta patrones básicos de velas japonesas y explica
qué significan de forma educativa.

IMPORTANTE: Este análisis es solo educativo. NO es una recomendación
de compra o venta. Solo muestra información para aprender.
"""

from typing import List, Dict, Optional


# ============================================================================
# CÓDIGOS TÉCNICOS (i18n - para traducción en frontend)
# ============================================================================

# Códigos de patrones
PATTERN_HAMMER = "HAMMER"
PATTERN_DOJI_STANDARD = "DOJI_STANDARD"
PATTERN_DOJI_DRAGONFLY = "DOJI_DRAGONFLY"
PATTERN_DOJI_GRAVESTONE = "DOJI_GRAVESTONE"
PATTERN_BULLISH_ENGULFING = "BULLISH_ENGULFING"

# Códigos de contexto/significado
CONTEXT_INDECISION = "INDECISION"
CONTEXT_BULLISH_REVERSAL = "BULLISH_REVERSAL"
CONTEXT_POTENTIAL_BULLISH = "POTENTIAL_BULLISH"

# Códigos de confianza
CONFIDENCE_LOW = "LOW"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_HIGH = "HIGH"

# Código de aviso legal
DISCLAIMER_CODE = "DISCLAIMER"


# ============================================================================
# DATOS DE EJEMPLO
# ============================================================================

# Velas de ejemplo para probar los patrones
# Cada vela tiene: open, high, low, close, volume
EJEMPLO_VELAS = [
    # Vela 0: Normal alcista
    {"open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 1000},
    
    # Vela 1: Martillo (cuerpo pequeño arriba, sombra larga abajo)
    {"open": 104.0, "high": 105.0, "low": 98.0, "close": 103.5, "volume": 1200},
    
    # Vela 2: Doji (open y close casi iguales - indica indecisión)
    {"open": 103.5, "high": 104.5, "low": 102.5, "close": 103.6, "volume": 800},
    
    # Vela 3: Normal bajista
    {"open": 103.6, "high": 104.0, "low": 101.0, "close": 101.5, "volume": 1500},
    
    # Vela 4: Vela pequeña bajista (para formar envolvente)
    {"open": 101.5, "high": 102.0, "low": 101.0, "close": 101.8, "volume": 900},
    
    # Vela 5: ENVOLVENTE ALCISTA (esta vela "envuelve" a la anterior)
    # La vela anterior era pequeña y bajista, esta es grande y alcista
    {"open": 101.0, "high": 106.0, "low": 100.5, "close": 105.5, "volume": 2000},
    
    # Vela 6: Normal alcista
    {"open": 105.5, "high": 107.0, "low": 104.5, "close": 106.5, "volume": 1100},
]


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def calcular_tamaño_cuerpo(vela: Dict) -> float:
    """
    Calcula el tamaño del cuerpo de una vela.
    
    El "cuerpo" es la diferencia entre el precio de apertura (open)
    y el precio de cierre (close). Representa dónde abrió y cerró la vela.
    """
    return abs(vela["close"] - vela["open"])


def calcular_sombra_superior(vela: Dict) -> float:
    """
    Calcula el tamaño de la sombra superior de una vela.
    
    La "sombra superior" es la línea que va desde el cuerpo hasta
    el precio más alto (high). Muestra cuánto subió el precio pero volvió.
    """
    cuerpo_superior = max(vela["open"], vela["close"])
    return vela["high"] - cuerpo_superior


def calcular_sombra_inferior(vela: Dict) -> float:
    """
    Calcula el tamaño de la sombra inferior de una vela.
    
    La "sombra inferior" es la línea que va desde el cuerpo hasta
    el precio más bajo (low). Muestra cuánto bajó el precio pero volvió.
    """
    cuerpo_inferior = min(vela["open"], vela["close"])
    return cuerpo_inferior - vela["low"]


def es_vela_alcista(vela: Dict) -> bool:
    """
    Determina si una vela es alcista (verde) o bajista (roja).
    
    Una vela es alcista cuando el precio de cierre (close) es mayor
    que el precio de apertura (open). Esto significa que el precio subió.
    """
    return vela["close"] > vela["open"]


def es_vela_bajista(vela: Dict) -> bool:
    """
    Determina si una vela es bajista (roja).
    
    Una vela es bajista cuando el precio de cierre (close) es menor
    que el precio de apertura (open). Esto significa que el precio bajó.
    """
    return vela["close"] < vela["open"]


# ============================================================================
# DETECCIÓN DE PATRONES
# ============================================================================

def detectar_martillo(vela: Dict, umbral: float = 2.0) -> Optional[Dict]:
    """
    Detecta el patrón MARTILLO.
    
    ¿Qué es un Martillo?
    ====================
    Un Martillo es una vela con:
    - Cuerpo pequeño (arriba)
    - Sombra inferior MUY larga (al menos 2 veces el cuerpo)
    - Sombra superior pequeña o inexistente
    
    ¿Qué significa?
    ===============
    El Martillo sugiere que hubo mucha presión de VENTA durante el día,
    pero al final los COMPRADORES lograron subir el precio. Es una señal
    potencial de que el precio podría empezar a subir después de una caída.
    
    IMPORTANTE: Es solo una señal. No garantiza nada. Se debe confirmar
    con otras herramientas de análisis.
    
    Args:
        vela: Diccionario con datos OHLCV
        umbral: Qué tan larga debe ser la sombra (múltiplo del cuerpo)
    
    Returns:
        Diccionario con información del patrón o None si no se detecta
    """
    # Calcular tamaños
    cuerpo = calcular_tamaño_cuerpo(vela)
    sombra_inferior = calcular_sombra_inferior(vela)
    sombra_superior = calcular_sombra_superior(vela)
    
    # Evitar división por cero
    if cuerpo == 0:
        cuerpo = 0.001
    
    # Condiciones para ser un Martillo:
    # 1. Sombra inferior debe ser al menos 2 veces el cuerpo
    # 2. Sombra superior debe ser pequeña (menor a la mitad del cuerpo)
    # 3. El cuerpo debe estar en la parte superior (no importa si es alcista o bajista)
    
    if (sombra_inferior >= cuerpo * umbral and
        sombra_superior <= cuerpo * 0.5 and
        sombra_inferior > 0):
        
        return {
            "pattern_code": PATTERN_HAMMER,
            "context_code": CONTEXT_POTENTIAL_BULLISH,
            "confidence": CONFIDENCE_MEDIUM,
            "datos_tecnicos": {
                "cuerpo": round(cuerpo, 2),
                "sombra_inferior": round(sombra_inferior, 2),
                "sombra_superior": round(sombra_superior, 2),
                "proporcion_sombra_cuerpo": round(sombra_inferior / cuerpo, 2),
            }
        }
    
    return None


def detectar_envolvente_alcista(vela_anterior: Dict, vela_actual: Dict) -> Optional[Dict]:
    """
    Detecta el patrón ENVOLVENTE ALCISTA (Bullish Engulfing).
    
    ¿Qué es un Envolvente Alcista?
    ===============================
    Es un patrón de DOS velas donde:
    1. La primera vela es BAJISTA (roja) y pequeña
    2. La segunda vela es ALCISTA (verde) y GRANDE
    3. La segunda vela "envuelve" completamente a la primera
       (su cuerpo abarca desde más abajo hasta más arriba que la anterior)
    
    ¿Qué significa?
    ===============
    Sugiere un cambio fuerte de sentimiento del mercado. La presión de venta
    (primera vela roja) fue superada por una presión de compra mucho mayor
    (segunda vela verde grande). Es una señal potencial de reversión alcista.
    
    IMPORTANTE: Funciona mejor después de una caída. Siempre confirma con
    otras herramientas antes de tomar decisiones.
    
    Args:
        vela_anterior: La primera vela (debe ser bajista y pequeña)
        vela_actual: La segunda vela (debe ser alcista y envolver a la anterior)
    
    Returns:
        Diccionario con información del patrón o None si no se detecta
    """
    # Verificar condiciones básicas
    if not (es_vela_bajista(vela_anterior) and es_vela_alcista(vela_actual)):
        return None
    
    # Calcular cuerpos
    cuerpo_anterior = calcular_tamaño_cuerpo(vela_anterior)
    cuerpo_actual = calcular_tamaño_cuerpo(vela_actual)
    
    # Evitar división por cero
    if cuerpo_anterior == 0:
        cuerpo_anterior = 0.001
    
    # Condiciones para ser Envolvente Alcista:
    # 1. La vela actual debe tener un cuerpo mayor (al menos 1.5 veces)
    # 2. El open de la vela actual debe estar por debajo del close de la anterior
    # 3. El close de la vela actual debe estar por encima del open de la anterior
    
    cuerpo_suficientemente_grande = cuerpo_actual >= cuerpo_anterior * 1.5
    open_por_debajo = vela_actual["open"] < vela_anterior["close"]
    close_por_encima = vela_actual["close"] > vela_anterior["open"]
    
    if (cuerpo_suficientemente_grande and open_por_debajo and close_por_encima):
        return {
            "pattern_code": PATTERN_BULLISH_ENGULFING,
            "context_code": CONTEXT_BULLISH_REVERSAL,
            "confidence": CONFIDENCE_MEDIUM,
            "datos_tecnicos": {
                "vela_anterior": {
                    "open": vela_anterior["open"],
                    "close": vela_anterior["close"],
                    "is_bearish": True,
                    "cuerpo": round(cuerpo_anterior, 2),
                },
                "vela_actual": {
                    "open": vela_actual["open"],
                    "close": vela_actual["close"],
                    "is_bullish": True,
                    "cuerpo": round(cuerpo_actual, 2),
                },
                "proporcion_cuerpos": round(cuerpo_actual / cuerpo_anterior, 2),
            }
        }
    
    return None


def detectar_doji(vela: Dict, tolerancia: float = 0.1) -> Optional[Dict]:
    """
    Detecta el patrón DOJI.
    
    ¿Qué es un Doji?
    ================
    Un Doji es una vela donde el precio de apertura (open) y cierre (close)
    están prácticamente iguales. El cuerpo es casi invisible o muy pequeño.
    
    ¿Qué significa?
    ===============
    Indica INDECISIÓN en el mercado. Los compradores y vendedores están
    en equilibrio. Ninguno ganó claramente durante ese período.
    
    Según dónde aparezca, puede significar:
    - Después de una subida: Los compradores están perdiendo fuerza (posible caída)
    - Después de una caída: Los vendedores están perdiendo fuerza (posible subida)
    - En medio de una tendencia: La tendencia podría estar perdiendo impulso
    
    IMPORTANTE: Un Doji por sí solo no dice mucho. Necesitas ver el contexto
    (qué pasó antes y después) para darle significado.
    
    Args:
        vela: Diccionario con datos OHLCV
        tolerancia: Qué tan cerca deben estar open y close (como porcentaje del rango)
    
    Returns:
        Diccionario con información del patrón o None si no se detecta
    """
    # Calcular el cuerpo y el rango total
    cuerpo = calcular_tamaño_cuerpo(vela)
    rango_total = vela["high"] - vela["low"]
    
    # Evitar división por cero
    if rango_total == 0:
        return None
    
    # Un Doji es cuando el cuerpo es muy pequeño comparado con el rango total
    # Generalmente menos del 10% del rango total
    proporcion_cuerpo_rango = cuerpo / rango_total
    
    if proporcion_cuerpo_rango <= tolerancia and rango_total > 0:
        # Determinar el tipo de Doji según las sombras
        sombra_superior = calcular_sombra_superior(vela)
        sombra_inferior = calcular_sombra_inferior(vela)
        
        # Tipo de Doji según las sombras
        if sombra_superior > sombra_inferior * 1.5:
            pattern_code = PATTERN_DOJI_GRAVESTONE
        elif sombra_inferior > sombra_superior * 1.5:
            pattern_code = PATTERN_DOJI_DRAGONFLY
        else:
            pattern_code = PATTERN_DOJI_STANDARD
        
        return {
            "pattern_code": pattern_code,
            "context_code": CONTEXT_INDECISION,
            "confidence": CONFIDENCE_LOW,
            "datos_tecnicos": {
                "open": vela["open"],
                "close": vela["close"],
                "diferencia_open_close": round(abs(vela["close"] - vela["open"]), 2),
                "rango_total": round(rango_total, 2),
                "proporcion_cuerpo_rango": round(proporcion_cuerpo_rango * 100, 2),
                "sombra_superior": round(sombra_superior, 2),
                "sombra_inferior": round(sombra_inferior, 2),
            }
        }
    
    return None


# ============================================================================
# FUNCIÓN PRINCIPAL DE ANÁLISIS
# ============================================================================

def analizar_patrones(velas: List[Dict]) -> Dict:
    """
    Analiza una lista de velas y detecta todos los patrones presentes.
    
    Esta función es la principal que deberías usar. Recibe una lista de velas
    y devuelve todos los patrones encontrados con sus explicaciones educativas.
    
    Args:
        velas: Lista de diccionarios con datos OHLCV
    
    Returns:
        Diccionario con todos los patrones detectados y explicaciones
    """
    if len(velas) < 1:
        return {
            "error": "Se necesitan al menos 1 vela para analizar",
            "patrones_detectados": []
        }
    
    patrones_detectados = []
    
    total_velas = len(velas)
    
    # Analizar cada vela individual
    for i, vela in enumerate(velas):
        # Detectar Martillo
        martillo = detectar_martillo(vela)
        if martillo:
            martillo["posicion"] = i
            # pattern_index: -1 para última vela, -2 para penúltima, etc.
            # Útil para visualización en frontend (indexación desde el final)
            martillo["pattern_index"] = i - total_velas
            patrones_detectados.append(martillo)
        
        # Detectar Doji
        doji = detectar_doji(vela)
        if doji:
            doji["posicion"] = i
            # pattern_index: -1 para última vela, -2 para penúltima, etc.
            doji["pattern_index"] = i - total_velas
            patrones_detectados.append(doji)
        
        # Detectar Envolvente Alcista (necesita vela anterior)
        if i > 0:
            envolvente = detectar_envolvente_alcista(velas[i-1], vela)
            if envolvente:
                envolvente["posicion"] = i
                # pattern_index: -1 para última vela, -2 para penúltima, etc.
                envolvente["pattern_index"] = i - total_velas
                envolvente["vela_anterior_posicion"] = i - 1
                envolvente["vela_anterior_pattern_index"] = (i - 1) - total_velas
                patrones_detectados.append(envolvente)
    
    # Construir respuesta con códigos técnicos (i18n para frontend)
    resultado = {
        "total_velas_analizadas": total_velas,
        "patrones_detectados": len(patrones_detectados),
        "patrones": patrones_detectados,
        "disclaimer_code": DISCLAIMER_CODE
    }
    
    return resultado


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo: Analizar las velas de ejemplo
    print("=" * 70)
    print("ANÁLISIS DE PATRONES DE VELAS JAPONESAS - EJEMPLO EDUCATIVO")
    print("=" * 70)
    print()
    
    resultado = analizar_patrones(EJEMPLO_VELAS)
    
    print(f"Total de velas analizadas: {resultado['total_velas_analizadas']}")
    print(f"Patrones detectados: {resultado['patrones_detectados']}")
    print()
    print("-" * 70)
    
    for patron in resultado["patrones"]:
        print(f"\n📍 Patrón en posición {patron['posicion']}: {patron['patron']}")
        print(f"   Tipo: {patron['tipo']}")
        print(f"\n   📖 Descripción:")
        print(f"   {patron['descripcion']}")
        print(f"\n   💡 Explicación Simple:")
        print(f"   {patron['explicacion_simple']}")
        print(f"\n   📊 Datos Técnicos: {patron['datos_tecnicos']}")
        print(f"\n   ⚠️ Recordatorio:")
        print(f"   {patron['recordatorio_educativo']}")
        print("-" * 70)
    
    print(f"\n{resultado['mensaje_importante']}")
    print()
