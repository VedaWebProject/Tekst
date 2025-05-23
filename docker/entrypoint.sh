#!/bin/sh -e

# run DB migration if arg #1 is "migrate"
if [[ "$1" == "migrate" ]]; then
    python3 -m tekst migrate
    exit $?
fi

# run bootstrapping routine first
python3 -m tekst bootstrap

# remove (all) trailing slashes from TEKST_WEB_PATH
TEKST_WEB_PATH=$(echo "$TEKST_WEB_PATH" | sed 's|/*$||')

# remove existing base tag from client's index.html, if any
# and inject base tag with base URL into client's index.html
sed -Ei /var/www/html/index.html -e 's|<base [^>]+>||' \
    -e 's|<head>|\0<base href="'"$TEKST_WEB_PATH/"'" />|'

# start caddy (will detach and run in background after startup)
caddy start --config /etc/caddy/Caddyfile

exec "$@"
