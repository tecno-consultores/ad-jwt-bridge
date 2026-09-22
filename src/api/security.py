import base64
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Ruta de la clave montada en el contenedor (por defecto en /app/certs)
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "/app/certs/private_key.pem")

if not os.path.exists(PRIVATE_KEY_PATH):
    raise FileNotFoundError(
        f"CRÍTICO: No se encontró la clave privada en {PRIVATE_KEY_PATH}. "
        "Ejecuta './setup_certs.sh' antes de iniciar el Identity Broker."
    )

# Carga estática de la clave RSA desde el archivo físico
with open(PRIVATE_KEY_PATH, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

public_key = private_key.public_key()

PEM_PRIVATE_KEY = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

def create_access_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "iss": "ad-jwt-bridge"})
    
    encoded_jwt = jwt.encode(to_encode, PEM_PRIVATE_KEY, algorithm="RS256", headers={"kid": "key-1"})
    return encoded_jwt

def int_to_base64url(value: int) -> str:
    value_bytes = value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')
    return base64.urlsafe_b64encode(value_bytes).decode('utf-8').rstrip('=')

def get_jwks() -> dict[str, Any]:
    public_numbers = public_key.public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "key-1",
                "use": "sig",
                "alg": "RS256",
                "n": int_to_base64url(public_numbers.n),
                "e": int_to_base64url(public_numbers.e)
            }
        ]
    }
