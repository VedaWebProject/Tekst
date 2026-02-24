# What is Tekst?

!!! warning "Work-in-progress"
    While the Tekst platform is already in its open beta phase, this manual is still very much work-in-progress. We'll try to complete it as soon as possible, but please bear with us if you encounter any incomplete information.

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts. It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project, where it constitutes the technical basis of the *VedaWeb* research platform.

## Use cases

Tekst is primarily meant as a platform software for philological research projects. The original intent for the development of Tekst was to create the technical basis for the online research platform [VedaWeb](https://vedaweb.uni-koeln.de/), where numerous resources on multiple Old Indic Sanskrit texts can be browsed, compared and searched. These include text versions, translations, annotations, audio recordings of recitations and references to external sources, which are all aligned to the structure of their respective reference texts.

Therefore, the main use cases for Tekst are comparable research projects that either want to publish and showcase their research data, simply curate a set of established resources on certain reference texts, or even encourage the research community to participate and contribute to a central platform dedicated to provide relevant resources.

In the end, giving it a try on your local machine [is relatively easy](setup/installation.md#docker-based-deployment-recommended).

## Features

This list is far from exhaustive, but includes some features that might be decisive in certain scenarios:

- Manage multiple independent, potentially differently structured texts
- Publish data from various multi-modal resources, aligned to the structure of their respective common reference text
  - Plain text
  - Rich text
  - Text annotations
  - Images
  - Audio
  - External references
  - Integration of external APIs
  - Arbitrary key-value metadata
- Run it as a closed, internally curated publishing platform or as an open platform for a selected research community to encourage user contributions
- Built-in user management with authentication and a combination of role-based and ownership-based authorization
- Built-in [i18n](https://en.wikipedia.org/wiki/Internationalization_and_localization) with an extensible set of languages (contributions are welcome!)
- Customize logos, UI colors, fonts, on-screen keyboards, ...
- Per-resource data export (full or range-based) as JSON or CSV
- Dozens of specialized usability features, developed with real-world needs of humanities researchers in mind
- Extensively typed and documented server API (via [OpenAPI](https://spec.openapis.org/oas/v3.0.2) specification) and built-in interactive API documentation (via [Swagger UI](https://github.com/swagger-api/swagger-ui) and/or [ReDoc](https://github.com/Redocly/redoc)), all thanks to [FastAPI](https://github.com/tiangolo/fastapi)
- Built-in user messaging system
- ...

## Caveats

Depending on your requirements, you might want to consider the following list of potential shortcomings:

- SEO: The web client is a [SPA](https://en.wikipedia.org/wiki/Single-page_application) that is rendered in the browser (no SSR). As a result, visibility to search engines is somewhat limited.
- No built-in functionality for uploading and managing media files. If you want to integrate image- or audio-based resources, you will have to host the respective media files yourself and link to them from your resources.
- ... _(get in touch if you find anything that should be added to this list, we mean it!)_
