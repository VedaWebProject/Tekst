# Tekst Documentation

## Development

To run the development server for locally previewing changes in the documentation, use the compose file in `dev/` from the repository root:

```
docker compose -f dev/compose.yml --profile docs -p tekst-docs up
```

Then, visit `http://127.0.0.1:8091` using your web browser.
