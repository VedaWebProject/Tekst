# Quick Search

The quick search is a full-text search across all available resources of the selected texts. Which resources are available for quick search depends on your access rights and the type and configuration of the resources.

## Operators

- `+` AND operator
- `|` OR operator
- `-` negates a single token
- `"` encloses a sequence of tokens to indicate a phrase for the search
- `*` at the end of a term for a prefix search
- `(` and `)` indicate the precedence of search operators
- `~N` after a word for edit distance (fuzziness), where `N` is a digit
- `~N` after a phrase for word distance, where `N` is a digit

## Settings

### Respect Diacritics

If this feature is activated, entered or missing (!) diacritics will be considered during the search, and only content with the same use of diacritics will be found.

### All Terms Must Occur

With this setting you can define how individual search terms should logically be connected by default. If this function is activated, only locations containing all entered search terms will be found. Otherwise, locations with the most hits will rank higher in the search results than those with fewer hits.

### Interpret Regular Expressions

Quick search can handle search queries using a regular expression. This feature **deactivates the standard search operators** listed above!

The expression _must_ correspond to an entire term — so do not use boundary anchors (`^` at the beginning and `$` at the end of the expression). An overview of the available RegExp syntax can be found in the [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/regexp-syntax.html).

### Include Content from Higher-Level Locations

If this option is activated, the contents of all higher-level locations will also apply to each child location. For example, a verse in a poem will be found if the search yields a hit in content from the parent stanza.

### Find Locations at All Levels

If this option is activated, locations at all structural levels will be found, not just those from the default level.

### Text Selection

Defines which texts will be searched. By default, all available texts are selected. This setting will automatically reset when you change your working text.

## Location Aliases

In addition to search terms, location aliases can also be entered in the quick search, allowing you to quickly jump to a specific location using known aliases.
