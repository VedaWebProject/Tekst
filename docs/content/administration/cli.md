# CLI

The Tekst-API offers a simple CLI, e.g. for bootstrapping the API before startup, triggering certain maintenance routines or migrating the database after an upgrade of Tekst.

!!! warning "Important"
    If the Tekst-API is running in a container, the commands below have to be **prefixed** with...

    ```sh
    docker exec -i $container
    ```

    ...where `$container` is the name of the container!

To get an overview of the available commands and their arguments, you can also run `python -m tekst --help`.


## `bootstrap`

This command **has to be run each time before starting up the Tekst-API**. It makes sure the data in the database is compatible with the Tekst version used (and runs automatic migrations if needed and [configured](../setup/configuration.md)), inserts demo data into the database if it is empty (on first start), creates the initial admin user (if no users exist yet), generates precomputed data (cache) and updates the search indices (if necessary).

All this can only be done by _a single process_ and should not happen concurrently. This is why it has to happen before the API startup, which is usually powered by multiple workers acting asynchronously.

```sh
python -m tekst bootstrap
```


## `index`

(Re)creates/updates all search indices if they are out of date.

```sh
python -m tekst index
```

!!! tip
    The `index` command is included in the things the `maintenance` command does (see below!).


## `precompute`

Tekst uses a precomputed cache holding data that is expensive to generate but essential for the application to work. This command triggers the update/creation of the precomputed cache.

```sh
python -m tekst precompute
```

!!! tip
    The `precompute` command is included in the things the `maintenance` command does (see below!).


## `cleanup`

Triggers the internal cleanup routine of the Tekst-API. It deletes stale user messages and outdated access tokens.

```sh
python -m tekst cleanup
```

!!! tip
    The `cleanup` command is included in the things the `maintenance` command does (see below!).


## `maintenance`

A single command that runs `index`, `precompute` and `cleanup` sequentially. Very handy to be scheduled as a recurring (e.g. nightly) job.

```sh
python -m tekst maintenance
```


## `migrate`

Checks the data in the database for compatibility with the currently used version of Tekst and runs database migrations if necessary. This has to be used after an [upgrade of Tekst](./upgrades.md) if [`TEKST_AUTO_MIGRATE=false`](../setup/configuration.md).

```sh
python -m tekst migrate

# Or use the --yes flag to suppress asking for confirmation:
# python -m tekst migrate --yes
```


## `schema`

Generates a JSON file with the [OpenAPI schema](https://spec.openapis.org/oas/latest.html) of the Tekst-API.

```sh
python -m tekst schema
```

This command takes several arguments for customizing its behavior:

```
Usage: python -m tekst schema [OPTIONS]

  Exports Tekst's OpenAPI schema to a JSON file

  Important: The active Tekst environment variables might influence the
  schema!

Options:
  -f, --to-file           Output to file defined by --output-file instead of
                          stdout
  -o, --output-file TEXT  Output file path to write to if --to-file flag is
                          set  [default: openapi.json]
  -i, --indent INTEGER    Indent output by n whitespace characters (0 for no
                          indentation)  [default: 2]
  -s, --sort-keys         Sort keys in output JSON
  -q, --quiet             Don't output anything (only effective if --to-file
                          flag is not set)
  --help                  Show this message and exit.
```
