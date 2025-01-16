#!/usr/bin/env bash

cd $( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Documentation will be served on http://127.0.0.1:8091"

docker run \
    --rm \
    -p 127.0.0.1:8091:8000 \
    -v ${PWD}/../docs:/docs:ro \
    squidfunk/mkdocs-material:9
