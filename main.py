"""
Trading Educativo - Punto de entrada principal de la aplicación

Este archivo inicia el servidor web FastAPI.
Es como el "motor" que pone en marcha toda la aplicación.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Crear la aplicación FastAPI
# title: el nombre que aparece en la documentación
# description: una descripción de qué hace la app
app = FastAPI(
    title=settings.APP_NAME,
    description="Aplicación educativa de análisis técnico para criptomonedas y acciones",
    version=settings.APP_VERSION,
)

# Configurar CORS (permite que un frontend en otro servidor se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ruta raíz - cuando alguien visita la URL principal
@app.get("/")
async def root():
    """
    Endpoint de bienvenida.
    Visita http://localhost:8000/ para ver este mensaje.
    """
    return {
        "message": "¡Bienvenido a Trading Educativo!",
        "description": "Aplicación educativa de análisis técnico",
        "docs": "Visita /docs para ver la documentación completa",
        "version": settings.APP_VERSION
    }


# Ruta de salud - para verificar que el servidor funciona
@app.get("/health")
async def health_check():
    """
    Endpoint de salud. Útil para verificar que el servidor está funcionando.
    """
    return {"status": "healthy", "service": settings.APP_NAME}


# Importar las rutas de la API
from app.api import analysis, assets

# Incluir los routers en la aplicación
app.include_router(analysis.router)
app.include_router(assets.router)


# Eventos de inicio de la aplicación
@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    
    Aquí se hace el warm-up del cache: se precargan activos populares
    para que el cache esté listo antes de las primeras peticiones.
    """
    print("✅ Servidor iniciado correctamente")
    
    # Warm-up desactivado temporalmente para debugging
    # Para reactivarlo, descomentar las siguientes líneas:
    # from app.services.cache_warmup import warmup_cache_background
    # warmup_cache_background()
    # if settings.DEBUG:
    #     print("🔥 Cache warm-up iniciado en segundo plano...")


if __name__ == "__main__":
    import uvicorn
    
    # Iniciar el servidor
    # host="0.0.0.0" permite conexiones desde cualquier IP
    # port=8000 es el puerto donde escuchará
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # Recarga automática en desarrollo
    )
