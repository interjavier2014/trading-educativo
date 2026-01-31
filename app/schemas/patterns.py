"""
Esquemas de validación para patrones de velas

Estos esquemas definen cómo deben ser los datos que recibe el endpoint.
Son como "moldes" que validan que la información sea correcta antes de procesarla.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional


class VelaSchema(BaseModel):
    """
    Esquema para una vela OHLCV.
    
    Cada vela debe tener:
    - open: Precio de apertura
    - high: Precio más alto del período
    - low: Precio más bajo del período
    - close: Precio de cierre
    - volume: Volumen de transacciones
    """
    open: float = Field(..., description="Precio de apertura de la vela", gt=0)
    high: float = Field(..., description="Precio más alto del período", gt=0)
    low: float = Field(..., description="Precio más bajo del período", gt=0)
    close: float = Field(..., description="Precio de cierre de la vela", gt=0)
    volume: Optional[float] = Field(None, description="Volumen de transacciones", ge=0)
    
    @model_validator(mode='after')
    def validar_precios(self):
        """
        Valida que high sea el más alto y low el más bajo.
        Se ejecuta después de que todos los campos se validen.
        """
        if self.high < self.low:
            raise ValueError('high debe ser mayor o igual que low')
        if self.high < self.open:
            raise ValueError('high debe ser mayor o igual que open')
        if self.high < self.close:
            raise ValueError('high debe ser mayor o igual que close')
        if self.low > self.open:
            raise ValueError('low debe ser menor o igual que open')
        if self.low > self.close:
            raise ValueError('low debe ser menor o igual que close')
        return self


class AnalisisPatronesRequest(BaseModel):
    """
    Esquema para la petición de análisis de patrones.
    
    El usuario envía una lista de velas y el endpoint las analiza.
    """
    velas: List[VelaSchema] = Field(
        ...,
        description="Lista de velas OHLCV para analizar",
        min_length=1,
        max_length=100  # Limitar a 100 velas máximo
    )
    
    @field_validator('velas')
    def validar_cantidad_velas(cls, v):
        """Valida que haya al menos una vela"""
        if len(v) < 1:
            raise ValueError('Se necesita al menos 1 vela para analizar')
        if len(v) > 100:
            raise ValueError('El máximo de velas permitido es 100')
        return v


class PatronDetectadoResponse(BaseModel):
    """Esquema para un patrón detectado en la respuesta (con códigos técnicos para i18n)"""
    pattern_code: str  # Código del patrón (ej: HAMMER, DOJI_STANDARD, BULLISH_ENGULFING)
    context_code: str  # Código del contexto/significado (ej: INDECISION, BULLISH_REVERSAL)
    confidence: str  # Nivel de confianza (LOW, MEDIUM, HIGH)
    datos_tecnicos: dict
    posicion: int  # Índice 0-based en la lista de velas (0 = primera vela)
    pattern_index: int  # Índice para visualización: -1 = última vela, -2 = penúltima, etc.


class AnalisisPatronesResponse(BaseModel):
    """
    Esquema para la respuesta del análisis de patrones.
    
    Esta es la estructura que devuelve el endpoint cuando analiza las velas.
    Usa códigos técnicos (i18n) para que el frontend pueda traducir.
    """
    total_velas_analizadas: int
    patrones_detectados: int
    patrones: List[PatronDetectadoResponse]
    disclaimer_code: str  # Código del aviso legal (DISCLAIMER)


class AnalisisUnificadoResponse(BaseModel):
    """
    Esquema para la respuesta del análisis unificado (múltiples mercados).
    
    Respuesta educativa con información del activo, mercado, timeframe
    y patrones detectados usando códigos técnicos.
    
    Incluye campos opcionales para casos de fallback cuando Yahoo Finance
    está temporalmente no disponible.
    """
    asset: str  # Símbolo del activo (ej: BTCUSDT, AAPL, AAPL.BA)
    market: str  # Mercado (crypto, stocks, cedears)
    timeframe: str  # Período de tiempo (1h, 4h, 1d)
    precio_actual: float  # Precio actual o precio_referencia si es fallback
    total_velas_analizadas: int  # 0 si es fallback
    patrones_detectados: int  # 0 si es fallback
    patrones: List[PatronDetectadoResponse]  # Lista vacía si es fallback
    disclaimer_code: str
    # Campos opcionales para fallback
    status_code: Optional[str] = None  # "DATA_TEMPORARILY_UNAVAILABLE" si es fallback
    message_code: Optional[str] = None  # "DATA_SOURCE_RATE_LIMIT" si es fallback
    confidence: Optional[str] = None  # "LOW" si es fallback


class AssetInfo(BaseModel):
    """Información de un activo individual"""
    symbol: str = Field(..., description="Símbolo del activo (ej: BTCUSDT, AAPL, AAPL.BA)")
    name: str = Field(..., description="Nombre descriptivo del activo")


class AssetsListResponse(BaseModel):
    """Respuesta con la lista de activos soportados por mercado"""
    crypto: List[AssetInfo] = Field(..., description="Lista de criptomonedas soportadas")
    stocks: List[AssetInfo] = Field(..., description="Lista de acciones soportadas")
    cedears: List[AssetInfo] = Field(..., description="Lista de CEDEARs soportados")
