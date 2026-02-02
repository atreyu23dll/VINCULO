#!/bin/bash

# ==========================================
# SCRIPT DE CONFIGURACIÓN AUTOMÁTICA DE ENTORNOS
# PROYECTO: VINCULO
# ==========================================

# 1. Encontrar la raíz del proyecto dinámicamente
# Detecta dónde está este script y sube un nivel para llegar a la raíz
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

echo "📂 Raíz del proyecto detectada: $PROJECT_ROOT"
echo "🔄 Detectando configuración de red..."

MY_IP=""

# 2. DETECCIÓN DE ENTORNO (WSL vs LINUX NATIVO)
# Si es WSL, necesitamos pedirle la IP a Windows, no a Linux.
if grep -qi "microsoft" /proc/version; then
    echo "🪟 Detectado entorno WSL (Windows Subsystem for Linux)."
    echo "   ⏳ Consultando IP de Windows vía PowerShell (esto puede tardar unos segundos)..."
    
    # Intento 1: Buscar interfaz Wi-Fi en Windows
    # El 'tr -d \r' borra el retorno de carro de Windows que rompe los .env
    MY_IP=$(powershell.exe -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi').IPAddress" 2>/dev/null | tr -d '\r')
    
    # Intento 2: Si no hay Wi-Fi, buscar Ethernet
    if [ -z "$MY_IP" ]; then
         MY_IP=$(powershell.exe -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Ethernet').IPAddress" 2>/dev/null | tr -d '\r')
    fi
fi

# 3. DETECCIÓN ESTÁNDAR (LINUX / MAC)
# Si no es WSL o falló lo anterior, usamos el método nativo
if [ -z "$MY_IP" ]; then
    # 'ip route get 1.1.1.1' nos dice qué IP usa la PC para salir a internet
    MY_IP=$(ip route get 1.1.1.1 2>/dev/null | sed -n 's/.*src \([0-9.]\+\).*/\1/p')
fi

# Fallback final de emergencia
if [ -z "$MY_IP" ]; then
    MY_IP=$(hostname -I | awk '{print $1}')
fi

echo "📍 Tu IP local asignada es: $MY_IP"
echo "----------------------------------------"

# 4. CONFIGURAR FRONTEND (React Native)
FRONT_ENV="$PROJECT_ROOT/appVinculo/.env"
echo "📝 Generando configuración Frontend en: appVinculo/.env"

echo "# Auto-generado por script/generar_env.sh" > "$FRONT_ENV"
echo "# Esta IP permite que tu celular encuentre a tu PC" >> "$FRONT_ENV"
echo "EXPO_PUBLIC_API_URL=http://$MY_IP:8000" >> "$FRONT_ENV"


# 5. CONFIGURAR BACKEND (FastAPI / Docker)
BACK_ENV="$PROJECT_ROOT/backend/.env"
echo "📝 Generando configuración Backend en: backend/.env"

echo "# Auto-generado por script/generar_env.sh" > "$BACK_ENV"
# La DB usa el nombre del servicio de Docker ('db'), no la IP local
echo "DATABASE_URL=postgresql://user:password@db:5432/vinculo_db" >> "$BACK_ENV"
echo "SECRET_KEY=admin1234" >> "$BACK_ENV"
echo "DEBUG=True" >> "$BACK_ENV"

echo "----------------------------------------"
echo "✅ ¡TODO LISTO!"
echo "   Ejecuta: docker compose up --build"