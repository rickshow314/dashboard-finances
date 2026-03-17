"""
Seguridad - Funciones de autenticación JWT, hash de contraseñas, etc.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from app.core.config import settings

# ==================== CONFIGURACIÓN ====================

BCRYPT_ROUNDS = 12
security = HTTPBearer()

# ==================== FUNCIONES HASH ====================

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    # Convertir a bytes
    password_bytes = password.encode('utf-8')
    # Truncar a 72 bytes si es necesario (límite de bcrypt)
    password_bytes = password_bytes[:72]
    # Hashear
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    plain_password_bytes = plain_password.encode('utf-8')[:72]
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


# ==================== JWT ====================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un JWT access token.
    
    Args:
        data: Datos a incluir en el token (típicamente {"sub": user_id})
        expires_delta: Tiempo de expiración personalizado (usa config si no se provee)
    
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT access token.
    
    Args:
        token: Token JWT a validar
    
    Returns:
        Datos decodificados del token
    
    Raises:
        HTTPException: Si el token es inválido o está expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==================== DEPENDENCIAS ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependencia para obtener el usuario actual desde el token JWT.
    
    Uso en endpoints:
        @app.get("/protected")
        def protected_route(current_user: dict = Depends(get_current_user)):
            return {"user_id": current_user["sub"]}
    
    Args:
        credentials: Credenciales HTTP Bearer extraídas automáticamente
    
    Returns:
        Payload decodificado del token (incluye "sub" = user_id)
    
    Raises:
        HTTPException: Si el token es inválido o no se proporciona
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Versión opcional de get_current_user.
    Retorna None si no se proporciona token.
    
    Args:
        credentials: Credenciales HTTP Bearer (opcional)
    
    Returns:
        Payload del token si está presente, None si no hay token
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload
