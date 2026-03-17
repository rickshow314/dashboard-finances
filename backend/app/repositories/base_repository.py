"""
Base Repository - Clase base con operaciones CRUD comunes.

Proporciona métodos estándar reutilizables para todas las entidades.
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import desc

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Clase base para todos los repositorios"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene un registro por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtiene todos los registros con paginación"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: dict) -> T:
        """Crea un nuevo registro"""
        db_obj = self.model(**obj)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj: dict) -> Optional[T]:
        """Actualiza un registro"""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in obj.items():
                if value is not None:
                    setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Elimina un registro"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
