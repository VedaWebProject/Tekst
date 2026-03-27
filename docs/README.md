# Tekst Documentation

To run the development server for locally previewing changes in the documentation, run this command in the repository root (or replace `${PWD}/docs` by `${PWD}` if you run it from the `docs/` directory):

```
docker run --rm -it -p 127.0.0.1:8080:8000 -v ${PWD}/docs:/docs zensical/zensical
```

Then, visit `http://127.0.0.1:8080` using your web browser.
