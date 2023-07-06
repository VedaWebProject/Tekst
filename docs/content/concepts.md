# Concepts


## Texts and structure modeling

One instance of Tekst can handle one or more reference texts that can be selected from the user interface. Switching to a different reference text changes the working context of Tekst, including available data layers, settings, etc.

Each text's structure has to be modeled in advance to lay the foundation for Tekst to work with it. The structure model of a text has to follow a clear hierarchical scheme of nested structure levels (e.g. "Series" contains "Book" contains "Chapter" contains "Paragraph" contains "Sentence").

Each structure level *must* be subordinate to *one* parent structure level and can have *at most one* child level. It is not possible to have two structure levels modeled as siblings under the same parent level.

!!! info "Example"
    A book's chapters may contain footnotes you'd want to model separately from the paragraphs contained in the chapters. This is not possible via the structure model. But you may very well just use "Chapter" containing "Paragraph" and associate data layers containing resources on the footnotes to each node on the "Paragraph" level.

The reason for this limitation is the concept of exploratory browsing implemented by Tekst. For being able to skip through the nodes on a certain structure level like you turn the pages of a book, there has to be both a clear hierarchy of structure levels as well as a sequencial order of the nodes on each level.

![data model diagram](assets/data_model_visualization.png)
*Data model diagram: Example of a simple song structure modeled for use as a reference work (or "text") in Tekst, with a selection of (partly imaginary) data layers associated with each structure level. A data layer may provide zero to one data units per node on its respective structure level.*


## Data Layers

!!! info

    The following selection of data layer types is just a part of what is currently planned. More data layer types may be added in the future.

### Plain Text
This very simple data layer type may be used for plain text (unformatted) data like a text version or translation on a "Paragraph" or "Sentence" level.

### Rich Text
Similar to [Plain Text](#plain-text) but with added text formatting/styling capabilities, this data layer type is useful for longer sequences of textual data that have their own internal structure, like a short analysis on a "Paragraph" structure level.

### Annotation
(WIP)

### External Reference
(WIP)

### Image
(WIP)

### Audio
(WIP)
