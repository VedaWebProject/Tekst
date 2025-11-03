# What is Tekst?

<img src="assets/home_header.jpg" width="100%" title="We couldn't pay a designer for this, sorry." alt="An unpleasing AI slop showing a stack of books transitioning into what is supposed to graphically represent something like digital data flow but does an unfortunate job and looks like a public transport network plan instead" />

!!! warning

    🏗 The Tekst platform as well as this documentation are still work-in-progress.

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts ([and more](#alternative-use-cases)). It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project, where it constitutes the technical basis of the *VedaWeb* research platform.

## Use cases

### Philological research projects

The original intent for the development of Tekst was to create the technical basis for the online research platform [VedaWeb](https://vedaweb.uni-koeln.de/), where numerous resources on multiple Old Indic Sanskrit texts can be browsed, compared and searched. These include text versions, translations, annotations, audio recordings of recitations and references to external sources, which are all aligned to the structure of their respective reference texts.

Therefore, the main use cases for Tekst are comparable research projects that either want to publish and showcase their research data, simply curate a set of established resources on certain reference texts, or even encourage the research community to participate and contribute to a central platform dedicated to provide relevant resources.

### Alternative use cases

The above being said, nothing is stopping you from using Tekst in different contexts. Tekst might be a viable option for you as long as the following conditions are met:

1. Your data revolves around a somewhat structured work or other phenomenon (e.g. book, movie, theatre play or even a simple sequence of years).
2. The [types of resources](concepts.md#resources) Tekst offers are sufficiently able to represent the data you want to work with.

In the end, giving it a try on your local machine [is relatively easy](setup/installation.md#docker-based-deployment-recommended).

!!! info "Please note"
    Despite the alternative use cases mentioned, "texts" are used exemplary throughout this documentation and in the internal user interface of Tekst, as they are still the main use case.


## Features

This list is far from exhaustive, but includes some features that might be decisive in certain scenarios:

- Manage multiple independent, potentially differently structured texts and arbitrary related resources in a single platform instance
- One common user base for the whole platform
- Built-in [i18n](https://en.wikipedia.org/wiki/Internationalization_and_localization) with an extensible set of languages (contributions welcome!)
- Integrated user management with authentication and a combination of role-based and ownership-based authorization
- Optional *Closed Mode* to disable public registrations (or applications) for an internally curated platform without user contributions
- Customization of
    - Content fonts
    - On-screen keyboard character sets
    - UI Colors
    - ...
- Extensively typed and documented server API (via [OpenAPI](https://spec.openapis.org/oas/v3.0.2) specification) and built-in interactive API documentation (via [Swagger UI](https://github.com/swagger-api/swagger-ui) and/or [ReDoc](https://github.com/Redocly/redoc)), all thanks to [FastAPI](https://github.com/tiangolo/fastapi)
- ...


## Caveats

Depending on your requirements, you might want to consider the following list of potential shortcomings:

- SEO: The (web-) client is a [SPA](https://en.wikipedia.org/wiki/Single-page_application) that is rendered in the browser (so no SSR). As a result, visibility to search engines is somewhat limited.
- ...?
