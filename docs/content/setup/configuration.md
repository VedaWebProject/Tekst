# Configuration

The following table lists all the configuration values that can be set as environment variables (e.g. via a `.env` file).

!!! warning "Important"
    - Any changes to the configuration values listed below require an application restart to take effect.
    - Some variable names contain _double_ underscores (`__`) to reflect the nested internal configuration – be careful not to miss those in case you're into typing things by hand!


## Core Config

Basic configuration, URL, paths, ...

### `TEKST_SERVER_URL`
Full public URL of the server running the application (without sub path, port only if other than 80/443) (String – default: `http://127.0.0.1:8000`)

### `TEKST_API_PATH`
Public sub path of the API. This **must** be set independently from `TEKST_WEB_PATH`, so if `TEKST_WEB_PATH` is `/foo`, `TEKST_API_PATH` must include the web path, like `/foo/api`. (String – default: `/api`)

!!! warning "Important"
    The official docker image **assumes an API path ending with `/api`**, so either **do not** set `TEKST_API_PATH` at all (if you deploy Tekst under `/`) to let it default to `/api`, or set an API path that is a combination of `TEKST_WEB_PATH` and the path suffix `/api`, e.g. `/foo/api`!

### `TEKST_WEB_PATH`
Public path of the web client (String – default: `/`)

