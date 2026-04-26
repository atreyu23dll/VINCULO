#!/bin/bash

# 1. Cargar la IP desde el archivo .env si existe
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "🚀 Iniciando Vínculo con IP: $MY_IP"

# 2. Limpiar e iniciar servicios
# El backend ejecutará automáticamente init_db.py y el sembrado de etiquetas
docker compose down
docker compose up -d

# 3. Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios despierten..."
sleep 10

# 4. Configurar Keycloak DESDE EL CONTENEDOR (Portabilidad Total)
echo "⚙️ Configurando Keycloak (Realm, Cliente, Usuario)..."
docker exec vinculo_backend python scripts/configurar_keycloak.py

# 5. Mostrar el QR del Frontend
echo "📱 Levantando el Frontend..."
docker compose stop frontend
docker compose run --service-ports frontend
