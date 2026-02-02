# 🚀 Proyecto Vínculo

¡Bienvenido al repositorio oficial de **Vínculo**! Aquí es donde ocurre la magia. Este proyecto está diseñado para ser moderno, rápido y modular, conectando un frontend poderoso con un backend robusto.

---

## 🛠 stack Tecnológico

- **Frontend**: React Native (Expo) + **NativeWind** (Tailwind CSS).
- **Backend**: FastAPI (Python).
- **Base de Datos**: PostgreSQL.
- **Infraestructura**: Docker & Docker Compose.

---

## 🎒 Prerrequisitos (Antes de empezar)

### 0.1 📱 En tu Celular
Necesitas la app **Expo Go** para poder escanear el código QR y probar la app en tiempo real.
- [Descargar para Android](https://play.google.com/store/apps/details?id=host.exp.exponent)
- [Descargar para iOS](https://apps.apple.com/us/app/expo-go/id982107779)

### 0.2 🪟 Usuarios de Windows (WSL)
Si usas Windows, **necesitas** WSL 2 (Windows Subsystem for Linux), ya que este proyecto usa scripts de bash y Docker.
1.  Abre PowerShell como administrador y ejecuta: `wsl --install`.
2.  Reinicia tu computadora.
3.  Instala **Docker Desktop** para Windows.
4.  En los ajustes de Docker -> *Resources* -> *WSL Integration*, asegúrate de activar la integración con tu distribución (Ubuntu/Debian).

### 0.3 🐧 Usuarios de Linux (Debian ❤️)
Como amamos **Debian**, aquí están los comandos para el sistema operativo supremo:
```bash
# Comandos para Debian (y derivados)
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker
```

---

## 🔥 Inicio Rápido (Setup)

Sigue estos pasos para tener todo corriendo en minutos, ya sea que estés en **Linux** o **WSL (Windows)**.

### 1. Clonar y Preparar Ramas

> ⚠️ **REGLA DE ORO**: Nunca trabajes directo en `main`.

1.  Clona el repositorio.
2.  Cámbiate a la rama `desarrollo` (o créala si no existe):
    ```bash
    git checkout desarrollo
    # Si no existe: git checkout -b desarrollo
    ```
3.  **Para trabajar en una nueva feature**, crea tu rama SIEMPRE desde `desarrollo`:
    ```bash
    git checkout -b feature/mi-nueva-funcionalidad desarrollo
    ```

### 2. Configurar Entorno (El truco de la IP) 🪄

Para que la app en tu celular pueda hablar con el backend en tu PC, necesitamos configurar las IPs dinámicamente. ¡No lo hagas a mano! Tenemos un script para eso.

Ejecuta desde la raíz del proyecto:

```bash
chmod +x ./scripts/creacion_entorno.sh
./scripts/creacion_entorno.sh
```

**¿Qué hace este script?**
- Detecta si estás en **WSL** o **Linux nativo**.
- Busca tu IP local real (la de la red Wi-Fi/Ethernet).
- Genera automáticamente los archivos `.env` en `appVinculo/` y `backend/`.

### 3. Levantar el Proyecto 🐳

Para iniciar todo junto (Frontend, Backend y BD), usa nuestro script de arranque:

```bash
chmod +x ./scripts/reinicio.sh
./scripts/reinicio.sh
```

Este script:
1.  Baja cualquier contenedor viejo.
2.  Construye y levanta todo de nuevo.
3.  Te deja el log del **Frontend** en pantalla para que puedas escanear el código QR con tu celular.

---

## 📁 Estructura del Proyecto

- **`appVinculo/`**: Todo el código de React Native.
  - `src/`: Componentes modulares y estilos globales.
  - `app/`: Pantallas y rutas (Expo Router).
- **`backend/`**: API en python con FastAPI.
- **`scripts/`**: Utilidades para facilitarte la vida.
- **`docker-compose.yaml`**: La orquestación de servicios.

## ⚠️ Solución de Problemas Comunes

**"El puerto 5432 está ocupado"**
Probablemente tengas un Postgres local corriendo.
- Opción A: Detén tu Postgres local (`sudo service postgresql stop`).
- Opción B: Cambia el puerto en `docker-compose.yaml` (ej. `5433:5432`).

- Si cambias el puerto en el archivo .yaml, asegurate de regresar al puerto original antes de mandar tus cambios al repositorio.

**"No conecta el backend desde el celular"**
Asegúrate de que tu celular y tu PC estén en la misma red Wi-Fi y regenera los entornos con `./scripts/creacion_entorno.sh`.

---

¡A programar! 👨‍💻👩‍💻
