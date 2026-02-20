# Internationalization

## Help translations (`help/`)

- Each subdirectory is named with a short language code (e.g. `enUS`, `deDE`, ...)
- The files within each directory are Markdown files (`.md`) containing the language-specific help text for the respective topic.
- Each Markdown file is named using the help text key also used in the source code as a `help-key` attribute value for help button elements **and** a one-letter marker that specifies the minimum user role needed to access the help text (`v` for visitor, `u` for user, `s` for superuser). This is solely for the purpose of showing only relevant help texts to the user in the help overview. Acessing the help text directly via the little help buttons would always work, regardless of the user's role, but users won't see help buttons not meant for their role in the first place.
- The format for the filename is `<help-key>.<role>.md`, e.g. `browseView.v.md` for the visitor help text for the "About" topic.

## UI translations (`ui/`)

- This directory contains one `.yml` file for each supported language, named using the short language code (e.g. `enUS.yml`, `deDE.yml`, ...).
- The `.yml` files contain the language-specific translations for the UI elements' labels, alerts, dialogs and so on.
