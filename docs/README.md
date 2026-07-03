# Tekst Documentation

## Development

To run the development server for locally previewing changes in the documentation, run this command in the repository root:

```
docker compose -f docs/compose.yml up
```

...or this one from within the `docs/` directory:

```
docker compose up
```

Then, visit **`http://127.0.0.1:8888`** using your web browser.

## Deployment

There is a GH Actions workflow in `.github/workflows/docs.yml` that automatically builds and deploys the documentation to GitHub Pages. It is triggered on every push to the `main` branch.

**Important:** Zensical is pinned to a certain version in the deployment workflow. Remember to update it there as well whenever changing the version in development for new features or bug fixes.
