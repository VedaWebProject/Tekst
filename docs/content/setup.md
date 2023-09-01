# Setup


## General Requirements

The follwing requirements apply to either deployment strategy. Each deployment strategy then comes with its own respective additional requirements.

- A server to deploy Tekst to (the deployment instructions below assume a Linux-based server with Docker and Docker Compose installed, as this is the recommended setup strategy)
- A webserver configured to handle traffic between the outside world and Tekst **via HTTPS** (!)
- Access to a working, reliable **SMTP server** to send out emails containing verification links, password reset links, etc. It is important that this SMTP server is well-configured so the emails it sends actually reach their recepients. Whether you use a third-party SMTP server (like the one of your email provider) or your own self-hosted one is up to you. If you plan to run Tekst in [closed mode](index.md#closed-mode) (only one or more administrators, no public users who can create content), this requirement is **not strictly necessary**.


## Setup Configuration

The following values can be configured in an `.env` file to match your deployment environment and needed features. Use the below list for guidance. The configuration defaults to values for a full-featured, Docker-based production environment served at `/` (root path). There *are* things you *have to* configure for them to work, though. By default, the application will later be available locally on port `8087` at `127.0.0.1`.


## Deployment via Docker (recommended)

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

See [Configuration](#configuration) for details on initially configuring Tekst via the `.env` file.

#### Passing secrets to Tekst and its services

!!! danger "Attention!"

    Please follow this part very carefully and **pick [secure passwords](https://www.security.org/how-secure-is-my-password/)**!

You need one initial administrator account to manage your Tekst platform and activate further accounts. Also, the access credentials to some of the services need to be configured. This is done via "secret files" that will be made available to the respective processes inside their containers.

The default location for these files (on your host system) is the `./secrets` folder inside the Tekst project directory. For now, this folder is empty, as the repository you just cloned ignores everything inside it (except a README file) for security reasons.

!!! info

    If you want to change the location of the secrets files, you'll have to adjust their paths in the `docker-compose.yaml` in the `secrets` section!

For each of the following secrets, create the respective secret files in your secrets folder and edit them to contain nothing but the secret value in question. The file names must exactly match the ones listed below.

| Secret | File name | Note |
| --- | --- | --- |
| Initial admin account email | `init_admin_email.txt` |  |
| Initial admin account password | `init_admin_password.txt` | Min. 8 characters, must contain `a-z`, `A-Z`, `0-9` |

You should now somehow protect these files from unauthorized access. You *could* delete them after running the stack (see next sections), but that would mean you'd have to *create them from scratch each time you have to restart the stack* (or your server, for that matter). So a more practical approach is to secure these files via your operating system's file system permissions.

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

    After you finish deploying Tekst by going through these instructions, please log into the initial admin account and **change its password immediately**. Also, you should delete the two secrets files containing the initial admin's credentials **in any case**, or Tekst will (try to) recreate the inital admin account on each restart!

#### Building the Tekst images

Build the docker images for the **Tekst-API** (server) and **Tekst-Web** (client) applications.

```sh
docker compose build tekst-api tekst-web
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


## Deployment on host system ("bare-metal")

> 🏗 TODO: As this will be mostly a list of links to the documentations of the needed services etc., there's not much to expect from this part of the deployment documentation.
