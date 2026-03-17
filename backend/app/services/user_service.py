"""
User Service - Lógica de negocio para usuarios
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.schemas.auth import UserCreate, UserResponse


class UserService:
    """Servicio de usuarios"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crea un nuevo usuario"""
        # Verificar que el email no exista
        if self.user_repo.exists_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Hashear contraseña
        password_hash = hash_password(user_data.password)
        
        # Crear usuario
        user = self.user_repo.create(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        return UserResponse.model_validate(user)
    
    def authenticate_user(self, email: str, password: str) -> dict:
        """
        Autentica un usuario y retorna sus datos.
        
        Raises:
            HTTPException: Si el email no existe o la contraseña es incorrecta
        """
        user = self.user_repo.get_by_email(email)
        
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario ha sido desactivado"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    
    def get_user(self, user_id: int) -> UserResponse:
        """Obtiene un usuario por ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UserResponse.model_validate(user)
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Cambia la contraseña de un usuario"""
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La contraseña actual es incorrecta"
            )
        
        # Actualizar contraseña
        password_hash = hash_password(new_password)
        self.user_repo.update_password(user_id, password_hash)
    
    def update_user(self, user_id: int, **kwargs) -> UserResponse:
        """Actualiza datos del usuario (no contraseña)"""
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No permitir cambio de email si ya existe
        if "email" in kwargs and kwargs["email"] != user.email:
            if self.user_repo.exists_email(kwargs["email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
        
        updated_user = self.user_repo.update(user_id, **kwargs)
        return UserResponse.model_validate(updated_user)
