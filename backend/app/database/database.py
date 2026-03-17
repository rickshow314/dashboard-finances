"""
Configuración de conexión y sesión de SQLAlchemy.

Maneja:
- Conexión a la base de datos
- Sesiones de SQLAlchemy
- Creación de tablas
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# URL de conexión a la base de datos
DATABASE_URL = settings.DATABASE_URL

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.DATABASE_ECHO,  # Mostrar queries en desarrollo
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Crear SessionLocal para obtener sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency para obtener sesión de base de datos en endpoints.
    
    Uso en FastAPI:
        @app.get("/items/")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """
    Crea todas las tablas en la base de datos.
    
    Nota: En producción, usar Alembic para migraciones.
    """
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Elimina todas las tablas de la base de datos.
    
    Usar solo en desarrollo/testing.
    """
    from app.database.models import Base
    Base.metadata.drop_all(bind=engine)
