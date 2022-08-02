#!/bin/sh

set -e

. /opt/pysetup/.venv/bin/activate

# misc setup logic...

# passed command...
exec gunicorn "$@"