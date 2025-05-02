#!/bin/sh

# run DB migration if arg #1 is "migrate"
if [ "$1" = "migrate" ]; then
    python3 -m tekst migrate
    exit $?
fi;

# run bootstrapping routine first
python3 -m tekst bootstrap
test $? -ne 0 && exit 1

# remove (all) trailing slashes from TEKST_WEB_PATH
TEKST_WEB_PATH=$(echo "$VALUE" | sed 's|/*$||')
# remove existing base tag from client's index.html, if any
sed -i 's|<base href=".*">||g' /var/www/html/index.html
# inject base tag with base URL into client's index.html
sed -i 's|<head>|<head><base href="'"$TEKST_WEB_PATH"'/" />|g' /var/www/html/index.html

# start caddy (will detach and run in background after startup)
caddy start --config /etc/caddy/Caddyfile

exec "$@"
