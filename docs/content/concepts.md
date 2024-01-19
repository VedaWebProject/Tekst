# Concepts


## Collaboration

Tekst aims to encourage collaboration between parties with common backgrounds or interests, like researchers working with data on the same reference text. The goal of this collaboration is the creation of a common, central platform for relevant data resources concerning one or multiple (related) texts. With Tekst, research communities are able to:

- accumulate relevant resources on one online platform
- create and propose new resources for publication
- evaluate, compare and improve data created by other community members
- publish curated datasets to the broader public (which is a decision of the party operating the platform)
- offer different ways for accessing the data, like browsing contents along the texts structure, extensive search functionalities or exporting datasets in various formats
- maintain a close network of likeminded researchers

![collaboration flow](assets/collaboration_flow.png)
*Collaboration flow between administrators, registered users and visitors of the platform.*

The administrator(s) operating the platform curate the resources that are visible to public visitors. A selected community of registered users is able to create and share datasets with each other, propose corrections or additions, stay up to date on each other's progress and maintain a cooperative relationship to other representatives of their field.

## Texts and Structure

One instance of Tekst can handle one or more reference texts that can be selected from the user interface. Switching to a different reference text changes the working context of Tekst, including available resources, settings, etc.

Each text's structure has to be modeled in advance to lay the foundation for Tekst to work with it. The structure model of a text has to follow a clear hierarchical scheme of nested structure levels (e.g. "Series" contains "Book" contains "Chapter" contains "Paragraph" contains "Sentence").

Each structure level *must* be subordinate to *one* parent structure level and can have *at most one* direct child level. It is not possible to have two structure levels modeled as siblings under the same parent level.

!!! info "Example"
    A book's chapters may contain footnotes you'd want to model separately from the paragraphs contained in the chapters. This is not possible via the structure model. But you may very well just use a structure of "Chapter" containing "Paragraph" and associate resources containing resources on the footnotes to each node on the "Paragraph" level.

The reason for this limitation is the concept of exploratory browsing implemented by Tekst. For being able to skip through the nodes on a certain structure level like you turn the pages of a book, there has to be both a clear hierarchy of structure levels as well as a sequencial order of the nodes on each level.

![data model](assets/data_model_visualization.png)
*Data model: Example of a simple song structure modeled for use as a reference work (or "text") in Tekst, with a selection of (partly imaginary) resources associated with each structure level. A resource may provide zero to one contents per node on its respective structure level.*


## Resources

!!! info

    The following selection of resource types is just a part of what is currently planned. More resource types may be added in the future.

### Plain Text
This very simple resource type may be used for plain text (unformatted) data like a text version or translation on a "Paragraph" or "Sentence" level.

### Rich Text
Similar to [Plain Text](#plain-text) but with added text formatting/styling capabilities, this resource type is useful for longer sequences of textual data that have their own internal structure, like a short analysis on a "Paragraph" structure level.

### Annotation
(WIP)

### External Reference
(WIP)

### Image
(WIP)

### Audio
(WIP)
