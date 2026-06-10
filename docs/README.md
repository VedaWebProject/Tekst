# Tekst Documentation

## Development

To run the development server for locally previewing changes in the documentation, run this command in the repository root (or replace `${PWD}/docs` by `${PWD}` if you run it from the `docs/` directory):

```
docker run --rm -it -p 127.0.0.1:8080:8000 -v ${PWD}/docs:/docs zensical/zensical
```

Then, visit **`http://127.0.0.1:8080`** using your web browser.

To update the locally used Zensical image:

```
docker pull zensical/zensical
```

## Deployment

There is a GH Actions workflow in `.github/workflows/docs.yml` that automatically builds and deploys the documentation to GitHub Pages. It is triggered on every push to the `main` branch.

**Important:** Zensical is pinned to a certain version in the deployment workflow. Remember to update it there as well whenever successfully changing the version in development for new features or bug fixes.
