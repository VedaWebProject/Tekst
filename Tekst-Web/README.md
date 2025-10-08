# Tekst Web

[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?logo=vuedotjs&logoColor=fff)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=fff)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=fff)](https://vite.dev/)

This project holds the codebase for the **client** part of the Tekst platform.
For general information on Tekst, visit the [Tekst repository](https://github.com/VedaWebProject/tekst).

## Development

1. Clone this repository via `git clone https://github.com/VedaWebProject/Tekst-Web.git`
2. Install the project and its dependencies (from project directory): `npm install`
3. You can now use
   - `npm run dev` to run the [Vite](https://vitejs.dev/) dev server
   - `npm run build` to build the project
   - `npm run api-schema` to generate types from the Tekst-API OpenAPI schema
   - `npm run translations` to generate translation modules from the translation files
   - [...and so on](package.json)
4. The project has some _very_ convenient tasks configured that can be run with [Task](https://taskfile.dev/) (a task runner). This is optional, but it helps _a lot_. You can install it form [here](https://taskfile.dev/installation/). Tasks can then be run via `task <taskname>`. You'll get a commented overview of the configured tasks if you run `task` without any arguments (or look [here](Taskfile.yml)).
