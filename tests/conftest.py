import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# --- SETUP PREVIO PARA TESTS ---
# Este bloque se ejecuta antes de que Pytest intente importar 'src.api.routes'.
# Evita que security.py arroje un FileNotFoundError en un clon limpio o pipeline CI/CD.

os.makedirs("certs", exist_ok=True)
key_path = "certs/private_key.pem"

if not os.path.exists(key_path):
    dummy_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    with open(key_path, "wb") as f:
        f.write(
            dummy_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
