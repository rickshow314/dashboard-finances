"""
Main FastAPI Application - Dashboard Financiero

Configuración central de la aplicación, routers, middleware y lifecycle events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.database import create_all_tables

# ==================== CONFIGURACIÓN DE LOGGING ====================

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== CREAR APP ====================

app = FastAPI(
    title=settings.APP_NAME,
    description="API REST para Dashboard Financiero Personal",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)


# ==================== MIDDLEWARE CORS ====================

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS configurado para orígenes: %s", settings.BACKEND_CORS_ORIGINS)


# ==================== REGISTRAR ROUTERS ====================

# Authentication endpoints
from app.api.routers_auth import router as auth_router
app.include_router(auth_router)
logger.info("✅ Router de Autenticación registrado")

# Analytics endpoints
from app.api.routers_analytics import router as analytics_router
app.include_router(analytics_router)
logger.info("✅ Router de Analytics registrado")

# CRUD endpoints - Accounts & Transactions
from app.api.routers_accounts_transactions import router as accounts_transactions_router
app.include_router(accounts_transactions_router)
logger.info("✅ Router de Accounts & Transactions registrado")

# CRUD endpoints - Budgets
from app.api.routers_budgets import router as budgets_router
app.include_router(budgets_router)
logger.info("✅ Router de Budgets registrado")

# CRUD endpoints - Categories, Recurring, Goals
from app.api.routers_crud import router as crud_router
app.include_router(crud_router)
logger.info("✅ Router de CRUD (Categories, Recurring, Goals) registrado")

# Users endpoints (legacy)
from app.api.routers_users import router as users_router
app.include_router(users_router)
logger.info("✅ Router de Users registrado")


# ==================== LIFECYCLE EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """
    Se ejecuta al iniciar la aplicación.
    Crea las tablas de la BD si no existen.
    """
    logger.info("🚀 Iniciando aplicación...")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Base de datos: {settings.DATABASE_URL}")
    
    try:
        create_all_tables()
        logger.info("✅ Tablas de base de datos verificadas/creadas")
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {e}")
        raise
    
    logger.info("✅ Aplicación lista para recibir requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta al cerrar la aplicación"""
    logger.info("🛑 Cerrando aplicación...")


# ==================== RUTAS BASE ====================

@app.get("/", tags=["Health Check"])
async def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {
        "mensaje": "Bienvenido a Dashboard Financiero API",
        "versión": "1.0.0",
        "documentación": "/api/docs",
        "estado": "operacional"
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check para monitoreo"""
    return {
        "estado": "ok",
        "aplicación": settings.APP_NAME,
        "entorno": settings.ENVIRONMENT
    }


@app.get("/api/health", tags=["Health Check"])
async def api_health_check():
    """Health check API para monitoreo"""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }


# ==================== MANEJO DE ERRORES GLOBAL ====================

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Manejo de errores de validación"""
    logger.warning(f"Error de validación: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detalle": "Error de validación",
            "errores": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo de errores generales"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detalle": "Error interno del servidor",
            "tipo": exc.__class__.__name__
        }
    )


# ==================== INFO ====================

logger.info(f"""
╔════════════════════════════════════════════════════════════════════════╗
║           DASHBOARD FINANCIERO API - v1.0.0                            ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  📊 ENDPOINTS DISPONIBLES: 55 endpoints total                         ║
║                                                                        ║
║  ✅ API OPERACIONAL Y LISTA PARA TESTING                              ║
║                                                                        ║
║  🔍 HEALTH CHECK:                                                      ║
║    GET  /                    - Verificar API                           ║
║    GET  /health              - Health check                            ║
║                                                                        ║
║  🔐 AUTENTICACIÓN:                                                     ║
║    POST /api/v1/auth/register    - Registrarse                         ║
║    POST /api/v1/auth/login       - Iniciar sesión (obtener token)      ║
║    GET  /api/v1/auth/me          - Obtener perfil (requiere token)     ║
║    PUT  /api/v1/auth/me          - Actualizar perfil (requiere token)  ║
║    POST /api/v1/auth/change-password - Cambiar contraseña              ║
║    POST /api/v1/auth/validate-token  - Validar token                   ║
║                                                                        ║
║  💰 CUENTAS + 📝 TRANSACCIONES + 📊 PRESUPUESTOS                       ║
║  🏷️  CATEGORÍAS + 🔄 RECURRENTES + 🎯 OBJETIVOS                       ║
║                                                                        ║
║  📚 DOCUMENTACIÓN:                                                      ║
║    http://localhost:8000/api/docs             - Swagger UI             ║
║    http://localhost:8000/api/redoc            - ReDoc                  ║
║                                                                        ║
║  ⚙️  CONFIGURACIÓN:                                                     ║
║    Entorno: {settings.ENVIRONMENT}                                      ║
║    Debug: {settings.DEBUG}                                              ║
║    Base de Datos: BD Local                                             ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
""")
