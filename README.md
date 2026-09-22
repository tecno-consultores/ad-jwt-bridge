# AD JWT Bridge

Microservicio construido con FastAPI diseñado para actuar como un Identity Broker (Capa Intermedia). Permite validar credenciales contra un controlador de dominio Active Directory (Windows Server 2012 R2) vía LDAP/LDAPS, y emite JSON Web Tokens (JWT) firmados asimétricamente mediante RS256 para que otros microservicios validen la identidad sin conexión directa al AD.

La API ha sido diseñada con estándares de nivel empresarial:
*   **Modelos Estructurados:** Uso de Pydantic para la validación estricta de formularios OAuth2.
*   **Código Impecable:** Formateo automático y linting ultrarrápido garantizado por `ruff`.
*   **Alta Fiabilidad:** Probada exhaustivamente con una cobertura de código superior al 95%.
*   **Tipado Estricto:** Código 100% validado estáticamente en origen mediante `mypy`.
*   **Compatibilidad Total:** Matriz de pruebas automatizada para múltiples versiones de Python.
*   **Interoperabilidad:** Políticas CORS configuradas para integraciones seguras con Frontends (React, Vue, etc.).

## Configuración

La API lee sus parámetros de conexión y seguridad desde variables de entorno. En la raíz de tu proyecto, crea un archivo `.env` con la siguiente estructura:

```ini
# Configuración de Active Directory
AD_URL="ldaps://192.168.1.1:636"
AD_DOMAIN="TU_DOMINIO_CORTO"
AD_SEARCH_BASE="dc=tu-dominio,dc=local"
AD_TIMEOUT=5

# Credenciales de Servicio a Servicio (Service-to-Service)
SERVICE_CLIENT_ID="microservicio-cliente"
SERVICE_CLIENT_SECRET="secreto-robusto-123"

# Credenciales exclusivas para las pruebas de integración End-to-End
TEST_AD_USER="tu_usuario_de_prueba"
TEST_AD_PASSWORD="tu_password_seguro"
```

> **Importante:** Asegúrate de que el archivo `.env` esté incluido en tu `.gitignore` para evitar exponer tus credenciales.

## Preparación y Ejecución

### 1. Generación de Claves RSA (Obligatorio)
Para evitar que los tokens emitidos se invaliden al reiniciar el contenedor, el broker requiere una clave privada física persistente. Antes de iniciar el servicio por primera vez, ejecuta:

```bash
chmod +x setup_certs.sh
./setup_certs.sh
```
Esto creará el archivo `certs/private_key.pem`.

### 2. Levantar el Servicio en Vivo (Desarrollo)
La API se despliega mediante Docker, instalando dependencias al vuelo gracias a `uv`.

```bash
docker compose up api
```
Una vez iniciado, visita `http://localhost:8000/docs` para acceder a la interfaz interactiva (Swagger UI) y probar la emisión de tokens en caliente.

### 3. Ejecución de la Suite de Pruebas
Si prefieres no instalar dependencias en tu sistema anfitrión, puedes ejecutar las herramientas de validación a través del contenedor de pruebas aislado:

```bash
docker compose run --rm test bash -c "uv pip install --system -e '.[dev]' && pytest -v"
```

## Endpoints Principales

1.  **`GET /.well-known/jwks.json` (Público):** Expone las claves públicas (JWKS). Otros microservicios deben consumir este endpoint para validar criptográficamente las firmas de los tokens emitidos.
2.  **`POST /token` (Autenticación):** 
    *   Acepta `grant_type=password` para validar usuarios de Active Directory y extraer sus grupos.
    *   Acepta `grant_type=client_credentials` para la comunicación máquina a máquina (Service-to-Service).
