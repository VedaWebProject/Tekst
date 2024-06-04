# Tekst Maintenance Utility Script

This Bash script simplifies performing common maintenance tasks (backup/restore database, recreate search index, ...).

## Usage

Run `./tekst-util --help` for an overview of the commands, flags and arguments. Each command has its own help that can be accessed via `./tekst-util <command> --help`.

## Development

This utility script has been created using [Bashly](https://bashly.dannyb.co/).
To easily run Bashly commands via the Bashly Docker image, just create this alias:

```sh
alias bashly='docker run --rm -it --user $(id -u):$(id -g) --volume "$PWD:/app" dannyben/bashly'
```

See the [Bashly documentation](https://bashly.dannyb.co/usage/getting-started/) for how to use this (it's not hard at all).
