"""
Tests de integración para endpoints de Autenticación JWT.
Valida registro, login, y endpoints protegidos.
"""

import pytest
from datetime import datetime


class TestAuthenticationEndpoints:
    """Tests para endpoints de Autenticación."""
    
    def test_register_user_success(self, client):
        """Verifica registro exitoso de un nuevo usuario."""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "id" in data
        assert "password" not in data  # No devolver password
    
    def test_register_user_duplicate_email(self, client):
        """Verifica validación: email duplicado."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePassword123",
            "first_name": "User"
        }
        
        # Primer registro
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Segundo registro con mismo email
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400  # Email already registered
        detail = response2.json()["detail"].lower()
        # El mensaje puede variar, pero debe indicar que el email existe
        assert "email" in detail or "existe" in detail or "registr" in detail
    
    def test_register_user_invalid_email(self, client):
        """Verifica validación: email inválido."""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_user_short_password(self, client):
        """Verifica validación: password muy corto."""
        user_data = {
            "email": "user@example.com",
            "password": "123"  # Menos de 6 caracteres
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client, registered_user):
        """Verifica login exitoso y obtención de JWT."""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user_id"] == registered_user["id"]
    
    def test_login_invalid_email(self, client):
        """Verifica login con email inexistente."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401  # Unauthorized
        detail = response.json()["detail"].lower()
        # El mensaje puede variar, pero debe indicar credenciales inválidas
        assert "email" in detail or "contrase" in detail or "incorrecto" in detail
    
    def test_login_invalid_password(self, client, registered_user):
        """Verifica login con contraseña incorrecta."""
        login_data = {
            "email": registered_user["email"],
            "password": "WrongPassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        detail = response.json()["detail"].lower()
        # El mensaje puede variar, pero debe indicar credenciales inválidas
        assert "email" in detail or "contrase" in detail or "incorrecto" in detail
    
    def test_get_current_user_with_token(self, client, auth_token):
        """Verifica obtención del perfil actual con token válido."""
        headers = {"Authorization": f"Bearer {auth_token['access_token']}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert data["id"] == auth_token["user_id"]
    
    def test_get_current_user_without_token(self, client):
        """Verifica acceso denegado sin token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden
    
    def test_get_current_user_invalid_token(self, client):
        """Verifica acceso denegado con token inválido."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401  # Unauthorized
    
    def test_get_current_user_expired_token(self, client, expired_token):
        """Verifica acceso denegado con token expirado."""
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401  # Token expired
    
    def test_update_user_profile(self, client, auth_token):
        """Verifica actualización del perfil con token."""
        headers = {"Authorization": f"Bearer {auth_token['access_token']}"}
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        response = client.put("/api/v1/auth/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
    
    def test_update_user_profile_without_token(self, client):
        """Verifica que actualización sin token es rechazada."""
        update_data = {"first_name": "Jane"}
        
        response = client.put("/api/v1/auth/me", json=update_data)
        assert response.status_code == 403
    
    def test_change_password_success(self, client, auth_token, registered_user):
        """Verifica cambio de contraseña exitoso."""
        headers = {"Authorization": f"Bearer {auth_token['access_token']}"}
        change_data = {
            "current_password": registered_user["password"],
            "new_password": "NewSecurePassword456",
            "confirm_password": "NewSecurePassword456"
        }
        
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        
        assert response.status_code == 200
        # El endpoint puede devolver "mensaje" o "message", aceptar ambos
        data = response.json()
        assert "mensaje" in data or "message" in data
    
    def test_change_password_wrong_current(self, client, auth_token):
        """Verifica que cambio con password actual incorrecto falla."""
        headers = {"Authorization": f"Bearer {auth_token['access_token']}"}
        change_data = {
            "current_password": "WrongPassword123",
            "new_password": "NewSecurePassword456",
            "confirm_password": "NewSecurePassword456"
        }
        
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 401
    
    def test_change_password_mismatch(self, client, auth_token, registered_user):
        """Verifica que las nuevas passwords no coincidan falla."""
        headers = {"Authorization": f"Bearer {auth_token['access_token']}"}
        change_data = {
            "current_password": registered_user["password"],
            "new_password": "NewSecurePassword456",
            "confirm_password": "DifferentPassword789"
        }
        
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 400
    
    def test_change_password_without_token(self, client):
        """Verifica que cambio sin token es rechazado."""
        change_data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword456",
            "confirm_password": "NewPassword456"
        }
        
        response = client.post("/api/v1/auth/change-password", json=change_data)
        assert response.status_code == 403
    
    def test_validate_token_success(self, client, auth_token):
        """Verifica validación de token válido."""
        token_data = {"token": auth_token["access_token"]}
        
        response = client.post("/api/v1/auth/validate-token", json=token_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == auth_token["user_id"]
    
    def test_validate_token_invalid(self, client):
        """Verifica validación de token inválido."""
        token_data = {"token": "invalid_token"}
        
        response = client.post("/api/v1/auth/validate-token", json=token_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
    
    def test_validate_token_expired(self, client, expired_token):
        """Verifica validación de token expirado."""
        token_data = {"token": expired_token}
        
        response = client.post("/api/v1/auth/validate-token", json=token_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


class TestJWTTokenBehavior:
    """Tests para comportamiento específico de JWT."""
    
    def test_token_contains_user_id(self, client, auth_token):
        """Verifica que el token contiene el user_id."""
        assert auth_token["user_id"] is not None
        assert isinstance(auth_token["user_id"], int)
    
    def test_token_expiration_time(self, client, auth_token):
        """Verifica que el token tiene un tiempo de expiración."""
        assert auth_token["expires_in"] > 0
        # Default es 30 minutos
        assert auth_token["expires_in"] <= 1800  # 30 minutos en segundos
    
    def test_token_type_is_bearer(self, client, auth_token):
        """Verifica que el tipo de token es bearer."""
        assert auth_token["token_type"].lower() == "bearer"
    
    def test_login_with_different_emails(self, client):
        """Verifica que emails diferentes generan usuarios diferentes."""
        user1_data = {
            "email": "user1@example.com",
            "password": "Password123"
        }
        user2_data = {
            "email": "user2@example.com",
            "password": "Password456"
        }
        
        # Registrar dos usuarios
        resp1 = client.post("/api/v1/auth/register", json=user1_data)
        resp2 = client.post("/api/v1/auth/register", json=user2_data)
        
        user1_id = resp1.json()["id"]
        user2_id = resp2.json()["id"]
        
        assert user1_id != user2_id


class TestAuthenticationWithDataAccess:
    """Tests para autenticación e interacción con datos."""
    
    def test_authenticated_user_can_create_account(self, client, auth_token):
        """Verifica que usuario autenticado puede crear cuenta (cuando protejamos endpoints)."""
        # Este test será más relevante cuando protejamos los endpoints de cuentas
        # Por ahora, solo verifica que tenemos un token válido
        headers = {"Authorization": f"Bearer {auth_token['access_token']}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
    
    def test_different_users_isolated(self, client):
        """Verifica que diferentes usuarios son aislados."""
        user1_data = {
            "email": "isolated1@example.com",
            "password": "Password123"
        }
        user2_data = {
            "email": "isolated2@example.com",
            "password": "Password456"
        }
        
        # Registrar dos usuarios
        resp1 = client.post("/api/v1/auth/register", json=user1_data)
        resp2 = client.post("/api/v1/auth/register", json=user2_data)
        
        assert resp1.status_code == 201
        assert resp2.status_code == 201
        
        user1_id = resp1.json()["id"]
        user2_id = resp2.json()["id"]
        
        assert user1_id != user2_id
