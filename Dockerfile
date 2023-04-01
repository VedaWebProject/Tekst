FROM node:18.15-alpine AS builder
WORKDIR "/app"
COPY . .
RUN npm install && npm run build

FROM caddy:2.6-alpine AS prod
WORKDIR "/app"
COPY --from=builder /app/dist/ ./
COPY ./resources/Caddyfile /etc/caddy/
