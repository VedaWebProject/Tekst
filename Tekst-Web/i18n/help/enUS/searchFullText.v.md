# Full-text Search

A full-text search can be used both via the Quick Search and in the Advanced Search for resources of the following types:

- Plain Text
- Formatted Text
- Audio
- Images
- External References

Search terms are looked for within text contents. These can be texts themselves or titles or descriptions of media or links.

The full-text search syntax supports the following special operators:

- `+` AND operator
- `|` OR operator
- `-` negates a single token
- `"` encloses a sequence of tokens to mark a phrase for searching
- `*` at the end of a term for a prefix search
- `(` and `)` denote precedence of search operators
- `~N` after a word for edit distance (fuzziness), where `N` is a digit
- `~N` after a phrase for word proximity, where `N` is a digit
