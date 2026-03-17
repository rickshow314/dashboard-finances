"""
Authentication Router - Endpoints para autenticación JWT
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import UserService
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password
)
from app.schemas.auth import (
    UserLogin,
    UserCreate,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest
)
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"],
    responses={404: {"description": "No encontrado"}}
)


@router.post("/register", response_model=UserResponse, status_code=201, summary="Registrarse")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema.
    
    - **email**: Email único
    - **password**: Contraseña (mín. 6 caracteres)
    - **first_name**: Nombre (opcional)
    - **last_name**: Apellido (opcional)
    """
    try:
        service = UserService(db)
        return service.create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y retorna un JWT access token.
    
    - **email**: Email registrado
    - **password**: Contraseña
    
    Retorna:
    - access_token: JWT para usar en endpoints protegidos
    - token_type: Siempre "bearer"
    - expires_in: Segundos hasta que expire el token
    - user_id: ID del usuario autenticado
    """
    try:
        service = UserService(db)
        
        # Autenticar usuario
        user_data = service.authenticate_user(credentials.email, credentials.password)
        
        # Crear token
        access_token = create_access_token(
            data={"sub": str(user_data["id"])},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user_data["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserResponse, summary="Obtener perfil actual")
def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil del usuario autenticado.
    
    Requiere: JWT access token en header Authorization
    """
    try:
        service = UserService(db)
        user_id = int(current_user["sub"])
        return service.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/me", response_model=UserResponse, summary="Actualizar perfil")
def update_profile(
    user_update: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado.
    
    Campos permitidos:
    - first_name: Nombre
    - last_name: Apellido
    
    Requiere: JWT access token en header Authorization
    """
    try:
        service = UserService(db)
        user_id = int(current_user["sub"])
        
        # Filtrar solo campos permitidos
        allowed_fields = {"first_name", "last_name"}
        filtered_update = {k: v for k, v in user_update.items() if k in allowed_fields}
        
        return service.update_user(user_id, **filtered_update)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-password", summary="Cambiar contraseña")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mín. 6 caracteres)
    - **confirm_password**: Confirmación de nueva contraseña
    
    Requiere: JWT access token en header Authorization
    """
    try:
        # Validar que las contraseñas coinciden
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las nuevas contraseñas no coinciden"
            )
        
        service = UserService(db)
        user_id = int(current_user["sub"])
        
        service.change_password(user_id, password_data.current_password, password_data.new_password)
        
        return {
            "mensaje": "Contraseña actualizada exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate-token", summary="Validar token")
def validate_token(
    token_data: dict,
    db: Session = Depends(get_db)
):
    """
    Valida que un token JWT sea válido.
    
    Body:
    - **token**: JWT access token a validar
    
    Retorna:
    - valid: True si el token es válido, False si no
    - user_id: ID del usuario si el token es válido
    """
    try:
        from app.core.security import decode_access_token
        
        token = token_data.get("token") if isinstance(token_data, dict) else token_data
        
        if not token:
            return {"valid": False, "user_id": None, "message": "Token no proporcionado"}
        
        decoded = decode_access_token(token)
        return {
            "valid": True,
            "user_id": int(decoded.get("sub")),
            "message": "Token válido"
        }
    except Exception:
        return {"valid": False, "user_id": None, "message": "Token inválido o expirado"}
