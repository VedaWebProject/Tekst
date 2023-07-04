# Introduction

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts (and more). It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project on Old Indic texts, where it constitutes the technical basis of the *VedaWeb* research platform.


## Use Cases

(WIP)


## Concepts

(WIP)


## Features

This list is not exhaustive, but includes some features that might be decisive for certain use cases:

- Manage multiple independent, potentially differently structured texts and arbitrary related resources in a single platform instance
- One common user base for the whole platform
- UI colors will adapt to the currently selected working text for visual unambiguity
- Built-in [i18n](https://en.wikipedia.org/wiki/Internationalization_and_localization) with an extensible set of languages
- Integrated user management with authentication and role-based as well as owner-based authorization
- *Closed Mode* to run the platform purely administrator-driven, turning off registration for arbitrary users
- Extensively typed and documented server API (via [OpenAPI](https://spec.openapis.org/oas/v3.0.2) specification) and built-in interactive API documentation (via [Swagger UI](https://github.com/swagger-api/swagger-ui) and/or [ReDoc](https://github.com/Redocly/redoc)), all thanks to [FastAPI](https://github.com/tiangolo/fastapi)


## Caveats

Depending on your requirements, you might want to consider the following list of potential shortcomings:

- SEO: The (web-) client is a [SPA](https://en.wikipedia.org/wiki/Single-page_application) that is rendered in the browser (so no SSR). As a result, visibility to search engines is somewhat limited.
- UI responsiveness: The user interface – especially the public-facing part – is responsive to the use on hand-held mobile devices. That being said, it was primarily developed for desktop-based usage. This might show in places.
