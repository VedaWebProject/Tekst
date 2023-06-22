# Setup

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


## Configuration

The following values can be configured in an `.env` file to match your deployment environment and needed features. Use the below list for guidance. The configuration defaults to values for a full-featured, Docker-based production environment served at `/` (root path). There *are* things you *have to* configure for them to work, though. By default, the application will later be available locally on port `8087` at `127.0.0.1`.


## Deployment

### General Requirements

The follwing requirements apply to either deployment strategy. Each deployment strategy then comes with its own respective additional requirements.

- Access to a working, reliable **SMTP server** to send out emails containing verification links, password reset links, etc. It is important that this SMTP server is well-configured so the emails it sends actually reach their recepients. Whether you use a third-party SMTP server (like the one of your email provider) or your own self-hosted one is up to you. If you plan to run Tekst in [closed mode](index.md#closed-mode) (only one or more administrators, no public users who can create content), this requirement is **not strictly necessary**.

### Docker (recommended)

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
