import os

import pytest

from src.ldap_service.client import ADClient

# Este marcador asegura que pytest la ignore a menos que uses "-m integration"
pytestmark = pytest.mark.integration

def test_real_ad_connection_success():
    # 1. Cargar configuración desde el entorno
    ad_url = os.getenv("AD_URL")
    ad_domain = os.getenv("AD_DOMAIN")
    search_base = os.getenv("AD_SEARCH_BASE")
    username = os.getenv("TEST_AD_USER")
    password = os.getenv("TEST_AD_PASSWORD")

    # 2. Protección: abortar limpia y claramente si faltan credenciales
    if not all([ad_url, ad_domain, search_base, username, password]):
        pytest.skip("Omitiendo prueba: Faltan variables en el .env para conectar al AD real")

    # 3. Inicializar el cliente con un timeout holgado (útil si el tráfico 
    #    pasa a través de túneles como WireGuard o Tailscale hacia tu infraestructura)
    client = ADClient(server_uri=ad_url, domain=ad_domain, search_base=search_base, timeout=10)
    
    # 4. Ejecutar la autenticación real
    result = client.authenticate_and_get_groups(username, password)
    
    # 5. Validar la estructura de la respuesta
    assert result is not None, "La conexión falló o las credenciales son incorrectas"
    assert result["username"] == username
    assert isinstance(result["groups"], list)
    
    # Imprimimos los grupos para que puedas verificarlos visualmente en la terminal
    print(f"\n[ÉXITO] Usuario: {result['display_name']} | Grupos extraídos: {result['groups']}")

def test_real_ad_connection_wrong_password():
    ad_url = os.getenv("AD_URL")
    ad_domain = os.getenv("AD_DOMAIN")
    search_base = os.getenv("AD_SEARCH_BASE")
    username = os.getenv("TEST_AD_USER")
    
    if not all([ad_url, ad_domain, search_base, username]):
        pytest.skip("Omitiendo prueba por falta de variables en el .env")

    client = ADClient(server_uri=ad_url, domain=ad_domain, search_base=search_base, timeout=10)
    
    # Forzar una contraseña incorrecta
    result = client.authenticate_and_get_groups(username, "ClaveIncorrecta123!")
    
    # El broker debe manejar el error y devolver None sin colapsar
    assert result is None
