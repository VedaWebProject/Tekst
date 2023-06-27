# Setup


## General Requirements

The follwing requirements apply to either deployment strategy. Each deployment strategy then comes with its own respective additional requirements.

- A server to deploy Tekst to (the deployment instructions below assume a Linux-based server with Docker and Docker Compose installed, as this is the recommended setup strategy)
- Access to a working, reliable **SMTP server** to send out emails containing verification links, password reset links, etc. It is important that this SMTP server is well-configured so the emails it sends actually reach their recepients. Whether you use a third-party SMTP server (like the one of your email provider) or your own self-hosted one is up to you. If you plan to run Tekst in [closed mode](index.md#closed-mode) (only one or more administrators, no public users who can create content), this requirement is **not strictly necessary**.


## Configuration

The following values can be configured in an `.env` file to match your deployment environment and needed features. Use the below list for guidance. The configuration defaults to values for a full-featured, Docker-based production environment served at `/` (root path). There *are* things you *have to* configure for them to work, though. By default, the application will later be available locally on port `8087` at `127.0.0.1`.


## Deployment

### Using Docker (recommended)

As with every Docker-based deployment, the benefits of this approach are a reproducable deployment environment and an overall isolated setup.

#### Requirements
- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/engine/install)
- preferably also Docker Compose (If you're on Linux, the [docker-compose-plugin](https://docs.docker.com/compose/install/linux/) for Docker is recommended. Otherwise there's [Compose](https://docs.docker.com/compose/install/other/) standalone, for which the commands below have to be run as `docker-compose ...` instead of `docker compose ...`)

#### Instructions

All example commands assume using a shell on a Unix-like operating system with Docker and Docker Compose installed.

Clone this repository and change into the resulting directory:

```sh
git clone https://github.com/VedaWebProject/Tekst.git && cd Tekst
```

Copy the `.env.docker` file and name the copy `.env`:

```sh
cp .env.docker .env
```

See [Configuration](#configuration) for details on initially configuring Tekst via this `.env` file.

!!! danger "Attention!"

    You need one initial administrator account to manage your Tekst platform.
    Please read [Initial Admin Account](#initial-admin-account) to learn how to set it up!

Build the docker images for the **Tekst-API** (server) and **Tekst-Web** (client) applications. **Important:** Whenever you decide to change one of `TEKST_WEB_PATH`, `TEKST_SERVER_URL` or `TEKST_API_PATH` in your `.env` file, you'll have to build the image for **Tekst-Web** (client) again, as these values are statically replaced in the code during the build process!

```sh
docker compose build tekst-api tekst-web
```

... now grab a (small) coffee ☕

Run the complete application stack:

```sh
docker compose up
```

Add the `-d` flag to run it in detached mode (in the background).

Read [this](https://docs.docker.com/engine/reference/commandline/compose/) to learn how to stop, start, reset (...) the application stack using Docker Compose.


### On host system

#### Requirements
> 🏗 TODO


#### Instructions
> 🏗 TODO


## Initial Admin Account

To configure an initial admin account, follow these steps:

1. In your `.env` file, set `TEKST_SECURITY__INIT_ADMIN_EMAIL` (admin account initial email address) and `TEKST_SECURITY__INIT_ADMIN_PASSWORD` (admin account initial password). The Password **must** have at least 8 characters and **must** container at least one of each:
    - lowercase letters
    - UPPERCASE LETTERS
    - digits 0-9
2. Follow the setup instructions depending on the deployment strategy you chose above.
3. When setup is finished and everything is working, **immediately log in with your initial administrator account and change its password!**

Alternatively, and this is for advanced users, you can leave the two values blank in `.env` and just register a new user via the Webclient as normal. You then have to log into the database modify the documents for this initial account to be activated, verified and a superuser (admin).
