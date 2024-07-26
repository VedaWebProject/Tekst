# Tekst <!-- omit in toc -->

<img width="64" height="64" align="right" style="position: absolute;  top: 0; right: 0; padding: 12px; z-index: 9" src="docs/content/assets/logo.png" alt="Tekst logo"/>

...as in **T**ext **E**xploration and **K**nowledge **S**tructuring **T**ool

![Server tests status](https://img.shields.io/github/actions/workflow/status/VedaWebProject/Tekst/server-tests.yml?label=server%20tests)
[![Server tests coverage](https://img.shields.io/coverallsCoverage/github/VedaWebProject/Tekst?branch=main&label=server%20tests%20coverage)](https://coveralls.io/github/VedaWebProject/Tekst?branch=main)
![Client build status](https://img.shields.io/github/actions/workflow/status/VedaWebProject/Tekst/client-build.yml?label=client%20build) \
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/VedaWebProject/Tekst)
![GitHub code size](https://img.shields.io/github/languages/code-size/VedaWebProject/Tekst)
![GitHub repo size](https://img.shields.io/github/repo-size/VedaWebProject/Tekst)

> 🏗 Tekst is still in a pre-alpha stage. As of now there's no complete (let alone production-ready) version available.
> As soon as we're ready for it, the new [VedaWeb platform](https://vedaweb.uni-koeln.de/rigveda) will become the first public instance of Tekst. Until then, you are welcome to follow the development of Tekst in this very repository.

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts (and more). It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project on Old Indic texts, where it constitutes the technical basis of the research platform "VedaWeb", which will be launched in its new form as part of the project's efforts.

## Manual

You are looking for information on concepts, use cases, features, setup, deployment or administration of the Tekst platform?

<!-- I know this is a sin – and it hurts me, too. But I need the bigger font on this. -->

### 📖 [Click here for the _Tekst_ manual!](https://vedawebproject.github.io/Tekst)

## Publications

We presented our vision for a collaborative text research platform at the **DH2023** conference (Digital Humanities 2023. Collaboration as Opportunity, Graz, Austria, 10-14 July 2023). You can find our conference paper [here](https://doi.org/10.5281/zenodo.8107794)!

## Development

This is a monorepo containing the codebases of the following parts of the Tekst platform:

| Project Directory | Description |
| --- | --- |
| [Tekst-API](Tekst-API) | API server project |
| [Tekst-Web](Tekst-Web) | Web client project |
| [Tekst-Util](Tekst-Util) | API maintenance utility script (Bash-based) |
| [docs](docs) | Documentation and user manual, to be found [here](https://vedawebproject.github.io/Tekst) |

Where applicable, the different project directories contain their own respective `README.md` files covering the development tooling and overall project setup.

## Contributing

Please see the [contributing guidelines](CONTRIBUTING.md).
