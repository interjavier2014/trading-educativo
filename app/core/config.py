"""
Configuración central de la aplicación

Este archivo carga todas las configuraciones desde variables de entorno.
Es como un "panel de control" donde están todos los ajustes.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuraciones de la aplicación.
    Los valores se toman del archivo .env o del sistema.
    """
    
    # Información de la aplicación
    APP_NAME: str = "Trading Educativo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API Keys para obtener datos de precios
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    # Base de datos (para el futuro)
    DATABASE_URL: str = "sqlite:///./trading.db"
    
    # Seguridad
    SECRET_KEY: str = "change-this-in-production"
    
    class Config:
        # Le dice a Pydantic que busque las variables en un archivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Crear una instancia global de configuración
# Esto permite usar settings en cualquier parte de la aplicación
settings = Settings()
