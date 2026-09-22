#!/usr/bin/env bash
# Made by Sinfallas <sinfallas@yahoo.com>
# Licence: GPL-2
LC_ALL=C

if [[ "$EUID" != "0" ]]; then
        echo "ERROR: debe ser root."
        exit 1
fi

clear
echo "Limpiando artefactos del proyecto AD JWT Bridge..."

# Archivos de cobertura
rm -f .coverage
rm -f coverage.xml

# Cachés de herramientas de calidad
rm -rf .mypy_cache
rm -rf .pytest_cache
rm -rf .ruff_cache
rm -rf .tox

# Carpetas de compilación
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

# Búsqueda y eliminación dinámica de todo el bytecode de Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.py[co]" -delete

# Limpieza profunda de Docker
docker system prune -af

echo "Finalizado."
exit 0