### `TEKST_BEHIND_REVERSE_PROXY`
If the API runs behind a reverse proxy (e.g. if using the the project's `compose.yml`), set this to `true` and make sure the reverse proxy is properly setting (or appending to) the [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) header on the passed requests. This is to make sure the API is able to **try to** prevent accidentally flooding the workers with long-running background jobs. (Boolean – default: `false`)

### `TEKST_WEB_STATIC_DIR`
Local path to static web files directory (String – default: `/var/www/tekst/static/`)

### `TEKST_DEV_MODE`
Development mode – only use for development! (Boolean – default: `false`)

### `TEKST_LOG_LEVEL`
API log level (`DEBUG` | `INFO` | `WARNING` | `ERROR` | `CRITICAL` – default: `WARNING`)

### `TEKST_AUTO_MIGRATE`
If `false` (default) and there are pending DB migrations that should be run, the bootstrap routine will fail with a critical log message (as the API itself will always do). If `true`, pending migrations will be run as part of the bootstrap routine. (Boolean – default: `false`)

### `TEKST_XSRF`
Enables/disables [XSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery) protection enforced by the API. (Boolean – default: `true`)

### `TEKST_TEMP_FILES_DIR`
Absolute path to local temporary directory to use (String – default: `/tmp/tekst_tmp`)



## Database (MongoDB)

Configuration for the MongoDB connection

### `TEKST_DB__PROTOCOL`
MongoDB protocol (String – default: `mongodb`)

### `TEKST_DB__HOST`
MongoDB host (String – default: `127.0.0.1`)

### `TEKST_DB__PORT`
MongoDB port (Integer – default: `27017`)

### `TEKST_DB__USER`
MongoDB user (String – default: _none_)

### `TEKST_DB__PASSWORD`
MongoDB password (String – default: _none_)

### `TEKST_DB__NAME`
MongoDB database name (String – default: `tekst`)



## Search Server (Elasticsearch)

Configuration for the connection to the Elasticsearch server

### `TEKST_ES__PROTOCOL`
Elasticsearch protocol (String – default: `http`)

### `TEKST_ES__HOST`
Elasticsearch host (String – default: `127.0.0.1`)

### `TEKST_ES__PORT`
Elasticsearch port (Integer – default: `9200`)

### `TEKST_ES__PREFIX`
Elasticsearch prefix (for index, templates, etc.) (String – default: `tekst`)

### `TEKST_ES__TIMEOUT_INIT_S`
Timeout for waiting for Elasticsearch service to be available on startup, in seconds (Integer – default: `240`)

### `TEKST_ES__TIMEOUT_GENERAL_S`
General client timeout for requests to Elasticsearch, in seconds (Integer – default: `30`)

### `TEKST_ES__TIMEOUT_SEARCH_S`
Timeout for search reqests to Elasticsearch, in seconds (Integer – default: `30`)



## Security

All the configuration related to app-level security

### `TEKST_SECURITY__SECRET`
Secret to use for token generation (String – default: `must_change_this`)

### `TEKST_SECURITY__CLOSED_MODE`
Whether to allow public registrations (Boolean – default: `false`)

### `TEKST_SECURITY__USERS_ACTIVE_BY_DEFAULT`
Whether new user accounts are active by default (otherwise have to be activated by admins) (Boolean – default: `false`)

### `TEKST_SECURITY__ENABLE_COOKIE_AUTH`
Enable cookie-based authentication (needed for the web client to work!) (Boolean – default: `true`)

### `TEKST_SECURITY__AUTH_COOKIE_NAME`
Cookie name (String – default: `tekstuserauth`)

### `TEKST_SECURITY__AUTH_COOKIE_DOMAIN`
Cookie domain (String – default: _none_)

### `TEKST_SECURITY__AUTH_COOKIE_LIFETIME`
Cookie lifetime in seconds – `0` produces session cookies (Integer – default: `43200`)

### `TEKST_SECURITY__ACCESS_TOKEN_LIFETIME`
Lifetime of access tokens in seconds; limits validity of cookies and must thus be greater than or equal to `TEKST_SECURITY__AUTH_COOKIE_LIFETIME` (Integer – default: `43200`, min.: `3600`)

### `TEKST_SECURITY__ENABLE_JWT_AUTH`
Enable JWT-based authentication (optional, useful for programmatic access to the API) (Boolean – default: `false`)

### `TEKST_SECURITY__AUTH_JWT_LIFETIME`
Lifetime of JWT used for authentication (Integer – default: `86400`)

### `TEKST_SECURITY__RESET_PW_TOKEN_LIFETIME`
Lifetime of password reset tokens (Integer – default: `3600`)

### `TEKST_SECURITY__VERIFICATION_TOKEN_LIFETIME`
Lifetime of account verification tokens (Integer – default: `86400`)

### `TEKST_SECURITY__INIT_ADMIN_EMAIL`
Email address of initial admin account (String – default: _none_)

### `TEKST_SECURITY__INIT_ADMIN_PASSWORD`
Password of initial admin account (String – default: _none_)



## Email

Configuration for the SMTP connection and sender address of outgoing emails

### `TEKST_EMAIL__SMTP_SERVER`
SMTP server address (String – default: `127.0.0.1`)

### `TEKST_EMAIL__SMTP_PORT`
SMTP server port (Integer – default: `25`)

### `TEKST_EMAIL__SMTP_USER`
SMTP user (String – default: _none_)

### `TEKST_EMAIL__SMTP_PASSWORD`
SMTP password (String – default: _none_)

### `TEKST_EMAIL__SMTP_STARTTLS`
Whether to use StartTLS for SMTP connection (Boolean – default: `true`)

### `TEKST_EMAIL__FROM_ADDRESS`
From-address used for outgoing emails (String – default: `noreply@example-tekst-instance.org`)



## Documentation

Configuration for the OpenAPI schema URL and API documentation via SwaggerUI and/or Redoc

### `TEKST_API__OPENAPI_URL`
URL sub path (under `TEKST_API_PATH`) to public `openapi.json` API schema (if not set, disables SwaggerUI and Redoc) (String – default: `/openapi.json`)

### `TEKST_API__SWAGGERUI_URL`
URL sub path (under `TEKST_API_PATH`) to SwaggerUI interactive API docs; empty value disables SwaggerUI (String – default: `/docs`)

### `TEKST_API__REDOC_URL`
URL sub path (under `TEKST_API_PATH`) to Redoc API docs; empty value disables Redoc (String – default: `/redoc`)

### `TEKST_API__TITLE`
Platform API title (String – default: `Tekst`)

### `TEKST_API__SUMMARY`
Platform API summary (String – default: _none_)

### `TEKST_API__DESCRIPTION`
Platform API description (String – default: _none_)

### `TEKST_API__TERMS_URL`
URL to API usage terms (String – default: _none_)

### `TEKST_API__CONTACT_NAME`
API contact name (String – default: _none_)

### `TEKST_API__CONTACT_EMAIL`
API contact email (String – default: _none_)

### `TEKST_API__CONTACT_URL`
API contact URL (String – default: _none_)

### `TEKST_API__LICENSE_NAME`
API license name; if not set, no license info will be integrated in API docs (String – default: _none_)

### `TEKST_API__LICENSE_ID`
API license ID (canonical short form of name) (String – default: _none_)

### `TEKST_API__LICENSE_URL`
API license URL (String – default: _none_)



## Cross-Origin Resource Sharing (CORS)

You _should_ handle CORS via your webserver configuration. But if for some reason you nead app-level CORS management, this is where to look.

### `TEKST_CORS__ENABLE`
Enable CORS header control; only enable this if you don't have a web server / reverse proxy that already handles it! (Boolean – default: `false`)

### `TEKST_CORS__ALLOW_ORIGINS`
CORS allow origins (Comma-separated list as string – default: `*`)

### `TEKST_CORS__ALLOW_CREDENTIALS`
CORS allow credentials (Boolean – default: `true`)

### `TEKST_CORS__ALLOW_METHODS`
CORS allow methods (Comma-separated list as string – default: `*`)

### `TEKST_CORS__ALLOW_HEADERS`
CORS allow headers (Comma-separated list as string – default: `*`)



## What is left

All these configuration values – and then some...

### `TEKST_MISC__USRMSG_FORCE_DELETE_AFTER_DAYS`
Delete old user messages after n days (Integer – default: `365`)

### `TEKST_MISC__MAX_RESOURCES_PER_USER`
Maximum number of resources/versions that one user is allowed to own (Integer – default: `10`)

### `TEKST_MISC__DEL_EXPORTS_AFTER_MINUTES`
Time in minutes after whichfinished/failed tasks that produce a downloadable file artifact (namely "exports") will be deleted automatically, including the respective file (Integer – default: `5`)
