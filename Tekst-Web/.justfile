# print list of available recipes
list:
  @just --list

# print web client version
version:
  @echo "Test-Web version: $(npx -c 'node -p "process.env.npm_package_version"')"

# install dependencies
install:
  npm install

# format code
format:
  npm run format

# lint code
lint:
  npm run lint

# format and lint code
fix:
  npm run format
  npm run lint

# run dev server
dev:
  -npm run start

# build distribution files
build: install
  npm run build

# generate TypeScript types from OpenAPI schema
types:
  npm run types

# generate translation assets
translations:
  npm run translations

# run full pre-commit toolchain
all:
  just fix
  npm run build

# visualize bundle
visualize:
  npx vite-bundle-visualizer
