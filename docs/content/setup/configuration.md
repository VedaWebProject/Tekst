# Configuration

| Variable | Description |
| --- | --- |
| `TEKST_SERVER_URL` | Full public URL of the server running the application (without sub path, port only if other than 80/443) (default: `http://127.0.0.1:8000`) |
| `TEKST_WEB_PATH` | Sub path of the web client (default: `/`) |
| `TEKST_API_PATH` | Sub path of the API (default: `/api`) |
| `TEKST_DEV_MODE` | Development mode – only use for development! (default: `false`) |
| `TEKST_LOG_LEVEL` | API log level (default: `warning`) |
| `TEKST_SETTINGS_CACHE_TTL` | Time-To-Live for the API settings cache (in seconds) (default: `60`) |
| `TEKST_TEMP_FILES_DIR` | Absolute path to local temporary directory to use (default: `/tmp/tekst_tmp`) |
| `TEKST_DB__PROTOCOL` | MongoDB protocol (default: `mongodb`) |
| `TEKST_DB__HOST` | MongoDB host (default: `127.0.0.1`) |
| `TEKST_DB__PORT` | MongoDB port (default: `27017`) |
| `TEKST_DB__USER` | MongoDB user (default: _none_) |
| `TEKST_DB__PASSWORD` | MongoDB password (default: _none_) |
| `TEKST_DB__NAME` | MongoDB database name (default: `tekst`) |
| `TEKST_ES__PROTOCOL` | Elasticsearch protocol (default: `http`) |
| `TEKST_ES__HOST` | Elasticsearch host (default: `127.0.0.1`) |
| `TEKST_ES__PORT` | Elasticsearch port (default: `9200`) |
| `TEKST_ES__PREFIX` | Elasticsearch prefix (for index, templates, etc.) (default: `tekst`) |
| `TEKST_ES__INIT_TIMEOUT_S` | Timeout for waiting for Elasticsearch service to be available on startup (default: `120`) |
| `TEKST_SECURITY__SECRET` | Secret to use for token generation (default: `must_change_this`) |
| `TEKST_SECURITY__CLOSED_MODE` | Whether to allow public registrations (default: `false`) |
| `TEKST_SECURITY__USERS_ACTIVE_BY_DEFAULT` | Whether new user accounts are active by default (otherwise have to be activated by admins) (default: `false`) |
| `TEKST_SECURITY__ENABLE_COOKIE_AUTH` | Enable cookie-based authentication (needed for the web client to work!) (default: `true`) |
| `TEKST_SECURITY__AUTH_COOKIE_NAME` | Cookie name (default: `tekstuserauth`) |
| `TEKST_SECURITY__AUTH_COOKIE_DOMAIN` | Cookie domain (default: _none_) |
| `TEKST_SECURITY__AUTH_COOKIE_LIFETIME` | Cookie lifetime in seconds (default: `43200`) |
| `TEKST_SECURITY__ACCESS_TOKEN_LIFETIME` | Lifetime of access token in DB (should match `TEKST_SECURITY__AUTH_COOKIE_LIFETIME`) (default: `43200`) |
| `TEKST_SECURITY__ENABLE_JWT_AUTH` | Enable JWT-based authentication (optional, useful for programmatic access to the API) (default: `false`) |
| `TEKST_SECURITY__AUTH_JWT_LIFETIME` | Lifetime of JWT used for authentication (default: `86400`) |
| `TEKST_SECURITY__RESET_PW_TOKEN_LIFETIME` | Lifetime of password reset tokens (default: `3600`) |
| `TEKST_SECURITY__VERIFICATION_TOKEN_LIFETIME` | Lifetime of account verification tokens (default: `86400`) |
| `TEKST_SECURITY__INIT_ADMIN_EMAIL` | Email address of initial admin account (default: _none_) |
| `TEKST_SECURITY__INIT_ADMIN_PASSWORD` | Password of initial admin account (default: _none_) |
| `TEKST_EMAIL__SMTP_SERVER` | SMTP server address (default: `127.0.0.1`) |
| `TEKST_EMAIL__SMTP_PORT` | SMTP server port (default: `25`) |
| `TEKST_EMAIL__SMTP_USER` | SMTP user (default: _none_) |
| `TEKST_EMAIL__SMTP_PASSWORD` | SMTP password (default: _none_) |
| `TEKST_EMAIL__SMTP_STARTTLS` | Whether to use StartTLS for SMTP connection (default: `true`) |
| `TEKST_EMAIL__FROM_ADDRESS` | From-address used for outgoing emails (default: `noreply@example-tekst-instance.org`) |
| `TEKST_DOC__OPENAPI_URL` | URL sub path (under `TEKST_API_PATH`) to public `openapi.json` API schema (if not set, disables SwaggerUI and Redoc) (default: `/openapi.json`) |
| `TEKST_DOC__SWAGGERUI_URL` | URL sub path (under `TEKST_API_PATH`) to SwaggerUI interactive API docs (default: `/docs`) |
| `TEKST_DOC__REDOC_URL` | URL sub path (under `TEKST_API_PATH`) to Redoc API docs (default: `/redoc`) |
| `TEKST_INFO__PLATFORM_NAME` | Initial platform name (default: `Tekst`) |
| `TEKST_INFO__SUBTITLE` | Initial platform subtitle (default: `An online text research platform`) |
| `TEKST_INFO__TERMS` | URL to API usage terms (default: _none_) |
| `TEKST_INFO__CONTACT_NAME` | API contact name (default: `Tekst Administrator`) |
| `TEKST_INFO__CONTACT_EMAIL` | API contact email (default: `noreply@tekst-contact-email-not-set.com`) |
| `TEKST_INFO__CONTACT_URL` | API contact URL (default: _none_) |
| `TEKST_CORS__ALLOW_ORIGINS` | CORS allow origins (default: `*`) |
| `TEKST_CORS__ALLOW_CREDENTIALS` | CORS allow credentials (default: `true`) |
| `TEKST_CORS__ALLOW_METHODS` | CORS allow methods (default: `*`) |
| `TEKST_CORS__ALLOW_HEADERS` | CORS allow headers (default: `*`) |
| `TEKST_MISC__USRMSG_FORCE_DELETE_AFTER_DAYS` | Delete old user messages after n days (default: `365`) |
| `TEKST_MISC__MAX_RESOURCES_PER_USER` | Maximum number of resources/versions that one user is allowed to own (default: `10`) |
