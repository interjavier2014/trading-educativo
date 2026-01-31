# Trading Educativo - Aplicación de Análisis Técnico

## ¿Qué es este proyecto?

Esta es una aplicación web que ayuda a **principiantes** a aprender análisis técnico de criptomonedas y acciones. 

**IMPORTANTE**: Esta aplicación es solo educativa. NO proporciona recomendaciones de inversión. Solo muestra información y señales para aprender.

## ¿Cómo funciona?

La aplicación:
1. Obtiene datos de precios (velas OHLCV) de mercados financieros
2. Detecta patrones básicos de velas japonesas (como Doji, Martillo, etc.)
3. Analiza la tendencia del precio
4. Muestra una señal educativa explicando qué significa cada cosa

## Estructura del Proyecto

Te explico qué hace cada carpeta y archivo:

### Archivos principales (raíz del proyecto)

- **`main.py`**: Es el archivo principal que inicia la aplicación. Es como el "motor" que pone todo en marcha.

- **`requirements.txt`**: Lista todas las "herramientas" (librerías) que necesita el proyecto para funcionar. Es como una lista de compras para el programa.

- **`.env.example`**: Un ejemplo de archivo de configuración. Aquí irían las claves secretas y configuraciones. Nunca subas el archivo `.env` real a internet (por seguridad).

- **`.gitignore`**: Le dice a Git qué archivos NO debe guardar (como archivos temporales o secretos).

### Carpeta `app/` (el código principal)

- **`app/api/`**: Aquí están las "rutas" o "endpoints" de la API. Son como las puertas de entrada que los usuarios usarán para pedir información.

- **`app/core/`**: Configuración central de la aplicación. Cosas que se usan en todo el proyecto.

- **`app/models/`**: Define cómo se guardan los datos en la base de datos (para el futuro).

- **`app/schemas/`**: Define cómo deben llegar los datos cuando alguien hace una petición. Es como un "molde" que valida la información.

- **`app/services/`**: Aquí está la "lógica de negocio". El código que hace el análisis técnico, detecta patrones, etc. Es el "cerebro" de la aplicación.

- **`app/utils/`**: Funciones auxiliares que se usan en varios lugares. Código reutilizable.

## ¿Cómo empezar?

1. Instalar Python 3.9 o superior
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno: `venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Copiar `.env.example` a `.env` y configurar tus claves API
6. Ejecutar: `python main.py`

## Próximos pasos

- [ ] Implementar obtención de datos de precios
- [ ] Implementar detección de patrones de velas japonesas
- [ ] Implementar análisis de tendencia
- [ ] Crear endpoints educativos
- [ ] Agregar autenticación (para monetizar después)
- [ ] Agregar base de datos (para guardar historial)
