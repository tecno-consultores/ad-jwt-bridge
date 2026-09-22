#!/usr/bin/env bash
# setup_certs.sh - Generador de claves RSA para AD JWT Bridge

mkdir -p certs

# Solo genera la clave si no existe previamente
if [ ! -f certs/private_key.pem ]; then
    echo "Generando nueva clave RSA de 2048 bits para producción..."
    openssl genrsa -out certs/private_key.pem 2048
    chmod 600 certs/private_key.pem
    echo "Clave generada y protegida en certs/private_key.pem"
else
    echo "La clave RSA ya existe. Omitiendo generación para conservar validez de los JWT actuales."
fi
