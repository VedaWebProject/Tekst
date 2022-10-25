#!/bin/sh

set -e

. /textrig/.venv/bin/activate

# misc setup logic...

# passed command...
exec gunicorn "$@"
