#!/bin/sh

# run DB migration if arg #1 is "migrate"
if [ "$1" = "migrate" ]; then
    python3 -m tekst migrate
    exit $?
fi;

# run bootstrapping routine first
python3 -m tekst bootstrap
test $? -ne 0 && exit 1

# run Gunicorn WSGI server to serve the application
exec gunicorn tekst.app:app --config /etc/gunicorn/gunicorn_conf.py "$@"
