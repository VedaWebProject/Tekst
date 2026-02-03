#!/usr/bin/env bash

if [ "$1" != "major" -a "$1" != "minor" -a "$1" != "patch" ]; then
    echo "First and only argument must be one of: major, minor, patch."
    exit 1
fi

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# bump client version first
cd "$script_dir/../Tekst-Web"
npm version "pre$1" --git-tag-version false --preid alpha # TODO: remove after pre-stable phase: "pre..." and --preid

# remember new client version
new_version=$(npx -c 'node -p "process.env.npm_package_version"')

# bump API version to same version as client
cd "$script_dir/../Tekst-API"
uv version $new_version # uv understands the different format and handles it <3

# install new API version
uv sync

# create updated API schema
TEKST_DEV_MODE=true TEKST_LOG_LEVEL=warning uv run python3 -m tekst schema -f

# install client (also recreates types from new API schema)
cd "$script_dir/../Tekst-Web"
npm install
