FROM node:18.15-alpine AS builder

WORKDIR "/textrig"

COPY . .
RUN npm install && npm run build


FROM caddy:2.6-alpine AS prod

WORKDIR "/textrig"

COPY resources/Caddyfile /etc/caddy/
COPY --from=builder /textrig/dist/ ./
