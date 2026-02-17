# Installation

## General requirements

The follwing requirements apply to either deployment strategy. Each deployment strategy then comes with its own respective additional requirements.

- A server to deploy Tekst to (the deployment instructions below assume a Linux-based server with Docker and Docker Compose installed, as this is the recommended setup strategy)
- A webserver configured to handle traffic between the outside world and Tekst **via HTTPS** (!)
- Access to a working, reliable **SMTP server** to send out emails containing verification links, password reset links, etc. It is important that this SMTP server is well-configured so the emails it sends actually reach their recepients. Whether you use a third-party SMTP server (like the one of your email provider) or your own self-hosted one is up to you. If you plan to run Tekst in [closed mode](configuration.md#tekst_security__closed_mode) (only one or more administrators, no public users who can create content), this requirement is **not strictly necessary**.


## Docker-based deployment (recommended)

As with every Docker-based deployment, the benefits of this approach are a reproducable deployment environment and an overall isolated setup. Also, a Docker-based deployment will save you from jumping through all the hoops of a bare-metal deployment of all the needed services and environments.

The instructions below will help you deploy a stack consisting of everything Tekst needs to run (one container for each part of the stack):

- Tekst itself – Tekst-API (the server part) and Tekst-Web (the client part) come as a single container image
- MongoDB
- Elasticsearch

!!! info "Requirements"

    As the prepared Docker-based setup handles the isolated installation of the services listed above, all you'll need is the following:

    - [Git](https://git-scm.com/)
    - [Docker](https://docs.docker.com/engine/install)
    - Docker Compose (If you're on Linux, the [Docker Compose Plugin](https://docs.docker.com/compose/install/linux/) for Docker is recommended. Otherwise there's [Compose](https://docs.docker.com/compose/install/other/) standalone, for which the commands below have to be run as `docker-compose ...` instead of `docker compose ...`)
    - `crontab` or something similar for scheduling recurring background jobs

!!! note
    All example commands on this page assume you're using a shell on a Unix-like operating system with Docker and Docker Compose installed.

1. Create a directory to store your Tekst deployment data in and enter it:

   ```sh
   mkdir my-tekst-instance && cd my-tekst-instance
   ```

2. Copy the compose file template from [here](https://raw.githubusercontent.com/VedaWebProject/Tekst/refs/heads/main/compose.yml) and save it as `compose.yml`:

    ```sh
    wget -O compose.yml https://raw.githubusercontent.com/VedaWebProject/Tekst/refs/heads/main/compose.yml
    ```

3. Configure Tekst's deployment:

    Copy the `.env.docker` template file from [here](https://raw.githubusercontent.com/VedaWebProject/Tekst/refs/heads/main/.env.docker) and name the copy `.env`. The template has some values preset for working with a deployment based on the project's `compose.yml`. See the [Configuration](configuration.md) page for guidance. The configuration defaults to sensible values wherever possible. There _are_ things you **have to configure** for Tekst to work, though.

    ```sh
    wget -O .env https://raw.githubusercontent.com/VedaWebProject/Tekst/refs/heads/main/.env.docker
    ```

4. Secure sensitive configuration values:

    Your `.env` file will contain some sensitive data, like the secret used for token generation or DB credentials. To better secure these values, let `root` own the `.env` file:

    ```sh
    sudo chown root:root .env
    ```

    ... and restrict all read/write acces to the owner/group of the file:

    ```sh
    sudo chmod ug=rw,o= .env
    ```

    (or `sudo chmod 660 .env` if you're into numbers)

    !!! warning

        After you finish deploying Tekst by following these instructions, please log into the initial admin account and **change its password immediately**.

5. Run Tekst 🚀

    Run the complete application stack via

    ```sh
    docker compose up -d
    ```

    Depending on the state of your data and the performance of your hardware, starting the Tekst stack might take a while. You can monitor the startup by looking at the logs of the Tekst container:

    ```sh
    docker compose logs -f tekst
    ```

    The application is now locally available at `127.0.0.1:8087`. If you wanted to change this port, you'd have to do so in the `compose.yml` and restart the stack. See the note below.

    !!! note
        The above command will detach the process of running the stack from your terminal and run it in the background (which is usually what you'd want in production). This is what the `-d` flag does. For checking the log output of the running stack, call `docker compose logs` from the same directory (the one containing the `compose.yml`). If you only want to see the log output of one of the services, just append the service's name from the `compose.yml` to the command, e.g. `docker compose logs tekst` (use `mongo` or `es` instead of `tekst` to see the logs of the MongoDB or Elasticsearch instances, respectively).

        Read the [Docker Compose documentation](https://docs.docker.com/engine/reference/commandline/compose/) to learn how to stop, start, reset (...) the application stack using Docker Compose.

6. Setup scheduled jobs

    Tekst needs to run some recurring background jobs to function propertly. Please continue with the instructions on [scheduled jobs](#scheduled-jobs)!


## Bare-metal deployment

Please be aware that taking this approach is **not recommended** as it is **considerably more difficult** and requires **much more manual maintenance** than deploying via Docker. The expertise needed to install and configure all these services will surely also suffice for extrapolating from the Docker-based setup a bit. For a big part, the process depends on the environment you want to deploy in.

!!! info
    Please see the general requirements at the top of this page and see the `compose.yml` file for the versions of the services used.

    You will also need:

    - NodeJS for building the client
    - Python >=3.12 for running the API
    - Gunicorn (or similar) as a WSGI with ASGI workers, typically from Uvicorn (see [here](https://www.uvicorn.org/deployment/))
    - `crontab` or something similar for scheduling recurring background jobs

The following steps are just a rough outline of the deployment process:

1. Install and configure the needed services
2. Configure Tekst following [the configuration overview](configuration.md).
3. Copy `Tekst-Web/.env.template` to `Tekst-Web/.env.production`
4. Adjust the values in the `Tekst-Web/.env.production` file
5. Build the client: `npm run build-only --base=./` (use `./` for a relative base path, `/` for root base path or `/foo` for, well, `/foo`)
6. Make your web server serve the built client files (in `Tekst-Web/dist`)
7. Copy `Tekst-API/.env.template` to `Tekst-API/.env`
8. Configure the server (Tekst-API) via `Tekst-API/.env` (see the [Configuration](configuration.md) page for guidance)
9. Install the Tekst-API project on your system as a Python module (see [here](https://pip.pypa.io/en/latest/topics/local-project-installs/#regular-installs))
10. Run the server (Tekst-API) via the WSGI you have installed, using ASGI workers
11. Configure your web server to reverse-proxy requests to the configured server URL + API path to the local port your WSGI server is serving the Tekst API on
12. Tekst needs to run some recurring background jobs to function propertly. Please read about this [below](#scheduled-jobs)!


## Scheduled jobs

It's a good idea to periodically update the search indices and the precomputed cache (daily is recommended). Also, the internal cleanup routine should be run from time to time. The most obvious way to do this is by using a [cron job](https://en.wikipedia.org/wiki/Cron).

The CLI Tekst-API offers as an interface for this are documented in the section about the [Tekst-API CLI](../administration/cli.md).
