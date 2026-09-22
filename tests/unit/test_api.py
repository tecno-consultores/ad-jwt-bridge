import os
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.routes import app, get_ad_client

client = TestClient(app)

# --- Dependencia Falsa (Mock) para FastAPI ---
class MockADClient:
    def authenticate_and_get_groups(self, username: str, password: str) -> dict[str, Any] | None:
        if username == "admin_mock" and password == "correct_pass":
            return {"username": "admin_mock", "groups": ["Admins"], "display_name": "Admin Mock"}
        return None

# Sobreescribimos la dependencia real con nuestro mock antes de correr las pruebas
app.dependency_overrides[get_ad_client] = lambda: MockADClient()

# --- Pruebas ---
def test_cors_headers() -> None:
    # Simulamos una petición 'preflight' de un navegador (ej. React/Vue) desde otro dominio
    test_origin = "http://frontend-service.local"
    response = client.options(
        "/.well-known/jwks.json",
        headers={
            "Origin": test_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    # FastAPI refleja el origen exacto porque allow_credentials=True prohíbe usar "*"
    assert response.headers["access-control-allow-origin"] == test_origin

def test_jwks_endpoint() -> None:
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) > 0
    assert data["keys"][0]["alg"] == "RS256"
    assert data["keys"][0]["use"] == "sig"

# Usamos patch.dict para inyectar variables de entorno temporalmente solo durante esta prueba
@patch.dict(os.environ, {"SERVICE_CLIENT_ID": "test-id", "SERVICE_CLIENT_SECRET": "test-secret"})
def test_service_to_service_auth_success() -> None:
    response = client.post(
        "/token", 
        data={
            "grant_type": "client_credentials",
            "client_id": "test-id",
            "client_secret": "test-secret",
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@patch.dict(os.environ, {"SERVICE_CLIENT_ID": "test-id", "SERVICE_CLIENT_SECRET": "test-secret"})
def test_service_to_service_auth_invalid() -> None:
    response = client.post(
        "/token", 
        data={
            "grant_type": "client_credentials",
            "client_id": "test-id",
            "client_secret": "clave_equivocada",
        }
    )
    assert response.status_code == 401

def test_user_ad_auth_success() -> None:
    response = client.post(
        "/token",
        data={"grant_type": "password", "username": "admin_mock", "password": "correct_pass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_user_ad_auth_failure() -> None:
    response = client.post(
        "/token",
        data={"grant_type": "password", "username": "admin_mock", "password": "wrong_password"}
    )
    assert response.status_code == 401

def test_get_ad_client_dependency() -> None:
    from src.api.routes import get_ad_client
    client_instance = get_ad_client()
    assert client_instance is not None

def test_unsupported_grant_type() -> None:
    response = client.post("/token", data={"grant_type": "unsupported_grant"})
    assert response.status_code == 400
