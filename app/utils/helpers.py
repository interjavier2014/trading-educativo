"""
Funciones auxiliares reutilizables

Aquí pondremos funciones que se usan en varios lugares del código.
Cosas útiles que no pertenecen a un servicio específico.
"""

from typing import List, Dict, Optional


def format_price(price: float, decimals: int = 2) -> str:
    """
    Formatea un precio para mostrarlo de forma legible
    
    Ejemplo: format_price(1234.5678, 2) -> "1,234.57"
    """
    return f"{price:,.{decimals}f}"


def validate_symbol(symbol: str, asset_type: str = "crypto") -> bool:
    """
    Valida que un símbolo tenga el formato correcto
    
    Args:
        symbol: Símbolo a validar (ej: "BTCUSDT", "AAPL")
        asset_type: Tipo de activo ("crypto" o "stock")
    """
    if not symbol or len(symbol) < 2:
        return False
    
    if asset_type == "crypto":
        # Para crypto: debe tener formato como "BTCUSDT"
        return symbol.isalnum() and len(symbol) >= 6
    elif asset_type == "stock":
        # Para acciones: debe tener formato como "AAPL"
        return symbol.isalpha() and len(symbol) <= 5
    
    return False


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calcula el cambio porcentual entre dos valores
    
    Ejemplo: calculate_percentage_change(100, 110) -> 10.0
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100
