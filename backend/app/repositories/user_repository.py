"""
User Repository - Operaciones CRUD para usuarios
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import User


class UserRepository:
    """Repositorio para operaciones con usuarios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, password_hash: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
        """Crea un nuevo usuario"""
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene todos los usuarios"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Actualiza un usuario"""
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if value is not None and key != "password_hash":
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update_password(self, user_id: int, password_hash: str) -> Optional[User]:
        """Actualiza la contraseña de un usuario"""
        user = self.get_by_id(user_id)
        if user:
            user.password_hash = password_hash
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def exists_email(self, email: str) -> bool:
        """Verifica si un email ya existe"""
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def deactivate(self, user_id: int) -> Optional[User]:
        """Desactiva un usuario"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            self.db.refresh(user)
        return user
