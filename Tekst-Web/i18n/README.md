# Internationalization

## Help translations (`help/`)

- Each subdirectory is named with a short language code (e.g. `enUS`, `deDE`, ...)
- The files within each directory are Markdown files (`.md`) containing the language-specific help text for the respective topic.
- Each Markdown file is named using the help text key also used in the source code as a `help-key` attribute value for help button elements **and** a one-letter marker that specifies the user role needed to access the help text (`v` for visitor, `u` for user, `s` for superuser). The format for the filename is `<help-key>.<role>.md`, e.g. `browseView.v.md` for the visitor help text for the "About" topic.

## UI translations (`ui/`)

- This directory contains one `.yml` file for each supported language, named using the short language code (e.g. `enUS.yml`, `deDE.yml`, ...).
- The `.yml` files contain the language-specific translations for the UI elements' labels, alerts, dialogs and so on.
