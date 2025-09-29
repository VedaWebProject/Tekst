# Installation

## General requirements

The follwing requirements apply to either deployment strategy. Each deployment strategy then comes with its own respective additional requirements.

- A server to deploy Tekst to (the deployment instructions below assume a Linux-based server with Docker and Docker Compose installed, as this is the recommended setup strategy)
- A webserver configured to handle traffic between the outside world and Tekst **via HTTPS** (!)
- Access to a working, reliable **SMTP server** to send out emails containing verification links, password reset links, etc. It is important that this SMTP server is well-configured so the emails it sends actually reach their recepients. Whether you use a third-party SMTP server (like the one of your email provider) or your own self-hosted one is up to you. If you plan to run Tekst in [closed mode](configuration.md#tekst_security__closed_mode) (only one or more administrators, no public users who can create content), this requirement is **not strictly necessary**.


## Docker-based deployment (recommended)

As with every Docker-based deployment, the benefits of this approach are a reproducable deployment environment and an overall isolated setup. Also, a Docker-based deployment will save you from jumping through all the hoops of a bare-metal deployment of all the needed services and environments.

The instructions below will help you deploy a stack consisting of everything Tekst needs to run (one container for each part of the stack):

- A webserver (Caddy) serving the static client application (Tekst-Web) and routing API-requests to the server (Tekst-API)
- The Tekst server application (Tekst-API)
- MongoDB
- Elasticsearch

!!! warning "Requirements"

    As the prepared Docker-based setup handles the isolated installation of the services listed above, all you'll need is the following:

    - [Git](https://git-scm.com/)
    - [Docker](https://docs.docker.com/engine/install)
    - Docker Compose (If you're on Linux, the [Docker Compose Plugin](https://docs.docker.com/compose/install/linux/) for Docker is recommended. Otherwise there's [Compose](https://docs.docker.com/compose/install/other/) standalone, for which the commands below have to be run as `docker-compose ...` instead of `docker compose ...`)
    - `crontab` or something similar for scheduling recurring background jobs

!!! info
    All example commands on this page assume you're using a shell on a Unix-like operating system with Docker and Docker Compose installed.

1. Clone this repository and change into the resulting directory:

    ```sh
    git clone https://github.com/VedaWebProject/Tekst.git && cd Tekst
    ```

2. Configure Tekst's deployment:

    Copy the `.env.docker` template file and name the copy `.env`. The template has some values preset for working with a deployment based on the project's `compose.yml`. See the [Configuration](configuration.md) page for guidance. The configuration defaults to sensible values wherever possible. There _are_ things you **have to configure** for Tekst to work, though.

    ```sh
    cp .env.docker .env
    ```

3. Secure sensitive configuration values:

    Your `.env` file will contain some sensitive data, like the secret used for token generation or DB credentials. To better secure these values, let `root` own the `.env` file:

    ```sh
    sudo chown root:root .env
    ```

    ... and restrict all read/write acces to the owner/group of the file:

    ```sh
    sudo chmod ug=rw,o= .env
    ```

    (or `sudo chmod 660 .env` if you're into numbers)

    !!! warning "Very important!"

        After you finish deploying Tekst by following these instructions, please log into the initial admin account and **change its password immediately**.

4. Build the Tekst images:

    Build the docker images for the **Tekst-API** (server) and **Tekst-Web** (client) applications.

    ```sh
    docker compose build api web
    ```

    ... now grab a (small) coffee ☕

    !!! note

        Whenever you decide to change one of `TEKST_SERVER_URL`, `TEKST_API_PATH` or `TEKST_WEB_PATH` in your `.env` file, you'll have to build the image for **Tekst-Web** (client) again (using `docker compose build web --no-cache`), as these values are statically replaced in the client's code during the build process!

5. Run Tekst 🚀

    Run the complete application stack via

    ```sh
    docker compose up -d
    ```

    The container interfacing the host system and the application stack is now available locally at `127.0.0.1:8087`. If you wanted to change this port, you'd have to do so in the `compose.yml`.

    !!! note
        The above command will detach the process of running the stack from your terminal and run it in the background (which is usually what you'd want in production). This is what the `-d` flag does. For checking the log output of the running stack, call `docker compose logs` from the same directory (the one containing the `compose.yml`). If you only want to see the log output of one of the services, just append the service's name from the `compose.yml` to the command, e.g. `docker compose logs api`.

        Read the [Docker Compose documentation](https://docs.docker.com/engine/reference/commandline/compose/) to learn how to stop, start, reset (...) the application stack using Docker Compose.

6. Setup scheduled jobs

    Tekst needs to run some recurring background jobs to function propertly. Please read about this [below](#scheduled-jobs)!


## Bare-metal deployment

Please be aware that taking this approach is considerably more difficult and requires much more manual maintenance than deploying via Docker. The expertise needed to install and configure all these services will surely also suffice for extrapolating from the Docker-based setup a bit. For a big part, the process depends on the environment you want to deploy in.

!!! warning "Requirements"
    Please see the general requirements at the top of this page and see the `compose.yaml` file for the versions of the services used.

    You will also need:

    - NodeJS for building the client
    - Python >=3.12 for running the API
    - Gunicorn (or similar) as a WSGI with ASGI workers, typically from Uvicorn (see [here](https://www.uvicorn.org/deployment/))
    - `crontab` or something similar for scheduling recurring background jobs

The following steps are just a rough outline of the deployment process:

1. Install and configure the needed services
2. Configure Tekst following [the configuration overview](configuration.md).
3. Copy `Tekst-Web/.env` to `Tekst-Web/.env.production`
4. Configure the client (Tekst-Web) via the `Tekst-Web/.env.production` file
5. Build the client: `npm run build-only`
6. Make your web server serves the built client files (in `Tekst-Web/dist`) at the URL you configured in step 3
7. Copy `Tekst-API/.env` to `Tekst-API/.env.prod`
8. Configure the server (Tekst-API) via `Tekst-API/.env.prod`
9. Install the Tekst-API project on your system as a Python module (see [here](https://pip.pypa.io/en/latest/topics/local-project-installs/#regular-installs))
10. Run the server (Tekst-API) via the WSGI you have installed, using ASGI workers
11. Configure your web server to reverse-proxy requests to the configured server URL + API path to the local port your WSGI server is serving the Tekst API on
12. Tekst needs to run some recurring background jobs to function propertly. Please read about this [below](#scheduled-jobs)!


## Scheduled jobs

It's a good idea to periodically update the search indices and the precomputed cache (daily is recommended). Also, the internal cleanup routine should be run from time to time. The most obvious way to do this is by using a [cron job](https://en.wikipedia.org/wiki/Cron).

The commands Tekst offers as an interface for this are documented in the section about the [Tekst-API CLI](../administration/cli.md).
