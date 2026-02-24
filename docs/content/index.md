# What is Tekst?

!!! warning "Work-in-progress"
    While the Tekst platform is already in its open beta phase, this manual is still very much work-in-progress. We'll try to keep it up-to-date and complete it as soon as possible, but please bear with us if you encounter any incomplete or outdated information.

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts ([and more](#alternative-use-cases)). It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project, where it constitutes the technical basis of the *VedaWeb* research platform.

## Use cases

Tekst is primarily meant as a platform software for philological research projects. The original intent for the development of Tekst was to create the technical basis for the online research platform [VedaWeb](https://vedaweb.uni-koeln.de/), where numerous resources on multiple Old Indic Sanskrit texts can be browsed, compared and searched. These include text versions, translations, annotations, audio recordings of recitations and references to external sources, which are all aligned to the structure of their respective reference texts.

Therefore, the main use cases for Tekst are comparable research projects that either want to publish and showcase their research data, simply curate a set of established resources on certain reference texts, or even encourage the research community to participate and contribute to a central platform dedicated to provide relevant resources.

In the end, giving it a try on your local machine [is relatively easy](setup/installation.md#docker-based-deployment-recommended).

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

## Conceptual Caveats

Depending on your requirements, you might want to consider the following list of potential shortcomings:

- SEO: The web client is a [SPA](https://en.wikipedia.org/wiki/Single-page_application) that is rendered in the browser (no SSR). As a result, visibility to search engines is somewhat limited.
- ... _(get in touch if you find anything that should be added to this list, we mean it!)_
