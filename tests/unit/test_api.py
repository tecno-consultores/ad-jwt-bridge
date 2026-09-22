from typing import Any

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
def test_jwks_endpoint() -> None:
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) > 0
    assert data["keys"][0]["alg"] == "RS256"
    assert data["keys"][0]["use"] == "sig"

def test_service_to_service_auth_success() -> None:
    response = client.post(
        "/token", 
        data={
            "grant_type": "client_credentials",
            "client_id": "microservicio-cliente",
            "client_secret": "secreto-robusto-123",
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_service_to_service_auth_invalid() -> None:
    response = client.post(
        "/token", 
        data={
            "grant_type": "client_credentials",
            "client_id": "microservicio-cliente",
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
