# Estrategia de Pruebas (Testing)

En `ad-jwt-bridge` mantenemos un estándar estricto de calidad de código. Este documento detalla la arquitectura de pruebas implementada para garantizar la estabilidad de la API, la integridad criptográfica y la resiliencia ante fallos de red.

## 1. Tipos de Pruebas y Tecnologías Utilizadas

Nuestra suite de validación se divide en dos enfoques principales:

### A. Pruebas Unitarias (Unit Tests)
*   **Propósito:** Verificar el comportamiento lógico interno del Identity Broker (generación JWT, inyección de dependencias, políticas CORS) de forma completamente aislada, determinista y ultrarrápida.
*   **Paquetes y tecnologías:** `pytest` actúa como el motor de ejecución principal. Utilizamos `unittest.mock` con `@patch` para interceptar la librería `ldap3` e inyectar variables de entorno efímeras.
*   **Manejo Criptográfico (conftest.py):** Para evitar fallos en entornos limpios de CI/CD que no posean la clave RSA física (`private_key.pem`), el archivo `conftest.py` intercepta el inicio de la prueba y genera una clave "dummy" temporal de 2048 bits de forma automática.
*   **Diferencia clave:** En esta prueba nunca hay conexión a la red ni al controlador de dominio.

### B. Pruebas de Integración (Integration Tests)
*   **Propósito:** Validar la comunicación real de extremo a extremo (End-to-End) con el servidor Active Directory en producción. 
*   **Paquetes y tecnologías:** Ejecutadas mediante `pytest`, aisladas con el marcador explícito `pytest -m integration`. La configuración depende de inyectar las credenciales reales desde el archivo `.env` local.
*   **Diferencia clave:** Esta prueba requiere red y credenciales reales. Fallará automáticamente si el servidor de Windows 2012 R2 cae o cambia sus políticas de seguridad (TLS).

---

## 2. Pilares de Calidad y Validación Avanzada

### A. Linting y Formateo Automático
*   **Propósito:** Asegurar que el código comparta el mismo estilo visual (PEP 8, máximo 120 caracteres por línea).
*   **Herramienta:** `ruff` (linter ultrarrápido escrito en Rust).
*   **Implementación:** Ruff está integrado como el primer paso de nuestra matriz en Tox; si el código no cumple las reglas, la prueba se aborta inmediatamente.

### B. Análisis de Cobertura
*   **Propósito:** Cuantificar qué porcentaje del código fuente es validado.
*   **Herramienta:** `pytest-cov`.
*   **Implementación:** Exigimos un estándar de cobertura superior al 95%. Forzamos la evaluación de bloques `try/except` simulando errores de conexión LDAP.

### C. Análisis Estático de Tipos
*   **Propósito:** Auditar el flujo de datos para garantizar que variables y retornos coincidan con la estructura esperada.
*   **Herramienta:** `mypy` configurado en modo estricto.
*   **Implementación:** Mypy audita el 100% de la base, previniendo excepciones en tiempo de ejecución.

### D. Testing de Matriz
*   **Propósito:** Certificar la compatibilidad universal del paquete contra múltiples intérpretes.
*   **Herramientas:** `tox` potenciado por `tox-uv`.
*   **Implementación:** Levanta entornos aislados para Python 3.10, 3.11, 3.12 y 3.13.

---

## 3. Ejecución de las Pruebas

Toda la suite de validación está empaquetada dentro de contenedores Docker para evitar conflictos locales.

**A. Validación Estricta (Requerido antes de desplegar):**
Descarga versiones, audita con Ruff, ejecuta análisis estático y corre todas las pruebas unitarias en todas las versiones soportadas.
```bash
docker compose run --rm -e UV_PYTHON_DOWNLOADS=true test bash -c "uv pip install --system -e '.[dev]' && tox"
```

**B. Ejecución Rápida de Desarrollo (Unitarias):**
Omite la red y evalúa la lógica.
```bash
docker compose run --rm test bash -c "uv pip install --system -e '.[dev]' && pytest -m 'not integration' -v"
```

**C. Prueba Exclusiva de Conexión (Solo Integración):**
Verifica únicamente si la comunicación segura con el Active Directory local funciona.
```bash
docker compose run --rm test bash -c "uv pip install --system -e '.[dev]' && pytest -m integration -v -s"
```
