# 📁 Explicación de la Estructura del Proyecto

Este documento explica **en lenguaje simple** qué hace cada archivo y carpeta del proyecto.

## 🗂️ Vista General de la Estructura

```
trading-educativo/
│
├── 📄 main.py                    # ⚡ El motor que inicia todo
├── 📄 requirements.txt            # 📦 Lista de herramientas necesarias
├── 📄 README.md                   # 📖 Instrucciones del proyecto
├── 📄 .gitignore                  # 🚫 Archivos que Git ignora
│
├── 📁 app/                        # 💻 Todo el código principal
│   │
│   ├── 📁 api/                    # 🚪 Puertas de entrada (endpoints)
│   │   ├── __init__.py
│   │   └── analysis.py           # Endpoints de análisis
│   │
│   ├── 📁 core/                   # ⚙️ Configuración central
│   │   ├── __init__.py
│   │   └── config.py             # Todos los ajustes aquí
│   │
│   ├── 📁 models/                 # 🗄️ Modelos de base de datos (futuro)
│   │   └── __init__.py
│   │
│   ├── 📁 schemas/                # ✅ Validación de datos
│   │   └── __init__.py
│   │
│   ├── 📁 services/               # 🧠 La lógica inteligente
│   │   ├── __init__.py
│   │   ├── price_service.py      # Obtiene precios
│   │   ├── pattern_service.py    # Detecta patrones de velas
│   │   └── trend_service.py      # Analiza tendencias
│   │
│   ├── 📁 utils/                  # 🔧 Herramientas auxiliares
│   │   ├── __init__.py
│   │   └── helpers.py            # Funciones útiles
│   │
│   └── __init__.py
│
└── 📁 tests/                      # 🧪 Pruebas del código
    ├── __init__.py
    └── test_example.py
```

---

## 📄 Archivos Principales (Raíz del Proyecto)

### `main.py`
**¿Qué hace?**  
Es el archivo que **inicia** toda la aplicación. Es como prender el motor de un auto.

**¿Qué contiene?**
- Configuración de FastAPI
- Rutas básicas (como la página de bienvenida)
- El comando para iniciar el servidor web

**¿Cuándo lo usas?**  
Cuando quieres ejecutar la aplicación. Ejecutas: `python main.py`

---

### `requirements.txt`
**¿Qué hace?**  
Es una **lista de herramientas** (librerías) que el proyecto necesita para funcionar.

**Ejemplo:**  
Si la aplicación necesita FastAPI, aquí está escrito `fastapi==0.104.1`

**¿Cuándo lo usas?**  
Cuando instalas el proyecto por primera vez:
```bash
pip install -r requirements.txt
```
Esto instala todas las herramientas necesarias.

---

### `README.md`
**¿Qué hace?**  
Es un documento que explica qué es el proyecto y cómo usarlo. Como un "manual de instrucciones".

**¿Para quién es?**  
Para ti y para cualquier persona que quiera entender o usar el proyecto.

---

### `.gitignore`
**¿Qué hace?**  
Le dice a Git (sistema de control de versiones) qué archivos **NO debe guardar**.

**Ejemplo:**  
- Archivos temporales (como `__pycache__/`)
- Secretos (como archivos `.env` con claves API)
- Archivos del sistema operativo

**¿Por qué es importante?**  
Para no subir accidentalmente información sensible a internet.

---

## 📁 Carpeta `app/` (Código Principal)

Esta carpeta contiene **todo el código funcional** de la aplicación.

### `app/api/` - Las Puertas de Entrada
**¿Qué hace?**  
Aquí están las **rutas** o **endpoints** de la API. Son como las puertas que los usuarios usan para pedir información.

**Ejemplo:**  
Cuando alguien visita `http://tu-servidor.com/api/analysis/crypto/btc-usdt`, ese pedido llega aquí.

**Archivos:**
- `analysis.py`: Rutas relacionadas con análisis técnico

**Analogía:**  
Es como la recepción de un hotel. Los clientes llegan aquí y se les dirige al lugar correcto.

---

### `app/core/` - Configuración Central
**¿Qué hace?**  
Aquí está toda la **configuración** que se usa en toda la aplicación.

**Archivos:**
- `config.py`: Lee variables de entorno (como claves API), configuración del servidor, etc.

**¿Por qué está separado?**  
Para tener todos los ajustes en un solo lugar. Si necesitas cambiar el puerto del servidor, solo editas este archivo.

**Analogía:**  
Es como el panel de control de una casa. Tienes todos los interruptores y ajustes aquí.

---

