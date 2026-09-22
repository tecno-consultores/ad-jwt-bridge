from unittest.mock import MagicMock, patch

import pytest
from ldap3.core.exceptions import LDAPException, LDAPSocketOpenError  # type: ignore

from src.ldap_service.client import ADClient


@pytest.fixture
def ad_client() -> ADClient:
    return ADClient(server_uri="ldap://mock-server:389", domain="mock.local", search_base="dc=mock,dc=local")

@patch("src.ldap_service.client.Connection")
@patch("src.ldap_service.client.Server")
def test_authenticate_success(mock_server: MagicMock, mock_connection: MagicMock, ad_client: ADClient) -> None:
    mock_conn_instance = MagicMock()
    mock_connection.return_value = mock_conn_instance
    
    mock_entry = MagicMock()
    mock_entry.displayName = "Usuario Simulado"
    mock_entry.memberOf.values = ["CN=AdminGroup,OU=Users,DC=mock,DC=local"]
    mock_conn_instance.entries = [mock_entry]
    
    result = ad_client.authenticate_and_get_groups("user", "pass")
    
    assert result is not None
    assert result["username"] == "user"
    assert result["display_name"] == "Usuario Simulado"
    assert "AdminGroup" in result["groups"]
    mock_conn_instance.unbind.assert_called_once()

@patch("src.ldap_service.client.Connection")
@patch("src.ldap_service.client.Server")
def test_authenticate_timeout(mock_server: MagicMock, mock_connection: MagicMock, ad_client: ADClient) -> None:
    mock_connection.side_effect = LDAPSocketOpenError("Timeout simulado")
    result = ad_client.authenticate_and_get_groups("user", "pass")
    assert result is None

@patch("src.ldap_service.client.Connection")
@patch("src.ldap_service.client.Server")
def test_authenticate_invalid_credentials(
    mock_server: MagicMock, mock_connection: MagicMock, ad_client: ADClient
) -> None:
    mock_connection.side_effect = LDAPException("Credenciales inválidas")
    result = ad_client.authenticate_and_get_groups("user", "pass")
    assert result is None

def test_client_init_ldaps() -> None:
    client = ADClient(server_uri="ldaps://mock-server:636", domain="mock", search_base="dc=mock")
    assert client.use_ssl is True
    assert client.tls_config is not None
