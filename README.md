# 📸 Checador Facial AI

Sistema de asistencia de empleados con reconocimiento facial usando inteligencia artificial. API REST desarrollada con FastAPI y face_recognition (dlib).

## 🚀 Características

- **Reconocimiento facial en tiempo real** usando modelos de deep learning
- **Registro de entrada/salida automático** con detección inteligente
- **API REST completa** con documentación interactiva (Swagger)
- **Base de datos SQLite** con SQLAlchemy ORM
- **CORS habilitado** para integración con frontend móvil/web
- **Vectores biométricos** almacenados de forma segura

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **face_recognition** - Reconocimiento facial con dlib
- **OpenCV** - Procesamiento de imágenes
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI de alto rendimiento

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Visual Studio C++ Build Tools (para compilar dlib en Windows)

### Instalación de dlib en Windows

dlib requiere compilación en Windows. Sigue estos pasos:

1. Descarga e instala [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. Durante la instalación, selecciona "Desktop development with C++"
3. O instala dlib precompilado:
   ```bash
   pip install cmake
   pip install dlib
   ```

## ⚙️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Ozelot12100/checador-facial-ai.git
   cd checador-facial-ai
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**
   
   Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Uso

### Iniciar el servidor

**Opción 1 - Usando uvicorn directamente:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Opción 2 - Ejecutando main.py:**
```bash
python main.py
```

El servidor estará disponible en:
- API: `http://localhost:8000`
- Documentación interactiva: `http://localhost:8000/docs`
- Documentación alternativa: `http://localhost:8000/redoc`

### Desde la red local

Para acceder desde otros dispositivos en la misma red (ej. celular):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Luego accede desde: `http://<IP_DE_TU_PC>:8000`

## 📡 Endpoints Principales

### Empleados

- `POST /api/employees/` - Registrar nuevo empleado con foto
- `GET /api/employees/` - Obtener lista de empleados
- `GET /api/employees/{id}` - Obtener empleado por ID
- `DELETE /api/employees/{id}` - Eliminar empleado

### Asistencia

- `POST /api/attendance/check-in` - Registrar entrada/salida con foto
- `GET /api/attendance/today` - Obtener registros del día
- `GET /api/attendance/history/{employee_id}` - Historial de empleado

## 📦 Estructura del Proyecto

```
checador_api/
├── main.py                 # Punto de entrada de la aplicación
├── database.py             # Configuración de base de datos
├── models.py               # Modelos SQLAlchemy
├── schemas.py              # Esquemas Pydantic
├── requirements.txt        # Dependencias del proyecto
├── test_con_fotos.py       # Script de pruebas con fotos
├── checador_python.db      # Base de datos SQLite (generada automáticamente)
├── routers/
│   ├── employees.py        # Rutas de empleados
│   └── attendance.py       # Rutas de asistencia
├── services/
│   └── biometric.py        # Servicio de reconocimiento facial
├── uploads/                # Fotos de empleados (generado automáticamente)
└── venv/                   # Entorno virtual (no incluido en git)
```

## 🧪 Pruebas

Ejecutar pruebas con fotos:
```bash
python test_con_fotos.py
```

## 🔒 Seguridad

- Los vectores biométricos se almacenan como arrays numéricos, no las fotos originales
- CORS configurado para red local (ajustar para producción)
- Validación de datos con Pydantic

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas de Desarrollo

### Base de Datos

- SQLite para desarrollo local (`checador_python.db`)
- Las tablas se crean automáticamente al iniciar la aplicación
- Carpeta `uploads/` se genera automáticamente para almacenar fotos de empleados

### Sistema de Reconocimiento

- Threshold de similitud: 0.5 (ajustable en `services/biometric.py`)
- Vectores de 128 dimensiones por rostro
- Algoritmo: Euclidean distance para comparación
- Las fotos se guardan en la carpeta `uploads/` con UUID único

### Lógica de Entrada/Salida

- Auto-detección de entrada/salida basada en último registro
- Periodo de 12 horas para cambio automático de tipo
- Timestamp UTC para consistencia global

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado para RockySushi Sistema Completo

## 🐛 Reportar Problemas

Si encuentras algún bug o tienes una sugerencia, por favor abre un [issue](https://github.com/Ozelot12100/checador-facial-ai/issues).

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
