FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && apk add --no-cache curl
COPY src/ ./src/
EXPOSE 3001
USER node
CMD ["node", "src/server.js"]
