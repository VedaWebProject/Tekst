# Introduction

!!! warning "Work-in-progress"
    While the Tekst platform software is already in its open beta phase, this manual is still very much work-in-progress. We'll try to complete it as soon as possible, but please bear with us if you encounter any incomplete information.

## What is Tekst?

Tekst is a collaborative, web-based research platform for aligning, displaying, linking, exploring, and enriching resources on natural language texts. It has been initially developed within the scope of the VedaWeb 2.0 project to serve as the technical basis of the [VedaWeb](https://vedaweb.uni-koeln.de/) research platform for the linguistic study of Old Indo-Aryan texts.

But its design is not limited to the study of any particular language or text type as it is meant to be project-agnostic and handle multimodal resources on arbitrary texts.

## Use cases

Tekst is primarily meant as a platform software for philological research projects. The original task for Tekst was to provide a central research community platform for the VedaWeb project and its research data, including text versions, translations, annotations, audio recordings of recitations and references to external sources, which are all aligned to the structure of their respective reference texts.

Therefore, the main use cases for Tekst are comparable research projects that either want to publish and showcase their research data, simply curate a set of established resources on certain reference texts, or even encourage the research community to participate and contribute to a central platform dedicated to provide relevant resources.

In the end, giving it a try on your local machine [is relatively easy](setup/installation.md#docker-based-deployment-recommended).

## Features

This list is far from exhaustive, but includes some features that might be decisive in certain scenarios:

!!! note
    - [x] This feature is already implemented.
    - [ ] This feature is planned, not yet implemented.

- [x] Manage multiple independent, potentially **differently structured texts**
- [x] Run it as a **closed, internally curated** publishing platform **or as an open platform** for a selected research **community** to encourage user **contributions**
- [x] Built-in **user management** with authentication and a combination of role-based and ownership-based authorization
- [x] Built-in [i18n](https://en.wikipedia.org/wiki/Internationalization_and_localization) with an extensible set of languages (contributions are welcome!)
- [x] Encouraging **user contributons and collaboration** by enabling user to
    - [x] submit quick correction notes
    - [x] create versions of existing resources to compose and propose deviating data
    - [x] create own resources, propose them for publication and have them reviewed by the community
- [x] Per-resource data **export** (full or range-based) as JSON or CSV
- [x] Dozens of **specialized usability features**, developed with **real-world needs of scholars** in mind
- [x] Content **archiving and versioning**
- [x] Flexible **citation** hints and URLs to specific contents from specific resources at a certain point in time
- [x] Extensively **typed and documented server API** (via [OpenAPI](https://spec.openapis.org/oas/v3.0.2) specification) and built-in interactive API documentation (via [Swagger UI](https://github.com/swagger-api/swagger-ui) and/or [ReDoc](https://github.com/Redocly/redoc)), all thanks to [FastAPI](https://github.com/tiangolo/fastapi)
- [x] **Customize** logos, UI colors, fonts, on-screen keyboards, ...
- [x] Built-in **user messaging** system
- [ ] Publish data from various **multi-modal resources**, aligned to the structure of their respective common **reference text**
    - [x] Plain text
    - [x] Rich text
    - [x] Text annotations
    - [x] Images
    - [x] Audio
    - [ ] Video
    - [ ] 3D models
    - [x] External references
    - [x] Integration of external APIs
    - [x] Arbitrary key-value metadata

## Caveats

Depending on your requirements, you might want to consider the following list of potential shortcomings:

- SEO: The web client is a [SPA](https://en.wikipedia.org/wiki/Single-page_application) that is rendered in the browser (no SSR). As a result, visibility to search engines is somewhat limited.
- No built-in functionality for uploading and managing media files. If you want to integrate multimedia resources, you will have to host the respective files yourself and reference them by URL in your resources.
- _...get in touch if you find anything that should be added to this list, we mean it!_

## Publications

- **DHd 2026**: We talked about Tekst's concept of integrating multimodal data alongside textual resources using the structure of reference texts in a [talk at the **DHd 2026** conference](https://doi.org/10.5281/zenodo.18696589) (Digital Humanities im deutschsprachigen Raum 2026: Nicht nur Text, nicht nur Daten. Vienna, Austria, 23-27 February 2026).
- **DH 2023**: We presented our vision for a collaborative text research platform in [a talk at the international **DH 2023** conference](https://doi.org/10.5281/zenodo.8107794) (Digital Humanities 2023: Collaboration as Opportunity. Graz, Austria, 10-14 July 2023).
