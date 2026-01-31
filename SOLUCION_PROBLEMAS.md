# 🔧 Solución de Problemas - Trading Educativo

Guía para resolver problemas comunes al ejecutar la aplicación.

---

## ❌ Error: "no se encontró Python"

### **Problema:**
```
no se encontró Python; ejecutar sin argumentos para instalar...
```

### **Solución:**

#### **Opción 1: Instalar Python desde python.org**
1. Ve a: https://www.python.org/downloads/
2. Descarga Python 3.9 o superior
3. **IMPORTANTE:** Durante la instalación, marca la casilla "Add Python to PATH"
4. Instala
5. Reinicia tu terminal
6. Verifica: `python --version`

#### **Opción 2: Usar el Python Launcher (Windows)**
En Windows, puedes intentar:
```powershell
py main.py
```
O:
```powershell
py -3 main.py
```

#### **Opción 3: Verificar Python instalado pero no en PATH**
1. Busca dónde está instalado Python (ej: `C:\Users\TuUsuario\AppData\Local\Programs\Python\`)
2. Agrega Python al PATH del sistema:
   - Presiona `Win + R`
   - Escribe `sysdm.cpl` y presiona Enter
   - Pestaña "Avanzado" → "Variables de entorno"
   - Edita "Path" → Agrega la carpeta de Python

---

## ❌ Error: "ModuleNotFoundError: No module named 'fastapi'"

### **Problema:**
Faltan las dependencias instaladas.

### **Solución:**
```bash
pip install -r requirements.txt
```

Si `pip` no funciona, prueba:
```bash
python -m pip install -r requirements.txt
```

O en Windows con py:
```bash
py -m pip install -r requirements.txt
```

---

## ❌ Error: "ImportError" o "ModuleNotFoundError"

### **Problema:**
Python no encuentra los módulos del proyecto.

### **Solución:**
1. Asegúrate de estar en la carpeta correcta:
   ```bash
   cd C:\Users\inter\trading-educativo
   ```

2. Verifica que la estructura de carpetas sea correcta:
   ```
   trading-educativo/
   ├── app/
   │   ├── __init__.py
   │   ├── api/
   │   ├── core/
   │   ├── schemas/
   │   └── services/
   ├── main.py
   └── requirements.txt
   ```

---

## ❌ Error: "Port 8000 already in use"

### **Problema:**
Otro programa está usando el puerto 8000.

### **Solución:**

**Opción 1: Cambiar el puerto**
Edita `app/core/config.py` y cambia:
```python
PORT: int = 8001  # O cualquier otro puerto libre
```

**Opción 2: Cerrar el programa que usa el puerto**
```powershell
# Encontrar qué está usando el puerto 8000
netstat -ano | findstr :8000

# Matar el proceso (reemplaza PID con el número que aparezca)
taskkill /PID <PID> /F
```

---

## ❌ Error: "SyntaxError" o errores de sintaxis

### **Problema:**
Hay un error de sintaxis en el código.

### **Solución:**
1. Ejecuta el linter:
   ```bash
   python -m py_compile main.py
   python -m py_compile app/api/analysis.py
   python -m py_compile app/schemas/patterns.py
   ```

2. Revisa los errores que muestre y corrígelos.

---

## ❌ El servidor inicia pero no responde

### **Problema:**
El servidor se inicia pero no puedes acceder a él.

### **Solución:**

1. **Verifica que esté escuchando:**
   ```powershell
   # Deberías ver algo como esto en la terminal:
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Prueba desde el navegador:**
   ```
   http://localhost:8000/
   http://localhost:8000/docs
   ```

3. **Si usas un firewall**, permite el acceso al puerto 8000.

---

## ✅ Verificación Paso a Paso

Sigue estos pasos para diagnosticar:

### **Paso 1: Verificar Python**
```bash
python --version
```
**Debería mostrar:** `Python 3.9.x` o superior

### **Paso 2: Verificar pip**
```bash
pip --version
```

### **Paso 3: Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **Paso 4: Verificar estructura**
```bash
# Deberías ver estas carpetas:
dir app
dir app\api
dir app\core
dir app\services
dir app\schemas
```

### **Paso 5: Ejecutar el servidor**
```bash
python main.py
```

**Deberías ver:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### **Paso 6: Probar el endpoint**
Abre en el navegador:
```
http://localhost:8000/api/analysis/patrones/ejemplo
```

---

## 🆘 Si nada funciona

### **Reinstalar desde cero:**

1. **Elimina el entorno virtual (si usas uno):**
   ```bash
   rmdir /s venv
   ```

2. **Crea un nuevo entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instala dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta:**
   ```bash
   python main.py
   ```

---

## 📞 Información para pedir ayuda

Si necesitas ayuda, proporciona:

1. **Versión de Python:**
   ```bash
   python --version
   ```

2. **Sistema operativo:**
   ```powershell
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
   ```

3. **Error completo:**
   - Copia y pega TODO el mensaje de error

4. **Comando que ejecutaste:**
   - Ejemplo: `python main.py`

---

## 🔍 Verificar que todo esté bien

Ejecuta este script de verificación:

```python
# verificar_instalacion.py
import sys

print("Python version:", sys.version)
print("\nVerificando módulos...")

try:
    import fastapi
    print("✅ FastAPI instalado")
except ImportError:
    print("❌ FastAPI NO instalado")

try:
    import uvicorn
    print("✅ Uvicorn instalado")
except ImportError:
    print("❌ Uvicorn NO instalado")

try:
    from app.core.config import settings
    print("✅ Configuración cargada correctamente")
except ImportError as e:
    print(f"❌ Error cargando configuración: {e}")

try:
    from app.services.candlestick_patterns import analizar_patrones
    print("✅ Servicio de patrones cargado correctamente")
except ImportError as e:
    print(f"❌ Error cargando servicio: {e}")

print("\n✅ Verificación completa!")
```

Guarda esto como `verificar_instalacion.py` y ejecuta:
```bash
python verificar_instalacion.py
```

---

¿Seguís con problemas? Describe exactamente qué error ves y cómo lo reproduciste.
