"""
Users Router - Placeholder para autenticación futura

Este router será expandido cuando se implemente JWT Authentication.
Por ahora, solo proporciona un endpoint de login básico.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/", tags=["Health Check"])
async def users_health():
    """Health check para users"""
    return {"status": "users router active", "message": "JWT authentication coming soon"}
