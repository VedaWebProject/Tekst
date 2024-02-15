# Installation


## General Requirements

The follwing requirements apply to either deployment strategy. Each deployment strategy then comes with its own respective additional requirements.

- A server to deploy Tekst to (the deployment instructions below assume a Linux-based server with Docker and Docker Compose installed, as this is the recommended setup strategy)
- A webserver configured to handle traffic between the outside world and Tekst **via HTTPS** (!)
- Access to a working, reliable **SMTP server** to send out emails containing verification links, password reset links, etc. It is important that this SMTP server is well-configured so the emails it sends actually reach their recepients. Whether you use a third-party SMTP server (like the one of your email provider) or your own self-hosted one is up to you. If you plan to run Tekst in [closed mode](../index.md#closed-mode) (only one or more administrators, no public users who can create content), this requirement is **not strictly necessary**.


## Initial Configuration

The following values can be configured in an `.env` file to match your deployment environment and needed features. Use the below list for guidance. The configuration defaults to values for a full-featured, Docker-based production environment served at `/` (root path). There *are* things you *have to* configure for them to work, though. By default, the application will later be available locally on port `8087` at `127.0.0.1`.


## Deploy via Docker (recommended)

As with every Docker-based deployment, the benefits of this approach are a reproducable deployment environment and an overall isolated setup. Also, a Docker-based deployment will save you from jumping through all the hoops of a bare-metal deployment of all the needed services and environments.

The instructions below will help you deploy a stack consisting of everything Tekst needs to run (one container for each part of the stack):

- A webserver (Caddy) serving the static client application (Tekst-Web) and routing API-requests to the server (Tekst-API)
- The Tekst server application (Tekst-API)
- MongoDB
- Elasticsearch

### Requirements
- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/engine/install)
- Docker Compose (If you're on Linux, the [docker-compose-plugin](https://docs.docker.com/compose/install/linux/) for Docker is recommended. Otherwise there's [Compose](https://docs.docker.com/compose/install/other/) standalone, for which the commands below have to be run as `docker-compose ...` instead of `docker compose ...`)

### Instructions

All example commands assume using a shell on a Unix-like operating system with Docker and Docker Compose installed.

#### Cloning the repository

Clone this repository and change into the resulting directory:

```sh
git clone https://github.com/VedaWebProject/Tekst.git && cd Tekst
```

#### Configuring Tekst's deployment

Copy the `.env.docker` file and name the copy `.env`:

```sh
cp .env.docker .env
```

See [Configuration](#initial-configuration) for details on initially configuring Tekst via the `.env` file.

#### Passing secrets to Tekst and its services

!!! danger "Attention!"

    Please follow this part very carefully and **pick [secure passwords](https://www.security.org/how-secure-is-my-password/)**!

You need one initial administrator account to manage your Tekst platform and activate further accounts. Also, the access credentials to some of the services need to be configured. In a Docker-based deployment, this is done via "secret files" that will be made available to the respective processes inside their containers.

The default location for these files (on your host system) is the `./secrets` folder inside the Tekst project directory. For now, this folder is empty, as the repository you just cloned ignores everything inside it (except a README file) for security reasons.

!!! info

    If you want to change the location of the secrets files, you'll have to adjust their paths in the `docker-compose.yaml` in the `secrets` section!

For each of the following secrets, create the respective secret files in your secrets folder and edit them to contain nothing but the secret value in question. The file names must exactly match the ones listed below.

| Secret | File name |
| --- | --- |
| Initial admin account email | `security_init_admin_email.txt` |
| Initial admin account password | `security_init_admin_password.txt` |
| Database username | `db_user.txt` |
| Database password | `db_password.txt` |

!!! info

    Please note that the initial admin password must contain at least 8 characters, including at least one lower-case letter, one upper-case letter and one digit!

Now you should now somehow protect these files from unauthorized access. You *could* delete them after running the stack (see next sections), but that would mean you'd have to *create them from scratch each time you have to restart the stack* (or your server, for that matter). So a more practical approach is to secure these files via your operating system's file system permissions.

Change ownership of the secrets files to `root` (assuming you are running this command from the parent directory of a `secrets` folder with the secret files you created):

```sh
sudo chown root:root secrets/*
```

Restrict all read/write acces to the owner of the files:

```sh
sudo chmod u=rw,go= secrets/*
```

(or `sudo chmod 600 secrets/*` if you're into numbers)

!!! danger "Very important!"

    After you finish deploying Tekst by following these instructions, please log into the initial admin account and **change its password immediately**. Also, you should delete the two secrets files containing the initial admin's credentials **in any case**, or Tekst will (try to) recreate the inital admin account on each restart!

#### Building the Tekst images

Build the docker images for the **Tekst-API** (server) and **Tekst-Web** (client) applications.

```sh
docker compose build server client
```

... now grab a (small) coffee ☕

!!! warning

    Whenever you decide to change one of `TEKST_WEB_PATH`, `TEKST_SERVER_URL` or `TEKST_API_PATH` in your `.env` file, you'll have to build the image for **Tekst-Web** (client) again (`docker compose build tekst-web`), as these values are statically replaced in the code during the build process!

#### Running Tekst 🚀

Run the complete application stack via

```sh
docker compose up
```

!!! info "Please note"

    The above command will keep your shell attached to the running process. To run the stack in the background (which is usually what you'd want in production), add the `-d` flag to the command above:

    ```sh
    docker compose up -d
    ```

    For checking the log output of the running stack, call this from the same directory (the one containing the `docker-compose.yml`):

    ```sh
    docker compose logs
    ```

Read [this](https://docs.docker.com/engine/reference/commandline/compose/) to learn how to stop, start, reset (...) the application stack using Docker Compose.


## Deploy directly on host system ("bare-metal")

Please be aware that taking this approach is considerably more difficult and requires much more manual maintenance than deploying via Docker. The expertise needed to install and configure all these services will surely also suffice for extrapolating from the Docker-based setup a bit. For a big part, the process depends on the environment you want to deploy in.

!!! info "About secrets/credentials"

    One thing to note for a bare-metal deployment is that without Docker, the values passed as secrets can also be directly set in the environment file and will be read and used by Tekst. That is, you don't *have to* use secret files. It may still be a good idea to use them, but you'll have to give the respective processes reading rights for those files while restricting access for anyone else.

### Requirements

Please see the general requirements at the top of this page and see the `docker-compose.yaml` for the versions of the services used.

You will also need:

- NodeJS for building the client
- Python >3.10 for running the server
- Gunicorn (or similar) as a WSGI with ASGI workers, typically from Uvicorn (see [here](https://www.uvicorn.org/deployment/))

### Instructions

The following steps are just a rough outline of the deployment process:

1. Install and configure the needed services
2. Copy `Tekst-Web/.env` to `Tekst-Web/.env.production`
3. Configure the client (Tekst-Web) via the `Tekst-Web/.env.production` file
4. Build the client: `npm run build-only`
5. Make your webserver serve the built client files (in `Tekst-Web/dist`) at the URL you configured in step 3
6. Copy `Tekst-API/.env` to `Tekst-API/.env.prod`
7. Configure the server (Tekst-API) via `Tekst-API/.env.prod`
8. Run the server (Tekst-API) via the WSGI you have installed, using ASGI workers
