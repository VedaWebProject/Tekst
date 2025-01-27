# What is Tekst?

!!! warning

    🏗 Just like Tekst itself, this manual/documentation is still very incomplete and "work in progress".

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts ([and more](#alternative-use-cases)). It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project on Old Indic texts, where it constitutes the technical basis of the *VedaWeb* research platform.

!!! info

    At the moment, the VedaWeb platform is still a custom made application that was developed in an earlier phase of the VedaWeb project. Many of its concepts will find their way into Tekst, but it lacks core features like user management, collaboration and the possibility to work with multiple arbitrarily structured texts. As soon as Tekst is ready, the VedaWeb platform will become the first public instance of Tekst.


## Use cases

### Philological research projects

The original intent for the development of Tekst was to create the technical basis for the online research platform [VedaWeb](https://vedaweb.uni-koeln.de/), where numerous resources on multiple Old Indic Sanskrit texts can be browsed, compared and searched. These include text versions, translations, annotations and references to external sources, which are all aligned to the structure of their respective reference texts.

Therefore, the main use case for Tekst are comparable research projects that either want to publish and showcase their research data, simply curate a set of established resources on certain reference texts, or even encourage the research community to participate and contribute to a central platform dedicated to provide relevant resources.

### Alternative use cases

The above being said, nothing is stopping you from using Tekst in different contexts. Tekst might be a viable option for you as long as

1. your data revolves around a somewhat structured work or other phenomenon (e.g. book, movie, theatre play or even a simple sequence of years)
2. the types of [resources](concepts.md#resources) Tekst offers are sufficiently able to represent the data you want to work with

In the end, giving it a try on your local machine [is relatively easy](setup/installation.md#deploy-via-docker-recommended).

!!! info "Please note"
    Despite the alternative use cases mentioned, "texts" are used exemplary throughout this documentation and in the internal user interface of Tekst, as this is still the main use case.


## Features

This list is far from exhaustive, but includes some features that might be decisive for certain use cases:

- Manage multiple independent, potentially differently structured texts and arbitrary related resources in a single platform instance
- One common user base for the whole platform
- UI colors will adapt to the currently selected working text for visual unambiguity
- Built-in [i18n](https://en.wikipedia.org/wiki/Internationalization_and_localization) with an extensible set of languages
- Integrated user management with authentication and role-based as well as owner-based authorization
- *Closed Mode* to run the platform purely administrator-driven, turning off registration for arbitrary users
- Customization of
    - Content fonts
    - On-screen keyboard character sets
- Extensively typed and documented server API (via [OpenAPI](https://spec.openapis.org/oas/v3.0.2) specification) and built-in interactive API documentation (via [Swagger UI](https://github.com/swagger-api/swagger-ui) and/or [ReDoc](https://github.com/Redocly/redoc)), all thanks to [FastAPI](https://github.com/tiangolo/fastapi)
- ...


## Caveats

Depending on your requirements, you might want to consider the following list of potential shortcomings:

- SEO: The (web-) client is a [SPA](https://en.wikipedia.org/wiki/Single-page_application) that is rendered in the browser (so no SSR). As a result, visibility to search engines is somewhat limited.
- UI responsiveness: The user interface – especially the public-facing part – is responsive to the use on hand-held mobile devices. That being said, it was primarily developed for desktop-based usage. This might show in places.
