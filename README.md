<img width="72" height="72" align="right" style="position: absolute;  top: 0; right: 0; padding: 12px;" src="resources/logo.png" alt="Tekst logo"/>

# Tekst <!-- omit in toc -->

Tekst is a collaborative, web-based research platform for displaying, linking, exploring, and enriching resources on natural language texts. It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project on Old Indic texts, where it constitutes the technical basis of the research platform "VedaWeb", which will be launched in its new form as part of the project's efforts.

This is the "main" Tekst repository. While destinct parts of the application code have their own respective repositories (namely the server and client application projects), this very repository is meant as the go-to place for general information, documentation and the resources needed to deploy an instance of the Tekst platform for yourself.

If, however, you want to visit or even contribute to the Tekst code repositories, here's where to look first:

- [**tekst-server**](https://github.com/VedaWebProject/tekst-server) - Codebase of the **Tekst** *server* application.
- [**tekst-client**](https://github.com/VedaWebProject/tekst-client) - Codebase of the **Tekst** *client* application.


## Contents  <!-- omit in toc -->

- [State of development](#state-of-development)
- [Deployment](#deployment)
  - [Docker (recommended)](#docker-recommended)


## State of development

Development on this software is in an early conceptual phase. At this point, there is no usable release or public instance.


## Deployment

### Docker (recommended)
To deploy Tekst with Docker, follow these steps (example commands assume using some kind of loosely POSIX compliant shell):

1. Requirements:
   - [Git](https://git-scm.com/)
   - [Docker](https://docs.docker.com/engine/install), including the [docker-compose-plugin](https://docs.docker.com/compose/install/linux/) (recommended) or [Compose](https://docs.docker.com/compose/install/other/) standalone

2. Clone this repository and change into the resulting directory:

    ```sh
    git clone https://github.com/VedaWebProject/tekst.git
    cd tekst
    ```

3. Download the `.env` files from [the server repository](https://raw.githubusercontent.com/VedaWebProject/tekst-server/main/.env) as well as [the client repository](https://raw.githubusercontent.com/VedaWebProject/tekst-client/main/.env) and name them `.env.server` and `.env.client`, respectively:

    ```sh
    wget https://raw.githubusercontent.com/VedaWebProject/tekst-server/main/.env
    mv .env .env.server
    wget https://raw.githubusercontent.com/VedaWebProject/tekst-client/main/.env
    mv .env .env.client
    ```

4. Configure the values in `.env.server` and `.env.client` to match your deployment environment and needed features. Use the comments in those files for guidance. If you leave everything unchanged, Tekst will run with sensible defaults for a full-featured, Docker-based production environment served at `/` (root path). The application will be available via the local port `8008` of address `127.0.0.1`.

5. Build the docker images for the server and client applications (for the client, you'll have to repeat this whenever you change the value of `TEKST_CLIENT_PATH` in `.env.client`!):

    ```sh
    docker compose --env-file .env.client build tekst-client tekst-server
    ```

    (...this may take a while!)

6. Run the complete stack with:

    ```sh
    docker compose up
    ```

    Add the `-d` flag to run it in detached mode (in the background).

7. Read [this](https://docs.docker.com/engine/reference/commandline/compose/) to learn how to stop, start, reset (...) the application stack with Docker Compose.
