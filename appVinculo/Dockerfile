# Usamos Node LTS
FROM node:20-slim

WORKDIR /app

# Instalamos git y otras herramientas necesarias para compilar módulos nativos
RUN apt-get update && apt-get install -y git python3 make g++ && rm -rf /var/lib/apt/lists/*
# -----------------------

# Copiamos los archivos de definición de paquetes
COPY package.json package-lock.json ./

# Instalamos dependencias
RUN npm install --legacy-peer-deps

# Instalamos globalmente expo-cli
RUN npm install -g expo-cli

RUN npm install -g @expo/ngrok

# Copiamos el código fuente
COPY . .

# Exponemos el puerto
EXPOSE 8081

# Iniciamos con túnel
CMD ["npx", "expo", "start", "--tunnel"]