#!/bin/sh
python3 -m tekst setup && \
exec gunicorn tekst.app:app --config gunicorn_conf.py "$@" || \
exit 1
