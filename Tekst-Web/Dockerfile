# =======
# BUILDER
# =======

FROM node:22.12.0-alpine3.20 AS builder

ARG WEB_PATH
ARG SERVER_URL
ARG API_PATH
ENV TEKST_SERVER_URL=$SERVER_URL \
    TEKST_API_PATH=$API_PATH

WORKDIR /app
COPY . .
RUN npm install && npm run build-only --base=$WEB_PATH


# =================
# PROD CLIENT IMAGE
# =================

FROM caddy:2.9-alpine AS prod

ARG API_PATH
ENV TEKST_API_PATH=$API_PATH

WORKDIR /var/www/html
COPY --from=builder /app/dist/ ./
COPY ./deploy/Caddyfile /etc/caddy/

VOLUME /var/www/tekst/static

# 82:82 is alpine default for www-data
RUN set -x && adduser -u 82 -D -S -G www-data www-data
USER www-data

EXPOSE 80
