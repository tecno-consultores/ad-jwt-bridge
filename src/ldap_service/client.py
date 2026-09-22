import logging
import ssl
from typing import Any

from ldap3 import ALL, SUBTREE, Connection, Server, Tls  # type: ignore
from ldap3.core.exceptions import LDAPException, LDAPSocketOpenError  # type: ignore

logger = logging.getLogger(__name__)

class ADClient:
    def __init__(self, server_uri: str, domain: str, search_base: str, timeout: int = 5) -> None:
        self.server_uri = server_uri
        self.domain = domain
        self.search_base = search_base
        self.timeout = timeout
        
        self.use_ssl = self.server_uri.lower().startswith('ldaps://')
        self.tls_config = None
        
        if self.use_ssl:
            self.tls_config = Tls(
                validate=ssl.CERT_NONE,
                ciphers='ALL:@SECLEVEL=0'
            )

    def authenticate_and_get_groups(self, username: str, password: str) -> dict[str, Any] | None:
        # CAMBIO: Formato UPN (usuario@dominio.local) en lugar de DOMINIO\usuario
        user_principal = f"{username}@{self.domain}"
        
        try:
            server = Server(
                self.server_uri, 
                get_info=ALL, 
                connect_timeout=self.timeout,
                tls=self.tls_config if self.use_ssl else None
            )
            # El intento de conexión a AD se hace aquí
            conn = Connection(server, user=user_principal, password=password, auto_bind=True)
            
            search_filter = f"(&(objectclass=person)(sAMAccountName={username}))"
            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['memberOf', 'displayName']
            )
            
            user_info: dict[str, Any] = {"username": username, "groups": [], "display_name": username}
            if conn.entries:
                entry = conn.entries[0]
                if hasattr(entry, 'displayName') and entry.displayName:
                    user_info["display_name"] = str(entry.displayName)
                if hasattr(entry, 'memberOf') and entry.memberOf:
                    raw_groups = entry.memberOf.values
                    user_info["groups"] = [str(g).split(',')[0].split('=')[1] for g in raw_groups if '=' in str(g)]
                
            conn.unbind()
            return user_info
            
        except LDAPSocketOpenError as e:
            logger.error(f"Timeout o error de red conectando al AD: {e}")
            return None
        except LDAPException as e:
            logger.warning(f"Fallo de autenticación en AD para {username}: {e}")
            return None