### `app/models/` - Modelos de Base de Datos (Futuro)
**¿Qué hace?**  
Aquí se definen cómo se guardan los datos en la base de datos.

**Por ahora:**  
Está vacío porque todavía no implementamos base de datos.

**Futuro:**  
Cuando implementes base de datos, aquí dirás cosas como "un usuario tiene: email, nombre, fecha de registro".

**Analogía:**  
Es como los planos de una casa. Defines cómo deben ser las habitaciones (tablas de base de datos).

---

### `app/schemas/` - Validación de Datos
**¿Qué hace?**  
Define **cómo deben llegar los datos** cuando alguien hace una petición a la API.

**Ejemplo:**  
Si alguien pide analizar "BTCUSDT", aquí defines:
- El símbolo debe tener formato correcto
- El intervalo debe ser "1h", "1d", etc.
- Debe incluir todos los campos necesarios

**¿Por qué es importante?**  
Para evitar errores. Si alguien envía datos incorrectos, se rechazan antes de procesarlos.

**Analogía:**  
Es como un filtro de seguridad. Solo deja pasar información válida.

---

### `app/services/` - La Lógica Inteligente
**¿Qué hace?**  
Aquí está el **"cerebro"** de la aplicación. Toda la lógica de negocio va aquí.

**Archivos:**
- `price_service.py`: Obtiene precios de criptomonedas y acciones desde APIs externas
- `pattern_service.py`: Detecta patrones de velas japonesas (Doji, Martillo, etc.)
- `trend_service.py`: Analiza si la tendencia es alcista, bajista o lateral

**¿Por qué está separado?**  
Para mantener el código organizado. Cada servicio tiene una responsabilidad específica.

**Analogía:**  
Es como los departamentos de una empresa. Cada uno tiene su función:
- Price Service: El que compra materiales (obtiene datos)
- Pattern Service: El que analiza productos (detecta patrones)
- Trend Service: El que estudia el mercado (analiza tendencias)

---

### `app/utils/` - Herramientas Auxiliares
**¿Qué hace?**  
Funciones pequeñas y útiles que se usan en varios lugares.

**Ejemplo:**  
- Formatear precios: convertir `1234.5678` a `"1,234.57"`
- Validar símbolos: verificar que "BTCUSDT" es válido
- Calcular porcentajes: calcular cambios de precio

**¿Por qué está separado?**  
Para evitar repetir código. Escribes la función una vez y la usas donde la necesites.

**Analogía:**  
Es como una caja de herramientas. Tienes herramientas que usas frecuentemente y las guardas ahí.

---

## 📁 Carpeta `tests/` - Pruebas
**¿Qué hace?**  
Aquí escribes **pruebas** que verifican que tu código funciona correctamente.

**Por ahora:**  
Solo hay un ejemplo básico.

**Futuro:**  
Puedes escribir pruebas como:
- "Verificar que detecta correctamente un patrón Doji"
- "Verificar que calcula bien la tendencia"

**¿Por qué es importante?**  
Para asegurarte de que cuando cambies código, no rompas cosas que ya funcionaban.

**Analogía:**  
Es como hacer pruebas de calidad. Antes de vender un producto, lo pruebas para asegurarte de que funciona.

---

## 🔄 Cómo Funciona Todo Junto

1. **Usuario hace una petición** → `app/api/analysis.py` recibe el pedido
2. **Validación** → `app/schemas/` verifica que los datos sean correctos
3. **Obtener precios** → `app/services/price_service.py` busca los datos
4. **Detectar patrones** → `app/services/pattern_service.py` analiza las velas
5. **Analizar tendencia** → `app/services/trend_service.py` determina la tendencia
6. **Respuesta** → Todo se combina y se devuelve una señal educativa al usuario

---

## 🎯 ¿Dónde Agregar Código Nuevo?

- **Nuevo endpoint?** → `app/api/`
- **Nueva lógica de análisis?** → `app/services/`
- **Nueva configuración?** → `app/core/config.py`
- **Nueva validación?** → `app/schemas/`
- **Nueva función auxiliar?** → `app/utils/`

---

## ✅ Ventajas de Esta Estructura

1. **Organizada**: Cada cosa tiene su lugar
2. **Escalable**: Fácil agregar nuevas funcionalidades
3. **Mantenible**: Si algo se rompe, sabes dónde buscar
4. **Profesional**: Sigue las mejores prácticas de la industria
5. **Lista para monetizar**: Fácil agregar autenticación, base de datos, etc.

---

¿Tienes dudas sobre algún archivo? ¡Pregúntame!
