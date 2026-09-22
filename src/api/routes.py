import os
from datetime import timedelta
from typing import Any, Optional

from fastapi import Depends, FastAPI, Form, HTTPException, status

from src.api.security import create_access_token, get_jwks
from src.ldap_service.client import ADClient

app = FastAPI(title="AD JWT Bridge", version="0.1.0")

def get_ad_client() -> ADClient:
    return ADClient(
        server_uri=os.getenv("AD_URL", "ldaps://tu-controlador.local:636"),
        domain=os.getenv("AD_DOMAIN", "TU_DOMINIO"),
        search_base=os.getenv("AD_SEARCH_BASE", "dc=tu-dominio,dc=local"),
        timeout=int(os.getenv("AD_TIMEOUT", "5"))
    )

# --- Formulario de Autenticación Universal ---
class BrokerAuthForm:
    def __init__(
        self,
        grant_type: str = Form(...),
        username: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

# --- Endpoints ---
@app.get("/.well-known/jwks.json", tags=["Public"])
async def jwks_endpoint() -> dict[str, Any]:
    return get_jwks()

@app.post("/token", tags=["Auth"])
async def login(
    form_data: BrokerAuthForm = Depends(),
    ad_client: ADClient = Depends(get_ad_client)
) -> dict[str, str]:
    
    # 1. Autenticación Service-to-Service (Client Credentials)
    if form_data.grant_type == "client_credentials":
        valid_services = {"microservicio-cliente": "secreto-robusto-123"}
        
        if form_data.client_id and valid_services.get(form_data.client_id) == form_data.client_secret:
            token = create_access_token(
                data={"sub": form_data.client_id, "type": "service", "roles": ["internal"]},
                expires_delta=timedelta(hours=2)
            )
            return {"access_token": token, "token_type": "bearer"}
            
        raise HTTPException(status_code=401, detail="Credenciales de servicio inválidas")

    # 2. Autenticación de Usuarios (Active Directory)
    if form_data.grant_type == "password":
        if not form_data.username or not form_data.password:
            raise HTTPException(status_code=400, detail="Falta usuario o contraseña")
            
        user_info = ad_client.authenticate_and_get_groups(form_data.username, form_data.password)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas o AD inalcanzable",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = create_access_token(
            data={"sub": user_info["username"], "type": "user", "roles": user_info["groups"]},
            expires_delta=timedelta(minutes=60)
        )
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=400, detail="Grant type no soportado")
