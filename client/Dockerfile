# =========================
# VUE 3 + VITE DEV SERVER
# =========================
FROM node:20-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas arquivos de dependências para aproveitar cache
COPY package*.json ./

# Instala dependências (modo dev)
RUN npm install

# Expõe a porta padrão do Vite
EXPOSE 5173

# Comando padrão para iniciar o servidor de desenvolvimento
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
