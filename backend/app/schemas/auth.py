"""
Schemas de autenticación - Login, Token, Usuario
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    """Schema para respuesta de token"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta que expire el token")
    user_id: int = Field(..., description="ID del usuario autenticado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": 1
            }
        }


class UserCreate(BaseModel):
    """Schema para crear un usuario"""
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=6, description="Contraseña")
    first_name: Optional[str] = Field(None, max_length=100, description="Nombre")
    last_name: Optional[str] = Field(None, max_length=100, description="Apellido")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "securepassword123",
                "first_name": "Juan",
                "last_name": "Pérez"
            }
        }


class UserResponse(BaseModel):
    """Schema para responder datos de usuario"""
    id: int = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    first_name: Optional[str] = Field(None, description="Nombre")
    last_name: Optional[str] = Field(None, description="Apellido")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "Juan",
                "last_name": "Pérez",
                "created_at": "2025-11-18T10:00:00"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    confirm_password: str = Field(..., min_length=6, description="Confirmar nueva contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword456",
                "confirm_password": "newpassword456"
            }
        }
