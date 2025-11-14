# Dashboard

Un proyecto full-stack moderno con backend FastAPI y frontend React + Vite.

## 📋 Requisitos Previos

- **Python 3.8+** (recomendado 3.10 o superior)
- **Node.js 18+** y **npm 9+**
- **Git** (opcional, para control de versiones)

## 🚀 Instalación

### Backend (FastAPI)

1. **Navega a la carpeta del backend:**
   ```bash
   cd backend
   ```

2. **Crea un entorno virtual (si no existe):**
   ```bash
   python -m venv venv
   ```

3. **Activa el entorno virtual:**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

### Frontend (React + Vite)

1. **Navega a la carpeta del frontend:**
   ```bash
   cd frontend
   ```

2. **Instala las dependencias:**
   ```bash
   npm install
   ```

## 🏃 Ejecución

### Backend

Desde la carpeta `backend` (con el entorno virtual activado):

```bash
python -m uvicorn app.main:app --reload
```

El servidor estará disponible en: **http://127.0.0.1:8000**

**Documentación interactiva:**
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Frontend

Desde la carpeta `frontend`:

```bash
npm run dev
```

El servidor estará disponible en: **http://localhost:5173**

## 📦 Dependencias del Proyecto

### Backend (`requirements.txt`)
- **FastAPI** - Framework web moderno para APIs
- **Uvicorn** - Servidor ASGI
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **python-dotenv** - Gestión de variables de entorno

### Frontend (`package.json`)
- **React 19** - Librería de UI
- **Vite 7** - Empaquetador y bundler rápido
- **ESLint** - Linter de JavaScript

## 📁 Estructura del Proyecto

```
Dashboard/
├── backend/
│   ├── venv/                    # Entorno virtual
│   ├── app/
│   │   ├── api/                 # Rutas y endpoints
│   │   ├── core/                # Configuración y seguridad
│   │   ├── database/            # Conexión a BD y modelos
│   │   ├── routers/             # Enrutadores adicionales
│   │   ├── schemas/             # Esquemas Pydantic
│   │   ├── services/            # Lógica de negocio
│   │   ├── utils/               # Funciones auxiliares
│   │   └── main.py              # Punto de entrada
│   └── requirements.txt         # Dependencias Python
│
├── frontend/
│   ├── node_modules/            # Dependencias npm
│   ├── src/
│   │   ├── components/          # Componentes reutilizables
│   │   ├── pages/               # Páginas principales
│   │   ├── services/            # Cliente HTTP y API
│   │   ├── assets/              # Recursos estáticos
│   │   ├── App.jsx              # Componente raíz
│   │   └── main.jsx             # Punto de entrada
│   ├── package.json             # Dependencias npm
│   ├── vite.config.js           # Configuración de Vite
│   └── index.html               # HTML principal
│
└── README.md                     # Este archivo
```

## 🔧 Scripts Disponibles

### Backend
```bash
# Ejecutar servidor con recarga automática
python -m uvicorn app.main:app --reload

# Ejecutar servidor sin recarga automática
python -m uvicorn app.main:app
```

### Frontend
```bash
# Ejecutar servidor de desarrollo
npm run dev

# Compilar para producción
npm run build

# Linter (verificar código)
npm run lint

# Preview de la compilación
npm run preview
```

## 🌐 Endpoints Disponibles

### Backend API
- `GET /api/ping` - Verifica que el servidor esté funcionando
- Más rutas disponibles en `/docs`

### Frontend
- `http://localhost:5173/` - Aplicación React

## 📝 Variables de Entorno

Si necesitas variables de entorno, crea un archivo `.env` en la carpeta `backend`:

```
# Ejemplo de .env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

> **Nota:** Recuerda agregar `.env` a `.gitignore` para no compartir datos sensibles.

## 🛠️ Troubleshooting

### El backend no inicia
- Verifica que el entorno virtual esté activado
- Asegúrate de tener Python 3.8+ instalado
- Ejecuta `pip install -r requirements.txt` nuevamente

### El frontend no inicia
- Elimina la carpeta `node_modules/` y el archivo `package-lock.json`
- Ejecuta `npm install` nuevamente
- Verifica que tengas Node.js 18+ instalado

### Puerto 8000 o 5173 ya en uso
```powershell
# Windows - Encontrar y matar proceso por puerto
Get-Process -Name "python" | Stop-Process -Force  # Backend
Get-Process -Name "node" | Stop-Process -Force     # Frontend
```

## 📖 Documentación Adicional

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)

## 👤 Autor

Tu Nombre

## 📄 Licencia

MIT
