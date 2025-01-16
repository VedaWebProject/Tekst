#!/bin/sh
python3 -m tekst setup
test $? -ne 0 && exit 1
exec gunicorn tekst.app:app --config /etc/gunicorn/gunicorn_conf.py "$@"
