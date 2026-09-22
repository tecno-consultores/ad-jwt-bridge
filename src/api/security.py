import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generación de clave RSA en memoria. 
# (En producción multinstancia, se podría inyectar desde un gestor de secretos).
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
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
