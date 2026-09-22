# Guía de Contribución y Desarrollo

Gracias por interesarte en el desarrollo de `ad-jwt-bridge`. Este documento explica cómo está configurado el entorno de trabajo y cuáles son los pasos exactos para probar el código.

## Entorno de Trabajo

Este repositorio incluye un entorno basado en Docker Compose diseñado para aislar completamente el ciclo de desarrollo. De esta manera, garantizamos la reproducibilidad de las pruebas sin depender de la configuración local o de las dependencias instaladas en el sistema anfitrión.

## Calidad de Código y Pruebas (Testing)

Para garantizar un estándar de nivel empresarial, el proyecto implementa múltiples capas de validación automatizada:

1.  **Linting y Formateo Automático:** Uso de `ruff` para asegurar estilo uniforme y detectar *imports* desordenados al instante.
2.  **Pruebas Unitarias y de Integración:** A través de `pytest`, simulando a `ldap3` u operando en vivo.
3.  **Cobertura de Código:** Medida con `pytest-cov`, garantizando más del 95% de ejecución.
4.  **Análisis Estático de Tipos:** Código validado en modo estricto con `mypy`.
5.  **Matriz de Compatibilidad:** Pruebas orquestadas con `tox` para múltiples intérpretes.

### Comandos Clave de Desarrollo

**A. La Matriz Completa (Auditoría Integral):**
Ideal antes de un commit.
```bash
docker compose run --rm -e UV_PYTHON_DOWNLOADS=true test bash -c "uv pip install --system -e '.[dev]' && tox"
```

**B. Auto-corrección de Estilo (Ruff):**
Formatea y arregla automáticamente los espacios, límites de línea e *imports* del proyecto.
```bash
docker compose run --rm test bash -c "uv pip install --system -e '.[dev]' && ruff format src/ tests/ && ruff check --fix src/ tests/"
```

## Solución de Problemas (Troubleshooting)

### Archivos de caché rastreados accidentalmente por Git
Si Git incluyó carpetas de caché temporal (como `.ruff_cache/` o `.pytest_cache/`) antes de que el archivo `.gitignore` fuera configurado, estas seguirán apareciendo en los *commits* futuros. Para obligar a Git a olvidarlas sin eliminarlas de tu disco duro, ejecuta:

```bash
git rm -r --cached .ruff_cache/
git rm -r --cached .pytest_cache/
git rm -r --cached .tox/
```
