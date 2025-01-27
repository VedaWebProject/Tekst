# Tekst Documentation

## Development

To run the development server for locally previewing changes in the documentation, use the compose file in `dev/` from the repository root:

```
docker compose -f dev/compose.yml --profile docs -p tekst-docs up
```

Then, visit the URL shown in the terminal using your web browser.

> [!IMPORTANT]
> Some parts/snippets of the documentation are actually re-used help text translations from the client project in `Tekst-Web`. To make these available to the docs dev server, you'll have to first install the client project in `Tekst-Web` and run `npm run translations`.
